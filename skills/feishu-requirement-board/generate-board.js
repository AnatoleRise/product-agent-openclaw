#!/usr/bin/env node
/**
 * 需求看板生成器
 * 从飞书多维表格数据生成 HTML 看板
 * 
 * 用法：node generate-board.js [input.json] [output.html]
 * 默认：输入 /tmp/requirement-data.json, 输出当前目录 requirement-board.html
 * 环境变量: OUTPUT_DIR 可指定输出目录
 */

const fs = require('fs');
const path = require('path');

// 输入输出文件
const inputFile = process.argv[2] || '/tmp/requirement-data.json';
const outputFile = process.argv[3] || path.join(process.cwd(), 'requirement-board.html');

// 读取数据
console.log(`📖 读取数据：${inputFile}`);
const rawData = JSON.parse(fs.readFileSync(inputFile, 'utf-8'));
const records = rawData.data?.items || [];

// 处理数据并转换为 v2 格式
function processRecords(records) {
  const dateFields = ['原定上线时间', '开发开始日期', '技术方案评审日期', '提出需求日期', '提测日期', '真实上线日期'];
  
  return records.filter(r => r.fields && r.fields['标题']).map(record => {
    const fields = record.fields || {};
    
    // 处理日期字段
    dateFields.forEach(field => {
      if (fields[field]) {
        if (typeof fields[field] === 'number') {
          const date = new Date(fields[field]);
          fields[field] = date.toLocaleString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
        } else if (Array.isArray(fields[field])) {
          fields[field] = fields[field].join(' ');
        }
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
      assignee: Array.isArray(fields['相关人员']) ? fields['相关人员'].join(', ') : (fields['相关人员'] || '未分配'),
      plannedDate: fields['原定上线时间'] || '',
      actualDate: fields['真实上线日期'] || '',
      usefulLink: fields['有用链接'] || ''
    };
  });
}

const processedRecords = processRecords(records);
console.log(`✅ 处理完成，共 ${processedRecords.length} 条记录`);

// 生成 HTML
const embeddedData = JSON.stringify(processedRecords);
const updateTime = new Date().toLocaleString('zh-CN');

const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>需求管理看板 - ${updateTime} 更新</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
      -webkit-backdrop-filter: blur(20px);
      padding: 2rem; border-radius: 20px; border: 1px solid rgba(255,255,255,0.2);
    }
    .header h1 { font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }
    .header p { font-size: 1.1rem; opacity: 0.95; }
    .stats {
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.25rem; margin-bottom: 2rem;
    }
    .stat-card {
      background: rgba(255,255,255,0.98); padding: 1.5rem; border-radius: 16px;
      text-align: center; backdrop-filter: blur(20px); box-shadow: 0 10px 40px rgba(0,0,0,0.15);
      transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .stat-card:hover { transform: translateY(-4px); box-shadow: 0 15px 50px rgba(0,0,0,0.2); }
    .stat-number {
      font-size: 3rem; font-weight: 800;
      background: linear-gradient(135deg, var(--primary), var(--primary-dark));
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    .stat-label { color: var(--text-light); font-size: 0.9rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
    .filters {
      background: rgba(255,255,255,0.98); padding: 1.5rem 2rem; border-radius: 16px;
      margin-bottom: 2rem; box-shadow: 0 10px 40px rgba(0,0,0,0.15); backdrop-filter: blur(20px);
    }
    .filter-group { display: flex; gap: 1.5rem; flex-wrap: wrap; align-items: center; }
    .filter-item { display: flex; align-items: center; gap: 0.75rem; }
    .filter-item label { font-weight: 600; color: var(--text); font-size: 0.9rem; }
    .filter-item select {
      padding: 0.6rem 1.2rem; border: 2px solid var(--border); border-radius: 10px;
      font-size: 0.9rem; cursor: pointer; background: white; font-weight: 500;
      transition: all 0.2s;
    }
    .filter-item select:hover { border-color: var(--primary); }
    .filter-item select:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1); }
    .charts-section {
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; margin-bottom: 2rem;
    }
    .chart-card {
      background: rgba(255,255,255,0.98); padding: 1.5rem; border-radius: 16px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.15); backdrop-filter: blur(20px); position: relative;
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
      box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
    }
    .card {
      background: rgba(255,255,255,0.85); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
      border-radius: 14px; padding: 1.25rem; margin-bottom: 1rem;
      border: 2px solid rgba(255,255,255,0.3);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer;
      box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .card:hover {
      transform: translateY(-3px) scale(1.01);
      box-shadow: 0 12px 35px rgba(0,0,0,0.2);
      border-color: rgba(255,255,255,0.5);
      background: rgba(255,255,255,0.95);
    }
    .card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem; gap: 0.5rem; }
    .card-title { font-size: 0.95rem; font-weight: 600; color: var(--text); line-height: 1.5; flex: 1; }
    .priority-badge { padding: 0.25rem 0.65rem; border-radius: 8px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; flex-shrink: 0; }
    .priority-p0 { background: linear-gradient(135deg, #fee2e2, #fecaca); color: #dc2626; border: 1px solid #fca5a5; }
    .priority-p1 { background: linear-gradient(135deg, #fef3c7, #fde68a); color: #d97706; border: 1px solid #fcd34d; }
    .priority-p2 { background: linear-gradient(135deg, #dbeafe, #bfdbfe); color: #2563eb; border: 1px solid #93c5fd; }
    .priority-p3 { background: linear-gradient(135deg, #e0e7ff, #c7d2fe); color: #4f46e5; border: 1px solid #a5b4fc; }
    .card-meta { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.75rem; }
    .meta-tag { background: linear-gradient(135deg, var(--bg), #f1f5f9); padding: 0.3rem 0.65rem; border-radius: 8px; font-size: 0.7rem; color: var(--text-light); font-weight: 600; border: 1px solid var(--border); }
    .card-assignee { font-size: 0.8rem; color: var(--text-light); margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.35rem; }
    .card-assignee::before { content: '👤'; font-size: 0.9rem; }
    .card-dates { display: flex; justify-content: space-between; font-size: 0.7rem; color: var(--text-light); padding-top: 0.75rem; border-top: 1px dashed var(--border); }
    .date-item { display: flex; flex-direction: column; gap: 0.15rem; }
    .date-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.7; }
    .status-badge { display: inline-block; padding: 0.4rem 0.85rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.3px; }
    .status-已上线 { background: linear-gradient(135deg, #d1fae5, #a7f3d0); color: #059669; border: 1px solid #6ee7b7; }
    .status-开发阶段 { background: linear-gradient(135deg, #dbeafe, #bfdbfe); color: #2563eb; border: 1px solid #93c5fd; }
    .status-端测/联调 { background: linear-gradient(135deg, #fef3c7, #fde68a); color: #d97706; border: 1px solid #fcd34d; }
    .status-算法实验 { background: linear-gradient(135deg, #e0e7ff, #c7d2fe); color: #4f46e5; border: 1px solid #a5b4fc; }
    .status-内部测试 { background: linear-gradient(135deg, #fce7f3, #fbcfe8); color: #db2777; border: 1px solid #f9a8d4; }
    .status-需求阶段 { background: linear-gradient(135deg, #f3e8ff, #e9d5ff); color: #9333ea; border: 1px solid #d8b4fe; }
    .status-方案阶段 { background: linear-gradient(135deg, #cffafe, #a5f3fc); color: #0891b2; border: 1px solid #67e8f9; }
    .status-上线阶段 { background: linear-gradient(135deg, #dcfce7, #bbf7d0); color: #16a34a; border: 1px solid #86efac; }
    .status-需求转出 { background: linear-gradient(135deg, #f1f5f9, #e2e8f0); color: #64748b; border: 1px solid #cbd5e1; }
    @media (max-width: 1400px) { .charts-section { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 1200px) { .board { grid-template-columns: repeat(2, 1fr); } .stats { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 768px) { body { padding: 1rem; } .header h1 { font-size: 1.8rem; } .board { grid-template-columns: 1fr; } .stats { grid-template-columns: 1fr; } .filters { padding: 1rem; } .filter-group { flex-direction: column; align-items: stretch; } .filter-item { justify-content: space-between; } }
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
      <div class="stat-card"><div class="stat-number" id="completed" style="background:linear-gradient(135deg,#10b981,#059669);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">0</div><div class="stat-label">已上线</div></div>
      <div class="stat-card"><div class="stat-number" id="inProgress" style="background:linear-gradient(135deg,#f59e0b,#d97706);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">0</div><div class="stat-label">进行中</div></div>
      <div class="stat-card"><div class="stat-number" id="p0Count" style="background:linear-gradient(135deg,#ef4444,#dc2626);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">0</div><div class="stat-label">P0 紧急</div></div>
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
        type: 'doughnut',
        data: { labels: Object.keys(statusCounts), datasets: [{ data: Object.values(statusCounts), backgroundColor: ['#a78bfa', '#60a5fa', '#34d399', '#fbbf24', '#f87171', '#f472b6', '#22d3ee', '#10b981', '#94a3b8'] }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { boxWidth: 12, font: { size: 10 } } } } }
      });
      const moduleCounts = {}; requirements.forEach(r => { moduleCounts[r.module] = (moduleCounts[r.module] || 0) + 1; });
      charts.module = new Chart(document.getElementById('moduleChart'), {
        type: 'bar',
        data: { labels: Object.keys(moduleCounts), datasets: [{ label: '需求数', data: Object.values(moduleCounts), backgroundColor: 'rgba(99, 102, 241, 0.7)', borderColor: '#6366f1', borderWidth: 1, borderRadius: 6 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }
      });
      const priorityCounts = { P0: 0, P1: 0, P2: 0, P3: 0 }; requirements.forEach(r => { if (priorityCounts[r.priority] !== undefined) priorityCounts[r.priority]++; });
      charts.priority = new Chart(document.getElementById('priorityChart'), {
        type: 'pie',
        data: { labels: ['P0', 'P1', 'P2', 'P3'], datasets: [{ data: [priorityCounts.P0, priorityCounts.P1, priorityCounts.P2, priorityCounts.P3], backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6', '#10b981'] }] },
        options: { responsive: true, maintainAspectRatio: true, aspectRatio: 1, plugins: { legend: { position: 'right', labels: { boxWidth: 12, font: { size: 10 } } } } }
      });
      const monthlyData = {}; requirements.filter(r => r.actualDate).forEach(r => { const month = r.actualDate.substring(0, 7); monthlyData[month] = (monthlyData[month] || 0) + 1; });
      const sortedMonths = Object.keys(monthlyData).sort();
      charts.trend = new Chart(document.getElementById('trendChart'), {
        type: 'line',
        data: { labels: sortedMonths, datasets: [{ label: '完成数', data: sortedMonths.map(m => monthlyData[m]), borderColor: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.1)', fill: true, tension: 0.4, pointRadius: 4, pointBackgroundColor: '#10b981' }] },
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
      const usefulLinkHtml = req.usefulLink ? '<a href="' + req.usefulLink + '" target="_blank" style="display:inline-flex;align-items:center;gap:0.35rem;background:linear-gradient(135deg,#10b981,#059669);color:white;padding:0.4rem 0.85rem;border-radius:8px;text-decoration:none;font-size:0.75rem;font-weight:600;transition:all 0.3s;box-shadow:0 2px 8px rgba(16,185,129,0.2);"><span>🔗</span><span>有用链接</span></a>' : '';
      return '<div class="card"><div class="card-header"><div class="card-title">' + req.title + '</div><span class="priority-badge priority-' + req.priority.toLowerCase() + '">' + req.priority + '</span></div><div class="card-meta"><span class="meta-tag">📁 ' + req.module + '</span><span class="status-badge status-' + req.status.replace(/\\//g, '/') + '">' + req.status + '</span></div><div class="card-assignee">' + req.assignee + '</div><div class="card-dates"><div class="date-item"><span class="date-label">计划</span><span>' + (req.plannedDate || '-') + '</span></div><div class="date-item"><span class="date-label">实际</span><span>' + (req.actualDate || '-') + '</span></div></div>' + usefulLinkHtml + '</div>';
    }
    // 页面加载完成后初始化
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
    } else {
      init();
    }
  </script>
</body>
</html>`;

// 写入文件
fs.writeFileSync(outputFile, html);
console.log(`✅ 看板已生成：${outputFile}`);
console.log(`📈 记录数：${processedRecords.length}`);
