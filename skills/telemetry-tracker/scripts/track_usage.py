#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
track_usage.py - 智能体/技能使用数据上报脚本

职责：
    将一次 Agent / Skill / 普通对话的使用记录写入 SQLite 数据库。
    供各智能体 AGENTS.md 和技能 SKILL.md 的「使用埋点」规则隐式调用。

设计要点：
    - 数据库默认放在 ~/.openclaw/workspace/shared/telemetry/usage.db
      （跨 Agent 共享区，绕开各子 Agent workspace 隔离）
    - 首次运行自动建库建表，幂等可重复执行
    - SQLite 开启 WAL 模式 + busy_timeout，缓解多 Agent 并发写锁
    - 写入失败自动追加到同目录 failed_events.jsonl，绝不丢失、绝不向用户报错
    - user_name 为空时用 user_id 兜底，两者皆空填 unknown
    - user_query 自动截断到 500 字

用法：
    python3 track_usage.py \
        --event-type agent \
        --target-name product_discovery \
        --target-label "产品探索智能体" \
        --user-query "帮我做腾讯 WorkBuddy 竞品分析" \
        --user-id zhangsan \
        --user-name "张三"

    # 普通对话（未触发任何 Agent/Skill）
    python3 track_usage.py --event-type chat --target-name "-"
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime

# ============================================================
# 路径常量
# ============================================================

# 跨 Agent 共享的数据目录（OpenClaw workspace 约定的 shared 公共区）
DEFAULT_DB_DIR = os.path.expanduser("~/.openclaw/workspace/shared/telemetry")
DEFAULT_DB_PATH = os.path.join(DEFAULT_DB_DIR, "usage.db")
FAILED_LOG_PATH = os.path.join(DEFAULT_DB_DIR, "failed_events.jsonl")

# user_query 最大保留长度，避免单条记录过大
MAX_QUERY_LEN = 500


# ============================================================
# 数据库初始化（幂等）
# ============================================================

def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """获取数据库连接，首次运行自动建库建表、开 WAL、设超时。"""
    db_dir = os.path.dirname(db_path)
    os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(db_path, timeout=5.0)
    # 开启 WAL：多读单写，显著降低并发写锁冲突
    conn.execute("PRAGMA journal_mode=WAL")
    # 写入遇锁时等待 5 秒而非立即报错
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row

    _init_schema(conn)
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    """建表 + 建索引，IF NOT EXISTS 保证幂等。"""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS usage_events (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type    TEXT    NOT NULL,   -- agent / skill / chat
            target_name   TEXT    NOT NULL,   -- 智能体或技能 ID
            target_label  TEXT,               -- 中文名，便于汇报展示
            user_query    TEXT,               -- 用户原始输入（已截断）
            user_id       TEXT,               -- 用户标识
            user_name     TEXT,               -- 真实姓名；取不到则回退 user_id / unknown
            invoke_count  INTEGER DEFAULT 1,  -- 本次触发子调用次数
            turn_no       INTEGER DEFAULT 1,  -- 交互轮次
            output_files  TEXT,               -- 产出文件链接，JSON 数组字符串
            status        TEXT    DEFAULT 'success',  -- success / failed
            created_at    TEXT    NOT NULL    -- 上报时间 ISO 格式
        );

        CREATE INDEX IF NOT EXISTS idx_name ON usage_events(target_name);
        CREATE INDEX IF NOT EXISTS idx_type ON usage_events(event_type);
        CREATE INDEX IF NOT EXISTS idx_time ON usage_events(created_at);
        """
    )
    conn.commit()


# ============================================================
# 核心写入逻辑
# ============================================================

def record_event(
    event_type: str,
    target_name: str,
    target_label: str = "",
    user_query: str = "",
    user_id: str = "",
    user_name: str = "",
    invoke_count: int = 1,
    turn_no: int = 1,
    output_files=None,
    status: str = "success",
    db_path: str = DEFAULT_DB_PATH,
) -> bool:
    """
    写入一条使用记录。

    姓名兜底链路（由调用方 LLM 在对话层先尝试 wecom-cli 查询与询问）：
        user_name 非空 -> 直接用
        user_name 空   -> 用 user_id
        两者皆空       -> 填 unknown

    返回 True 表示成功落库，False 表示失败（已写本地兜底日志）。
    """
    # ---- 字段清洗 ----
    event_type = (event_type or "chat").strip().lower()
    target_name = (target_name or "-").strip() or "-"

    # 姓名三级兜底
    if not user_name:
        user_name = user_id if user_id else "unknown"

    # query 截断
    if user_query and len(user_query) > MAX_QUERY_LEN:
        user_query = user_query[:MAX_QUERY_LEN]

    # output_files 统一存 JSON 数组字符串
    if output_files is None:
        output_files_json = ""
    elif isinstance(output_files, (list, tuple)):
        output_files_json = json.dumps(list(output_files), ensure_ascii=False)
    else:
        # 已是字符串则原样保留
        output_files_json = str(output_files)

    created_at = datetime.now().isoformat(timespec="seconds")

    row = {
        "event_type": event_type,
        "target_name": target_name,
        "target_label": target_label,
        "user_query": user_query,
        "user_id": user_id,
        "user_name": user_name,
        "invoke_count": int(invoke_count) if invoke_count else 1,
        "turn_no": int(turn_no) if turn_no else 1,
        "output_files": output_files_json,
        "status": status or "success",
        "created_at": created_at,
    }

    # ---- 尝试写入数据库 ----
    try:
        conn = get_connection(db_path)
        try:
            conn.execute(
                """
                INSERT INTO usage_events
                    (event_type, target_name, target_label, user_query, user_id,
                     user_name, invoke_count, turn_no, output_files, status, created_at)
                VALUES
                    (:event_type, :target_name, :target_label, :user_query, :user_id,
                     :user_name, :invoke_count, :turn_no, :output_files, :status, :created_at)
                """,
                row,
            )
            conn.commit()
            return True
        finally:
            conn.close()
    except Exception:
        # ---- 兜底：写本地日志，绝不抛错、绝不打扰用户 ----
        _write_fallback(row)
        return False


def _write_fallback(row: dict) -> None:
    """数据库写入失败时，把记录追加到 failed_events.jsonl。"""
    try:
        os.makedirs(os.path.dirname(FAILED_LOG_PATH), exist_ok=True)
        with open(FAILED_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        # 连兜底日志都写不进去（如磁盘满），静默放弃
        pass


# ============================================================
# 命令行入口
# ============================================================

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="track_usage.py",
        description="智能体/技能使用数据上报。每次任务结束后由埋点规则隐式调用，静默执行。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--event-type",
        required=True,
        choices=["agent", "skill", "chat"],
        help="事件类型：agent（智能体）/ skill（技能）/ chat（普通对话，未触发 Agent/Skill）",
    )
    parser.add_argument(
        "--target-name",
        required=True,
        help='目标名称（智能体或技能的 ID，如 product_discovery、prd-document-generator）；普通对话填 "-"',
    )
    parser.add_argument("--target-label", default="", help="目标中文名，便于汇报展示（如「产品探索智能体」）")
    parser.add_argument("--user-query", default="", help="用户原始输入文本（会自动截断到 500 字）")
    parser.add_argument("--user-id", default="", help="当前用户标识（如飞书/企业微信 user_id）")
    parser.add_argument("--user-name", default="", help="当前用户真实姓名；为空时脚本用 user_id 兜底")
    parser.add_argument(
        "--invoke-count",
        type=int,
        default=1,
        help="本次交互触发的 Agent/Skill 调用总次数（含子任务调度），默认 1",
    )
    parser.add_argument(
        "--turn-no",
        type=int,
        default=1,
        help="交互轮次（同一需求链累计数），默认 1",
    )
    parser.add_argument(
        "--output-files",
        default="",
        help='产出文件链接，多个用逗号分隔；无产出留空',
    )
    parser.add_argument(
        "--status",
        default="success",
        choices=["success", "failed"],
        help="本次执行状态，默认 success",
    )
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help=argparse.SUPPRESS)
    return parser


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)

    # output_files 逗号分隔 -> 列表
    output_files = []
    if args.output_files:
        output_files = [s.strip() for s in args.output_files.split(",") if s.strip()]

    ok = record_event(
        event_type=args.event_type,
        target_name=args.target_name,
        target_label=args.target_label,
        user_query=args.user_query,
        user_id=args.user_id,
        user_name=args.user_name,
        invoke_count=args.invoke_count,
        turn_no=args.turn_no,
        output_files=output_files,
        status=args.status,
        db_path=args.db_path,
    )

    # 静默退出：无论成败都不打印（埋点不应打扰用户）
    # 仅在显式调试时可通过环境变量 TELEMETRY_DEBUG=1 查看结果
    if os.environ.get("TELEMETRY_DEBUG"):
        print("上报成功" if ok else "上报失败（已写兜底日志）", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
