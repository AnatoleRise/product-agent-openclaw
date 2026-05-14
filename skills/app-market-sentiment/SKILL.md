---
name: app-market-sentiment
description: 应用市场舆情洞察与痛点挖掘技能。当用户需要：(1) 分析应用商店用户评论，(2) 识别版本发布后的舆情风险，(3) 从海量吐槽中提炼用户真实需求，(4) 生成痛点排行榜和版本趋势对比，(5) 检测爆发式负面舆情并预警时，使用此技能。输入为应用市场评论数据（App Store、应用宝、华为应用市场等）；输出为结构化舆情报告、痛点清单、紧急预警。支持多源评论自动采集、智能语义分析与去重、版本关联分析。
---

# 应用市场舆情洞察与痛点挖掘

## 核心定位

将海量、杂乱的用户评论转化为结构化的"产品改进需求清单"，实现版本发布后舆情监控，快速确认是否存在重大Bug或体验倒退。

## 输入

- 应用市场评论数据（App Store、应用宝、华为应用市场、小米应用商店等）
- 版本发布记录
- 历史评论数据（用于趋势对比）

## 输出

1. **结构化舆情报告**：情感分析、问题聚类、版本趋势
2. **痛点排行榜**：按频次和严重程度排序的问题清单
3. **紧急预警**：爆发式负面舆情警报
4. **改进建议**：基于问题类型的初步解决方案

## 核心能力

### 多源评论自动采集
- 增量监控：每日自动抓取新增评论，重点关注近7天和近30天
- 版本关联：自动识别评论对应的软件版本号
- 评分过滤：重点抓取1-3星低分评论，抽样4-5星中的建议部分

### 智能语义分析与去重
- 负面情感识别：精准识别愤怒、失望、困惑等情绪
- 问题聚类：语义归并（如"打不开""闪退""崩溃"归并为【稳定性-启动异常】）
- 热度排序：统计同类问题出现频次
- 版本趋势对比：分析问题是否随新版本发布而激增

### 结构化输出与预警
- 痛点清单：问题类别、典型原声、影响范围
- 紧急预警：爆发式负面舆情立即警报
- 改进建议：匹配历史解决方案库或竞品做法

## 使用方式

```bash
# 分析指定应用市场的评论
python scripts/analyze_app_reviews.py --source appstore --app-id xxx --days 7 --output report.md

# 批量分析多个应用市场
python scripts/analyze_app_reviews.py --sources appstore,huawei,xiaomi --days 30 --output report.md

# 版本对比分析
python scripts/analyze_app_reviews.py --source appstore --version v2.5 --compare-version v2.4 --output version_compare.md
```

## 参考文档

- `references/review_sources.md` - 应用市场数据源配置
- `references/sentiment_analysis_framework.md` - 情感分析框架
- `references/pain_point_taxonomy.md` - 痛点分类体系