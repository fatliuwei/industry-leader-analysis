#!/bin/bash

# GitHub上传脚本
# 使用方法：bash upload_to_github.sh 你的用户名

set -e

# 检查参数
if [ $# -eq 0 ]; then
    echo "使用方法: bash upload_to_github.sh <你的GitHub用户名>"
    echo "示例: bash upload_to_github.sh zhangsan"
    exit 1
fi

USERNAME=$1
REPO_NAME="industry-leader-analysis"

echo "=========================================="
echo "GitHub上传脚本"
echo "=========================================="
echo ""
echo "目标仓库: https://github.com/$USERNAME/$REPO_NAME"
echo ""

# 检查是否已配置用户信息
if ! git config user.name > /dev/null; then
    echo "请先配置Git用户信息:"
    echo "  git config user.name \"你的名字\""
    echo "  git config user.email \"你的邮箱\""
    exit 1
fi

# 检查是否已有远程仓库
if git remote | grep -q "origin"; then
    echo "[!] 远程仓库已存在"
    echo "当前远程仓库:"
    git remote -v
    echo ""
    read -p "是否更新远程仓库地址? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote set-url origin git@github.com:$USERNAME/$REPO_NAME.git
        echo "[OK] 远程仓库地址已更新"
    fi
else
    echo "[1/3] 添加远程仓库..."
    git remote add origin git@github.com:$USERNAME/$REPO_NAME.git
    echo "[OK] 远程仓库已添加"
fi

echo ""
echo "[2/3] 切换到main分支..."
git branch -M main
echo "[OK] 分支已切换"

echo ""
echo "[3/3] 推送代码到GitHub..."
git push -u origin main

echo ""
echo "=========================================="
echo "✅ 上传成功！"
echo "=========================================="
echo ""
echo "仓库地址: https://github.com/$USERNAME/$REPO_NAME"
echo ""
echo "下一步:"
echo "1. 访问仓库页面添加描述和标签"
echo "2. 创建第一个Release (v1.0.0)"
echo "3. 分享你的项目到社交媒体"
echo ""
