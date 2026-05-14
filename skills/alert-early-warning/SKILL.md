---
name: alert-early-warning
description: 主动预警与风险拦截技能。当用户需要：(1) 检测爆发式负面舆情并发送警报，(2) 监控核心业务指标异常波动，(3) 设置自定义预警规则，(4) 生成风险拦截建议时，使用此技能。输入为实时或准实时的舆情数据、指标数据；输出为预警通知、风险等级评估、应对建议。支持多级别预警（高/中/低）、多渠道通知（飞书/钉钉/邮件）、智能阈值调整。
---

# 主动预警与风险拦截

## 核心定位

从"被动救火"转为"主动预警"，利用AI实时捕捉舆情爆发点与指标异常值，将风险拦截在萌芽状态。

## 输入

- 实时舆情数据（应用市场评论、社群消息、客服工单）
- 实时指标数据（DAU/MAU、容量、用户数）
- 历史基线数据（用于异常判断）
- 预警规则配置（阈值、条件、通知方式）

## 输出

1. **预警通知**：包含问题摘要、风险等级、影响范围
2. **风险等级评估**：高/中/低三级风险评估
3. **应对建议**：基于问题类型的初步处理建议
4. **预警历史**：预警触发记录和处理状态

## 核心能力

### 舆情预警
- 爆发式负面检测：短时间内同一关键词大量出现
- 情感突变检测：整体情感评分突然下降
- 版本问题预警：新版本发布后负面评论激增
- 热点话题预警：新兴问题快速升温

### 指标预警
- 阈值突破预警：指标超过预设上下限
- 异常波动预警：基于统计模型的异常检测（2σ/3σ规则）
- 趋势恶化预警：连续多日下滑或增速放缓
- 量价背离预警：用户与容量关系异常

### 预警管理
- 多级别预警：🔴严重、🟡警告、💡关注
- 智能降噪：避免重复预警、误报过滤
- 阈值自适应：基于历史数据自动调整阈值
- 预警收敛：相关预警合并，避免轰炸

### 通知渠道
- 飞书/钉钉：即时消息通知
- 邮件：详细报告发送
- Webhook：对接企业内部系统
- 仪表盘：可视化预警展示

## 使用方式

```bash
# 检测舆情爆发
python scripts/detect_anomalies.py --type sentiment --input reviews.json --threshold 3sigma --output alerts.json

# 检测指标异常
python scripts/detect_anomalies.py --type metrics --input metrics.json --metrics dau,mau --threshold 2sigma --output alerts.json

# 启动持续监控
python scripts/monitor.py --config monitor_config.json --interval 300 --output alert_stream.json

# 发送预警通知
python scripts/send_alert.py --input alerts.json --channels feishu,email --output notification_log.json
```

## 预警规则配置示例

```json
{
  "sentiment_rules": [
    {
      "name": "爆发式负面舆情",
      "condition": "negative_count > 50 AND growth_rate > 300%",
      "level": "critical",
      "window": "1h"
    },
    {
      "name": "版本问题预警",
      "condition": "version_negative_rate > 30%",
      "level": "warning",
      "window": "24h"
    }
  ],
  "metrics_rules": [
    {
      "name": "DAU骤降",
      "metric": "dau",
      "condition": "drop_rate > 20%",
      "level": "critical"
    },
    {
      "name": "容量异常",
      "metric": "upload_capacity",
      "condition": "deviation > 2sigma",
      "level": "warning"
    }
  ]
}
```

## 参考文档

- `references/alert_rules.md` - 预警规则配置指南
- `references/anomaly_detection.md` - 异常检测算法说明
- `references/notification_channels.md` - 通知渠道配置