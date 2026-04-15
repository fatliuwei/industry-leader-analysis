#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
申万行业龙头股分析器 - 核心模块

支持功能：
1. 行业数据获取
2. 龙头股识别
3. 财务数据分析
4. 报告生成
5. 定时任务支持
"""

import tushare as ts
import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import time


class IndustryAnalyzer:
    """申万行业龙头股分析器"""
    
    def __init__(self, token: str = None, output_dir: str = 'reports'):
        """
        初始化分析器
        
        Args:
            token: Tushare API token（可选，默认从环境变量读取）
            output_dir: 输出目录
        """
        # 设置Tushare token
        if token:
            self.pro = ts.pro_api(token)
        else:
            self.pro = ts.pro_api()
        
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 配置参数
        self.enable_smart_search = False
        self.smart_search_industries = []
        self.custom_keywords = {}
        
        # 行业关键词映射
        self.INDUSTRY_KEYWORDS = {
            '食用菌': ['菌', '蘑菇', '雪榕', '众兴菌'],
            '宠物食品': ['宠物', '佩蒂', '中宠', '乖宝'],
            '钾肥': ['钾肥', '盐湖股份'],
            '氮肥': ['氮肥', '华鲁恒升', '鲁西化工'],
            '农药': ['农药', '扬农化工', '利尔化学', '红太阳'],
            '水产饲料': ['水产饲料', '海大集团', '天马科技'],
            '改性塑料': ['改性塑料', '金发科技', '普利特'],
        }
    
    def get_industry_classification(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        获取申万行业分类数据
        
        Returns:
            Tuple: (L1数据, L2数据, L3数据)
        """
        print("正在获取申万行业分类数据...")
        
        # 获取L1级行业
        l1_df = self.pro.index_classify(level='L1', src='SW2021')
        print(f"L1级行业: {len(l1_df)} 个")
        
        # 获取L2级行业
        l2_df = self.pro.index_classify(level='L2', src='SW2021')
        print(f"L2级行业: {len(l2_df)} 个")
        
        # 获取L3级行业
        l3_df = self.pro.index_classify(level='L3', src='SW2021')
        print(f"L3级行业: {len(l3_df)} 个")
        
        return l1_df, l2_df, l3_df
    
    def get_stock_data(self) -> pd.DataFrame:
        """
        获取所有股票的基础数据和财务数据
        
        Returns:
            DataFrame: 股票数据
        """
        print("正在获取股票数据...")
        
        # 获取所有上市股票
        stock_basic = self.pro.stock_basic(exchange='', list_status='L', 
                                          fields='ts_code,name,industry,list_date')
        print(f"上市股票数: {len(stock_basic)}")
        
        # 获取最近的市值数据
        print("正在获取市值数据...")
        mv_df = pd.DataFrame()
        
        for days_ago in range(0, 10):
            from datetime import timedelta
            check_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y%m%d')
            
            try:
                daily_basic = self.pro.daily_basic(
                    trade_date=check_date,
                    fields='ts_code,total_mv,circ_mv,pe,pb'
                )
                if not daily_basic.empty:
                    mv_df = daily_basic
                    print(f"成功获取 {check_date} 的市值数据: {len(mv_df)} 只股票")
                    break
            except:
                continue
        
        # 获取财务指标
        print("正在获取财务指标...")
        fina_df = pd.DataFrame()
        
        periods = ['20241231', '20240930', '20240630', '20240331']
        for period in periods:
            try:
                fina = self.pro.fina_indicator(
                    period=period,
                    fields='ts_code,ann_date,roe,roa,netprofit_margin,or_yoy,op_yoy'
                )
                if not fina.empty:
                    fina_df = fina
                    print(f"成功获取 {period} 的财务数据: {len(fina_df)} 只股票")
                    break
            except:
                continue
        
        # 合并数据
        stock_data = stock_basic.merge(mv_df, on='ts_code', how='left')
        stock_data = stock_data.merge(fina_df, on='ts_code', how='left')
        
        return stock_data
    
    def identify_leaders(self, industry_code: str, stock_data: pd.DataFrame) -> Optional[Dict]:
        """
        识别行业龙头股
        
        Args:
            industry_code: 行业代码
            stock_data: 股票数据
            
        Returns:
            Dict: 龙头股信息
        """
        try:
            # 获取行业成分股
            members = self.pro.index_member(index_code=industry_code)
            
            if members.empty:
                return None
            
            # 合并市值数据
            member_data = members.merge(stock_data, left_on='con_code', right_on='ts_code', how='left')
            
            # 筛选有市值数据的股票
            valid_data = member_data[member_data['total_mv'].notna()]
            
            if valid_data.empty:
                return None
            
            # 按市值排序，选择龙头股
            leader = valid_data.nlargest(1, 'total_mv').iloc[0]
            
            return {
                'code': leader['con_code'],
                'name': leader['name'],
                'total_mv': leader['total_mv'],
                'roe': leader.get('roe'),
                'netprofit_margin': leader.get('netprofit_margin'),
                'or_yoy': leader.get('or_yoy'),
                'source': '成分股数据'
            }
        except:
            return None
    
    def analyze_all_industries(self) -> pd.DataFrame:
        """
        分析所有行业
        
        Returns:
            DataFrame: 分析结果
        """
        print("\n" + "=" * 80)
        print("开始分析所有行业")
        print("=" * 80)
        
        # 获取行业分类
        l1_df, l2_df, l3_df = self.get_industry_classification()
        
        # 获取股票数据
        stock_data = self.get_stock_data()
        
        # 分析L1级行业
        results = []
        
        for level, level_df in [('L1', l1_df), ('L2', l2_df), ('L3', l3_df)]:
            print(f"\n正在分析 {level} 级行业...")
            
            for idx, row in level_df.iterrows():
                industry_code = row['index_code']
                industry_name = row['industry_name']
                
                leader_info = self.identify_leaders(industry_code, stock_data)
                
                if leader_info:
                    result = {
                        '行业代码': industry_code,
                        '行业名称': industry_name,
                        '行业级别': level,
                        '龙头股代码': leader_info['code'],
                        '龙头股名称': leader_info['name'],
                        '总市值(亿元)': leader_info['total_mv'] / 10000 if leader_info['total_mv'] else None,
                        'ROE(%)': leader_info['roe'],
                        '净利率(%)': leader_info['netprofit_margin'],
                        '数据来源': leader_info['source']
                    }
                    
                    # 生成推荐理由
                    reasons = []
                    if leader_info['total_mv']:
                        reasons.append(f"市值第一({leader_info['total_mv']/10000:.2f}亿)")
                    if leader_info['roe']:
                        reasons.append(f"ROE {leader_info['roe']:.2f}%")
                    if leader_info['netprofit_margin']:
                        reasons.append(f"净利率 {leader_info['netprofit_margin']:.2f}%")
                    if leader_info['or_yoy']:
                        reasons.append(f"营收增长 {leader_info['or_yoy']:.2f}%")
                    
                    result['推荐理由'] = '、'.join(reasons) if reasons else '市值第一'
                else:
                    result = {
                        '行业代码': industry_code,
                        '行业名称': industry_name,
                        '行业级别': level,
                        '龙头股代码': None,
                        '龙头股名称': None,
                        '总市值(亿元)': None,
                        'ROE(%)': None,
                        '净利率(%)': None,
                        '推荐理由': '暂无成分股数据',
                        '数据来源': '无数据'
                    }
                
                results.append(result)
        
        return pd.DataFrame(results)
    
    def generate_report(self, df: pd.DataFrame, output_dir: str = None) -> Dict[str, str]:
        """
        生成报告文件
        
        Args:
            df: 分析结果数据
            output_dir: 输出目录
            
        Returns:
            Dict: 生成的文件路径
        """
        if output_dir is None:
            output_dir = self.output_dir
        
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        files = {}
        
        # 生成CSV文件
        csv_file = os.path.join(output_dir, f'申万行业龙头股分析_{timestamp}.csv')
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        files['csv'] = csv_file
        print(f"[OK] CSV文件已保存: {csv_file}")
        
        # 生成Excel文件
        excel_file = os.path.join(output_dir, f'申万行业龙头股分析_{timestamp}.xlsx')
        df.to_excel(excel_file, index=False, engine='openpyxl')
        files['excel'] = excel_file
        print(f"[OK] Excel文件已保存: {excel_file}")
        
        # 生成Markdown报告
        md_file = os.path.join(output_dir, f'行业分析报告_{timestamp}.md')
        self._generate_markdown_report(df, md_file)
        files['markdown'] = md_file
        print(f"[OK] Markdown报告已保存: {md_file}")
        
        return files
    
    def _generate_markdown_report(self, df: pd.DataFrame, output_file: str):
        """生成Markdown格式的报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 申万行业龙头股分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # 数据统计
            f.write("## 数据统计\n\n")
            total = len(df)
            has_data = len(df[df['数据来源'] != '无数据'])
            f.write(f"- 总行业数: {total}\n")
            f.write(f"- 有龙头股数据: {has_data} ({has_data/total*100:.1f}%)\n\n")
            
            # TOP 10 市值龙头
            f.write("## 市值TOP 10龙头股\n\n")
            l1_df = df[df['行业级别'] == 'L1'].copy()
            l1_df['总市值(亿元)'] = pd.to_numeric(l1_df['总市值(亿元)'], errors='coerce')
            l1_top = l1_df.nlargest(10, '总市值(亿元)')
            
            f.write("| 排名 | 行业 | 龙头股 | 市值(亿元) |\n")
            f.write("|------|------|--------|------------|\n")
            for idx, row in l1_top.iterrows():
                rank = l1_top.index.get_loc(idx) + 1
                mv = f"{row['总市值(亿元)']:.2f}" if pd.notna(row['总市值(亿元)']) else "-"
                f.write(f"| {rank} | {row['行业名称']} | {row['龙头股名称']} | {mv} |\n")
    
    def get_leaders_by_level(self, level: str = 'L1', top_n: int = 10, 
                            sort_by: str = '市值') -> pd.DataFrame:
        """
        按行业级别获取龙头股
        
        Args:
            level: 行业级别 (L1/L2/L3)
            top_n: 返回数量
            sort_by: 排序字段 (市值/ROE/净利率)
            
        Returns:
            DataFrame: 龙头股数据
        """
        # 先执行分析
        df = self.analyze_all_industries()
        
        # 筛选指定级别
        level_df = df[df['行业级别'] == level].copy()
        
        # 排序
        if sort_by == '市值':
            level_df['总市值(亿元)'] = pd.to_numeric(level_df['总市值(亿元)'], errors='coerce')
            level_df = level_df.nlargest(top_n, '总市值(亿元)')
        elif sort_by == 'ROE':
            level_df['ROE(%)'] = pd.to_numeric(level_df['ROE(%)'], errors='coerce')
            level_df = level_df.nlargest(top_n, 'ROE(%)')
        
        return level_df
    
    def filter_industries(self, roe_min: float = None, mv_min: float = None) -> pd.DataFrame:
        """
        筛选行业
        
        Args:
            roe_min: ROE最小值
            mv_min: 市值最小值（亿元）
            
        Returns:
            DataFrame: 筛选结果
        """
        df = self.analyze_all_industries()
        
        # 转换数据类型
        df['ROE(%)'] = pd.to_numeric(df['ROE(%)'], errors='coerce')
        df['总市值(亿元)'] = pd.to_numeric(df['总市值(亿元)'], errors='coerce')
        
        # 筛选条件
        if roe_min:
            df = df[df['ROE(%)'] >= roe_min]
        
        if mv_min:
            df = df[df['总市值(亿元)'] >= mv_min]
        
        return df


def main():
    """主函数"""
    print("=" * 80)
    print("申万行业龙头股分析工具")
    print("=" * 80)
    
    # 创建分析器
    analyzer = IndustryAnalyzer(output_dir='reports')
    
    # 分析所有行业
    print("\n开始分析所有行业...")
    result = analyzer.analyze_all_industries()
    
    # 生成报告
    print("\n生成报告文件...")
    files = analyzer.generate_report(result)
    
    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)
    
    # 输出统计信息
    total = len(result)
    has_data = len(result[result['数据来源'] != '无数据'])
    print(f"\n总行业数: {total}")
    print(f"有龙头股数据: {has_data} ({has_data/total*100:.1f}%)")
    print(f"\n生成的文件:")
    for file_type, file_path in files.items():
        print(f"  - {file_type}: {file_path}")


if __name__ == '__main__':
    main()
