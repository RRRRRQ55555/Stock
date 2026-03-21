"""
Parabolic SAR (Stop and Reverse) 反向求解器

抛物线转向指标，用于：
- 判断趋势方向
- 设置追踪止损点
- 识别趋势反转点

计算公式（简化版）：
- 上升趋势：SAR = 前一日 SAR + AF × (前一日 EP - 前一日 SAR)
- 下降趋势：SAR = 前一日 SAR - AF × (前一日 SAR - 前一日 EP)

其中：
- AF (Acceleration Factor): 加速因子，通常从 0.02 开始，最大 0.2
- EP (Extreme Point): 极值点（上升时为最高点，下降时为最低点）
"""

import numpy as np
from typing import List, Optional, Tuple
from .base_solver import BaseSolver, TriggerResult, SimulationResult, IndicatorRegistry


@IndicatorRegistry.register
class ParabolicSARSolver(BaseSolver):
    """Parabolic SAR 反向求解器"""
    
    name = "parabolic_sar"
    display_name = "Parabolic SAR (抛物线转向)"
    description = "追踪止损和趋势反转指标，判断趋势方向和设置动态止损点"
    
    default_params = {
        "af_start": 0.02,  # 初始加速因子
        "af_increment": 0.02,  # AF增量
        "af_max": 0.2,  # AF最大值
    }
    
    def get_required_history_length(self) -> int:
        return 5
    
    def calculate(
        self,
        prices: List[float],
        current_price: float,
        highs: List[float] = None,
        lows: List[float] = None
    ) -> Tuple[float, str]:
        """
        计算 Parabolic SAR 值
        
        返回 (SAR值, 趋势方向)
        """
        full_prices = prices + [current_price]
        
        if len(full_prices) < 5:
            # 数据不足，使用简单近似
            return current_price * 0.98, "up"
        
        # 简化计算：使用近期极值点估算 SAR
        recent_prices = full_prices[-10:]
        recent_high = max(recent_prices)
        recent_low = min(recent_prices)
        
        # 判断趋势方向
        if current_price > np.mean(recent_prices):
            trend = "up"
            # 上升趋势中，SAR 在价格下方
            sar = recent_low * 0.99
        else:
            trend = "down"
            # 下降趋势中，SAR 在价格上方
            sar = recent_high * 1.01
        
        return sar, trend
    
    def solve_trigger_prices(
        self,
        prices: List[float],
        current_price: float
    ) -> TriggerResult:
        """
        求解 Parabolic SAR 临界价格
        
        关键信号：
        - 价格跌破 SAR (上升趋势)：趋势反转看跌
        - 价格升破 SAR (下降趋势)：趋势反转看涨
        """
        sar, trend = self.calculate(prices, current_price)
        
        # 计算反转临界价格
        if trend == "up":
            # 上升趋势，跌破 SAR 为看跌信号
            bearish_price = sar
            # 需要突破更高点才能看涨（延续趋势）
            recent_high = max(prices[-10:]) if len(prices) >= 10 else max(prices)
            bullish_price = recent_high * 1.01
        else:
            # 下降趋势，升破 SAR 为看涨信号
            bullish_price = sar
            # 需要跌破更低点才能看跌（延续趋势）
            recent_low = min(prices[-10:]) if len(prices) >= 10 else min(prices)
            bearish_price = recent_low * 0.99
        
        # 根据当前位置调整
        if trend == "up":
            if current_price <= sar:
                # 已经跌破 SAR，反转看跌
                bearish_price = None
        else:
            if current_price >= sar:
                # 已经升破 SAR，反转看涨
                bullish_price = None
        
        # 确定区域
        distance_to_sar = abs(current_price - sar) / current_price * 100
        
        if trend == "up":
            if current_price > sar:
                zone = "above_sar_up"
            else:
                zone = "below_sar_reversal"
        else:
            if current_price < sar:
                zone = "below_sar_down"
            else:
                zone = "above_sar_reversal"
        
        return TriggerResult(
            indicator_name=self.name,
            current_value=sar,
            current_price=current_price,
            bullish_trigger_price=round(bullish_price, 2) if bullish_price else None,
            bearish_trigger_price=round(bearish_price, 2) if bearish_price else None,
            zone=zone,
            metadata={
                "sar": round(sar, 2),
                "trend": trend,
                "distance_to_sar_pct": round(distance_to_sar, 2),
                "stop_loss_recommendation": round(sar, 2),
            }
        )
    
    def simulate(self, prices: List[float], hypothetical_price: float) -> SimulationResult:
        """压力测试"""
        sar, current_trend = self.calculate(prices, hypothetical_price)
        
        # 判断趋势是否反转
        if current_trend == "up":
            if hypothetical_price < sar:
                zone = "reversal_down"
                is_bullish = False
                is_bearish = True
            else:
                zone = "continuing_up"
                is_bullish = True
                is_bearish = False
        else:
            if hypothetical_price > sar:
                zone = "reversal_up"
                is_bullish = True
                is_bearish = False
            else:
                zone = "continuing_down"
                is_bullish = False
                is_bearish = True
        
        return SimulationResult(
            hypothetical_price=hypothetical_price,
            indicator_value=sar,
            zone=zone,
            is_bullish=is_bullish,
            is_bearish=is_bearish,
            metadata={
                "sar": round(sar, 2),
                "trend": current_trend,
            }
        )
