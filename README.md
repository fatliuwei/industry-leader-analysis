# 申万行业龙头股分析 Skill

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/your-repo/industry-leader-analysis)
[![Python](https://img.shields.io/badge/python-3.7+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

一个专业的申万行业龙头股分析工具，支持自动化获取、分析和定时更新行业数据。

## ✨ 核心特性

- 📊 **全面覆盖** - 511个申万行业（L1/L2/L3级），78.3%数据覆盖率
- 🔍 **智能识别** - 三层数据补充机制（成分股 → 关键词 → 智能搜索）
- 📈 **财务分析** - 市值、ROE、净利率、营收增长等关键指标
- 📑 **报表下载** - 自动下载上市公司财务报表PDF（年报/半年报/季报）
- 🤖 **定时任务** - 支持每日/每周/每月自动更新
- 📄 **多格式输出** - CSV、Excel、Markdown报告
- 🎯 **易于集成** - 可在openclaw、opencode、claude code中使用

## 📦 安装

### 1. 安装依赖

```bash
pip install tushare pandas openpyxl
```

### 2. 配置Tushare Token

```bash
# 方法1: 环境变量
export TUSHARE_TOKEN="your_token_here"

# 方法2: 代码中配置
from src.industry_analyzer import IndustryAnalyzer
analyzer = IndustryAnalyzer(token="your_token_here")
```

### 3. 安装Skill

将整个 `申万行业龙头股分析` 文件夹复制到你的skills目录：

```
your-project/
└── skills/
    └── 申万行业龙头股分析/
        ├── skill.md
        ├── src/
        ├── examples/
        └── automation/
```

## 🚀 快速开始

### 方法1: Python API

```python
from src.industry_analyzer import IndustryAnalyzer

# 创建分析器
analyzer = IndustryAnalyzer(output_dir='reports')

# 分析所有行业
result = analyzer.analyze_all_industries()

# 生成报告
analyzer.generate_report(result)
```

### 方法2: 命令行工具

```bash
# 获取行业数据
python src/cli.py fetch --output industry_data/

# 分析龙头股
python src/cli.py analyze --output reports/

# 生成报告
python src/cli.py report --input reports/latest.csv --format all
```

### 方法3: 定时任务

```python
from codebuddy import automation_update

# 创建每日更新任务
automation_update(
    mode="suggested create",
    name="行业龙头股每日更新",
    prompt="更新申万行业龙头股数据并生成报告",
    scheduleType="recurring",
    rrule="FREQ=DAILY;BYHOUR=18;BYMINUTE=0",
    cwds=["d:/tonghuashun"],
    status="ACTIVE"
)
```

## 📖 使用示例

### 示例1: 基础分析

```python
from src.industry_analyzer import IndustryAnalyzer

analyzer = IndustryAnalyzer()
result = analyzer.analyze_all_industries()

# 查看数据统计
print(f"总行业数: {len(result)}")
print(f"有龙头股数据: {len(result[result['数据来源'] != '无数据'])}")
```

### 示例2: 筛选L1级龙头

```python
# 获取L1级行业市值TOP 10
l1_top = analyzer.get_leaders_by_level(level='L1', top_n=10, sort_by='市值')
print(l1_top[['行业名称', '龙头股名称', '总市值(亿元)']])
```

### 示例3: 高ROE行业筛选

```python
# 筛选ROE>30%的行业
high_roe = analyzer.filter_industries(roe_min=30.0)
print(high_roe[['行业名称', '龙头股名称', 'ROE(%)', '净利率(%)']])
```

更多示例请查看 `examples/basic_usage.py`。

### 示例4: 财务报表下载 ⭐ NEW

下载上市公司财务报表PDF文件：

```bash
# 下载贵州茅台最新年报
python src/financial_report_downloader.py --stock 600519 --report-type annual --latest

# 下载银行业所有公司最新年报
python src/financial_report_downloader.py --industry 银行 --report-type annual --latest

# 下载特定股票的所有类型报告
python src/financial_report_downloader.py --stock 600519 000858 --report-type all --latest
```

详细文档：`QUICKSTART_FINANCIAL_REPORTS.md`

## 📊 数据说明

### 数据字段

| 字段 | 类型 | 说明 |
|------|------|------|
| 行业代码 | string | 申万行业指数代码 |
| 行业名称 | string | 申万行业名称 |
| 行业级别 | string | L1/L2/L3 |
| 龙头股代码 | string | 龙头股股票代码 |
| 龙头股名称 | string | 龙头股名称 |
| 总市值(亿元) | float | 最新总市值 |
| ROE(%) | float | 净资产收益率 |
| 净利率(%) | float | 净利率 |
| 推荐理由 | string | 推荐依据 |
| 数据来源 | string | 数据获取方式 |

### 数据覆盖率

| 级别 | 总数 | 覆盖数 | 覆盖率 |
|------|------|--------|--------|
| L1 | 31 | 31 | 100.0% |
| L2 | 134 | 130 | 97.0% |
| L3 | 346 | 239 | 69.1% |
| **总计** | **511** | **400** | **78.3%** |

## ⏰ 定时任务

### 预设任务

#### 行业龙头股分析

| 任务 | 频率 | 说明 |
|------|------|------|
| 每日更新 | 每天18:00 | 更新市值数据 |
| 每周分析 | 每周日20:00 | 深度分析报告 |
| 月度财报 | 每月1日9:00 | 更新财务指标 |
| 季度研究 | 季度中旬 | 投资策略报告 |

#### 财务报表下载 ⭐ NEW

| 任务 | 频率 | 说明 |
|------|------|------|
| 季度财报下载 | 每季度中旬 | 下载最新季度报告 |
| 年报集中下载 | 每年5月1日 | 批量下载上一年度年报 |
| 重点公司跟踪 | 每月20日 | 跟踪重点公司财报 |
| 龙头股自动下载 | 每周六 | 自动下载龙头股财报 |

财务报表下载详细配置：`automation/financial_report_schedule.yaml`

### 自定义任务

编辑 `automation/schedule_examples.yaml` 文件，自定义定时任务：

```yaml
自定义任务:
  name: 我的定时任务
  schedule: "FREQ=WEEKLY;BYDAY=MO;BYHOUR=10;BYMINUTE=0"
  prompt: |
    执行自定义分析任务
  cwds: ["d:/tonghuashun"]
  status: ACTIVE
```

## 🎯 应用场景

### 1. 行业配置策略

```python
# 获取大市值行业龙头
l1_leaders = analyzer.get_leaders_by_level('L1', top_n=20, sort_by='市值')
```

### 2. ROE选股策略

```python
# 筛选高ROE行业
high_roe = analyzer.filter_industries(roe_min=30.0, mv_min=100)
```

### 3. 产业链分析

```python
# 对比产业链上下游
result = analyzer.analyze_all_industries()
upstream = result[result['二级行业'] == '上游行业']
downstream = result[result['二级行业'] == '下游行业']
```

### 4. 定期数据更新

配置定时任务，自动更新数据和生成报告。

## 📁 项目结构

```
申万行业龙头股分析/
├── skill.md                    # Skill说明文档
├── README.md                   # 使用指南
├── src/                        # 源代码
│   ├── industry_analyzer.py    # 核心分析模块
│   └── cli.py                  # 命令行工具
├── examples/                   # 使用示例
│   └── basic_usage.py          # 基础示例
└── automation/                 # 定时任务
    └── schedule_examples.yaml  # 任务配置
```

## 🔧 高级功能

### 1. 智能搜索补充

```python
analyzer.enable_smart_search = True
analyzer.smart_search_industries = ['医疗美容', '旅游零售']
```

### 2. 自定义关键词

```python
analyzer.add_custom_keywords({
    '新行业': ['关键词1', '关键词2']
})
```

### 3. 数据验证

```python
validation = analyzer.validate_data(result)
print(validation.summary())
```

## ⚠️ 注意事项

1. **API限制** - Tushare有调用频率限制，建议使用定时任务错峰更新
2. **数据时效** - 市值数据每日变化，财务指标季度更新
3. **权限要求** - 基础功能免费，高级功能需积分≥2000
4. **存储管理** - 定期清理历史文件，避免占用过多空间

## 🐛 故障排查

### 问题1: Tushare权限不足

```
解决方案: 
1. 捐赠升级积分（推荐）
2. 使用免费功能
3. 申请学术权限
```

### 问题2: 网络代理错误

```
解决方案:
1. 检查代理设置
2. 禁用VPN重试
3. 使用国内网络
```

### 问题3: 数据缺失

```
解决方案:
1. 启用智能搜索
2. 添加自定义关键词
3. 手动补充数据
```

## 📚 文档

- [使用指南](docs/使用指南.md)
- [API文档](docs/API.md)
- [定时任务](docs/Automation.md)
- [常见问题](docs/FAQ.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 👥 作者

AI Assistant

## 🙏 致谢

- [Tushare](https://tushare.pro/) - 数据源
- [申万宏源](http://www.swsresearch.com/) - 行业分类标准

---

**最后更新**: 2026-04-15  
**版本**: v1.0.0  
**支持**: openclaw, opencode, claude code
