"""
MACD 反向求解器

通过代数推导，计算触发 MACD 金叉/死叉所需的临界价格。

核心公式推导:
EMA(n)_today = P * α_n + EMA(n)_yest * (1 - α_n), 其中 α_n = 2/(n+1)
DIF = EMA(12) - EMA(26)
Signal = Signal_yest + α_9 * (DIF - Signal_yest)
金叉条件: DIF = Signal
"""

import numpy as np
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass


@dataclass
class MACDState:
    """MACD 昨日状态数据"""
    ema_12: float  # 12日EMA昨日值
    ema_26: float  # 26日EMA昨日值
    signal: float  # Signal线昨日值
    dif: float     # DIF昨日值 (用于验证)
    close: float   # 昨日收盘价 (用于验证)
    

@dataclass
class MACDTriggerResult:
    """MACD 临界价格计算结果"""
    golden_cross_price: Optional[float]  # 金叉临界价格
    death_cross_price: Optional[float]  # 死叉临界价格
    current_price: float                 # 当前价格
    dif_current: float                 # 当前DIF值
    signal_current: float              # 当前Signal值
    
    # 距离信息
    distance_to_golden: Optional[float] = None  # 距离金叉的百分比
    distance_to_death: Optional[float] = None   # 距离死叉的百分比
    
    def __post_init__(self):
        if self.golden_cross_price is not None and self.current_price > 0:
            self.distance_to_golden = (
                (self.golden_cross_price - self.current_price) / self.current_price * 100
            )
        if self.death_cross_price is not None and self.current_price > 0:
            self.distance_to_death = (
                (self.death_cross_price - self.current_price) / self.current_price * 100
            )


class MACDSolver:
    """MACD 反向求解器"""
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        """
        初始化 MACD 求解器
        
        Args:
            fast_period: 快线周期，默认12
            slow_period: 慢线周期，默认26
            signal_period: Signal线周期，默认9
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        
        # 计算EMA系数 α = 2/(n+1)
        self.alpha_fast = 2.0 / (fast_period + 1)
        self.alpha_slow = 2.0 / (slow_period + 1)
        self.alpha_signal = 2.0 / (signal_period + 1)
    
    def calculate_ema(self, previous_ema: float, price: float, period: int) -> float:
        """
        计算EMA值
        
        EMA_today = Price * α + EMA_yest * (1 - α)
        其中 α = 2/(period+1)
        """
        alpha = 2.0 / (period + 1)
        return price * alpha + previous_ema * (1 - alpha)
    
    def calculate_macd(self, state: MACDState, current_price: float) -> Tuple[float, float, float]:
        """
        计算当前价格下的 MACD 值
        
        Returns:
            (DIF, Signal, Histogram)
        """
        # 计算今日EMA
        ema_fast = self.calculate_ema(state.ema_12, current_price, self.fast_period)
        ema_slow = self.calculate_ema(state.ema_26, current_price, self.slow_period)
        
        # 计算DIF
        dif = ema_fast - ema_slow
        
        # 计算Signal线 (DIF的EMA)
        signal = state.signal + self.alpha_signal * (dif - state.signal)
        
        # 计算柱状图
        histogram = dif - signal
        
        return dif, signal, histogram
    
    def solve_golden_cross_price(self, state: MACDState) -> Optional[float]:
        """
        求解 MACD 金叉临界价格
        
        金叉条件: DIF = Signal
        
        推导过程:
        设 DIF = EMA12 - EMA26
        EMA12 = P * α12 + EMA12_yest * (1 - α12)
        EMA26 = P * α26 + EMA26_yest * (1 - α26)
        Signal = Signal_yest + α9 * (DIF - Signal_yest)
        
        金叉条件展开:
        DIF = Signal_yest + α9 * (DIF - Signal_yest)
        DIF = Signal_yest + α9 * DIF - α9 * Signal_yest
        DIF - α9 * DIF = Signal_yest * (1 - α9)
        DIF * (1 - α9) = Signal_yest * (1 - α9)
        DIF = Signal_yest  ... (这是金叉条件)
        
        然后:
        P * (α12 - α26) + EMA12_yest * (1 - α12) - EMA26_yest * (1 - α26) = Signal_yest
        
        求解 P:
        P = [Signal_yest - EMA12_yest * (1 - α12) + EMA26_yest * (1 - α26)] / (α12 - α26)
        
        Returns:
            金叉临界价格，如果无解返回 None
        """
        try:
            # 分母: α12 - α26
            denominator = self.alpha_fast - self.alpha_slow
            
            # 如果分母接近0，说明快慢周期相同，无意义
            if abs(denominator) < 1e-10:
                return None
            
            # 分子
            numerator = (
                state.signal 
                - state.ema_12 * (1 - self.alpha_fast) 
                + state.ema_26 * (1 - self.alpha_slow)
            )
            
            golden_price = numerator / denominator
            
            # 验证结果（价格必须为正）
            if golden_price <= 0:
                return None
            
            # 验证金叉方向：当前DIF < Signal，临界后 DIF >= Signal
            dif_current, signal_current, _ = self.calculate_macd(state, state.close)
            if dif_current >= signal_current:
                # 当前已经是金叉或平头状态，无需再求金叉价
                return None
            
            return golden_price
            
        except (ZeroDivisionError, ValueError):
            return None
    
    def solve_death_cross_price(self, state: MACDState) -> Optional[float]:
        """
        求解 MACD 死叉临界价格
        
        死叉条件: DIF = Signal (与金叉相同，但方向相反)
        
        返回的价格与金叉相同，但需要验证当前状态：
        - 当前 DIF > Signal 时，求解的价格会导致死叉
        - 当前 DIF < Signal 时，求解的价格会导致金叉
        
        Returns:
            死叉临界价格，如果无解返回 None
        """
        try:
            # 死叉的代数推导与金叉相同，只是方向相反
            denominator = self.alpha_fast - self.alpha_slow
            
            if abs(denominator) < 1e-10:
                return None
            
            numerator = (
                state.signal 
                - state.ema_12 * (1 - self.alpha_fast) 
                + state.ema_26 * (1 - self.alpha_slow)
            )
            
            death_price = numerator / denominator
            
            if death_price <= 0:
                return None
            
            # 验证死叉方向：当前DIF > Signal，临界后 DIF <= Signal
            dif_current, signal_current, _ = self.calculate_macd(state, state.close)
            if dif_current <= signal_current:
                # 当前已经是死叉或平头状态
                return None
            
            return death_price
            
        except (ZeroDivisionError, ValueError):
            return None
    
    def solve_trigger_prices(self, state: MACDState, current_price: float) -> MACDTriggerResult:
        """
        求解所有 MACD 临界价格
        
        Args:
            state: 昨日MACD状态
            current_price: 当前价格
            
        Returns:
            MACDTriggerResult 包含金叉/死叉临界价格及距离信息
        """
        # 计算当前DIF和Signal
        dif_current, signal_current, _ = self.calculate_macd(state, current_price)
        
        # 求解临界价格
        golden_price = None
        death_price = None
        
        # 根据当前DIF和Signal的关系决定哪个临界价格有效
        if dif_current < signal_current:
            # 当前处于空头，求金叉价格
            golden_price = self.solve_golden_cross_price(state)
        elif dif_current > signal_current:
            # 当前处于多头，求死叉价格
            death_price = self.solve_death_cross_price(state)
        else:
            # 当前平头，同时求两个方向的价格
            golden_price = self.solve_golden_cross_price(state)
            death_price = self.solve_death_cross_price(state)
        
        return MACDTriggerResult(
            golden_cross_price=golden_price,
            death_cross_price=death_price,
            current_price=current_price,
            dif_current=dif_current,
            signal_current=signal_current
        )
    
    def simulate_price(self, state: MACDState, hypothetical_price: float) -> dict:
        """
        压力测试：模拟在假设价格下的 MACD 状态
        
        Args:
            state: 昨日MACD状态
            hypothetical_price: 假设的今日价格
            
        Returns:
            包含DIF、Signal、Histogram及金叉/死叉状态的字典
        """
        dif, signal, histogram = self.calculate_macd(state, hypothetical_price)
        
        # 判断信号状态
        is_golden_cross = dif > signal
        is_death_cross = dif < signal
        
        # 计算距离金叉/死叉的差值
        diff_to_cross = abs(dif - signal)
        
        return {
            "hypothetical_price": hypothetical_price,
            "dif": round(dif, 4),
            "signal": round(signal, 4),
            "histogram": round(histogram, 4),
            "is_golden_cross": is_golden_cross,
            "is_death_cross": is_death_cross,
            "diff_to_cross": round(diff_to_cross, 4),
            "trend": "up" if dif > signal else "down" if dif < signal else "neutral"
        }


# 常用MACD参数组合
COMMON_MACD_SETS = [
    {"name": "标准MACD", "fast": 12, "slow": 26, "signal": 9, "desc": "经典参数，适合中长线"},
    {"name": "短线MACD", "fast": 6, "slow": 13, "signal": 5, "desc": "短线参数，信号更灵敏"},
    {"name": "长线MACD", "fast": 24, "slow": 52, "signal": 18, "desc": "长线参数，过滤噪音"},
    {"name": "超短线MACD", "fast": 3, "slow": 8, "signal": 3, "desc": "超短线，高频交易"},
]


@dataclass
class MultiMACDState:
    """多参数MACD状态"""
    states: Dict[str, MACDState]  # 不同参数组合的状态


@dataclass
class MultiMACDResult:
    """多参数MACD计算结果"""
    current_price: float
    results: Dict[str, MACDTriggerResult]
    best_params: Optional[str]  # 推荐的参数组合
    consensus_signal: str  # 综合信号 (bullish/bearish/neutral)


class MultiMACDSolver:
    """
    多参数MACD求解器
    
    同时计算多种参数组合下的MACD状态和临界价格
    """
    
    def __init__(self):
        """初始化多参数MACD求解器"""
        self.solvers = {}
        self._init_solvers()
    
    def _init_solvers(self):
        """初始化各参数组合的求解器"""
        for macd_set in COMMON_MACD_SETS:
            key = f"{macd_set['fast']},{macd_set['slow']},{macd_set['signal']}"
            self.solvers[key] = MACDSolver(
                fast_period=macd_set['fast'],
                slow_period=macd_set['slow'],
                signal_period=macd_set['signal']
            )
    
    def solve_all_params(
        self,
        price_data: Dict[str, float],  # 各周期EMA数据
        current_price: float,
        selected_params: List[str] = None
    ) -> MultiMACDResult:
        """
        计算所有参数组合的MACD触发价格
        
        Args:
            price_data: 包含各EMA周期的字典
            current_price: 当前价格
            selected_params: 指定参数组合，默认全部
            
        Returns:
            MultiMACDResult
        """
        results = {}
        golden_count = 0
        death_count = 0
        
        params_to_use = selected_params or list(self.solvers.keys())
        
        for param_key in params_to_use:
            if param_key not in self.solvers:
                continue
            
            solver = self.solvers[param_key]
            parts = param_key.split(',')
            fast_key = f"ema_{parts[0]}"
            slow_key = f"ema_{parts[1]}"
            signal_key = f"signal_{parts[2]}"
            
            if fast_key in price_data and slow_key in price_data and signal_key in price_data:
                state = MACDState(
                    ema_12=price_data[fast_key],
                    ema_26=price_data[slow_key],
                    signal=price_data[signal_key],
                    dif=price_data[fast_key] - price_data[slow_key],
                    close=price_data.get('close', current_price)
                )
                
                result = solver.solve_trigger_prices(state, current_price)
                results[param_key] = result
                
                # 统计信号
                if result.golden_cross_price is not None:
                    death_count += 1
                elif result.death_cross_price is not None:
                    golden_count += 1
        
        # 确定综合信号
        if golden_count > death_count:
            consensus = "bullish"
        elif death_count > golden_count:
            consensus = "bearish"
        else:
            consensus = "neutral"
        
        # 推荐参数组合
        best_params = self._recommend_params(results, consensus)
        
        return MultiMACDResult(
            current_price=current_price,
            results=results,
            best_params=best_params,
            consensus_signal=consensus
        )
    
    def _recommend_params(
        self,
        results: Dict[str, MACDTriggerResult],
        consensus: str
    ) -> Optional[str]:
        """根据结果推荐最佳参数组合"""
        if not results:
            return None
        
        # 优先推荐有明确信号的参数
        for param_key, result in results.items():
            if consensus == "bullish" and result.death_cross_price is not None:
                return param_key
            elif consensus == "bearish" and result.golden_cross_price is not None:
                return param_key
        
        # 否则返回第一个
        return list(results.keys())[0]
    
    def get_param_recommendation(
        self,
        trading_style: str  # "short" | "medium" | "long"
    ) -> Dict[str, any]:
        """根据交易风格推荐MACD参数"""
        recommendations = {
            "short": {
                "params": "6,13,5",
                "name": "短线MACD",
                "desc": "信号灵敏，适合日内或短线交易",
                "hold_time": "1-3天"
            },
            "medium": {
                "params": "12,26,9",
                "name": "标准MACD",
                "desc": "平衡灵敏度与稳定性，适合波段交易",
                "hold_time": "1-4周"
            },
            "long": {
                "params": "24,52,18",
                "name": "长线MACD",
                "desc": "过滤噪音，适合趋势跟踪",
                "hold_time": "1-6个月"
            }
        }
        
        return recommendations.get(trading_style, recommendations["medium"])


# 便捷的函数接口
def calculate_macd_trigger(
    ema_12: float,
    ema_26: float,
    signal: float,
    current_price: float,
    close_yesterday: float
) -> MACDTriggerResult:
    """
    便捷函数：计算 MACD 临界价格
    
    Args:
        ema_12: 12日EMA昨日值
        ema_26: 26日EMA昨日值
        signal: Signal线昨日值
        current_price: 当前价格
        close_yesterday: 昨日收盘价
        
    Returns:
        MACDTriggerResult
    """
    state = MACDState(
        ema_12=ema_12,
        ema_26=ema_26,
        signal=signal,
        dif=ema_12 - ema_26,  # 昨日DIF
        close=close_yesterday
    )
    
    solver = MACDSolver()
    return solver.solve_trigger_prices(state, current_price)


def simulate_macd_at_price(
    ema_12: float,
    ema_26: float,
    signal: float,
    hypothetical_price: float
) -> dict:
    """
    便捷函数：模拟 MACD 在假设价格下的状态
    
    Args:
        ema_12: 12日EMA昨日值
        ema_26: 26日EMA昨日值
        signal: Signal线昨日值
        hypothetical_price: 假设价格
        
    Returns:
        包含DIF、Signal等信息的字典
    """
    state = MACDState(
        ema_12=ema_12,
        ema_26=ema_26,
        signal=signal,
        dif=ema_12 - ema_26,
        close=hypothetical_price  # 这里传入假设价格作为昨日收盘，用于计算验证
    )
    
    solver = MACDSolver()
    return solver.simulate_price(state, hypothetical_price)


def calculate_multi_macd(
    price_data: Dict[str, float],
    current_price: float,
    selected_params: List[str] = None
) -> MultiMACDResult:
    """
    便捷函数：计算多参数MACD触发结果
    
    Args:
        price_data: 包含各EMA周期的字典
        current_price: 当前价格
        selected_params: 指定参数组合
        
    Returns:
        MultiMACDResult
    """
    solver = MultiMACDSolver()
    return solver.solve_all_params(price_data, current_price, selected_params)
