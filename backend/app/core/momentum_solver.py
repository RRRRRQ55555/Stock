"""
Momentum (动量指标) 反向求解器

动量 = 当前价格 - N 周期前的价格

表示价格变化的速度和幅度
- 正值：上涨动能
- 负值：下跌动能
- 零轴穿越：动量转向信号
"""

import numpy as np
from typing import List, Optional
from .base_solver import BaseSolver, TriggerResult, SimulationResult, IndicatorRegistry


@IndicatorRegistry.register
class MomentumSolver(BaseSolver):
    """Momentum 动量指标反向求解器"""
    
    name = "momentum"
    display_name = "Momentum (动量指标)"
    description = "衡量价格变化的速度，判断动能强弱和转向"
    
    default_params = {
        "period": 12,  # 动量计算周期
        "strong_threshold": 5,  # 强动量阈值 (%)
    }
    
    def get_required_history_length(self) -> int:
        return self.params["period"] + 1
    
    def calculate(
        self,
        prices: List[float],
        current_price: float
    ) -> float:
        """
        计算动量值
        
        Momentum = Current - Price[N periods ago]
        返回百分比形式
        """
        period = self.params["period"]
        
        full_prices = prices + [current_price]
        
        if len(full_prices) < period + 1:
            return 0.0
        
        price_n_periods_ago = full_prices[-(period+1)]
        
        if price_n_periods_ago == 0:
            return 0.0
        
        momentum = (current_price - price_n_periods_ago) / price_n_periods_ago * 100
        
        return float(momentum)
    
    def solve_trigger_prices(
        self,
        prices: List[float],
        current_price: float
    ) -> TriggerResult:
        """
        求解动量临界价格
        
        关键阈值：
        - 动量转正：看涨信号
        - 动量转负：看跌信号
        - 强动量突破：趋势加速
        """
        period = self.params["period"]
        strong_threshold = self.params["strong_threshold"]
        
        current_momentum = self.calculate(prices, current_price)
        
        # 获取 N 周期前的价格
        if len(prices) >= period:
            price_n_ago = prices[-period]
        else:
            price_n_ago = prices[0] if prices else current_price
        
        # 计算动量为零的价格（与 N 周期前价格相同）
        zero_momentum_price = price_n_ago
        
        # 计算强动量价格
        # 上涨强动量：P = P_n_ago * (1 + strong_threshold/100)
        strong_bullish_price = price_n_ago * (1 + strong_threshold / 100)
        
        # 下跌强动量：P = P_n_ago * (1 - strong_threshold/100)
        strong_bearish_price = price_n_ago * (1 - strong_threshold / 100)
        
        # 根据当前动量状态设置触发价
        bullish_price = None
        bearish_price = None
        
        if current_momentum < 0:
            # 当前负动量，转正为看涨
            bullish_price = zero_momentum_price
        elif current_momentum < strong_threshold:
            # 当前正动量但未达强动量，突破为看涨
            bullish_price = strong_bullish_price
        
        if current_momentum > 0:
            # 当前正动量，转负为看跌
            bearish_price = zero_momentum_price
        elif current_momentum > -strong_threshold:
            # 当前负动量但未达强负动量，突破为看跌
            bearish_price = strong_bearish_price
        
        # 确定区域
        if current_momentum <= -strong_threshold:
            zone = "strong_down"
        elif current_momentum < 0:
            zone = "weak_down"
        elif current_momentum < strong_threshold:
            zone = "weak_up"
        else:
            zone = "strong_up"
        
        return TriggerResult(
            indicator_name=self.name,
            current_value=current_momentum,
            current_price=current_price,
            bullish_trigger_price=round(bullish_price, 2) if bullish_price else None,
            bearish_trigger_price=round(bearish_price, 2) if bearish_price else None,
            zone=zone,
            metadata={
                "period": period,
                "price_n_periods_ago": round(price_n_ago, 2),
                "zero_momentum_price": round(zero_momentum_price, 2),
                "momentum_pct": round(current_momentum, 2),
            }
        )
    
    def simulate(self, prices: List[float], hypothetical_price: float) -> SimulationResult:
        """压力测试"""
        momentum = self.calculate(prices, hypothetical_price)
        
        strong_threshold = self.params["strong_threshold"]
        
        if momentum <= -strong_threshold:
            zone = "strong_down"
            is_bullish = False
            is_bearish = True
        elif momentum < 0:
            zone = "weak_down"
            is_bullish = False
            is_bearish = False
        elif momentum < strong_threshold:
            zone = "weak_up"
            is_bullish = False
            is_bearish = False
        else:
            zone = "strong_up"
            is_bullish = True
            is_bearish = False
        
        return SimulationResult(
            hypothetical_price=hypothetical_price,
            indicator_value=momentum,
            zone=zone,
            is_bullish=is_bullish,
            is_bearish=is_bearish,
            metadata={"momentum_pct": round(momentum, 2)}
        )
