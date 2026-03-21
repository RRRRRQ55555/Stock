"""
预警服务

监控价格与临界点的距离，当接近或触发临界点时发送预警
"""

import asyncio
from typing import Dict, List, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
import json

from ..models.schemas import AlertMessage
from ..core.indicator_engine import TriggerMatrix


@dataclass
class AlertRule:
    """预警规则"""
    symbol: str
    alert_type: str  # "proximity", "triggered", "resonance"
    threshold_pct: float = 1.0  # 接近预警阈值(%)
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    min_interval_seconds: int = 300  # 同一预警的最小间隔(秒)


class AlertService:
    """预警服务"""
    
    def __init__(self):
        """初始化预警服务"""
        self._rules: Dict[str, AlertRule] = {}  # symbol -> rule
        self._callbacks: List[Callable[[AlertMessage], None]] = []
        self._active_symbols: Set[str] = set()
        self._last_matrix: Dict[str, TriggerMatrix] = {}
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
    
    def add_rule(self, rule: AlertRule) -> None:
        """添加预警规则"""
        self._rules[rule.symbol] = rule
        self._active_symbols.add(rule.symbol)
    
    def remove_rule(self, symbol: str) -> None:
        """移除预警规则"""
        if symbol in self._rules:
            del self._rules[symbol]
            self._active_symbols.discard(symbol)
    
    def register_callback(self, callback: Callable[[AlertMessage], None]) -> None:
        """注册预警回调函数"""
        self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable[[AlertMessage], None]) -> None:
        """注销预警回调函数"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    async def check_alerts(
        self,
        symbol: str,
        current_price: float,
        matrix: TriggerMatrix
    ) -> List[AlertMessage]:
        """
        检查是否需要触发预警
        
        Args:
            symbol: 股票代码
            current_price: 当前价格
            matrix: 触发矩阵
            
        Returns:
            预警消息列表
        """
        if symbol not in self._rules:
            return []
        
        rule = self._rules[symbol]
        if not rule.enabled:
            return []
        
        # 检查上次触发时间
        if rule.last_triggered:
            elapsed = (datetime.now() - rule.last_triggered).total_seconds()
            if elapsed < rule.min_interval_seconds:
                return []
        
        alerts = []
        
        # 检查接近预警
        alerts.extend(self._check_proximity_alerts(symbol, current_price, matrix, rule))
        
        # 检查触发预警
        alerts.extend(self._check_triggered_alerts(symbol, current_price, matrix, rule))
        
        # 检查共振预警
        alerts.extend(self._check_resonance_alerts(symbol, current_price, matrix, rule))
        
        # 更新上次触发时间
        if alerts:
            rule.last_triggered = datetime.now()
        
        return alerts
    
    def _check_proximity_alerts(
        self,
        symbol: str,
        current_price: float,
        matrix: TriggerMatrix,
        rule: AlertRule
    ) -> List[AlertMessage]:
        """检查接近临界点预警"""
        alerts = []
        threshold = rule.threshold_pct
        
        # 检查 MACD
        if matrix.macd_golden_price:
            distance = abs(matrix.macd_golden_price - current_price) / current_price * 100
            if distance <= threshold:
                alerts.append(AlertMessage(
                    symbol=symbol,
                    alert_type="proximity",
                    message=f"MACD金叉临界价格接近: 距离 ${matrix.macd_golden_price:.2f} 还有 {distance:.2f}%",
                    critical_price=matrix.macd_golden_price,
                    current_price=current_price,
                    distance_pct=distance,
                    timestamp=datetime.now()
                ))
        
        if matrix.macd_death_price:
            distance = abs(matrix.macd_death_price - current_price) / current_price * 100
            if distance <= threshold:
                alerts.append(AlertMessage(
                    symbol=symbol,
                    alert_type="proximity",
                    message=f"MACD死叉临界价格接近: 距离 ${matrix.macd_death_price:.2f} 还有 {distance:.2f}%",
                    critical_price=matrix.macd_death_price,
                    current_price=current_price,
                    distance_pct=distance,
                    timestamp=datetime.now()
                ))
        
        # 检查均线
        if matrix.ma_golden_price:
            distance = abs(matrix.ma_golden_price - current_price) / current_price * 100
            if distance <= threshold:
                alerts.append(AlertMessage(
                    symbol=symbol,
                    alert_type="proximity",
                    message=f"均线金叉临界价格接近: 距离 ${matrix.ma_golden_price:.2f} 还有 {distance:.2f}%",
                    critical_price=matrix.ma_golden_price,
                    current_price=current_price,
                    distance_pct=distance,
                    timestamp=datetime.now()
                ))
        
        if matrix.ma_death_price:
            distance = abs(matrix.ma_death_price - current_price) / current_price * 100
            if distance <= threshold:
                alerts.append(AlertMessage(
                    symbol=symbol,
                    alert_type="proximity",
                    message=f"均线死叉临界价格接近: 距离 ${matrix.ma_death_price:.2f} 还有 {distance:.2f}%",
                    critical_price=matrix.ma_death_price,
                    current_price=current_price,
                    distance_pct=distance,
                    timestamp=datetime.now()
                ))
        
        # 检查 KDJ
        if matrix.kdj_oversold_price:
            distance = abs(matrix.kdj_oversold_price - current_price) / current_price * 100
            if distance <= threshold:
                alerts.append(AlertMessage(
                    symbol=symbol,
                    alert_type="proximity",
                    message=f"KDJ超卖临界价格接近: 距离 ${matrix.kdj_oversold_price:.2f} 还有 {distance:.2f}%",
                    critical_price=matrix.kdj_oversold_price,
                    current_price=current_price,
                    distance_pct=distance,
                    timestamp=datetime.now()
                ))
        
        if matrix.kdj_overbought_price:
            distance = abs(matrix.kdj_overbought_price - current_price) / current_price * 100
            if distance <= threshold:
                alerts.append(AlertMessage(
                    symbol=symbol,
                    alert_type="proximity",
                    message=f"KDJ超买临界价格接近: 距离 ${matrix.kdj_overbought_price:.2f} 还有 {distance:.2f}%",
                    critical_price=matrix.kdj_overbought_price,
                    current_price=current_price,
                    distance_pct=distance,
                    timestamp=datetime.now()
                ))
        
        return alerts
    
    def _check_triggered_alerts(
        self,
        symbol: str,
        current_price: float,
        matrix: TriggerMatrix,
        rule: AlertRule
    ) -> List[AlertMessage]:
        """检查已触发的信号预警"""
        alerts = []
        
        # 获取上次状态进行比较
        last_matrix = self._last_matrix.get(symbol)
        if not last_matrix:
            self._last_matrix[symbol] = matrix
            return alerts
        
        # 检查 MACD 信号变化
        # 金叉：DIF 从 < Signal 变为 >= Signal
        if (last_matrix.macd_dif_current < last_matrix.macd_signal_current and
            matrix.macd_dif_current >= matrix.macd_signal_current):
            alerts.append(AlertMessage(
                symbol=symbol,
                alert_type="triggered",
                message=f"MACD金叉信号触发！DIF ({matrix.macd_dif_current:.4f}) 上穿 Signal ({matrix.macd_signal_current:.4f})",
                current_price=current_price,
                timestamp=datetime.now()
            ))
        
        # 死叉：DIF 从 > Signal 变为 <= Signal
        if (last_matrix.macd_dif_current > last_matrix.macd_signal_current and
            matrix.macd_dif_current <= matrix.macd_signal_current):
            alerts.append(AlertMessage(
                symbol=symbol,
                alert_type="triggered",
                message=f"MACD死叉信号触发！DIF ({matrix.macd_dif_current:.4f}) 下穿 Signal ({matrix.macd_signal_current:.4f})",
                current_price=current_price,
                timestamp=datetime.now()
            ))
        
        # 检查均线信号变化
        if (last_matrix.ma_short_current < last_matrix.ma_long_current and
            matrix.ma_short_current >= matrix.ma_long_current):
            alerts.append(AlertMessage(
                symbol=symbol,
                alert_type="triggered",
                message=f"均线金叉信号触发！MA{matrix.ma_short_period} 上穿 MA{matrix.ma_long_period}",
                current_price=current_price,
                timestamp=datetime.now()
            ))
        
        if (last_matrix.ma_short_current > last_matrix.ma_long_current and
            matrix.ma_short_current <= matrix.ma_long_current):
            alerts.append(AlertMessage(
                symbol=symbol,
                alert_type="triggered",
                message=f"均线死叉信号触发！MA{matrix.ma_short_period} 下穿 MA{matrix.ma_long_period}",
                current_price=current_price,
                timestamp=datetime.now()
            ))
        
        # 检查 KDJ 区域变化
        last_zone = last_matrix._get_kdj_zone() if hasattr(last_matrix, '_get_kdj_zone') else "neutral"
        current_zone = matrix._get_kdj_zone() if hasattr(matrix, '_get_kdj_zone') else "neutral"
        
        if last_zone != "oversold" and current_zone == "oversold":
            alerts.append(AlertMessage(
                symbol=symbol,
                alert_type="triggered",
                message=f"KDJ进入极度超卖区！J值 = {matrix.kdj_j_current:.2f}",
                current_price=current_price,
                timestamp=datetime.now()
            ))
        
        if last_zone != "overbought" and current_zone == "overbought":
            alerts.append(AlertMessage(
                symbol=symbol,
                alert_type="triggered",
                message=f"KDJ进入极度超买区！J值 = {matrix.kdj_j_current:.2f}",
                current_price=current_price,
                timestamp=datetime.now()
            ))
        
        # 更新历史状态
        self._last_matrix[symbol] = matrix
        
        return alerts
    
    def _check_resonance_alerts(
        self,
        symbol: str,
        current_price: float,
        matrix: TriggerMatrix,
        rule: AlertRule
    ) -> List[AlertMessage]:
        """检查共振区间预警"""
        alerts = []
        
        if not matrix.resonance_zones:
            return alerts
        
        for zone in matrix.resonance_zones:
            # 检查是否进入共振区间
            if zone['price_min'] <= current_price <= zone['price_max']:
                alerts.append(AlertMessage(
                    symbol=symbol,
                    alert_type="resonance",
                    message=f"进入共振买入区间！{', '.join(zone['indicators'])} 在 ${zone['price_center']:.2f} 附近重合",
                    critical_price=zone['price_center'],
                    current_price=current_price,
                    distance_pct=0,
                    timestamp=datetime.now()
                ))
            # 检查是否接近共振区间
            else:
                distance = min(
                    abs(zone['price_min'] - current_price),
                    abs(zone['price_max'] - current_price)
                ) / current_price * 100
                
                if distance <= rule.threshold_pct:
                    alerts.append(AlertMessage(
                        symbol=symbol,
                        alert_type="resonance",
                        message=f"接近共振区间！{', '.join(zone['indicators'])} 在 ${zone['price_center']:.2f} 附近重合，距离 {distance:.2f}%",
                        critical_price=zone['price_center'],
                        current_price=current_price,
                        distance_pct=distance,
                        timestamp=datetime.now()
                    ))
        
        return alerts
    
    async def notify(self, alert: AlertMessage) -> None:
        """通知所有注册的回调"""
        for callback in self._callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"预警回调执行失败: {e}")
    
    async def start_monitoring(self, check_interval: int = 5) -> None:
        """
        启动监控循环（后台任务）
        
        Args:
            check_interval: 检查间隔（秒）
        """
        self._running = True
        
        while self._running:
            # 这里应该调用数据服务获取最新价格和矩阵
            # 实际监控逻辑由外部调用 check_alerts 实现
            await asyncio.sleep(check_interval)
    
    def stop_monitoring(self) -> None:
        """停止监控"""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()


# 全局预警服务实例
alert_service = AlertService()
