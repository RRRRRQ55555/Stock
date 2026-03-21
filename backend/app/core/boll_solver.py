"""
布林带 (BOLL) 反向求解器

布林带由三条轨道组成：
- 中轨 (MB): N日简单移动平均线
- 上轨 (UP): 中轨 + k × 标准差
- 下轨 (DN): 中轨 - k × 标准差

通常 N=20, k=2

触顶上轨：价格可能回调
触底下轨：价格可能反弹
"""

import numpy as np
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class BOLLState:
    """布林带昨日状态"""
    prices: List[float]  # 最近N-1日的收盘价
    period: int = 20
    k: float = 2.0  # 标准差倍数
    current_price: float = 0.0


@dataclass
class BOLLTriggerResult:
    """布林带临界价格计算结果"""
    upper_touch_price: Optional[float]   # 触及上轨临界价格
    lower_touch_price: Optional[float]   # 触及下轨临界价格
    current_price: float
    mb_current: float  # 当前中轨
    up_current: float  # 当前上轨
    dn_current: float  # 当前下轨
    
    # 距离信息
    distance_to_upper: Optional[float] = None
    distance_to_lower: Optional[float] = None
    
    # 位置判断
    position: str = "inside"  # above_upper, inside, below_lower
    
    def __post_init__(self):
        if self.current_price > self.up_current:
            self.position = "above_upper"
        elif self.current_price < self.dn_current:
            self.position = "below_lower"
        else:
            self.position = "inside"
        
        if self.upper_touch_price is not None and self.current_price > 0:
            self.distance_to_upper = (
                (self.upper_touch_price - self.current_price) / self.current_price * 100
            )
        if self.lower_touch_price is not None and self.current_price > 0:
            self.distance_to_lower = (
                (self.lower_touch_price - self.current_price) / self.current_price * 100
            )


class BOLLSolver:
    """布林带反向求解器"""
    
    def __init__(self, period: int = 20, k: float = 2.0):
        """
        初始化布林带求解器
        
        Args:
            period: 计算周期，默认20
            k: 标准差倍数，默认2.0
        """
        self.period = period
        self.k = k
    
    def calculate_boll(self, state: BOLLState, close_price: float) -> tuple:
        """
        计算布林带值
        
        Returns:
            (中轨, 上轨, 下轨)
        """
        # 计算中轨 (MA)
        all_prices = state.prices + [close_price]
        mb = sum(all_prices) / len(all_prices)
        
        # 计算标准差
        variance = sum((p - mb) ** 2 for p in all_prices) / len(all_prices)
        std = np.sqrt(variance)
        
        # 计算上轨和下轨
        up = mb + self.k * std
        dn = mb - self.k * std
        
        return mb, up, dn
    
    def _solve_upper_touch_price(self, state: BOLLState) -> Optional[float]:
        """
        求解触及上轨的临界价格
        
        推导：
        当价格触及上轨时：P = MB + k × STD
        
        设 P 为未知数，则：
        MB = (SUM(prices) + P) / N
        STD = sqrt(Σ(Pi - MB)² / N)
        
        这是一个非线性方程，使用数值方法近似求解
        
        简化方法：
        假设价格P对MA的影响较小，先估算MA，再求解
        """
        try:
            if len(state.prices) != self.period - 1:
                return None
            
            prev_close = state.current_price
            sum_prices = sum(state.prices)
            
            # 迭代求解
            # 初始估计：假设 P ≈ 当前MA + k × 当前STD
            current_ma = sum_prices / len(state.prices)
            current_variance = sum((p - current_ma) ** 2 for p in state.prices) / len(state.prices)
            current_std = np.sqrt(current_variance)
            
            p_estimate = current_ma + self.k * current_std * 1.5  # 粗略估计
            
            # 迭代优化
            for _ in range(10):  # 最多10次迭代
                # 计算新的MA和STD
                new_ma = (sum_prices + p_estimate) / self.period
                variance = (sum((p - new_ma) ** 2 for p in state.prices) + (p_estimate - new_ma) ** 2) / self.period
                new_std = np.sqrt(variance)
                
                # 目标：P = MA + k × STD
                target_p = new_ma + self.k * new_std
                
                # 如果收敛，返回结果
                if abs(target_p - p_estimate) < 0.001:
                    return round(target_p, 4)
                
                # 更新估计值
                p_estimate = target_p
            
            return round(p_estimate, 4) if p_estimate > 0 else None
            
        except (ZeroDivisionError, ValueError):
            return None
    
    def _solve_lower_touch_price(self, state: BOLLState) -> Optional[float]:
        """
        求解触及下轨的临界价格
        
        推导类似上轨，但方向相反：
        P = MB - k × STD
        """
        try:
            if len(state.prices) != self.period - 1:
                return None
            
            prev_close = state.current_price
            sum_prices = sum(state.prices)
            
            # 初始估计
            current_ma = sum_prices / len(state.prices)
            current_variance = sum((p - current_ma) ** 2 for p in state.prices) / len(state.prices)
            current_std = np.sqrt(current_variance)
            
            p_estimate = current_ma - self.k * current_std * 1.5
            
            # 迭代优化
            for _ in range(10):
                new_ma = (sum_prices + p_estimate) / self.period
                variance = (sum((p - new_ma) ** 2 for p in state.prices) + (p_estimate - new_ma) ** 2) / self.period
                new_std = np.sqrt(variance)
                
                target_p = new_ma - self.k * new_std
                
                if abs(target_p - p_estimate) < 0.001:
                    return round(target_p, 4)
                
                p_estimate = target_p
            
            return round(p_estimate, 4) if p_estimate > 0 else None
            
        except (ZeroDivisionError, ValueError):
            return None
    
    def solve_trigger_prices(self, state: BOLLState) -> BOLLTriggerResult:
        """
        求解布林带临界价格
        
        Args:
            state: 布林带状态
            
        Returns:
            BOLLTriggerResult 包含上轨/下轨临界价格
        """
        # 计算当前布林带值
        mb, up, dn = self.calculate_boll(state, state.current_price)
        
        # 根据当前位置求解
        upper_price = None
        lower_price = None
        
        if state.current_price < up:
            # 当前未触及上轨，求解上轨临界
            upper_price = self._solve_upper_touch_price(state)
        
        if state.current_price > dn:
            # 当前未触及下轨，求解下轨临界
            lower_price = self._solve_lower_touch_price(state)
        
        return BOLLTriggerResult(
            upper_touch_price=upper_price,
            lower_touch_price=lower_price,
            current_price=state.current_price,
            mb_current=mb,
            up_current=up,
            dn_current=dn
        )
    
    def simulate_price(self, state: BOLLState, hypothetical_price: float) -> dict:
        """
        压力测试：模拟在假设价格下的布林带状态
        
        Args:
            state: 布林带状态
            hypothetical_price: 假设价格
            
        Returns:
            包含布林带值及位置状态的字典
        """
        mb, up, dn = self.calculate_boll(state, hypothetical_price)
        
        return {
            "hypothetical_price": hypothetical_price,
            "mb": round(mb, 4),
            "up": round(up, 4),
            "dn": round(dn, 4),
            "bandwidth": round((up - dn) / mb * 100, 2),  # 带宽百分比
            "is_above_upper": hypothetical_price > up,
            "is_below_lower": hypothetical_price < dn,
            "position": "above" if hypothetical_price > up else "below" if hypothetical_price < dn else "inside"
        }


# 便捷的函数接口
def calculate_boll_trigger(
    prices: List[float],
    current_price: float,
    period: int = 20,
    k: float = 2.0
) -> BOLLTriggerResult:
    """
    便捷函数：计算布林带临界价格
    
    Args:
        prices: 最近N-1日的收盘价
        current_price: 当前价格
        period: 周期
        k: 标准差倍数
        
    Returns:
        BOLLTriggerResult
    """
    state = BOLLState(
        prices=prices,
        period=period,
        k=k,
        current_price=current_price
    )
    
    solver = BOLLSolver(period, k)
    return solver.solve_trigger_prices(state)


def simulate_boll_at_price(
    prices: List[float],
    hypothetical_price: float,
    period: int = 20,
    k: float = 2.0
) -> dict:
    """
    便捷函数：模拟布林带在假设价格下的状态
    
    Args:
        prices: 最近N-1日的收盘价
        hypothetical_price: 假设价格
        period: 周期
        k: 标准差倍数
        
    Returns:
        包含布林带值等信息的字典
    """
    state = BOLLState(
        prices=prices,
        period=period,
        k=k,
        current_price=hypothetical_price
    )
    
    solver = BOLLSolver(period, k)
    return solver.simulate_price(state, hypothetical_price)
