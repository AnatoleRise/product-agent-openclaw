# 产品探索智能体

`product_discovery/` 是产品管理多 Agent 团队中的产品探索子智能体目录，对应 OpenClaw Agent ID：`product_discovery`。

## 文件结构

```text
product_discovery/
├── AGENTS.md
├── SOUL.md
├── IDENTITY.md
└── README.md
```

## 依赖技能

```text
skills/
├── product-exploration/
├── competitor-web-crawler/
├── report-generator/
└── difference-panel/
```

| Skill | 职责 |
|-------|------|
| `product-exploration` | workflow 主技能，先做意图判断，再编排抓取、报告和差异面板 |
| `competitor-web-crawler` | 生成检索策略，使用网页搜索和抓取工具收集竞品证据 |
| `report-generator` | 清洗证据，生成结构化竞品分析报告 |
| `difference-panel` | 输出维度化竞品差异面板，标注领先、持平、缺失、未知和来源 |

## 适用任务

- 产品立项与市场格局扫描
- 竞品对比和替代方案分析
- 功能实现方式与坑点调研
- 竞品版本、价格、活动和舆情监控
- 商业模式、运营玩法、渠道入口、权益体系、生态分润和 MVP 路径调研

## 输出要求

最终报告必须包含：

- 执行摘要
- 研究范围与信息缺口
- 竞品差异面板
- 场景化分析章节
- 机会、风险与验证问题
- References

## 证据规则

- 每个关键判断必须绑定来源。
- 市场格局或开放式竞品研究默认识别 5 个核心竞品。
- 每个核心竞品尽量保留至少 3 个可信来源。
- 证据不足时最多补充搜索 2 轮。
- 商业模式和运营玩法必须区分公开事实、策略推断和待验证问题。
- 未找到公开证据的信息写"未披露"或"公开资料未披露"，不得直接写成"没有"。
