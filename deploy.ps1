# 股票技术指标工具 - PowerShell 部署脚本

# 添加 Git 到 PATH
$env:PATH = "D:\GIT\Git\bin;$env:PATH"

Write-Host "`n" -NoNewline
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  📦 股票技术指标前置预判工具 - Git 部署脚本" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "`n" -NoNewline

# 进入项目目录
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectPath

Write-Host "[1/5] 初始化 Git 仓库..." -ForegroundColor Yellow
git init
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ 初始化失败" -ForegroundColor Red
    exit 1
}

Write-Host "[2/5] 配置 Git 用户信息..." -ForegroundColor Yellow
git config user.email "submission@example.com"
git config user.name "Stock Assistant Developer"

Write-Host "[3/5] 添加所有文件..." -ForegroundColor Yellow
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ 添加文件失败" -ForegroundColor Red
    exit 1
}

Write-Host "[4/5] 提交代码..." -ForegroundColor Yellow
git commit -m "Stock technical indicator tool - ready for submission"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ 提交失败" -ForegroundColor Red
    exit 1
}

Write-Host "[5/5] 准备推送..." -ForegroundColor Yellow

Write-Host "`n" -NoNewline
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  ✅ 本地 Git 仓库已准备就绪！" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "`n" -NoNewline

Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "  1. 打开 GitHub：https://github.com/new" -ForegroundColor Gray
Write-Host "  2. 创建新仓库，名称为 'stock-assistant'" -ForegroundColor Gray
Write-Host "  3. 获得仓库 URL（https://github.com/YOUR_USERNAME/stock-assistant.git）" -ForegroundColor Gray
Write-Host "  4. 在下方输入你的 GitHub 仓库 URL" -ForegroundColor Gray
Write-Host "`n" -NoNewline

$githubUrl = Read-Host "请输入你的 GitHub 仓库 URL"

if ([string]::IsNullOrEmpty($githubUrl)) {
    Write-Host "  ❌ 未输入 URL" -ForegroundColor Red
    exit 1
}

Write-Host "`n正在添加远程仓库..." -ForegroundColor Yellow
git remote add origin $githubUrl

Write-Host "正在推送到 GitHub..." -ForegroundColor Yellow
git branch -M main
git push -u origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n  ❌ 推送失败" -ForegroundColor Red
    Write-Host "  可能原因：GitHub 账户未认证" -ForegroundColor Yellow
    Write-Host "  解决方案：" -ForegroundColor Yellow
    Write-Host "    1. 创建 Personal Access Token：https://github.com/settings/tokens" -ForegroundColor Gray
    Write-Host "    2. 使用 token 替代密码" -ForegroundColor Gray
    exit 1
}

Write-Host "`n" -NoNewline
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  ✅ 代码已成功推送到 GitHub！" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "`n" -NoNewline

Write-Host "现在：" -ForegroundColor Yellow
Write-Host "  1. 打开 Vercel：https://vercel.com" -ForegroundColor Green
Write-Host "  2. 用 GitHub 账户登录" -ForegroundColor Green
Write-Host "  3. 点击 'Add New' → 'Project'" -ForegroundColor Green
Write-Host "  4. 选择 'stock-assistant' 仓库" -ForegroundColor Green
Write-Host "  5. 配置：Root Directory = frontend" -ForegroundColor Green
Write-Host "  6. 点击 Deploy" -ForegroundColor Green
Write-Host "`n" -NoNewline

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "`n" -NoNewline

Read-Host "按 Enter 键结束"
