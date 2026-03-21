"""
KDJ 反向求解器

通过代数推导，计算触发 KDJ 超买/超卖信号所需的临界价格。

核心公式:
RSV = (Close - L9) / (H9 - L9) * 100
K = 2/3 * K_yest + 1/3 * RSV
D = 2/3 * D_yest + 1/3 * K
J = 3K - 2D

超卖条件: J <= 0 (极度超卖)
超买条件: J >= 100 (极度超买)
"""

import numpy as np
from typing import Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class KDJState:
    """KDJ 昨日状态"""
    k_yest: float      # K值昨日收盘值
    d_yest: float      # D值昨日收盘值
    h9: float         # 9日最高价
    l9: float         # 9日最低价
    current_price: float
    
    def __post_init__(self):
        # 确保 H9 >= L9
        if self.h9 < self.l9:
            self.h9, self.l9 = self.l9, self.h9


@dataclass
class KDJTriggerResult:
    """KDJ 临界价格计算结果"""
    oversold_price: Optional[float]   # 超卖临界价格 (J <= 0)
    overbought_price: Optional[float]  # 超买临界价格 (J >= 100)
    current_price: float
    k_current: float
    d_current: float
    j_current: float
    
    # 距离信息
    distance_to_oversold: Optional[float] = None
    distance_to_overbought: Optional[float] = None
    
    # 区域判断
    zone: str = "neutral"  # oversold, neutral, overbought
    
    def __post_init__(self):
        if self.j_current <= 0:
            self.zone = "oversold"
        elif self.j_current >= 100:
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


class KDJolver:
    """KDJ 反向求解器"""
    
    def __init__(self, period: int = 9, k_smooth: float = 1/3, d_smooth: float = 1/3):
        """
        初始化 KDJ 求解器
        
        Args:
            period: RSV计算周期，默认9日
            k_smooth: K值平滑系数，默认1/3
            d_smooth: D值平滑系数，默认1/3
        """
        self.period = period
        self.k_alpha = k_smooth  # K的权重系数
        self.d_alpha = d_smooth  # D的权重系数
    
    def calculate_kdj(self, state: KDJState, close_price: float) -> Tuple[float, float, float]:
        """
        计算 KDJ 值
        
        Args:
            state: KDJ状态
            close_price: 今日收盘价
            
        Returns:
            (K, D, J) 三个值
        """
        # 计算RSV
        # RSV = (Close - L9) / (H9 - L9) * 100
        
        if state.h9 == state.l9:
            # 如果最高价等于最低价，避免除零
            rsv = 50.0
        else:
            rsv = (close_price - state.l9) / (state.h9 - state.l9) * 100
            # 限制RSV在0-100范围内
            rsv = max(0, min(100, rsv))
        
        # 计算K值: K = (1 - α) * K_yest + α * RSV
        # 标准公式: K = 2/3 * K_yest + 1/3 * RSV
        k = (1 - self.k_alpha) * state.k_yest + self.k_alpha * rsv
        
        # 计算D值: D = (1 - β) * D_yest + β * K
        # 标准公式: D = 2/3 * D_yest + 1/3 * K
        d = (1 - self.d_alpha) * state.d_yest + self.d_alpha * k
        
        # 计算J值: J = 3K - 2D
        j = 3 * k - 2 * d
        
        return k, d, j
    
    def solve_oversold_price(self, state: KDJState) -> Optional[float]:
        """
        求解 KDJ 超卖临界价格 (J <= 0)
        
        推导过程:
        条件: J <= 0
        J = 3K - 2D <= 0
        => K <= (2/3)D
        
        代入:
        K = (1-α)K_yest + α * RSV
        D = (1-β)D_yest + β * K
        
        先表达D关于RSV:
        D = (1-β)D_yest + β[(1-α)K_yest + α * RSV]
        D = (1-β)D_yest + β(1-α)K_yest + βα * RSV
        
        然后J关于RSV:
        J = 3[(1-α)K_yest + α * RSV] - 2[(1-β)D_yest + β(1-α)K_yest + βα * RSV]
        J = 3(1-α)K_yest + 3α * RSV - 2(1-β)D_yest - 2β(1-α)K_yest - 2βα * RSV
        J = [3(1-α) - 2β(1-α)]K_yest - 2(1-β)D_yest + [3α - 2βα]RSV
        J = (1-α)(3-2β)K_yest - 2(1-β)D_yest + α(3-2β)RSV
        
        令 J = 0:
        α(3-2β)RSV = 2(1-β)D_yest - (1-α)(3-2β)K_yest
        RSV = [2(1-β)D_yest - (1-α)(3-2β)K_yest] / [α(3-2β)]
        
        然后:
        (P - L9) / (H9 - L9) * 100 = RSV
        P = L9 + (H9 - L9) * RSV / 100
        
        Returns:
            超卖临界价格，如果无解返回 None
        """
        try:
            alpha = self.k_alpha
            beta = self.d_alpha
            
            # 计算临界RSV (使 J = 0 的RSV值)
            # RSV_oversold = [2(1-β)D_yest - (1-α)(3-2β)K_yest] / [α(3-2β)]
            
            denominator = alpha * (3 - 2 * beta)
            
            if abs(denominator) < 1e-10:
                return None
            
            numerator = (
                2 * (1 - beta) * state.d_yest 
                - (1 - alpha) * (3 - 2 * beta) * state.k_yest
            )
            
            rsv_critical = numerator / denominator
            
            # RSV限制在0-100范围
            # 如果临界RSV超出这个范围，说明在当前周期内无法达到该状态
            if rsv_critical < 0 or rsv_critical > 100:
                # 扩展到理论价格，不限于0-100
                pass
            
            # 计算临界价格
            # RSV = (P - L9) / (H9 - L9) * 100
            if state.h9 == state.l9:
                # 如果最高价等于最低价，价格就是该值
                return state.l9
            
            oversold_price = state.l9 + (state.h9 - state.l9) * rsv_critical / 100
            
            # 验证结果
            if oversold_price <= 0:
                return None
            
            # 验证方向：当前J > 0，临界后 J <= 0
            k_current, d_current, j_current = self.calculate_kdj(state, state.current_price)
            if j_current <= 0:
                # 当前已经是超卖状态
                return None
            
            return oversold_price
            
        except (ZeroDivisionError, ValueError):
            return None
    
    def solve_overbought_price(self, state: KDJState) -> Optional[float]:
        """
        求解 KDJ 超买临界价格 (J >= 100)
        
        推导过程:
        条件: J >= 100
        3K - 2D >= 100
        
        同样推导:
        RSV = [100 + 2(1-β)D_yest - (1-α)(3-2β)K_yest] / [α(3-2β)]
        
        P = L9 + (H9 - L9) * RSV / 100
        
        Returns:
            超买临界价格，如果无解返回 None
        """
        try:
            alpha = self.k_alpha
            beta = self.d_alpha
            
            denominator = alpha * (3 - 2 * beta)
            
            if abs(denominator) < 1e-10:
                return None
            
            # J = 100 时的临界RSV
            numerator = (
                100 
                + 2 * (1 - beta) * state.d_yest 
                - (1 - alpha) * (3 - 2 * beta) * state.k_yest
            )
            
            rsv_critical = numerator / denominator
            
            # 计算临界价格
            if state.h9 == state.l9:
                return state.l9
            
            overbought_price = state.l9 + (state.h9 - state.l9) * rsv_critical / 100
            
            if overbought_price <= 0:
                return None
            
            # 验证方向
            k_current, d_current, j_current = self.calculate_kdj(state, state.current_price)
            if j_current >= 100:
                # 当前已经是超买状态
                return None
            
            return overbought_price
            
        except (ZeroDivisionError, ValueError):
            return None
    
    def solve_trigger_prices(self, state: KDJState) -> KDJTriggerResult:
        """
        求解 KDJ 超买/超卖临界价格
        
        Args:
            state: KDJ状态
            
        Returns:
            KDJTriggerResult 包含超买/超卖临界价格
        """
        # 计算当前KDJ值
        k_current, d_current, j_current = self.calculate_kdj(state, state.current_price)
        
        # 根据当前状态求解
        oversold_price = None
        overbought_price = None
        
        if j_current > 0:
            # 当前非超卖，求解超卖价格
            oversold_price = self.solve_oversold_price(state)
        
        if j_current < 100:
            # 当前非超买，求解超买价格
            overbought_price = self.solve_overbought_price(state)
        
        return KDJTriggerResult(
            oversold_price=oversold_price,
            overbought_price=overbought_price,
            current_price=state.current_price,
            k_current=k_current,
            d_current=d_current,
            j_current=j_current
        )
    
    def simulate_price(self, state: KDJState, hypothetical_price: float) -> dict:
        """
        压力测试：模拟在假设价格下的 KDJ 状态
        
        Args:
            state: KDJ状态
            hypothetical_price: 假设价格
            
        Returns:
            包含K、D、J值及超买/超卖状态的字典
        """
        k, d, j = self.calculate_kdj(state, hypothetical_price)
        
        return {
            "hypothetical_price": hypothetical_price,
            "k": round(k, 4),
            "d": round(d, 4),
            "j": round(j, 4),
            "is_oversold": j <= 0,
            "is_overbought": j >= 100,
            "rsv": round(
                (hypothetical_price - state.l9) / (state.h9 - state.l9) * 100 
                if state.h9 != state.l9 else 50, 4
            ),
            "zone": "oversold" if j <= 0 else "overbought" if j >= 100 else "neutral"
        }
    
    def calculate_rsi_like_zones(self, state: KDJState, current_price: float) -> dict:
        """
        计算类似RSI的多个关键区域
        
        返回:
            - J <= 0: 极度超卖
            - J <= 20: 超卖区
            - 20 < J < 80: 震荡区
            - J >= 80: 超买区
            - J >= 100: 极度超买
        """
        result = self.solve_trigger_prices(state)
        
        zones = {
            "current_j": result.j_current,
            "oversold_price": result.oversold_price,  # J = 0
            "overbought_price": result.overbought_price,  # J = 100
            "zone": result.zone,
        }
        
        # 计算 J = 20 和 J = 80 的临界价格（可选）
        try:
            alpha = self.k_alpha
            beta = self.d_alpha
            denominator = alpha * (3 - 2 * beta)
            
            if abs(denominator) > 1e-10:
                # J = 20
                numerator_20 = (
                    20 
                    + 2 * (1 - beta) * state.d_yest 
                    - (1 - alpha) * (3 - 2 * beta) * state.k_yest
                )
                rsv_20 = numerator_20 / denominator
                price_20 = state.l9 + (state.h9 - state.l9) * rsv_20 / 100
                zones["j20_price"] = price_20 if price_20 > 0 else None
                
                # J = 80
                numerator_80 = (
                    80 
                    + 2 * (1 - beta) * state.d_yest 
                    - (1 - alpha) * (3 - 2 * beta) * state.k_yest
                )
                rsv_80 = numerator_80 / denominator
                price_80 = state.l9 + (state.h9 - state.l9) * rsv_80 / 100
                zones["j80_price"] = price_80 if price_80 > 0 else None
        except:
            pass
        
        return zones


# 便捷的函数接口
def calculate_kdj_trigger(
    k_yest: float,
    d_yest: float,
    h9: float,
    l9: float,
    current_price: float
) -> KDJTriggerResult:
    """
    便捷函数：计算 KDJ 临界价格
    
    Args:
        k_yest: K值昨日收盘值
        d_yest: D值昨日收盘值
        h9: 9日最高价
        l9: 9日最低价
        current_price: 当前价格
        
    Returns:
        KDJTriggerResult
    """
    state = KDJState(
        k_yest=k_yest,
        d_yest=d_yest,
        h9=h9,
        l9=l9,
        current_price=current_price
    )
    
    solver = KDJolver()
    return solver.solve_trigger_prices(state)


def simulate_kdj_at_price(
    k_yest: float,
    d_yest: float,
    h9: float,
    l9: float,
    hypothetical_price: float
) -> dict:
    """
    便捷函数：模拟 KDJ 在假设价格下的状态
    
    Args:
        k_yest: K值昨日收盘值
        d_yest: D值昨日收盘值
        h9: 9日最高价
        l9: 9日最低价
        hypothetical_price: 假设价格
        
    Returns:
        包含K、D、J值等信息的字典
    """
    state = KDJState(
        k_yest=k_yest,
        d_yest=d_yest,
        h9=h9,
        l9=l9,
        current_price=hypothetical_price
    )
    
    solver = KDJolver()
    return solver.simulate_price(state, hypothetical_price)
