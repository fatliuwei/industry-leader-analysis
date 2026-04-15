# 快速开始：定时下载财务报表

本指南帮助你快速设置定时任务，自动下载上市公司财务报表PDF文件。

## 🎯 目标

- ✅ 自动下载财务报表PDF文件
- ✅ 支持按行业、股票代码批量下载
- ✅ 支持年报、半年报、季报
- ✅ 定时自动执行，无需人工干预

## 📋 前提条件

1. 已安装Python 3.7+
2. 已配置Tushare Token（如需按行业或公司名称下载）
3. 在Claude Code环境中（支持automation_update工具）

## 🚀 快速设置（5分钟）

### 步骤1: 测试下载功能

先手动测试一下下载功能：

```bash
# 下载贵州茅台最新年报
python skills/申万行业龙头股分析/src/financial_report_downloader.py \
  --stock 600519 \
  --report-type annual \
  --latest

# 查看下载结果
ls financial_reports/贵州茅台_600519/年报/
```

### 步骤2: 创建定时任务

在Claude Code中运行以下代码：

```python
from codebuddy import automation_update

# 创建季度财报下载任务
automation_update(
    mode="suggested create",
    name="季度财务报表自动下载",
    prompt="""
    执行季度财务报表下载任务：
    
    1. 切换到工作目录：d:/tonghuashun
    
    2. 下载银行业最新财报：
       python skills/申万行业龙头股分析/src/financial_report_downloader.py \\
         --industry 银行 \\
         --report-type all \\
         --latest \\
         --output financial_reports/banking/
    
    3. 下载电子行业最新财报：
       python skills/申万行业龙头股分析/src/financial_report_downloader.py \\
         --industry 电子 \\
         --report-type all \\
         --latest \\
         --output financial_reports/electronics/
    
    4. 统计下载结果
    
    完成后，财务报表将保存在 financial_reports/ 目录。
    """,
    scheduleType="recurring",
    rrule="FREQ=QUARTERLY;BYMONTH=1,4,7,10;BYMONTHDAY=15;BYHOUR=20;BYMINUTE=0",
    cwds=["d:/tonghuashun"],
    status="ACTIVE"
)
```

### 步骤3: 验证任务

```python
# 查看已创建的任务
automation_update(mode="view")
```

## 📊 使用示例

### 示例1: 下载特定股票的财报

```bash
# 下载茅台、五粮液、比亚迪的最新年报和半年报
python skills/申万行业龙头股分析/src/financial_report_downloader.py \
  --stock 600519 000858 002594 \
  --report-type annual semi \
  --latest
```

### 示例2: 下载整个行业的财报

```bash
# 下载银行业所有上市公司的最新年报
python skills/申万行业龙头股分析/src/financial_report_downloader.py \
  --industry 银行 \
  --report-type annual \
  --latest
```

### 示例3: 下载指定年份的财报

```bash
# 下载2023-2024年的年报
python skills/申万行业龙头股分析/src/financial_report_downloader.py \
  --stock 600519 \
  --report-type annual \
  --year 2023 2024
```

### 示例4: 下载所有类型的报告

```bash
# 下载年报、半年报、一季报、三季报
python skills/申万行业龙头股分析/src/financial_report_downloader.py \
  --stock 600519 \
  --report-type all \
  --latest
```

## ⏰ 定时任务配置

### 预设任务

| 任务名称 | 执行频率 | 说明 |
|---------|---------|------|
| 季度财报下载 | 每季度中旬 | 下载最新季度报告 |
| 年报集中下载 | 每年5月1日 | 批量下载上一年度年报 |
| 重点公司跟踪 | 每月20日 | 跟踪重点公司财报 |
| 龙头股自动下载 | 每周六 | 自动下载龙头股财报 |

详细配置见：`automation/financial_report_schedule.yaml`

### 自定义任务

#### 每月下载重点公司财报

```python
automation_update(
    mode="suggested create",
    name="重点公司财报月度下载",
    prompt="""
    下载重点公司最新财报：
    python skills/申万行业龙头股分析/src/financial_report_downloader.py \\
      --stock 600519 000858 000333 002594 300750 \\
      --report-type all \\
      --latest \\
      --output financial_reports/key_companies/
    """,
    scheduleType="recurring",
    rrule="FREQ=MONTHLY;BYMONTHDAY=20;BYHOUR=21;BYMINUTE=0",
    cwds=["d:/tonghuashun"],
    status="ACTIVE"
)
```

#### 每周下载龙头股财报

```python
automation_update(
    mode="suggested create",
    name="龙头股财报周度下载",
    prompt="""
    下载行业龙头股最新财报：
    
    1. 获取龙头股代码：
       python skills/申万行业龙头股分析/src/cli.py analyze
    
    2. 下载龙头股报告：
       python skills/申万行业龙头股分析/src/financial_report_downloader.py \\
         --stock [从步骤1获取的代码] \\
         --report-type annual semi \\
         --latest \\
         --output financial_reports/industry_leaders/
    """,
    scheduleType="recurring",
    rrule="FREQ=WEEKLY;BYDAY=SAT;BYHOUR=22;BYMINUTE=0",
    cwds=["d:/tonghuashun"],
    status="ACTIVE"
)
```

## 📁 输出结构

下载的财务报表将按以下结构保存：

```
financial_reports/
├── banking/                          # 银行业财报
│   ├── 工商银行_601398/
│   │   ├── 年报/
│   │   │   └── 工商银行_601398_20250410_2024年年度报告.pdf
│   │   ├── 半年报/
│   │   ├── 一季报/
│   │   └── 三季报/
│   ├── 招商银行_600036/
│   └── ...
├── electronics/                      # 电子行业财报
│   ├── 工业富联_601138/
│   ├── 立讯精密_002475/
│   └── ...
└── key_companies/                    # 重点公司财报
    ├── 贵州茅台_600519/
    ├── 五粮液_000858/
    └── ...
```

## 🔧 高级功能

### 1. 断点续传

已下载的文件会被自动跳过，不会重复下载：

```bash
# 第一次运行：下载10个文件
python skills/申万行业龙头股分析/src/financial_report_downloader.py \
  --stock 600519 --report-type annual

# 第二次运行：跳过已下载的10个文件
python skills/申万行业龙头股分析/src/financial_report_downloader.py \
  --stock 600519 --report-type annual
```

### 2. 自动重试

网络错误会自动重试（最多3次）。

### 3. 请求限速

默认请求间隔0.6秒，避免被巨潮资讯网封IP：

```bash
# 自定义请求间隔
python skills/申万行业龙头股分析/src/financial_report_downloader.py \
  --stock 600519 \
  --report-type annual \
  --delay 1.0
```

### 4. 按公司名称下载

支持按公司名称模糊匹配：

```bash
# 按公司名称下载
python skills/申万行业龙头股分析/src/financial_report_downloader.py \
  --stock 茅台 五粮液 比亚迪 \
  --report-type annual \
  --latest
```

## 📊 监控和日志

### 查看下载统计

每次下载完成后会输出统计信息：

```
==================================================
下载完成
  找到公告: 150 条
  新下载:   120 个
  跳过已有: 30 个
  失败:     0 个
  文件保存: /path/to/financial_reports/
==================================================
```

### 检查下载日志

```bash
# 查看最近的下载记录
tail -f logs/financial_report_downloader.log
```

## ⚠️ 注意事项

### 1. 数据源

- 财务报表来源于巨潮资讯网（证监会指定信息披露平台）
- 请求频率限制：建议间隔≥0.6秒
- 单次下载建议不超过100个公司

### 2. 存储空间

- 单个PDF文件：2-10MB
- 单个公司全部报告：约50-200MB
- 整个行业（如银行业）：约5-20GB
- 全市场年报：约100-300GB

### 3. 下载时间

建议在非高峰期执行大规模下载：
- 夜间（22:00-06:00）
- 周末
- 节假日

### 4. 网络要求

- 需要稳定的网络连接
- 建议使用国内网络
- 避免使用VPN

## 🐛 常见问题

### Q1: 提示"Permission denied"？

**原因**: 未配置Tushare Token

**解决**: 
```bash
export TUSHARE_TOKEN="your_token_here"
```

### Q2: 下载速度慢？

**原因**: 网络延迟或巨潮服务器响应慢

**解决**: 
- 增加请求间隔：`--delay 1.0`
- 在夜间下载
- 分批下载

### Q3: 部分文件下载失败？

**原因**: 网络不稳定或文件不存在

**解决**: 
- 重新运行下载命令（会自动跳过已下载文件）
- 检查网络连接
- 查看错误日志

### Q4: 如何下载历史年份的报告？

**解决**:
```bash
python skills/申万行业龙头股分析/src/financial_report_downloader.py \
  --stock 600519 \
  --report-type annual \
  --year 2020 2021 2022 2023
```

## 📚 更多资源

- [完整文档](README.md)
- [定时任务配置](automation/financial_report_schedule.yaml)
- [财务报表下载工具文档](src/financial_report_downloader.py)

## ✅ 检查清单

设置完成后，确认以下事项：

- [ ] 已测试手动下载功能
- [ ] 已创建定时任务
- [ ] 任务状态为ACTIVE
- [ ] 输出目录有写入权限
- [ ] 存储空间充足
- [ ] 网络连接稳定

## 🎉 完成！

恭喜！你已经成功设置了财务报表定时下载功能！

**现在系统会自动**:
- ✅ 定期下载最新财务报表
- ✅ 按行业和公司分类保存
- ✅ 跳过已下载的文件
- ✅ 生成下载统计报告

**下一步**:
1. 等待第一次定时执行
2. 检查下载的PDF文件
3. 根据需要调整下载策略

---

**需要帮助？**
- 查看文档: `README.md`
- 查看配置: `automation/financial_report_schedule.yaml`
- 提交问题: GitHub Issues
