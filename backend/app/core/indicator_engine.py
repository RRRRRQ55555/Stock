"""
技术指标引擎

整合 MACD/MA/KDJ 求解器，提供统一的接口进行临界价格计算和压力测试。
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from .macd_solver import MACDSolver, MACDState, MACDTriggerResult
from .ma_solver import MASolver, MAState, MATriggerResult
from .kdj_solver import KDJolver, KDJState, KDJTriggerResult
from .rsi_solver import RSISolver, RSIState, RSITriggerResult
from .boll_solver import BOLLSolver, BOLLState, BOLLTriggerResult
from .wr_solver import WRSolver, WRState, WRTriggerResult
from .cci_solver import CCISolver, CCIState, CCITriggerResult


@dataclass
class TriggerMatrix:
    """
    临界价格触发矩阵
    
    整合所有技术指标的临界价格信息
    """
    symbol: str
    current_price: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    # MACD临界价格
    macd_golden_price: Optional[float] = None
    macd_death_price: Optional[float] = None
    macd_dif_current: float = 0.0
    macd_signal_current: float = 0.0
    
    # 均线临界价格
    ma_golden_price: Optional[float] = None
    ma_death_price: Optional[float] = None
    ma_short_current: float = 0.0
    ma_long_current: float = 0.0
    ma_short_period: int = 5
    ma_long_period: int = 10
    
    # KDJ临界价格
    kdj_oversold_price: Optional[float] = None
    kdj_overbought_price: Optional[float] = None
    kdj_k_current: float = 0.0
    kdj_d_current: float = 0.0
    kdj_j_current: float = 0.0

    # RSI临界价格
    rsi_oversold_price: Optional[float] = None
    rsi_overbought_price: Optional[float] = None
    rsi_current: float = 50.0

    # 布林带临界价格
    boll_upper_price: Optional[float] = None
    boll_lower_price: Optional[float] = None
    boll_mb_current: float = 0.0
    boll_up_current: float = 0.0
    boll_dn_current: float = 0.0
    boll_position: str = "middle"

    # 威廉指标临界价格
    wr_overbought_price: Optional[float] = None
    wr_oversold_price: Optional[float] = None
    wr_current: float = -50.0

    # CCI临界价格
    cci_overbought_price: Optional[float] = None
    cci_oversold_price: Optional[float] = None
    cci_current: float = 0.0

    # 共振区间
    resonance_zones: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "symbol": self.symbol,
            "current_price": self.current_price,
            "timestamp": self.timestamp.isoformat(),
            "macd": {
                "golden_cross_price": self.macd_golden_price,
                "death_cross_price": self.macd_death_price,
                "dif": round(self.macd_dif_current, 4),
                "signal": round(self.macd_signal_current, 4),
                "distance_to_golden": self._calc_distance(self.macd_golden_price),
                "distance_to_death": self._calc_distance(self.macd_death_price),
            },
            "ma": {
                "golden_cross_price": self.ma_golden_price,
                "death_cross_price": self.ma_death_price,
                "ma_short": round(self.ma_short_current, 4),
                "ma_long": round(self.ma_long_current, 4),
                "short_period": self.ma_short_period,
                "long_period": self.ma_long_period,
                "is_bullish": self.ma_short_current > self.ma_long_current,
                "distance_to_golden": self._calc_distance(self.ma_golden_price),
                "distance_to_death": self._calc_distance(self.ma_death_price),
            },
            "kdj": {
                "oversold_price": self.kdj_oversold_price,
                "overbought_price": self.kdj_overbought_price,
                "k": round(self.kdj_k_current, 4),
                "d": round(self.kdj_d_current, 4),
                "j": round(self.kdj_j_current, 4),
                "zone": self._get_kdj_zone(),
                "distance_to_oversold": self._calc_distance(self.kdj_oversold_price),
                "distance_to_overbought": self._calc_distance(self.kdj_overbought_price),
            },
            "rsi": {
                "oversold_price": self.rsi_oversold_price,
                "overbought_price": self.rsi_overbought_price,
                "value": round(self.rsi_current, 2),
                "zone": self._get_rsi_zone(),
                "distance_to_oversold": self._calc_distance(self.rsi_oversold_price),
                "distance_to_overbought": self._calc_distance(self.rsi_overbought_price),
            },
            "boll": {
                "upper_touch_price": self.boll_upper_price,
                "lower_touch_price": self.boll_lower_price,
                "mb": round(self.boll_mb_current, 4),
                "up": round(self.boll_up_current, 4),
                "dn": round(self.boll_dn_current, 4),
                "position": self.boll_position,
                "distance_to_upper": self._calc_distance(self.boll_upper_price),
                "distance_to_lower": self._calc_distance(self.boll_lower_price),
            },
            "wr": {
                "overbought_price": self.wr_overbought_price,
                "oversold_price": self.wr_oversold_price,
                "value": round(self.wr_current, 2),
                "zone": self._get_wr_zone(),
                "distance_to_overbought": self._calc_distance(self.wr_overbought_price),
                "distance_to_oversold": self._calc_distance(self.wr_oversold_price),
            },
            "cci": {
                "overbought_price": self.cci_overbought_price,
                "oversold_price": self.cci_oversold_price,
                "value": round(self.cci_current, 2),
                "zone": self._get_cci_zone(),
                "distance_to_overbought": self._calc_distance(self.cci_overbought_price),
                "distance_to_oversold": self._calc_distance(self.cci_oversold_price),
            },
            "resonance": self.resonance_zones
        }
    
    def _calc_distance(self, target_price: Optional[float]) -> Optional[float]:
        """计算距离目标价格的百分比"""
        if target_price is None or self.current_price <= 0:
            return None
        return round((target_price - self.current_price) / self.current_price * 100, 2)
    
    def _get_kdj_zone(self) -> str:
        """获取KDJ当前区域"""
        if self.kdj_j_current <= 0:
            return "oversold"
        elif self.kdj_j_current >= 100:
            return "overbought"
        else:
            return "neutral"
    
    def _get_rsi_zone(self) -> str:
        """获取RSI当前区域"""
        if self.rsi_current <= 30:
            return "oversold"
        elif self.rsi_current >= 70:
            return "overbought"
        else:
            return "neutral"
    
    def _get_wr_zone(self) -> str:
        """获取WR当前区域"""
        if self.wr_current <= -80:
            return "overbought"
        elif self.wr_current >= -20:
            return "oversold"
        else:
            return "neutral"
    
    def _get_cci_zone(self) -> str:
        """获取CCI当前区域"""
        if self.cci_current >= 100:
            return "overbought"
        elif self.cci_current <= -100:
            return "oversold"
        else:
            return "neutral"


class IndicatorEngine:
    """技术指标计算引擎"""
    
    def __init__(
        self,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        ma_short: int = 5,
        ma_long: int = 10,
        kdj_period: int = 9,
        rsi_period: int = 14,
        boll_period: int = 20,
        boll_k: float = 2.0,
        wr_period: int = 14,
        cci_period: int = 14
    ):
        """
        初始化指标引擎
        
        Args:
            macd_fast: MACD快线周期
            macd_slow: MACD慢线周期
            macd_signal: MACD信号线周期
            ma_short: 短期均线周期
            ma_long: 长期均线周期
            kdj_period: KDJ计算周期
            rsi_period: RSI计算周期
            boll_period: 布林带周期
            boll_k: 布林带标准差倍数
            wr_period: 威廉指标周期
            cci_period: CCI周期
        """
        # 初始化求解器
        self.macd_solver = MACDSolver(macd_fast, macd_slow, macd_signal)
        self.ma_solver = MASolver(ma_short, ma_long)
        self.kdj_solver = KDJolver(kdj_period)
        self.rsi_solver = RSISolver(rsi_period)
        self.boll_solver = BOLLSolver(boll_period, boll_k)
        self.wr_solver = WRSolver(wr_period)
        self.cci_solver = CCISolver(cci_period)
        
        # 保存配置
        self.config = {
            "macd": {"fast": macd_fast, "slow": macd_slow, "signal": macd_signal},
            "ma": {"short": ma_short, "long": ma_long},
            "kdj": {"period": kdj_period},
            "rsi": {"period": rsi_period},
            "boll": {"period": boll_period, "k": boll_k},
            "wr": {"period": wr_period},
            "cci": {"period": cci_period}
        }
    
    def calculate_trigger_matrix(
        self,
        symbol: str,
        current_price: float,
        macd_state: MACDState,
        ma_state: MAState,
        kdj_state: KDJState,
        rsi_state: RSIState = None,
        boll_state: BOLLState = None,
        wr_state: WRState = None,
        cci_state: CCIState = None
    ) -> TriggerMatrix:
        """
        计算完整的临界价格触发矩阵
        
        Args:
            symbol: 股票代码
            current_price: 当前价格
            macd_state: MACD昨日状态
            ma_state: 均线昨日状态
            kdj_state: KDJ昨日状态
            rsi_state: RSI昨日状态 (可选)
            boll_state: 布林带昨日状态 (可选)
            wr_state: 威廉指标昨日状态 (可选)
            cci_state: CCI昨日状态 (可选)
            
        Returns:
            TriggerMatrix 包含所有临界价格信息
        """
        # 计算MACD临界价格
        macd_result = self.macd_solver.solve_trigger_prices(macd_state, current_price)
        
        # 计算均线临界价格
        ma_result = self.ma_solver.solve_trigger_prices(ma_state)
        
        # 计算KDJ临界价格
        kdj_result = self.kdj_solver.solve_trigger_prices(kdj_state)
        
        # 构建触发矩阵
        matrix = TriggerMatrix(
            symbol=symbol,
            current_price=current_price,
            macd_golden_price=macd_result.golden_cross_price,
            macd_death_price=macd_result.death_cross_price,
            macd_dif_current=macd_result.dif_current,
            macd_signal_current=macd_result.signal_current,
            ma_golden_price=ma_result.golden_cross_price,
            ma_death_price=ma_result.death_cross_price,
            ma_short_current=ma_result.ma_short_current,
            ma_long_current=ma_result.ma_long_current,
            ma_short_period=self.config["ma"]["short"],
            ma_long_period=self.config["ma"]["long"],
            kdj_oversold_price=kdj_result.oversold_price,
            kdj_overbought_price=kdj_result.overbought_price,
            kdj_k_current=kdj_result.k_current,
            kdj_d_current=kdj_result.d_current,
            kdj_j_current=kdj_result.j_current
        )
        
        # 计算RSI临界价格
        if rsi_state:
            rsi_result = self.rsi_solver.solve_trigger_prices(rsi_state)
            matrix.rsi_oversold_price = rsi_result.oversold_price
            matrix.rsi_overbought_price = rsi_result.overbought_price
            matrix.rsi_current = rsi_result.rsi_current
        
        # 计算布林带临界价格
        if boll_state:
            boll_result = self.boll_solver.solve_trigger_prices(boll_state)
            matrix.boll_upper_price = boll_result.upper_touch_price
            matrix.boll_lower_price = boll_result.lower_touch_price
            matrix.boll_mb_current = boll_result.mb_current
            matrix.boll_up_current = boll_result.up_current
            matrix.boll_dn_current = boll_result.dn_current
            matrix.boll_position = boll_result.position
        
        # 计算威廉指标临界价格
        if wr_state:
            wr_result = self.wr_solver.solve_trigger_prices(wr_state)
            matrix.wr_overbought_price = wr_result.overbought_price
            matrix.wr_oversold_price = wr_result.oversold_price
            matrix.wr_current = wr_result.wr_current
        
        # 计算CCI临界价格
        if cci_state:
            cci_result = self.cci_solver.solve_trigger_prices(cci_state)
            matrix.cci_overbought_price = cci_result.overbought_price
            matrix.cci_oversold_price = cci_result.oversold_price
            matrix.cci_current = cci_result.cci_current
        
        # 检测共振区间
        matrix.resonance_zones = self._detect_resonance(matrix)
        
        return matrix
    
    def _detect_resonance(self, matrix: TriggerMatrix) -> List[Dict[str, Any]]:
        """
        检测多指标共振区间
        
        共振定义：多个技术指标的临界价格在相近区间内重合
        
        Returns:
            共振区间列表
        """
        zones = []
        
        # 收集所有有效临界价格
        critical_prices = []
        
        if matrix.macd_golden_price:
            critical_prices.append(("MACD金叉", matrix.macd_golden_price))
        if matrix.macd_death_price:
            critical_prices.append(("MACD死叉", matrix.macd_death_price))
        if matrix.ma_golden_price:
            critical_prices.append(("均线金叉", matrix.ma_golden_price))
        if matrix.ma_death_price:
            critical_prices.append(("均线死叉", matrix.ma_death_price))
        if matrix.kdj_oversold_price:
            critical_prices.append(("KDJ超卖", matrix.kdj_oversold_price, "buy"))
        if matrix.kdj_overbought_price:
            critical_prices.append(("KDJ超买", matrix.kdj_overbought_price, "sell"))
        
        # RSI
        if matrix.rsi_oversold_price:
            critical_prices.append(("RSI超卖", matrix.rsi_oversold_price, "buy"))
        if matrix.rsi_overbought_price:
            critical_prices.append(("RSI超买", matrix.rsi_overbought_price, "sell"))
        
        # 布林带
        if matrix.boll_upper_price:
            critical_prices.append(("布林上轨", matrix.boll_upper_price, "sell"))
        if matrix.boll_lower_price:
            critical_prices.append(("布林下轨", matrix.boll_lower_price, "buy"))
        
        # WR
        if matrix.wr_overbought_price:
            critical_prices.append(("WR超买", matrix.wr_overbought_price, "sell"))
        if matrix.wr_oversold_price:
            critical_prices.append(("WR超卖", matrix.wr_oversold_price, "buy"))
        
        # CCI
        if matrix.cci_overbought_price:
            critical_prices.append(("CCI超买", matrix.cci_overbought_price, "sell"))
        if matrix.cci_oversold_price:
            critical_prices.append(("CCI超卖", matrix.cci_oversold_price, "buy"))
        
        if len(critical_prices) < 2:
            return zones
        
        # 简单聚类：找出价格接近的指标组
        # 阈值：价格相差小于2%视为共振
        threshold_pct = 0.02
        
        # 按价格排序
        critical_prices.sort(key=lambda x: x[1])
        
        # 滑动窗口找共振
        i = 0
        while i < len(critical_prices):
            cluster = [critical_prices[i]]
            j = i + 1
            
            while j < len(critical_prices):
                # 检查当前价格与聚类中心的差距
                cluster_center = sum(p[1] for p in cluster) / len(cluster)
                if abs(critical_prices[j][1] - cluster_center) / cluster_center <= threshold_pct:
                    cluster.append(critical_prices[j])
                    j += 1
                else:
                    break
            
            # 如果有多个指标在聚类中，标记为共振区间
            if len(cluster) >= 2:
                prices = [p[1] for p in cluster]
                zone = {
                    "type": "resonance",
                    "indicators": [p[0] for p in cluster],
                    "price_min": round(min(prices), 2),
                    "price_max": round(max(prices), 2),
                    "price_center": round(sum(prices) / len(prices), 2),
                    "confidence": min(len(cluster) * 0.3, 0.9),  # 简单置信度计算
                    "distance_pct": round(
                        (sum(prices) / len(prices) - matrix.current_price) 
                        / matrix.current_price * 100, 2
                    ) if matrix.current_price > 0 else None
                }
                zones.append(zone)
            
            i = j
        
        return zones
    
    def stress_test(
        self,
        hypothetical_price: float,
        macd_state: MACDState,
        ma_state: MAState,
        kdj_state: KDJState
    ) -> Dict[str, Any]:
        """
        压力测试：模拟在假设价格下的所有指标状态
        
        Args:
            hypothetical_price: 假设价格
            macd_state: MACD昨日状态
            ma_state: 均线昨日状态
            kdj_state: KDJ昨日状态
            
        Returns:
            包含所有指标模拟结果的字典
        """
        # 模拟MACD
        macd_sim = self.macd_solver.simulate_price(macd_state, hypothetical_price)
        
        # 模拟均线
        ma_sim = self.ma_solver.simulate_price(ma_state, hypothetical_price)
        
        # 模拟KDJ
        kdj_sim = self.kdj_solver.simulate_price(kdj_state, hypothetical_price)
        
        # 综合判断
        bullish_signals = sum([
            macd_sim.get("is_golden_cross", False),
            ma_sim.get("is_golden_cross", False),
            kdj_sim.get("zone") == "oversold"  # 超卖后可能反弹
        ])
        
        bearish_signals = sum([
            macd_sim.get("is_death_cross", False),
            ma_sim.get("is_death_cross", False),
            kdj_sim.get("zone") == "overbought"  # 超买后可能回调
        ])
        
        return {
            "hypothetical_price": hypothetical_price,
            "macd": macd_sim,
            "ma": ma_sim,
            "kdj": kdj_sim,
            "summary": {
                "bullish_signals": bullish_signals,
                "bearish_signals": bearish_signals,
                "overall": "bullish" if bullish_signals > bearish_signals else
                           "bearish" if bearish_signals > bullish_signals else "neutral"
            }
        }

    def calculate_strategy_range(
        self,
        current_price: float,
        macd_state: MACDState,
        ma_state: MAState,
        kdj_state: KDJState,
        rsi_state: RSIState = None,
        buy_conditions: Dict[str, bool] = None,
        stop_conditions: Dict[str, bool] = None
    ) -> Dict[str, Any]:
        """
        计算策略满足的价格区间

        分析在什么价格区间，用户的买入/止损策略会被满足

        Args:
            current_price: 当前价格
            macd_state: MACD状态
            ma_state: 均线状态
            kdj_state: KDJ状态
            rsi_state: RSI状态
            buy_conditions: 买入条件设置
            stop_conditions: 止损条件设置

        Returns:
            价格区间分析结果
        """
        buy_conditions = buy_conditions or {}
        stop_conditions = stop_conditions or {}

        result = {
            "buy": None,
            "stop": None,
            "recommendation": "观望"
        }

        # 计算买入条件的价格区间
        if buy_conditions:
            buy_range = self._calculate_buy_range(
                current_price, macd_state, ma_state, kdj_state, rsi_state, buy_conditions
            )
            result["buy"] = buy_range

            # 如果当前价格已满足买入条件
            if buy_range.get("current_satisfied"):
                result["recommendation"] = "可买"

        # 计算止损条件的价格区间
        if stop_conditions:
            stop_range = self._calculate_stop_range(
                current_price, macd_state, ma_state, kdj_state, stop_conditions
            )
            result["stop"] = stop_range

            # 如果当前价格触发止损
            if stop_range.get("current_triggered"):
                result["recommendation"] = "止损"

        return result

    def _calculate_buy_range(
        self,
        current_price: float,
        macd_state: MACDState,
        ma_state: MAState,
        kdj_state: KDJState,
        rsi_state: RSIState,
        conditions: Dict[str, bool]
    ) -> Dict[str, Any]:
        """计算买入策略满足的价格区间"""

        # 获取各条件的临界价格
        critical_prices = []
        unsatisfied_conditions = []

        # MACD金叉条件
        if conditions.get("macdGolden"):
            macd_result = self.macd_solver.solve_trigger_prices(macd_state, current_price)
            if macd_result.golden_cross_price:
                # 如果当前已金叉（golden_cross_price为None或小于当前价）
                if macd_state.dif <= macd_state.signal:
                    critical_prices.append({
                        "condition": "MACD金叉",
                        "target_price": macd_result.golden_cross_price,
                        "direction": "above",
                        "distance_pct": (macd_result.golden_cross_price - current_price) / current_price * 100
                    })
                    unsatisfied_conditions.append("MACD金叉")

        # 先计算均线结果
        ma_result = self.ma_solver.solve_trigger_prices(ma_state)
        ma_short_current = ma_result.ma_short_current
        ma_long_current = ma_result.ma_long_current
        is_bullish = ma_result.is_bullish

        # 均线上穿条件
        if conditions.get("maGolden"):
            if ma_result.golden_cross_price:
                if not is_bullish:
                    critical_prices.append({
                        "condition": "均线上穿",
                        "target_price": ma_result.golden_cross_price,
                        "direction": "above",
                        "distance_pct": (ma_result.golden_cross_price - current_price) / current_price * 100
                    })
                    unsatisfied_conditions.append("均线上穿")

        # 站上MA5条件
        if conditions.get("priceAboveMA5"):
            if ma_state.current_price < ma_short_current:  # 严格判断：当前价必须 >= MA5
                target = ma_short_current
                critical_prices.append({
                    "condition": "站上MA5",
                    "target_price": target,
                    "direction": "above",
                    "distance_pct": (target - current_price) / current_price * 100
                })
                unsatisfied_conditions.append("站上MA5")

        # 站上MA10条件
        if conditions.get("priceAboveMA10"):
            if ma_state.current_price < ma_long_current:  # 严格判断：当前价必须 >= MA10
                target = ma_long_current
                critical_prices.append({
                    "condition": "站上MA10",
                    "target_price": target,
                    "direction": "above",
                    "distance_pct": (target - current_price) / current_price * 100
                })
                unsatisfied_conditions.append("站上MA10")

        # KDJ超卖条件
        if conditions.get("kdjOversold"):
            kdj_result = self.kdj_solver.solve_trigger_prices(kdj_state)
            if kdj_result.oversold_price:
                if kdj_state.current_price > kdj_result.oversold_price:
                    critical_prices.append({
                        "condition": "KDJ超卖",
                        "target_price": kdj_result.oversold_price,
                        "direction": "below",
                        "distance_pct": (current_price - kdj_result.oversold_price) / current_price * 100
                    })
                    unsatisfied_conditions.append("KDJ超卖")

        # 找出最难满足的条件（最大距离）
        if critical_prices:
            # 买入条件需要价格上涨才能满足的
            above_conditions = [p for p in critical_prices if p["direction"] == "above"]
            below_conditions = [p for p in critical_prices if p["direction"] == "below"]

            # 计算有效区间
            min_price = current_price
            max_price = current_price * 2  # 上限设为当前价格2倍

            if above_conditions:
                # 需要突破最高价格
                highest = max(above_conditions, key=lambda x: x["target_price"])
                min_price = highest["target_price"]

            if below_conditions:
                # 需要跌破最低价格
                lowest = min(below_conditions, key=lambda x: x["target_price"])
                max_price = lowest["target_price"]

            return {
                "current_satisfied": len(unsatisfied_conditions) == 0,
                "price_min": round(min_price, 2),
                "price_max": round(max_price, 2),
                "unsatisfied_conditions": unsatisfied_conditions,
                "critical_prices": critical_prices
            }

        return {
            "current_satisfied": True,
            "message": "所有买入条件已满足"
        }

    def _calculate_stop_range(
        self,
        current_price: float,
        macd_state: MACDState,
        ma_state: MAState,
        kdj_state: KDJState,
        conditions: Dict[str, bool]
    ) -> Dict[str, Any]:
        """计算止损策略触发的价格区间"""

        triggered_conditions = []

        # MACD死叉
        if conditions.get("macdDeath"):
            if macd_state.dif < macd_state.signal:
                triggered_conditions.append("MACD死叉")

        # 先计算均线结果
        ma_result = self.ma_solver.solve_trigger_prices(ma_state)
        ma_short_current = ma_result.ma_short_current
        ma_long_current = ma_result.ma_long_current
        is_bullish = ma_result.is_bullish

        # 均线死叉
        if conditions.get("maDeath"):
            if not is_bullish:
                triggered_conditions.append("均线死叉")

        # 跌破MA5
        if conditions.get("priceBelowMA5"):
            if ma_state.current_price < ma_short_current:  # 严格判断
                triggered_conditions.append("跌破MA5")

        # 跌破MA10
        if conditions.get("priceBelowMA20"):
            if ma_state.current_price < ma_long_current:  # 严格判断
                triggered_conditions.append("跌破MA10")

        # 计算止损线（取最高的一条）
        stop_lines = []
        macd_result = self.macd_solver.solve_trigger_prices(macd_state, current_price)
        if macd_result.death_cross_price:
            stop_lines.append({"name": "MACD死叉", "price": macd_result.death_cross_price})

        if ma_result.death_cross_price:
            stop_lines.append({"name": "均线死叉", "price": ma_result.death_cross_price})

        if conditions.get("priceBelowMA5") and ma_short_current:
            stop_lines.append({"name": "MA5", "price": ma_short_current})

        if conditions.get("priceBelowMA20") and ma_long_current:
            stop_lines.append({"name": "MA10", "price": ma_long_current})

        stop_price = max([s["price"] for s in stop_lines]) if stop_lines else current_price * 0.9

        return {
            "current_triggered": len(triggered_conditions) > 0,
            "stop_price": round(stop_price, 2),
            "triggered_conditions": triggered_conditions,
            "distance_to_stop": round((current_price - stop_price) / current_price * 100, 2)
        }

    def calculate_from_prices(
        self,
        symbol: str,
        prices: List[float],
        current_price: float
    ) -> Optional[TriggerMatrix]:
        """
        从价格列表计算触发矩阵（便捷函数）
        
        Args:
            symbol: 股票代码
            prices: 历史收盘价列表，至少26个（用于计算MACD和均线）
            current_price: 当前价格
            
        Returns:
            TriggerMatrix 或 None（如果数据不足）
        """
        if len(prices) < 26:
            return None
        
        # 计算MACD状态（需要至少26日数据）
        # 简化：使用最近的价格计算EMA
        recent_prices = prices[-26:]
        
        # 初始化EMA（用简单平均）
        ema12_yest = sum(recent_prices[-13:-1]) / 12  # 简化计算
        ema26_yest = sum(recent_prices[-27:-1]) / 26 if len(recent_prices) >= 27 else sum(recent_prices) / len(recent_prices)
        
        # DIF和Signal
        dif_yest = ema12_yest - ema26_yest
        signal_yest = dif_yest  # 简化
        
        macd_state = MACDState(
            ema_12=ema12_yest,
            ema_26=ema26_yest,
            signal=signal_yest,
            dif=dif_yest,
            close=prices[-1]
        )
        
        # 计算均线状态
        ma_prices_short = prices[-5:-1]  # 4个价格用于5日均线
        ma_prices_long = prices[-10:-1]  # 9个价格用于10日均线
        
        ma_state = MAState(
            prices_short=ma_prices_short,
            prices_long=ma_prices_long,
            short_period=5,
            long_period=10,
            current_price=current_price
        )
        
        # 计算KDJ状态
        recent_9 = prices[-9:]
        h9 = max(recent_9)
        l9 = min(recent_9)
        
        # 初始化K、D值（简化）
        rsv_init = (prices[-2] - l9) / (h9 - l9) * 100 if h9 != l9 else 50
        k_yest = 50  # 简化初始化
        d_yest = 50
        
        kdj_state = KDJState(
            k_yest=k_yest,
            d_yest=d_yest,
            h9=h9,
            l9=l9,
            current_price=current_price
        )
        
        return self.calculate_trigger_matrix(symbol, current_price, macd_state, ma_state, kdj_state)
