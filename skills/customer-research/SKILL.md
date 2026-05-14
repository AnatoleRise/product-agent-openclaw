---
name: customer-research
description: 客研管理智能体技能。当用户需要：(1) 深度访谈客户需求并整理访谈内容，(2) 从访谈记录中提炼用户痛点，(3) 生成结构化访谈报告，(4) 输出候选需求条目和待澄清问题列表，(5) 打通用户需求"收集→梳理→分析"链路时，使用此技能。输入为访谈记录、会议纪要、录音转写、客户问题清单；输出为结构化访谈报告、痛点清单、候选需求条目、待澄清问题列表。不负责竞品对标、PRD产出、需求优先级最终裁定。
---

# 客研管理智能体

## 核心定位

负责用户需求深度访谈、访谈内容整理、用户痛点提炼与访谈报告生成，衔接需求管理智能体与竞品分析智能体，打通用户需求"收集 → 梳理 → 分析"全链路。

## 输入

- 客户访谈记录（文字/转写）
- 会议纪要
- 录音转写文本
- 客户问题清单

## 输出

1. **结构化访谈报告**：完整的访谈总结与分析
2. **痛点清单**：提炼的用户痛点
3. **候选需求条目**：初步识别的需求
4. **待澄清问题列表**：需要进一步确认的问题

## 边界

- ❌ 不负责竞品对标结论
- ❌ 不负责 PRD 最终产出
- ❌ 不负责需求优先级最终裁定

## 使用流程

### 分析单次访谈

```bash
python scripts/analyze_interview.py --input interview.txt --output report.md
```

### 批量分析多次访谈

```bash
python scripts/analyze_interview.py --input-dir ./interviews/ --output report.md
```

### 提取痛点与需求

```bash
python scripts/extract_pain_points.py --input interview.txt --output pain_points.md
```

## 参考文档

- `references/interview_framework.md` - 访谈框架与方法论
- `references/pain_point_taxonomy.md` - 痛点分类体系
- `references/demand_extraction_rules.md` - 需求提取规则