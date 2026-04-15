# 快速开始：设置定时下载行业报表

本指南帮助你快速设置定时任务，自动下载和更新申万行业龙头股报表。

## 🎯 目标

- ✅ 创建定时任务，每天自动更新数据
- ✅ 生成行业龙头股分析报告
- ✅ 保存到指定目录

## 📋 前提条件

1. 已安装Python 3.7+
2. 已配置Tushare Token
3. 在Claude Code环境中（支持automation_update工具）

## 🚀 快速设置（5分钟）

### 步骤1: 安装依赖

```bash
pip install tushare pandas openpyxl
```

### 步骤2: 配置Token

```bash
# 设置环境变量
export TUSHARE_TOKEN="your_token_here"
```

### 步骤3: 创建定时任务

在Claude Code中运行以下Python代码：

```python
from codebuddy import automation_update

# 创建每日更新任务
automation_update(
    mode="suggested create",
    name="申万行业龙头股每日更新",
    prompt="""
    执行申万行业龙头股数据更新任务：
    
    1. 切换到工作目录：d:/tonghuashun
    2. 导入分析模块：
       import sys
       sys.path.append('skills/申万行业龙头股分析/src')
       from industry_analyzer import IndustryAnalyzer
    3. 创建分析器：
       analyzer = IndustryAnalyzer(output_dir='reports')
    4. 执行分析：
       result = analyzer.analyze_all_industries()
    5. 生成报告：
       files = analyzer.generate_report(result)
    6. 输出统计信息：
       total = len(result)
       has_data = len(result[result['数据来源'] != '无数据'])
       print(f"总行业数: {total}, 有龙头股数据: {has_data}")
    
    完成后，报告将保存在 reports/ 目录。
    """,
    scheduleType="recurring",
    rrule="FREQ=DAILY;BYHOUR=18;BYMINUTE=0",  # 每天18:00执行
    cwds=["d:/tonghuashun"],
    status="ACTIVE"
)
```

### 步骤4: 验证任务

```python
# 查看已创建的任务
automation_update(mode="view")
```

## 📊 任务执行流程

```
定时触发 (每天18:00)
    ↓
切换到工作目录
    ↓
导入分析模块
    ↓
获取行业分类数据 (511个行业)
    ↓
获取股票数据 (市值、ROE等)
    ↓
识别行业龙头股
    ↓
生成分析报告
    ├── CSV文件
    ├── Excel文件
    └── Markdown报告
    ↓
保存到 reports/ 目录
    ↓
发送通知 (可选)
```

## 🎨 自定义任务

### 每周深度分析

```python
automation_update(
    mode="suggested create",
    name="每周深度分析",
    prompt="""
    执行每周深度分析：
    1. 完整更新所有行业数据
    2. 对比上周数据变化
    3. 识别市值和ROE变化最大的行业
    4. 生成周度深度报告
    """,
    scheduleType="recurring",
    rrule="FREQ=WEEKLY;BYDAY=SUN;BYHOUR=20;BYMINUTE=0",
    cwds=["d:/tonghuashun"],
    status="ACTIVE"
)
```

### 月度财报更新

```python
automation_update(
    mode="suggested create",
    name="月度财报更新",
    prompt="""
    执行月度财报更新：
    1. 更新ROE、净利率等财务指标
    2. 对比上月数据
    3. 生成月度财务分析报告
    """,
    scheduleType="recurring",
    rrule="FREQ=MONTHLY;BYMONTHDAY=1;BYHOUR=9;BYMINUTE=0",
    cwds=["d:/tonghuashun"],
    status="ACTIVE"
)
```

### 自定义频率

```python
# 工作日每天执行
rrule="FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=17;BYMINUTE=0"

# 每周一、三、五执行
rrule="FREQ=WEEKLY;BYDAY=MO,WE,FR;BYHOUR=15;BYMINUTE=30"

# 每月1日和15日执行
rrule="FREQ=MONTHLY;BYMONTHDAY=1,15;BYHOUR=10;BYMINUTE=0"
```

## 📁 输出文件

每次任务执行后，会在 `reports/` 目录生成以下文件：

```
reports/
├── 申万行业龙头股分析_20260415_180000.csv
├── 申万行业龙头股分析_20260415_180000.xlsx
└── 行业分析报告_20260415_180000.md
```

### 文件说明

- **CSV文件**: 原始数据，可用于程序处理
- **Excel文件**: 格式化的数据，便于查看和分析
- **Markdown报告**: 包含统计摘要和TOP排行榜

## 🔍 查看执行结果

### 方法1: 查看日志

任务执行日志会保存在 `.codebuddy/automations/` 目录。

### 方法2: 查看输出文件

```bash
# 查看最新的报告
ls -lt reports/ | head

# 查看CSV数据
head -20 reports/申万行业龙头股分析_*.csv

# 查看Markdown报告
cat reports/行业分析报告_*.md
```

### 方法3: 数据分析

```python
import pandas as pd
import glob

# 读取最新数据
files = sorted(glob.glob('reports/申万行业龙头股分析_*.csv'), reverse=True)
df = pd.read_csv(files[0])

# 查看统计
print(f"总行业数: {len(df)}")
print(f"有龙头股数据: {len(df[df['数据来源'] != '无数据'])}")

# 查看TOP 10
l1_df = df[df['行业级别'] == 'L1']
l1_df['总市值(亿元)'] = pd.to_numeric(l1_df['总市值(亿元)'], errors='coerce')
print(l1_df.nlargest(10, '总市值(亿元)')[['行业名称', '龙头股名称', '总市值(亿元)']])
```

## ⚙️ 高级配置

### 1. 添加通知功能

在prompt中添加通知逻辑：

```python
prompt="""
执行数据更新任务...

完成后发送通知：
import requests
webhook_url = "your_webhook_url"
message = f"任务完成，总行业数: {len(result)}"
requests.post(webhook_url, json={"text": message})
"""
```

### 2. 数据验证

```python
prompt="""
执行数据更新任务...

验证数据完整性：
validation = analyzer.validate_data(result)
if not validation.is_valid:
    print("数据验证失败:", validation.errors)
    # 发送告警
"""
```

### 3. 历史数据对比

```python
prompt="""
执行数据更新任务...

对比历史数据：
import glob
files = sorted(glob.glob('reports/申万行业龙头股分析_*.csv'), reverse=True)
if len(files) > 1:
    old_data = pd.read_csv(files[1])
    new_data = pd.read_csv(files[0])
    # 对比逻辑...
"""
```

## 🐛 常见问题

### Q1: 任务没有按时执行？

**检查项**:
1. 确认任务状态为 `ACTIVE`
2. 检查rrule格式是否正确
3. 查看任务日志是否有错误

**解决方法**:
```python
# 重新创建任务
automation_update(
    mode="suggested create",
    name="申万行业龙头股每日更新",
    # ... 参数
    status="ACTIVE"
)
```

### Q2: API调用失败？

**可能原因**:
1. Tushare Token未配置
2. 网络连接问题
3. API限流

**解决方法**:
```bash
# 检查Token
echo $TUSHARE_TOKEN

# 测试连接
python -c "import tushare as ts; pro = ts.pro_api(); print(pro.trade_cal())"
```

### Q3: 数据不完整？

**原因**: 部分行业暂无成分股数据

**解决方法**:
```python
# 启用智能搜索补充
analyzer.enable_smart_search = True
```

## 📚 更多资源

- [完整文档](README.md)
- [集成指南](INTEGRATION_GUIDE.md)
- [定时任务配置](automation/schedule_examples.yaml)
- [使用示例](examples/basic_usage.py)

## ✅ 检查清单

设置完成后，确认以下事项：

- [ ] 已安装依赖包 (tushare, pandas, openpyxl)
- [ ] 已配置Tushare Token
- [ ] 已创建定时任务
- [ ] 任务状态为ACTIVE
- [ ] 输出目录存在且有写入权限
- [ ] 已测试手动执行一次

## 🎉 完成！

恭喜！你已经成功设置了定时任务。现在系统会自动：

- ✅ 每天更新行业数据
- ✅ 识别龙头股
- ✅ 生成分析报告
- ✅ 保存到指定目录

**下一步**:
1. 等待第一次定时执行
2. 查看生成的报告
3. 根据需要调整任务频率和内容

---

**需要帮助？**
- 查看文档: `README.md`
- 查看示例: `examples/basic_usage.py`
- 提交问题: GitHub Issues
