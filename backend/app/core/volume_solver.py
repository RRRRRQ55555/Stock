"""
成交量指标求解器

包含：
1. OBV (On-Balance Volume) - 能量潮
2. VWAP (Volume-Weighted Average Price) - 成交量加权平均价
3. Volume Ratio - 量比
"""

import numpy as np
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from .base_solver import BaseSolver, TriggerResult, SimulationResult, IndicatorRegistry


@dataclass
class VolumeData:
    """成交量数据结构"""
    volume: int
    price: float


@IndicatorRegistry.register
class VolumeSolver(BaseSolver):
    """成交量指标求解器"""
    
    name = "volume"
    display_name = "成交量指标 (OBV/VWAP)"
    description = "量价分析，判断资金流向和支撑压力位"
    
    default_params = {
        "vwap_period": 20,  # VWAP计算周期
        "volume_ma_period": 5,  # 成交量均线周期
    }
    
    def get_required_history_length(self) -> int:
        return max(self.params["vwap_period"], self.params["volume_ma_period"]) + 1
    
    def calculate_vwap(
        self,
        prices: List[float],
        volumes: List[int],
        current_price: float,
        current_volume: int = None
    ) -> float:
        """
        计算 VWAP (Volume-Weighted Average Price)
        
        VWAP = Σ(Price × Volume) / Σ(Volume)
        """
        period = self.params["vwap_period"]
        
        # 使用典型价格 (High + Low + Close) / 3，这里简化为 Close
        if current_volume is None:
            # 如果没有当前成交量，使用历史平均
            current_volume = int(np.mean(volumes[-period:]))
        
        # 取最近 period 个数据
        recent_prices = prices[-period+1:] + [current_price]
        recent_volumes = volumes[-period+1:] + [current_volume]
        
        # 计算 VWAP
        tpv = sum(p * v for p, v in zip(recent_prices, recent_volumes))
        total_volume = sum(recent_volumes)
        
        return tpv / total_volume if total_volume > 0 else current_price
    
    def calculate_obv(
        self,
        prices: List[float],
        volumes: List[int],
        current_price: float,
        current_volume: int = None
    ) -> float:
        """
        计算 OBV (On-Balance Volume)
        
        今日OBV = 昨日OBV + sgn(今日收盘价 - 昨日收盘价) × 今日成交量
        """
        if current_volume is None:
            current_volume = int(np.mean(volumes[-5:])) if volumes else 0
        
        obv = 0
        full_prices = prices + [current_price]
        full_volumes = volumes + [current_volume]
        
        for i in range(1, len(full_prices)):
            if full_prices[i] > full_prices[i-1]:
                obv += full_volumes[i]
            elif full_prices[i] < full_prices[i-1]:
                obv -= full_volumes[i]
            # 相等时 OBV 不变
        
        return float(obv)
    
    def calculate_volume_ratio(
        self,
        volumes: List[int],
        current_volume: int = None
    ) -> float:
        """
        计算量比 (Volume Ratio)
        
        量比 = 当日成交量 / 过去N日平均成交量
        """
        period = self.params["volume_ma_period"]
        
        if len(volumes) < period:
            return 1.0
        
        avg_volume = np.mean(volumes[-period:])
        
        if current_volume is None:
            current_volume = volumes[-1] if volumes else avg_volume
        
        return current_volume / avg_volume if avg_volume > 0 else 1.0
    
    def calculate(self, prices: List[float], current_price: float) -> float:
        """
        返回价格相对于 VWAP 的偏离百分比作为指标值
        """
        # 由于没有外部传入成交量，这里使用模拟的成交量数据
        # 实际使用时应该从数据源获取
        volumes = self._estimate_volumes(prices)
        
        vwap = self.calculate_vwap(prices, volumes, current_price)
        
        # 返回价格偏离 VWAP 的百分比
        return ((current_price - vwap) / vwap * 100) if vwap != 0 else 0
    
    def _estimate_volumes(self, prices: List[float]) -> List[int]:
        """
        估计成交量（简化处理）
        
        实际应该从数据源获取真实成交量
        这里使用价格变动的绝对值作为成交量的代理
        """
        volumes = []
        for i in range(len(prices)):
            if i == 0:
                volumes.append(1000000)  # 基础成交量
            else:
                # 价格变动越大，成交量估计越高
                change = abs(prices[i] - prices[i-1]) / prices[i-1]
                base_vol = 1000000
                volumes.append(int(base_vol * (1 + change * 10)))
        return volumes
    
    def solve_trigger_prices(
        self,
        prices: List[float],
        current_price: float
    ) -> TriggerResult:
        """
        求解成交量指标临界价格
        
        主要关注 VWAP：
        - 价格跌破 VWAP = 资金流出/看跌信号
        - 价格升破 VWAP = 资金流入/看涨信号
        """
        volumes = self._estimate_volumes(prices)
        
        # 计算当前 VWAP
        vwap = self.calculate_vwap(prices, volumes, current_price)
        
        # 计算 OBV 趋势
        obv = self.calculate_obv(prices, volumes, current_price)
        
        # 计算量比
        volume_ratio = self.calculate_volume_ratio(volumes)
        
        # 计算临界价格
        # 假设成交量变化时，VWAP 会随之移动
        
        # 看涨临界：价格跌至 VWAP 下方一定比例（放量支撑位）
        # 如果当前价格高于 VWAP，计算跌至 VWAP 的价格
        if current_price > vwap:
            bullish_price = vwap * 0.995  # 略低于 VWAP
        else:
            bullish_price = None  # 已在 VWAP 下方
        
        # 看跌临界：价格升至 VWAP 上方一定比例（放量阻力位）
        if current_price < vwap:
            bearish_price = vwap * 1.005  # 略高于 VWAP
        else:
            bearish_price = None  # 已在 VWAP 上方
        
        # 确定当前区域
        deviation = (current_price - vwap) / vwap * 100
        if deviation > 2:
            zone = "above_vwap"  # VWAP上方，偏看涨
        elif deviation < -2:
            zone = "below_vwap"  # VWAP下方，偏看跌
        else:
            zone = "at_vwap"  # 接近VWAP
        
        return TriggerResult(
            indicator_name=self.name,
            current_value=deviation,
            current_price=current_price,
            bullish_trigger_price=bullish_price,
            bearish_trigger_price=bearish_price,
            zone=zone,
            metadata={
                "vwap": round(vwap, 2),
                "obv": round(obv, 0),
                "volume_ratio": round(volume_ratio, 2),
                "deviation_from_vwap": round(deviation, 2),
            }
        )
    
    def simulate(self, prices: List[float], hypothetical_price: float) -> SimulationResult:
        """压力测试"""
        volumes = self._estimate_volumes(prices)
        
        vwap = self.calculate_vwap(prices, volumes, hypothetical_price)
        deviation = (hypothetical_price - vwap) / vwap * 100
        
        return SimulationResult(
            hypothetical_price=hypothetical_price,
            indicator_value=deviation,
            zone="above_vwap" if deviation > 0 else "below_vwap",
            is_bullish=hypothetical_price < vwap * 0.98,  # 明显低于VWAP后反弹
            is_bearish=hypothetical_price > vwap * 1.02,  # 明显高于VWAP后回调
            metadata={
                "vwap": round(vwap, 2),
                "deviation": round(deviation, 2),
            }
        )
