#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据看板生成脚本
功能：生成用户之声仪表盘和核心功能数据看板
"""

import argparse
import json
import os
from datetime import datetime

class DashboardGenerator:
    def __init__(self):
        self.templates = {
            'user_voice': self._user_voice_template,
            'core_metrics': self._core_metrics_template,
            'comprehensive': self._comprehensive_template
        }
    
    def generate_dashboard(self, data, dashboard_type, output_file):
        """生成看板"""
        if dashboard_type not in self.templates:
            raise ValueError(f"不支持的看板类型：{dashboard_type}")
        
        template_func = self.templates[dashboard_type]
        html_content = template_func(data)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file
    
    def _user_voice_template(self, data):
        """用户之声仪表盘模板"""
        sentiment = data.get('sentiment', {'positive': 30, 'neutral': 40, 'negative': 30})
        top_problems = data.get('top_problems', [])
        trend = data.get('trend', [])
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>用户之声仪表盘</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .dashboard {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .header .time {{ opacity: 0.8; margin-top: 10px; }}
        .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .card h3 {{ margin: 0 0 15px 0; color: #333; font-size: 16px; }}
        .metric {{ font-size: 32px; font-weight: bold; color: #667eea; }}
        .metric-label {{ color: #666; font-size: 14px; margin-top: 5px; }}
        .sentiment-bar {{ display: flex; height: 30px; border-radius: 15px; overflow: hidden; margin-top: 10px; }}
        .sentiment-positive {{ background: #52c41a; width: {sentiment.get('positive', 30)}%; }}
        .sentiment-neutral {{ background: #faad14; width: {sentiment.get('neutral', 40)}%; }}
        .sentiment-negative {{ background: #f5222d; width: {sentiment.get('negative', 30)}%; }}
        .problem-list {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .problem-item {{ display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f0f0f0; }}
        .problem-item:last-child {{ border-bottom: none; }}
        .problem-name {{ font-weight: 500; }}
        .problem-count {{ background: #f5222d; color: white; padding: 4px 12px; border-radius: 12px; font-size: 14px; }}
        .alert {{ background: #fff2f0; border: 1px solid #ffccc7; padding: 15px; border-radius: 8px; margin-top: 20px; }}
        .alert-title {{ color: #cf1322; font-weight: bold; margin-bottom: 5px; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>用户之声仪表盘</h1>
            <div class="time">生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </div>
        
        <div class="cards">
            <div class="card">
                <h3>今日反馈数</h3>
                <div class="metric">{data.get('today_count', 0)}</div>
                <div class="metric-label">较昨日 {data.get('day_change', 0):+.1f}%</div>
            </div>
            <div class="card">
                <h3>本周反馈数</h3>
                <div class="metric">{data.get('week_count', 0)}</div>
                <div class="metric-label">较上周 {data.get('week_change', 0):+.1f}%</div>
            </div>
            <div class="card">
                <h3>负面反馈占比</h3>
                <div class="metric">{sentiment.get('negative', 30)}%</div>
                <div class="metric-label">需重点关注</div>
            </div>
            <div class="card">
                <h3>情感分布</h3>
                <div class="sentiment-bar">
                    <div class="sentiment-positive" title="正面 {sentiment.get('positive', 30)}%"></div>
                    <div class="sentiment-neutral" title="中性 {sentiment.get('neutral', 40)}%"></div>
                    <div class="sentiment-negative" title="负面 {sentiment.get('negative', 30)}%"></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 12px; color: #666;">
                    <span>正面 {sentiment.get('positive', 30)}%</span>
                    <span>中性 {sentiment.get('neutral', 40)}%</span>
                    <span>负面 {sentiment.get('negative', 30)}%</span>
                </div>
            </div>
        </div>
        
        <div class="problem-list">
            <h3>Top 问题排行</h3>
            {self._generate_problem_items(top_problems)}
        </div>
        
        {self._generate_alert_section(data)}
    </div>
</body>
</html>
"""
        return html
    
    def _core_metrics_template(self, data):
        """核心功能数据看板模板"""
        metrics = data.get('metrics', {})
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>核心功能数据看板</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .dashboard {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; }}
        .metric-value {{ font-size: 36px; font-weight: bold; color: #1890ff; }}
        .metric-name {{ color: #666; font-size: 14px; margin-top: 8px; }}
        .metric-change {{ font-size: 14px; margin-top: 5px; }}
        .metric-change.up {{ color: #52c41a; }}
        .metric-change.down {{ color: #f5222d; }}
        .chart-container {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .chart-title {{ font-size: 18px; font-weight: 500; margin-bottom: 15px; }}
        .anomaly-list {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .anomaly-item {{ padding: 10px; margin: 5px 0; border-radius: 5px; }}
        .anomaly-critical {{ background: #fff2f0; border-left: 4px solid #f5222d; }}
        .anomaly-warning {{ background: #fffbe6; border-left: 4px solid #faad14; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>核心功能数据看板</h1>
            <div>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </div>
        
        <div class="metrics-grid">
            {self._generate_metric_cards(metrics)}
        </div>
        
        <div class="chart-container">
            <div class="chart-title">指标趋势</div>
            <div style="height: 300px; background: #fafafa; border-radius: 5px; display: flex; align-items: center; justify-content: center; color: #999;">
                趋势图表区域（需接入图表库）
            </div>
        </div>
        
        {self._generate_anomaly_section(data)}
    </div>
</body>
</html>
"""
        return html
    
    def _comprehensive_template(self, data):
        """综合看板模板"""
        return self._user_voice_template(data)  # 简化实现
    
    def _generate_problem_items(self, problems):
        """生成问题列表HTML"""
        if not problems:
            return '<div style="color: #999; text-align: center; padding: 20px;">暂无数据</div>'
        
        items = []
        for problem in problems[:10]:
            name = problem.get('category', '未知问题')
            count = problem.get('count', 0)
            items.append(f'<div class="problem-item"><span class="problem-name">{name}</span><span class="problem-count">{count}</span></div>')
        
        return '\n'.join(items)
    
    def _generate_alert_section(self, data):
        """生成预警区域"""
        alerts = data.get('alerts', [])
        if not alerts:
            return ''
        
        alert_html = '<div class="alert"><div class="alert-title">⚠️ 预警信息</div>'
        for alert in alerts[:3]:
            alert_html += f'<div>{alert}</div>'
        alert_html += '</div>'
        
        return alert_html
    
    def _generate_metric_cards(self, metrics):
        """生成指标卡片"""
        cards = []
        metric_names = {
            'dau': '日活 (DAU)',
            'mau': '月活 (MAU)',
            'upload_users': '上传用户数',
            'download_users': '下载用户数',
            'upload_capacity': '上传容量 (GB)',
            'download_capacity': '下载容量 (GB)'
        }
        
        for key, value in metrics.items():
            name = metric_names.get(key, key)
            current = value.get('current', 0)
            change = value.get('change', 0)
            change_class = 'up' if change >= 0 else 'down'
            change_symbol = '+' if change >= 0 else ''
            
            cards.append(f'''
            <div class="metric-card">
                <div class="metric-value">{current:,}</div>
                <div class="metric-name">{name}</div>
                <div class="metric-change {change_class}">{change_symbol}{change:.1f}%</div>
            </div>
            ''')
        
        return '\n'.join(cards) if cards else '<div style="color: #999;">暂无指标数据</div>'
    
    def _generate_anomaly_section(self, data):
        """生成异常区域"""
        anomalies = data.get('anomalies', [])
        if not anomalies:
            return ''
        
        html = '<div class="anomaly-list"><h3>异常检测</h3>'
        for anomaly in anomalies[:5]:
            level = anomaly.get('level', 'warning')
            metric = anomaly.get('metric', '未知指标')
            value = anomaly.get('value', 0)
            description = anomaly.get('description', '')
            
            html += f'<div class="anomaly-item anomaly-{level}">'
            html += f'<strong>{metric}</strong>: {value} - {description}'
            html += '</div>'
        
        html += '</div>'
        return html

def main():
    parser = argparse.ArgumentParser(description='数据看板生成工具')
    parser.add_argument('--type', required=True, choices=['user_voice', 'core_metrics', 'comprehensive'], help='看板类型')
    parser.add_argument('--input', required=True, help='输入数据文件（JSON格式）')
    parser.add_argument('--output', required=True, help='输出HTML文件路径')
    
    args = parser.parse_args()
    
    # 加载数据
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 生成看板
    generator = DashboardGenerator()
    output_path = generator.generate_dashboard(data, args.type, args.output)
    
    print(f"✅ 数据看板已生成：{output_path}")
    print(f"请用浏览器打开查看")

if __name__ == '__main__':
    main()