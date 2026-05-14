#!/bin/bash
# Refresh requirement board data from Feishu Bitable

# 飞书应用配置 - 通过环境变量注入，勿硬编码
APP_ID="${FEISHU_APP_ID}"
APP_SECRET="${FEISHU_APP_SECRET}"
APP_TOKEN="${FEISHU_APP_TOKEN}"
TABLE_ID="${FEISHU_TABLE_ID}"

# Get access token
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" | jq -r '.tenant_access_token')

# Get records
curl -s "https://open.feishu.cn/open-apis/bitable/v1/apps/$APP_TOKEN/tables/$TABLE_ID/records" \
  -H "Authorization: Bearer $TOKEN" > /tmp/requirement-data.json

# 生成看板 HTML
echo "📊 生成看板 HTML..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 看板输出到当前工作目录（兼容非本地部署）
OUTPUT_DIR="${OUTPUT_DIR:-$(pwd)}"
node "$SCRIPT_DIR/generate-board.js" /tmp/requirement-data.json "$OUTPUT_DIR/requirement-board.html"

echo "✅ 数据刷新 + 看板生成完成"
