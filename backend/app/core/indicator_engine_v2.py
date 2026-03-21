"""
技术指标引擎 V2

使用可扩展的指标求解器架构，支持任意数量的技术指标
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np

from .base_solver import (
    IndicatorRegistry, BaseSolver, TriggerResult,
    calculate_all_indicators, detect_resonance_zones
)

# 导入所有求解器以完成注册
from .rsi_solver import RSISolver
from .bollinger_solver import BollingerSolver
from .volume_solver import VolumeSolver
from .cci_solver import CCISolver
from .atr_solver import ATRSolver
from .adx_solver import ADXSolver
from .stochastic_solver import StochasticSolver
from .momentum_solver import MomentumSolver
from .parabolic_sar_solver import ParabolicSARSolver
from .ichimoku_solver import IchimokuSolver

# 保留原有求解器导入
from .macd_solver import MACDSolver, MACDState
from .ma_solver import MASolver, MAState
from .kdj_solver import KDJolver, KDJState


@dataclass
class EnhancedTriggerMatrix:
    """
    增强版触发矩阵
    
    支持任意数量的技术指标
    """
    symbol: str
    current_price: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    # 各指标结果
    indicators: Dict[str, TriggerResult] = field(default_factory=dict)
    
    # 共振区间
    resonance_zones: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "symbol": self.symbol,
            "current_price": self.current_price,
            "timestamp": self.timestamp.isoformat(),
            "indicators": {},
            "resonance": self.resonance_zones,
            "summary": self._generate_summary()
        }
        
        # 转换各指标结果
        for name, indicator_result in self.indicators.items():
            result["indicators"][name] = {
                "current_value": round(indicator_result.current_value, 4),
                "current_price": indicator_result.current_price,
                "bullish_trigger_price": indicator_result.bullish_trigger_price,
                "bearish_trigger_price": indicator_result.bearish_trigger_price,
                "distance_to_bullish": indicator_result.distance_to_bullish,
                "distance_to_bearish": indicator_result.distance_to_bearish,
                "zone": indicator_result.zone,
                "metadata": indicator_result.metadata
            }
        
        return result
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成汇总信息"""
        bullish_count = sum(
            1 for r in self.indicators.values()
            if r.zone in ["oversold", "below_vwap", "below_cloud", "strong_up"]
        )
        bearish_count = sum(
            1 for r in self.indicators.values()
            if r.zone in ["overbought", "above_vwap", "above_cloud", "strong_down"]
        )
        neutral_count = len(self.indicators) - bullish_count - bearish_count
        
        # 找出距离最近的看涨/看跌触发价
        closest_bullish = None
        closest_bearish = None
        
        for r in self.indicators.values():
            if r.bullish_trigger_price and r.distance_to_bullish is not None:
                if closest_bullish is None or abs(r.distance_to_bullish) < abs(closest_bullish["distance"]):
                    closest_bullish = {
                        "indicator": r.indicator_name,
                        "price": r.bullish_trigger_price,
                        "distance": r.distance_to_bullish
                    }
            
            if r.bearish_trigger_price and r.distance_to_bearish is not None:
                if closest_bearish is None or abs(r.distance_to_bearish) < abs(closest_bearish["distance"]):
                    closest_bearish = {
                        "indicator": r.indicator_name,
                        "price": r.bearish_trigger_price,
                        "distance": r.distance_to_bearish
                    }
        
        return {
            "total_indicators": len(self.indicators),
            "bullish_signals": bullish_count,
            "bearish_signals": bearish_count,
            "neutral_signals": neutral_count,
            "overall_sentiment": (
                "bullish" if bullish_count > bearish_count + 2 else
                "bearish" if bearish_count > bullish_count + 2 else
                "neutral"
            ),
            "closest_bullish_trigger": closest_bullish,
            "closest_bearish_trigger": closest_bearish,
        }


class EnhancedIndicatorEngine:
    """增强版技术指标计算引擎"""
    
    def __init__(self, selected_indicators: List[str] = None):
        """
        初始化引擎
        
        Args:
            selected_indicators: 选中的指标列表，None表示使用所有可用指标
        """
        # 获取所有可用求解器
        all_solvers = IndicatorRegistry.get_all_solvers()
        
        # 过滤选中的指标
        if selected_indicators:
            self.solvers = {
                name: solver
                for name, solver in all_solvers.items()
                if name in selected_indicators
            }
        else:
            self.solvers = all_solvers
        
        self.selected_indicators = list(self.solvers.keys())
    
    def calculate_trigger_matrix(
        self,
        symbol: str,
        prices: List[float],
        current_price: float
    ) -> EnhancedTriggerMatrix:
        """
        计算完整的触发矩阵
        
        Args:
            symbol: 股票代码
            prices: 历史价格列表
            current_price: 当前价格
            
        Returns:
            EnhancedTriggerMatrix
        """
        # 计算所有指标的临界价格
        indicators = {}
        
        for name, solver in self.solvers.items():
            try:
                if solver.validate_prices(prices):
                    result = solver.solve_trigger_prices(prices, current_price)
                    indicators[name] = result
            except Exception as e:
                print(f"计算 {name} 失败: {e}")
        
        # 检测共振区间
        resonance = detect_resonance_zones(indicators)
        
        return EnhancedTriggerMatrix(
            symbol=symbol,
            current_price=current_price,
            indicators=indicators,
            resonance_zones=resonance
        )
    
    def stress_test(
        self,
        prices: List[float],
        hypothetical_price: float
    ) -> Dict[str, Any]:
        """
        压力测试
        
        Args:
            prices: 历史价格列表
            hypothetical_price: 假设价格
            
        Returns:
            压力测试结果
        """
        results = {}
        
        for name, solver in self.solvers.items():
            try:
                if solver.validate_prices(prices):
                    sim_result = solver.simulate(prices, hypothetical_price)
                    results[name] = {
                        "hypothetical_price": sim_result.hypothetical_price,
                        "indicator_value": round(sim_result.indicator_value, 4),
                        "zone": sim_result.zone,
                        "is_bullish": sim_result.is_bullish,
                        "is_bearish": sim_result.is_bearish,
                        "metadata": sim_result.metadata
                    }
            except Exception as e:
                print(f"压力测试 {name} 失败: {e}")
        
        # 汇总
        bullish_count = sum(1 for r in results.values() if r["is_bullish"])
        bearish_count = sum(1 for r in results.values() if r["is_bearish"])
        
        return {
            "hypothetical_price": hypothetical_price,
            "indicators": results,
            "summary": {
                "bullish_signals": bullish_count,
                "bearish_signals": bearish_count,
                "overall": (
                    "bullish" if bullish_count > bearish_count else
                    "bearish" if bearish_count > bullish_count else
                    "neutral"
                )
            }
        }
    
    @staticmethod
    def list_available_indicators() -> List[Dict[str, str]]:
        """列出所有可用的技术指标"""
        return IndicatorRegistry.list_solvers()


# 向后兼容：保留原有 IndicatorEngine 的接口
class IndicatorEngine:
    """原有指标引擎（保持向后兼容）"""
    
    def __init__(
        self,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        ma_short: int = 5,
        ma_long: int = 20,
        kdj_period: int = 9
    ):
        """初始化原有引擎"""
        # 原有求解器
        self.macd_solver = MACDSolver(macd_fast, macd_slow, macd_signal)
        self.ma_solver = MASolver(ma_short, ma_long)
        self.kdj_solver = KDJolver(kdj_period)
        
        # 新增：增强版引擎（包含所有指标）
        self.enhanced_engine = EnhancedIndicatorEngine()
    
    def calculate_trigger_matrix(self, *args, **kwargs):
        """原有接口"""
        # 如果有增强版引擎的结果，转换为原有格式
        if len(args) >= 3 and isinstance(args[2], list):
            # 新接口：calculate_trigger_matrix(symbol, prices, current_price)
            return self.enhanced_engine.calculate_trigger_matrix(*args)
        else:
            # 旧接口：保持原有逻辑
            from .indicator_engine import IndicatorEngine as OldEngine
            old_engine = OldEngine()
            return old_engine.calculate_trigger_matrix(*args, **kwargs)
    
    def stress_test(self, prices: List[float], hypothetical_price: float):
        """压力测试新接口"""
        return self.enhanced_engine.stress_test(prices, hypothetical_price)
