#!/bin/bash
# 股票助手状态查看脚本

echo "📊 股票助手服务状态"
echo "===================="

# 检查进程
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "✅ 服务运行中"
    echo ""
    echo "进程信息："
    pgrep -a -f "uvicorn app.main:app"
    echo ""
    echo "健康检查："
    curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "无法访问"
else
    echo "❌ 服务未运行"
fi

echo ""
echo "日志位置: /opt/stock-assistant/backend/app.log"
echo "查看日志: tail -f /opt/stock-assistant/backend/app.log"
