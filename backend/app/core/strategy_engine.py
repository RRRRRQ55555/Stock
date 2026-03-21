"""
交易策略引擎

帮助用户维持交易策略，自动计算：
1. 符合入场条件的今日价格区间
2. 符合止损条件的触发价格
3. 策略执行状态跟踪

核心概念：
- 入场策略：技术指标组合满足时的买入区间
- 止损策略：技术指标组合满足时的卖出价格
- 每日检查：自动计算今日策略可行性
"""

from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, date
import json

from .condition_filter import ConditionFilter, Condition, ConditionType
from .indicator_engine import IndicatorEngine
from .macd_solver import MACDState
from .ma_solver import MAState
from .kdj_solver import KDJState
from .rsi_solver import RSIState
from .boll_solver import BOLLState
from .wr_solver import WRState
from .cci_solver import CCIState


class StrategyStatus(Enum):
    """策略状态"""
    PENDING = "pending"          # 等待入场
    ENTRY_READY = "entry_ready"  # 今日可入场（给出区间）
    ENTERED = "entered"          # 已入场
    STOP_LOSS = "stop_loss"      # 已触发止损
    TAKE_PROFIT = "take_profit"  # 已触发止盈
    EXPIRED = "expired"          # 已过期


class StrategyType(Enum):
    """策略类型"""
    LONG = "long"    # 做多
    SHORT = "short"  # 做空（暂不实现）


@dataclass
class EntryCondition:
    """入场条件"""
    conditions: List[Condition]
    description: str = ""  # 人类可读描述
    
    def __post_init__(self):
        if not self.description:
            self.description = " + ".join([c.description for c in self.conditions])


@dataclass
class StopLossCondition:
    """止损条件"""
    conditions: List[Condition]
    description: str = ""  # 人类可读描述
    fixed_price: Optional[float] = None  # 固定止损价格（优先于技术指标）
    fixed_pct: Optional[float] = None    # 固定止损百分比（如 -5%）
    
    def __post_init__(self):
        if not self.description:
            if self.fixed_price:
                self.description = f"固定止损: ¥{self.fixed_price:.2f}"
            elif self.fixed_pct:
                self.description = f"百分比止损: {self.fixed_pct}%"
            else:
                self.description = "技术止损: " + " + ".join([c.description for c in self.conditions])


@dataclass
class TakeProfitCondition:
    """止盈条件（可选）"""
    conditions: List[Condition] = field(default_factory=list)
    description: str = ""
    fixed_price: Optional[float] = None
    fixed_pct: Optional[float] = None
    r_ratio: Optional[float] = None  # 盈亏比（如 2R）


@dataclass
class TradingStrategy:
    """交易策略"""
    id: str
    name: str
    symbol: str
    
    # 条件 (必须字段在前)
    entry: EntryCondition = field(default_factory=lambda: EntryCondition(conditions=[]))
    stop_loss: StopLossCondition = field(default_factory=lambda: StopLossCondition(conditions=[]))
    
    # 可选字段
    type: StrategyType = StrategyType.LONG
    take_profit: Optional[TakeProfitCondition] = None
    
    # 状态
    status: StrategyStatus = StrategyStatus.PENDING
    entry_price: Optional[float] = None      # 实际入场价格
    entry_date: Optional[date] = None          # 入场日期
    stop_loss_price: Optional[float] = None    # 实际止损价格
    take_profit_price: Optional[float] = None  # 实际止盈价格
    
    # 创建时间
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # 备注
    notes: str = ""


@dataclass
class StrategyCheckResult:
    """策略检查结果"""
    strategy_id: str
    symbol: str
    current_price: float
    check_date: date
    
    # 入场分析
    can_enter_today: bool
    entry_price_min: Optional[float] = None    # 今日可入场最低价
    entry_price_max: Optional[float] = None    # 今日可入场最高价
    entry_confidence: float = 0.0              # 入场置信度
    entry_distance_pct: Optional[float] = None  # 距离入场区间的百分比
    
    # 止损分析
    stop_loss_price: Optional[float] = None    # 止损触发价格
    stop_loss_distance_pct: Optional[float] = None  # 距离止损的百分比
    
    # 止盈分析
    take_profit_price: Optional[float] = None  # 止盈目标价格
    take_profit_distance_pct: Optional[float] = None
    
    # 综合建议
    recommendation: str = ""
    risk_reward_ratio: Optional[float] = None  # 盈亏比
    
    # 详细分析
    entry_constraints: List[Dict] = field(default_factory=list)
    stop_loss_constraints: List[Dict] = field(default_factory=list)


class StrategyEngine:
    """交易策略引擎"""
    
    def __init__(self):
        self.condition_filter = ConditionFilter()
        self.indicator_engine = IndicatorEngine()
    
    def create_strategy(
        self,
        name: str,
        symbol: str,
        entry_conditions: List[Condition],
        stop_loss_conditions: List[Condition],
        take_profit_conditions: Optional[List[Condition]] = None,
        notes: str = ""
    ) -> TradingStrategy:
        """
        创建交易策略
        
        Args:
            name: 策略名称
            symbol: 股票代码
            entry_conditions: 入场条件列表
            stop_loss_conditions: 止损条件列表
            take_profit_conditions: 止盈条件列表（可选）
            notes: 备注
            
        Returns:
            TradingStrategy
        """
        import uuid
        
        strategy = TradingStrategy(
            id=str(uuid.uuid4())[:8],
            name=name,
            symbol=symbol,
            entry=EntryCondition(conditions=entry_conditions),
            stop_loss=StopLossCondition(conditions=stop_loss_conditions),
            take_profit=TakeProfitCondition(conditions=take_profit_conditions or []) if take_profit_conditions else None,
            notes=notes
        )
        
        return strategy
    
    def check_strategy(
        self,
        strategy: TradingStrategy,
        current_price: float,
        macd_state: MACDState,
        ma_state: MAState,
        kdj_state: KDJState,
        rsi_state: Optional[RSIState] = None,
        boll_state: Optional[BOLLState] = None,
        wr_state: Optional[WRState] = None,
        cci_state: Optional[CCIState] = None
    ) -> StrategyCheckResult:
        """
        检查策略状态
        
        计算：
        1. 今日是否能入场（给出价格区间）
        2. 止损触发价格
        3. 综合建议
        """
        today = date.today()
        
        # 1. 检查入场条件
        entry_result = self.condition_filter.filter(
            symbol=strategy.symbol,
            current_price=current_price,
            conditions=strategy.entry.conditions,
            macd_state=macd_state,
            ma_state=ma_state,
            kdj_state=kdj_state,
            rsi_state=rsi_state,
            boll_state=boll_state,
            wr_state=wr_state,
            cci_state=cci_state
        )
        
        can_enter = entry_result.feasible_min is not None or entry_result.feasible_max is not None
        
        # 2. 检查止损条件
        stop_loss_price = None
        stop_loss_distance = None
        
        # 优先使用固定止损
        if strategy.stop_loss.fixed_price:
            stop_loss_price = strategy.stop_loss.fixed_price
            stop_loss_distance = (stop_loss_price - current_price) / current_price * 100
        elif strategy.stop_loss.fixed_pct and strategy.status == StrategyStatus.ENTERED:
            # 只有已入场才计算百分比止损
            if strategy.entry_price:
                stop_loss_price = strategy.entry_price * (1 + strategy.stop_loss.fixed_pct / 100)
                stop_loss_distance = (stop_loss_price - current_price) / current_price * 100
        else:
            # 技术止损
            stop_result = self.condition_filter.filter(
                symbol=strategy.symbol,
                current_price=current_price,
                conditions=strategy.stop_loss.conditions,
                macd_state=macd_state,
                ma_state=ma_state,
                kdj_state=kdj_state,
                rsi_state=rsi_state,
                boll_state=boll_state,
                wr_state=wr_state,
                cci_state=cci_state
            )
            # 止损价格使用可行区间的边界
            if stop_result.feasible_min is not None:
                stop_loss_price = stop_result.feasible_min
                stop_loss_distance = (stop_loss_price - current_price) / current_price * 100
        
        # 3. 计算止盈价格
        take_profit_price = None
        take_profit_distance = None
        
        if strategy.take_profit:
            if strategy.take_profit.fixed_price:
                take_profit_price = strategy.take_profit.fixed_price
                take_profit_distance = (take_profit_price - current_price) / current_price * 100
            elif strategy.take_profit.fixed_pct and strategy.status == StrategyStatus.ENTERED:
                if strategy.entry_price:
                    take_profit_price = strategy.entry_price * (1 + strategy.take_profit.fixed_pct / 100)
                    take_profit_distance = (take_profit_price - current_price) / current_price * 100
            elif strategy.take_profit.r_ratio and strategy.stop_loss_price:
                # 根据盈亏比计算
                risk = abs(strategy.entry_price - strategy.stop_loss_price) if strategy.entry_price else 0
                reward = risk * strategy.take_profit.r_ratio
                take_profit_price = strategy.entry_price + reward if strategy.entry_price else None
                if take_profit_price:
                    take_profit_distance = (take_profit_price - current_price) / current_price * 100
        
        # 4. 计算盈亏比
        risk_reward = None
        if entry_result.feasible_max and stop_loss_price and take_profit_price:
            entry_avg = (entry_result.feasible_min + entry_result.feasible_max) / 2 if entry_result.feasible_min else entry_result.feasible_max
            risk = abs(entry_avg - stop_loss_price)
            reward = abs(take_profit_price - entry_avg)
            if risk > 0:
                risk_reward = reward / risk
        
        # 5. 生成建议
        recommendation = self._generate_recommendation(
            strategy, can_enter, entry_result, stop_loss_price, take_profit_price, risk_reward
        )
        
        # 6. 计算距离
        entry_distance = None
        if can_enter and entry_result.feasible_min and entry_result.feasible_max:
            entry_avg = (entry_result.feasible_min + entry_result.feasible_max) / 2
            entry_distance = (entry_avg - current_price) / current_price * 100
        
        return StrategyCheckResult(
            strategy_id=strategy.id,
            symbol=strategy.symbol,
            current_price=current_price,
            check_date=today,
            can_enter_today=can_enter,
            entry_price_min=entry_result.feasible_min,
            entry_price_max=entry_result.feasible_max,
            entry_confidence=entry_result.overall_confidence,
            entry_distance_pct=entry_distance,
            stop_loss_price=stop_loss_price,
            stop_loss_distance_pct=stop_loss_distance,
            take_profit_price=take_profit_price,
            take_profit_distance_pct=take_profit_distance,
            recommendation=recommendation,
            risk_reward_ratio=risk_reward,
            entry_constraints=entry_result.to_dict().get("constraints", []),
            stop_loss_constraints=[]
        )
    
    def _generate_recommendation(
        self,
        strategy: TradingStrategy,
        can_enter: bool,
        entry_result,
        stop_loss_price: Optional[float],
        take_profit_price: Optional[float],
        risk_reward: Optional[float]
    ) -> str:
        """生成交易建议"""
        if strategy.status == StrategyStatus.ENTERED:
            # 已入场，关注止损/止盈
            if stop_loss_price and strategy.entry_price:
                if strategy.entry_price > stop_loss_price:
                    # 多头止损
                    return f"已入场，止损价¥{stop_loss_price:.2f}，建议严格执行止损"
            return "已入场，关注止损/止盈条件"
        
        # 未入场
        if can_enter:
            if entry_result.feasible_min and entry_result.feasible_max:
                if risk_reward and risk_reward >= 2:
                    return f"今日可入场！区间¥{entry_result.feasible_min:.2f}-¥{entry_result.feasible_max:.2f}，盈亏比{risk_reward:.1f}:1（优秀）"
                elif risk_reward and risk_reward >= 1.5:
                    return f"今日可入场，区间¥{entry_result.feasible_min:.2f}-¥{entry_result.feasible_max:.2f}，盈亏比{risk_reward:.1f}:1（良好）"
                else:
                    return f"今日可入场，区间¥{entry_result.feasible_min:.2f}-¥{entry_result.feasible_max:.2f}，盈亏比一般，谨慎考虑"
            else:
                return "入场条件部分满足，建议观望"
        else:
            if entry_result.unsatisfied_conditions:
                conditions_str = ", ".join([c.description for c, _ in entry_result.unsatisfied_conditions[:2]])
                return f"今日不符合入场条件，等待：{conditions_str}"
            return "今日不符合入场条件，继续观望"
    
    def execute_entry(self, strategy: TradingStrategy, price: float) -> TradingStrategy:
        """执行入场"""
        strategy.status = StrategyStatus.ENTERED
        strategy.entry_price = price
        strategy.entry_date = date.today()
        strategy.updated_at = datetime.now()
        
        # 根据止损条件计算止损价格
        if strategy.stop_loss.fixed_price:
            strategy.stop_loss_price = strategy.stop_loss.fixed_price
        elif strategy.stop_loss.fixed_pct:
            strategy.stop_loss_price = price * (1 + strategy.stop_loss.fixed_pct / 100)
        
        return strategy
    
    def execute_exit(
        self,
        strategy: TradingStrategy,
        price: float,
        reason: str  # "stop_loss" | "take_profit" | "manual"
    ) -> TradingStrategy:
        """执行出场"""
        if reason == "stop_loss":
            strategy.status = StrategyStatus.STOP_LOSS
        elif reason == "take_profit":
            strategy.status = StrategyStatus.TAKE_PROFIT
        else:
            strategy.status = StrategyStatus.EXPIRED
        
        strategy.updated_at = datetime.now()
        return strategy


# 预设策略模板
PREDEFINED_STRATEGIES = {
    "均线金叉追涨": {
        "name": "均线金叉追涨策略",
        "entry_conditions": [
            Condition(ConditionType.PRICE_ABOVE_MA, {"period": 5}),
            Condition(ConditionType.MA_GOLDEN_CROSS, {"short": 5, "long": 10}),
            Condition(ConditionType.MACD_GOLDEN_CROSS, {}),
        ],
        "stop_loss_conditions": [
            Condition(ConditionType.PRICE_BELOW_MA, {"period": 10}),
        ],
        "description": "MA5金叉MA10且MACD金叉，价格站稳MA5时入场，跌破MA10止损"
    },
    "超卖反弹抄底": {
        "name": "超卖反弹策略",
        "entry_conditions": [
            Condition(ConditionType.KDJ_J_LT_ZERO, {}),
            Condition(ConditionType.RSI_OVERSOLD, {}),
            Condition(ConditionType.BOLL_BELOW_LOWER, {}),
        ],
        "stop_loss_conditions": [
            Condition(ConditionType.KDJ_J_LT_ZERO, {}),
        ],
        "description": "KDJ超卖+RSI超卖+触及布林下轨，KDJ继续恶化止损"
    },
    "水上金叉": {
        "name": "MACD水上金叉策略",
        "entry_conditions": [
            Condition(ConditionType.MACD_ABOVE_ZERO, {}),
            Condition(ConditionType.MACD_GOLDEN_CROSS, {}),
            Condition(ConditionType.PRICE_ABOVE_MA, {"period": 5}),
        ],
        "stop_loss_conditions": [
            Condition(ConditionType.MACD_DIF_GT_SIGNAL, {}),
        ],
        "description": "MACD水上金叉且站上MA5，DIF跌破Signal止损"
    },
    "均线粘合突破": {
        "name": "均线粘合突破策略",
        "entry_conditions": [
            Condition(ConditionType.PRICE_BETWEEN_MAS, {"short": 5, "long": 20}),
            Condition(ConditionType.MA_GOLDEN_CROSS, {"short": 5, "long": 20}),
        ],
        "stop_loss_conditions": [
            Condition(ConditionType.PRICE_BELOW_MA, {"period": 10}),
        ],
        "description": "均线粘合后向上突破，跌破MA10止损"
    },
}


def create_strategy_from_template(template_name: str, symbol: str) -> Optional[TradingStrategy]:
    """从预设模板创建策略"""
    if template_name not in PREDEFINED_STRATEGIES:
        return None
    
    template = PREDEFINED_STRATEGIES[template_name]
    engine = StrategyEngine()
    
    return engine.create_strategy(
        name=template["name"],
        symbol=symbol,
        entry_conditions=template["entry_conditions"],
        stop_loss_conditions=template["stop_loss_conditions"],
        notes=template["description"]
    )
