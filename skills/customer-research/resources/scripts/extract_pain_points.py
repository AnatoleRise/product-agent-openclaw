#!/usr/bin/env python3
"""
客研管理智能体 - 痛点提取脚本
快速提取痛点清单
"""

import argparse
import re
from collections import Counter

def extract_pain_points(input_path, output_path=None):
    """
    提取痛点清单
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
    
    Returns:
        痛点列表
    """
    
    print(f"🔍 提取痛点：{input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取痛点
    patterns = [
        r'(?:痛点|困难|问题|挑战)(?:是|在于|有)?[：:]?\s*(.{5,60})',
        r'(?:不方便|不好用|不满意)(?:的是)?(.{5,60})',
        r'(?:耗时|费力|麻烦)(?:的是)?(.{5,60})',
        r'(?:缺乏|不足|不够)(.{5,60})'
    ]
    
    pain_points = []
    seen = set()
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            match = match.strip()
            if match not in seen and len(match) > 5:
                seen.add(match)
                pain_points.append({
                    "description": match,
                    "severity": "高" if any(kw in match for kw in ['核心', '关键', '严重']) else "中",
                    "category": classify_pain(match)
                })
    
    # 生成报告
    report = format_pain_report(pain_points)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ 痛点清单已生成：{output_path}")
    
    return pain_points

def classify_pain(text):
    """分类痛点"""
    if any(kw in text for kw in ['功能', '能力', '系统']):
        return "功能缺失"
    elif any(kw in text for kw in ['体验', '操作', '界面']):
        return "体验问题"
    elif any(kw in text for kw in ['性能', '速度', '响应']):
        return "性能问题"
    elif any(kw in text for kw in ['成本', '价格', '费用']):
        return "成本问题"
    else:
        return "其他"

def format_pain_report(pain_points):
    """格式化痛点报告"""
    
    report = "# ⚠️ 痛点清单\n\n"
    report += "| 序号 | 痛点描述 | 类别 | 严重程度 |\n"
    report += "|------|----------|------|----------|\n"
    
    for i, pain in enumerate(pain_points, 1):
        desc = pain['description'][:50] + '...' if len(pain['description']) > 50 else pain['description']
        report += f"| {i} | {desc} | {pain['category']} | {pain['severity']} |\n"
    
    report += f"\n**总计**：{len(pain_points)} 个痛点\n"
    
    return report

def main():
    parser = argparse.ArgumentParser(description='提取痛点清单')
    parser.add_argument('--input', '-i', required=True, help='输入文件路径')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    args = parser.parse_args()
    
    extract_pain_points(args.input, args.output)

if __name__ == '__main__':
    main()
