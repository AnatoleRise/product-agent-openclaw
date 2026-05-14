#!/usr/bin/env node
/**
 * 飞书需求周报生成器
 * 每周五下午运行，分析需求多维表格并生成周报
 */

const https = require('https');
const fs = require('fs');

const path = require('path');

// 配置
const CONFIG = {
  APP_ID: process.env.FEISHU_APP_ID || '',
  APP_SECRET: process.env.FEISHU_APP_SECRET || '',
  APP_TOKEN: process.env.FEISHU_APP_TOKEN || '',
  TABLE_ID: process.env.FEISHU_TABLE_ID || '',
  OUTPUT_DIR: process.env.OUTPUT_DIR || process.cwd(),
  // 飞书机器人 open_id（通过环境变量注入）
  BOT_OPEN_ID: process.env.FEISHU_BOT_OPEN_ID || '',
  // 接收周报的飞书用户 ID（open_id）
  RECIPIENT_ID: process.env.RECIPIENT_ID || null,
  // 或者使用 webhook URL（二选一）
  WEBHOOK_URL: process.env.FEISHU_WEBHOOK_URL || null
};

// 字段定义
const FIELD_NAMES = [
  '标题',
  '重要性',
  '一级模块',
  '二级模块',
  '状态',
  '当前状态',
  '原定上线时间',
  '真实上线时间',
  '提测时间',
  '相关人员',
  '提出需求时间',
  '最后修改时间'
];

/**
 * 获取 Access Token
 */
function getAccessToken() {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      app_id: CONFIG.APP_ID,
      app_secret: CONFIG.APP_SECRET
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
          reject(new Error(`获取 token 失败：${result.msg}`));
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

/**
 * 获取多维表格记录
 */
function listRecords(accessToken) {
  return new Promise((resolve, reject) => {
    const encodedFieldNames = FIELD_NAMES.map(f => encodeURIComponent(f)).join(',');
    const path = `/open-apis/bitable/v1/apps/${CONFIG.APP_TOKEN}/tables/${CONFIG.TABLE_ID}/records?field_names[]=${encodedFieldNames}&page_size=500`;

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
      res.on('end', () => {
        const result = JSON.parse(body);
        if (result.code === 0) {
          resolve(result.data.items);
        } else {
          reject(new Error(`获取记录失败：${result.msg}`));
        }
      });
    }).on('error', reject);
  });
}

/**
 * 解析飞书日期字段
 */
function parseFeishuDate(dateValue) {
  if (!dateValue || !Array.isArray(dateValue) || dateValue.length === 0) {
    return null;
  }
  
  // 飞书日期格式：["August 15", "2025"] 或 ["2025-08-15"]
  if (dateValue.length === 2 && !dateValue[1].includes('-')) {
    // 格式：["August 15", "2025"]
    const dateStr = `${dateValue[0]} ${dateValue[1]}`;
    return new Date(dateStr);
  } else {
    // 格式：["2025-08-15"]
    return new Date(dateValue[0]);
  }
}

/**
 * 处理记录数据
 */
function processRecords(records) {
  const dateFields = ['原定上线时间', '提测时间', '真实上线时间', '提出需求时间', '最后修改时间'];
  
  return records.map(record => {
    const processed = { 
      id: record.id,
      fields: { ...record.fields }
    };
    
    dateFields.forEach(field => {
      const fieldValue = processed.fields[field];
      // 处理飞书日期字段：可能是字符串、数组或 null
      if (fieldValue) {
        if (typeof fieldValue === 'string' && fieldValue.includes('T')) {
          // ISO 字符串格式
          const dateVal = new Date(fieldValue);
          processed.fields[field] = dateVal;
          processed.fields[`${field}_str`] = dateVal.toISOString().split('T')[0];
        } else if (Array.isArray(fieldValue) && fieldValue.length > 0) {
          const dateVal = parseFeishuDate(fieldValue);
          processed.fields[field] = dateVal;
          processed.fields[`${field}_str`] = dateVal ? dateVal.toISOString().split('T')[0] : null;
        } else {
          processed.fields[field] = null;
          processed.fields[`${field}_str`] = null;
        }
      } else {
        processed.fields[field] = null;
        processed.fields[`${field}_str`] = null;
      }
    });
    
    return processed;
  });
}

/**
 * 分析需求数据
 */
function analyzeRequirements(records) {
  const now = new Date();
  const todayStr = now.toISOString().split('T')[0];
  
  // 计算一周前的日期
  const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
  const weekAgoStr = weekAgo.toISOString().split('T')[0];
  
  // 所有记录（不过滤）
  const totalRecords = records;
  
  // 过滤掉已转出的需求
  const activeRecords = records.filter(r => 
    r.fields['状态'] !== '需求转出'
  );
  
  // 延期需求（只关注高/中优先级，且状态不是已上线或需求转出）
  const overdueRequirements = [];
  activeRecords.forEach(r => {
    const launchDateStr = r.fields['原定上线时间_str'];
    const status = r.fields['状态'];
    const importance = r.fields['重要性'] || '📌 低';
    
    // 已上线的需求不算延期
    if (status === '已上线' || status === '需求转出') {
      return;
    }
    
    // 只关注高/中优先级
    if (importance !== '⚠️ 高' && importance !== '⚡ 中') {
      return;
    }
    
    // 使用字符串日期计算（更可靠）
    if (launchDateStr) {
      const launchDateObj = new Date(launchDateStr);
      if (launchDateObj < now) {
        const daysOverdue = Math.floor((now - launchDateObj) / (24 * 60 * 60 * 1000));
        overdueRequirements.push({ ...r, daysOverdue, launchDateStr, importance });
      }
    }
  });
  
  // 按重要性排序（高 > 中），同优先级按延期天数排序
  overdueRequirements.sort((a, b) => {
    const importanceOrder = { '⚠️ 高': 0, '⚡ 中': 1, '📌 低': 2 };
    const aOrder = importanceOrder[a.importance] || 2;
    const bOrder = importanceOrder[b.importance] || 2;
    if (aOrder !== bOrder) {
      return aOrder - bOrder;
    }
    return b.daysOverdue - a.daysOverdue; // 延期天数多的在前
  });
  
  // 优先级分布统计
  const priorityDist = { '⚠️ 高': 0, '⚡ 中': 0, '📌 低': 0 };
  activeRecords.forEach(r => {
    const imp = r.fields['重要性'] || '📌 低';
    priorityDist[imp] = (priorityDist[imp] || 0) + 1;
  });
  
  // 状态分布统计
  const statusDist = {};
  activeRecords.forEach(r => {
    const status = r.fields['状态'] || '未知';
    statusDist[status] = (statusDist[status] || 0) + 1;
  });
  
  // 模块分布统计
  const moduleDist = {};
  activeRecords.forEach(r => {
    const module = r.fields['一级模块'] || '未分类';
    moduleDist[module] = (moduleDist[module] || 0) + 1;
  });
  
  return {
    total: totalRecords.length,
    activeTotal: activeRecords.length,
    weekAgoStr,
    todayStr,
    overdueRequirements,
    priorityDist,
    statusDist,
    moduleDist
  };
}

/**
 * 生成周报文本（参考用户提供的格式）
 */
function generateWeeklyReport(analysis) {
  const { total, activeTotal, weekAgoStr, todayStr, overdueRequirements, priorityDist, statusDist, moduleDist } = analysis;
  
  // 格式化日期范围（如：3 月 27 日 - 4 月 3 日）
  const weekAgoDate = new Date(weekAgoStr);
  const todayDate = new Date(todayStr);
  const weekAgoMonth = weekAgoDate.getMonth() + 1;
  const weekAgoDay = weekAgoDate.getDate();
  const todayMonth = todayDate.getMonth() + 1;
  const todayDay = todayDate.getDate();
  const dateRange = `${weekAgoMonth}月${weekAgoDay}日 - ${todayMonth}月${todayDay}日`;
  
  let report = `📊 需求周报 (${dateRange})\n\n`;
  
  // === 数据更新提醒 ===
  report += `⚠️ 数据更新提醒\n`;
  report += `本周表格数据${total > 0 ? '没有明显变化' : '为空'}（记录数：${total} 条）\n`;
  report += `💡 提醒：请及时更新表格中的需求状态、进度和关键时间点！\n\n`;
  
  // === 延期风险警报 ===
  report += `🚨 延期风险警报\n`;
  if (overdueRequirements.length > 0) {
    report += `发现 ${overdueRequirements.length} 个需求存在延期风险：\n`;
    overdueRequirements.slice(0, 10).forEach((r, i) => {
      const title = r.fields['标题'] || '未命名需求';
      const daysOverdue = r.daysOverdue || 0;
      report += `${i + 1}. ${title} - 已延期 ${daysOverdue} 天 🔴\n`;
    });
    if (overdueRequirements.length > 10) {
      report += `... 还有 ${overdueRequirements.length - 10} 个延期需求\n`;
    }
  } else {
    report += `✅ 无延期需求\n`;
  }
  report += `\n`;
  
  // === 本周需求变动汇总 ===
  report += `📈 本周需求变动汇总\n`;
  report += `• 需求总数：${total} 个\n`;
  
  // 优先级分布
  const priorityStr = Object.entries(priorityDist)
    .filter(([_, count]) => count > 0)
    .map(([priority, count]) => {
      const label = priority === '⚠️ 高' ? '高' : priority === '⚡ 中' ? '中' : '低';
      return `${label} ${count} 个`;
    })
    .join(' | ');
  report += `• 优先级分布：${priorityStr}\n`;
  
  // 状态分布
  const statusStr = Object.entries(statusDist)
    .map(([status, count]) => `${status} ${count}`)
    .join(' | ');
  report += `• 状态分布：${statusStr}\n`;
  
  // 模块分布
  const moduleStr = Object.entries(moduleDist)
    .sort((a, b) => b[1] - a[1]) // 按数量降序
    .map(([module, count]) => `${module} ${count}`)
    .join(' | ');
  report += `• 按模块：${moduleStr}\n`;
  report += `\n`;
  
  // === 生成时间 ===
  const now = new Date();
  const genTime = `${now.getFullYear()}/${now.getMonth() + 1}/${now.getDate()} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
  report += `生成时间：${genTime}\n`;
  
  return report;
}

/**
 * 发送飞书消息（支持 webhook 和 API 两种方式）
 */
function sendFeishuMessage(accessToken, content) {
  const { exec } = require('child_process');
  
  return new Promise((resolve, reject) => {
    // 方式 1: 使用 Webhook（最简单）
    if (CONFIG.WEBHOOK_URL) {
      const data = JSON.stringify({
        msg_type: 'text',
        content: { text: content }
      });

      const url = new URL(CONFIG.WEBHOOK_URL);
      const options = {
        hostname: url.hostname,
        port: 443,
        path: url.pathname,
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
          if (result.code === 0 || result.StatusCode === 0) {
            console.log('   ✅ 消息已通过 Webhook 发送！');
            resolve(result);
          } else {
            console.error('   ❌ Webhook 发送失败:', result);
            reject(new Error(`Webhook 发送失败：${result.msg || JSON.stringify(result)}`));
          }
        });
      });

      req.on('error', (e) => {
        console.error('   ❌ Webhook 请求错误:', e.message);
        reject(e);
      });
      req.write(data);
      req.end();
      return;
    }

    // 方式 2: 使用 API 发送给用户（使用 curl）
    if (CONFIG.RECIPIENT_ID) {
      const contentEscaped = content.replace(/'/g, "'\"'\"'");
      const curlCmd = `curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
        -H "Authorization: Bearer ${accessToken}" \
        -H "Content-Type: application/json" \
        -d '{"msg_type":"text","content":${JSON.stringify(JSON.stringify({text: content}))},"receive_id":"${CONFIG.RECIPIENT_ID}"}'`;
      
      exec(curlCmd, (error, stdout, stderr) => {
        if (error) {
          console.error('   ❌ 执行 curl 失败:', error.message);
          reject(error);
          return;
        }
        
        const result = JSON.parse(stdout);
        if (result.code === 0) {
          console.log('   ✅ 消息已发送给用户！');
          resolve(result);
        } else {
          console.error('   ❌ API 发送失败:', stdout);
          reject(new Error(`API 发送失败：${result.msg}`));
        }
      });
      return;
    }

    reject(new Error('未配置发送方式：请设置 WEBHOOK_URL 或 RECIPIENT_ID'));
  });
}

/**
 * 主函数
 */
async function main() {
  try {
    console.log('🚀 开始生成需求周报...');
    
    // 1. 获取 Access Token
    console.log('📝 获取访问令牌...');
    const accessToken = await getAccessToken();
    
    // 2. 获取需求数据
    console.log('📊 读取需求数据...');
    const records = await listRecords(accessToken);
    console.log(`   共读取 ${records.length} 条记录`);
    
    // 3. 处理数据
    console.log('🔧 处理数据...');
    const processedRecords = processRecords(records);
    
    // 4. 保存原始数据（用于调试）
    const dataPath = `${CONFIG.OUTPUT_DIR}/weekly-report-data.json`;
    fs.writeFileSync(dataPath, JSON.stringify(processedRecords, null, 2));
    console.log(`   数据已保存：${dataPath}`);
    
    // 5. 分析数据
    console.log('📈 分析数据...');
    const analysis = analyzeRequirements(processedRecords);
    console.log(`   总需求数：${analysis.total} 个`);
    console.log(`   延期需求：${analysis.overdueRequirements.length} 个`);
    
    // 6. 生成周报
    console.log('📝 生成周报...');
    const report = generateWeeklyReport(analysis);
    
    // 7. 发送飞书消息（先打印周报内容）
    console.log('\n✅ 周报生成完成！');
    console.log('\n' + '='.repeat(50));
    console.log(report);
    console.log('\n' + '='.repeat(50));
    
    console.log('\n📤 尝试发送飞书消息...');
    console.log('   Token:', accessToken.substring(0, 20) + '...');
    console.log('   接收人:', CONFIG.RECIPIENT_ID);
    try {
      await sendFeishuMessage(accessToken, report);
    } catch (sendError) {
      console.log('⚠️  发送失败:', sendError.message);
      console.log('   请检查配置或手动复制上方周报内容发送');
    }
    
  } catch (error) {
    console.error('❌ 错误:', error.message);
    process.exit(1);
  }
}

main();
