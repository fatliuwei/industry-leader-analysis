#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
申万行业龙头股分析 - 基础使用示例
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from industry_analyzer import IndustryAnalyzer


def example_1_basic_analysis():
    """
    示例1: 基础分析
    获取所有行业的龙头股数据
    """
    print("=" * 80)
    print("示例1: 基础分析")
    print("=" * 80)
    
    # 创建分析器
    analyzer = IndustryAnalyzer(output_dir='reports')
    
    # 分析所有行业
    result = analyzer.analyze_all_industries()
    
    # 生成报告
    files = analyzer.generate_report(result)
    
    print("\n分析完成！")
    print(f"总行业数: {len(result)}")
    print(f"有龙头股数据: {len(result[result['数据来源'] != '无数据'])}")


def example_2_filter_by_level():
    """
    示例2: 按行业级别筛选
    获取L1级行业的市值TOP 10龙头股
    """
    print("\n" + "=" * 80)
    print("示例2: L1级行业市值TOP 10")
    print("=" * 80)
    
    analyzer = IndustryAnalyzer(output_dir='reports')
    
    # 获取L1级市值TOP 10
    l1_top10 = analyzer.get_leaders_by_level(level='L1', top_n=10, sort_by='市值')
    
    print("\nL1级行业市值TOP 10:")
    print(l1_top10[['行业名称', '龙头股名称', '总市值(亿元)']].to_string(index=False))


def example_3_filter_by_roe():
    """
    示例3: 按ROE筛选
    筛选ROE>30%的高盈利行业
    """
    print("\n" + "=" * 80)
    print("示例3: 筛选ROE>30%的行业")
    print("=" * 80)
    
    analyzer = IndustryAnalyzer(output_dir='reports')
    
    # 筛选ROE>30%的行业
    high_roe = analyzer.filter_industries(roe_min=30.0)
    
    print(f"\nROE>30%的行业共 {len(high_roe)} 个:")
    print(high_roe[['行业名称', '龙头股名称', 'ROE(%)', '净利率(%)']].to_string(index=False))


def example_4_custom_analysis():
    """
    示例4: 自定义分析
    筛选特定条件的行业
    """
    print("\n" + "=" * 80)
    print("示例4: 自定义分析")
    print("=" * 80)
    
    analyzer = IndustryAnalyzer(output_dir='reports')
    
    # 分析所有行业
    result = analyzer.analyze_all_industries()
    
    # 自定义筛选：市值>1000亿 且 ROE>15%
    import pandas as pd
    result['总市值(亿元)'] = pd.to_numeric(result['总市值(亿元)'], errors='coerce')
    result['ROE(%)'] = pd.to_numeric(result['ROE(%)'], errors='coerce')
    
    filtered = result[
        (result['总市值(亿元)'] > 1000) & 
        (result['ROE(%)'] > 15)
    ]
    
    print(f"\n市值>1000亿且ROE>15%的行业共 {len(filtered)} 个:")
    print(filtered[['行业名称', '龙头股名称', '总市值(亿元)', 'ROE(%)']].to_string(index=False))


def example_5_industry_comparison():
    """
    示例5: 行业对比分析
    对比同一产业链上下游行业
    """
    print("\n" + "=" * 80)
    print("示例5: 行业对比分析")
    print("=" * 80)
    
    analyzer = IndustryAnalyzer(output_dir='reports')
    
    # 分析所有行业
    result = analyzer.analyze_all_industries()
    
    # 对比"电子"行业下的细分赛道
    electronics = result[result['一级行业'] == '电子']
    
    print("\n电子行业细分赛道对比:")
    print(electronics[['行业名称', '龙头股名称', '总市值(亿元)', 'ROE(%)']].to_string(index=False))


def main():
    """运行所有示例"""
    examples = [
        example_1_basic_analysis,
        example_2_filter_by_level,
        example_3_filter_by_roe,
        example_4_custom_analysis,
        example_5_industry_comparison,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n[ERROR] 示例执行失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("所有示例执行完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()
