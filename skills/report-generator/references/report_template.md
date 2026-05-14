# Report Template

## Purpose

Define the structure and formatting rules for product exploration reports. The final output is always a Markdown competitor analysis report with an embedded competitor difference panel.

## Report Types

Select the appropriate template based on `intent_type`.

### 1. Product Planning and Market Landscape Report

Use when `intent_type = market_landscape`.

```markdown
# {target_market} 产品探索与竞品分析报告

---

## Executive Summary

[2-3 sentences summarizing market structure, key players, opportunity gaps, and major risks.]

---

## 研究范围与信息缺口

| 项目 | 内容 |
|------|------|
| 目标市场 | |
| 覆盖竞品 | |
| 信息来源 | |
| 信息缺口 | |

---

## 竞品差异面板

[由 difference-panel 子技能填充]

---

## 市场概览

- 市场格局与主要玩家 [1]
- 用户/客户需求变化 [2]
- 增长驱动与主要阻碍 [3]

---

## 主要玩家

| # | Product | Vendor | Website | Positioning | Verification |
|---|---------|--------|---------|-------------|--------------|
| 1 | | | | | |

---

## 机会点与空白

| 机会点 | 证据 | 相关竞品 | 不确定性 |
|--------|------|----------|----------|
| | | | |

---

## 风险与约束

| 风险 | 影响 | 证据 | 建议验证 |
|------|------|------|----------|
| | | | |

---

## 产品规划建议

- 可考虑方向 1：... [1]
- 需验证问题 1：...

---

## References

[1] Title - URL
```

### 2. Feature Design and Iteration Report

Use when `intent_type = feature_iteration`.

```markdown
# {feature_focus} 功能探索与竞品分析报告

---

## Executive Summary

[2-3 sentences summarizing competitor implementations, best practices, pitfalls, and design opportunities.]

---

## 研究范围与信息缺口

| 项目 | 内容 |
|------|------|
| 目标功能 | |
| 覆盖竞品 | |
| 覆盖页面 | |
| 信息缺口 | |

---

## 竞品差异面板

[由 difference-panel 子技能填充]

---

## 竞品实现方式

| Product | Entry Point | Core Flow | Rules/Permissions | Feedback/Data | Sources |
|---------|-------------|-----------|-------------------|---------------|---------|
| | | | | | |

---

## 用户反馈与已知坑点

| 问题/反馈 | 涉及产品 | 证据 | 可借鉴/规避 |
|-----------|----------|------|-------------|
| | | | |

---

## 最佳实践提炼

1. **Practice 1**: Description with evidence [1]
2. **Practice 2**: Description with evidence [2]

---

## 功能方案建议

- 可考虑设计：...
- 需要验证：...

---

## References

[1] Title - URL
```

### 3. Competitive Comparison Report

Use when `intent_type = product_competition`.

```markdown
# {target_product} 竞品对比分析报告

---

## Executive Summary

[2-3 sentences about the competitive landscape and differentiation.]

---

## 研究范围与信息缺口

| 项目 | 内容 |
|------|------|
| 目标产品 | |
| 对比竞品 | |
| 信息来源 | |
| 信息缺口 | |

---

## 竞品差异面板

[由 difference-panel 子技能填充]

---

## Products Overview

| Attribute | Product A | Product B | Product C |
|-----------|-----------|-----------|-----------|
| Vendor | | | |
| Website | | | |
| Target User | | | |
| Pricing | | | |

---

## Feature Comparison

| Feature | Product A | Product B | Product C | Evidence |
|---------|-----------|-----------|-----------|----------|
| Feature 1 | Yes/No/Unknown | Yes/No/Unknown | Yes/No/Unknown | [1] |

---

## Differentiation

- **Product A**: Unique strength with evidence [1]
- **Product B**: Unique strength with evidence [2]

---

## Recommendations

- Best for {scenario}: {product} because...
- Needs validation: ...

---

## References

[1] Title - URL
```

### 4. Market Monitoring and Risk Alert Report

Use when `intent_type = market_monitoring`.

```markdown
# {target_product_or_market} 市场动态与风险预警报告

---

## Executive Summary

[2-3 sentences summarizing recent updates, pricing/campaign changes, negative signals, and risk level.]

---

## 监控范围与信息缺口

| 项目 | 内容 |
|------|------|
| 监控对象 | |
| 监控信号 | release / pricing / campaign / risk |
| 时间范围 | |
| 信息缺口 | |

---

## 竞品差异面板

[由 difference-panel 子技能填充]

---

## 动态摘要

| Date | Product | Signal | Summary | Source | Verification |
|------|---------|--------|---------|--------|--------------|
| | | | | | |

---

## 价格与市场活动变化

| Product | Change | Evidence | Potential Impact |
|---------|--------|----------|------------------|
| | | | |

---

## 风险信号

| Risk | Product | Severity | Evidence | Uncertainty |
|------|---------|----------|----------|-------------|
| | | Low/Medium/High | | |

---

## 响应建议

- 需要立即关注：...
- 后续监控建议：...

---

## References

[1] Title - URL
```

## Writing Rules

1. **Evidence-based**: Every claim should reference a source `[1]`.
2. **No fabrication**: Write "未在搜索结果中找到" for missing data.
3. **Objective tone**: Avoid promotional language and final business decisions.
4. **Panel required**: Every report must include `## 竞品差异面板`.
5. **Concise**: Prefer tables over paragraphs for comparative data.
6. **Source attribution**: List all source URLs in the References section.
7. **Honest gaps**: Explicitly note what information is missing or unverified.
