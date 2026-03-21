"""
均线交叉反向求解器

通过代数推导，计算触发均线金叉/死叉所需的临界价格。

核心公式:
MA(N)_today = (SUM(Close[-N+1:0]) + P) / N

金叉条件 (MA_short > MA_long):
(SUM_S_short + P) / N_short > (SUM_S_long + P) / N_long

通过解这个不等式找到临界价格 P
"""

import numpy as np
from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class MAState:
    """均线昨日状态"""
    prices_short: List[float]  # 短期均线所需的历史价格 (N-1个)
    prices_long: List[float]   # 长期均线所需的历史价格 (N-1个)
    short_period: int
    long_period: int
    current_price: float


@dataclass
class MATriggerResult:
    """均线临界价格计算结果"""
    golden_cross_price: Optional[float]  # 金叉临界价格 (短期上穿长期)
    death_cross_price: Optional[float]   # 死叉临界价格 (短期下穿长期)
    current_price: float
    ma_short_current: float
    ma_long_current: float
    
    # 距离信息
    distance_to_golden: Optional[float] = None
    distance_to_death: Optional[float] = None
    
    # 当前状态
    is_bullish: bool = False  # 多头排列 (MA_short > MA_long)
    
    def __post_init__(self):
        self.is_bullish = self.ma_short_current > self.ma_long_current
        
        if self.golden_cross_price is not None and self.current_price > 0:
            self.distance_to_golden = (
                (self.golden_cross_price - self.current_price) / self.current_price * 100
            )
        if self.death_cross_price is not None and self.current_price > 0:
            self.distance_to_death = (
                (self.death_cross_price - self.current_price) / self.current_price * 100
            )


class MASolver:
    """均线交叉反向求解器"""
    
    def __init__(self, short_period: int = 5, long_period: int = 10):
        """
        初始化均线求解器
        
        Args:
            short_period: 短期均线周期，默认5日
            long_period: 长期均线周期，默认10日
        """
        self.short_period = short_period
        self.long_period = long_period
    
    def calculate_ma(self, prices: List[float], new_price: float, period: int) -> float:
        """
        计算MA值
        
        MA = (sum(prices) + new_price) / period
        其中 prices 是前 (period-1) 个收盘价
        
        Args:
            prices: 前(period-1)日的收盘价列表
            new_price: 今日的收盘价
            period: 均线周期
            
        Returns:
            MA值
        """
        if len(prices) != period - 1:
            raise ValueError(f"需要 {period-1} 个历史价格，但收到 {len(prices)} 个")
        
        return (sum(prices) + new_price) / period
    
    def solve_golden_cross_price(self, state: MAState) -> Optional[float]:
        """
        求解均线金叉临界价格 (短期均线上穿长期均线)
        
        推导过程:
        MA_short = (SUM_S_short + P) / N_short
        MA_long = (SUM_S_long + P) / N_long
        
        金叉条件: MA_short >= MA_long
        (SUM_S_short + P) / N_short >= (SUM_S_long + P) / N_long
        
        两边同乘 N_short * N_long:
        (SUM_S_short + P) * N_long >= (SUM_S_long + P) * N_short
        SUM_S_short * N_long + P * N_long >= SUM_S_long * N_short + P * N_short
        P * N_long - P * N_short >= SUM_S_long * N_short - SUM_S_short * N_long
        P * (N_long - N_short) >= SUM_S_long * N_short - SUM_S_short * N_long
        
        因为 N_long > N_short，所以:
        P >= (SUM_S_long * N_short - SUM_S_short * N_long) / (N_long - N_short)
        
        临界价格 P_critical = (SUM_S_long * N_short - SUM_S_short * N_long) / (N_long - N_short)
        
        Returns:
            金叉临界价格，如果无解返回 None
        """
        try:
            sum_short = sum(state.prices_short)
            sum_long = sum(state.prices_long)
            
            n_short = state.short_period
            n_long = state.long_period
            
            # 分母
            denominator = n_long - n_short
            
            if denominator <= 0:
                return None  # 长期周期必须大于短期周期
            
            # 分子
            numerator = sum_long * n_short - sum_short * n_long
            
            critical_price = numerator / denominator
            
            # 验证：价格必须为正
            if critical_price <= 0:
                return None
            
            # 验证金叉方向
            ma_short_current = self.calculate_ma(state.prices_short, state.current_price, n_short)
            ma_long_current = self.calculate_ma(state.prices_long, state.current_price, n_long)
            
            if ma_short_current >= ma_long_current:
                # 当前已经是金叉或平头状态
                return None
            
            return critical_price
            
        except (ZeroDivisionError, ValueError):
            return None
    
    def solve_death_cross_price(self, state: MAState) -> Optional[float]:
        """
        求解均线死叉临界价格 (短期均线下穿长期均线)
        
        死叉条件: MA_short <= MA_long
        代数推导与金叉相同，临界价格相同，只是方向判断相反
        
        Returns:
            死叉临界价格，如果无解返回 None
        """
        try:
            sum_short = sum(state.prices_short)
            sum_long = sum(state.prices_long)
            
            n_short = state.short_period
            n_long = state.long_period
            
            denominator = n_long - n_short
            
            if denominator <= 0:
                return None
            
            numerator = sum_long * n_short - sum_short * n_long
            critical_price = numerator / denominator
            
            if critical_price <= 0:
                return None
            
            # 验证死叉方向
            ma_short_current = self.calculate_ma(state.prices_short, state.current_price, n_short)
            ma_long_current = self.calculate_ma(state.prices_long, state.current_price, n_long)
            
            if ma_short_current <= ma_long_current:
                # 当前已经是死叉或平头状态
                return None
            
            return critical_price
            
        except (ZeroDivisionError, ValueError):
            return None
    
    def solve_trigger_prices(self, state: MAState) -> MATriggerResult:
        """
        求解均线交叉临界价格
        
        Args:
            state: 均线状态数据
            
        Returns:
            MATriggerResult 包含金叉/死叉临界价格
        """
        # 计算当前MA值
        ma_short = self.calculate_ma(state.prices_short, state.current_price, state.short_period)
        ma_long = self.calculate_ma(state.prices_long, state.current_price, state.long_period)
        
        # 根据当前状态决定求解哪个临界价格
        golden_price = None
        death_price = None
        
        if ma_short < ma_long:
            # 当前空头排列，求解金叉价格
            golden_price = self.solve_golden_cross_price(state)
        elif ma_short > ma_long:
            # 当前多头排列，求解死叉价格
            death_price = self.solve_death_cross_price(state)
        else:
            # 当前均线粘合，两个方向的价格都有效
            # 金叉价格 = 死叉价格 (在均线粘合点)
            try:
                sum_short = sum(state.prices_short)
                sum_long = sum(state.prices_long)
                n_short = state.short_period
                n_long = state.long_period
                critical = (sum_long * n_short - sum_short * n_long) / (n_long - n_short)
                if critical > 0:
                    golden_price = death_price = critical
            except:
                pass
        
        return MATriggerResult(
            golden_cross_price=golden_price,
            death_cross_price=death_price,
            current_price=state.current_price,
            ma_short_current=ma_short,
            ma_long_current=ma_long
        )
    
    def simulate_price(self, state: MAState, hypothetical_price: float) -> dict:
        """
        压力测试：模拟在假设价格下的均线状态
        
        Args:
            state: 均线状态
            hypothetical_price: 假设价格
            
        Returns:
            包含MA值和金叉/死叉状态的字典
        """
        ma_short = self.calculate_ma(state.prices_short, hypothetical_price, state.short_period)
        ma_long = self.calculate_ma(state.prices_long, hypothetical_price, state.long_period)
        
        diff = ma_short - ma_long
        
        return {
            "hypothetical_price": hypothetical_price,
            "ma_short": round(ma_short, 4),
            "ma_long": round(ma_long, 4),
            "diff": round(diff, 4),
            "is_golden_cross": ma_short > ma_long,
            "is_death_cross": ma_short < ma_long,
            "is_aligned": abs(diff) < 0.01,  # 均线粘合
            "trend": "bullish" if ma_short > ma_long else "bearish" if ma_short < ma_long else "neutral"
        }


# 常用均线周期组合
COMMON_MA_PAIRS = [
    {"name": "MA5-MA10", "short": 5, "long": 10, "desc": "短线多空"},
    {"name": "MA5-MA20", "short": 5, "long": 20, "desc": "短线趋势"},
    {"name": "MA10-MA20", "short": 10, "long": 20, "desc": "中线多空"},
    {"name": "MA10-MA30", "short": 10, "long": 30, "desc": "中线趋势"},
    {"name": "MA20-MA60", "short": 20, "long": 60, "desc": "中长线"},
    {"name": "MA30-MA60", "short": 30, "long": 60, "desc": "长线多空"},
]

# 常用单条均线
COMMON_MA_PERIODS = [
    {"name": "MA5", "period": 5, "desc": "攻击线"},
    {"name": "MA10", "period": 10, "desc": "操盘线"},
    {"name": "MA20", "period": 20, "desc": "生命线"},
    {"name": "MA30", "period": 30, "desc": "趋势线"},
    {"name": "MA60", "period": 60, "desc": "决策线"},
    {"name": "MA120", "period": 120, "desc": "半年线"},
    {"name": "MA250", "period": 250, "desc": "年线"},
]


@dataclass
class MultiMATriggerResult:
    """多周期均线触发结果"""
    current_price: float
    ma_values: Dict[int, float]  # 各周期MA当前值
    pair_results: Dict[str, MATriggerResult]  # 各组合的触发结果
    overall_trend: str  # 总体趋势判断
    alignment_score: float  # 均线粘合度 (0-1)


class MultiMASolver:
    """
    多周期均线求解器
    
    同时计算5/10/20/30/60/120/250日均线的状态
    支持多组均线组合的交叉临界价格计算
    """
    
    def __init__(self, periods: List[int] = None):
        """
        初始化多周期均线求解器
        
        Args:
            periods: 均线周期列表，默认 [5, 10, 20, 30, 60]
        """
        self.periods = periods or [5, 10, 20, 30, 60]
        self.solvers = {}
        self._init_solvers()
    
    def _init_solvers(self):
        """初始化各组合的求解器"""
        for pair in COMMON_MA_PAIRS:
            key = f"MA{pair['short']}-MA{pair['long']}"
            self.solvers[key] = MASolver(pair['short'], pair['long'])
    
    def solve_all_periods(
        self,
        price_history: List[float],
        current_price: float
    ) -> MultiMATriggerResult:
        """
        计算所有周期的均线状态和触发价格
        
        Args:
            price_history: 历史价格数据（至少250日用于计算年线）
            current_price: 当前价格
            
        Returns:
            MultiMATriggerResult
        """
        ma_values = {}
        pair_results = {}
        
        # 计算各周期MA值
        for period in self.periods:
            if len(price_history) >= period - 1:
                prices = price_history[-(period-1):] if period > 1 else []
                ma = (sum(prices) + current_price) / period
                ma_values[period] = ma
        
        # 计算各组合的触发价格
        for pair in COMMON_MA_PAIRS:
            short_p, long_p = pair['short'], pair['long']
            key = f"MA{short_p}-MA{long_p}"
            
            if short_p in ma_values and long_p in ma_values:
                # 构建状态
                short_prices = price_history[-(short_p-1):] if short_p > 1 else []
                long_prices = price_history[-(long_p-1):] if long_p > 1 else []
                
                state = MAState(
                    prices_short=short_prices,
                    prices_long=long_prices,
                    short_period=short_p,
                    long_period=long_p,
                    current_price=current_price
                )
                
                result = self.solvers[key].solve_trigger_prices(state)
                pair_results[key] = result
        
        # 计算总体趋势
        overall_trend = self._calculate_overall_trend(ma_values)
        
        # 计算均线粘合度
        alignment_score = self._calculate_alignment(ma_values)
        
        return MultiMATriggerResult(
            current_price=current_price,
            ma_values=ma_values,
            pair_results=pair_results,
            overall_trend=overall_trend,
            alignment_score=alignment_score
        )
    
    def _calculate_overall_trend(self, ma_values: Dict[int, float]) -> str:
        """根据多条均线位置判断总体趋势"""
        if len(ma_values) < 3:
            return "unknown"
        
        # 计算短期均线在价格上方还是下方
        short_ma = ma_values.get(5, 0)
        long_ma = ma_values.get(60, ma_values.get(30, 0))
        
        if short_ma > long_ma * 1.1:
            return "strong_bullish"
        elif short_ma > long_ma:
            return "bullish"
        elif short_ma < long_ma * 0.9:
            return "strong_bearish"
        elif short_ma < long_ma:
            return "bearish"
        else:
            return "neutral"
    
    def _calculate_alignment(self, ma_values: Dict[int, float]) -> float:
        """计算均线粘合度 (0-1，值越大粘合越紧密)"""
        if len(ma_values) < 2:
            return 0.0
        
        values = list(ma_values.values())
        if len(values) == 0:
            return 0.0
        
        max_val = max(values)
        min_val = min(values)
        avg_val = sum(values) / len(values)
        
        if avg_val == 0:
            return 0.0
        
        # 粘合度 = 1 - (最大差 / 平均值)
        alignment = 1 - (max_val - min_val) / avg_val
        return max(0.0, min(1.0, alignment))
    
    def get_best_cross_pair(self, ma_values: Dict[int, float]) -> Optional[str]:
        """根据当前价格位置推荐最佳的均线组合"""
        if 5 in ma_values and 10 in ma_values:
            diff_5_10 = abs(ma_values[5] - ma_values[10])
            if diff_5_10 / ma_values[5] < 0.02:  # 5%以内
                return "MA5-MA10"
        
        if 10 in ma_values and 20 in ma_values:
            diff_10_20 = abs(ma_values[10] - ma_values[20])
            if diff_10_20 / ma_values[10] < 0.03:  # 3%以内
                return "MA10-MA20"
        
        if 20 in ma_values and 60 in ma_values:
            return "MA20-MA60"
        
        return None


# 便捷的函数接口
def calculate_ma_trigger(
    prices_short: List[float],
    prices_long: List[float],
    current_price: float,
    short_period: int = 5,
    long_period: int = 10
) -> MATriggerResult:
    """
    便捷函数：计算均线交叉临界价格
    
    Args:
        prices_short: 短期均线所需的历史价格 (short_period-1个)
        prices_long: 长期均线所需的历史价格 (long_period-1个)
        current_price: 当前价格
        short_period: 短期均线周期
        long_period: 长期均线周期
        
    Returns:
        MATriggerResult
    """
    state = MAState(
        prices_short=prices_short,
        prices_long=prices_long,
        short_period=short_period,
        long_period=long_period,
        current_price=current_price
    )
    
    solver = MASolver(short_period, long_period)
    return solver.solve_trigger_prices(state)


def simulate_ma_at_price(
    prices_short: List[float],
    prices_long: List[float],
    hypothetical_price: float,
    short_period: int = 5,
    long_period: int = 10
) -> dict:
    """
    便捷函数：模拟均线在假设价格下的状态
    
    Args:
        prices_short: 短期均线所需历史价格
        prices_long: 长期均线所需历史价格
        hypothetical_price: 假设价格
        short_period: 短期均线周期
        long_period: 长期均线周期
        
    Returns:
        包含MA值等信息的字典
    """
    state = MAState(
        prices_short=prices_short,
        prices_long=prices_long,
        short_period=short_period,
        long_period=long_period,
        current_price=hypothetical_price
    )
    
    solver = MASolver(short_period, long_period)
    return solver.simulate_price(state, hypothetical_price)


def calculate_multi_ma_triggers(
    price_history: List[float],
    current_price: float,
    periods: List[int] = None
) -> MultiMATriggerResult:
    """
    便捷函数：计算多周期均线触发结果
    
    Args:
        price_history: 历史价格数据
        current_price: 当前价格
        periods: 均线周期列表，默认 [5, 10, 20, 30, 60]
        
    Returns:
        MultiMATriggerResult
    """
    solver = MultiMASolver(periods)
    return solver.solve_all_periods(price_history, current_price)
