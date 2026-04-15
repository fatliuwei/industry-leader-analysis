# 申万行业龙头股分析 Skill

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/fatliuwei/industry-leader-analysis)
[![Python](https://img.shields.io/badge/python-3.7+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

一个专业的申万行业龙头股分析 + 财务报表自动下载工具，支持定时任务自动执行。

## 核心特性

- 511个申万行业龙头股分析（L1/L2/L3级，78.3%覆盖率）
- 财务报表PDF自动下载（年报/半年报/季报，来自巨潮资讯网）
- 定时任务支持（每日/每周/每月自动更新和下载）
- 多格式输出（CSV/Excel/Markdown）
- 兼容 openclaw / opencode / claude code

---

## 快速开始

### 1. 安装依赖

```bash
pip install tushare pandas openpyxl requests
```

### 2. 配置Token

```bash
# 行业分析需要Tushare Token
export TUSHARE_TOKEN="your_token_here"

# 财务报表下载不需要Token（直接从巨潮资讯网获取）
```

### 3. 使用

```bash
# 分析行业龙头股
python src/cli.py analyze --output reports/

# 下载贵州茅台最新年报
python src/financial_report_downloader.py --stock 600519 --report-type annual --latest

# 下载银行业所有公司最新年报
python src/financial_report_downloader.py --industry 银行 --report-type annual --latest
```

---

## 功能一：行业数据获取

获取申万2021分类体系的行业列表。

```bash
# 命令行
python src/cli.py fetch --output industry_data/
```

```python
# Python API
from src.industry_analyzer import IndustryAnalyzer
analyzer = IndustryAnalyzer()
l1_df, l2_df, l3_df = analyzer.get_industry_classification()
```

输出：`industry_data/申万一级行业_*.csv` 等3个文件。

---

## 功能二：龙头股分析

识别511个申万行业的龙头股，获取市值、ROE、净利率等指标。

```bash
# 命令行 - 完整分析
python src/cli.py analyze --output reports/
```

```python
# Python API
from src.industry_analyzer import IndustryAnalyzer

analyzer = IndustryAnalyzer(output_dir='reports')

# 完整分析
result = analyzer.analyze_all_industries()

# L1级市值TOP 10
l1_top = analyzer.get_leaders_by_level(level='L1', top_n=10, sort_by='市值')

# ROE>30%的行业
high_roe = analyzer.filter_industries(roe_min=30.0)

# 生成报告
files = analyzer.generate_report(result)
```

输出：`reports/申万行业龙头股分析_*.csv`、`*.xlsx`、`*.md`

---

## 功能三：财务报表PDF下载

从巨潮资讯网（证监会指定信息披露平台）下载财务报表PDF。

### 按股票代码下载

```bash
# 单只股票最新年报
python src/financial_report_downloader.py --stock 600519 --report-type annual --latest

# 多只股票年报+半年报
python src/financial_report_downloader.py --stock 600519 000858 --report-type annual semi --latest

# 指定年份
python src/financial_report_downloader.py --stock 600519 --report-type annual --year 2024 2025

# 所有类型（年报+半年报+一季报+三季报）
python src/financial_report_downloader.py --stock 600519 --report-type all --latest
```

### 按行业批量下载

```bash
# 银行业所有公司最新年报
python src/financial_report_downloader.py --industry 银行 --report-type annual --latest

# 电子行业所有类型报告
python src/financial_report_downloader.py --industry 电子 --report-type all --latest
```

### Python API

```python
from src.financial_report_downloader import CNINFOClient, download_reports, resolve_stock_codes

client = CNINFOClient()
stocks = resolve_stock_codes(stock_args=["600519"], industry_arg=None)
result = download_reports(
    client=client, stocks=stocks,
    report_types=["annual"], year_range=("2025", "2025"),
    output_dir="financial_reports/"
)
```

### 参数说明

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `--stock` | 二选一 | 6位股票代码或公司名称 | `600519` |
| `--industry` | 二选一 | 申万一级行业名称 | `银行` |
| `--report-type` | 否 | annual/semi/q1/q3/all | 默认`annual` |
| `--year` | 否 | 年份范围 | `2024 2025` |
| `--latest` | 否 | 只下载最近一年 | 无需值 |
| `--output` | 否 | 输出目录 | 默认`financial_reports/` |

---

## 功能四：报告生成

```bash
# 生成所有格式报告
python src/cli.py report --output reports/

# 只生成Markdown
python src/cli.py report --format markdown

# 只生成总结
python src/cli.py report --format summary
```

---

## 功能五：定时任务

### 在Claude Code中创建

```python
# 每日行业数据更新
automation_update(
    mode="suggested create",
    name="行业龙头股每日更新",
    prompt="运行 python src/cli.py analyze --output reports/ 更新行业龙头股数据",
    scheduleType="recurring",
    rrule="FREQ=DAILY;BYHOUR=18;BYMINUTE=0",
    cwds=["d:/tonghuashun/skills/申万行业龙头股分析"],
    status="ACTIVE"
)

# 每周六下载龙头股财报
automation_update(
    mode="suggested create",
    name="龙头股财报周下载",
    prompt="运行 python src/financial_report_downloader.py --stock 600519 000858 --report-type all --latest --output financial_reports/leaders/",
    scheduleType="recurring",
    rrule="FREQ=WEEKLY;BYDAY=SAT;BYHOUR=22;BYMINUTE=0",
    cwds=["d:/tonghuashun/skills/申万行业龙头股分析"],
    status="ACTIVE"
)

# 一次性任务
automation_update(
    mode="suggested create",
    name="2025年报批量下载",
    prompt="运行 python src/financial_report_downloader.py --industry 银行 --report-type annual --year 2025",
    scheduleType="once",
    scheduledAt="2026-05-15T02:00",
    cwds=["d:/tonghuashun/skills/申万行业龙头股分析"],
    status="ACTIVE"
)
```

### 预设模板

| 模板 | rrule | 用途 |
|------|-------|------|
| 每日更新 | `FREQ=DAILY;BYHOUR=18;BYMINUTE=0` | 市值数据更新 |
| 工作日日报 | `FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=17;BYMINUTE=0` | 每日简要报告 |
| 每周深度 | `FREQ=WEEKLY;BYDAY=SUN;BYHOUR=20;BYMINUTE=0` | 深度分析报告 |
| 每月更新 | `FREQ=MONTHLY;BYMONTHDAY=1;BYHOUR=9;BYMINUTE=0` | 财务指标更新 |
| 季度下载 | `FREQ=MONTHLY;BYMONTH=1,4,7,10;BYMONTHDAY=15;BYHOUR=20;BYMINUTE=0` | 行业财报下载 |
| 年报集中 | `FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=1;BYHOUR=9;BYMINUTE=0` | 年度报表下载 |

详细配置见 `automation/schedule_examples.yaml` 和 `automation/financial_report_schedule.yaml`。

---

## 数据字段

| 字段 | 说明 |
|------|------|
| 行业代码 | 申万行业指数代码 |
| 行业名称 | 申万行业名称 |
| 行业级别 | L1/L2/L3 |
| 龙头股代码 | 龙头股股票代码 |
| 龙头股名称 | 龙头股名称 |
| 总市值(亿元) | 最新总市值 |
| ROE(%) | 净资产收益率 |
| 净利率(%) | 净利率 |
| 推荐理由 | 推荐依据 |
| 数据来源 | 成分股数据/关键词匹配/智能搜索 |

## 数据覆盖率

| 级别 | 总数 | 覆盖数 | 覆盖率 |
|------|------|--------|--------|
| L1 | 31 | 31 | 100.0% |
| L2 | 134 | 130 | 97.0% |
| L3 | 346 | 239 | 69.1% |
| **总计** | **511** | **400** | **78.3%** |

---

## 项目结构

```
申万行业龙头股分析/
├── skill.md                              # Skill主文档（触发词+功能说明）
├── README.md                             # 本文件
├── QUICKSTART.md                         # 快速开始（行业分析）
├── QUICKSTART_FINANCIAL_REPORTS.md       # 快速开始（财务报表下载）
├── INTEGRATION_GUIDE.md                  # 集成指南
├── requirements.txt                      # 依赖文件
├── LICENSE                               # MIT许可证
├── src/
│   ├── industry_analyzer.py              # 行业分析核心模块
│   ├── cli.py                            # 命令行工具
│   └── financial_report_downloader.py    # 财务报表下载工具
├── examples/
│   └── basic_usage.py                    # 使用示例
└── automation/
    ├── schedule_examples.yaml            # 行业分析定时任务配置
    └── financial_report_schedule.yaml    # 财务报表下载定时任务配置
```

---

## 环境要求

| 依赖 | 版本 | 用途 |
|------|------|------|
| tushare | >=1.2.0 | 行业分类、股票数据 |
| pandas | >=1.3.0 | 数据处理 |
| openpyxl | >=3.0.0 | Excel输出 |
| requests | >=2.25.0 | 财务报表下载 |

## Token权限

| 功能 | 最低权限 | 积分 |
|------|---------|------|
| 申万行业分类 | 免费 | 0 |
| 股票基础数据 | 免费 | 0 |
| 市值/财务数据 | 基础 | 2000+ |
| 财务报表下载 | 不需要Token | 0 |

---

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| Tushare权限不足 | 捐赠升级积分 |
| 网络代理错误 | 关闭VPN或配置白名单 |
| 巨潮下载失败 | 自动重试3次，检查网络 |
| 财报搜索为空 | 确认6位股票代码 |

---

## 许可证

MIT License

## 链接

- **GitHub**: https://github.com/fatliuwei/industry-leader-analysis
- **Tushare**: https://tushare.pro/
- **巨潮资讯网**: http://www.cninfo.com.cn/

---

**版本**: v1.1.0 | **更新**: 2026-04-15 | **支持**: openclaw, opencode, claude code
