"""
技术指标求解器基类

提供统一的接口和扩展机制，便于添加新的技术指标
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TriggerResult:
    """统一的触发结果格式"""
    indicator_name: str
    current_value: float
    current_price: float
    
    # 临界价格
    bullish_trigger_price: Optional[float] = None  # 看涨/买入触发价
    bearish_trigger_price: Optional[float] = None  # 看跌/卖出触发价
    
    # 距离信息
    distance_to_bullish: Optional[float] = None  # 距离看涨触发的百分比
    distance_to_bearish: Optional[float] = None  # 距离看跌触发的百分比
    
    # 当前状态
    zone: str = "neutral"  # 当前区域: oversold, neutral, overbought, bullish, bearish
    
    # 额外信息
    metadata: Dict[str, Any] = None  # 指标特定的额外数据
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        
        # 计算距离
        if self.bullish_trigger_price is not None and self.current_price > 0:
            self.distance_to_bullish = (
                (self.bullish_trigger_price - self.current_price) / self.current_price * 100
            )
        if self.bearish_trigger_price is not None and self.current_price > 0:
            self.distance_to_bearish = (
                (self.bearish_trigger_price - self.current_price) / self.current_price * 100
            )


@dataclass
class SimulationResult:
    """压力测试结果"""
    hypothetical_price: float
    indicator_value: float
    zone: str
    is_bullish: bool
    is_bearish: bool
    metadata: Dict[str, Any] = None


class BaseSolver(ABC):
    """
    技术指标求解器基类
    
    所有新的技术指标求解器都应该继承此类
    """
    
    # 指标名称（必须唯一）
    name: str = "base"
    
    # 指标中文名称
    display_name: str = "基础指标"
    
    # 指标描述
    description: str = "技术指标基础类"
    
    # 默认参数
    default_params: Dict[str, Any] = {}
    
    def __init__(self, **params):
        """
        初始化求解器
        
        Args:
            **params: 指标特定参数，覆盖默认值
        """
        self.params = {**self.default_params, **params}
    
    @abstractmethod
    def calculate(self, prices: List[float], current_price: float) -> float:
        """
        计算当前指标值
        
        Args:
            prices: 历史价格列表
            current_price: 当前价格
            
        Returns:
            指标值
        """
        pass
    
    @abstractmethod
    def solve_trigger_prices(
        self,
        prices: List[float],
        current_price: float
    ) -> TriggerResult:
        """
        求解临界价格
        
        Args:
            prices: 历史价格列表
            current_price: 当前价格
            
        Returns:
            TriggerResult 包含临界价格信息
        """
        pass
    
    @abstractmethod
    def simulate(self, prices: List[float], hypothetical_price: float) -> SimulationResult:
        """
        压力测试：模拟假设价格下的指标值
        
        Args:
            prices: 历史价格列表
            hypothetical_price: 假设价格
            
        Returns:
            SimulationResult
        """
        pass
    
    def get_required_history_length(self) -> int:
        """
        获取计算所需的最小历史数据长度
        
        Returns:
            最小数据长度
        """
        return 1
    
    def validate_prices(self, prices: List[float]) -> bool:
        """
        验证价格数据是否满足计算要求
        
        Args:
            prices: 价格列表
            
        Returns:
            是否有效
        """
        if not prices or len(prices) < self.get_required_history_length():
            return False
        return all(isinstance(p, (int, float)) and p > 0 for p in prices)


class IndicatorRegistry:
    """指标注册表 - 管理所有可用的技术指标求解器"""
    
    _solvers: Dict[str, type] = {}
    
    @classmethod
    def register(cls, solver_class: type):
        """
        注册求解器类
        
        用法：
            @IndicatorRegistry.register
            class RSISolver(BaseSolver):
                name = "rsi"
        """
        if not issubclass(solver_class, BaseSolver):
            raise ValueError(f"求解器必须继承 BaseSolver: {solver_class}")
        
        name = solver_class.name
        if name in cls._solvers:
            raise ValueError(f"指标名称已存在: {name}")
        
        cls._solvers[name] = solver_class
        return solver_class
    
    @classmethod
    def get_solver(cls, name: str) -> Optional[type]:
        """获取求解器类"""
        return cls._solvers.get(name)
    
    @classmethod
    def create_solver(cls, name: str, **params) -> Optional[BaseSolver]:
        """
        创建求解器实例
        
        Args:
            name: 指标名称
            **params: 初始化参数
            
        Returns:
            求解器实例或None
        """
        solver_class = cls.get_solver(name)
        if solver_class:
            return solver_class(**params)
        return None
    
    @classmethod
    def list_solvers(cls) -> List[Dict[str, str]]:
        """列出所有可用的求解器"""
        return [
            {
                "name": name,
                "display_name": solver.display_name,
                "description": solver.description
            }
            for name, solver in cls._solvers.items()
        ]
    
    @classmethod
    def get_all_solvers(cls, **default_params) -> Dict[str, BaseSolver]:
        """
        获取所有求解器实例
        
        Args:
            **default_params: 默认参数
            
        Returns:
            名称到求解器实例的字典
        """
        return {
            name: solver_class(**default_params)
            for name, solver_class in cls._solvers.items()
        }


def calculate_all_indicators(
    prices: List[float],
    current_price: float,
    solvers: Dict[str, BaseSolver] = None
) -> Dict[str, TriggerResult]:
    """
    计算所有指标的临界价格
    
    Args:
        prices: 历史价格列表
        current_price: 当前价格
        solvers: 求解器字典（默认使用所有注册的求解器）
        
    Returns:
        指标名称到触发结果的字典
    """
    if solvers is None:
        solvers = IndicatorRegistry.get_all_solvers()
    
    results = {}
    for name, solver in solvers.items():
        try:
            if solver.validate_prices(prices):
                result = solver.solve_trigger_prices(prices, current_price)
                results[name] = result
        except Exception as e:
            print(f"计算 {name} 失败: {e}")
    
    return results


def detect_resonance_zones(
    results: Dict[str, TriggerResult],
    threshold_pct: float = 2.0
) -> List[Dict[str, Any]]:
    """
    检测多指标共振区间
    
    Args:
        results: 所有指标的触发结果
        threshold_pct: 价格重合阈值（百分比）
        
    Returns:
        共振区间列表
    """
    # 收集所有临界价格
    critical_prices = []
    
    for name, result in results.items():
        if result.bullish_trigger_price:
            critical_prices.append((
                f"{name}_bullish",
                result.bullish_trigger_price,
                result.distance_to_bullish
            ))
        if result.bearish_trigger_price:
            critical_prices.append((
                f"{name}_bearish",
                result.bearish_trigger_price,
                result.distance_to_bearish
            ))
    
    if len(critical_prices) < 2:
        return []
    
    # 按价格排序
    critical_prices.sort(key=lambda x: x[1])
    
    # 滑动窗口找共振
    zones = []
    i = 0
    while i < len(critical_prices):
        cluster = [critical_prices[i]]
        j = i + 1
        
        while j < len(critical_prices):
            cluster_center = sum(p[1] for p in cluster) / len(cluster)
            if abs(critical_prices[j][1] - cluster_center) / cluster_center <= threshold_pct / 100:
                cluster.append(critical_prices[j])
                j += 1
            else:
                break
        
        if len(cluster) >= 2:
            prices = [p[1] for p in cluster]
            zone = {
                "type": "resonance",
                "indicators": [p[0] for p in cluster],
                "price_min": round(min(prices), 2),
                "price_max": round(max(prices), 2),
                "price_center": round(sum(prices) / len(prices), 2),
                "confidence": min(len(cluster) * 0.15, 0.95),
            }
            zones.append(zone)
        
        i = j
    
    return zones
