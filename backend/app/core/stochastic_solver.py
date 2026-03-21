"""
Stochastic Oscillator (随机指标) 反向求解器

类似于 KDJ，但计算方式略有不同：
- %K = (Current Close - Lowest Low) / (Highest High - Lowest Low) × 100
- %D = %K 的 N 日移动平均

阈值：
- > 80: 超买
- < 20: 超卖
"""

import numpy as np
from typing import List, Optional
from .base_solver import BaseSolver, TriggerResult, SimulationResult, IndicatorRegistry


@IndicatorRegistry.register
class StochasticSolver(BaseSolver):
    """Stochastic 随机指标反向求解器"""
    
    name = "stochastic"
    display_name = "Stochastic (随机指标)"
    description = "类似于 KDJ，判断价格在近期区间内的相对位置"
    
    default_params = {
        "k_period": 14,  # %K 周期
        "d_period": 3,   # %D 周期（平滑）
        "overbought": 80,
        "oversold": 20,
    }
    
    def get_required_history_length(self) -> int:
        return self.params["k_period"]
    
    def calculate(
        self,
        prices: List[float],
        current_price: float
    ) -> float:
        """计算 %K 值"""
        period = self.params["k_period"]
        
        # 获取最近 period 个价格
        recent_prices = prices[-period+1:] + [current_price] if len(prices) >= period-1 else prices + [current_price]
        
        if len(recent_prices) < period:
            return 50.0
        
        lowest = min(recent_prices)
        highest = max(recent_prices)
        
        if highest == lowest:
            return 50.0
        
        k = (current_price - lowest) / (highest - lowest) * 100
        return float(k)
    
    def solve_trigger_prices(
        self,
        prices: List[float],
        current_price: float
    ) -> TriggerResult:
        """求解 Stochastic 临界价格"""
        period = self.params["k_period"]
        overbought = self.params["overbought"]
        oversold = self.params["oversold"]
        
        current_k = self.calculate(prices, current_price)
        
        # 获取近期高低点
        recent_prices = prices[-period:] if len(prices) >= period else prices
        lowest_low = min(recent_prices)
        highest_high = max(recent_prices)
        
        # 计算超卖临界价格 (K = oversold)
        # oversold = (P - L) / (H - L) * 100
        # P = L + (H - L) * oversold / 100
        bullish_price = lowest_low + (highest_high - lowest_low) * oversold / 100
        
        # 计算超买临界价格 (K = overbought)
        bearish_price = lowest_low + (highest_high - lowest_low) * overbought / 100
        
        # 根据当前状态调整
        if current_k <= oversold:
            bullish_price = None  # 已经是超卖状态
        if current_k >= overbought:
            bearish_price = None  # 已经是超买状态
        
        # 确定区域
        if current_k <= oversold:
            zone = "oversold"
        elif current_k >= overbought:
            zone = "overbought"
        else:
            zone = "neutral"
        
        return TriggerResult(
            indicator_name=self.name,
            current_value=current_k,
            current_price=current_price,
            bullish_trigger_price=round(bullish_price, 2) if bullish_price else None,
            bearish_trigger_price=round(bearish_price, 2) if bearish_price else None,
            zone=zone,
            metadata={
                "k_period": period,
                "lowest_low": round(lowest_low, 2),
                "highest_high": round(highest_high, 2),
                "range": round(highest_high - lowest_low, 2),
            }
        )
    
    def simulate(self, prices: List[float], hypothetical_price: float) -> SimulationResult:
        """压力测试"""
        k = self.calculate(prices, hypothetical_price)
        
        overbought = self.params["overbought"]
        oversold = self.params["oversold"]
        
        if k >= overbought:
            zone = "overbought"
        elif k <= oversold:
            zone = "oversold"
        else:
            zone = "neutral"
        
        return SimulationResult(
            hypothetical_price=hypothetical_price,
            indicator_value=k,
            zone=zone,
            is_bullish=k <= oversold,
            is_bearish=k >= overbought,
            metadata={"stochastic_k": round(k, 2)}
        )
