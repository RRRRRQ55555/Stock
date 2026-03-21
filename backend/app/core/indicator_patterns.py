"""
技术指标形态定义（黑话术语）

将复杂的技术指标组合预定义为交易者常用的"黑话"形态，
方便用户快速选择，无需手动配置参数。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .condition_filter import Condition, ConditionType


class PatternCategory(Enum):
    """形态分类"""
    MACD = "macd"
    MA = "ma"
    KDJ = "kdj"
    RSI = "rsi"
    BOLL = "boll"
    WR = "wr"
    CCI = "cci"
    COMBO = "combo"  # 组合形态


@dataclass
class IndicatorPattern:
    """技术指标形态"""
    id: str  # 唯一标识
    name: str  # 显示名称
    category: PatternCategory
    description: str  # 详细说明
    conditions: List[Condition]
    params: Dict[str, Any]  # 可配置参数
    bullish: bool  # 是否看涨信号
    strength: int  # 信号强度 1-5
    applicable_timeframes: List[str]  # 适用时间周期 ["1d", "1h", "15m"]


# ============= MACD 形态定义 =============

MACD_PATTERNS = [
    IndicatorPattern(
        id="macd_golden_above",
        name="水上金叉",
        category=PatternCategory.MACD,
        description="DIF在零轴上方金叉DEA，强势上涨信号，通常表示多头趋势确认",
        conditions=[
            Condition(ConditionType.MACD_ABOVE_ZERO, {}, 1.0),
            Condition(ConditionType.MACD_GOLDEN_CROSS, {}, 1.0),
        ],
        params={"fast": 12, "slow": 26, "signal": 9},
        bullish=True,
        strength=5,
        applicable_timeframes=["1d", "1h", "30m"]
    ),
    IndicatorPattern(
        id="macd_golden_below",
        name="水下金叉",
        category=PatternCategory.MACD,
        description="DIF在零轴下方金叉DEA，弱势反弹信号，可能是底部反转",
        conditions=[
            Condition(ConditionType.MACD_DIF_GT_SIGNAL, {}, 1.0),
        ],
        params={"fast": 12, "slow": 26, "signal": 9},
        bullish=True,
        strength=3,
        applicable_timeframes=["1d", "1h", "30m"]
    ),
    IndicatorPattern(
        id="macd_death_above",
        name="水上死叉",
        category=PatternCategory.MACD,
        description="DIF在零轴上方死叉DEA，强势调整信号，可能是短期回调",
        conditions=[
            Condition(ConditionType.MACD_ABOVE_ZERO, {}, 1.0),
        ],  # 死叉条件需要DIF<Signal，这里用占位
        params={"fast": 12, "slow": 26, "signal": 9},
        bullish=False,
        strength=3,
        applicable_timeframes=["1d", "1h", "30m"]
    ),
    IndicatorPattern(
        id="macd_death_below",
        name="水下死叉",
        category=PatternCategory.MACD,
        description="DIF在零轴下方死叉DEA，弱势下跌信号，空头趋势延续",
        conditions=[
            Condition(ConditionType.MACD_DIF_GT_SIGNAL, {}, 1.0),
        ],
        params={"fast": 12, "slow": 26, "signal": 9},
        bullish=False,
        strength=4,
        applicable_timeframes=["1d", "1h", "30m"]
    ),
    IndicatorPattern(
        id="macd_above_zero",
        name="DIF上穿零轴",
        category=PatternCategory.MACD,
        description="DIF从负区间进入正区间，多头力量增强",
        conditions=[
            Condition(ConditionType.MACD_ABOVE_ZERO, {}, 1.0),
        ],
        params={"fast": 12, "slow": 26, "signal": 9},
        bullish=True,
        strength=4,
        applicable_timeframes=["1d", "1h"]
    ),
    IndicatorPattern(
        id="macd_below_zero",
        name="DIF下穿零轴",
        category=PatternCategory.MACD,
        description="DIF从正区间进入负区间，空头力量增强",
        conditions=[
            Condition(ConditionType.MACD_ABOVE_ZERO, {}, 1.0),
        ],
        params={"fast": 12, "slow": 26, "signal": 9},
        bullish=False,
        strength=4,
        applicable_timeframes=["1d", "1h"]
    ),
    IndicatorPattern(
        id="macd_bullish_divergence",
        name="MACD底背离",
        category=PatternCategory.MACD,
        description="价格创新低但DIF未创新低，底部反转信号",
        conditions=[
            Condition(ConditionType.MACD_GOLDEN_CROSS, {}, 1.0),
        ],
        params={"fast": 12, "slow": 26, "signal": 9},
        bullish=True,
        strength=5,
        applicable_timeframes=["1d", "4h"]
    ),
    IndicatorPattern(
        id="macd_bearish_divergence",
        name="MACD顶背离",
        category=PatternCategory.MACD,
        description="价格创新高但DIF未创新高，顶部反转信号",
        conditions=[
            Condition(ConditionType.MACD_GOLDEN_CROSS, {}, 1.0),
        ],
        params={"fast": 12, "slow": 26, "signal": 9},
        bullish=False,
        strength=5,
        applicable_timeframes=["1d", "4h"]
    ),
]


# ============= 均线形态定义 =============

MA_PATTERNS = [
    IndicatorPattern(
        id="ma_bullish_alignment",
        name="均线多头排列",
        category=PatternCategory.MA,
        description="MA5>MA10>MA20>MA60，均线向上发散，强势上涨趋势",
        conditions=[
            Condition(ConditionType.PRICE_ABOVE_MA, {"period": 5}, 1.0),
            Condition(ConditionType.PRICE_ABOVE_MA, {"period": 10}, 1.0),
            Condition(ConditionType.PRICE_ABOVE_MA, {"period": 20}, 1.0),
        ],
        params={"short": 5, "medium": 10, "long": 20, "super_long": 60},
        bullish=True,
        strength=5,
        applicable_timeframes=["1d"]
    ),
    IndicatorPattern(
        id="ma_bearish_alignment",
        name="均线空头排列",
        category=PatternCategory.MA,
        description="MA5<MA10<MA20<MA60，均线向下发散，强势下跌趋势",
        conditions=[
            Condition(ConditionType.PRICE_BELOW_MA, {"period": 5}, 1.0),
            Condition(ConditionType.PRICE_BELOW_MA, {"period": 10}, 1.0),
            Condition(ConditionType.PRICE_BELOW_MA, {"period": 20}, 1.0),
        ],
        params={"short": 5, "medium": 10, "long": 20, "super_long": 60},
        bullish=False,
        strength=5,
        applicable_timeframes=["1d"]
    ),
    IndicatorPattern(
        id="ma_golden_5_10",
        name="MA5金叉MA10",
        category=PatternCategory.MA,
        description="5日均线上穿10日均线，短线多头信号",
        conditions=[
            Condition(ConditionType.MA_GOLDEN_CROSS, {"short": 5, "long": 10}, 1.0),
        ],
        params={"short": 5, "long": 10},
        bullish=True,
        strength=3,
        applicable_timeframes=["1d", "1h"]
    ),
    IndicatorPattern(
        id="ma_golden_5_20",
        name="MA5金叉MA20",
        category=PatternCategory.MA,
        description="5日均线上穿20日均线，中线多头信号",
        conditions=[
            Condition(ConditionType.MA_GOLDEN_CROSS, {"short": 5, "long": 20}, 1.0),
        ],
        params={"short": 5, "long": 20},
        bullish=True,
        strength=4,
        applicable_timeframes=["1d"]
    ),
    IndicatorPattern(
        id="ma_golden_10_30",
        name="MA10金叉MA30",
        category=PatternCategory.MA,
        description="10日均线上穿30日均线，中线趋势确认",
        conditions=[
            Condition(ConditionType.MA_GOLDEN_CROSS, {"short": 10, "long": 30}, 1.0),
        ],
        params={"short": 10, "long": 30},
        bullish=True,
        strength=4,
        applicable_timeframes=["1d"]
    ),
    IndicatorPattern(
        id="ma_death_5_10",
        name="MA5死叉MA10",
        category=PatternCategory.MA,
        description="5日均线下穿10日均线，短线空头信号",
        conditions=[
            Condition(ConditionType.MA_GOLDEN_CROSS, {"short": 5, "long": 10}, 1.0),
        ],
        params={"short": 5, "long": 10},
        bullish=False,
        strength=3,
        applicable_timeframes=["1d", "1h"]
    ),
    IndicatorPattern(
        id="ma_price_above_5",
        name="股价站上MA5",
        category=PatternCategory.MA,
        description="收盘价高于5日均线，短线强势",
        conditions=[
            Condition(ConditionType.PRICE_ABOVE_MA, {"period": 5}, 1.0),
        ],
        params={"period": 5},
        bullish=True,
        strength=2,
        applicable_timeframes=["1d", "1h", "15m"]
    ),
    IndicatorPattern(
        id="ma_price_above_20",
        name="股价站上MA20",
        category=PatternCategory.MA,
        description="收盘价高于20日均线，中线强势",
        conditions=[
            Condition(ConditionType.PRICE_ABOVE_MA, {"period": 20}, 1.0),
        ],
        params={"period": 20},
        bullish=True,
        strength=3,
        applicable_timeframes=["1d"]
    ),
    IndicatorPattern(
        id="ma_price_below_5",
        name="股价跌破MA5",
        category=PatternCategory.MA,
        description="收盘价低于5日均线，短线弱势",
        conditions=[
            Condition(ConditionType.PRICE_BELOW_MA, {"period": 5}, 1.0),
        ],
        params={"period": 5},
        bullish=False,
        strength=2,
        applicable_timeframes=["1d", "1h", "15m"]
    ),
    IndicatorPattern(
        id="ma_bullish_between",
        name="股价在MA5-MA20之间",
        category=PatternCategory.MA,
        description="股价在短期和中期均线之间震荡",
        conditions=[
            Condition(ConditionType.PRICE_BETWEEN_MAS, {"short": 5, "long": 20}, 1.0),
        ],
        params={"short": 5, "long": 20},
        bullish=True,
        strength=2,
        applicable_timeframes=["1d"]
    ),
]


# ============= KDJ 形态定义 =============

KDJ_PATTERNS = [
    IndicatorPattern(
        id="kdj_golden",
        name="KDJ金叉",
        category=PatternCategory.KDJ,
        description="K线上穿D线，买入信号",
        conditions=[
            Condition(ConditionType.KDJ_K_LT_D, {}, 1.0),
        ],
        params={"n": 9, "m1": 3, "m2": 3},
        bullish=True,
        strength=3,
        applicable_timeframes=["1d", "1h"]
    ),
    IndicatorPattern(
        id="kdj_death",
        name="KDJ死叉",
        category=PatternCategory.KDJ,
        description="K线下穿D线，卖出信号",
        conditions=[
            Condition(ConditionType.KDJ_K_LT_D, {}, 1.0),
        ],
        params={"n": 9, "m1": 3, "m2": 3},
        bullish=False,
        strength=3,
        applicable_timeframes=["1d", "1h"]
    ),
    IndicatorPattern(
        id="kdj_oversold",
        name="KDJ超卖区",
        category=PatternCategory.KDJ,
        description="K、D值小于20，处于超卖状态，可能反弹",
        conditions=[
            Condition(ConditionType.KDJ_J_LT_ZERO, {}, 1.0),
        ],
        params={"n": 9, "m1": 3, "m2": 3, "threshold": 20},
        bullish=True,
        strength=4,
        applicable_timeframes=["1d"]
    ),
    IndicatorPattern(
        id="kdj_overbought",
        name="KDJ超买区",
        category=PatternCategory.KDJ,
        description="K、D值大于80，处于超买状态，可能回调",
        conditions=[
            Condition(ConditionType.KDJ_J_GT_100, {}, 1.0),
        ],
        params={"n": 9, "m1": 3, "m2": 3, "threshold": 80},
        bullish=False,
        strength=4,
        applicable_timeframes=["1d"]
    ),
    IndicatorPattern(
        id="kdj_j_negative",
        name="J值小于0",
        category=PatternCategory.KDJ,
        description="J值进入负区间，极度超卖，反弹概率大",
        conditions=[
            Condition(ConditionType.KDJ_J_LT_ZERO, {}, 1.0),
        ],
        params={"n": 9, "m1": 3, "m2": 3},
        bullish=True,
        strength=5,
        applicable_timeframes=["1d"]
    ),
    IndicatorPattern(
        id="kdj_j_exceed_100",
        name="J值大于100",
        category=PatternCategory.KDJ,
        description="J值超过100，极度超买，回调概率大",
        conditions=[
            Condition(ConditionType.KDJ_J_GT_100, {}, 1.0),
        ],
        params={"n": 9, "m1": 3, "m2": 3},
        bullish=False,
        strength=4,
        applicable_timeframes=["1d"]
    ),
]


# ============= RSI 形态定义 =============

RSI_PATTERNS = [
    IndicatorPattern(
        id="rsi_oversold_30",
        name="RSI超卖(<30)",
        category=PatternCategory.RSI,
        description="RSI低于30，超卖状态，可能反弹",
        conditions=[
            Condition(ConditionType.RSI_OVERSOLD, {}, 1.0),
        ],
        params={"period": 14, "threshold": 30},
        bullish=True,
        strength=4,
        applicable_timeframes=["1d"]
    ),
    IndicatorPattern(
        id="rsi_overbought_70",
        name="RSI超买(>70)",
        category=PatternCategory.RSI,
        description="RSI高于70，超买状态，可能回调",
        conditions=[
            Condition(ConditionType.RSI_OVERBOUGHT, {}, 1.0),
        ],
        params={"period": 14, "threshold": 70},
        bullish=False,
        strength=4,
        applicable_timeframes=["1d"]
    ),
    IndicatorPattern(
        id="rsi_extreme_oversold",
        name="RSI极度超卖(<20)",
        category=PatternCategory.RSI,
        description="RSI低于20，极度超卖，强烈反弹预期",
        conditions=[
            Condition(ConditionType.RSI_OVERSOLD, {}, 1.0),
        ],
        params={"period": 14, "threshold": 20},
        bullish=True,
        strength=5,
        applicable_timeframes=["1d"]
    ),
]


# ============= 布林带 形态定义 =============

BOLL_PATTERNS = [
    IndicatorPattern(
        id="boll_touch_lower",
        name="触及布林带下轨",
        category=PatternCategory.BOLL,
        description="股价触及或跌破布林带下轨，可能反弹",
        conditions=[
            Condition(ConditionType.BOLL_BELOW_LOWER, {}, 1.0),
        ],
        params={"period": 20, "std_dev": 2},
        bullish=True,
        strength=4,
        applicable_timeframes=["1d"]
    ),
    IndicatorPattern(
        id="boll_touch_upper",
        name="触及布林带上轨",
        category=PatternCategory.BOLL,
        description="股价触及或突破布林带上轨，可能回调",
        conditions=[
            Condition(ConditionType.BOLL_ABOVE_UPPER, {}, 1.0),
        ],
        params={"period": 20, "std_dev": 2},
        bullish=False,
        strength=4,
        applicable_timeframes=["1d"]
    ),
    IndicatorPattern(
        id="boll_inside",
        name="在布林带中轨之上",
        category=PatternCategory.BOLL,
        description="股价在布林带中轨上方，相对强势",
        conditions=[
            Condition(ConditionType.BOLL_INSIDE, {}, 1.0),
        ],
        params={"period": 20, "std_dev": 2},
        bullish=True,
        strength=2,
        applicable_timeframes=["1d"]
    ),
]


# ============= 组合形态定义 =============

COMBO_PATTERNS = [
    IndicatorPattern(
        id="combo_strong_buy",
        name="多重共振买入",
        category=PatternCategory.COMBO,
        description="MACD水上金叉 + 均线多头排列 + KDJ金叉，强烈买入信号",
        conditions=[
            Condition(ConditionType.MACD_ABOVE_ZERO, {}, 1.0),
            Condition(ConditionType.MACD_GOLDEN_CROSS, {}, 1.0),
            Condition(ConditionType.PRICE_ABOVE_MA, {"period": 5}, 1.0),
            Condition(ConditionType.PRICE_ABOVE_MA, {"period": 10}, 1.0),
        ],
        params={},
        bullish=True,
        strength=5,
        applicable_timeframes=["1d"]
    ),
    IndicatorPattern(
        id="combo_strong_sell",
        name="多重共振卖出",
        category=PatternCategory.COMBO,
        description="MACD水下死叉 + 均线空头排列 + KDJ死叉，强烈卖出信号",
        conditions=[
            Condition(ConditionType.PRICE_BELOW_MA, {"period": 5}, 1.0),
            Condition(ConditionType.PRICE_BELOW_MA, {"period": 10}, 1.0),
        ],
        params={},
        bullish=False,
        strength=5,
        applicable_timeframes=["1d"]
    ),
    IndicatorPattern(
        id="combo_bottom_rebound",
        name="底部反弹组合",
        category=PatternCategory.COMBO,
        description="KDJ超卖 + RSI超卖 + 触及布林下轨，底部反弹信号",
        conditions=[
            Condition(ConditionType.KDJ_J_LT_ZERO, {}, 1.0),
            Condition(ConditionType.RSI_OVERSOLD, {}, 1.0),
            Condition(ConditionType.BOLL_BELOW_LOWER, {}, 1.0),
        ],
        params={},
        bullish=True,
        strength=5,
        applicable_timeframes=["1d"]
    ),
]


# 所有形态的集合
ALL_PATTERNS: List[IndicatorPattern] = (
    MACD_PATTERNS + 
    MA_PATTERNS + 
    KDJ_PATTERNS + 
    RSI_PATTERNS + 
    BOLL_PATTERNS + 
    COMBO_PATTERNS
)


def get_pattern_by_id(pattern_id: str) -> Optional[IndicatorPattern]:
    """根据ID获取形态定义"""
    for pattern in ALL_PATTERNS:
        if pattern.id == pattern_id:
            return pattern
    return None


def get_patterns_by_category(category: PatternCategory) -> List[IndicatorPattern]:
    """根据分类获取形态列表"""
    return [p for p in ALL_PATTERNS if p.category == category]


def get_patterns_by_direction(bullish: bool) -> List[IndicatorPattern]:
    """根据方向获取形态列表（看涨/看跌）"""
    return [p for p in ALL_PATTERNS if p.bullish == bullish]


def get_pattern_categories() -> Dict[str, List[IndicatorPattern]]:
    """获取按分类组织的形态"""
    return {
        "macd": MACD_PATTERNS,
        "ma": MA_PATTERNS,
        "kdj": KDJ_PATTERNS,
        "rsi": RSI_PATTERNS,
        "boll": BOLL_PATTERNS,
        "combo": COMBO_PATTERNS,
    }


def create_entry_strategy_from_patterns(
    pattern_ids: List[str],
    custom_params: Optional[Dict[str, Any]] = None
) -> List[Condition]:
    """
    从选择的形态创建入场策略条件
    
    Args:
        pattern_ids: 选择的形态ID列表
        custom_params: 自定义参数（覆盖默认参数）
        
    Returns:
        组合后的条件列表
    """
    all_conditions = []
    
    for pattern_id in pattern_ids:
        pattern = get_pattern_by_id(pattern_id)
        if pattern:
            # 复制条件，避免修改原始定义
            for cond in pattern.conditions:
                # 应用自定义参数
                params = {**cond.params}
                if custom_params and pattern_id in custom_params:
                    params.update(custom_params[pattern_id])
                
                all_conditions.append(Condition(
                    condition_type=cond.condition_type,
                    params=params,
                    weight=cond.weight
                ))
    
    return all_conditions


# 形态分类的中文名称
CATEGORY_NAMES = {
    "macd": "MACD形态",
    "ma": "均线形态",
    "kdj": "KDJ形态",
    "rsi": "RSI形态",
    "boll": "布林带形态",
    "combo": "组合形态",
}
