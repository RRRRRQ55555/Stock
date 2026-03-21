"""
FastAPI 主入口

技术指标前置预判工具 API 服务
"""

import asyncio
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# 加载环境变量
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(backend_dir, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"[OK] 已加载配置文件: {env_path}")
else:
    load_dotenv()

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .api.strategy_routes import router as strategy_router
from .api.websocket import websocket_endpoint, start_websocket_services, manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    启动时初始化服务，关闭时清理资源
    """
    # 启动时
    print("\n启动技术指标预判工具服务...")
    
    # 检查Tushare配置
    token = os.getenv("TUSHARE_TOKEN")
    if token:
        print("[OK] Tushare Token 已配置")
    else:
        print("[INFO] Tushare Token 未配置，使用Yahoo Finance获取数据")
    
    # 启动WebSocket服务
    await start_websocket_services()
    print("[OK] 服务启动完成\n")
    
    yield
    
    # 关闭时
    print("关闭服务...")
    manager.stop_price_updates()


# 创建 FastAPI 应用
app = FastAPI(
    title="技术指标前置预判工具 API",
    description="""
    通过反向数学推导计算技术指标临界价格
    
    ## 核心功能
    
    ### 1. 临界价格计算
    - MACD 金叉/死叉临界价格
    - 均线多头排列/空头排列临界价格  
    - KDJ 超买/超卖临界价格
    
    ### 2. 压力测试
    模拟假设价格下的技术指标状态
    
    ### 3. 实时预警
    当价格接近临界点或触发信号时推送通知
    
    ### 4. WebSocket 实时推送
    实时价格更新和预警推送
    
    ### 5. 交易策略管理
    - 创建自定义交易策略（入场/止损/止盈条件）
    - 每日策略可行性检查
    - 自动计算入场区间和止损价格
    - 策略执行跟踪
    """,
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api", tags=["API"])
app.include_router(strategy_router, prefix="/api", tags=["交易策略"])


# WebSocket端点
@app.websocket("/ws")
async def websocket_handler(websocket: WebSocket):
    """WebSocket连接处理"""
    await websocket_endpoint(websocket)


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "技术指标前置预判工具",
        "version": "1.0.0"
    }


# 根路径
@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "技术指标前置预判工具 API",
        "docs": "/docs",
        "health": "/health",
        "websocket": "/ws"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
