# GitHub上传指南

本指南帮助你将申万行业龙头股分析Skill上传到GitHub。

## 📋 准备工作

### 1. 配置Git用户信息（首次使用）

```bash
# 全局配置（推荐）
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"

# 或仅在本项目配置
cd d:/tonghuashun/skills/申万行业龙头股分析
git config user.name "你的名字"
git config user.email "你的邮箱"
```

### 2. 生成SSH密钥（如果还没有）

```bash
# 生成SSH密钥
ssh-keygen -t rsa -b 4096 -C "你的邮箱"

# 查看公钥
cat ~/.ssh/id_rsa.pub

# 将公钥添加到GitHub
# GitHub -> Settings -> SSH and GPG keys -> New SSH key
```

## 🚀 上传步骤

### 方法1: 创建新仓库并推送（推荐）

#### 步骤1: 在GitHub创建新仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `industry-leader-analysis` 或 `shenwan-industry-analysis`
   - **Description**: `申万行业龙头股分析工具 - 自动获取和分析511个申万行业的龙头股数据`
   - **可见性**: Public（公开）或 Private（私有）
   - **不要勾选**: 
     - ❌ Add a README file
     - ❌ Add .gitignore
     - ❌ Choose a license
   
3. 点击 **Create repository**

#### 步骤2: 推送代码到GitHub

```bash
# 进入项目目录
cd d:/tonghuashun/skills/申万行业龙头股分析

# 添加远程仓库（替换为你的用户名）
git remote add origin https://github.com/你的用户名/industry-leader-analysis.git

# 或使用SSH（推荐）
git remote add origin git@github.com:你的用户名/industry-leader-analysis.git

# 推送代码
git branch -M main
git push -u origin main
```

#### 步骤3: 验证上传

访问你的仓库页面：`https://github.com/你的用户名/industry-leader-analysis`

---

### 方法2: 使用GitHub CLI（推荐）

如果你安装了GitHub CLI (`gh`)：

```bash
# 进入项目目录
cd d:/tonghuashun/skills/申万行业龙头股分析

# 登录GitHub
gh auth login

# 创建仓库并推送
gh repo create industry-leader-analysis --public --source=. --push

# 或创建私有仓库
gh repo create industry-leader-analysis --private --source=. --push
```

---

### 方法3: 使用GitHub Desktop

1. 打开 GitHub Desktop
2. File -> Add local repository
3. 选择项目目录：`d:/tonghuashun/skills/申万行业龙头股分析`
4. 点击 "Create a new repository on GitHub"
5. 填写仓库信息并创建
6. 点击 "Publish repository"

---

## 📝 仓库设置建议

### 1. 添加主题标签

在仓库设置中添加标签：
- `python`
- `finance`
- `stock-analysis`
- `tushare`
- `industry-analysis`
- `quant`
- `automated-trading`

### 2. 设置主页

在仓库设置中：
- **Website**: 你的个人网站或文档站点
- **Topics**: 添加相关主题标签

### 3. 添加徽章

在README.md顶部添加徽章：

```markdown
[![GitHub stars](https://img.shields.io/github/stars/你的用户名/industry-leader-analysis.svg?style=for-the-badge)](https://github.com/你的用户名/industry-leader-analysis/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/你的用户名/industry-leader-analysis.svg?style=for-the-badge)](https://github.com/你的用户名/industry-leader-analysis/network)
[![GitHub issues](https://img.shields.io/github/issues/你的用户名/industry-leader-analysis.svg?style=for-the-badge)](https://github.com/你的用户名/industry-leader-analysis/issues)
[![GitHub license](https://img.shields.io/github/license/你的用户名/industry-leader-analysis.svg?style=for-the-badge)](https://github.com/你的用户名/industry-leader-analysis/blob/main/LICENSE)
```

---

## 🔄 后续更新

### 提交更改

```bash
# 查看更改
git status

# 添加更改
git add .

# 提交
git commit -m "描述你的更改"

# 推送
git push
```

### 创建新版本

```bash
# 创建标签
git tag -a v1.0.0 -m "Release v1.0.0"

# 推送标签
git push origin v1.0.0

# 或推送所有标签
git push --tags
```

---

## 📊 项目统计

当前提交包含：
- ✅ 12个文件
- ✅ 2443行代码
- ✅ 完整文档
- ✅ 使用示例
- ✅ MIT许可证

---

## 🎯 推广建议

### 1. 社交媒体分享

在社交媒体分享你的项目：
- Twitter/X
- LinkedIn
- 微博
- 知乎

示例文案：
```
🚀 刚发布了一个新项目！

申万行业龙头股分析工具
✅ 511个申万行业全覆盖
✅ 自动识别龙头股
✅ 支持定时任务
✅ 多格式报告输出

适合：量化交易、投资研究、行业分析

GitHub: https://github.com/你的用户名/industry-leader-analysis

#Python #Finance #Quant
```

### 2. 提交到项目集合

- [Python官方包索引PyPI](https://pypi.org/)
- [Awesome Python](https://github.com/vinta/awesome-python)
- [Awesome Quant](https://github.com/wilsonfreitas/awesome-quant)

### 3. 写博客文章

- 在CSDN、掘金、知乎写介绍文章
- 在Medium、Dev.to写英文介绍

---

## ❓ 常见问题

### Q1: 推送失败，提示权限错误？

```bash
# 解决方案1: 使用SSH
git remote set-url origin git@github.com:你的用户名/industry-leader-analysis.git

# 解决方案2: 使用Personal Access Token
# GitHub -> Settings -> Developer settings -> Personal access tokens
git remote set-url origin https://你的token@github.com/你的用户名/industry-leader-analysis.git
```

### Q2: 如何更新仓库？

```bash
# 查看更改
git status

# 添加所有更改
git add .

# 提交
git commit -m "更新说明"

# 推送
git push
```

### Q3: 如何创建Release？

1. GitHub仓库页面 -> Releases -> Draft a new release
2. 选择标签（如v1.0.0）
3. 填写Release标题和说明
4. 上传附加文件（可选）
5. 点击 "Publish release"

### Q4: 如何添加协作者？

1. GitHub仓库 -> Settings -> Collaborators
2. 输入协作者的GitHub用户名或邮箱
3. 选择权限（Read/Write/Admin）
4. 发送邀请

---

## ✅ 检查清单

上传前确认：

- [ ] 已配置Git用户信息
- [ ] 已生成SSH密钥并添加到GitHub
- [ ] 已在GitHub创建仓库
- [ ] 已添加远程仓库地址
- [ ] 已推送代码
- [ ] 已验证仓库页面可访问
- [ ] 已添加仓库描述和标签
- [ ] 已在README.md添加徽章（可选）

---

## 📚 更多资源

- [GitHub文档](https://docs.github.com)
- [Git官方文档](https://git-scm.com/doc)
- [GitHub CLI文档](https://cli.github.com/manual/)

---

## 🎉 完成！

恭喜！你的项目已成功上传到GitHub！

**下一步**:
1. 添加仓库描述和标签
2. 创建第一个Release
3. 分享到社交媒体
4. 收集反馈并持续改进

---

**仓库地址**: https://github.com/你的用户名/industry-leader-analysis

**问题反馈**: https://github.com/你的用户名/industry-leader-analysis/issues
