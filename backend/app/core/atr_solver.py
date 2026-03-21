"""
ATR (Average True Range) 真实波幅指标反向求解器

ATR 衡量市场波动性，用于：
- 设置止损位
- 判断趋势强度
- 预测价格突破范围

计算公式：
TR = max(High-Low, |High-PrevClose|, |Low-PrevClose|)
ATR = N日 TR 的移动平均

突破阈值：当前 ATR × 倍数（通常 2-3 倍）
"""

import numpy as np
from typing import List, Optional
from .base_solver import BaseSolver, TriggerResult, SimulationResult, IndicatorRegistry


@IndicatorRegistry.register
class ATRSolver(BaseSolver):
    """ATR 反向求解器"""
    
    name = "atr"
    display_name = "ATR (真实波幅)"
    description = "衡量市场波动性，用于设置止损和预测价格突破范围"
    
    default_params = {
        "period": 14,  # ATR计算周期
        "breakout_multiplier": 2.0,  # 突破倍数
        "stop_loss_multiplier": 1.5,  # 止损倍数
    }
    
    def get_required_history_length(self) -> int:
        return self.params["period"] + 1
    
    def calculate_true_range(
        self,
        high: float,
        low: float,
        prev_close: float
    ) -> float:
        """计算真实波幅 TR"""
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        return max(tr1, tr2, tr3)
    
    def calculate(
        self,
        prices: List[float],
        current_price: float
    ) -> float:
        """
        计算 ATR 值
        
        简化版本：使用价格变动幅度近似 TR
        """
        period = self.params["period"]
        
        if len(prices) < period:
            return 0.0
        
        # 计算 TR 序列（使用价格变动近似）
        tr_values = []
        for i in range(1, len(prices)):
            tr = abs(prices[i] - prices[i-1])
            tr_values.append(tr)
        
        # 加上当前价格的 TR
        tr_values.append(abs(current_price - prices[-1]))
        
        # 计算 ATR (简单移动平均)
        atr = np.mean(tr_values[-period:])
        
        return float(atr)
    
    def solve_trigger_prices(
        self,
        prices: List[float],
        current_price: float
    ) -> TriggerResult:
        """
        求解 ATR 临界价格
        
        突破判断：
        - 向上突破：价格 > 近期高点 + ATR × 倍数
        - 向下突破：价格 < 近期低点 - ATR × 倍数
        """
        period = self.params["period"]
        breakout_mult = self.params["breakout_multiplier"]
        stop_mult = self.params["stop_loss_multiplier"]
        
        # 计算 ATR
        atr = self.calculate(prices, current_price)
        
        # 计算近期高低点
        recent_high = max(prices[-period:]) if len(prices) >= period else max(prices)
        recent_low = min(prices[-period:]) if len(prices) >= period else min(prices)
        
        # 计算突破临界价格
        # 向上突破临界
        bullish_breakout = recent_high + atr * breakout_mult
        
        # 向下突破临界
        bearish_breakout = recent_low - atr * breakout_mult
        
        # 止损价格（基于当前价格）
        stop_loss_long = current_price - atr * stop_mult  # 多头止损
        stop_loss_short = current_price + atr * stop_mult  # 空头止损
        
        # 计算当前波动率等级
        price_range = recent_high - recent_low
        if price_range == 0:
            volatility_pct = 0
        else:
            volatility_pct = (atr / price_range) * 100
        
        # 确定当前状态
        if current_price > recent_high:
            zone = "breaking_out_up"
        elif current_price < recent_low:
            zone = "breaking_out_down"
        else:
            zone = "ranging"
        
        # ATR 没有传统意义的看涨/看跌价格，而是提供波动率参考
        # 看涨价格 = 突破上方阻力位
        # 看跌价格 = 跌破下方支撑位
        
        return TriggerResult(
            indicator_name=self.name,
            current_value=atr,
            current_price=current_price,
            bullish_trigger_price=bullish_breakout,
            bearish_trigger_price=bearish_breakout,
            zone=zone,
            metadata={
                "atr": round(atr, 4),
                "atr_percent": round((atr / current_price) * 100, 2),
                "recent_high": round(recent_high, 2),
                "recent_low": round(recent_low, 2),
                "stop_loss_long": round(stop_loss_long, 2),
                "stop_loss_short": round(stop_loss_short, 2),
                "breakout_up": round(bullish_breakout, 2),
                "breakout_down": round(bearish_breakout, 2),
            }
        )
    
    def simulate(self, prices: List[float], hypothetical_price: float) -> SimulationResult:
        """压力测试"""
        period = self.params["period"]
        
        # 计算假设价格下的 ATR
        atr = self.calculate(prices, hypothetical_price)
        
        # 计算假设的波动率
        volatility_pct = (atr / hypothetical_price) * 100 if hypothetical_price > 0 else 0
        
        recent_high = max(prices[-period:]) if len(prices) >= period else max(prices)
        recent_low = min(prices[-period:]) if len(prices) >= period else min(prices)
        
        # 判断突破状态
        if hypothetical_price > recent_high:
            zone = "breakout_up"
            is_bullish = True
        elif hypothetical_price < recent_low:
            zone = "breakout_down"
            is_bearish = True
        else:
            zone = "ranging"
            is_bullish = False
            is_bearish = False
        
        return SimulationResult(
            hypothetical_price=hypothetical_price,
            indicator_value=atr,
            zone=zone,
            is_bullish=is_bullish,
            is_bearish=is_bearish,
            metadata={
                "atr": round(atr, 4),
                "volatility_pct": round(volatility_pct, 2),
                "daily_range": round(atr * 2, 2),  # 预计日波动范围
            }
        )
