---
name: core-metrics-analysis
description: 核心业务指标趋势分析技能。当用户需要：(1) 分析DAU/MAU等规模指标趋势，(2) 分析上传/下载容量等价值指标变化，(3) 检测量价背离等异常模式，(4) 进行同环比趋势监测和异常检测，(5) 生成指标诊断报告时，使用此技能。输入为核心业务指标数据（日活、月活、上传/下载用户数、上传/下载容量等）；输出为趋势分析报告、量价背离诊断、异常预警、归因推测。支持自动计算衍生关键比率（人均容量等）。
---

# 核心业务指标趋势分析

## 核心定位

在缺乏行为路径的情况下，通过"规模指标"（用户数）与"价值指标"（容量/流量）的交叉分析，诊断产品健康度与增长质量。

## 输入

- 规模指标：日活(DAU)、月活(MAU)、上传用户数、下载用户数
- 价值指标：上传总容量、下载总容量
- 历史数据：用于基线计算和趋势对比

## 输出

1. **趋势分析报告**：同环比趋势、增长率曲线
2. **量价背离诊断**：用户与容量的交叉分析
3. **异常检测报告**：非季节性异常波动识别
4. **归因推测报告**：指标异动与舆情的关联分析

## 核心能力

### 指标体系定义与接入
- 规模指标（用户侧）：DAU/MAU、上传/下载用户数
- 价值指标（资源侧）：上传/下载总容量
- 衍生关键比率：人均容量 = 总容量 / 活跃用户数

### 多维趋势分析
- 同环比趋势监测：日/周/月的环比(WoW, MoM)和同比(YoY)
- 异常检测：基于历史数据基线，识别非季节性异常波动
- 量价/量容背离分析：
  - 用户涨，容量跌 → 警惕"水货用户"
  - 用户跌，容量涨 → 警惕"大户依赖"
  - 功能使用率下降 → 功能边缘化

### 归因推测与报告
- 关联分析：将指标异动与舆情自动关联
- 周期性报告：日报、周报、月报自动生成

## 使用方式

```bash
# 分析核心指标趋势
python scripts/analyze_core_metrics.py --metrics dau,mau,upload_users,download_users,upload_capacity,download_capacity --period 30d --output report.md

# 量价背离分析
python scripts/analyze_core_metrics.py --analysis divergence --period 7d --output divergence_report.md

# 异常检测
python scripts/analyze_core_metrics.py --metrics all --detect-anomalies --threshold 2sigma --output anomalies.json

# 生成周期性报告
python scripts/analyze_core_metrics.py --report-type daily --output daily_report.md
python scripts/analyze_core_metrics.py --report-type weekly --output weekly_report.md
```

## 参考文档

- `references/metrics_definition.md` - 指标定义与计算规则
- `references/anomaly_detection_rules.md` - 异常检测规则
- `references/divergence_analysis_framework.md` - 量价背离分析框架