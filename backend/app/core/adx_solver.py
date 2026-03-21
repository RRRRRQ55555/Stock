"""
ADX (Average Directional Index) 平均趋向指数反向求解器

ADX 衡量趋势强度（非方向）：
- ADX < 20: 弱趋势/无趋势（震荡市）
- ADX 20-40: 中等趋势强度
- ADX > 40: 强趋势
- ADX > 50: 极强趋势

需要结合 +DI 和 -DI 判断趋势方向：
- +DI > -DI: 上升趋势
- +DI < -DI: 下降趋势

计算公式涉及 DM (Directional Movement)
"""

import numpy as np
from typing import List, Optional
from .base_solver import BaseSolver, TriggerResult, SimulationResult, IndicatorRegistry


@IndicatorRegistry.register
class ADXSolver(BaseSolver):
    """ADX 反向求解器"""
    
    name = "adx"
    display_name = "ADX (平均趋向指数)"
    description = "衡量趋势强度，判断趋势行情或震荡行情"
    
    default_params = {
        "period": 14,  # ADX计算周期
        "weak_trend": 20,  # 弱趋势阈值
        "strong_trend": 40,  # 强趋势阈值
        "extreme_trend": 50,  # 极强趋势阈值
    }
    
    def get_required_history_length(self) -> int:
        return self.params["period"] * 2
    
    def calculate(
        self,
        prices: List[float],
        current_price: float
    ) -> float:
        """
        计算 ADX 值（简化版本）
        
        使用价格变动的连续性来近似趋势强度
        """
        period = self.params["period"]
        
        full_prices = prices + [current_price]
        if len(full_prices) < period * 2:
            return 25.0  # 默认中等趋势
        
        # 计算价格变动
        deltas = np.diff(full_prices)
        
        # 计算 +DM 和 -DM 的近似值
        plus_dm = np.where(deltas > 0, deltas, 0)
        minus_dm = np.where(deltas < 0, -deltas, 0)
        
        # 计算平滑后的 DM
        smoothed_plus_dm = np.mean(plus_dm[-period:])
        smoothed_minus_dm = np.mean(minus_dm[-period:])
        
        # 计算 TR 的近似值（价格变动幅度）
        tr_values = np.abs(deltas)
        atr = np.mean(tr_values[-period:])
        
        if atr == 0:
            return 0.0
        
        # 计算 +DI 和 -DI
        plus_di = (smoothed_plus_dm / atr) * 100
        minus_di = (smoothed_minus_dm / atr) * 100
        
        # 计算 DX
        dx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100 if (plus_di + minus_di) > 0 else 0
        
        # DX 的移动平均即为 ADX（简化）
        adx = dx
        
        return float(adx)
    
    def solve_trigger_prices(
        self,
        prices: List[float],
        current_price: float
    ) -> TriggerResult:
        """
        求解 ADX 临界价格
        
        ADX 本身不直接给出买卖价格，但可以帮助判断：
        - ADX > 40: 趋势行情，顺势而为
        - ADX < 20: 震荡行情，高抛低吸
        
        这里计算使 ADX 达到强趋势阈值的价格
        """
        period = self.params["period"]
        weak_trend = self.params["weak_trend"]
        strong_trend = self.params["strong_trend"]
        
        current_adx = self.calculate(prices, current_price)
        
        # 计算当前的 +DI 和 -DI 趋势方向
        full_prices = prices[-period:] + [current_price]
        deltas = np.diff(full_prices)
        
        plus_moves = sum(1 for d in deltas if d > 0)
        minus_moves = sum(1 for d in deltas if d < 0)
        
        trend_direction = "up" if plus_moves > minus_moves else "down"
        
        # 计算使 ADX 进入强趋势的价格（需要价格持续同向运动）
        # 这是一个近似计算
        
        bullish_price = None
        bearish_price = None
        
        if trend_direction == "up":
            # 上升趋势中，继续上涨使趋势强化
            bullish_price = current_price * 1.03  # 上涨 3% 进入强趋势
        else:
            # 下降趋势中，继续下跌使趋势强化
            bearish_price = current_price * 0.97  # 下跌 3% 进入强趋势
        
        # 确定当前趋势状态
        if current_adx < weak_trend:
            zone = "ranging"  # 震荡市
        elif current_adx < strong_trend:
            zone = "moderate_trend"  # 中等趋势
        else:
            zone = "strong_trend"  # 强趋势
        
        return TriggerResult(
            indicator_name=self.name,
            current_value=current_adx,
            current_price=current_price,
            bullish_trigger_price=bullish_price,
            bearish_trigger_price=bearish_price,
            zone=zone,
            metadata={
                "period": period,
                "trend_direction": trend_direction,
                "adx_level": "weak" if current_adx < weak_trend else "moderate" if current_adx < strong_trend else "strong",
                "suggestion": "趋势跟踪" if current_adx > weak_trend else "震荡交易",
            }
        )
    
    def simulate(self, prices: List[float], hypothetical_price: float) -> SimulationResult:
        """压力测试"""
        adx = self.calculate(prices, hypothetical_price)
        
        weak_trend = self.params["weak_trend"]
        strong_trend = self.params["strong_trend"]
        
        if adx < weak_trend:
            zone = "ranging"
        elif adx < strong_trend:
            zone = "moderate_trend"
        else:
            zone = "strong_trend"
        
        # ADX 不直接判断方向，只判断趋势强度
        return SimulationResult(
            hypothetical_price=hypothetical_price,
            indicator_value=adx,
            zone=zone,
            is_bullish=False,  # ADX 不判断方向
            is_bearish=False,
            metadata={
                "adx": round(adx, 2),
                "trend_strength": "weak" if adx < weak_trend else "moderate" if adx < strong_trend else "strong",
            }
        )
