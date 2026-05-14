#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户反馈处理脚本
功能：整合多渠道反馈，进行结构化处理和分类
"""

import argparse
import json
import re
from datetime import datetime
from collections import Counter, defaultdict

class FeedbackProcessor:
    def __init__(self):
        self.category_patterns = {
            '功能缺陷': ['bug', '故障', '错误', '异常', '崩溃', '闪退', '无法', '不能', '失败'],
            '体验不佳': ['卡顿', '慢', '延迟', '不流畅', '难用', '复杂', '麻烦'],
            '价格争议': ['贵', '便宜', '价格', '收费', '付费', '会员', '太贵'],
            '客服态度': ['客服', '服务', '态度', '不理', '敷衍', '推诿'],
            '竞品对比': ['竞品', '对手', '别人家', '其他', '不如', '比不上'],
            '功能建议': ['建议', '希望', '期待', '想要', '增加', '添加', '优化'],
            '使用咨询': ['怎么', '如何', '请问', '咨询', '疑问', '不懂']
        }
        
        self.sentiment_words = {
            'positive': ['好', '棒', '优秀', '满意', '喜欢', '推荐', '感谢', '赞'],
            'negative': ['差', '烂', '糟糕', '失望', '愤怒', '气愤', '恶心', '垃圾'],
            'neutral': ['一般', '还行', '凑合', '普通', '正常']
        }
    
    def process_feedback(self, feedback_data, channels=None):
        """处理反馈数据"""
        # 按渠道过滤
        if channels:
            feedback_data = [f for f in feedback_data if f.get('channel') in channels]
        
        # 去重
        deduplicated = self._deduplicate(feedback_data)
        
        # 分类
        categorized = self._categorize(deduplicated)
        
        # 情感分析
        sentiment_result = self._analyze_sentiment_batch(deduplicated)
        
        # 提取痛点
        pain_points = self._extract_pain_points(categorized)
        
        # 生成报告
        report = {
            'summary': {
                'total_count': len(feedback_data),
                'after_dedup': len(deduplicated),
                'channel_distribution': self._channel_distribution(deduplicated),
                'category_distribution': self._category_distribution(categorized),
                'sentiment_distribution': sentiment_result
            },
            'details': {
                'categorized_feedback': categorized,
                'pain_points': pain_points,
                'hot_topics': self._extract_hot_topics(deduplicated)
            }
        }
        
        return report
    
    def _deduplicate(self, feedback_data):
        """去重处理"""
        seen = set()
        result = []
        
        for item in feedback_data:
            # 生成指纹
            content = item.get('content', '')
            fingerprint = self._generate_fingerprint(content)
            
            if fingerprint not in seen:
                seen.add(fingerprint)
                result.append(item)
        
        return result
    
    def _generate_fingerprint(self, text):
        """生成文本指纹（用于去重）"""
        # 简单实现：取前30个字符+长度
        text = re.sub(r'[^\w]', '', text)
        return text[:30] + str(len(text))
    
    def _categorize(self, feedback_data):
        """分类反馈"""
        categorized = defaultdict(list)
        
        for item in feedback_data:
            content = item.get('content', '')
            category = self._determine_category(content)
            item['category'] = category
            categorized[category].append(item)
        
        return dict(categorized)
    
    def _determine_category(self, content):
        """确定反馈类别"""
        scores = defaultdict(int)
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if pattern in content:
                    scores[category] += 1
        
        if scores:
            return max(scores, key=scores.get)
        return '其他'
    
    def _analyze_sentiment_batch(self, feedback_data):
        """批量情感分析"""
        sentiments = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        for item in feedback_data:
            content = item.get('content', '')
            sentiment = self._analyze_single_sentiment(content)
            sentiments[sentiment] += 1
        
        total = len(feedback_data) if feedback_data else 1
        return {k: round(v/total*100, 2) for k, v in sentiments.items()}
    
    def _analyze_single_sentiment(self, content):
        """单条情感分析"""
        pos_count = sum(1 for word in self.sentiment_words['positive'] if word in content)
        neg_count = sum(1 for word in self.sentiment_words['negative'] if word in content)
        
        if neg_count > pos_count:
            return 'negative'
        elif pos_count > neg_count:
            return 'positive'
        else:
            return 'neutral'
    
    def _extract_pain_points(self, categorized_data):
        """提取痛点"""
        pain_points = []
        
        for category, items in categorized_data.items():
            if category in ['功能缺陷', '体验不佳']:
                # 提取高频关键词
                keywords = self._extract_keywords([i['content'] for i in items])
                pain_points.append({
                    'category': category,
                    'count': len(items),
                    'keywords': keywords[:5],
                    'typical_examples': [i['content'][:100] for i in items[:3]]
                })
        
        # 按数量排序
        pain_points.sort(key=lambda x: x['count'], reverse=True)
        return pain_points
    
    def _extract_keywords(self, texts):
        """提取关键词"""
        word_count = Counter()
        
        for text in texts:
            # 简单分词（按2-4字词）
            for length in range(2, 5):
                for i in range(len(text) - length + 1):
                    word = text[i:i+length]
                    if len(word) >= 2:
                        word_count[word] += 1
        
        # 过滤常见词
        stop_words = {'一个', '这个', '那个', '什么', '怎么', '可以', '没有', '就是'}
        filtered = {k: v for k, v in word_count.items() if k not in stop_words and v > 1}
        
        return sorted(filtered.items(), key=lambda x: x[1], reverse=True)
    
    def _channel_distribution(self, feedback_data):
        """渠道分布"""
        channels = [f.get('channel', 'unknown') for f in feedback_data]
        counter = Counter(channels)
        total = len(feedback_data) if feedback_data else 1
        return {k: round(v/total*100, 2) for k, v in counter.items()}
    
    def _category_distribution(self, categorized_data):
        """分类分布"""
        total = sum(len(items) for items in categorized_data.values())
        if total == 0:
            return {}
        return {k: round(len(v)/total*100, 2) for k, v in categorized_data.items()}
    
    def _extract_hot_topics(self, feedback_data):
        """提取热点话题"""
        all_text = ' '.join([f.get('content', '') for f in feedback_data])
        keywords = self._extract_keywords([all_text])
        return keywords[:10]
    
    def generate_report(self, report_data, output_file):
        """生成Markdown报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 用户反馈结构化报告\n\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            # 摘要
            summary = report_data['summary']
            f.write("## 摘要\n\n")
            f.write(f"- 原始反馈数：{summary['total_count']}\n")
            f.write(f"- 去重后：{summary['after_dedup']}\n")
            f.write(f"- 去重率：{round((1-summary['after_dedup']/summary['total_count'])*100, 2)}%\n\n")
            
            # 渠道分布
            f.write("### 渠道分布\n\n")
            for channel, percentage in summary['channel_distribution'].items():
                f.write(f"- {channel}：{percentage}%\n")
            f.write("\n")
            
            # 分类分布
            f.write("### 分类分布\n\n")
            for category, percentage in summary['category_distribution'].items():
                f.write(f"- {category}：{percentage}%\n")
            f.write("\n")
            
            # 情感分布
            f.write("### 情感分布\n\n")
            for sentiment, percentage in summary['sentiment_distribution'].items():
                f.write(f"- {sentiment}：{percentage}%\n")
            f.write("\n")
            
            # 痛点清单
            f.write("## 痛点清单\n\n")
            for i, pain in enumerate(report_data['details']['pain_points'], 1):
                f.write(f"### {i}. {pain['category']} ({pain['count']}条)\n\n")
                f.write("**关键词**：" + ", ".join([k[0] for k in pain['keywords']]) + "\n\n")
                f.write("**典型反馈**：\n\n")
                for example in pain['typical_examples']:
                    f.write(f"> {example}\n\n")
            
            # 热点话题
            f.write("## 热点话题\n\n")
            f.write("| 话题 | 提及次数 |\n")
            f.write("|------|----------|\n")
            for topic, count in report_data['details']['hot_topics']:
                f.write(f"| {topic} | {count} |\n")

def main():
    parser = argparse.ArgumentParser(description='用户反馈处理工具')
    parser.add_argument('--input', required=True, help='输入反馈数据文件（JSON格式）')
    parser.add_argument('--channels', help='指定渠道，逗号分隔')
    parser.add_argument('--output', required=True, help='输出报告文件路径')
    parser.add_argument('--trend-analysis', action='store_true', help='启用趋势分析')
    parser.add_argument('--period', type=int, default=30, help='趋势分析周期（天）')
    parser.add_argument('--extract-pain-points', action='store_true', help='提取痛点')
    
    args = parser.parse_args()
    
    # 加载数据
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 解析渠道
    channels = None
    if args.channels:
        channels = [c.strip() for c in args.channels.split(',')]
    
    # 处理
    processor = FeedbackProcessor()
    report = processor.process_feedback(data, channels=channels)
    
    # 生成报告
    processor.generate_report(report, args.output)
    print(f"✅ 反馈处理报告已生成：{args.output}")

if __name__ == '__main__':
    main()