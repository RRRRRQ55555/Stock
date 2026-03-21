#!/bin/bash
# 股票助手启动脚本（最简单方式）

cd /opt/stock-assistant/backend

echo "🚀 启动股票助手后端服务..."
echo "📊 API 地址: http://localhost:8000"
echo "📚 文档地址: http://localhost:8000/docs"
echo ""

# 检查是否已在运行
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "⚠️ 服务已在运行"
    echo "查看状态: ./status.sh"
    exit 1
fi

# 后台启动
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &

sleep 2

# 检查是否启动成功
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 服务启动成功！"
    echo ""
    echo "常用命令："
    echo "  查看日志: tail -f /opt/stock-assistant/backend/app.log"
    echo "  停止服务: ./stop.sh"
    echo "  查看状态: ./status.sh"
else
    echo "❌ 启动失败，查看日志："
    echo "  tail -f /opt/stock-assistant/backend/app.log"
fi
