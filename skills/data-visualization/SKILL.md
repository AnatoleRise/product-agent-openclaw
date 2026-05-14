---
name: data-visualization
description: 数据可视化与看板生成技能。当用户需要：(1) 生成用户之声仪表盘，(2) 生成核心功能使用数据看板，(3) 将分析结果转化为可视化图表，(4) 创建可交互的数据报告时，使用此技能。输入为分析后的数据（舆情分析结果、指标趋势数据、反馈分类数据等）；输出为HTML看板、图表集合、可视化报告。支持多种图表类型（趋势图、饼图、热力图、词云等）和自定义主题。
---

# 数据可视化与看板生成

## 核心定位

将复杂的分析结果转化为直观、可交互的可视化看板，让产品团队一眼看清产品健康度和用户声音。

## 输入

- 舆情分析结果（情感分布、痛点排行、版本趋势）
- 指标趋势数据（DAU/MAU、容量变化、增长率）
- 反馈分类数据（分类占比、渠道分布、时间趋势）
- 预警数据（异常点、风险等级、触发时间）

## 输出

1. **用户之声仪表盘**：舆情总览、痛点排行、情感趋势
2. **核心功能使用数据看板**：指标趋势、量价分析、异常标记
3. **可视化报告**：可交互的HTML报告，支持钻取和筛选
4. **图表集合**：独立图表文件，便于嵌入其他文档

## 核心能力

### 用户之声仪表盘
- 舆情总览：今日/本周/本月反馈量、情感分布
- 痛点排行：Top 10 问题，支持按版本、渠道筛选
- 情感趋势：时间维度上的情感变化曲线
- 关键词云：高频问题关键词可视化
- 版本对比：不同版本的舆情表现对比

### 核心功能使用数据看板
- 指标卡片：DAU/MAU、上传/下载用户数、容量等核心指标
- 趋势图表：折线图展示指标变化趋势
- 量价分析：散点图或组合图展示用户与容量关系
- 异常标记：在趋势图上标注异常点
- 对比分析：支持多维度对比（版本、渠道、用户群）

### 可视化组件
- 趋势图：折线图、面积图（时间序列数据）
- 占比图：饼图、环形图、堆叠柱状图（分类占比）
- 对比图：柱状图、分组柱状图（多维度对比）
- 分布图：热力图、箱线图（数据分布）
- 文本可视化：词云、情感河流图（文本数据）

## 使用方式

```bash
# 生成用户之声仪表盘
python scripts/generate_dashboard.py --type user_voice --input sentiment_data.json --output user_voice_dashboard.html

# 生成核心功能数据看板
python scripts/generate_dashboard.py --type core_metrics --input metrics_data.json --output metrics_dashboard.html

# 生成综合看板
python scripts/generate_dashboard.py --type comprehensive --input data/ --output full_dashboard.html

# 生成独立图表
python scripts/generate_chart.py --data trend_data.csv --chart-type line --output trend_chart.png
python scripts/generate_chart.py --data distribution_data.csv --chart-type pie --output distribution_chart.png
```

## 参考文档

- `references/chart_types.md` - 图表类型选择指南
- `references/dashboard_design.md` - 看板设计规范
- `references/color_themes.md` - 配色方案