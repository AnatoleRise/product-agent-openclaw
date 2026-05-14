#!/usr/bin/env node
/**
 * 飞书需求归档脚本
 * 
 * 扫描需求表，筛选"已上线"和"需求转出"记录
 * 写入归档统计 JSON 供周报使用
 * 
 * 用法：node archive.js
 * 输出：/tmp/requirement-archive-stats.json
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const CONFIG = {
  APP_ID: process.env.FEISHU_APP_ID || '',
  APP_SECRET: process.env.FEISHU_APP_SECRET || '',
  APP_TOKEN: process.env.FEISHU_APP_TOKEN || '',
  TABLE_ID: process.env.FEISHU_TABLE_ID || '',
  OUTPUT_DIR: process.env.OUTPUT_DIR || process.cwd()
};

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
      headers: { 'Content-Type': 'application/json', 'Content-Length': data.length }
    };
    const req = https.request(options, res => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        const result = JSON.parse(body);
        if (result.code === 0) resolve(result.tenant_access_token);
        else reject(new Error(`获取 token 失败：${result.msg}`));
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

function listRecords(accessToken) {
  return new Promise((resolve, reject) => {
    const fields = ['标题','重要性','一级模块','二级模块','状态','原定上线时间','真实上线时间','提出需求时间','最后修改时间']
      .map(f => encodeURIComponent(f)).join(',');
    const path = `/open-apis/bitable/v1/apps/${CONFIG.APP_TOKEN}/tables/${CONFIG.TABLE_ID}/records?field_names[]=${fields}&page_size=500`;
    const options = {
      hostname: 'open.feishu.cn', port: 443, path, method: 'GET',
      headers: { 'Authorization': `Bearer ${accessToken}` }
    };
    https.get(options, res => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        const result = JSON.parse(body);
        if (result.code === 0) resolve(result.data.items);
        else reject(new Error(`获取记录失败：${result.msg}`));
      });
    }).on('error', reject);
  });
}

function getWeekRange() {
  const now = new Date();
  // 往前找最近的周五
  const dayOfWeek = now.getDay();
  const fridayOffset = dayOfWeek === 5 ? 0 : (dayOfWeek < 5 ? dayOfWeek + 2 : dayOfWeek - 5);
  const friday = new Date(now);
  friday.setDate(friday.getDate() - fridayOffset);
  
  const monday = new Date(friday);
  monday.setDate(monday.getDate() - 4);
  
  const weekStart = monday.toISOString().split('T')[0];
  const weekEnd = friday.toISOString().split('T')[0];
  return { weekStart, weekEnd };
}

async function main() {
  try {
    console.log('📦 开始需求归档...');
    
    const token = await getAccessToken();
    console.log('   ✅ 获取 token 成功');
    
    const records = await listRecords(token);
    console.log(`   📊 共 ${records.length} 条记录`);
    
    // 分析所有记录
    let onlineCount = 0;
    let transferredCount = 0;
    const moduleDist = {};
    
    records.forEach(rec => {
      const status = rec.fields?.['状态'] || '';
      const module = rec.fields?.['一级模块'] || '未分类';
      
      if (status === '已上线') {
        onlineCount++;
        moduleDist[module] = (moduleDist[module] || 0) + 1;
      } else if (status === '需求转出') {
        transferredCount++;
      }
    });
    
    const { weekStart, weekEnd } = getWeekRange();
    
    const stats = {
      weekStart,
      weekEnd,
      newOnline: onlineCount,
      newTransferred: transferredCount,
      totalOnline: onlineCount,
      totalTransferred: transferredCount,
      moduleDistribution: moduleDist,
      cumulativeTotal: onlineCount + transferredCount,
      generatedAt: new Date().toISOString()
    };
    
    const outputPath = path.join(CONFIG.OUTPUT_DIR, 'requirement-archive-stats.json');
    fs.writeFileSync(outputPath, JSON.stringify(stats, null, 2));
    
    console.log(`   ✅ 归档完成`);
    console.log(`      本周已上线: ${onlineCount}`);
    console.log(`      本周转出: ${transferredCount}`);
    console.log(`      模块分布: ${Object.entries(moduleDist).map(([k,v]) => `${k}:${v}`).join(', ')}`);
    console.log(`      输出: ${outputPath}`);
    
  } catch (err) {
    console.error('❌ 归档失败:', err.message);
    process.exit(1);
  }
}

main();
