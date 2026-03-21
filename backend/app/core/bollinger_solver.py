"""
布林带 (Bollinger Bands) 反向求解器

布林带由三条线组成：
- 中轨 (Middle Band) = N日简单移动平均线 (SMA)
- 上轨 (Upper Band) = 中轨 + K × N日标准差
- 下轨 (Lower Band) = 中轨 - K × N日标准差

常用参数：N=20, K=2
"""

import numpy as np
from typing import List, Optional
from .base_solver import BaseSolver, TriggerResult, SimulationResult, IndicatorRegistry


@IndicatorRegistry.register
class BollingerSolver(BaseSolver):
    """布林带反向求解器"""
    
    name = "bollinger"
    display_name = "布林带 (Bollinger Bands)"
    description = "基于移动平均线和标准差，判断价格超买超卖和波动率"
    
    default_params = {
        "period": 20,  # 计算周期
        "std_dev": 2,  # 标准差倍数
    }
    
    def get_required_history_length(self) -> int:
        return self.params["period"]
    
    def calculate_bands(
        self,
        prices: List[float],
        current_price: float
    ) -> tuple:
        """
        计算布林带三条线
        
        Returns:
            (upper, middle, lower, bandwidth, percent_b)
        """
        period = self.params["period"]
        std_dev_mult = self.params["std_dev"]
        
        # 包含当前价格的完整序列
        full_prices = np.array(prices[-period+1:] + [current_price])
        
        if len(full_prices) < period:
            # 数据不足，使用简单计算
            middle = np.mean(prices + [current_price])
            std_dev = np.std(prices + [current_price])
        else:
            middle = np.mean(full_prices)
            std_dev = np.std(full_prices)
        
        upper = middle + std_dev_mult * std_dev
        lower = middle - std_dev_mult * std_dev
        
        # %B 指标 (价格在布林带中的位置)
        if upper == lower:
            percent_b = 0.5
        else:
            percent_b = (current_price - lower) / (upper - lower)
        
        # 带宽 (带宽收窄预示大行情)
        bandwidth = (upper - lower) / middle if middle != 0 else 0
        
        return upper, middle, lower, bandwidth, percent_b
    
    def calculate(self, prices: List[float], current_price: float) -> float:
        """返回 %B 值作为指标值"""
        _, _, _, _, percent_b = self.calculate_bands(prices, current_price)
        return float(percent_b * 100)  # 转为百分比
    
    def solve_trigger_prices(
        self,
        prices: List[float],
        current_price: float
    ) -> TriggerResult:
        """
        求解布林带临界价格
        
        触及上轨 = 超买/回调信号
        触及下轨 = 超卖/反弹信号
        """
        upper, middle, lower, bandwidth, percent_b = self.calculate_bands(
            prices, current_price
        )
        
        period = self.params["period"]
        
        # 计算触及上轨的价格（看跌触发）
        # upper = SMA + K*STD = target
        # 设新价格 P，求解 SMA_new 和 STD_new
        # 近似：SMA_new ≈ (SMA_old * (N-1) + P) / N
        # STD_new 会随 P 变化
        bearish_price = self._solve_for_upper_band(prices, period)
        
        # 计算触及下轨的价格（看涨触发）
        bullish_price = self._solve_for_lower_band(prices, period)
        
        # 确定当前位置
        if current_price >= upper:
            zone = "overbought"
        elif current_price <= lower:
            zone = "oversold"
        else:
            zone = "neutral"
        
        return TriggerResult(
            indicator_name=self.name,
            current_value=percent_b * 100,
            current_price=current_price,
            bullish_trigger_price=bullish_price,
            bearish_trigger_price=bearish_price,
            zone=zone,
            metadata={
                "upper_band": round(upper, 2),
                "middle_band": round(middle, 2),
                "lower_band": round(lower, 2),
                "bandwidth": round(bandwidth * 100, 2),  # 带宽百分比
                "period": period,
            }
        )
    
    def _solve_for_upper_band(
        self,
        prices: List[float],
        period: int
    ) -> Optional[float]:
        """
        求解触及上轨的价格
        
        使用数值方法求解
        """
        current_mean = np.mean(prices[-period+1:])
        
        # 搜索范围：当前均值到均值+20%
        low, high = current_mean, current_mean * 1.2
        target_std_dev = self.params["std_dev"]
        
        for _ in range(50):
            mid = (low + high) / 2
            test_prices = prices[-period+1:] + [mid]
            new_mean = np.mean(test_prices)
            new_std = np.std(test_prices)
            
            # 上轨位置
            upper = new_mean + target_std_dev * new_std
            
            if abs(mid - upper) < 0.01:
                return round(mid, 2)
            
            if mid < upper:
                low = mid
            else:
                high = mid
        
        return round((low + high) / 2, 2)
    
    def _solve_for_lower_band(
        self,
        prices: List[float],
        period: int
    ) -> Optional[float]:
        """求解触及下轨的价格"""
        current_mean = np.mean(prices[-period+1:])
        
        # 搜索范围：均值-20%到当前均值
        low, high = current_mean * 0.8, current_mean
        target_std_dev = self.params["std_dev"]
        
        for _ in range(50):
            mid = (low + high) / 2
            test_prices = prices[-period+1:] + [mid]
            new_mean = np.mean(test_prices)
            new_std = np.std(test_prices)
            
            # 下轨位置
            lower = new_mean - target_std_dev * new_std
            
            if abs(mid - lower) < 0.01:
                return round(mid, 2)
            
            if mid > lower:
                high = mid
            else:
                low = mid
        
        return round((low + high) / 2, 2)
    
    def simulate(self, prices: List[float], hypothetical_price: float) -> SimulationResult:
        """压力测试"""
        upper, middle, lower, bandwidth, percent_b = self.calculate_bands(
            prices, hypothetical_price
        )
        
        if hypothetical_price >= upper:
            zone = "overbought"
        elif hypothetical_price <= lower:
            zone = "oversold"
        else:
            zone = "neutral"
        
        return SimulationResult(
            hypothetical_price=hypothetical_price,
            indicator_value=percent_b * 100,
            zone=zone,
            is_bullish=hypothetical_price <= lower,  # 触及下轨看涨
            is_bearish=hypothetical_price >= upper,  # 触及上轨看跌
            metadata={
                "upper": round(upper, 2),
                "middle": round(middle, 2),
                "lower": round(lower, 2),
                "percent_b": round(percent_b * 100, 2),
            }
        )
