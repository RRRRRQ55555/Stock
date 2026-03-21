"""
威廉指标 (WR) 反向求解器

威廉指标 (Williams %R)

计算公式：
WR = (H_n - C) / (H_n - L_n) × (-100)

其中：
- H_n：N日内最高价
- L_n：N日内最低价  
- C：当日收盘价

通常周期为14日

超买临界：WR <= -80 (价格接近区间顶部，可能回调)
超卖临界：WR >= -20 (价格接近区间底部，可能反弹)

注意：WR 为负值，-0 表示最高价，-100 表示最低价
"""

import numpy as np
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class WRState:
    """WR 昨日状态"""
    h_n: float          # N日内最高价
    l_n: float          # N日内最低价
    wr_yest: float      # 昨日WR值
    period: int = 14
    current_price: float = 0.0


@dataclass
class WRTriggerResult:
    """WR 临界价格计算结果"""
    overbought_price: Optional[float]   # 超买临界价格 (WR <= -80)
    oversold_price: Optional[float]     # 超卖临界价格 (WR >= -20)
    current_price: float
    wr_current: float
    
    # 距离信息
    distance_to_overbought: Optional[float] = None
    distance_to_oversold: Optional[float] = None
    
    # 区域判断
    zone: str = "neutral"  # overbought, neutral, oversold
    
    def __post_init__(self):
        if self.wr_current <= -80:
            self.zone = "overbought"
        elif self.wr_current >= -20:
            self.zone = "oversold"
        else:
            self.zone = "neutral"
        
        if self.overbought_price is not None and self.current_price > 0:
            self.distance_to_overbought = (
                (self.overbought_price - self.current_price) / self.current_price * 100
            )
        if self.oversold_price is not None and self.current_price > 0:
            self.distance_to_oversold = (
                (self.oversold_price - self.current_price) / self.current_price * 100
            )


class WRSolver:
    """WR 反向求解器"""
    
    def __init__(self, period: int = 14, overbought_threshold: float = -80, oversold_threshold: float = -20):
        """
        初始化 WR 求解器
        
        Args:
            period: WR计算周期，默认14
            overbought_threshold: 超买阈值，默认-80
            oversold_threshold: 超卖阈值，默认-20
        """
        self.period = period
        self.overbought_threshold = overbought_threshold
        self.oversold_threshold = oversold_threshold
    
    def calculate_wr(self, state: WRState, close_price: float) -> float:
        """
        计算 WR 值
        
        Args:
            state: WR状态
            close_price: 当日收盘价
            
        Returns:
            WR值 (-100 到 0)
        """
        h_n = state.h_n
        l_n = state.l_n
        
        if h_n == l_n:
            return -50.0  # 避免除零，返回中间值
        
        wr = (h_n - close_price) / (h_n - l_n) * (-100)
        
        return max(-100, min(0, wr))
    
    def _solve_overbought_price(self, state: WRState) -> Optional[float]:
        """
        求解 WR 超买临界价格 (WR <= -80)
        
        推导：
        WR = (H_n - C) / (H_n - L_n) × (-100) = -80
        
        (H_n - C) / (H_n - L_n) = 0.8
        H_n - C = 0.8 × (H_n - L_n)
        C = H_n - 0.8 × (H_n - L_n)
        C = H_n × 0.2 + L_n × 0.8
        
        这意味着价格接近区间顶部的80%位置
        """
        try:
            h_n = state.h_n
            l_n = state.l_n
            
            if h_n <= l_n:
                return None
            
            # 验证当前状态
            wr_current = self.calculate_wr(state, state.current_price)
            if wr_current <= self.overbought_threshold:
                # 当前已经是超买状态
                return None
            
            # 计算临界价格
            # WR = -80 时
            wr_target = self.overbought_threshold
            ratio = (-wr_target) / 100  # 转换为比例，-80 -> 0.8
            
            # C = H_n - ratio * (H_n - L_n)
            critical_price = h_n - ratio * (h_n - l_n)
            
            if critical_price <= 0:
                return None
            
            return critical_price
            
        except (ZeroDivisionError, ValueError):
            return None
    
    def _solve_oversold_price(self, state: WRState) -> Optional[float]:
        """
        求解 WR 超卖临界价格 (WR >= -20)
        
        推导：
        WR = (H_n - C) / (H_n - L_n) × (-100) = -20
        
        (H_n - C) / (H_n - L_n) = 0.2
        H_n - C = 0.2 × (H_n - L_n)
        C = H_n - 0.2 × (H_n - L_n)
        C = H_n × 0.8 + L_n × 0.2
        
        这意味着价格接近区间底部的20%位置
        """
        try:
            h_n = state.h_n
            l_n = state.l_n
            
            if h_n <= l_n:
                return None
            
            # 验证当前状态
            wr_current = self.calculate_wr(state, state.current_price)
            if wr_current >= self.oversold_threshold:
                # 当前已经是超卖状态
                return None
            
            # 计算临界价格
            # WR = -20 时
            wr_target = self.oversold_threshold
            ratio = (-wr_target) / 100  # 转换为比例，-20 -> 0.2
            
            # C = H_n - ratio * (H_n - L_n)
            critical_price = h_n - ratio * (h_n - l_n)
            
            if critical_price <= 0:
                return None
            
            return critical_price
            
        except (ZeroDivisionError, ValueError):
            return None
    
    def solve_trigger_prices(self, state: WRState) -> WRTriggerResult:
        """
        求解 WR 超买/超卖临界价格
        
        Args:
            state: WR状态
            
        Returns:
            WRTriggerResult 包含超买/超卖临界价格
        """
        # 计算当前WR
        wr_current = self.calculate_wr(state, state.current_price)
        
        # 根据当前状态求解
        overbought_price = None
        oversold_price = None
        
        if wr_current > self.overbought_threshold:
            # 当前非超买，求解超买价格
            overbought_price = self._solve_overbought_price(state)
        
        if wr_current < self.oversold_threshold:
            # 当前非超卖，求解超卖价格
            oversold_price = self._solve_oversold_price(state)
        
        return WRTriggerResult(
            overbought_price=overbought_price,
            oversold_price=oversold_price,
            current_price=state.current_price,
            wr_current=wr_current
        )
    
    def simulate_price(self, state: WRState, hypothetical_price: float) -> dict:
        """
        压力测试：模拟在假设价格下的 WR 状态
        
        Args:
            state: WR状态
            hypothetical_price: 假设价格
            
        Returns:
            包含WR值及超买/超卖状态的字典
        """
        wr = self.calculate_wr(state, hypothetical_price)
        
        # 计算价格在区间内的位置百分比
        h_n = state.h_n
        l_n = state.l_n
        if h_n != l_n:
            position_pct = (hypothetical_price - l_n) / (h_n - l_n) * 100
        else:
            position_pct = 50
        
        return {
            "hypothetical_price": hypothetical_price,
            "wr": round(wr, 2),
            "position_pct": round(position_pct, 2),  # 区间位置百分比
            "is_overbought": wr <= self.overbought_threshold,
            "is_oversold": wr >= self.oversold_threshold,
            "zone": "overbought" if wr <= self.overbought_threshold else "oversold" if wr >= self.oversold_threshold else "neutral"
        }


# 便捷的函数接口
def calculate_wr_trigger(
    h_n: float,
    l_n: float,
    wr_yest: float,
    current_price: float,
    period: int = 14
) -> WRTriggerResult:
    """
    便捷函数：计算 WR 临界价格
    
    Args:
        h_n: N日内最高价
        l_n: N日内最低价
        wr_yest: 昨日WR值
        current_price: 当前价格
        period: WR周期
        
    Returns:
        WRTriggerResult
    """
    state = WRState(
        h_n=h_n,
        l_n=l_n,
        wr_yest=wr_yest,
        period=period,
        current_price=current_price
    )
    
    solver = WRSolver(period)
    return solver.solve_trigger_prices(state)


def simulate_wr_at_price(
    h_n: float,
    l_n: float,
    wr_yest: float,
    hypothetical_price: float,
    period: int = 14
) -> dict:
    """
    便捷函数：模拟 WR 在假设价格下的状态
    
    Args:
        h_n: N日内最高价
        l_n: N日内最低价
        wr_yest: 昨日WR值
        hypothetical_price: 假设价格
        period: WR周期
        
    Returns:
        包含WR值等信息的字典
    """
    state = WRState(
        h_n=h_n,
        l_n=l_n,
        wr_yest=wr_yest,
        period=period,
        current_price=hypothetical_price
    )
    
    solver = WRSolver(period)
    return solver.simulate_price(state, hypothetical_price)
