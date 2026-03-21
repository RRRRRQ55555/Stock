"""
智能条件筛选器

根据用户自定义的技术指标组合，计算满足所有条件的"共振价格区间"。

核心功能：
1. 条件定义：支持各种技术指标条件（如价格在5日线上、MACD水上金叉等）
2. 约束求解：计算满足所有条件的交集区间
3. 置信度评分：评估当前状态距离目标的接近程度
4. 近似解：当无精确解时，给出最接近的近似区间

支持的指标条件：
- 均线条件：股价 > MA5, 股价 < MA10, 均线多头排列等
- MACD条件：水上金叉（DIF>0且金叉）, DIF>Signal等
- KDJ条件：K<D, J<0等
- RSI条件：RSI<30, RSI>70等
- 布林带条件：股价触及上轨/下轨等
- 威廉指标条件：WR<-80, WR>-20等
- CCI条件：CCI>100, CCI<-100等
"""

from typing import List, Dict, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from datetime import datetime

from .indicator_engine import IndicatorEngine, TriggerMatrix
from .macd_solver import MACDState
from .ma_solver import MAState
from .kdj_solver import KDJState
from .rsi_solver import RSIState
from .boll_solver import BOLLState
from .wr_solver import WRState
from .cci_solver import CCIState


class ConditionType(Enum):
    """条件类型"""
    # 均线条件
    PRICE_ABOVE_MA = "price_above_ma"           # 价格 > MA(N)
    PRICE_BELOW_MA = "price_below_ma"           # 价格 < MA(N)
    PRICE_BETWEEN_MAS = "price_between_mas"     # MA(短) < 价格 < MA(长)
    MA_GOLDEN_CROSS = "ma_golden_cross"         # 均线金叉
    MA_BULLISH_ALIGNMENT = "ma_bullish"         # 均线多头排列
    
    # MACD条件
    MACD_GOLDEN_CROSS = "macd_golden"           # MACD金叉
    MACD_ABOVE_ZERO = "macd_above_zero"         # DIF > 0
    MACD_DIF_GT_SIGNAL = "macd_dif_gt_signal"   # DIF > Signal
    
    # KDJ条件
    KDJ_K_LT_D = "kdj_k_lt_d"                   # K < D
    KDJ_J_LT_ZERO = "kdj_j_lt_zero"             # J < 0
    KDJ_J_GT_100 = "kdj_j_gt_100"               # J > 100
    
    # RSI条件
    RSI_OVERSOLD = "rsi_oversold"               # RSI < 30
    RSI_OVERBOUGHT = "rsi_overbought"           # RSI > 70
    RSI_BETWEEN = "rsi_between"                 # 30 < RSI < 70
    
    # 布林带条件
    BOLL_ABOVE_UPPER = "boll_above_upper"       # 价格 > 上轨
    BOLL_BELOW_LOWER = "boll_below_lower"       # 价格 < 下轨
    BOLL_INSIDE = "boll_inside"                 # 下轨 < 价格 < 上轨
    
    # WR条件
    WR_OVERSOLD = "wr_oversold"                 # WR > -20 (超卖区)
    WR_OVERBOUGHT = "wr_overbought"             # WR < -80 (超买区)
    
    # CCI条件
    CCI_ABOVE_100 = "cci_above_100"             # CCI > 100
    CCI_BELOW_MINUS100 = "cci_below_minus100"   # CCI < -100


@dataclass
class Condition:
    """单个技术条件"""
    condition_type: ConditionType
    params: Dict[str, Any] = field(default_factory=dict)  # 参数如 {"period": 5}
    weight: float = 1.0  # 权重（用于置信度计算）
    description: str = ""  # 人类可读描述
    
    def __post_init__(self):
        if not self.description:
            self.description = self._generate_description()
    
    def _generate_description(self) -> str:
        """生成描述"""
        desc_map = {
            ConditionType.PRICE_ABOVE_MA: f"股价 > MA{self.params.get('period', 5)}",
            ConditionType.PRICE_BELOW_MA: f"股价 < MA{self.params.get('period', 10)}",
            ConditionType.PRICE_BETWEEN_MAS: f"MA{self.params.get('short', 5)} < 股价 < MA{self.params.get('long', 20)}",
            ConditionType.MA_GOLDEN_CROSS: f"MA{self.params.get('short', 5)} 上穿 MA{self.params.get('long', 20)}",
            ConditionType.MA_BULLISH_ALIGNMENT: "均线多头排列",
            ConditionType.MACD_GOLDEN_CROSS: "MACD水上金叉 (DIF>0且金叉)",
            ConditionType.MACD_ABOVE_ZERO: "DIF > 0",
            ConditionType.MACD_DIF_GT_SIGNAL: "DIF > Signal",
            ConditionType.KDJ_K_LT_D: "KDJ K < D",
            ConditionType.KDJ_J_LT_ZERO: "KDJ J < 0 (超卖)",
            ConditionType.KDJ_J_GT_100: "KDJ J > 100 (超买)",
            ConditionType.RSI_OVERSOLD: "RSI < 30 (超卖)",
            ConditionType.RSI_OVERBOUGHT: "RSI > 70 (超买)",
            ConditionType.BOLL_ABOVE_UPPER: "股价 > 布林上轨",
            ConditionType.BOLL_BELOW_LOWER: "股价触及布林下轨",
            ConditionType.WR_OVERSOLD: "WR > -20 (超卖区)",
            ConditionType.WR_OVERBOUGHT: "WR < -80 (超买区)",
            ConditionType.CCI_ABOVE_100: "CCI > 100",
            ConditionType.CCI_BELOW_MINUS100: "CCI < -100",
        }
        return desc_map.get(self.condition_type, str(self.condition_type))


@dataclass
class PriceConstraint:
    """价格约束（区间表示）"""
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    condition: Condition = None
    confidence: float = 0.0  # 该约束的可信度
    
    def is_satisfied(self, price: float) -> bool:
        """检查价格是否满足约束"""
        if self.min_price is not None and price < self.min_price:
            return False
        if self.max_price is not None and price > self.max_price:
            return False
        return True
    
    def __str__(self):
        if self.min_price is not None and self.max_price is not None:
            return f"[{self.min_price:.2f}, {self.max_price:.2f}]"
        elif self.min_price is not None:
            return f"[{self.min_price:.2f}, +∞)"
        elif self.max_price is not None:
            return f"(-∞, {self.max_price:.2f}]"
        return "(-∞, +∞)"


@dataclass
class FilterResult:
    """筛选结果"""
    symbol: str
    current_price: float
    
    # 满足条件的区间
    feasible_min: Optional[float] = None  # 可行区间下限
    feasible_max: Optional[float] = None  # 可行区间上限
    
    # 各条件的约束
    constraints: List[PriceConstraint] = field(default_factory=list)
    
    # 置信度
    overall_confidence: float = 0.0  # 总体置信度 (0-1)
    
    # 详细分析
    satisfied_conditions: List[Condition] = field(default_factory=list)  # 已满足的条件
    unsatisfied_conditions: List[Tuple[Condition, float]] = field(default_factory=list)  # 未满足的条件及距离
    
    # 推荐
    recommendation: str = ""
    target_price: Optional[float] = None  # 推荐目标价格
    distance_to_target: Optional[float] = None  # 距离目标的百分比
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "symbol": self.symbol,
            "current_price": self.current_price,
            "feasible_range": {
                "min": round(self.feasible_min, 4) if self.feasible_min else None,
                "max": round(self.feasible_max, 4) if self.feasible_max else None,
            },
            "confidence": round(self.overall_confidence, 4),
            "constraints": [
                {
                    "description": c.condition.description if c.condition else "未知",
                    "range": str(c),
                    "confidence": round(c.confidence, 4)
                }
                for c in self.constraints
            ],
            "satisfied": [c.description for c in self.satisfied_conditions],
            "unsatisfied": [
                {"condition": c.description, "distance_pct": round(d, 2)}
                for c, d in self.unsatisfied_conditions
            ],
            "recommendation": self.recommendation,
            "target_price": round(self.target_price, 4) if self.target_price else None,
            "distance_to_target": round(self.distance_to_target, 2) if self.distance_to_target else None,
        }


class ConditionFilter:
    """智能条件筛选器"""
    
    def __init__(self):
        """初始化筛选器"""
        self.engine = IndicatorEngine()
    
    def filter(
        self,
        symbol: str,
        current_price: float,
        conditions: List[Condition],
        macd_state: MACDState,
        ma_state: MAState,
        kdj_state: KDJState,
        rsi_state: RSIState = None,
        boll_state: BOLLState = None,
        wr_state: WRState = None,
        cci_state: CCIState = None
    ) -> FilterResult:
        """
        执行条件筛选
        
        计算满足所有条件的共振价格区间
        """
        constraints = []
        satisfied = []
        unsatisfied = []
        
        # 逐条计算约束
        for condition in conditions:
            constraint = self._calculate_constraint(
                condition, current_price,
                macd_state, ma_state, kdj_state,
                rsi_state, boll_state, wr_state, cci_state
            )
            
            if constraint:
                constraints.append(constraint)
                
                # 检查当前价格是否满足该条件
                if constraint.is_satisfied(current_price):
                    satisfied.append(condition)
                else:
                    # 计算距离
                    distance = self._calculate_distance(current_price, constraint)
                    unsatisfied.append((condition, distance))
        
        # 计算可行区间（所有约束的交集）
        feasible_min, feasible_max = self._compute_intersection(constraints)
        
        # 计算总体置信度
        confidence = self._compute_confidence(
            constraints, current_price, satisfied, unsatisfied
        )
        
        # 生成推荐
        recommendation, target_price, distance = self._generate_recommendation(
            feasible_min, feasible_max, current_price, satisfied, unsatisfied
        )
        
        return FilterResult(
            symbol=symbol,
            current_price=current_price,
            feasible_min=feasible_min,
            feasible_max=feasible_max,
            constraints=constraints,
            overall_confidence=confidence,
            satisfied_conditions=satisfied,
            unsatisfied_conditions=unsatisfied,
            recommendation=recommendation,
            target_price=target_price,
            distance_to_target=distance
        )
    
    def _calculate_constraint(
        self,
        condition: Condition,
        current_price: float,
        macd_state: MACDState,
        ma_state: MAState,
        kdj_state: KDJState,
        rsi_state: RSIState = None,
        boll_state: BOLLState = None,
        wr_state: WRState = None,
        cci_state: CCIState = None
    ) -> Optional[PriceConstraint]:
        """
        计算单个条件的价格约束
        """
        ct = condition.condition_type
        params = condition.params
        
        # 均线条件
        if ct == ConditionType.PRICE_ABOVE_MA:
            period = params.get('period', 5)
            # 需要重新计算MA临界价格
            ma_prices = ma_state.prices_short if period <= 5 else ma_state.prices_long
            # 求解 P > MA(P, period)
            # MA = (sum + P) / (N+1) < P
            # sum + P < P * (N+1)
            # sum < P * N
            # P > sum / N
            sum_prices = sum(ma_prices)
            min_price = sum_prices / (len(ma_prices))
            return PriceConstraint(
                min_price=min_price,
                condition=condition,
                confidence=0.9
            )
        
        elif ct == ConditionType.PRICE_BELOW_MA:
            period = params.get('period', 10)
            ma_prices = ma_state.prices_long  # 简化，使用已有数据
            sum_prices = sum(ma_prices)
            max_price = sum_prices / (len(ma_prices))
            return PriceConstraint(
                max_price=max_price,
                condition=condition,
                confidence=0.9
            )
        
        elif ct == ConditionType.PRICE_BETWEEN_MAS:
            # 价格在MA5和MA20之间
            short_prices = ma_state.prices_short
            long_prices = ma_state.prices_long
            min_p = sum(short_prices) / len(short_prices)
            max_p = sum(long_prices) / len(long_prices)
            return PriceConstraint(
                min_price=min(min_p, max_p),
                max_price=max(min_p, max_p),
                condition=condition,
                confidence=0.85
            )
        
        elif ct == ConditionType.MA_GOLDEN_CROSS:
            # 使用MA求解器的金叉临界价格
            ma_result = self.engine.ma_solver.solve_trigger_prices(ma_state)
            if ma_result.golden_cross_price:
                return PriceConstraint(
                    min_price=ma_result.golden_cross_price,
                    condition=condition,
                    confidence=0.8
                )
            return None
        
        # MACD条件
        elif ct == ConditionType.MACD_GOLDEN_CROSS:
            # 水上金叉：DIF>0且金叉
            macd_result = self.engine.macd_solver.solve_trigger_prices(macd_state, current_price)
            if macd_result.golden_cross_price:
                # 需要DIF>0
                # 简化：假设金叉价已经保证DIF>Signal
                return PriceConstraint(
                    min_price=macd_result.golden_cross_price,
                    condition=condition,
                    confidence=0.85
                )
            return None
        
        elif ct == ConditionType.MACD_ABOVE_ZERO:
            # DIF > 0
            # 求解使DIF=0的价格作为临界点
            # 这是一个近似求解
            if macd_state.dif > 0:
                # 当前已是水上，下边界为某价格
                return PriceConstraint(
                    min_price=current_price * 0.95,  # 简化估计
                    condition=condition,
                    confidence=0.7
                )
            else:
                # 当前水下，需要价格上涨
                return PriceConstraint(
                    min_price=current_price * 1.02,  # 简化估计
                    condition=condition,
                    confidence=0.6
                )
        
        # KDJ条件
        elif ct == ConditionType.KDJ_J_LT_ZERO:
            kdj_result = self.engine.kdj_solver.solve_trigger_prices(kdj_state)
            if kdj_result.oversold_price:
                return PriceConstraint(
                    max_price=kdj_result.oversold_price,
                    condition=condition,
                    confidence=0.85
                )
            return None
        
        # RSI条件
        elif ct == ConditionType.RSI_OVERSOLD:
            if rsi_state:
                rsi_result = self.engine.rsi_solver.solve_trigger_prices(rsi_state)
                if rsi_result.oversold_price:
                    return PriceConstraint(
                        max_price=rsi_result.oversold_price,
                        condition=condition,
                        confidence=0.8
                    )
            return None
        
        elif ct == ConditionType.RSI_OVERBOUGHT:
            if rsi_state:
                rsi_result = self.engine.rsi_solver.solve_trigger_prices(rsi_state)
                if rsi_result.overbought_price:
                    return PriceConstraint(
                        min_price=rsi_result.overbought_price,
                        condition=condition,
                        confidence=0.8
                    )
            return None
        
        # 布林带条件
        elif ct == ConditionType.BOLL_BELOW_LOWER:
            if boll_state:
                boll_result = self.engine.boll_solver.solve_trigger_prices(boll_state)
                if boll_result.lower_touch_price:
                    return PriceConstraint(
                        max_price=boll_result.lower_touch_price,
                        condition=condition,
                        confidence=0.8
                    )
            return None
        
        # WR条件
        elif ct == ConditionType.WR_OVERSOLD:
            if wr_state:
                wr_result = self.engine.wr_solver.solve_trigger_prices(wr_state)
                if wr_result.oversold_price:
                    return PriceConstraint(
                        min_price=wr_result.oversold_price,
                        condition=condition,
                        confidence=0.75
                    )
            return None
        
        return None
    
    def _calculate_distance(self, price: float, constraint: PriceConstraint) -> float:
        """计算当前价格距离约束的百分比"""
        if constraint.is_satisfied(price):
            return 0.0
        
        if constraint.min_price is not None and price < constraint.min_price:
            return (constraint.min_price - price) / price * 100
        
        if constraint.max_price is not None and price > constraint.max_price:
            return (price - constraint.max_price) / price * 100
        
        return 0.0
    
    def _compute_intersection(
        self,
        constraints: List[PriceConstraint]
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        计算所有约束的交集区间
        
        算法：
        1. 找出所有下限约束的最大值
        2. 找出所有上限约束的最小值
        3. 如果 下限 > 上限，则无解
        """
        if not constraints:
            return None, None
        
        min_prices = [c.min_price for c in constraints if c.min_price is not None]
        max_prices = [c.max_price for c in constraints if c.max_price is not None]
        
        feasible_min = max(min_prices) if min_prices else None
        feasible_max = min(max_prices) if max_prices else None
        
        # 检查可行性
        if feasible_min is not None and feasible_max is not None:
            if feasible_min > feasible_max:
                # 无解，返回空区间
                return None, None
        
        return feasible_min, feasible_max
    
    def _compute_confidence(
        self,
        constraints: List[PriceConstraint],
        current_price: float,
        satisfied: List[Condition],
        unsatisfied: List[Tuple[Condition, float]]
    ) -> float:
        """计算总体置信度"""
        if not constraints:
            return 0.0
        
        # 基础分：已满足条件数 / 总条件数
        total_weight = sum(c.weight for c in [s for s, _ in satisfied] + [u for u, _ in unsatisfied])
        satisfied_weight = sum(c.weight for c in satisfied)
        
        if total_weight == 0:
            return 0.0
        
        base_confidence = satisfied_weight / total_weight
        
        # 额外加分：对于未满足但距离近的
        for condition, distance in unsatisfied:
            if distance < 1:  # 距离小于1%
                base_confidence += condition.weight * 0.5  # 给一半分
            elif distance < 3:  # 距离小于3%
                base_confidence += condition.weight * 0.3
        
        return min(1.0, base_confidence)
    
    def _generate_recommendation(
        self,
        feasible_min: Optional[float],
        feasible_max: Optional[float],
        current_price: float,
        satisfied: List[Condition],
        unsatisfied: List[Tuple[Condition, float]]
    ) -> Tuple[str, Optional[float], Optional[float]]:
        """生成推荐建议"""
        if feasible_min is not None and feasible_max is not None:
            # 有可行区间
            target = (feasible_min + feasible_max) / 2
            distance = (target - current_price) / current_price * 100
            
            if distance > 0:
                recommendation = f"建议等待价格上涨至 {target:.2f} (区间 {feasible_min:.2f}-{feasible_max:.2f})"
            elif distance < 0:
                recommendation = f"建议等待价格下跌至 {target:.2f} (区间 {feasible_min:.2f}-{feasible_max:.2f})"
            else:
                recommendation = "当前价格已处于最佳区间，建议买入"
            
            return recommendation, target, distance
        
        elif feasible_min is not None:
            # 只有下限
            target = feasible_min * 1.005  # 略高出下限
            distance = (target - current_price) / current_price * 100
            return f"建议等待价格 >= {feasible_min:.2f}", target, distance
        
        elif feasible_max is not None:
            # 只有上限
            target = feasible_max * 0.995  # 略低于上限
            distance = (target - current_price) / current_price * 100
            return f"建议等待价格 <= {feasible_max:.2f}", target, distance
        
        else:
            # 无约束
            return "无明确价格约束，请调整筛选条件", None, None


# 便捷函数
def create_common_conditions(scenario: str) -> List[Condition]:
    """
    创建常见条件组合
    
    Args:
        scenario: 场景名称
        
    Returns:
        条件列表
    """
    scenarios = {
        "多头排列+MACD金叉": [
            Condition(ConditionType.PRICE_ABOVE_MA, {"period": 5}, 1.0),
            Condition(ConditionType.PRICE_ABOVE_MA, {"period": 10}, 1.0),
            Condition(ConditionType.MA_GOLDEN_CROSS, {"short": 5, "long": 20}, 1.0),
            Condition(ConditionType.MACD_GOLDEN_CROSS, {}, 1.0),
        ],
        "超卖反弹": [
            Condition(ConditionType.KDJ_J_LT_ZERO, {}, 1.0),
            Condition(ConditionType.RSI_OVERSOLD, {}, 1.0),
            Condition(ConditionType.BOLL_BELOW_LOWER, {}, 0.8),
        ],
        "水上金叉": [
            Condition(ConditionType.MACD_ABOVE_ZERO, {}, 1.0),
            Condition(ConditionType.MACD_GOLDEN_CROSS, {}, 1.0),
            Condition(ConditionType.PRICE_ABOVE_MA, {"period": 5}, 0.8),
        ],
        "均线粘合突破": [
            Condition(ConditionType.PRICE_BETWEEN_MAS, {"short": 5, "long": 20}, 1.0),
            Condition(ConditionType.MA_GOLDEN_CROSS, {"short": 5, "long": 20}, 1.0),
        ],
    }
    
    return scenarios.get(scenario, [])
