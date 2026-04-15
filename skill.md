# 申万行业龙头股分析 Skill

## 简介

这是一个用于获取和分析申万行业分类及其龙头股的专业工具。支持自动化获取511个申万行业（L1/L2/L3级）的龙头股数据，包括市值、ROE、净利率等关键财务指标，并生成详细的分析报告。

## 功能特性

### 核心功能
- ✅ **行业数据获取**: 自动获取申万2021分类体系（31个L1级、134个L2级、346个L3级行业）
- ✅ **龙头股识别**: 通过市值、ROE等指标识别行业龙头股
- ✅ **财务数据分析**: 获取总市值、ROE、净利率、营收增长等关键指标
- ✅ **智能补充机制**: 三层数据补充（成分股数据 → 关键词匹配 → 智能搜索）
- ✅ **分析报告生成**: 自动生成CSV、Excel和Markdown格式报告
- ✅ **定时任务支持**: 支持配置定时更新数据

### 数据覆盖率
- **L1级行业**: 100% (31/31)
- **L2级行业**: 97% (130/134)
- **L3级行业**: 69% (239/346)
- **总体覆盖率**: 78.3% (400/511)

## 安装要求

### 依赖项
```bash
pip install tushare
pip install pandas
pip install openpyxl
```

### Tushare权限
- 基础功能: 免费账户即可使用
- 高级功能: 建议积分≥2000（捐赠升级）
- 同花顺数据: 需要6000积分

## 快速开始

### 1. 基础使用

```python
from src.industry_analyzer import IndustryAnalyzer

# 初始化分析器
analyzer = IndustryAnalyzer()

# 获取所有行业龙头股数据
result = analyzer.analyze_all_industries()

# 生成报告
analyzer.generate_report(result, output_dir='reports/')
```

### 2. 定时任务配置

创建定时任务，每天/每周自动更新数据：

```yaml
# automation/schedule.yaml
name: 行业龙头股数据更新
schedule: "0 18 * * *"  # 每天18:00执行
prompt: |
  更新申万行业龙头股数据
  1. 获取最新的行业分类和成分股数据
  2. 更新龙头股市值和财务指标
  3. 生成分析报告并保存到 reports/ 目录
cwds: ["d:/tonghuashun"]
```

### 3. 命令行使用

```bash
# 获取行业数据
python src/cli.py --mode fetch --output industry_data/

# 分析龙头股
python src/cli.py --mode analyze --input industry_data/ --output reports/

# 生成报告
python src/cli.py --mode report --input reports/ --format all
```

## 使用场景

### 场景1: 行业配置策略
筛选大市值行业龙头，用于宏观行业配置决策。

```python
# 获取L1级行业龙头（市值TOP 10）
l1_leaders = analyzer.get_leaders_by_level('L1', top_n=10, sort_by='市值')
```

### 场景2: ROE选股策略
寻找高ROE行业，挖掘盈利能力强的赛道。

```python
# 筛选ROE>30%的行业
high_roe = analyzer.filter_industries(roe_min=30.0)
```

### 场景3: 定期数据更新
配置定时任务，定期更新数据。

```python
# 使用automation_update工具创建定时任务
from codebuddy import automation_update

automation_update(
    mode="suggested create",
    name="行业龙头股数据更新",
    prompt="更新申万行业龙头股数据并生成报告",
    scheduleType="recurring",
    rrule="FREQ=WEEKLY;BYDAY=MO;BYHOUR=18;BYMINUTE=0",
    cwds=["d:/tonghuashun"],
    status="ACTIVE"
)
```

## 输出文件

### 数据文件
- `申万行业龙头股分析_YYYYMMDD_HHMMSS.csv` - CSV格式数据
- `申万行业龙头股分析_YYYYMMDD_HHMMSS.xlsx` - Excel格式数据

### 分析报告
- `行业龙头股深度分析报告_YYYYMMDD_HHMMSS.md` - 详细分析报告
- `分析总结_YYYYMMDD_HHMMSS.txt` - 核心发现总结

### 基础数据
- `申万一级行业_YYYYMMDD.csv` - 31个一级行业列表
- `申万二级行业_YYYYMMDD.csv` - 134个二级行业列表
- `申万三级行业_YYYYMMDD.csv` - 346个三级行业列表

## 数据字段说明

| 字段名 | 类型 | 说明 |
|-------|------|------|
| 行业代码 | string | 申万行业指数代码 |
| 行业名称 | string | 申万行业名称 |
| 行业级别 | string | L1/L2/L3 |
| 龙头股代码 | string | 龙头股股票代码 |
| 龙头股名称 | string | 龙头股名称 |
| 总市值(亿元) | float | 最新总市值 |
| ROE(%) | float | 净资产收益率 |
| 净利率(%) | float | 净利率 |
| 推荐理由 | string | 推荐依据 |
| 数据来源 | string | 成分股数据/关键词匹配/智能搜索 |

## 高级功能

### 1. 智能搜索补充
对于API数据缺失的新兴行业，通过智能搜索补充龙头股。

```python
analyzer.enable_smart_search = True
analyzer.smart_search_industries = ['医疗美容', '旅游零售', '社交']
```

### 2. 自定义关键词匹配
添加自定义行业关键词映射。

```python
analyzer.add_custom_keywords({
    '新兴行业': ['关键词1', '关键词2']
})
```

### 3. 数据验证
自动验证数据的准确性和完整性。

```python
validation_result = analyzer.validate_data(result)
print(validation_result.summary())
```

## 定时任务示例

### 每日更新
```yaml
name: 每日行业数据更新
schedule: "FREQ=DAILY;BYHOUR=18;BYMINUTE=0"
prompt: |
  执行每日行业龙头股数据更新任务：
  1. 获取最新市值数据
  2. 更新财务指标
  3. 生成当日报告
```

### 每周深度分析
```yaml
name: 每周深度分析
schedule: "FREQ=WEEKLY;BYDAY=SUN;BYHOUR=20;BYMINUTE=0"
prompt: |
  执行每周深度分析任务：
  1. 完整更新所有行业数据
  2. 进行行业对比分析
  3. 生成周度分析报告
  4. 发送报告摘要
```

### 月度财报更新
```yaml
name: 月度财报数据更新
schedule: "FREQ=MONTHLY;BYMONTHDAY=1;BYHOUR=9;BYMINUTE=0"
prompt: |
  执行月度财报更新任务：
  1. 获取最新季报数据
  2. 更新ROE、净利率等指标
  3. 对比上月数据变化
  4. 生成月度报告
```

## 注意事项

1. **API限制**: Tushare有调用频率限制，建议使用定时任务错峰更新
2. **数据时效**: 市值数据每日变化，建议日度更新；财务指标季度更新即可
3. **数据验证**: L3级行业覆盖率较低，使用时需谨慎
4. **存储空间**: 每次运行会生成多个文件，建议定期清理历史文件

## 故障排查

### 问题1: Tushare权限不足
```
解决方案: 
1. 捐赠升级积分（推荐）
2. 使用免费的申万行业数据
3. 等待积分累计
```

### 问题2: 网络代理错误
```
解决方案:
1. 检查代理设置
2. 禁用VPN重试
3. 使用国内网络环境
```

### 问题3: 数据缺失
```
解决方案:
1. 启用智能搜索补充
2. 添加自定义关键词
3. 手动补充数据
```

## 更新日志

### v1.0.0 (2026-04-11)
- 初始版本发布
- 支持申万行业分类数据获取
- 实现三层数据补充机制
- 支持定时任务配置

## 技术支持

- GitHub Issues: [项目地址]
- 文档: `docs/使用指南.md`
- 示例: `examples/`

## 许可证

MIT License

## 作者

AI Assistant

---

**最后更新**: 2026-04-15
**版本**: v1.0.0
