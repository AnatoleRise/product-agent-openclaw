#!/bin/bash
# 飞书需求周报生成器 - 每周五下午运行
# 用法：./weekly-report.sh [webhook_url]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_SCRIPT="$SCRIPT_DIR/weekly-report.js"

# 如果提供了 webhook URL，设置环境变量
if [ -n "$1" ]; then
  export FEISHU_WEBHOOK_URL="$1"
fi

# 运行周报生成脚本
node "$REPORT_SCRIPT"
