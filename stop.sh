#!/bin/bash
# 股票助手停止脚本

echo "🛑 停止股票助手服务..."

# 查找并停止 uvicorn 进程
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    pkill -f "uvicorn app.main:app"
    echo "✅ 服务已停止"
else
    echo "⚠️ 服务未运行"
fi
