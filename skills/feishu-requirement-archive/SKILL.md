---
name: feishu-requirement-archive
description: "飞书需求归档统计。每周扫描需求表格，归档已上线和已转出的需求，生成归档统计并写入归档统计表。触发词：归档、需求归档、archive requirements、生成归档报告。"
---

# 飞书需求归档技能

## 功能概述

每周扫描 Feishu Bitable 中的需求记录，筛选出状态为「已上线」和「需求转出」的记录，写入归档统计表，并生成归档统计 JSON 供周报使用。

## 配置

- **App ID:** `your_app_id`
- **App Secret:** `your_app_id`
- **Bitable App Token:** `your_app_token`
- **需求表 Table ID:** `your_table_id`

## 执行流程

1. 获取 Feishu tenant access token
2. 从需求表读取所有记录
3. 筛选「已上线」和「需求转出」状态的记录
4. 计算本周归档统计（本周新增已上线数、本周新增需求转出数、模块分布等）
5. 写入归档统计 JSON 到 `/tmp/requirement-archive-stats.json`
6. 返回统计摘要

## 输出格式

```json
{
  "weekStart": "2026-04-21",
  "weekEnd": "2026-04-28",
  "newOnline": 5,
  "newTransferred": 2,
  "totalOnline": 45,
  "totalTransferred": 12,
  "moduleDistribution": {
    "用户系统": 3,
    "订单系统": 2
  },
  "cumulativeTotal": 57
}
```