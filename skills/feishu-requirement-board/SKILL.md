---
name: feishu-requirement-board
description: "Generate requirement management dashboard from Feishu Bitable (multidimensional table). Activate when user mentions 生成需求看板，需求看板，requirement board or similar phrases in Feishu chat context with a Bitable URL provided."
metadata:
  {
    "openclaw":
      {
        "emoji": "📊",
        "requires": { "bins": ["curl", "jq"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "jq",
              "bins": ["jq"],
              "label": "Install jq (brew)",
            },
          ],
      },
  }
---

# Feishu Requirement Board Generator

🦞 红温 AI 助手 - 需求管理看板生成器

## 触发条件

用户说以下短语时激活：
- "生成需求看板"
- "需求看板"
- "requirement board"
- "做个需求仪表盘"
- "导出需求数据"

可附带飞书多维表格 URL。

## 快速开始

### 方式 1: 通过 OpenClaw（推荐）

在飞书中说：
```
生成需求看板
```

### 方式 2: 手动执行

```bash
# 1. 刷新数据
bash skills/feishu-requirement-board/refresh.sh

# 2. 生成看板
node skills/feishu-requirement-board/generate-board.js

# 3. 打开看板
open $OUTPUT_DIR/requirement-board.html
```

## 配置 (TOOLS.md)

### 飞书应用配置
- **App ID:** `your_app_id`
- **App Secret:** `your_app_secret`

### 飞书多维表格
- **默认 Bitable URL:** `https://my.feishu.cn/base/your_app_token
- **AppToken:** `your_app_token`
- **Table ID:** `your_table_id`

## 文件结构

```
skills/feishu-requirement-board/
├── SKILL.md              # 本文件（Skill 定义）
├── refresh.sh            # 数据刷新脚本（获取飞书数据）
├── generate-board.js     # 看板生成脚本（生成 HTML）
├── weekly-report.js      # 周报生成脚本
├── weekly-report.sh      # 周报执行脚本
└── setup-cron.sh         # Cron 配置脚本
```

## 核心实现

### Step 1: 提取 Bitable Token

从 URL 解析 app_token：
```
URL: https://my.feishu.cn/base/your_app_token
→ app_token: your_app_token
```

### Step 2: 获取 Access Token

```javascript
const https = require('https');

function getAccessToken() {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      app_id: 'your_app_id',
      app_secret: 'your_app_secret'
    });
    
    const options = {
      hostname: 'open.feishu.cn',
      port: 443,
      path: '/open-apis/auth/v3/tenant_access_token/internal',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    };
    
    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        const result = JSON.parse(body);
        if (result.code === 0) {
          resolve(result.tenant_access_token);
        } else {
          reject(new Error(result.msg));
        }
      });
    });
    
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}
```

### Step 3: 读取多维表格数据

```javascript
// 列出所有表格
async function listTables(appToken, accessToken) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'open.feishu.cn',
      port: 443,
      path: `/open-apis/bitable/v1/apps/${appToken}/tables`,
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    };
    
    https.get(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => resolve(JSON.parse(body)));
    }).on('error', reject);
  });
}

// 读取记录（注意 URL 编码！）
async function listRecords(appToken, tableId, accessToken, fieldNames) {
  return new Promise((resolve, reject) => {
    const encodedFieldNames = fieldNames.map(f => encodeURIComponent(f)).join(',');
    const path = `/open-apis/bitable/v1/apps/${appToken}/tables/${tableId}/records?field_names[]=${encodedFieldNames}`;
    
    const options = {
      hostname: 'open.feishu.cn',
      port: 443,
      path: path,
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    };
    
    https.get(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => resolve(JSON.parse(body)));
    }).on('error', reject);
  });
}
```

### Step 4: 处理数据并转换为 v2 格式

```javascript
function processRecords(records) {
  const dateFields = ['原定上线时间', '开发开始时间', '技术方案评审时间', '提出需求时间', '提测时间', '真实上线时间'];
  
  return records.map(record => {
    const fields = record.fields || {};
    
    // 处理日期字段
    dateFields.forEach(field => {
      if (Array.isArray(fields[field])) {
        fields[field] = fields[field].join(' ');
      }
    });
    
    // 转换重要性为 priority (P0/P1/P2/P3)
    let priority = 'P3';
    const importance = fields['重要性'] || '';
    if (importance.includes('⚠️ 高') || importance.includes('P0')) priority = 'P0';
    else if (importance.includes('⚡ 中') || importance.includes('P1')) priority = 'P1';
    else if (importance.includes('📌 低') || importance.includes('P2')) priority = 'P2';
    
    // 转换 v2 格式
    return {
      id: record.id,
      title: fields['标题'] || '未命名需求',
      priority: priority,
      status: fields['状态'] || '需求阶段',
      module: fields['一级模块'] || '未分类',
      assignee: fields['相关人员'] || '未分配',
      plannedDate: fields['原定上线时间'] || '',
      actualDate: fields['真实上线时间'] || '',
      usefulLink: fields['有用链接'] || ''
    };
  });
}
```

**字段映射关系：**

| 飞书字段 | v2 字段 | 转换规则 |
|---------|--------|----------|
| 重要性：⚠️ 高 | priority: "P0" | 紧急/高优先级 |
| 重要性：⚡ 中 | priority: "P1" | 中等优先级 |
| 重要性：📌 低 | priority: "P2" | 低优先级 |
| 无重要性标记 | priority: "P3" | 默认 P3 |
| 状态 | status | 直接映射 |
| 一级模块 | module | 直接映射 |
| 相关人员 | assignee | 直接映射 |
| 原定上线时间 | plannedDate | 直接映射 |
| 真实上线时间 | actualDate | 直接映射 |
| 有用链接 | usefulLink | 直接映射 |

### Step 5: 生成 HTML 仪表盘 (使用正式脚本)

**看板生成脚本已独立为正式文件：**

```
skills/feishu-requirement-board/generate-board.js
```

**用法：**
```bash
# 默认：从 /tmp/requirement-data.json 读取，输出到当前目录 requirement-board.html
# 可通过环境变量 OUTPUT_DIR 指定输出目录
node skills/feishu-requirement-board/generate-board.js

# 自定义输入输出
node skills/feishu-requirement-board/generate-board.js /path/to/input.json /path/to/output.html

# 或指定输出目录
OUTPUT_DIR=/path/to/output node skills/feishu-requirement-board/generate-board.js
node skills/feishu-requirement-board/generate-board.js /path/to/input.json /path/to/output.html
```

**核心处理逻辑（供参考）：**

```javascript
function generateHTML(records) {
  const embeddedData = JSON.stringify(records);
  const updateTime = new Date().toLocaleString('zh-CN');
  
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>需求管理看板 - ${updateTime} 更新</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    :root {
      --primary: #6366f1; --primary-dark: #4f46e5; --success: #10b981;
      --warning: #f59e0b; --danger: #ef4444; --info: #3b82f6;
      --bg: #f8fafc; --card-bg: #ffffff; --text: #1e293b;
      --text-light: #64748b; --border: #e2e8f0;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', 'Microsoft YaHei', sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh; padding: 2rem;
    }
    .container { max-width: 1600px; margin: 0 auto; }
    .header {
      text-align: center; margin-bottom: 2rem; color: white;
      background: rgba(255,255,255,0.1); backdrop-filter: blur(20px);
      padding: 2rem; border-radius: 20px; border: 1px solid rgba(255,255,255,0.2);
    }
    .header h1 { font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; }
    .header p { font-size: 1.1rem; opacity: 0.95; }
    .stats {
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.25rem; margin-bottom: 2rem;
    }
    .stat-card {
      background: rgba(255,255,255,0.98); padding: 1.5rem; border-radius: 16px;
      text-align: center; backdrop-filter: blur(20px); box-shadow: 0 10px 40px rgba(0,0,0,0.15);
      transition: transform 0.3s ease;
    }
    .stat-card:hover { transform: translateY(-4px); }
    .stat-number {
      font-size: 3rem; font-weight: 800;
      background: linear-gradient(135deg, var(--primary), var(--primary-dark));
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .stat-label { color: var(--text-light); font-size: 0.9rem; font-weight: 500; }
    .filters {
      background: rgba(255,255,255,0.98); padding: 1.5rem 2rem; border-radius: 16px;
      margin-bottom: 2rem; box-shadow: 0 10px 40px rgba(0,0,0,0.15);
    }
    .filter-group { display: flex; gap: 1.5rem; flex-wrap: wrap; align-items: center; }
    .filter-item { display: flex; align-items: center; gap: 0.75rem; }
    .filter-item label { font-weight: 600; color: var(--text); font-size: 0.9rem; }
    .filter-item select {
      padding: 0.6rem 1.2rem; border: 2px solid var(--border); border-radius: 10px;
      font-size: 0.9rem; cursor: pointer; background: white; font-weight: 500;
    }
    .filter-item select:focus { outline: none; border-color: var(--primary); }
    .charts-section {
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; margin-bottom: 2rem;
    }
    .chart-card {
      background: rgba(255,255,255,0.98); padding: 1.5rem; border-radius: 16px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.15); position: relative;
    }
    .chart-card h3 { font-size: 1rem; font-weight: 700; color: var(--text); margin-bottom: 1rem; text-align: center; }
    .chart-card canvas { max-width: 100%; max-height: 250px; }
    .board {
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; align-items: start;
    }
    .column {
      background: rgba(255,255,255,0.95); border-radius: 20px; padding: 1.25rem;
      box-shadow: 0 10px 40px rgba(0,0,0,0.15); backdrop-filter: blur(20px); min-height: 500px;
    }
    .column-header {
      display: flex; justify-content: space-between; align-items: center;
      margin-bottom: 1.25rem; padding: 1rem; border-radius: 12px;
      background: linear-gradient(135deg, var(--bg), #f1f5f9);
    }
    .column-title { font-size: 1rem; font-weight: 700; color: var(--text); display: flex; align-items: center; gap: 0.5rem; }
    .column-count {
      background: linear-gradient(135deg, var(--primary), var(--primary-dark));
      color: white; padding: 0.3rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 700;
    }
    .card {
      background: rgba(255,255,255,0.85); border-radius: 14px; padding: 1.25rem;
      margin-bottom: 1rem; border: 2px solid rgba(255,255,255,0.3);
      transition: all 0.3s; cursor: pointer; box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .card:hover { transform: translateY(-3px); box-shadow: 0 12px 35px rgba(0,0,0,0.2); }
    .card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem; gap: 0.5rem; }
    .card-title { font-size: 0.95rem; font-weight: 600; color: var(--text); line-height: 1.5; flex: 1; }
    .priority-badge { padding: 0.25rem 0.65rem; border-radius: 8px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; }
    .priority-p0 { background: linear-gradient(135deg, #fee2e2, #fecaca); color: #dc2626; border: 1px solid #fca5a5; }
    .priority-p1 { background: linear-gradient(135deg, #fef3c7, #fde68a); color: #d97706; border: 1px solid #fcd34d; }
    .priority-p2 { background: linear-gradient(135deg, #dbeafe, #bfdbfe); color: #2563eb; border: 1px solid #93c5fd; }
    .priority-p3 { background: linear-gradient(135deg, #e0e7ff, #c7d2fe); color: #4f46e5; border: 1px solid #a5b4fc; }
    .card-meta { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.75rem; }
    .meta-tag { background: linear-gradient(135deg, var(--bg), #f1f5f9); padding: 0.3rem 0.65rem; border-radius: 8px; font-size: 0.7rem; color: var(--text-light); font-weight: 600; }
    .card-assignee { font-size: 0.8rem; color: var(--text-light); margin-bottom: 0.75rem; }
    .card-dates { display: flex; justify-content: space-between; font-size: 0.7rem; color: var(--text-light); padding-top: 0.75rem; border-top: 1px dashed var(--border); }
    .status-badge { display: inline-block; padding: 0.4rem 0.85rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
    .status-已上线 { background: linear-gradient(135deg, #d1fae5, #a7f3d0); color: #059669; }
    .status-开发阶段 { background: linear-gradient(135deg, #dbeafe, #bfdbfe); color: #2563eb; }
    .status-端测/联调 { background: linear-gradient(135deg, #fef3c7, #fde68a); color: #d97706; }
    .status-算法实验 { background: linear-gradient(135deg, #e0e7ff, #c7d2fe); color: #4f46e5; }
    .status-内部测试 { background: linear-gradient(135deg, #fce7f3, #fbcfe8); color: #db2777; }
    .status-需求阶段 { background: linear-gradient(135deg, #f3e8ff, #e9d5ff); color: #9333ea; }
    .status-方案阶段 { background: linear-gradient(135deg, #cffafe, #a5f3fc); color: #0891b2; }
    .status-上线阶段 { background: linear-gradient(135deg, #dcfce7, #bbf7d0); color: #16a34a; }
    .status-需求转出 { background: linear-gradient(135deg, #f1f5f9, #e2e8f0); color: #64748b; }
    @media (max-width: 1400px) { .charts-section { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 1200px) { .board { grid-template-columns: repeat(2, 1fr); } .stats { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 768px) { body { padding: 1rem; } .board { grid-template-columns: 1fr; } .stats { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📋 需求管理看板</h1>
      <p>实时追踪项目进度与需求状态</p>
    </div>
    <div class="stats">
      <div class="stat-card"><div class="stat-number" id="total">0</div><div class="stat-label">总需求数</div></div>
      <div class="stat-card"><div class="stat-number" id="completed" style="background:linear-gradient(135deg,#10b981,#059669);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">0</div><div class="stat-label">已上线</div></div>
      <div class="stat-card"><div class="stat-number" id="inProgress" style="background:linear-gradient(135deg,#f59e0b,#d97706);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">0</div><div class="stat-label">进行中</div></div>
      <div class="stat-card"><div class="stat-number" id="p0Count" style="background:linear-gradient(135deg,#ef4444,#dc2626);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">0</div><div class="stat-label">P0 紧急</div></div>
    </div>
    <div class="charts-section">
      <div class="chart-card"><h3>📊 需求状态分布</h3><canvas id="statusChart"></canvas></div>
      <div class="chart-card"><h3>📈 模块分布</h3><canvas id="moduleChart"></canvas></div>
      <div class="chart-card"><h3>🎯 优先级分布</h3><canvas id="priorityChart"></canvas></div>
      <div class="chart-card"><h3>📅 完成趋势</h3><canvas id="trendChart"></canvas></div>
    </div>
    <div class="filters">
      <div class="filter-group">
        <div class="filter-item"><label>📁 模块:</label><select id="moduleFilter"><option value="all">全部</option></select></div>
        <div class="filter-item"><label>🎯 优先级:</label><select id="priorityFilter"><option value="all">全部</option><option value="P0">P0</option><option value="P1">P1</option><option value="P2">P2</option><option value="P3">P3</option></select></div>
        <div class="filter-item"><label>📊 状态:</label><select id="statusFilter"><option value="all">全部</option></select></div>
      </div>
    </div>
    <div class="board" id="board"></div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
    const requirements = ${embeddedData};
    const statusOrder = ['需求阶段', '方案阶段', '开发阶段', '端测/联调', '算法实验', '内部测试', '上线阶段', '已上线', '需求转出'];
    let charts = {};
    function init() { renderStats(); populateFilters(); renderCharts(); renderBoard(); setupFilters(); }
    function renderStats() {
      document.getElementById('total').textContent = requirements.length;
      document.getElementById('completed').textContent = requirements.filter(r => r.status === '已上线').length;
      document.getElementById('inProgress').textContent = requirements.filter(r => r.status !== '已上线').length;
      document.getElementById('p0Count').textContent = requirements.filter(r => r.priority === 'P0').length;
    }
    function populateFilters() {
      const modules = [...new Set(requirements.map(r => r.module))];
      const statuses = [...new Set(requirements.map(r => r.status))];
      const moduleSelect = document.getElementById('moduleFilter');
      modules.forEach(m => { const opt = document.createElement('option'); opt.value = m; opt.textContent = m; moduleSelect.appendChild(opt); });
      const statusSelect = document.getElementById('statusFilter');
      statuses.sort((a, b) => statusOrder.indexOf(a) - statusOrder.indexOf(b));
      statuses.forEach(s => { const opt = document.createElement('option'); opt.value = s; opt.textContent = s; statusSelect.appendChild(opt); });
    }
    function setupFilters() {
      document.getElementById('moduleFilter').addEventListener('change', renderBoard);
      document.getElementById('priorityFilter').addEventListener('change', renderBoard);
      document.getElementById('statusFilter').addEventListener('change', renderBoard);
    }
    function renderCharts() {
      const statusCounts = {}; requirements.forEach(r => { statusCounts[r.status] = (statusCounts[r.status] || 0) + 1; });
      charts.status = new Chart(document.getElementById('statusChart'), {
        type: 'doughnut', data: { labels: Object.keys(statusCounts), datasets: [{ data: Object.values(statusCounts), backgroundColor: ['#a78bfa', '#60a5fa', '#34d399', '#fbbf24', '#f87171', '#f472b6', '#22d3ee', '#10b981', '#94a3b8'] }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { boxWidth: 12, font: { size: 10 } } } } }
      });
      const moduleCounts = {}; requirements.forEach(r => { moduleCounts[r.module] = (moduleCounts[r.module] || 0) + 1; });
      charts.module = new Chart(document.getElementById('moduleChart'), {
        type: 'bar', data: { labels: Object.keys(moduleCounts), datasets: [{ label: '需求数', data: Object.values(moduleCounts), backgroundColor: 'rgba(99, 102, 241, 0.7)', borderColor: '#6366f1', borderWidth: 1, borderRadius: 6 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }
      });
      const priorityCounts = { P0: 0, P1: 0, P2: 0, P3: 0 }; requirements.forEach(r => { if (priorityCounts[r.priority] !== undefined) priorityCounts[r.priority]++; });
      charts.priority = new Chart(document.getElementById('priorityChart'), {
        type: 'pie', data: { labels: ['P0', 'P1', 'P2', 'P3'], datasets: [{ data: [priorityCounts.P0, priorityCounts.P1, priorityCounts.P2, priorityCounts.P3], backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6', '#10b981'] }] },
        options: { responsive: true, maintainAspectRatio: true, aspectRatio: 1, plugins: { legend: { position: 'right', labels: { boxWidth: 12, font: { size: 10 } } } } }
      });
      const monthlyData = {}; requirements.filter(r => r.actualDate).forEach(r => { const month = r.actualDate.substring(0, 7); monthlyData[month] = (monthlyData[month] || 0) + 1; });
      const sortedMonths = Object.keys(monthlyData).sort();
      charts.trend = new Chart(document.getElementById('trendChart'), {
        type: 'line', data: { labels: sortedMonths, datasets: [{ label: '完成数', data: sortedMonths.map(m => monthlyData[m]), borderColor: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.1)', fill: true, tension: 0.4, pointRadius: 4, pointBackgroundColor: '#10b981' }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }
      });
    }
    function getFilteredRequirements() {
      const module = document.getElementById('moduleFilter').value;
      const priority = document.getElementById('priorityFilter').value;
      const status = document.getElementById('statusFilter').value;
      return requirements.filter(r => (module === 'all' || r.module === module) && (priority === 'all' || r.priority === priority) && (status === 'all' || r.status === status));
    }
    function renderBoard() {
      const filtered = getFilteredRequirements();
      const grouped = {};
      filtered.forEach(r => { if (!grouped[r.status]) grouped[r.status] = []; grouped[r.status].push(r); });
      const board = document.getElementById('board');
      board.innerHTML = '';
      statusOrder.forEach(status => {
        if (!grouped[status]) return;
        const column = document.createElement('div');
        column.className = 'column';
        column.innerHTML = '<div class="column-header"><span class="column-title">' + status + '</span><span class="column-count">' + grouped[status].length + '</span></div>' + grouped[status].map(card => createCard(card)).join('');
        board.appendChild(column);
      });
    }
    function createCard(req) {
      const usefulLinkHtml = req.usefulLink ? '<a href="' + req.usefulLink + '" target="_blank" style="display:inline-flex;align-items:center;gap:0.35rem;background:linear-gradient(135deg,#10b981,#059669);color:white;padding:0.4rem 0.85rem;border-radius:8px;text-decoration:none;font-size:0.75rem;font-weight:600;margin-top:0.75rem;">🔗 有用链接</a>' : '';
      return '<div class="card"><div class="card-header"><div class="card-title">' + req.title + '</div><span class="priority-badge priority-' + req.priority.toLowerCase() + '">' + req.priority + '</span></div><div class="card-meta"><span class="meta-tag">📁 ' + req.module + '</span><span class="status-badge status-' + req.status.replace(/\//g, '\\/') + '">' + req.status + '</span></div><div class="card-assignee">👤 ' + req.assignee + '</div><div class="card-dates"><div class="date-item"><span class="date-label">计划</span><span>' + (req.plannedDate || '-') + '</span></div><div class="date-item"><span class="date-label">实际</span><span>' + (req.actualDate || '-') + '</span></div></div>' + usefulLinkHtml + '</div>';
    }
    init();
  </script>
</body>
</html>`;
}
```

### Step 6: 完整工作流程

**一键刷新 + 生成：**

```bash
# 1. 刷新数据
bash skills/feishu-requirement-board/refresh.sh

# 2. 生成看板
node skills/feishu-requirement-board/generate-board.js

# 3. 打开看板
open $OUTPUT_DIR/requirement-board.html
```

**自动化（Cron）：**

每周五 11:00 自动刷新（已在 setup-cron.sh 中配置）：

```bash
# 编辑 crontab
crontab -e

# 添加任务（每周五 11:00）
0 11 * * 5 OUTPUT_DIR=/path/to/output bash skills/feishu-requirement-board/refresh.sh
```

## 关键注意事项

### 1. URL 编码问题

| 问题 | 解决方案 |
|------|----------|
| `field_names[]` 参数包含未转义的 `[]` | 使用 `encodeURIComponent()` 或手动替换 `[]` → `%5B%5D` |
| 错误示例：`field_names[]=字段名` | 正确示例：`field_names%5B%5D=字段名` |

### 2. 日期字段格式

| 问题 | 解决方案 |
|------|----------|
| 飞书返回日期为数组 `["August 15", "2025"]` | 使用 `array.join(' ')` 转换为字符串 |
| 直接渲染会导致 HTML 显示异常 | 在 `processRecords()` 中预处理 |

### 3. 脚本执行顺序

| 顺序 | 内容 |
|------|------|
| 1️⃣ | 定义所有函数 (`loadData`, `initDashboard`, `initCharts` 等) |
| 2️⃣ | 定义 `window.EMBEDDED_DATA = {...}` |
| 3️⃣ | 调用 `loadData()`（在 `</body>` 之前） |

修复命令：
```bash
sed -i '' 's|</body>|<script>loadData();</script></body>|' file.html
```

### 4. file:// 协议 CORS 问题

| 问题 | 解决方案 |
|------|----------|
| 通过 `file://` 打开 HTML 时 `fetch()` 被阻止 | 直接嵌入数据为 `window.EMBEDDED_DATA`，不要 fetch 外部 JSON |

## 看板功能

### 交互式筛选

- 🔍 关键词搜索 - 搜索标题和内容
- 📁 模块筛选 - 按一级模块筛选（全网搜/云盘知识库/邮箱需求等）
- 📊 状态筛选 - 按开发状态筛选（已上线/开发中/需求阶段等）
- 🚀 部署筛选 - 按部署状态筛选（未部署/已部署）
- ⚡ 优先级筛选 - 按重要性筛选（📌低/⚡中/⚠️高）
- 🔄 排序选项 - 按不同字段排序

### 可视化图表

- 📈 趋势图 - 月度需求趋势（按优先级分解）
- 🥧 状态分布饼图 - 开发状态分布
- 📊 模块分布柱状图 - 各模块需求数量
- 🎯 优先级统计 - 颜色编码的优先级计数卡片

## 刷新脚本

刷新脚本位于：`skills/feishu-requirement-board/refresh.sh`

**使用方法：**
```bash
cd /path/to/workspace
OUTPUT_DIR=. bash skills/feishu-requirement-board/refresh.sh
```

## API 端点参考

```
POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
GET https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables
GET https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields
GET https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records
```

## 示例对话

**User:** 生成需求看板 https://my.feishu.cn/base/your_app_token

**Assistant:**
```
✅ 需求看板已生成！

📊 概览:
- 总需求：37 个
- 高优先级 (⚠️ 高): 5 个
- 中优先级 (⚡ 中): 20 个
- 低优先级 (📌 低): 12 个

📁 文件位置:
- HTML 看板：$OUTPUT_DIR/requirement-board.html
- 原始数据：/tmp/requirement-data.json（临时）

💡 提示：用浏览器打开 HTML 文件查看可视化仪表盘
```

## 维护计划

| 周期 | 任务 |
|------|------|
| 每日 | 检查是否有新需求添加到多维表格 |
| 每周 | 审查已完成需求，更新状态（自动刷新周五 11:00） |
| 每月 | 归档旧需求，清理仪表盘 |

## 相关文档

- Skill 位置：`skills/feishu-requirement-board/SKILL.md`
- 配置方式：`OUTPUT_DIR` 环境变量指定输出目录
- 生成文件：`$OUTPUT_DIR/requirement-board.html`

---
🦞 红温 AI 助手 - 有问题随时找我！
