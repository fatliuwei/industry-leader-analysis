#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
申万行业龙头股分析 - 命令行工具
"""

import argparse
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from industry_analyzer import IndustryAnalyzer


def cmd_fetch(args):
    """获取行业数据"""
    print("=" * 80)
    print("获取行业数据")
    print("=" * 80)
    
    analyzer = IndustryAnalyzer(output_dir=args.output)
    
    # 获取行业分类
    l1_df, l2_df, l3_df = analyzer.get_industry_classification()
    
    # 保存数据
    timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d")
    
    l1_df.to_csv(os.path.join(args.output, f'申万一级行业_{timestamp}.csv'), 
                index=False, encoding='utf-8-sig')
    l2_df.to_csv(os.path.join(args.output, f'申万二级行业_{timestamp}.csv'), 
                index=False, encoding='utf-8-sig')
    l3_df.to_csv(os.path.join(args.output, f'申万三级行业_{timestamp}.csv'), 
                index=False, encoding='utf-8-sig')
    
    print(f"\n[OK] 行业数据已保存到: {args.output}")


def cmd_analyze(args):
    """分析龙头股"""
    print("=" * 80)
    print("分析行业龙头股")
    print("=" * 80)
    
    analyzer = IndustryAnalyzer(output_dir=args.output)
    
    # 分析所有行业
    result = analyzer.analyze_all_industries()
    
    # 保存结果
    files = analyzer.generate_report(result, args.output)
    
    print(f"\n[OK] 分析完成，结果已保存到: {args.output}")


def cmd_report(args):
    """生成分析报告"""
    print("=" * 80)
    print("生成分析报告")
    print("=" * 80)
    
    import pandas as pd
    from datetime import datetime
    
    # 读取最新的数据文件
    if args.input:
        input_file = args.input
    else:
        # 查找最新的数据文件
        import glob
        files = sorted(glob.glob('reports/申万行业龙头股分析_*.csv'), reverse=True)
        if not files:
            print("[ERROR] 未找到数据文件，请先运行 analyze 命令")
            return
        input_file = files[0]
    
    print(f"读取数据: {input_file}")
    df = pd.read_csv(input_file)
    
    # 生成报告
    analyzer = IndustryAnalyzer(output_dir=args.output)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if args.format in ['all', 'markdown']:
        md_file = os.path.join(args.output, f'行业分析报告_{timestamp}.md')
        analyzer._generate_markdown_report(df, md_file)
        print(f"[OK] Markdown报告: {md_file}")
    
    if args.format in ['all', 'summary']:
        summary_file = os.path.join(args.output, f'分析总结_{timestamp}.txt')
        _generate_summary(df, summary_file)
        print(f"[OK] 总结报告: {summary_file}")


def _generate_summary(df: 'pd.DataFrame', output_file: str):
    """生成总结报告"""
    from datetime import datetime
    
    total = len(df)
    has_data = len(df[df['数据来源'] != '无数据'])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("申万行业龙头股分析总结\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("数据统计:\n")
        f.write(f"  - 总行业数: {total}\n")
        f.write(f"  - 有龙头股数据: {has_data} ({has_data/total*100:.1f}%)\n\n")
        
        # L1级TOP 10
        f.write("市值TOP 10龙头股:\n")
        l1_df = df[df['行业级别'] == 'L1'].copy()
        l1_df['总市值(亿元)'] = pd.to_numeric(l1_df['总市值(亿元)'], errors='coerce')
        l1_top = l1_df.nlargest(10, '总市值(亿元)')
        
        for idx, row in l1_top.iterrows():
            mv = f"{row['总市值(亿元)']:.2f}" if pd.notna(row['总市值(亿元)']) else "-"
            f.write(f"  {row['行业名称']}: {row['龙头股名称']} ({mv}亿)\n")


def cmd_schedule(args):
    """创建定时任务"""
    print("=" * 80)
    print("创建定时任务")
    print("=" * 80)
    
    try:
        from codebuddy import automation_update
    except ImportError:
        print("[ERROR] 此功能需要在 CodeBuddy 环境中使用")
        return
    
    # 创建定时任务
    automation_update(
        mode="suggested create",
        name=args.name,
        prompt=args.prompt,
        scheduleType="recurring",
        rrule=args.schedule,
        cwds=[args.workdir],
        status="ACTIVE"
    )
    
    print(f"\n[OK] 定时任务已创建: {args.name}")


def main():
    parser = argparse.ArgumentParser(description='申万行业龙头股分析工具')
    subparsers = parser.add_subparsers(dest='mode', help='运行模式')
    
    # fetch 命令
    fetch_parser = subparsers.add_parser('fetch', help='获取行业数据')
    fetch_parser.add_argument('--output', '-o', default='industry_data', 
                             help='输出目录')
    fetch_parser.set_defaults(func=cmd_fetch)
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析龙头股')
    analyze_parser.add_argument('--output', '-o', default='reports', 
                               help='输出目录')
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # report 命令
    report_parser = subparsers.add_parser('report', help='生成报告')
    report_parser.add_argument('--input', '-i', help='输入数据文件')
    report_parser.add_argument('--output', '-o', default='reports', 
                              help='输出目录')
    report_parser.add_argument('--format', '-f', choices=['markdown', 'summary', 'all'],
                              default='all', help='报告格式')
    report_parser.set_defaults(func=cmd_report)
    
    # schedule 命令
    schedule_parser = subparsers.add_parser('schedule', help='创建定时任务')
    schedule_parser.add_argument('--name', required=True, help='任务名称')
    schedule_parser.add_argument('--schedule', required=True, 
                                help='定时规则（cron格式）')
    schedule_parser.add_argument('--prompt', required=True, help='任务提示')
    schedule_parser.add_argument('--workdir', default=os.getcwd(), help='工作目录')
    schedule_parser.set_defaults(func=cmd_schedule)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
