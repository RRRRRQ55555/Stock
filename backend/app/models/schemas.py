"""
数据模型定义 (Pydantic)

定义所有API请求/响应的数据结构
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ============= 基础模型 =============

class StockSymbol(BaseModel):
    """股票代码"""
    symbol: str = Field(..., description="股票代码，如 AAPL")
    name: Optional[str] = Field(None, description="股票名称")
    exchange: Optional[str] = Field(None, description="交易所")


class PriceData(BaseModel):
    """价格数据点"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: Optional[int] = None


# ============= 指标状态模型 =============

class MACDStateInput(BaseModel):
    """MACD昨日状态输入"""
    ema_12: float = Field(..., description="12日EMA昨日值")
    ema_26: float = Field(..., description="26日EMA昨日值")
    signal: float = Field(..., description="Signal线昨日值")
    dif: float = Field(..., description="DIF昨日值")
    close: float = Field(..., description="昨日收盘价")


class MAStateInput(BaseModel):
    """均线昨日状态输入"""
    prices_short: List[float] = Field(..., description="短期均线历史价格 (N-1个)")
    prices_long: List[float] = Field(..., description="长期均线历史价格 (N-1个)")
    short_period: int = Field(5, description="短期均线周期")
    long_period: int = Field(10, description="长期均线周期")


class KDJStateInput(BaseModel):
    """KDJ昨日状态输入"""
    k_yest: float = Field(..., description="K值昨日收盘值")
    d_yest: float = Field(..., description="D值昨日收盘值")
    h9: float = Field(..., description="9日最高价")
    l9: float = Field(..., description="9日最低价")


# ============= 请求模型 =============

class TriggerMatrixRequest(BaseModel):
    """临界价格矩阵请求"""
    symbol: str = Field(..., description="股票代码")
    current_price: float = Field(..., description="当前价格")
    macd: MACDStateInput
    ma: MAStateInput
    kdj: KDJStateInput


class StressTestRequest(BaseModel):
    """压力测试请求"""
    symbol: str = Field(..., description="股票代码")
    hypothetical_price: float = Field(..., description="假设价格")
    macd: MACDStateInput
    ma: MAStateInput
    kdj: KDJStateInput


class HistoricalDataRequest(BaseModel):
    """历史数据请求"""
    symbol: str = Field(..., description="股票代码")
    period: str = Field("1y", description="时间周期，如 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
    interval: str = Field("1d", description="时间间隔，如 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")


# ============= 响应模型 =============

class MACDResult(BaseModel):
    """MACD计算结果"""
    golden_cross_price: Optional[float] = Field(None, description="金叉临界价格")
    death_cross_price: Optional[float] = Field(None, description="死叉临界价格")
    dif: float = Field(..., description="当前DIF值")
    signal: float = Field(..., description="当前Signal值")
    distance_to_golden: Optional[float] = Field(None, description="距离金叉的百分比")
    distance_to_death: Optional[float] = Field(None, description="距离死叉的百分比")


class MAResult(BaseModel):
    """均线计算结果"""
    golden_cross_price: Optional[float] = Field(None, description="金叉临界价格")
    death_cross_price: Optional[float] = Field(None, description="死叉临界价格")
    ma_short: float = Field(..., description="短期均线当前值")
    ma_long: float = Field(..., description="长期均线当前值")
    short_period: int = Field(..., description="短期均线周期")
    long_period: int = Field(..., description="长期均线周期")
    is_bullish: bool = Field(..., description="是否为多头排列")
    distance_to_golden: Optional[float] = Field(None, description="距离金叉的百分比")
    distance_to_death: Optional[float] = Field(None, description="距离死叉的百分比")


class KDJResult(BaseModel):
    """KDJ计算结果"""
    oversold_price: Optional[float] = Field(None, description="超卖临界价格(J<=0)")
    overbought_price: Optional[float] = Field(None, description="超买临界价格(J>=100)")
    k: float = Field(..., description="当前K值")
    d: float = Field(..., description="当前D值")
    j: float = Field(..., description="当前J值")
    zone: str = Field(..., description="当前区域: oversold, neutral, overbought")
    distance_to_oversold: Optional[float] = Field(None, description="距离超卖的百分比")
    distance_to_overbought: Optional[float] = Field(None, description="距离超买的百分比")


class RSIResult(BaseModel):
    """RSI计算结果"""
    oversold_price: Optional[float] = Field(None, description="超卖临界价格(RSI<=30)")
    overbought_price: Optional[float] = Field(None, description="超买临界价格(RSI>=70)")
    value: float = Field(..., description="当前RSI值")
    zone: str = Field(..., description="当前区域: oversold, neutral, overbought")
    distance_to_oversold: Optional[float] = Field(None, description="距离超卖的百分比")
    distance_to_overbought: Optional[float] = Field(None, description="距离超买的百分比")


class BOLLResult(BaseModel):
    """布林带计算结果"""
    upper_touch_price: Optional[float] = Field(None, description="触及上轨临界价格")
    lower_touch_price: Optional[float] = Field(None, description="触及下轨临界价格")
    mb: float = Field(..., description="中轨(MB)")
    up: float = Field(..., description="上轨(UP)")
    dn: float = Field(..., description="下轨(DN)")
    position: str = Field(..., description="当前位置: above, inside, below")
    distance_to_upper: Optional[float] = Field(None, description="距离上轨的百分比")
    distance_to_lower: Optional[float] = Field(None, description="距离下轨的百分比")


class WRResult(BaseModel):
    """威廉指标计算结果"""
    overbought_price: Optional[float] = Field(None, description="超买临界价格(WR<=-80)")
    oversold_price: Optional[float] = Field(None, description="超卖临界价格(WR>=-20)")
    value: float = Field(..., description="当前WR值")
    zone: str = Field(..., description="当前区域: overbought, neutral, oversold")
    distance_to_overbought: Optional[float] = Field(None, description="距离超买的百分比")
    distance_to_oversold: Optional[float] = Field(None, description="距离超卖的百分比")


class CCIResult(BaseModel):
    """CCI计算结果"""
    overbought_price: Optional[float] = Field(None, description="超买临界价格(CCI>=100)")
    oversold_price: Optional[float] = Field(None, description="超卖临界价格(CCI<=-100)")
    value: float = Field(..., description="当前CCI值")
    zone: str = Field(..., description="当前区域: overbought, neutral, oversold")
    distance_to_overbought: Optional[float] = Field(None, description="距离超买的百分比")
    distance_to_oversold: Optional[float] = Field(None, description="距离超卖的百分比")


class ResonanceZone(BaseModel):
    """共振区间"""
    type: str = Field("resonance", description="区间类型")
    indicators: List[str] = Field(..., description="涉及的指标列表")
    price_min: float = Field(..., description="区间最低价")
    price_max: float = Field(..., description="区间最高价")
    price_center: float = Field(..., description="区间中心价")
    confidence: float = Field(..., description="置信度 (0-1)")
    distance_pct: Optional[float] = Field(None, description="距离当前价格的百分比")


class TriggerMatrixResponse(BaseModel):
    """临界价格矩阵响应"""
    symbol: str = Field(..., description="股票代码")
    name: Optional[str] = Field(None, description="股票名称")
    current_price: float = Field(..., description="当前价格")
    timestamp: str = Field(..., description="计算时间戳")
    macd: MACDResult
    ma: MAResult
    kdj: KDJResult
    rsi: Optional[RSIResult] = Field(None, description="RSI指标结果")
    boll: Optional[BOLLResult] = Field(None, description="布林带指标结果")
    wr: Optional[WRResult] = Field(None, description="威廉指标结果")
    cci: Optional[CCIResult] = Field(None, description="CCI指标结果")
    resonance: List[ResonanceZone] = Field(default_factory=list)


class StressTestResponse(BaseModel):
    """压力测试响应"""
    hypothetical_price: float = Field(..., description="假设价格")
    macd: Dict[str, Any] = Field(..., description="MACD模拟结果")
    ma: Dict[str, Any] = Field(..., description="均线模拟结果")
    kdj: Dict[str, Any] = Field(..., description="KDJ模拟结果")
    summary: Dict[str, Any] = Field(..., description="综合结论")


class HistoricalDataResponse(BaseModel):
    """历史数据响应"""
    symbol: str = Field(..., description="股票代码")
    period: str = Field(..., description="时间周期")
    interval: str = Field(..., description="时间间隔")
    data: List[PriceData] = Field(..., description="价格数据列表")


# ============= WebSocket消息模型 =============

class PriceUpdate(BaseModel):
    """价格更新消息"""
    symbol: str
    price: float
    timestamp: datetime
    change_pct: Optional[float] = None


class AlertMessage(BaseModel):
    """预警消息"""
    symbol: str
    alert_type: str  # "proximity", "triggered", "resonance"
    message: str
    critical_price: Optional[float] = None
    current_price: float
    distance_pct: Optional[float] = None
    timestamp: datetime


# ============= 配置模型 =============

class IndicatorConfig(BaseModel):
    """指标配置"""
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    ma_short: int = 5
    ma_long: int = 20
    kdj_period: int = 9


class MAParams(BaseModel):
    """均线参数"""
    periods: List[int] = Field(default=[5, 10, 20, 30, 60], description="均线周期列表")
    pairs: List[Dict[str, int]] = Field(
        default=[
            {"short": 5, "long": 10},
            {"short": 5, "long": 20},
            {"short": 10, "long": 20},
            {"short": 20, "long": 60}
        ],
        description="均线组合对"
    )


class MACDParams(BaseModel):
    """MACD参数"""
    fast: int = Field(default=12, description="快线周期")
    slow: int = Field(default=26, description="慢线周期")
    signal: int = Field(default=9, description="信号线周期")


class KDJParams(BaseModel):
    """KDJ参数"""
    n: int = Field(default=9, description="RSV周期")
    m1: int = Field(default=3, description="K平滑因子")
    m2: int = Field(default=3, description="D平滑因子")


class RSIParams(BaseModel):
    """RSI参数"""
    periods: List[int] = Field(default=[6, 12, 24], description="RSI周期列表")


class BOLLParams(BaseModel):
    """布林带参数"""
    period: int = Field(default=20, description="中轨周期")
    std_dev: float = Field(default=2.0, description="标准差倍数")


class FullIndicatorConfig(BaseModel):
    """完整指标配置"""
    ma: MAParams = Field(default_factory=MAParams)
    macd: MACDParams = Field(default_factory=MACDParams)
    kdj: KDJParams = Field(default_factory=KDJParams)
    rsi: RSIParams = Field(default_factory=RSIParams)
    boll: BOLLParams = Field(default_factory=BOLLParams)


class AlertThreshold(BaseModel):
    """预警阈值配置"""
    proximity_threshold: float = Field(1.0, description="接近临界点预警阈值(%)")
    resonance_min_indicators: int = Field(2, description="共振最少指标数")


# ============= 条件筛选器模型 =============

class ConditionInput(BaseModel):
    """单个技术条件输入"""
    condition_type: str = Field(..., description="条件类型，如 price_above_ma, macd_golden, kdj_oversold")
    params: Dict[str, Any] = Field(default_factory=dict, description="条件参数")
    weight: float = Field(1.0, description="权重 (0-1)")


class ConditionFilterRequest(BaseModel):
    """条件筛选请求"""
    symbol: str = Field(..., description="股票代码")
    current_price: float = Field(..., description="当前价格")
    conditions: List[ConditionInput] = Field(..., description="条件列表")
    use_auto_data: bool = Field(True, description="是否自动获取股票数据")
    macd: Optional[MACDStateInput] = Field(None, description="MACD状态 (use_auto_data=False时需要)")
    ma: Optional[MAStateInput] = Field(None, description="均线状态 (use_auto_data=False时需要)")
    kdj: Optional[KDJStateInput] = Field(None, description="KDJ状态 (use_auto_data=False时需要)")


class ConstraintDetail(BaseModel):
    """约束详情"""
    description: str = Field(..., description="条件描述")
    range: str = Field(..., description="价格区间")
    confidence: float = Field(..., description="约束可信度")


class UnsatisfiedCondition(BaseModel):
    """未满足条件"""
    condition: str = Field(..., description="条件描述")
    distance_pct: float = Field(..., description="距离目标的百分比")


class ConditionFilterResponse(BaseModel):
    """条件筛选响应"""
    symbol: str = Field(..., description="股票代码")
    current_price: float = Field(..., description="当前价格")
    feasible_range: Dict[str, Optional[float]] = Field(..., description="可行价格区间 {min, max}")
    confidence: float = Field(..., description="总体置信度 (0-1)")
    constraints: List[ConstraintDetail] = Field(default_factory=list, description="各条件的价格约束")
    satisfied: List[str] = Field(default_factory=list, description="已满足的条件描述")
    unsatisfied: List[UnsatisfiedCondition] = Field(default_factory=list, description="未满足的条件及距离")
    recommendation: str = Field(..., description="推荐建议")
    target_price: Optional[float] = Field(None, description="推荐目标价格")
    distance_to_target: Optional[float] = Field(None, description="距离目标的百分比")


# ============= 预定义条件场景模型 =============

class ConditionScenario(BaseModel):
    """条件场景"""
    name: str = Field(..., description="场景名称")
    description: str = Field(..., description="场景描述")
    conditions: List[ConditionInput] = Field(..., description="条件列表")
    tags: List[str] = Field(default_factory=list, description="标签")


class GetScenariosResponse(BaseModel):
    """获取预定义场景响应"""
    scenarios: List[ConditionScenario] = Field(..., description="场景列表")


# ============= 交易策略模型 =============

class StopLossConfig(BaseModel):
    """止损配置"""
    conditions: List[ConditionInput] = Field(default_factory=list, description="技术止损条件")
    fixed_price: Optional[float] = Field(None, description="固定止损价格")
    fixed_pct: Optional[float] = Field(None, description="固定止损百分比（如-5表示跌5%止损）")
    description: str = Field("", description="止损描述")


class TakeProfitConfig(BaseModel):
    """止盈配置"""
    conditions: List[ConditionInput] = Field(default_factory=list, description="技术止盈条件")
    fixed_price: Optional[float] = Field(None, description="固定止盈价格")
    fixed_pct: Optional[float] = Field(None, description="固定止盈百分比")
    r_ratio: Optional[float] = Field(None, description="盈亏比（如2表示2倍风险收益）")
    description: str = Field("", description="止盈描述")


class CreateStrategyRequest(BaseModel):
    """创建策略请求"""
    name: str = Field(..., description="策略名称")
    symbol: str = Field(..., description="股票代码")
    entry_conditions: List[ConditionInput] = Field(..., description="入场条件")
    stop_loss: StopLossConfig = Field(..., description="止损配置")
    take_profit: Optional[TakeProfitConfig] = Field(None, description="止盈配置（可选）")
    notes: str = Field("", description="策略备注")
    use_template: Optional[str] = Field(None, description="使用预设模板创建")


class StrategyResponse(BaseModel):
    """策略响应"""
    id: str = Field(..., description="策略ID")
    name: str = Field(..., description="策略名称")
    symbol: str = Field(..., description="股票代码")
    status: str = Field(..., description="策略状态")
    entry_description: str = Field(..., description="入场条件描述")
    stop_loss_description: str = Field(..., description="止损条件描述")
    take_profit_description: Optional[str] = Field(None, description="止盈条件描述")
    entry_price: Optional[float] = Field(None, description="入场价格")
    entry_date: Optional[str] = Field(None, description="入场日期")
    stop_loss_price: Optional[float] = Field(None, description="止损价格")
    notes: str = Field("", description="备注")
    created_at: str = Field(..., description="创建时间")


class StrategyCheckResultResponse(BaseModel):
    """策略检查结果响应"""
    strategy_id: str = Field(..., description="策略ID")
    symbol: str = Field(..., description="股票代码")
    current_price: float = Field(..., description="当前价格")
    check_date: str = Field(..., description="检查日期")
    
    # 入场分析
    can_enter_today: bool = Field(..., description="今日是否可入场")
    entry_price_min: Optional[float] = Field(None, description="入场区间最低价")
    entry_price_max: Optional[float] = Field(None, description="入场区间最高价")
    entry_confidence: float = Field(..., description="入场置信度")
    entry_distance_pct: Optional[float] = Field(None, description="距离入场区间的百分比")
    
    # 止损分析
    stop_loss_price: Optional[float] = Field(None, description="止损触发价格")
    stop_loss_distance_pct: Optional[float] = Field(None, description="距离止损的百分比")
    
    # 止盈分析
    take_profit_price: Optional[float] = Field(None, description="止盈目标价格")
    take_profit_distance_pct: Optional[float] = Field(None, description="距离止盈的百分比")
    
    # 综合建议
    recommendation: str = Field(..., description="交易建议")
    risk_reward_ratio: Optional[float] = Field(None, description="盈亏比")


class ExecuteEntryRequest(BaseModel):
    """执行入场请求"""
    price: float = Field(..., description="入场价格")
    notes: Optional[str] = Field(None, description="入场备注")


class ExecuteExitRequest(BaseModel):
    """执行出场请求"""
    price: float = Field(..., description="出场价格")
    reason: str = Field(..., description="出场原因：stop_loss/take_profit/manual")
    notes: Optional[str] = Field(None, description="出场备注")


class GetStrategiesResponse(BaseModel):
    """获取策略列表响应"""
    strategies: List[StrategyResponse] = Field(..., description="策略列表")
    count: int = Field(..., description="策略总数")
    by_status: Dict[str, int] = Field(default_factory=dict, description="各状态数量")


class StrategyTemplate(BaseModel):
    """策略模板"""
    name: str = Field(..., description="模板名称")
    description: str = Field(..., description="模板描述")
    entry_conditions: List[ConditionInput] = Field(..., description="入场条件")
    stop_loss_conditions: List[ConditionInput] = Field(..., description="止损条件")
    tags: List[str] = Field(default_factory=list, description="标签")


class GetStrategyTemplatesResponse(BaseModel):
    """获取策略模板响应"""
    templates: List[StrategyTemplate] = Field(..., description="模板列表")
