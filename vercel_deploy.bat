@echo off
REM Vercel 直接部署脚本

echo.
echo ============================================================
echo  🚀 Vercel 直接部署 - 股票技术指标工具
echo ============================================================
echo.

REM 设置 Node 路径
set PATH=D:\NodeJS;%PATH%

REM 进入项目目录
cd /d "e:\RQ\龙虾\Stock\stock_assistant"

echo [1/3] 检查 Vercel CLI...
call npx vercel --version

echo.
echo [2/3] 登录 Vercel（如果需要）...
call npx vercel login --skip-dialog

echo.
echo [3/3] 部署到 Vercel...
echo.
call npx vercel --prod

echo.
echo ============================================================
echo  ✅ 部署完成！
echo ============================================================
echo.
echo 你的应用将在以下 URL 上线：
echo https://stock-assistant-XXXXX.vercel.app
echo.
pause
