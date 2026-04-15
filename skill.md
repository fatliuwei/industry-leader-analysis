# 申万行业龙头股分析 Skill

## 触发词

当用户提到以下关键词时激活本技能：
- 行业龙头、龙头股、行业分析、申万行业、行业分类
- 财务报表、财报下载、年报下载、季报下载
- 行业数据获取、行业轮动、ROE筛选
- 定时下载报表、自动下载财报

---

## 功能概览

| 功能 | 触发方式 | 核心命令 |
|------|---------|---------|
| 行业分类获取 | 对话/CLI/API | `python src/cli.py fetch` |
| 龙头股分析 | 对话/CLI/API | `python src/cli.py analyze` |
| 报告生成 | 对话/CLI | `python src/cli.py report` |
| 财务报表PDF下载 | 对话/CLI | `python src/financial_report_downloader.py` |
| 定时任务 | 对话/automation | `automation_update` 工具 |

---

## 功能1: 行业数据获取

### 说明
获取申万2021分类体系的行业列表（L1/L2/L3级）。

### 使用方式

#### 方式A: 对话触发（AI自动执行）
```
用户: "获取申万行业分类数据"
用户: "帮我获取最新的行业列表"
```
AI将自动运行 `python src/cli.py fetch --output industry_data/`

#### 方式B: 命令行
```bash
# 获取行业数据，保存到指定目录
python src/cli.py fetch --output industry_data/

# 等同于
python src/cli.py fetch -o industry_data/
```

#### 方式C: Python API
```python
from src.industry_analyzer import IndustryAnalyzer

analyzer = IndustryAnalyzer()
l1_df, l2_df, l3_df = analyzer.get_industry_classification()
```

### 输出
```
industry_data/
├── 申万一级行业_20260415.csv   # 31个一级行业
├── 申万二级行业_20260415.csv   # 134个二级行业
└── 申万三级行业_20260415.csv   # 346个三级行业
```

---

## 功能2: 龙头股分析

### 说明
识别511个申万行业的龙头股，获取市值、ROE、净利率等关键指标。

### 使用方式

#### 方式A: 对话触发
```
用户: "分析行业龙头股"
用户: "帮我找出各行业龙头"
用户: "ROE最高的行业龙头有哪些"
```

#### 方式B: 命令行
```bash
# 完整分析所有行业，生成报告
python src/cli.py analyze --output reports/

# 等同于
python src/cli.py analyze -o reports/
```

#### 方式C: Python API
```python
from src.industry_analyzer import IndustryAnalyzer

analyzer = IndustryAnalyzer(output_dir='reports')

# 完整分析
result = analyzer.analyze_all_industries()

# 按级别获取TOP N
l1_top10 = analyzer.get_leaders_by_level(level='L1', top_n=10, sort_by='市值')

# 按ROE筛选
high_roe = analyzer.filter_industries(roe_min=30.0)

# 生成报告
files = analyzer.generate_report(result)
```

### 输出
```
reports/
├── 申万行业龙头股分析_20260415_180000.csv    # CSV数据
├── 申万行业龙头股分析_20260415_180000.xlsx    # Excel数据
└── 行业分析报告_20260415_180000.md            # Markdown报告
```

### 数据字段

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

---

## 功能3: 报告生成

### 说明
基于已有数据生成Markdown或纯文本分析报告。

### 使用方式

#### 方式A: 对话触发
```
用户: "生成分析报告"
用户: "帮我生成行业分析报告"
```

#### 方式B: 命令行
```bash
# 生成所有格式报告
python src/cli.py report --output reports/

# 只生成Markdown报告
python src/cli.py report --format markdown

# 只生成总结
python src/cli.py report --format summary

# 指定输入数据文件
python src/cli.py report --input reports/申万行业龙头股分析_20260415.csv
```

---

## 功能4: 财务报表PDF下载

### 说明
从巨潮资讯网（证监会指定信息披露平台）下载上市公司财务报表PDF文件。

### 使用方式

#### 方式A: 对话触发
```
用户: "下载贵州茅台的年报"
用户: "帮我下载银行业所有公司的财报"
用户: "下载龙头股的最新季度报告"
用户: "定时下载财务报表"
```

#### 方式B: 命令行（最常用）
```bash
# ============ 按股票代码下载 ============

# 下载单只股票最新年报
python src/financial_report_downloader.py --stock 600519 --report-type annual --latest

# 下载多只股票最新年报+半年报
python src/financial_report_downloader.py --stock 600519 000858 --report-type annual semi --latest

# 下载指定年份的报告
python src/financial_report_downloader.py --stock 600519 --report-type annual --year 2024 2025

# 下载所有类型报告（年报+半年报+一季报+三季报）
python src/financial_report_downloader.py --stock 600519 --report-type all --latest

# 指定输出目录
python src/financial_report_downloader.py --stock 600519 --report-type annual --latest --output ./my_reports


# ============ 按申万行业批量下载 ============

# 下载银行业所有公司最新年报
python src/financial_report_downloader.py --industry 银行 --report-type annual --latest

# 下载电子行业所有类型报告
python src/financial_report_downloader.py --industry 电子 --report-type all --latest

# 下载医药生物行业2024年年报
python src/financial_report_downloader.py --industry 医药生物 --report-type annual --year 2024


# ============ 按公司名称下载（需TUSHARE_TOKEN） ============

# 通过公司名称下载（需要配置TUSHARE_TOKEN环境变量）
python src/financial_report_downloader.py --stock 贵州茅台 --report-type annual --latest
```

#### 方式C: Python API
```python
from src.financial_report_downloader import CNINFOClient, download_reports, resolve_stock_codes

# 初始化客户端
client = CNINFOClient()

# 解析股票
stocks = resolve_stock_codes(stock_args=["600519"], industry_arg=None)

# 执行下载
result = download_reports(
    client=client,
    stocks=stocks,
    report_types=["annual"],
    year_range=("2025", "2025"),
    output_dir="financial_reports/"
)

print(f"下载: {result.downloaded}, 跳过: {result.skipped}, 失败: {result.failed}")
```

### 参数说明

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `--stock` | 二选一 | 股票代码（6位）或公司名称 | `600519` 或 `贵州茅台` |
| `--industry` | 二选一 | 申万一级行业名称 | `银行` `电子` `医药生物` |
| `--report-type` | 否 | 报告类型，默认annual | `annual` `semi` `q1` `q3` `all` |
| `--year` | 否 | 年份范围 | `2025` 或 `2023 2025` |
| `--latest` | 否 | 只下载最近一年 | 无需值 |
| `--output` | 否 | 输出目录 | `./my_reports` |
| `--delay` | 否 | 请求间隔秒数 | `1.0` |

### 报告类型对照

| 参数值 | 说明 | 巨潮分类代码 |
|--------|------|-------------|
| `annual` | 年度报告 | ndbg_szsh |
| `semi` | 半年度报告 | bdbg_szsh |
| `q1` | 第一季度报告 | jdbg_szsh |
| `q3` | 第三季度报告 | jdbg_szsh |
| `all` | 全部类型 | - |

### 输出目录结构
```
financial_reports/
├── 贵州茅台_600519/
│   ├── 年报/
│   │   └── 贵州茅台_600519_20260410_2025年年度报告.pdf
│   ├── 半年报/
│   ├── 一季报/
│   └── 三季报/
├── 五粮液_000858/
│   └── 年报/
└── banking/                    # 按行业下载时
    ├── 工商银行_601398/
    └── 招商银行_600036/
```

### 特性
- 断点续传：跳过已下载文件
- 自动重试：网络错误自动重试3次
- 请求限速：默认0.6秒间隔，避免被封IP

---

## 功能5: 定时任务

### 说明
配置定时任务，自动执行行业数据更新和财务报表下载。

### 使用方式

#### 方式A: 对话触发（CodeBuddy/Claude Code环境）
```
用户: "创建一个每天更新行业数据的定时任务"
用户: "设置每周六下载龙头股财报"
用户: "每月1号帮我下载银行业年报"
```
AI将调用 `automation_update` 工具创建任务。

#### 方式B: 使用automation_update工具
```python
# 创建每日行业数据更新任务
automation_update(
    mode="suggested create",
    name="行业龙头股每日更新",
    prompt="执行行业龙头股数据更新：运行 python src/cli.py analyze --output reports/",
    scheduleType="recurring",
    rrule="FREQ=DAILY;BYHOUR=18;BYMINUTE=0",
    cwds=["d:/tonghuashun/skills/申万行业龙头股分析"],
    status="ACTIVE"
)

# 创建每周六下载龙头股财报任务
automation_update(
    mode="suggested create",
    name="龙头股财报周下载",
    prompt="执行龙头股财报下载：python src/financial_report_downloader.py --stock 600519 000858 000333 --report-type all --latest --output financial_reports/leaders/",
    scheduleType="recurring",
    rrule="FREQ=WEEKLY;BYDAY=SAT;BYHOUR=22;BYMINUTE=0",
    cwds=["d:/tonghuashun/skills/申万行业龙头股分析"],
    status="ACTIVE"
)

# 创建一次性任务
automation_update(
    mode="suggested create",
    name="2025年报批量下载",
    prompt="下载所有申万一级行业2025年年报：python src/financial_report_downloader.py --industry 银行 --report-type annual --year 2025 --output financial_reports/annual_2025/banking/",
    scheduleType="once",
    scheduledAt="2026-05-15T02:00",
    cwds=["d:/tonghuashun/skills/申万行业龙头股分析"],
    status="ACTIVE"
)
```

### 预设定时任务模板

| 模板名称 | 执行频率 | rrule | 适用场景 |
|---------|---------|-------|---------|
| 每日更新 | 每天18:00 | `FREQ=DAILY;BYHOUR=18;BYMINUTE=0` | 市值数据更新 |
| 工作日日报 | 工作日17:00 | `FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=17;BYMINUTE=0` | 每日简要报告 |
| 每周深度分析 | 每周日20:00 | `FREQ=WEEKLY;BYDAY=SUN;BYHOUR=20;BYMINUTE=0` | 深度分析报告 |
| 每月财报更新 | 每月1日9:00 | `FREQ=MONTHLY;BYMONTHDAY=1;BYHOUR=9;BYMINUTE=0` | 财务指标更新 |
| 龙头股财报周下载 | 每周六22:00 | `FREQ=WEEKLY;BYDAY=SAT;BYHOUR=22;BYMINUTE=0` | 龙头股财报下载 |
| 季度财报下载 | 每季度中旬 | `FREQ=MONTHLY;BYMONTH=1,4,7,10;BYMONTHDAY=15;BYHOUR=20;BYMINUTE=0` | 行业财报下载 |
| 年报集中下载 | 每年5月1日 | `FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=1;BYHOUR=9;BYMINUTE=0` | 年度报表下载 |

---

## 环境要求

### 必需依赖
```bash
pip install tushare pandas openpyxl
```

### 财务报表下载额外依赖
```bash
pip install requests
```

### Tushare Token配置
```bash
# 方式1: 环境变量（推荐）
export TUSHARE_TOKEN="your_token_here"

# 方式2: 代码中设置
import tushare as ts
ts.set_token("your_token_here")
```

### Token权限说明
| 功能 | 最低权限 | 积分要求 |
|------|---------|---------|
| 申万行业分类 | 免费账户 | 0 |
| 股票基础数据 | 免费账户 | 0 |
| 市值数据 | 基础权限 | 120+ |
| 财务指标 | 基础权限 | 2000+ |
| 行业成分股 | 基础权限 | 2000+ |
| 财务报表下载 | 不需要Token | 0（直接从巨潮获取） |

---

## 使用场景速查

### 场景1: 行业配置策略
```
用户: "帮我分析一下哪些行业值得关注"
```
AI执行: `python src/cli.py analyze` → 筛选市值大、ROE高的行业

### 场景2: ROE选股
```
用户: "找出ROE超过30%的行业龙头"
```
AI执行: `analyzer.filter_industries(roe_min=30.0)`

### 场景3: 下载特定公司财报
```
用户: "下载贵州茅台2024年年报"
```
AI执行: `python src/financial_report_downloader.py --stock 600519 --report-type annual --year 2024`

### 场景4: 批量下载行业财报
```
用户: "下载银行业所有公司的最新年报"
```
AI执行: `python src/financial_report_downloader.py --industry 银行 --report-type annual --latest`

### 场景5: 配置定时自动下载
```
用户: "每周六自动下载龙头股财报"
```
AI执行: 调用 `automation_update` 创建定时任务

---

## 故障排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Tushare权限不足 | 积分不够 | 捐赠升级积分 |
| 网络代理错误 | VPN/代理干扰 | 关闭VPN或配置代理白名单 |
| 巨潮下载失败 | 网络不稳定 | 自动重试3次，检查网络 |
| 财报搜索为空 | 公司名/代码错误 | 确认6位股票代码 |
| 定时任务未执行 | rrule格式错误 | 参考上方模板 |

---

## 版本信息

- **版本**: v1.1.0
- **更新日期**: 2026-04-15
- **GitHub**: https://github.com/fatliuwei/industry-leader-analysis
