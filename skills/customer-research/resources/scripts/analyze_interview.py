#!/usr/bin/env python3
"""
客研管理智能体 - 访谈分析脚本
输出：结构化访谈报告、痛点清单、候选需求条目、待澄清问题列表
"""

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime

def analyze_interview(input_path=None, input_dir=None, output_path=None):
    """
    分析访谈记录
    
    Args:
        input_path: 单次访谈记录路径
        input_dir: 多次访谈记录目录
        output_path: 输出文件路径
    
    Returns:
        分析结果
    """
    
    if input_dir:
        print(f"📁 批量分析访谈记录：{input_dir}")
        records = load_records_from_dir(input_dir)
    elif input_path:
        print(f"📄 分析访谈记录：{input_path}")
        records = [load_record(input_path)]
    else:
        print("❌ 请提供输入文件或目录")
        return None
    
    if not records:
        print("⚠️ 未找到有效记录")
        return None
    
    print(f"📊 分析 {len(records)} 条访谈记录")
    
    # 分析记录
    analysis = {
        "basic_info": extract_basic_info(records),
        "interview_summary": generate_summary(records),
        "pain_points": extract_pain_points(records),
        "candidate_requirements": extract_requirements(records),
        "open_questions": generate_open_questions(records),
        "key_findings": extract_key_findings(records),
        "sentiment_analysis": analyze_sentiment(records)
    }
    
    # 生成报告
    report = format_report(analysis)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ 访谈分析报告已生成：{output_path}")
    
    return analysis

def load_record(file_path):
    """加载单条记录"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 尝试提取日期
    date_match = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', content)
    date = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")
    
    # 尝试提取客户名称
    company_match = re.search(r'客户[：:]\s*(.+?)[\n\r]', content)
    company = company_match.group(1).strip() if company_match else "待确认"
    
    return {
        "date": date,
        "company": company,
        "content": content,
        "source": os.path.basename(file_path)
    }

def load_records_from_dir(input_dir):
    """从目录加载多条记录"""
    records = []
    
    if not os.path.exists(input_dir):
        return records
    
    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith(('.txt', '.md')):
            filepath = os.path.join(input_dir, filename)
            try:
                record = load_record(filepath)
                records.append(record)
            except Exception as e:
                print(f"⚠️ 加载失败 {filename}: {e}")
    
    return records

def extract_basic_info(records):
    """提取基本信息"""
    return {
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total_interviews": len(records),
        "date_range": {
            "start": records[0]["date"] if records else "",
            "end": records[-1]["date"] if records else ""
        },
        "customers": list(set([r["company"] for r in records]))
    }

def generate_summary(records):
    """生成访谈摘要"""
    all_content = "\n\n".join([r["content"] for r in records])
    
    # 提取关键句子
    sentences = re.split(r'[。！？\n]', all_content)
    key_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 20 and len(sentence) < 100:
            # 包含关键词的句子更可能是关键信息
            keywords = ['需要', '希望', '痛点', '问题', '建议', '期望', '困难']
            if any(kw in sentence for kw in keywords):
                key_sentences.append(sentence)
        if len(key_sentences) >= 5:
            break
    
    return {
        "overview": f"共分析 {len(records)} 次访谈记录，涉及 {len(set([r['company'] for r in records]))} 个客户",
        "key_points": key_sentences[:5]
    }

def extract_pain_points(records):
    """提取痛点清单"""
    all_content = "\n\n".join([r["content"] for r in records])
    
    patterns = [
        r'(?:痛点|困难|问题|挑战)(?:是|在于|有)?[：:]?\s*(.{5,60})',
        r'(?:不方便|不好用|不满意)(?:的是)?(.{5,60})',
        r'(?:耗时|费力|麻烦)(?:的是)?(.{5,60})',
        r'(?:缺乏|不足|不够)(.{5,60})',
        r'(.{5,40})(?:太|很|非常)(?:麻烦|复杂|困难|痛苦)'
    ]
    
    pain_points = []
    seen = set()
    
    for pattern in patterns:
        matches = re.findall(pattern, all_content)
        for match in matches:
            match = match.strip()
            if match not in seen and len(match) > 5:
                seen.add(match)
                pain_points.append({
                    "description": match,
                    "severity": assess_severity(match),
                    "frequency": 1,
                    "category": classify_pain_point(match)
                })
    
    # 统计频次
    pain_counter = Counter([p["description"] for p in pain_points])
    for p in pain_points:
        p["frequency"] = pain_counter[p["description"]]
    
    # 去重并排序
    unique_pains = []
    seen = set()
    for p in pain_points:
        if p["description"] not in seen:
            seen.add(p["description"])
            unique_pains.append(p)
    
    unique_pains.sort(key=lambda x: (x["frequency"], x["severity"] == "高"), reverse=True)
    
    return unique_pains[:15]

def assess_severity(text):
    """评估痛点严重程度"""
    high_indicators = ['核心', '关键', '严重', '非常', '极其', '根本']
    if any(kw in text for kw in high_indicators):
        return "高"
    return "中"

def classify_pain_point(text):
    """分类痛点"""
    if any(kw in text for kw in ['功能', '能力', '系统']):
        return "功能缺失"
    elif any(kw in text for kw in ['体验', '操作', '界面', '流程']):
        return "体验问题"
    elif any(kw in text for kw in ['性能', '速度', '响应', '卡顿']):
        return "性能问题"
    elif any(kw in text for kw in ['成本', '价格', '费用', '预算']):
        return "成本问题"
    elif any(kw in text for kw in ['服务', '支持', '售后']):
        return "服务问题"
    else:
        return "其他"

def extract_requirements(records):
    """提取候选需求条目"""
    all_content = "\n\n".join([r["content"] for r in records])
    
    patterns = [
        r'(?:需要|希望|想要|期望)(.{5,60})(?:功能|能力|特性|方案)',
        r'(?:建议|推荐)(.{5,60})(?:增加|添加|开发|优化)',
        r'(?:如果能|要是)(.{5,60})(?:就好了|就更好了)',
        r'(.{5,40})(?:必须|一定要|最好能)(.{3,30})'
    ]
    
    requirements = []
    seen = set()
    
    for pattern in patterns:
        matches = re.findall(pattern, all_content)
        for match in matches:
            if isinstance(match, tuple):
                match = ''.join(match)
            match = match.strip()
            if match not in seen and len(match) > 5:
                seen.add(match)
                requirements.append({
                    "description": match,
                    "category": classify_requirement(match),
                    "source": "访谈提取",
                    "confidence": "中",
                    "status": "候选"
                })
    
    # 去重并排序
    unique_reqs = []
    seen = set()
    for req in requirements:
        if req["description"] not in seen:
            seen.add(req["description"])
            unique_reqs.append(req)
    
    return unique_reqs[:15]

def classify_requirement(text):
    """分类需求"""
    if any(kw in text for kw in ['功能', '模块', '系统', '能力']):
        return "功能需求"
    elif any(kw in text for kw in ['界面', '体验', '操作', '流程', '交互']):
        return "体验需求"
    elif any(kw in text for kw in ['性能', '速度', '响应', '并发', '稳定']):
        return "性能需求"
    elif any(kw in text for kw in ['数据', '报表', '分析', '统计']):
        return "数据需求"
    elif any(kw in text for kw in ['集成', '对接', '接口', 'API']):
        return "集成需求"
    else:
        return "其他需求"

def generate_open_questions(records):
    """生成待澄清问题列表"""
    all_content = "\n\n".join([r["content"] for r in records])
    
    open_questions = []
    
    # 基于模糊表述生成澄清问题
    vague_patterns = [
        (r'(?:大概|大约|可能|也许)(.{3,20})', "请确认具体时间/范围"),
        (r'(?:等等|之类|等等)', "请列举完整列表"),
        (r'(?:等|等等)(?:等)?', "请确认是否还有其他"),
        (r'(?:比较|相对|稍微)(.{3,20})', "请量化具体指标"),
        (r'(?:尽快|马上|近期)(.{0,10})', "请确认具体时间节点"),
        (r'(?:很多人|有些|部分)(.{3,20})', "请确认具体范围和比例"),
        (r'(?:预算|费用|价格)(?:大概|大约)?(.{0,10})', "请确认具体预算范围"),
        (r'(?:优先级|重要|紧急)(?:比较)?(.{0,10})', "请确认优先级排序")
    ]
    
    for pattern, question_type in vague_patterns:
        matches = re.findall(pattern, all_content)
        for match in matches:
            if isinstance(match, str) and len(match) > 2:
                open_questions.append({
                    "question": f"关于'{match}'，{question_type}",
                    "type": question_type,
                    "context": match,
                    "priority": "高" if "预算" in match or "时间" in match else "中"
                })
    
    # 去重
    unique_questions = []
    seen = set()
    for q in open_questions:
        if q["question"] not in seen:
            seen.add(q["question"])
            unique_questions.append(q)
    
    return unique_questions[:10]

def extract_key_findings(records):
    """提取关键发现"""
    all_content = "\n\n".join([r["content"] for r in records])
    
    findings = []
    
    # 1. 需求强度
    req_count = len(extract_requirements(records))
    if req_count > 5:
        findings.append({
            "finding": f"客户表达了 {req_count} 个需求，需求意愿强烈",
            "evidence": "多次提及功能改进期望",
            "confidence": "高"
        })
    
    # 2. 痛点集中度
    pain_count = len(extract_pain_points(records))
    if pain_count > 3:
        findings.append({
            "finding": f"识别到 {pain_count} 个痛点，存在明显改进空间",
            "evidence": "痛点涉及多个维度",
            "confidence": "高"
        })
    
    # 3. 决策倾向
    if any(kw in all_content for kw in ['预算', '采购', '购买', '合作']):
        findings.append({
            "finding": "客户有明确的采购/合作意向",
            "evidence": "提及预算和合作方式",
            "confidence": "中"
        })
    
    # 4. 时间窗口
    if any(kw in all_content for kw in ['Q1', 'Q2', 'Q3', 'Q4', '本季度', '年底']):
        findings.append({
            "finding": "客户有明确的时间要求",
            "evidence": "提及具体时间节点",
            "confidence": "中"
        })
    
    return findings

def analyze_sentiment(records):
    """分析情绪倾向"""
    all_content = "\n\n".join([r["content"] for r in records])
    
    positive_words = ['满意', '喜欢', '好', '不错', '优秀', '推荐']
    negative_words = ['不满意', '差', '麻烦', '困难', '痛苦', '失望']
    
    positive_count = sum(all_content.count(w) for w in positive_words)
    negative_count = sum(all_content.count(w) for w in negative_words)
    
    total = positive_count + negative_count
    if total == 0:
        sentiment = "中性"
        score = 0.5
    else:
        score = positive_count / total
        if score > 0.6:
            sentiment = "积极"
        elif score < 0.4:
            sentiment = "消极"
        else:
            sentiment = "中性"
    
    return {
        "overall": sentiment,
        "positive_signals": positive_count,
        "negative_signals": negative_count,
        "score": round(score, 2)
    }

def format_report(analysis):
    """格式化报告"""
    
    info = analysis["basic_info"]
    
    report = f"""# 📊 客研管理智能体 - 访谈分析报告

**分析时间**：{info['analysis_date']}  
**访谈次数**：{info['total_interviews']}  
**时间跨度**：{info['date_range']['start']} 至 {info['date_range']['end']}  
**涉及客户**：{', '.join(info['customers'])}

---

## 📝 访谈摘要

{analysis['interview_summary']['overview']}

### 关键要点

"""
    
    for i, point in enumerate(analysis['interview_summary']['key_points'], 1):
        report += f"{i}. {point}\n"
    
    report += f"""

---

## 🔍 关键发现

"""
    
    for i, finding in enumerate(analysis['key_findings'], 1):
        report += f"""### 发现 {i}：{finding['finding']}
- **证据**：{finding['evidence']}
- **置信度**：{finding['confidence']}

"""
    
    report += f"""---

## 😊 情绪分析

- **整体倾向**：{analysis['sentiment_analysis']['overall']}
- **积极信号**：{analysis['sentiment_analysis']['positive_signals']} 次
- **消极信号**：{analysis['sentiment_analysis']['negative_signals']} 次
- **情绪得分**：{analysis['sentiment_analysis']['score']}

---

## ⚠️ 痛点清单

| 序号 | 痛点描述 | 类别 | 严重程度 | 频次 |
|------|----------|------|----------|------|
"""
    
    for i, pain in enumerate(analysis['pain_points'][:10], 1):
        desc = pain['description'][:40] + '...' if len(pain['description']) > 40 else pain['description']
        report += f"| {i} | {desc} | {pain['category']} | {pain['severity']} | {pain['frequency']} |\n"
    
    report += f"""

---

## 📋 候选需求条目

| 序号 | 需求描述 | 类别 | 置信度 | 状态 |
|------|----------|------|--------|------|
"""
    
    for i, req in enumerate(analysis['candidate_requirements'][:10], 1):
        desc = req['description'][:40] + '...' if len(req['description']) > 40 else req['description']
        report += f"| {i} | {desc} | {req['category']} | {req['confidence']} | {req['status']} |\n"
    
    report += f"""

---

## ❓ 待澄清问题列表

| 优先级 | 问题 | 类型 | 上下文 |
|--------|------|------|--------|
"""
    
    for q in analysis['open_questions'][:8]:
        report += f"| {q['priority']} | {q['question']} | {q['type']} | {q['context'][:20]}... |\n"
    
    report += f"""

---

## 🔄 后续建议

### 移交需求管理智能体
- 候选需求条目已整理，建议进一步评估优先级
- 痛点清单可作为需求优先级参考

### 移交竞品分析智能体
- 客户对现有解决方案的不满点已识别
- 可作为竞品对标切入点

### 待办事项
1. 澄清高优先级待确认问题
2. 验证候选需求的准确性
3. 补充竞品对比信息

---
*此报告由客研管理智能体自动生成*
*生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}*
"""
    
    return report

def main():
    parser = argparse.ArgumentParser(description='客研管理智能体 - 访谈分析')
    parser.add_argument('--input', '-i', help='单次访谈记录文件')
    parser.add_argument('--input-dir', '-d', help='多次访谈记录目录')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    args = parser.parse_args()
    
    analyze_interview(args.input, args.input_dir, args.output)

if __name__ == '__main__':
    main()
