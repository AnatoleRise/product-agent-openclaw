# Product Exploration Skill Kit

A platform-agnostic AI skill kit for product exploration and competitor research. It helps product managers move from "manually finding information" to reviewing AI-collected evidence, structured analysis, and competitor difference panels.

一个面向产品经理的产品探索智能体技能包。它通过自动抓取竞品网页、生成结构化竞品分析报告、输出竞品差异面板，帮助产品经理缩短信息搜集周期，并把注意力放在判断与决策上。

[English](#english) | [中文](#中文)

---

## English

### Positioning

This skill kit solves long manual research cycles and incomplete information gathering during product planning, feature iteration, and competitor monitoring.

### How It Works

```text
User Query → Intent Recognition → competitor-web-crawler (web_search + web_fetch) → report-generator → difference-panel → Competitor Analysis Report
```

The skill provides the **strategy**: what to search, which pages to fetch, how to clean evidence, how to structure the report, and how to render the difference panel. Your AI agent provides the **execution**: OpenClaw tools, file reading, and reasoning.

### Quick Start

```bash
git clone https://github.com/750928465/competitor-research-skill-kit.git
```

Copy the skill directories to your agent's skill directory:
- **OpenClaw**: Copy `skills/*` to `~/.openclaw/workspace/skills/`
- **Claude Code**: Copy `skills/*` to `.claude/skills/`
- **Other agents**: Point your agent to the project root or import the `skills/` directory

### Usage

Simply ask your agent:

```text
"AI customer service market opportunities"
"How do competitors implement membership points?"
"Superhuman vs Front comparison"
"Monitor Notion pricing and release updates"
```

### Core Scenarios

| Scenario | Example Input | Output Focus |
|----------|---------------|--------------|
| Product planning | "AI customer service market opportunities" | Market structure, key players, gaps, opportunities |
| Feature design and iteration | "Membership points competitor implementation" | Implementation patterns, user feedback, pitfalls, best practices |
| Market monitoring and risk alert | "Monitor Notion pricing and release updates" | Releases, pricing changes, campaigns, negative signals |

### Three Core Skills

| Skill | Responsibility |
|-------|----------------|
| `competitor-web-crawler` | Automatically discovers competitor pages with `web_search` and fetches key pages with `web_fetch` |
| `report-generator` | Cleans evidence and generates structured Markdown competitor analysis reports |
| `difference-panel` | Outputs a competitor difference panel with status labels and citations |

`product-exploration` is the orchestrator skill that coordinates the three core skills.

### Project Structure

```text
competitor-research-skill-kit/
├── AGENTS.md
├── SOUL.md
├── IDENTITY.md
├── README.md
└── skills/
    ├── product-exploration/                     # Main orchestrator skill
    │   └── SKILL.md
    ├── competitor-web-crawler/                  # Competitor page discovery and fetching
    │   ├── SKILL.md
    │   ├── references/
    │   │   ├── intent_parser.md
    │   │   └── search_strategy.md
    │   └── assets/
    │       └── sources.yaml
    ├── report-generator/                        # Structured report generation
    │   ├── SKILL.md
    │   └── references/
    │       ├── data_cleaning.md
    │       ├── report_template.md
    │       └── example_output.md
    └── difference-panel/                        # Competitor difference panel
        ├── SKILL.md
        └── references/
            └── panel_template.md
```

### Requirements

Your AI agent needs:
- **OpenClaw `web_search` tool** (required) — for discovering competitor pages and market sources
- **OpenClaw `web_fetch` tool** (required) — for fetching official pages, pricing pages, docs, changelogs, and evidence-rich sources
- **File reading** capability — to load skill references and assets

For non-OpenClaw agents, map `web_search` and `web_fetch` to the platform's equivalent web search and URL fetch tools.

### Output

The final output is a Markdown competitor analysis report, including:
- Executive summary
- Research scope and information gaps
- Competitor difference panel
- Market/product/feature/monitoring analysis
- Opportunities, risks, and validation questions
- References

### License

MIT License

---

## 中文

### 定位

产品探索智能体用于把产品经理从传统的“人找信息”模式中释放出来。智能体负责搜集、抓取、整理竞品信息，并输出分析结论、竞品差异面板和竞品分析报告；产品经理只需要辨别信息、验证关键假设并做决策。

解决的问题：
- 人工竞品分析周期长
- 信息搜集不全
- 功能方案设计缺少行业参照
- 核心竞品动态感知滞后

### 工作原理

```text
用户查询 → 意图识别 → competitor-web-crawler（web_search + web_fetch）→ report-generator → difference-panel → 竞品分析报告
```

技能包提供**策略**：搜什么、抓哪些页面、如何清洗证据、如何生成报告、如何输出差异面板。你的 AI 助手提供**执行能力**：OpenClaw 工具调用、文件读取和推理。

### 快速开始

```bash
git clone https://github.com/750928465/competitor-research-skill-kit.git
```

将技能目录复制到你智能体的技能目录下：
- **OpenClaw**：复制 `skills/*` 到 `~/.openclaw/workspace/skills/`
- **Claude Code**：复制 `skills/*` 到 `.claude/skills/`
- **其他智能体**：指向项目根目录或导入 `skills/` 目录即可

### 使用方式

直接向你的智能体提问：

```text
"AI客服市场立项分析"
"主流 SaaS 的会员积分体系怎么做"
"Superhuman vs Front 功能对比"
"监控 Notion 最近价格和版本更新"
```

### 核心场景

| 场景 | 示例输入 | 输出重点 |
|------|----------|----------|
| 产品立项与规划阶段 | "AI客服市场立项分析" | 市场格局、主要玩家、市场空白点、潜在机会 |
| 产品功能设计与迭代阶段 | "会员积分体系竞品怎么做" | 实现方式、用户反馈、优劣势、已知坑点、最佳实践 |
| 市场动态与风险预警 | "监控 Notion 最近价格和版本更新" | 版本更新、价格调整、市场活动、负面舆情、风险等级 |

### 三个核心技能

| Skill | 职责 |
|-------|------|
| `competitor-web-crawler` | 自动发现竞品网页，使用 `web_search` 检索并用 `web_fetch` 抓取关键页面 |
| `report-generator` | 清洗网页证据并生成结构化 Markdown 竞品分析报告 |
| `difference-panel` | 输出带状态标签和来源引用的竞品差异面板 |

`product-exploration` 是主编排技能，负责协调上述三个核心技能。

### 项目结构

```text
competitor-research-skill-kit/
├── AGENTS.md
├── SOUL.md
├── IDENTITY.md
├── README.md
└── skills/
    ├── product-exploration/                     # 主技能（编排调度）
    │   └── SKILL.md
    ├── competitor-web-crawler/                  # 竞品网页自动发现与抓取
    │   ├── SKILL.md
    │   ├── references/ (intent_parser, search_strategy)
    │   └── assets/     (sources.yaml)
    ├── report-generator/                        # 结构化报告生成
    │   ├── SKILL.md
    │   └── references/ (data_cleaning, report_template, example_output)
    └── difference-panel/                        # 竞品差异面板
        ├── SKILL.md
        └── references/ (panel_template)
```

### 工具要求

- **OpenClaw `web_search`**：必需，用于发现竞品网页和市场来源
- **OpenClaw `web_fetch`**：必需，用于抓取官网、定价页、功能页、文档、更新日志和高价值证据页
- **文件读取能力**：必需，用于加载各 skill 的 references 和 assets

非 OpenClaw 平台可将 `web_search` 和 `web_fetch` 映射为等价的网页搜索与 URL 抓取工具。

### 输出物

最终输出为 Markdown 竞品分析报告，包含：
- 执行摘要
- 研究范围与信息缺口
- 竞品差异面板
- 市场/产品/功能/动态分析
- 机会点、风险点和待验证问题
- References

### 许可证

MIT License
