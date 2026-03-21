"""
Ichimoku Cloud (一目均衡表) 反向求解器

复杂的趋势判断系统，包含五线：
1.  Tenkan-sen (转换线) = (最近9日最高 + 最近9日最低) / 2
2.  Kijun-sen (基准线) = (最近26日最高 + 最近26日最低) / 2
3.  Senkou Span A (先行上线A) = (转换线 + 基准线) / 2，向前偏移26日
4.  Senkou Span B (先行上线B) = (最近52日最高 + 最近52日最低) / 2，向前偏移26日
5.  Chikou Span (迟行线) = 当日收盘价，向后偏移26日

云 (Kumo) = Span A 和 Span B 之间的区域
- 价格在云上方：看涨
- 价格在云下方：看跌
- 价格在云内：震荡

穿越信号：
- 转换线上穿基准线：看涨信号 (Tenkan-Kijun Cross)
- 价格上穿云：看涨突破 (Kumo Breakout)
"""

import numpy as np
from typing import List, Optional, Dict, Any
from .base_solver import BaseSolver, TriggerResult, SimulationResult, IndicatorRegistry


@IndicatorRegistry.register
class IchimokuSolver(BaseSolver):
    """Ichimoku Cloud 反向求解器"""
    
    name = "ichimoku"
    display_name = "Ichimoku Cloud (一目均衡表)"
    description = "综合趋势判断系统，提供支撑阻力、趋势方向和交易信号"
    
    default_params = {
        "tenkan_period": 9,    # 转换线周期
        "kijun_period": 26,    # 基准线周期
        "senkou_b_period": 52,  # 先行上线B周期
    }
    
    def get_required_history_length(self) -> int:
        return self.params["senkou_b_period"] + 26  # 需要52日数据 + 偏移
    
    def calculate(
        self,
        prices: List[float],
        current_price: float,
        highs: List[float] = None,
        lows: List[float] = None
    ) -> Dict[str, float]:
        """
        计算 Ichimoku 各线数值
        
        简化版本：使用收盘价近似高低点
        """
        tenkan_period = self.params["tenkan_period"]
        kijun_period = self.params["kijun_period"]
        senkou_b_period = self.params["senkou_b_period"]
        
        full_prices = prices + [current_price]
        
        # 转换线 (Tenkan-sen)
        tenkan_high = max(full_prices[-tenkan_period:]) if len(full_prices) >= tenkan_period else max(full_prices)
        tenkan_low = min(full_prices[-tenkan_period:]) if len(full_prices) >= tenkan_period else min(full_prices)
        tenkan_sen = (tenkan_high + tenkan_low) / 2
        
        # 基准线 (Kijun-sen)
        kijun_high = max(full_prices[-kijun_period:]) if len(full_prices) >= kijun_period else max(full_prices)
        kijun_low = min(full_prices[-kijun_period:]) if len(full_prices) >= kijun_period else min(full_prices)
        kijun_sen = (kijun_high + kijun_low) / 2
        
        # 先行上线A (Senkou Span A) - 当前计算的简化版（实际应偏移26日）
        senkou_span_a = (tenkan_sen + kijun_sen) / 2
        
        # 先行上线B (Senkou Span B)
        senkou_b_high = max(full_prices[-senkou_b_period:]) if len(full_prices) >= senkou_b_period else max(full_prices)
        senkou_b_low = min(full_prices[-senkou_b_period:]) if len(full_prices) >= senkou_b_period else min(full_prices)
        senkou_span_b = (senkou_b_high + senkou_b_low) / 2
        
        # 云的范围
        cloud_top = max(senkou_span_a, senkou_span_b)
        cloud_bottom = min(senkou_span_a, senkou_span_b)
        
        return {
            "tenkan_sen": tenkan_sen,
            "kijun_sen": kijun_sen,
            "senkou_span_a": senkou_span_a,
            "senkou_span_b": senkou_span_b,
            "cloud_top": cloud_top,
            "cloud_bottom": cloud_bottom,
        }
    
    def solve_trigger_prices(
        self,
        prices: List[float],
        current_price: float
    ) -> TriggerResult:
        """
        求解 Ichimoku 临界价格
        
        关键信号：
        1. 价格上穿云顶：看涨突破
        2. 价格下穿云底：看跌突破
        3. 转换线上穿基准线：短期看涨信号
        """
        ichimoku = self.calculate(prices, current_price)
        
        tenkan_sen = ichimoku["tenkan_sen"]
        kijun_sen = ichimoku["kijun_sen"]
        cloud_top = ichimoku["cloud_top"]
        cloud_bottom = ichimoku["cloud_bottom"]
        
        # 判断当前位置
        if current_price > cloud_top:
            current_position = "above_cloud"
        elif current_price < cloud_bottom:
            current_position = "below_cloud"
        else:
            current_position = "inside_cloud"
        
        # 判断转换线与基准线关系
        if tenkan_sen > kijun_sen:
            tk_position = "tenkan_above_kijun"  # 看涨
        else:
            tk_position = "tenkan_below_kijun"  # 看跌
        
        # 计算临界价格
        bullish_price = None
        bearish_price = None
        
        # 云上穿突破（主要看涨信号）
        if current_position != "above_cloud":
            bullish_price = cloud_top * 1.005  # 略上穿云顶
        
        # 云下穿突破（主要看跌信号）
        if current_position != "below_cloud":
            bearish_price = cloud_bottom * 0.995  # 略下穿云底
        
        # 转换线上穿基准线（次要信号）
        if tk_position == "tenkan_below_kijun":
            # 计算转换线上穿基准线的价格
            # 简化为转换线接近基准线时的价格
            if bullish_price is None or bullish_price > cloud_bottom:
                bullish_price = kijun_sen * 1.002
        
        # 确定区域
        if current_position == "above_cloud":
            if tk_position == "tenkan_above_kijun":
                zone = "strong_bullish"
            else:
                zone = "bullish_with_warning"
        elif current_position == "below_cloud":
            if tk_position == "tenkan_below_kijun":
                zone = "strong_bearish"
            else:
                zone = "bearish_with_warning"
        else:
            zone = "inside_cloud_consolidating"
        
        return TriggerResult(
            indicator_name=self.name,
            current_value=tenkan_sen,  # 使用转换线作为代表值
            current_price=current_price,
            bullish_trigger_price=round(bullish_price, 2) if bullish_price else None,
            bearish_trigger_price=round(bearish_price, 2) if bearish_price else None,
            zone=zone,
            metadata={
                "tenkan_sen": round(tenkan_sen, 2),
                "kijun_sen": round(kijun_sen, 2),
                "cloud_top": round(cloud_top, 2),
                "cloud_bottom": round(cloud_bottom, 2),
                "cloud_thickness": round(cloud_top - cloud_bottom, 2),
                "tk_cross": tk_position,
                "price_position": current_position,
            }
        )
    
    def simulate(self, prices: List[float], hypothetical_price: float) -> SimulationResult:
        """压力测试"""
        ichimoku = self.calculate(prices, hypothetical_price)
        
        cloud_top = ichimoku["cloud_top"]
        cloud_bottom = ichimoku["cloud_bottom"]
        tenkan_sen = ichimoku["tenkan_sen"]
        kijun_sen = ichimoku["kijun_sen"]
        
        # 判断云位置
        if hypothetical_price > cloud_top:
            zone = "above_cloud"
            is_bullish = True
            is_bearish = False
        elif hypothetical_price < cloud_bottom:
            zone = "below_cloud"
            is_bullish = False
            is_bearish = True
        else:
            zone = "inside_cloud"
            is_bullish = False
            is_bearish = False
        
        return SimulationResult(
            hypothetical_price=hypothetical_price,
            indicator_value=tenkan_sen,
            zone=zone,
            is_bullish=is_bullish,
            is_bearish=is_bearish,
            metadata={
                "cloud_top": round(cloud_top, 2),
                "cloud_bottom": round(cloud_bottom, 2),
                "tk_cross_bullish": tenkan_sen > kijun_sen,
            }
        )
