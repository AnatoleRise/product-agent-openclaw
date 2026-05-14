#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用市场评论分析脚本
功能：采集、分析应用市场评论，生成舆情报告
"""

import argparse
import json
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict

class AppReviewAnalyzer:
    def __init__(self):
        self.sentiment_keywords = {
            'positive': ['好用', '流畅', '方便', '喜欢', '推荐', '满意', '完美', '优秀'],
            'negative': ['卡顿', '闪退', '崩溃', '垃圾', '难用', '失望', 'bug', '问题', '故障'],
            'angry': ['愤怒', '气愤', '垃圾', '骗子', '坑人', '恶心', '卸载']
        }
        self.problem_patterns = {
            '稳定性-启动异常': ['打不开', '闪退', '崩溃', '启动失败', '无法启动', '黑屏'],
            '稳定性-运行异常': ['卡顿', '死机', '无响应', '冻结', '卡死'],
            '功能-上传问题': ['上传失败', '上传慢', '传不了', '上传不了'],
            '功能-下载问题': ['下载失败', '下载慢', '下不了', '下载不了'],
            '功能-登录问题': ['登录失败', '登不上', '无法登录', '密码错误'],
            '体验-界面问题': ['界面丑', '不好看', '布局乱', '操作复杂'],
            '体验-性能问题': ['速度慢', '反应慢', '加载慢', '太卡']
        }
    
    def analyze_reviews(self, reviews, days=7, version=None):
        """分析评论数据"""
        # 过滤时间范围
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_reviews = [r for r in reviews if r.get('date', datetime.now()) >= cutoff_date]
        
        # 情感分析
        sentiment_result = self._analyze_sentiment(filtered_reviews)
        
        # 问题聚类
        problem_clusters = self._cluster_problems(filtered_reviews)
        
        # 版本关联分析
        version_analysis = self._analyze_by_version(filtered_reviews)
        
        # 生成报告
        report = {
            'summary': {
                'total_reviews': len(filtered_reviews),
                'sentiment_distribution': sentiment_result,
                'top_problems': problem_clusters[:10],
                'alert_level': self._determine_alert_level(problem_clusters, sentiment_result)
            },
            'details': {
                'problem_clusters': problem_clusters,
                'version_analysis': version_analysis,
                'typical_quotes': self._extract_typical_quotes(filtered_reviews, problem_clusters[:5])
            }
        }
        
        return report
    
    def _analyze_sentiment(self, reviews):
        """情感分析"""
        sentiments = {'positive': 0, 'neutral': 0, 'negative': 0, 'angry': 0}
        
        for review in reviews:
            content = review.get('content', '')
            score = 0
            
            for word in self.sentiment_keywords['angry']:
                if word in content:
                    score -= 3
            for word in self.sentiment_keywords['negative']:
                if word in content:
                    score -= 1
            for word in self.sentiment_keywords['positive']:
                if word in content:
                    score += 1
            
            if score <= -3:
                sentiments['angry'] += 1
            elif score < 0:
                sentiments['negative'] += 1
            elif score > 0:
                sentiments['positive'] += 1
            else:
                sentiments['neutral'] += 1
        
        total = len(reviews) if reviews else 1
        return {k: round(v/total*100, 2) for k, v in sentiments.items()}
    
    def _cluster_problems(self, reviews):
        """问题聚类"""
        problem_counts = defaultdict(int)
        problem_examples = defaultdict(list)
        
        for review in reviews:
            content = review.get('content', '')
            for category, patterns in self.problem_patterns.items():
                for pattern in patterns:
                    if pattern in content:
                        problem_counts[category] += 1
                        if len(problem_examples[category]) < 5:
                            problem_examples[category].append({
                                'quote': content[:100],
                                'rating': review.get('rating', 0)
                            })
                        break
        
        # 排序并生成结果
        sorted_problems = sorted(problem_counts.items(), key=lambda x: x[1], reverse=True)
        result = []
        for category, count in sorted_problems:
            result.append({
                'category': category,
                'count': count,
                'percentage': round(count/len(reviews)*100, 2) if reviews else 0,
                'examples': problem_examples[category]
            })
        
        return result
    
    def _analyze_by_version(self, reviews):
        """按版本分析"""
        version_stats = defaultdict(lambda: {'count': 0, 'negative': 0, 'avg_rating': []})
        
        for review in reviews:
            version = review.get('version', 'unknown')
            version_stats[version]['count'] += 1
            if review.get('rating', 5) <= 2:
                version_stats[version]['negative'] += 1
            version_stats[version]['avg_rating'].append(review.get('rating', 5))
        
        # 计算平均评分
        for version in version_stats:
            ratings = version_stats[version]['avg_rating']
            version_stats[version]['avg_rating'] = round(sum(ratings)/len(ratings), 2) if ratings else 0
        
        return dict(version_stats)
    
    def _determine_alert_level(self, problem_clusters, sentiment):
        """确定预警级别"""
        if not problem_clusters:
            return 'normal'
        
        top_problem = problem_clusters[0]
        if top_problem['percentage'] > 30 or sentiment.get('angry', 0) > 20:
            return 'critical'
        elif top_problem['percentage'] > 15 or sentiment.get('negative', 0) > 40:
            return 'warning'
        else:
            return 'normal'
    
    def _extract_typical_quotes(self, reviews, top_problems):
        """提取典型原声"""
        quotes = {}
        for problem in top_problems:
            category = problem['category']
            quotes[category] = problem.get('examples', [])
        return quotes
    
    def generate_report(self, report_data, output_file):
        """生成Markdown报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 应用市场舆情分析报告\n\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            # 摘要
            summary = report_data['summary']
            f.write("## 摘要\n\n")
            f.write(f"- 分析评论数：{summary['total_reviews']}\n")
            f.write(f"- 预警级别：{summary['alert_level']}\n")
            f.write(f"- 情感分布：正面{summary['sentiment_distribution'].get('positive', 0)}% | ")
            f.write(f"中性{summary['sentiment_distribution'].get('neutral', 0)}% | ")
            f.write(f"负面{summary['sentiment_distribution'].get('negative', 0)}% | ")
            f.write(f"愤怒{summary['sentiment_distribution'].get('angry', 0)}%\n\n")
            
            # Top问题
            f.write("## Top 问题排行\n\n")
            f.write("| 排名 | 问题类别 | 出现次数 | 占比 |\n")
            f.write("|------|----------|----------|------|\n")
            for i, problem in enumerate(summary['top_problems'][:10], 1):
                f.write(f"| {i} | {problem['category']} | {problem['count']} | {problem['percentage']}% |\n")
            f.write("\n")
            
            # 典型原声
            f.write("## 典型用户原声\n\n")
            for category, quotes in report_data['details']['typical_quotes'].items():
                f.write(f"### {category}\n\n")
                for quote in quotes[:3]:
                    f.write(f"> {quote['quote']}\n")
                    f.write(f"> 评分：{quote['rating']}星\n\n")
            
            # 版本分析
            f.write("## 版本分析\n\n")
            f.write("| 版本 | 评论数 | 负面占比 | 平均评分 |\n")
            f.write("|------|--------|----------|----------|\n")
            for version, stats in report_data['details']['version_analysis'].items():
                negative_rate = round(stats['negative']/stats['count']*100, 2) if stats['count'] else 0
                f.write(f"| {version} | {stats['count']} | {negative_rate}% | {stats['avg_rating']} |\n")

def main():
    parser = argparse.ArgumentParser(description='应用市场评论分析工具')
    parser.add_argument('--input', required=True, help='输入评论数据文件（JSON格式）')
    parser.add_argument('--days', type=int, default=7, help='分析最近N天的数据')
    parser.add_argument('--output', required=True, help='输出报告文件路径')
    parser.add_argument('--version', help='指定版本号进行重点分析')
    
    args = parser.parse_args()
    
    # 加载数据
    with open(args.input, 'r', encoding='utf-8') as f:
        reviews = json.load(f)
    
    # 分析
    analyzer = AppReviewAnalyzer()
    report = analyzer.analyze_reviews(reviews, days=args.days, version=args.version)
    
    # 生成报告
    analyzer.generate_report(report, args.output)
    print(f"✅ 舆情分析报告已生成：{args.output}")

if __name__ == '__main__':
    main()