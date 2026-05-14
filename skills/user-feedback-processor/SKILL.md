---
name: user-feedback-processor
description: 用户反馈结构化处理技能。当用户需要：(1) 整合分散在客服记录、应用商店、社群、问卷等渠道的用户反馈，(2) 对海量反馈进行清洗、去重、归类，(3) 提取用户痛点和需求，(4) 生成结构化反馈清单时，使用此技能。输入为多渠道用户反馈数据（客服记录、社群消息、问卷结果、应用商店评论等）；输出为结构化反馈清单、痛点分类、情感分析结果、典型原声摘录。支持自动去重、语义聚类、情感分析。
---

# 用户反馈结构化处理

## 核心定位

整合分散在客服记录、应用商店、社群、问卷等各个孤岛的用户反馈，进行结构化整理及归类，实现全局高效把控。

## 输入

- 客服记录（工单、聊天记录、电话录音转写）
- 社群反馈（微信群、QQ群、Discord、Slack等）
- 问卷数据（NPS、满意度调查、功能需求调研）
- 应用商店评论
- 其他渠道（邮件、论坛、社交媒体等）

## 输出

1. **结构化反馈清单**：分类标签、情感分析、典型原声
2. **痛点分类报告**：功能缺陷、体验不佳、价格争议、客服态度、竞品对比
3. **需求提取清单**：明确需求、潜在需求、改进需求
4. **反馈趋势分析**：时间维度上的反馈变化趋势

## 核心能力

### 多源数据整合
- 统一数据格式：将不同渠道的反馈数据标准化
- 去重处理：识别并合并重复反馈
- 时间对齐：按时间维度整合各渠道数据

### 智能语义处理
- 情感分析：正面、负面、中性情感识别
- 意图识别：投诉、建议、咨询、表扬
- 主题聚类：自动归类到预定义分类体系
- 关键词提取：识别高频问题和热点话题

### 结构化输出
- 反馈卡片：单条反馈的结构化展示
- 汇总报告：按分类、渠道、时间维度的统计
- 趋势图表：反馈量、情感分布、主题占比的变化

## 使用方式

```bash
# 处理单渠道反馈
python scripts/process_feedback.py --input customer_service.csv --channel cs --output feedback_report.md

# 批量处理多渠道反馈
python scripts/process_feedback.py --config multi_channel.json --output unified_report.md

# 生成反馈趋势分析
python scripts/process_feedback.py --input feedback_data/ --trend-analysis --period 30d --output trend_report.md

# 提取痛点和需求
python scripts/process_feedback.py --input feedback.csv --extract-pain-points --output pain_points.md
```

## 参考文档

- `references/feedback_sources.md` - 反馈渠道配置指南
- `references/classification_taxonomy.md` - 反馈分类体系
- `references/sentiment_analysis_guide.md` - 情感分析指南