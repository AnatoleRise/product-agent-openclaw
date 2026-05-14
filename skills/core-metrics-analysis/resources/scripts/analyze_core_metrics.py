#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心业务指标分析脚本
功能：分析DAU/MAU、上传下载等核心指标，生成趋势报告
"""

import argparse
import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict

class CoreMetricsAnalyzer:
    def __init__(self):
        self.metrics_config = {
            'dau': {'name': '日活', 'unit': '人', 'threshold': 0.2},
            'mau': {'name': '月活', 'unit': '人', 'threshold': 0.15},
            'upload_users': {'name': '上传用户数', 'unit': '人', 'threshold': 0.25},
            'download_users': {'name': '下载用户数', 'unit': '人', 'threshold': 0.25},
            'upload_capacity': {'name': '上传容量', 'unit': 'GB', 'threshold': 0.3},
            'download_capacity': {'name': '下载容量', 'unit': 'GB', 'threshold': 0.3}
        }
    
    def analyze_metrics(self, data, metrics, period_days=30):
        """分析核心指标"""
        results = {}
        
        for metric in metrics:
            if metric not in data:
                continue
            
            metric_data = data[metric]
            results[metric] = {
                'trend': self._calculate_trend(metric_data, period_days),
                'anomalies': self._detect_anomalies(metric_data),
                'statistics': self._calculate_statistics(metric_data),
                'divergence': self._analyze_divergence(metric, data) if metric in ['upload_users', 'download_users'] else None
            }
        
        # 综合分析
        results['comprehensive'] = self._comprehensive_analysis(data, metrics)
        
        return results
    
    def _calculate_trend(self, data, period_days):
        """计算趋势"""
        if not data or len(data) < 2:
            return {'error': '数据不足'}
        
        # 排序
        sorted_data = sorted(data, key=lambda x: x['date'])
        
        # 计算环比
        wow_changes = []
        for i in range(1, len(sorted_data)):
            prev = sorted_data[i-1]['value']
            curr = sorted_data[i]['value']
            if prev and prev != 0:
                change = (curr - prev) / prev
                wow_changes.append(change)
        
        # 计算平均环比
        avg_wow = statistics.mean(wow_changes) if wow_changes else 0
        
        # 计算总体变化
        first_value = sorted_data[0]['value']
        last_value = sorted_data[-1]['value']
        total_change = (last_value - first_value) / first_value if first_value else 0
        
        return {
            'period_days': period_days,
            'data_points': len(sorted_data),
            'avg_daily_change': round(avg_wow * 100, 2),
            'total_change': round(total_change * 100, 2),
            'trend_direction': 'up' if total_change > 0.05 else 'down' if total_change < -0.05 else 'stable'
        }
    
    def _detect_anomalies(self, data, threshold_sigma=2):
        """检测异常"""
        if not data or len(data) < 7:
            return []
        
        values = [d['value'] for d in data]
        mean = statistics.mean(values)
        std = statistics.stdev(values) if len(values) > 1 else 0
        
        anomalies = []
        for d in data:
            value = d['value']
            if std > 0:
                z_score = (value - mean) / std
                if abs(z_score) > threshold_sigma:
                    anomalies.append({
                        'date': d['date'],
                        'value': value,
                        'z_score': round(z_score, 2),
                        'type': 'high' if z_score > 0 else 'low'
                    })
        
        return anomalies
    
    def _calculate_statistics(self, data):
        """计算统计指标"""
        values = [d['value'] for d in data]
        if not values:
            return {}
        
        return {
            'min': min(values),
            'max': max(values),
            'mean': round(statistics.mean(values), 2),
            'median': round(statistics.median(values), 2),
            'stdev': round(statistics.stdev(values), 2) if len(values) > 1 else 0
        }
    
    def _analyze_divergence(self, metric, data):
        """分析量价/量容背离"""
        if metric == 'upload_users':
            counterpart = 'upload_capacity'
        elif metric == 'download_users':
            counterpart = 'download_capacity'
        else:
            return None
        
        if counterpart not in data:
            return None
        
        user_data = data[metric]
        capacity_data = data[counterpart]
        
        if not user_data or not capacity_data:
            return None
        
        # 计算最近的变化率
        user_change = self._calculate_trend(user_data, 7)['total_change']
        capacity_change = self._calculate_trend(capacity_data, 7)['total_change']
        
        # 判断背离类型
        if user_change > 5 and capacity_change < -5:
            divergence_type = 'user_up_capacity_down'
            risk = '水货用户风险：新增用户多为低价值用户'
        elif user_change < -5 and capacity_change > 5:
            divergence_type = 'user_down_capacity_up'
            risk = '大户依赖风险：核心大客户使用加深，但小用户流失'
        elif abs(user_change - capacity_change) > 15:
            divergence_type = 'significant_divergence'
            risk = '显著背离：需深入分析原因'
        else:
            divergence_type = 'normal'
            risk = '正常范围'
        
        return {
            'type': divergence_type,
            'user_change': user_change,
            'capacity_change': capacity_change,
            'risk_assessment': risk
        }
    
    def _comprehensive_analysis(self, data, metrics):
        """综合分析"""
        analysis = {
            'overall_health': 'healthy',
            'key_findings': [],
            'recommendations': []
        }
        
        # 检查是否有严重异常
        critical_anomalies = 0
        for metric in metrics:
            if metric in data:
                anomalies = self._detect_anomalies(data[metric], threshold_sigma=3)
                if anomalies:
                    critical_anomalies += len(anomalies)
        
        if critical_anomalies > 2:
            analysis['overall_health'] = 'critical'
            analysis['key_findings'].append(f'检测到{critical_anomalies}个严重异常点，需立即关注')
        elif critical_anomalies > 0:
            analysis['overall_health'] = 'warning'
            analysis['key_findings'].append(f'检测到{critical_anomalies}个异常点，建议关注')
        
        # 检查背离情况
        divergence_count = 0
        for metric in ['upload_users', 'download_users']:
            if metric in data:
                div = self._analyze_divergence(metric, data)
                if div and div['type'] != 'normal':
                    divergence_count += 1
                    analysis['key_findings'].append(div['risk_assessment'])
        
        if divergence_count > 0:
            analysis['recommendations'].append('存在量价背离，建议深入分析用户质量')
        
        return analysis
    
    def generate_report(self, results, output_file):
        """生成Markdown报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 核心业务指标分析报告\n\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            # 综合结论
            if 'comprehensive' in results:
                comp = results['comprehensive']
                f.write("## 综合评估\n\n")
                health_map = {
                    'healthy': '🟢 健康',
                    'warning': '🟡 警告',
                    'critical': '🔴 严重'
                }
                f.write(f"**整体状态**：{health_map.get(comp['overall_health'], comp['overall_health'])}\n\n")
                
                if comp['key_findings']:
                    f.write("### 关键发现\n\n")
                    for finding in comp['key_findings']:
                        f.write(f"- {finding}\n")
                    f.write("\n")
                
                if comp['recommendations']:
                    f.write("### 建议\n\n")
                    for rec in comp['recommendations']:
                        f.write(f"- {rec}\n")
                    f.write("\n")
            
            # 各指标详情
            f.write("## 指标详情\n\n")
            for metric, result in results.items():
                if metric == 'comprehensive':
                    continue
                
                config = self.metrics_config.get(metric, {'name': metric, 'unit': ''})
                f.write(f"### {config['name']} ({metric})\n\n")
                
                if 'trend' in result:
                    trend = result['trend']
                    f.write(f"- **趋势方向**：{trend.get('trend_direction', 'unknown')}\n")
                    f.write(f"- **平均日变化**：{trend.get('avg_daily_change', 0)}%\n")
                    f.write(f"- **总体变化**：{trend.get('total_change', 0)}%\n")
                    f.write(f"- **数据点数**：{trend.get('data_points', 0)}\n\n")
                
                if 'statistics' in result:
                    stats = result['statistics']
                    f.write(f"- **最小值**：{stats.get('min', 0)} {config['unit']}\n")
                    f.write(f"- **最大值**：{stats.get('max', 0)} {config['unit']}\n")
                    f.write(f"- **平均值**：{stats.get('mean', 0)} {config['unit']}\n")
                    f.write(f"- **中位数**：{stats.get('median', 0)} {config['unit']}\n\n")
                
                if 'anomalies' in result and result['anomalies']:
                    f.write("**异常点**：\n\n")
                    f.write("| 日期 | 数值 | Z分数 | 类型 |\n")
                    f.write("|------|------|-------|------|\n")
                    for anomaly in result['anomalies']:
                        f.write(f"| {anomaly['date']} | {anomaly['value']} | {anomaly['z_score']} | {anomaly['type']} |\n")
                    f.write("\n")
                
                if 'divergence' in result and result['divergence']:
                    div = result['divergence']
                    if div['type'] != 'normal':
                        f.write(f"**背离警告**：{div['risk_assessment']}\n")
                        f.write(f"- 用户变化：{div['user_change']}%\n")
                        f.write(f"- 容量变化：{div['capacity_change']}%\n\n")

def main():
    parser = argparse.ArgumentParser(description='核心业务指标分析工具')
    parser.add_argument('--input', required=True, help='输入指标数据文件（JSON格式）')
    parser.add_argument('--metrics', required=True, help='要分析的指标，逗号分隔')
    parser.add_argument('--period', type=int, default=30, help='分析周期（天）')
    parser.add_argument('--output', required=True, help='输出报告文件路径')
    parser.add_argument('--detect-anomalies', action='store_true', help='启用异常检测')
    parser.add_argument('--threshold', type=float, default=2, help='异常检测阈值（标准差倍数）')
    
    args = parser.parse_args()
    
    # 加载数据
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 解析指标列表
    metrics = [m.strip() for m in args.metrics.split(',')]
    
    # 分析
    analyzer = CoreMetricsAnalyzer()
    results = analyzer.analyze_metrics(data, metrics, period_days=args.period)
    
    # 生成报告
    analyzer.generate_report(results, args.output)
    print(f"✅ 指标分析报告已生成：{args.output}")

if __name__ == '__main__':
    main()