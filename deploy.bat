@echo off
REM 股票技术指标工具 - Git 自动部署脚本
REM 功能：初始化 Git、配置用户、推送到 GitHub

setlocal enabledelayedexpansion

REM 添加 Git 到环境变量
set PATH=D:\GIT\Git\bin;%PATH%

echo.
echo ============================================================
echo   📦 股票技术指标前置预判工具 - Git 部署脚本
echo ============================================================
echo.

REM 获取当前目录
cd /d "%~dp0"

echo [1/5] 初始化 Git 仓库...
call git init
if errorlevel 1 (
    echo   ❌ 初始化失败
    pause
    exit /b 1
)

echo [2/5] 配置 Git 用户信息...
call git config user.email "submission@example.com"
call git config user.name "Stock Assistant Developer"

echo [3/5] 添加所有文件...
call git add .
if errorlevel 1 (
    echo   ❌ 添加文件失败
    pause
    exit /b 1
)

echo [4/5] 提交代码...
call git commit -m "Stock technical indicator tool - ready for submission"
if errorlevel 1 (
    echo   ❌ 提交失败
    pause
    exit /b 1
)

echo [5/5] 准备推送...
echo.
echo ============================================================
echo   ✅ 本地 Git 仓库已准备就绪！
echo ============================================================
echo.
echo 下一步：
echo   1. 打开 GitHub：https://github.com/new
echo   2. 创建新仓库，名称为 "stock-assistant"
echo   3. 获得仓库 URL（https://github.com/YOUR_USERNAME/stock-assistant.git）
echo   4. 在下方输入你的 GitHub 仓库 URL
echo.

set /p GITHUB_URL="请输入你的 GitHub 仓库 URL: "

if "%GITHUB_URL%"=="" (
    echo   ❌ 未输入 URL
    pause
    exit /b 1
)

echo.
echo 正在添加远程仓库...
call git remote add origin %GITHUB_URL%

echo 正在推送到 GitHub...
call git branch -M main
call git push -u origin main

if errorlevel 1 (
    echo   ❌ 推送失败
    echo   可能原因：GitHub 账户未认证
    echo   解决方案：
    echo     1. 创建 Personal Access Token：https://github.com/settings/tokens
    echo     2. 使用 token 替代密码
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   ✅ 代码已成功推送到 GitHub！
echo ============================================================
echo.
echo 现在：
echo   1. 打开 Vercel：https://vercel.com
echo   2. 用 GitHub 账户登录
echo   3. 点击 "Add New" → "Project"
echo   4. 选择 "stock-assistant" 仓库
echo   5. 配置：Root Directory = frontend
echo   6. 点击 Deploy
echo.
echo ============================================================
echo.

pause
