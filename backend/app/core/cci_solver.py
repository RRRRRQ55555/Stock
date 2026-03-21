"""
CCI (商品通道指数) 反向求解器

CCI (Commodity Channel Index)

计算公式：
TP = (High + Low + Close) / 3  (典型价格)
MA = N日TP的简单移动平均
MD = N日TP的平均绝对偏差
CCI = (TP - MA) / (0.015 × MD)

通常周期为14日

超买临界：CCI >= +100 (价格偏强，可能回调)
超卖临界：CCI <= -100 (价格偏弱，可能反弹)
"""

import numpy as np
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class CCIState:
    """CCI 昨日状态"""
    tp_history: List[float]  # 最近N-1日的典型价格 (H+L+C)/3
    md: float                # 前N-1日平均绝对偏差
    period: int = 14
    current_price: float = 0.0
    current_high: float = 0.0  # 昨日最高价（用于估算今日最高/最低）
    current_low: float = 0.0   # 昨日最低价


@dataclass
class CCITriggerResult:
    """CCI 临界价格计算结果"""
    overbought_price: Optional[float]   # 超买临界价格 (CCI >= +100)
    oversold_price: Optional[float]    # 超卖临界价格 (CCI <= -100)
    current_price: float
    cci_current: float
    
    # 距离信息
    distance_to_overbought: Optional[float] = None
    distance_to_oversold: Optional[float] = None
    
    # 区域判断
    zone: str = "neutral"  # overbought, neutral, oversold
    
    def __post_init__(self):
        if self.cci_current >= 100:
            self.zone = "overbought"
        elif self.cci_current <= -100:
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


class CCISolver:
    """CCI 反向求解器"""
    
    def __init__(self, period: int = 14, constant: float = 0.015):
        """
        初始化 CCI 求解器
        
        Args:
            period: CCI计算周期，默认14
            constant: 常数，默认0.015
        """
        self.period = period
        self.constant = constant
    
    def _calculate_md(self, tp_values: List[float], ma: float) -> float:
        """
        计算平均绝对偏差 (Mean Deviation)
        
        MD = Σ|TP - MA| / N
        """
        if len(tp_values) == 0:
            return 0.0
        
        deviations = [abs(tp - ma) for tp in tp_values]
        return sum(deviations) / len(tp_values)
    
    def calculate_cci(self, state: CCIState, close_price: float) -> float:
        """
        计算 CCI 值
        
        Args:
            state: CCI状态
            close_price: 当日收盘价
            
        Returns:
            CCI值
        """
        # 估算今日典型价格
        # 假设今日最高/最低与昨日相近
        high = state.current_high
        low = state.current_low
        tp_today = (high + low + close_price) / 3
        
        # 所有典型价格
        all_tp = state.tp_history + [tp_today]
        
        if len(all_tp) < self.period:
            return 0.0
        
        # 计算MA
        ma = sum(all_tp) / len(all_tp)
        
        # 计算MD
        md = self._calculate_md(all_tp, ma)
        
        if md == 0:
            return 0.0
        
        # 计算CCI
        cci = (tp_today - ma) / (self.constant * md)
        
        return cci
    
    def _solve_overbought_price(self, state: CCIState) -> Optional[float]:
        """
        求解 CCI 超买临界价格 (CCI >= +100)
        
        推导：
        CCI = (TP - MA) / (0.015 × MD) = 100
        
        TP - MA = 100 × 0.015 × MD = 1.5 × MD
        TP = MA + 1.5 × MD
        
        这是一个近似求解，因为MA和MD都依赖于TP本身
        使用迭代方法
        """
        try:
            if len(state.tp_history) != self.period - 1:
                return None
            
            prev_close = state.current_price
            
            # 验证当前状态
            cci_current = self.calculate_cci(state, prev_close)
            if cci_current >= 100:
                # 当前已经是超买状态
                return None
            
            # 迭代求解
            p_estimate = prev_close * 1.02  # 初始估计上涨2%
            
            for _ in range(20):  # 最多20次迭代
                # 估算今日TP
                high = state.current_high * (1 + (p_estimate - prev_close) / prev_close * 0.5)
                low = state.current_low * (1 + (p_estimate - prev_close) / prev_close * 0.3)
                tp_today = (high + low + p_estimate) / 3
                
                all_tp = state.tp_history + [tp_today]
                ma = sum(all_tp) / len(all_tp)
                md = self._calculate_md(all_tp, ma)
                
                if md == 0:
                    return None
                
                # 目标：CCI = 100
                # TP = MA + 1.5 × MD
                target_tp = ma + 1.5 * md
                
                # 从目标TP反推价格P
                # TP = (H + L + P) / 3
                # P = 3 × TP - H - L
                target_p = 3 * target_tp - high - low
                
                if abs(target_p - p_estimate) < 0.001:
                    return round(target_p, 4)
                
                p_estimate = target_p
                
                if p_estimate <= 0:
                    return None
            
            return round(p_estimate, 4) if p_estimate > 0 else None
            
        except (ZeroDivisionError, ValueError):
            return None
    
    def _solve_oversold_price(self, state: CCIState) -> Optional[float]:
        """
        求解 CCI 超卖临界价格 (CCI <= -100)
        
        推导：
        CCI = (TP - MA) / (0.015 × MD) = -100
        
        TP - MA = -100 × 0.015 × MD = -1.5 × MD
        TP = MA - 1.5 × MD
        """
        try:
            if len(state.tp_history) != self.period - 1:
                return None
            
            prev_close = state.current_price
            
            # 验证当前状态
            cci_current = self.calculate_cci(state, prev_close)
            if cci_current <= -100:
                # 当前已经是超卖状态
                return None
            
            # 迭代求解
            p_estimate = prev_close * 0.98  # 初始估计下跌2%
            
            for _ in range(20):
                # 估算今日TP
                high = state.current_high * (1 + (p_estimate - prev_close) / prev_close * 0.3)
                low = state.current_low * (1 + (p_estimate - prev_close) / prev_close * 0.5)
                tp_today = (high + low + p_estimate) / 3
                
                all_tp = state.tp_history + [tp_today]
                ma = sum(all_tp) / len(all_tp)
                md = self._calculate_md(all_tp, ma)
                
                if md == 0:
                    return None
                
                # 目标：CCI = -100
                # TP = MA - 1.5 × MD
                target_tp = ma - 1.5 * md
                
                # 从目标TP反推价格P
                target_p = 3 * target_tp - high - low
                
                if abs(target_p - p_estimate) < 0.001:
                    return round(target_p, 4)
                
                p_estimate = target_p
                
                if p_estimate <= 0:
                    return None
            
            return round(p_estimate, 4) if p_estimate > 0 else None
            
        except (ZeroDivisionError, ValueError):
            return None
    
    def solve_trigger_prices(self, state: CCIState) -> CCITriggerResult:
        """
        求解 CCI 超买/超卖临界价格
        
        Args:
            state: CCI状态
            
        Returns:
            CCITriggerResult 包含超买/超卖临界价格
        """
        # 计算当前CCI
        cci_current = self.calculate_cci(state, state.current_price)
        
        # 根据当前状态求解
        overbought_price = None
        oversold_price = None
        
        if cci_current < 100:
            # 当前非超买，求解超买价格
            overbought_price = self._solve_overbought_price(state)
        
        if cci_current > -100:
            # 当前非超卖，求解超卖价格
            oversold_price = self._solve_oversold_price(state)
        
        return CCITriggerResult(
            overbought_price=overbought_price,
            oversold_price=oversold_price,
            current_price=state.current_price,
            cci_current=cci_current
        )
    
    def simulate_price(self, state: CCIState, hypothetical_price: float) -> dict:
        """
        压力测试：模拟在假设价格下的 CCI 状态
        
        Args:
            state: CCI状态
            hypothetical_price: 假设价格
            
        Returns:
            包含CCI值及超买/超卖状态的字典
        """
        cci = self.calculate_cci(state, hypothetical_price)
        
        return {
            "hypothetical_price": hypothetical_price,
            "cci": round(cci, 2),
            "is_overbought": cci >= 100,
            "is_oversold": cci <= -100,
            "zone": "overbought" if cci >= 100 else "oversold" if cci <= -100 else "neutral"
        }


# 便捷的函数接口
def calculate_cci_trigger(
    tp_history: List[float],
    md: float,
    current_price: float,
    current_high: float,
    current_low: float,
    period: int = 14
) -> CCITriggerResult:
    """
    便捷函数：计算 CCI 临界价格
    
    Args:
        tp_history: 最近N-1日的典型价格列表
        md: 前N-1日平均绝对偏差
        current_price: 当前价格
        current_high: 昨日最高价
        current_low: 昨日最低价
        period: CCI周期
        
    Returns:
        CCITriggerResult
    """
    state = CCIState(
        tp_history=tp_history,
        md=md,
        period=period,
        current_price=current_price,
        current_high=current_high,
        current_low=current_low
    )
    
    solver = CCISolver(period)
    return solver.solve_trigger_prices(state)


def simulate_cci_at_price(
    tp_history: List[float],
    md: float,
    hypothetical_price: float,
    current_high: float,
    current_low: float,
    period: int = 14
) -> dict:
    """
    便捷函数：模拟 CCI 在假设价格下的状态
    
    Args:
        tp_history: 典型价格列表
        md: 平均绝对偏差
        hypothetical_price: 假设价格
        current_high: 最高价
        current_low: 最低价
        period: CCI周期
        
    Returns:
        包含CCI值等信息的字典
    """
    state = CCIState(
        tp_history=tp_history,
        md=md,
        period=period,
        current_price=hypothetical_price,
        current_high=current_high,
        current_low=current_low
    )
    
    solver = CCISolver(period)
    return solver.simulate_price(state, hypothetical_price)
