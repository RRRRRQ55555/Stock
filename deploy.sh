#!/bin/bash
# 股票助手部署脚本

set -e

echo "🚀 开始部署股票助手..."

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "${RED}❌ Docker 未安装，请先安装 Docker${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "${RED}❌ Docker Compose 未安装，请先安装 Docker Compose${NC}"
    exit 1
fi

# 拉取最新代码
echo "📦 拉取最新代码..."
git pull origin main 2>/dev/null || echo "⚠️ 非 git 仓库，跳过拉取"

# 构建并启动
echo "🔨 构建 Docker 镜像..."
docker-compose build --no-cache

echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
sleep 5

# 健康检查
echo "🏥 健康检查..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "${GREEN}✅ 部署成功！服务运行正常${NC}"
    echo "📊 API 地址: http://localhost:8000"
    echo "📚 API 文档: http://localhost:8000/docs"
else
    echo "${RED}⚠️ 服务可能未正常启动，请检查日志: docker-compose logs${NC}"
fi

echo ""
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"
