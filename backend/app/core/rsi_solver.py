"""
RSI 反向求解器

RSI (Relative Strength Index) 相对强弱指标

计算公式：
RS = 平均上涨幅度 / 平均下跌幅度
RSI = 100 - (100 / (1 + RS))

通常周期为14日

超买临界：RSI >= 70
超卖临界：RSI <= 30
"""

import numpy as np
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class RSIState:
    """RSI 昨日状态"""
    avg_gain: float       # 前13日平均上涨幅度
    avg_loss: float       # 前13日平均下跌幅度
    gains: List[float]    # 最近13日的上涨幅度列表（用于计算新的平均值）
    losses: List[float]   # 最近13日的下跌幅度列表
    period: int = 14
    current_price: float = 0.0


@dataclass
class RSITriggerResult:
    """RSI 临界价格计算结果"""
    oversold_price: Optional[float]   # 超卖临界价格 (RSI <= 30)
    overbought_price: Optional[float]  # 超买临界价格 (RSI >= 70)
    current_price: float
    rsi_current: float
    
    # 距离信息
    distance_to_oversold: Optional[float] = None
    distance_to_overbought: Optional[float] = None
    
    # 区域判断
    zone: str = "neutral"  # oversold, neutral, overbought
    
    def __post_init__(self):
        if self.rsi_current <= 30:
            self.zone = "oversold"
        elif self.rsi_current >= 70:
            self.zone = "overbought"
        else:
            self.zone = "neutral"
        
        if self.oversold_price is not None and self.current_price > 0:
            self.distance_to_oversold = (
                (self.oversold_price - self.current_price) / self.current_price * 100
            )
        if self.overbought_price is not None and self.current_price > 0:
            self.distance_to_overbought = (
                (self.overbought_price - self.current_price) / self.current_price * 100
            )


class RSISolver:
    """RSI 反向求解器"""
    
    def __init__(self, period: int = 14, oversold_threshold: float = 30, overbought_threshold: float = 70):
        """
        初始化 RSI 求解器
        
        Args:
            period: RSI计算周期，默认14
            oversold_threshold: 超卖阈值，默认30
            overbought_threshold: 超买阈值，默认70
        """
        self.period = period
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold
    
    def calculate_rsi(self, state: RSIState, close_price: float) -> float:
        """
        计算 RSI 值
        
        Args:
            state: RSI状态
            close_price: 今日收盘价
            
        Returns:
            RSI值 (0-100)
        """
        # 计算今日涨跌幅（相对于昨日收盘价）
        prev_close = state.current_price
        if prev_close <= 0:
            return 50.0
        
        change = close_price - prev_close
        gain = max(0, change)
        loss = max(0, -change)
        
        # 使用平滑移动平均公式
        # 新平均 = (前平均 * (n-1) + 今日值) / n
        new_avg_gain = (state.avg_gain * (self.period - 1) + gain) / self.period
        new_avg_loss = (state.avg_loss * (self.period - 1) + loss) / self.period
        
        # 计算RS和RSI
        if new_avg_loss == 0:
            return 100.0
        
        rs = new_avg_gain / new_avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return max(0, min(100, rsi))
    
    def _solve_critical_price(self, state: RSIState, target_rsi: float) -> Optional[float]:
        """
        求解使 RSI 达到目标值的临界价格
        
        推导过程:
        RSI = 100 - 100/(1+RS) = target_rsi
        => 100/(1+RS) = 100 - target_rsi
        => 1+RS = 100 / (100 - target_rsi)
        => RS = 100/(100-target_rsi) - 1
        
        设新的平均上涨为 A_gain', 平均下跌为 A_loss'
        RS = A_gain' / A_loss'
        
        A_gain' = (A_gain * 13 + gain) / 14
        A_loss' = (A_loss * 13 + loss) / 14
        
        假设价格上涨（gain > 0, loss = 0）:
        A_loss' = A_loss * 13 / 14
        RS = ((A_gain * 13 + gain) / 14) / (A_loss * 13 / 14)
           = (A_gain * 13 + gain) / (A_loss * 13)
        => gain = RS * A_loss * 13 - A_gain * 13
        
        P = prev_close + gain
        """
        try:
            prev_close = state.current_price
            if prev_close <= 0:
                return None
            
            # 计算目标RS
            if target_rsi >= 100:
                target_rs = float('inf')
            elif target_rsi <= 0:
                target_rs = 0
            else:
                target_rs = 100 / (100 - target_rsi) - 1
            
            # 当前平均值的平滑计算后的新值
            # 上涨情景：loss = 0
            new_avg_loss_up = state.avg_loss * (self.period - 1) / self.period
            
            if new_avg_loss_up <= 0:
                # 如果平均下跌为0，RS趋于无穷大，RSI=100
                if target_rsi >= 100:
                    return prev_close * 1.001  # 微小上涨即可
                return None
            
            # 求解需要的 gain
            # target_rs = new_avg_gain / new_avg_loss
            # new_avg_gain = target_rs * new_avg_loss
            # (A_gain * 13 + gain) / 14 = target_rs * new_avg_loss
            # gain = target_rs * new_avg_loss * 14 - A_gain * 13
            required_avg_gain = target_rs * new_avg_loss_up
            required_gain = required_avg_gain * self.period - state.avg_gain * (self.period - 1)
            
            # 如果需要的涨幅不合理（为负或太大），说明当前无法达到
            if required_gain < 0:
                return None
            
            critical_price = prev_close + required_gain
            
            if critical_price <= 0:
                return None
            
            return critical_price
            
        except (ZeroDivisionError, ValueError):
            return None
    
    def _solve_overbought_price(self, state: RSIState) -> Optional[float]:
        """
        求解 RSI 超买临界价格 (RSI >= 70)
        
        推导逻辑同上，目标是使 RSI 达到超买阈值
        """
        try:
            prev_close = state.current_price
            if prev_close <= 0:
                return None
            
            # 验证当前状态
            rsi_current = self.calculate_rsi(state, prev_close)
            if rsi_current >= self.overbought_threshold:
                # 当前已经是超买状态
                return None
            
            return self._solve_critical_price(state, self.overbought_threshold)
            
        except (ZeroDivisionError, ValueError):
            return None
    
    def _solve_oversold_price(self, state: RSIState) -> Optional[float]:
        """
        求解 RSI 超卖临界价格 (RSI <= 30)
        
        推导：
        假设价格下跌（gain = 0, loss > 0）:
        new_avg_gain = A_gain * 13 / 14
        new_avg_loss = (A_loss * 13 + loss) / 14
        
        target_rs = new_avg_gain / new_avg_loss
        => new_avg_loss = new_avg_gain / target_rs
        (A_loss * 13 + loss) / 14 = (A_gain * 13 / 14) / target_rs
        A_loss * 13 + loss = A_gain * 13 / target_rs
        loss = A_gain * 13 / target_rs - A_loss * 13
        
        P = prev_close - loss
        """
        try:
            prev_close = state.current_price
            if prev_close <= 0:
                return None
            
            # 验证当前状态
            rsi_current = self.calculate_rsi(state, prev_close)
            if rsi_current <= self.oversold_threshold:
                # 当前已经是超卖状态
                return None
            
            # 计算目标RS
            if self.oversold_threshold >= 100:
                return None
            target_rs = 100 / (100 - self.oversold_threshold) - 1
            
            if target_rs <= 0:
                return None
            
            # 下跌情景：gain = 0
            new_avg_gain_down = state.avg_gain * (self.period - 1) / self.period
            
            if new_avg_gain_down <= 0:
                # 如果平均上涨为0，则RS=0，RSI=0
                if self.oversold_threshold <= 0:
                    return prev_close * 0.999
                return prev_close * 0.95  # 大幅下降
            
            # 求解需要的 loss
            # target_rs = new_avg_gain / new_avg_loss
            # new_avg_loss = new_avg_gain / target_rs
            required_avg_loss = new_avg_gain_down / target_rs
            required_loss = required_avg_loss * self.period - state.avg_loss * (self.period - 1)
            
            if required_loss < 0:
                return None
            
            critical_price = prev_close - required_loss
            
            if critical_price <= 0:
                return None
            
            return critical_price
            
        except (ZeroDivisionError, ValueError):
            return None
    
    def solve_trigger_prices(self, state: RSIState) -> RSITriggerResult:
        """
        求解 RSI 超买/超卖临界价格
        
        Args:
            state: RSI状态
            
        Returns:
            RSITriggerResult 包含超买/超卖临界价格
        """
        # 计算当前RSI
        rsi_current = self.calculate_rsi(state, state.current_price)
        
        # 根据当前状态求解
        oversold_price = None
        overbought_price = None
        
        if rsi_current > self.oversold_threshold:
            # 当前非超卖，求解超卖价格
            oversold_price = self._solve_oversold_price(state)
        
        if rsi_current < self.overbought_threshold:
            # 当前非超买，求解超买价格
            overbought_price = self._solve_overbought_price(state)
        
        return RSITriggerResult(
            oversold_price=oversold_price,
            overbought_price=overbought_price,
            current_price=state.current_price,
            rsi_current=rsi_current
        )
    
    def simulate_price(self, state: RSIState, hypothetical_price: float) -> dict:
        """
        压力测试：模拟在假设价格下的 RSI 状态
        
        Args:
            state: RSI状态
            hypothetical_price: 假设价格
            
        Returns:
            包含RSI值及超买/超卖状态的字典
        """
        rsi = self.calculate_rsi(state, hypothetical_price)
        
        return {
            "hypothetical_price": hypothetical_price,
            "rsi": round(rsi, 2),
            "is_oversold": rsi <= self.oversold_threshold,
            "is_overbought": rsi >= self.overbought_threshold,
            "zone": "oversold" if rsi <= self.oversold_threshold else "overbought" if rsi >= self.overbought_threshold else "neutral"
        }


# 便捷的函数接口
def calculate_rsi_trigger(
    avg_gain: float,
    avg_loss: float,
    gains: List[float],
    losses: List[float],
    current_price: float,
    period: int = 14
) -> RSITriggerResult:
    """
    便捷函数：计算 RSI 临界价格
    
    Args:
        avg_gain: 前N-1日平均上涨幅度
        avg_loss: 前N-1日平均下跌幅度
        gains: 最近N-1日的上涨幅度列表
        losses: 最近N-1日的下跌幅度列表
        current_price: 当前价格
        period: RSI周期
        
    Returns:
        RSITriggerResult
    """
    state = RSIState(
        avg_gain=avg_gain,
        avg_loss=avg_loss,
        gains=gains,
        losses=losses,
        period=period,
        current_price=current_price
    )
    
    solver = RSISolver(period)
    return solver.solve_trigger_prices(state)


def simulate_rsi_at_price(
    avg_gain: float,
    avg_loss: float,
    gains: List[float],
    losses: List[float],
    hypothetical_price: float,
    period: int = 14
) -> dict:
    """
    便捷函数：模拟 RSI 在假设价格下的状态
    
    Args:
        avg_gain: 平均上涨幅度
        avg_loss: 平均下跌幅度
        gains: 上涨幅度列表
        losses: 下跌幅度列表
        hypothetical_price: 假设价格
        period: RSI周期
        
    Returns:
        包含RSI值等信息的字典
    """
    state = RSIState(
        avg_gain=avg_gain,
        avg_loss=avg_loss,
        gains=gains,
        losses=losses,
        period=period,
        current_price=hypothetical_price
    )
    
    solver = RSISolver(period)
    return solver.simulate_price(state, hypothetical_price)
