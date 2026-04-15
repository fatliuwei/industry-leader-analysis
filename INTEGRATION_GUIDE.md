# Skill集成指南

本文档说明如何在openclaw、opencode和claude code中集成和使用申万行业龙头股分析Skill。

## 📦 安装Skill

### 方法1: 手动安装

1. 将 `申万行业龙头股分析` 文件夹复制到项目的skills目录：

```bash
your-project/
└── skills/
    └── 申万行业龙头股分析/
        ├── skill.md
        ├── src/
        ├── examples/
        └── automation/
```

2. 安装依赖：

```bash
cd skills/申万行业龙头股分析
pip install -r requirements.txt
```

### 方法2: Git子模块

```bash
cd your-project
git submodule add https://github.com/your-repo/industry-leader-analysis skills/申万行业龙头股分析
```

## 🔧 环境配置

### 1. Tushare Token配置

**方法1: 环境变量（推荐）**

```bash
# Linux/Mac
export TUSHARE_TOKEN="your_token_here"

# Windows
set TUSHARE_TOKEN=your_token_here
```

**方法2: 配置文件**

创建 `config/tushare_config.py`:

```python
TUSHARE_TOKEN = "your_token_here"
```

**方法3: 代码中指定**

```python
from src.industry_analyzer import IndustryAnalyzer
analyzer = IndustryAnalyzer(token="your_token_here")
```

### 2. 输出目录配置

默认输出目录为 `reports/`，可在初始化时修改：

```python
analyzer = IndustryAnalyzer(output_dir='custom_reports/')
```

## 🤖 在不同环境中使用

### 在openclaw中使用

**基本用法:**

```python
# 在你的agent或workflow中导入
import sys
sys.path.append('skills/申万行业龙头股分析/src')

from industry_analyzer import IndustryAnalyzer

# 创建分析器
analyzer = IndustryAnalyzer(output_dir='reports')

# 执行分析
result = analyzer.analyze_all_industries()

# 生成报告
files = analyzer.generate_report(result)
```

**在Workflow中使用:**

```python
# workflow.py
from openclaw import Workflow
from skills.申万行业龙头股分析.src.industry_analyzer import IndustryAnalyzer

class IndustryAnalysisWorkflow(Workflow):
    def run(self):
        analyzer = IndustryAnalyzer()
        result = analyzer.analyze_all_industries()
        return analyzer.generate_report(result)
```

**在Agent中使用:**

```python
# agent.py
from openclaw import Agent, Tool
from skills.申万行业龙头股分析.src.industry_analyzer import IndustryAnalyzer

class IndustryAnalysisTool(Tool):
    name = "industry_analysis"
    description = "分析申万行业龙头股"
    
    def run(self, params):
        analyzer = IndustryAnalyzer()
        result = analyzer.analyze_all_industries()
        return result.to_dict()

agent = Agent(tools=[IndustryAnalysisTool()])
```

### 在opencode中使用

**在Code Interpreter中使用:**

```python
# 直接导入使用
from skills.申万行业龙头股分析.src.industry_analyzer import IndustryAnalyzer

analyzer = IndustryAnalyzer()
result = analyzer.analyze_all_industries()

# 显示结果
import pandas as pd
pd.set_option('display.max_columns', None)
print(result.head(20))
```

**在插件中使用:**

创建插件配置 `plugins/industry_analysis.py`:

```python
from opencode import Plugin, command
from skills.申万行业龙头股分析.src.industry_analyzer import IndustryAnalyzer

class IndustryAnalysisPlugin(Plugin):
    name = "Industry Analysis"
    
    @command("/analyze_industries")
    def analyze_industries(self):
        """分析所有行业"""
        analyzer = IndustryAnalyzer()
        result = analyzer.analyze_all_industries()
        return result
```

**在Notebook中使用:**

```python
# 在Jupyter Notebook中
%load_ext autoreload
%autoreload 2

import sys
sys.path.append('skills/申万行业龙头股分析/src')

from industry_analyzer import IndustryAnalyzer

# 交互式分析
analyzer = IndustryAnalyzer()

# 获取L1级龙头
l1_top = analyzer.get_leaders_by_level('L1', top_n=10)
l1_top
```

### 在claude code中使用

**作为Skill使用:**

1. 确保skill.md文件存在且格式正确
2. Claude Code会自动识别并加载skill

**在对话中使用:**

```
用户: 分析所有申万行业的龙头股
Claude: 我将使用申万行业龙头股分析skill来获取数据...

[执行skill]
from src.industry_analyzer import IndustryAnalyzer
analyzer = IndustryAnalyzer()
result = analyzer.analyze_all_industries()
...
```

**创建定时任务:**

```python
# 使用Claude Code的automation_update工具
from codebuddy import automation_update

automation_update(
    mode="suggested create",
    name="行业龙头股每日更新",
    prompt="""
    执行每日行业龙头股数据更新：
    1. 获取最新申万行业分类
    2. 更新龙头股市值数据
    3. 生成分析报告
    4. 保存到reports/目录
    """,
    scheduleType="recurring",
    rrule="FREQ=DAILY;BYHOUR=18;BYMINUTE=0",
    cwds=["d:/tonghuashun"],
    status="ACTIVE"
)
```

## ⏰ 定时任务配置

### 在Claude Code中创建定时任务

**示例1: 每日更新**

```python
from codebuddy import automation_update

automation_update(
    mode="suggested create",
    name="每日行业数据更新",
    prompt="更新申万行业龙头股数据",
    scheduleType="recurring",
    rrule="FREQ=DAILY;BYHOUR=18;BYMINUTE=0",
    cwds=["d:/tonghuashun"],
    status="ACTIVE"
)
```

**示例2: 每周深度分析**

```python
automation_update(
    mode="suggested create",
    name="每周深度分析",
    prompt="""
    执行每周深度分析：
    1. 完整更新所有行业数据
    2. 对比上周数据变化
    3. 生成周度报告
    """,
    scheduleType="recurring",
    rrule="FREQ=WEEKLY;BYDAY=SUN;BYHOUR=20;BYMINUTE=0",
    cwds=["d:/tonghuashun"],
    status="ACTIVE"
)
```

**示例3: 月度财报更新**

```python
automation_update(
    mode="suggested create",
    name="月度财报更新",
    prompt="更新财务指标数据",
    scheduleType="recurring",
    rrule="FREQ=MONTHLY;BYMONTHDAY=1;BYHOUR=9;BYMINUTE=0",
    cwds=["d:/tonghuashun"],
    status="ACTIVE",
    validFrom="2026-04-15",
    validUntil="2026-12-31"
)
```

### 查看和管理定时任务

```python
# 查看所有任务
from codebuddy import automation_update

automation_update(mode="view")

# 更新任务
automation_update(
    mode="suggested update",
    id="task_id",
    status="PAUSED"  # 暂停任务
)

# 删除任务
# 使用 team_delete() 删除
```

## 🎯 最佳实践

### 1. 数据更新策略

- **市值数据**: 每日更新（实时性要求高）
- **财务指标**: 月度更新（财报季度发布）
- **行业分类**: 季度更新（申万指数季度调整）

### 2. 性能优化

```python
# 使用缓存
analyzer = IndustryAnalyzer()
analyzer.enable_cache = True  # 启用缓存

# 批量处理
# 分析特定级别，减少API调用
l1_only = analyzer.get_leaders_by_level('L1')
```

### 3. 错误处理

```python
try:
    result = analyzer.analyze_all_industries()
except Exception as e:
    print(f"分析失败: {e}")
    # 降级策略：使用缓存数据
    result = analyzer.load_cached_data()
```

### 4. 数据验证

```python
# 验证数据完整性
validation = analyzer.validate_data(result)

if not validation.is_valid:
    print("数据验证失败:")
    print(validation.errors)
```

## 📊 监控和日志

### 启用日志

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/industry_analysis.log'
)

# 在分析器中启用日志
analyzer = IndustryAnalyzer(enable_logging=True)
```

### 监控任务执行

```python
# 在定时任务中添加监控
def run_with_monitoring():
    import time
    start_time = time.time()
    
    try:
        analyzer = IndustryAnalyzer()
        result = analyzer.analyze_all_industries()
        files = analyzer.generate_report(result)
        
        # 发送成功通知
        send_notification(f"任务完成，生成文件: {files}")
        
    except Exception as e:
        # 发送失败通知
        send_notification(f"任务失败: {e}")
        raise
    
    finally:
        duration = time.time() - start_time
        log_metrics(duration=duration)
```

## 🔗 API集成

### REST API

创建简单的Flask API:

```python
# api.py
from flask import Flask, jsonify
from src.industry_analyzer import IndustryAnalyzer

app = Flask(__name__)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    analyzer = IndustryAnalyzer()
    result = analyzer.analyze_all_industries()
    return jsonify(result.to_dict())

@app.route('/api/leaders/<level>', methods=['GET'])
def get_leaders(level):
    analyzer = IndustryAnalyzer()
    leaders = analyzer.get_leaders_by_level(level, top_n=20)
    return jsonify(leaders.to_dict())

if __name__ == '__main__':
    app.run(debug=True)
```

### GraphQL API

```python
# graphql_api.py
from graphene import ObjectType, String, Float, List, Schema
from src.industry_analyzer import IndustryAnalyzer

class Industry(ObjectType):
    name = String()
    leader = String()
    market_cap = Float()
    roe = Float()

class Query(ObjectType):
    industries = List(Industry)
    
    def resolve_industries(self, info):
        analyzer = IndustryAnalyzer()
        result = analyzer.analyze_all_industries()
        return result.to_dict('records')

schema = Schema(query=Query)
```

## 📚 更多资源

- [完整API文档](docs/API.md)
- [定时任务配置](docs/Automation.md)
- [常见问题解答](docs/FAQ.md)
- [更新日志](CHANGELOG.md)

## 🆘 获取帮助

- **GitHub Issues**: [提交问题](https://github.com/your-repo/issues)
- **文档**: [在线文档](https://docs.your-site.com)
- **社区**: [Discord](https://discord.gg/your-invite)

---

**最后更新**: 2026-04-15  
**版本**: v1.0.0
