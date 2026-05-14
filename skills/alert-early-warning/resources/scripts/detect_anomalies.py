#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常检测与预警脚本
功能：检测舆情爆发和指标异常，生成预警通知
"""

import argparse
import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter

class AnomalyDetector:
    def __init__(self):
        self.alert_levels = {
            'critical': {'name': '严重', 'emoji': '🔴', 'threshold': 3},
            'warning': {'name': '警告', 'emoji': '🟡', 'threshold': 2},
            'notice': {'name': '关注', 'emoji': '💡', 'threshold': 1.5}
        }
    
    def detect_sentiment_anomalies(self, data, window_hours=1):
        """检测舆情异常"""
        alerts = []
        
        # 按时间窗口聚合
        windows = self._aggregate_by_window(data, window_hours)
        
        for window_time, reviews in windows.items():
            # 计算该窗口的负面率
            negative_count = sum(1 for r in reviews if r.get('sentiment') == 'negative')
            total_count = len(reviews)
            negative_rate = negative_count / total_count if total_count > 0 else 0
            
            # 检测爆发式负面
            if total_count >= 10 and negative_rate > 0.5:
                # 检查是否有集中关键词
                keywords = self._extract_burst_keywords(reviews)
                if keywords:
                    alerts.append({
                        'level': 'critical',
                        'type': 'sentiment_burst',
                        'time': window_time.isoformat(),
                        'message': f'检测到爆发式负面舆情',
                        'details': {
                            'review_count': total_count,
                            'negative_rate': round(negative_rate * 100, 2),
                            'burst_keywords': keywords,
                            'affected_versions': list(set(r.get('version', 'unknown') for r in reviews))
                        }
                    })
            
            # 检测版本问题
            version_reviews = [r for r in reviews if r.get('version')]
            if version_reviews:
                version_negative = defaultdict(int)
                version_total = defaultdict(int)
                
                for r in version_reviews:
                    v = r.get('version', 'unknown')
                    version_total[v] += 1
                    if r.get('sentiment') == 'negative':
                        version_negative[v] += 1
                
                for version, total in version_total.items():
                    if total >= 5:
                        neg_rate = version_negative[version] / total
                        if neg_rate > 0.3:
                            alerts.append({
                                'level': 'warning',
                                'type': 'version_issue',
                                'time': window_time.isoformat(),
                                'message': f'版本 {version} 负面率异常',
                                'details': {
                                    'version': version,
                                    'negative_rate': round(neg_rate * 100, 2),
                                    'review_count': total
                                }
                            })
        
        return alerts
    
    def detect_metrics_anomalies(self, data, threshold_sigma=2):
        """检测指标异常"""
        alerts = []
        
        for metric_name, metric_data in data.items():
            if not metric_data or len(metric_data) < 7:
                continue
            
            values = [d['value'] for d in metric_data]
            mean = statistics.mean(values)
            std = statistics.stdev(values) if len(values) > 1 else 0
            
            if std == 0:
                continue
            
            # 检查最近的数据点
            recent_data = metric_data[-3:]  # 最近3个数据点
            
            for d in recent_data:
                value = d['value']
                z_score = (value - mean) / std
                
                if abs(z_score) > threshold_sigma:
                    level = 'critical' if abs(z_score) > 3 else 'warning'
                    
                    alerts.append({
                        'level': level,
                        'type': 'metric_anomaly',
                        'time': d.get('date', datetime.now().isoformat()),
                        'message': f'指标 {metric_name} 异常波动',
                        'details': {
                            'metric': metric_name,
                            'value': value,
                            'mean': round(mean, 2),
                            'z_score': round(z_score, 2),
                            'deviation': round(abs(z_score), 2)
                        }
                    })
            
            # 检测趋势恶化
            if len(values) >= 7:
                recent_avg = statistics.mean(values[-3:])
                previous_avg = statistics.mean(values[-7:-3])
                
                if previous_avg != 0:
                    change_rate = (recent_avg - previous_avg) / previous_avg
                    
                    # 连续下降检测
                    if change_rate < -0.2:  # 下降超过20%
                        alerts.append({
                            'level': 'warning',
                            'type': 'metric_trend',
                            'time': datetime.now().isoformat(),
                            'message': f'指标 {metric_name} 持续下降',
                            'details': {
                                'metric': metric_name,
                                'recent_avg': round(recent_avg, 2),
                                'previous_avg': round(previous_avg, 2),
                                'change_rate': round(change_rate * 100, 2)
                            }
                        })
        
        return alerts
    
    def _aggregate_by_window(self, data, window_hours):
        """按时间窗口聚合数据"""
        windows = defaultdict(list)
        
        for item in data:
            timestamp = item.get('timestamp') or item.get('date')
            if timestamp:
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
                # 计算窗口起始时间
                window_start = timestamp.replace(minute=0, second=0, microsecond=0)
                window_start = window_start.replace(hour=window_start.hour - window_start.hour % window_hours)
                
                windows[window_start].append(item)
        
        return windows
    
    def _extract_burst_keywords(self, reviews):
        """提取爆发关键词"""
        all_text = ' '.join([r.get('content', '') for r in reviews])
        
        # 简单分词并统计
        words = all_text.split()
        word_count = Counter(words)
        
        # 过滤常见词
        stop_words = {'的', '了', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        
        filtered = {k: v for k, v in word_count.items() if k not in stop_words and len(k) >= 2 and v >= 3}
        
        # 返回Top 5
        return sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def generate_alert_report(self, alerts, output_file):
        """生成预警报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 预警报告\n\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            if not alerts:
                f.write("✅ 当前无异常，系统运行正常。\n")
                return
            
            # 按级别分组
            critical = [a for a in alerts if a['level'] == 'critical']
            warning = [a for a in alerts if a['level'] == 'warning']
            notice = [a for a in alerts if a['level'] == 'notice']
            
            # 摘要
            f.write("## 摘要\n\n")
            f.write(f"- 🔴 严重：{len(critical)} 条\n")
            f.write(f"- 🟡 警告：{len(warning)} 条\n")
            f.write(f"- 💡 关注：{len(notice)} 条\n\n")
            
            # 详细预警
            if critical:
                f.write("## 🔴 严重预警\n\n")
                for alert in critical:
                    self._write_alert_detail(f, alert)
            
            if warning:
                f.write("## 🟡 警告预警\n\n")
                for alert in warning:
                    self._write_alert_detail(f, alert)
            
            if notice:
                f.write("## 💡 关注提醒\n\n")
                for alert in notice:
                    self._write_alert_detail(f, alert)
            
            # 建议
            f.write("## 处理建议\n\n")
            if critical:
                f.write("1. **立即处理严重预警**：优先处理爆发式负面舆情，避免影响扩大\n")
            if warning:
                f.write("2. **关注警告项**：分析指标异常原因，准备应对方案\n")
            f.write("3. **持续监控**：保持对关键指标和舆情的实时监控\n")
    
    def _write_alert_detail(self, f, alert):
        """写入预警详情"""
        level_info = self.alert_levels.get(alert['level'], {})
        f.write(f"### {level_info.get('emoji', '')} {alert['message']}\n\n")
        f.write(f"- **时间**：{alert['time']}\n")
        f.write(f"- **类型**：{alert['type']}\n")
        
        details = alert.get('details', {})
        for key, value in details.items():
            if isinstance(value, list):
                f.write(f"- **{key}**：{', '.join(map(str, value))}\n")
            else:
                f.write(f"- **{key}**：{value}\n")
        
        f.write("\n")

def main():
    parser = argparse.ArgumentParser(description='异常检测与预警工具')
    parser.add_argument('--type', required=True, choices=['sentiment', 'metrics'], help='检测类型')
    parser.add_argument('--input', required=True, help='输入数据文件（JSON格式）')
    parser.add_argument('--threshold', type=float, default=2, help='异常检测阈值（标准差倍数）')
    parser.add_argument('--output', required=True, help='输出预警报告路径')
    parser.add_argument('--window', type=int, default=1, help='舆情检测时间窗口（小时）')
    
    args = parser.parse_args()
    
    # 加载数据
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 检测
    detector = AnomalyDetector()
    
    if args.type == 'sentiment':
        alerts = detector.detect_sentiment_anomalies(data, window_hours=args.window)
    else:
        alerts = detector.detect_metrics_anomalies(data, threshold_sigma=args.threshold)
    
    # 生成报告
    detector.generate_alert_report(alerts, args.output)
    
    print(f"✅ 预警报告已生成：{args.output}")
    print(f"检测到 {len(alerts)} 条预警")

if __name__ == '__main__':
    main()