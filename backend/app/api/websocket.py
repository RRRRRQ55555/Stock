"""
WebSocket 接口

提供实时行情推送和预警通知
"""

import asyncio
import json
from typing import Dict, Set
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect

from ..services.data_service import data_service
from ..services.alert_service import alert_service, AlertMessage, AlertRule
from ..core.indicator_engine import IndicatorEngine


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        """初始化连接管理器"""
        self.active_connections: Dict[str, Set[WebSocket]] = {}  # symbol -> connections
        self.symbol_subscriptions: Dict[WebSocket, Set[str]] = {}  # connection -> symbols
        self.price_update_task: asyncio.Task = None
        self._running = False
    
    async def connect(self, websocket: WebSocket, symbols: list = None):
        """接受新的WebSocket连接"""
        await websocket.accept()
        
        # 初始化连接
        self.symbol_subscriptions[websocket] = set(symbols or [])
        
        # 添加到各股票的连接集合
        for symbol in (symbols or []):
            if symbol not in self.active_connections:
                self.active_connections[symbol] = set()
            self.active_connections[symbol].add(websocket)
        
        # 如果没有symbol，默认订阅
        if not symbols:
            self.active_connections.setdefault("default", set()).add(websocket)
        
        print(f"WebSocket连接建立，当前连接数: {len(self.symbol_subscriptions)}")
    
    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        # 从所有symbol的连接集合中移除
        for symbol, connections in self.active_connections.items():
            connections.discard(websocket)
        
        # 移除订阅记录
        if websocket in self.symbol_subscriptions:
            del self.symbol_subscriptions[websocket]
        
        print(f"WebSocket连接断开，当前连接数: {len(self.symbol_subscriptions)}")
    
    async def subscribe(self, websocket: WebSocket, symbols: list):
        """订阅股票"""
        if websocket not in self.symbol_subscriptions:
            return
        
        # 从旧symbol中移除
        for old_symbol in self.symbol_subscriptions[websocket]:
            if old_symbol in self.active_connections:
                self.active_connections[old_symbol].discard(websocket)
        
        # 添加到新symbol
        self.symbol_subscriptions[websocket] = set(symbols)
        for symbol in symbols:
            if symbol not in self.active_connections:
                self.active_connections[symbol] = set()
            self.active_connections[symbol].add(websocket)
        
        # 发送确认
        await websocket.send_json({
            "type": "subscribe_confirm",
            "symbols": symbols,
            "timestamp": datetime.now().isoformat()
        })
    
    async def broadcast_to_symbol(self, symbol: str, message: dict):
        """向订阅某股票的所有连接广播消息"""
        if symbol not in self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections[symbol]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        # 清理断开的连接
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast(self, message: dict):
        """向所有连接广播消息"""
        disconnected = []
        for connection in self.symbol_subscriptions.keys():
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        # 清理断开的连接
        for conn in disconnected:
            self.disconnect(conn)
    
    async def start_price_updates(self, interval: int = 5):
        """
        启动价格更新推送
        
        Args:
            interval: 更新间隔（秒）
        """
        self._running = True
        
        while self._running:
            try:
                # 获取所有订阅的股票
                all_symbols = set()
                for symbols in self.symbol_subscriptions.values():
                    all_symbols.update(symbols)
                
                # 获取每个股票的价格并推送
                for symbol in all_symbols:
                    if not symbol or symbol == "default":
                        continue
                    
                    try:
                        # 获取当前价格
                        current_price = await data_service.get_current_price(symbol)
                        
                        # 推送价格更新
                        await self.broadcast_to_symbol(symbol, {
                            "type": "price_update",
                            "symbol": symbol,
                            "price": current_price,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        # 检查预警
                        await self._check_and_send_alerts(symbol, current_price)
                        
                    except Exception as e:
                        print(f"推送 {symbol} 价格失败: {e}")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"价格更新循环出错: {e}")
                await asyncio.sleep(interval)
    
    async def _check_and_send_alerts(self, symbol: str, current_price: float):
        """检查并发送预警"""
        try:
            # 获取种子数据
            seed_data = await data_service.calculate_indicator_seed(symbol)
            
            # 更新当前价格
            seed_data.macd.current_price = current_price
            seed_data.ma.current_price = current_price
            seed_data.kdj.current_price = current_price
            
            # 计算触发矩阵
            engine = IndicatorEngine()
            matrix = engine.calculate_trigger_matrix(
                symbol=symbol,
                current_price=current_price,
                macd_state=seed_data.macd,
                ma_state=seed_data.ma,
                kdj_state=seed_data.kdj
            )
            
            # 检查预警
            alerts = await alert_service.check_alerts(symbol, current_price, matrix)
            
            # 发送预警消息
            for alert in alerts:
                await self.broadcast_to_symbol(symbol, {
                    "type": "alert",
                    "symbol": symbol,
                    "alert_type": alert.alert_type,
                    "message": alert.message,
                    "critical_price": alert.critical_price,
                    "current_price": alert.current_price,
                    "distance_pct": alert.distance_pct,
                    "timestamp": alert.timestamp.isoformat()
                })
                
                # 同时通过alert_service通知其他回调
                await alert_service.notify(alert)
                
        except Exception as e:
            print(f"检查 {symbol} 预警失败: {e}")
    
    def stop_price_updates(self):
        """停止价格更新"""
        self._running = False
        if self.price_update_task:
            self.price_update_task.cancel()


# 全局连接管理器实例
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket端点处理函数
    
    处理客户端连接、订阅、消息接收等
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            msg_type = data.get("type", "")
            
            if msg_type == "subscribe":
                # 订阅股票
                symbols = data.get("symbols", [])
                await manager.subscribe(websocket, symbols)
                
            elif msg_type == "ping":
                # 心跳响应
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
                
            elif msg_type == "stress_test":
                # 实时压力测试请求
                symbol = data.get("symbol")
                hypothetical_price = data.get("price")
                
                if symbol and hypothetical_price:
                    try:
                        # 获取种子数据
                        seed_data = await data_service.calculate_indicator_seed(symbol)
                        
                        # 执行压力测试
                        engine = IndicatorEngine()
                        result = engine.stress_test(
                            hypothetical_price=hypothetical_price,
                            macd_state=seed_data.macd,
                            ma_state=seed_data.ma,
                            kdj_state=seed_data.kdj
                        )
                        
                        await websocket.send_json({
                            "type": "stress_test_result",
                            "symbol": symbol,
                            "result": result,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                    except Exception as e:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"压力测试失败: {str(e)}"
                        })
            
            elif msg_type == "get_matrix":
                # 请求触发矩阵
                symbol = data.get("symbol")
                
                if symbol:
                    try:
                        # 获取数据
                        seed_data = await data_service.calculate_indicator_seed(symbol)
                        current_price = await data_service.get_current_price(symbol)
                        
                        # 更新价格
                        seed_data.macd.current_price = current_price
                        seed_data.ma.current_price = current_price
                        seed_data.kdj.current_price = current_price
                        
                        # 计算
                        engine = IndicatorEngine()
                        matrix = engine.calculate_trigger_matrix(
                            symbol=symbol,
                            current_price=current_price,
                            macd_state=seed_data.macd,
                            ma_state=seed_data.ma,
                            kdj_state=seed_data.kdj
                        )
                        
                        await websocket.send_json({
                            "type": "matrix_update",
                            "symbol": symbol,
                            "matrix": matrix.to_dict(),
                            "timestamp": datetime.now().isoformat()
                        })
                        
                    except Exception as e:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"获取矩阵失败: {str(e)}"
                        })
                        
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket错误: {e}")
        manager.disconnect(websocket)


async def start_websocket_services():
    """启动WebSocket服务（后台任务）"""
    # 启动价格更新推送
    asyncio.create_task(manager.start_price_updates(interval=5))
    
    # 注册alert_service回调，将预警也推送到WebSocket
    async def on_alert(alert: AlertMessage):
        await manager.broadcast_to_symbol(alert.symbol, {
            "type": "alert",
            "symbol": alert.symbol,
            "alert_type": alert.alert_type,
            "message": alert.message,
            "critical_price": alert.critical_price,
            "current_price": alert.current_price,
            "distance_pct": alert.distance_pct,
            "timestamp": alert.timestamp.isoformat()
        })
    
    alert_service.register_callback(on_alert)
