---
name: telemetry-tracker
description: 使用数据埋点与统计技能。承担两个职责：(1) 自动埋点——被各智能体 AGENTS.md 和技能 SKILL.md 的「使用埋点」规则隐式调用，把每次 Agent/Skill 使用记录写入 SQLite 数据库；(2) 主动汇报——当用户询问"使用情况""调用统计""哪个用得多"等意图时，读取数据并生成中文文本汇报。
---

# 使用数据埋点与统计

## 核心定位

本技能是整个产品智能体系统的「数据底座」，承担两个互不干扰的职责：

1. **自动埋点（职责 A）**：**硬触发，每轮对话结束前必须执行**。各智能体/技能在每一轮交互结束前调用本技能，静默记录一条使用数据到 SQLite 数据库。全程不向用户展示、不等待用户确认。
2. **主动汇报（职责 B）**：当用户主动询问使用情况时，从数据库读取统计数据，组织成结构化中文文本汇报。

---

## 数据存储位置

- **数据库**：`~/.openclaw/workspace/shared/telemetry/usage.db`
- **兜底日志**：`~/.openclaw/workspace/shared/telemetry/failed_events.jsonl`（数据库写入失败时自动写入，不丢失）
- **选择理由**：`shared/` 是 README 定义的跨 Agent 公共协作区，是唯一能被主智能体和全部子智能体共同写入的位置，可绕开各子 Agent 的 workspace 隔离。

---

## 职责 A：自动埋点

### 触发方式

**硬触发 · 每轮必执行**：不是用户主动调用本技能，而是各智能体/技能在**每一轮对话结束前**的最后一步，依据自身配置文件里的「使用埋点」规则，**必须调用本技能上报**。不依赖记忆、不依赖隐式规则、不可跳过。

### 上报命令

```bash
python3 ~/.openclaw/workspace/skills/telemetry-tracker/scripts/track_usage.py \
  --event-type agent \
  --target-name product_discovery \
  --target-label "产品探索智能体" \
  --user-query "用户原始输入文本" \
  --session-key "agent:main:wecom:direct:wo_xxx" \
  --user-id wo_xxx \
  --user-name "张三"
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `--event-type` | 是 | `agent`（智能体）/ `skill`（技能）/ `chat`（普通对话） |
| `--target-name` | 是 | 智能体或技能的 ID；普通对话填 `-` |
| `--target-label` | 否 | 中文名，便于汇报展示 |
| `--user-query` | 否 | 用户原始输入（自动截断到 500 字） |
| `--session-key` | 否 | 完整会话标识（渠道无关），由调用方通过 session_status 获取；脚本会从中解析渠道用户 ID |
| `--user-id` | 否 | 渠道用户标识（ou_xxx / wo_xxx）；为空时脚本从 --session-key 解析 |
| `--user-name` | 否 | 用户真实姓名（获取链路见下） |
| `--invoke-count` | 否 | 本次触发子调用次数，默认 1 |
| `--output-files` | 否 | 产出文件链接，多个用逗号分隔 |
| `--status` | 否 | `success`（默认）/ `failed` |

### 执行原则（铁律）

1. **每轮必执行**：每一轮对话结束前必须上报，不可跳过、不可遗忘。
2. **尽力获取身份，匿名也要埋点**：每次上报**尽力**携带调用方通过 `session_status` 获取的 `session_key`（或解析出的 `user_id`）。身份缺失时仍正常埋点（脚本自动生成匿名 ID），保证使用次数统计不丢。
3. **静默**：不向用户展示任何提示、不等待确认、不报错。
4. **不阻断主流程**：上报失败不影响任务交付。
5. **姓名兜底链路**（见下节），由调用方 LLM 负责记忆查询与询问，脚本负责最后一层兜底。

---

## 用户身份与姓名获取链路（session_status 识别 + Relationships.md 记忆）

获取用户身份与真实姓名时，按以下顺序依次处理。**身份识别是尽力获取的加分项，缺失时正常埋点（记为匿名）**；拿到身份后，姓名优先查 Relationships.md 记忆。任何一层成功获取姓名后，都必须**回写到 Relationships.md**，供下次直接命中。

```
第 0 层（身份识别 · 会话启动尽力执行 · 由调用方 LLM 完成）：
  调用方调用 session_status(sessionKey="current") 获取当前会话信息。
  从返回结果解析 sessionKey（如 agent:main:wecom:direct:wo_xxx），
  并提取渠道用户 ID（sessionKey 最后一段，渠道无关）。
  -> 整轮对话保留 sessionKey 与 user_id，埋点上报时传递。
  ⚠️ 拿不到身份也正常埋点（记为匿名），不阻断后续链路。
      ↓ 拿到 user_id（或走匿名）
第 1 层（本地记忆 · Relationships.md）：
  加载 ~/.openclaw/workspace/shared/telemetry/Relationships.md，
  用上述 user_id 查询。
  命中 -> 直接使用该姓名，无需再查。
      ↓ 未命中 / 文件不存在
第 2 层（对话层 · LLM 执行）：
  调用 wecom-cli contact get_userlist，用当前 user_id 反查真实姓名。
  查到 -> 填入 --user-name 参数，并回写 Relationships.md。
  （注意：该接口仅返回可见范围 ≤10 人的成员，可能查不到）

  查不到 / 接口报错 / 不在可见范围
      ↓
第 3 层（对话层 · LLM 主动询问用户）：
  LLM 在对话中主动询问：「请问您的姓名是？」
  用户回复 -> 填入 --user-name，并回写 Relationships.md。
  用户不回复 / 拒绝 -> 进入第 4 层。

      ↓
第 4 层（脚本层 · track_usage.py 兜底）：
  --user-name 为空时，脚本用 --user-id（或从 --session-key 解析）兜底。
  user_id 也为空时，填字符串 "unknown"。
  （此层完全静默，不询问、不报错、不回写记忆）
```

### sessionKey 身份解析（渠道无关）

OpenClaw 的 sessionKey 格式统一为 `agent:<agentId>:<渠道>:<chatType>:<用户标识>`：

| 渠道 | sessionKey 示例 | 解析出的 user_id |
|---|---|---|
| 企业微信 | `agent:main:wecom:direct:wo1rsbeqaaua2k6c03rsqzhwk7uhejqg` | `wo1rsbeqaaua2k6c03rsqzhwk7uhejqg` |
| 飞书 | `agent:main:feishu:direct:ou_00beb6896485dbac9c92249d87a04534` | `ou_00beb6896485dbac9c92249d87a04534` |

脚本内置 `parse_identity()` 函数自动完成解析：取 sessionKey 以 `:` 分割后的最后一段作为 user_id。

### Relationships.md 记忆文件

这是跨 Agent 共享的用户身份长期记忆，让每个用户只需被询问一次姓名。

- **文件路径**：`~/.openclaw/workspace/shared/telemetry/Relationships.md`
- **格式**：JSON，键为渠道用户 ID，值为姓名。示例：`{"wo1rsbeqaaua2k6c03rsqzhwk7uhejqg":"陛下","ou_00beb...04534":"张三"}`
- **加载时机**：调用方智能体在**会话开始时**（第 1 层）加载，用 user_id 查询。
- **回写时机**：第 2、3 层成功获取姓名后，把 `{user_id: 姓名}` 追加到 JSON 并保存。
- **回写约束**：**禁止覆盖已有其他用户的记录**，只新增或更新当前用户的映射。
- **首次运行**：文件不存在视为空记忆 `{}`，正常进入第 2 层。

**为什么询问由 LLM 而非脚本执行**：身份识别（session_status）和 Relationships.md 读写都由调用方 LLM 在对话层完成；`wecom-cli contact` 受可见范围限制只作补充；「询问用户」是对话动作只能由 LLM 完成；脚本只做最后兜底。

---

## 职责 B：主动汇报

### 触发方式

**语义识别触发**（由主智能体 `main` 判断）。当用户输入语义匹配以下任一意图时，`main` 调用本技能的汇报能力：

- 「使用情况怎么样 / 调用统计 / 埋点数据 / 使用报表」
- 「哪个智能体/Skill 用得多 / 最受欢迎的功能」
- 「最近大家都在用什么 / 活跃度如何」
- 「telemetry / 统计 / 用量 / 上报」

### 查询命令

```bash
# 总览（推荐默认）
python3 ~/.openclaw/workspace/skills/telemetry-tracker/scripts/stats_usage.py --summary

# 近 7 天总览
python3 ~/.openclaw/workspace/skills/telemetry-tracker/scripts/stats_usage.py --summary --days 7

# 按智能体维度
python3 ~/.openclaw/workspace/skills/telemetry-tracker/scripts/stats_usage.py --by-agent

# 按技能维度
python3 ~/.openclaw/workspace/skills/telemetry-tracker/scripts/stats_usage.py --by-skill

# 每日明细（近 14 天）
python3 ~/.openclaw/workspace/skills/telemetry-tracker/scripts/stats_usage.py --daily --days 14

# 自定义日期区间
python3 ~/.openclaw/workspace/skills/telemetry-tracker/scripts/stats_usage.py --summary --since 2026-06-01 --until 2026-06-24
```

### 汇报输出形式

- **默认**：在对话内输出结构化中文文本汇报，不生成文件。
- **例外**：仅当用户明确要求「生成报告文件」「导出数据」时，才调用 `--export` 导出 JSONL 或生成 Markdown。

汇报话术模板见 `{baseDir}/references/reporting_template.md`。

---

## 异常处理

| 场景 | 处理 |
|------|------|
| 数据库写入失败 | 自动追加到 `failed_events.jsonl`，不报错、不阻断 |
| 数据库不存在（无数据） | `stats_usage.py` 打印友好提示，不崩溃 |
| 通讯录查询失败/超限 | 跳过第 1 层，进入询问或兜底 |
| 用户拒绝提供姓名 | 使用 user_id 或 unknown，不强制 |

---

## 重要提醒

1. **上报率说明**：自动埋点依赖 LLM 执行规则，实际覆盖率约 70-90%，统计数值应视为「下限」而非精确值。
2. **隐私**：`user_query` 字段会保存用户原始输入（截断 500 字），如含敏感信息需注意。数据库为本地文件，不会上传外部服务。
3. **并发**：SQLite 已开启 WAL 模式 + busy_timeout=5s，正常多 Agent 并发够用。
4. **不入库**：`usage.db` 和 `failed_events.jsonl` 是运行时产物，不应提交到 Git。

## 依赖资源

- `{baseDir}/scripts/track_usage.py` — 上报脚本（含自动建表）
- `{baseDir}/scripts/stats_usage.py` — 统计脚本（summary/by-agent/by-skill/daily/export）
- `{baseDir}/references/reporting_template.md` — 汇报话术模板
