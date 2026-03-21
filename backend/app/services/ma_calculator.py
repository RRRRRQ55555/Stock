"""
MA均线计算器 - 基于Tushare daily_basic数据

核心逻辑：
1. 从 daily_basic 获取前4个交易日收盘价
2. 获取今日实时价格（最新交易价）
3. 计算 MA5 = (前4日收盘价 + 今日实时价) / 5
4. 计算策略触发价格：
   - 买入触发价：今日需要涨到什么价格 >= MA5
   - 止损触发价：今日跌到什么价格 < MA5
"""

import pandas as pd
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class MA5Result:
    """MA5计算结果"""
    current_price: float          # 今日实时价格
    prev_4_closes: List[float]    # 前4日收盘价
    ma5_value: float              # MA5值
    is_above: bool                # 当前是否站上MA5
    
    # 触发价格计算
    buy_trigger_price: float      # 需要涨到此价才站上MA5
    buy_need_pct: float          # 需要涨多少百分比
    
    stop_trigger_price: float     # 跌到此价触发止损（跌破MA5）
    stop_need_pct: float         # 距离止损的百分比


class MA5Calculator:
    """MA5计算器 - 基于Tushare数据"""
    
    def __init__(self, tushare_pro):
        """
        初始化
        
        Args:
            tushare_pro: Tushare pro_api 实例
        """
        self.ts = tushare_pro
    
    def calculate_ma5(
        self, 
        symbol: str, 
        current_price: Optional[float] = None
    ) -> MA5Result:
        """
        计算MA5
        
        Args:
            symbol: 股票代码 (如 "600519.SS")
            current_price: 今日实时价格（不提供则自动获取）
            
        Returns:
            MA5Result 包含计算结果和触发价格
        """
        # 1. 获取前4个交易日收盘价
        prev_4_closes = self._get_prev_4_closes(symbol)
        
        # 2. 获取今日实时价格
        if current_price is None:
            current_price = self._get_current_price(symbol)
        
        # 3. 计算MA5
        ma5_value = (sum(prev_4_closes) + current_price) / 5
        
        # 4. 判断是否站上MA5
        is_above = current_price >= ma5_value
        
        # 5. 计算买入触发价格（需要涨到什么价格）
        # MA5 = (sum(prev_4) + P) / 5
        # P = MA5 * 5 - sum(prev_4)
        buy_trigger_price = (sum(prev_4_closes) * 4 / 4)  # 简化为前4日平均
        # 实际上：要让新的MA5 <= 当前价
        # 新的MA5 = (sum(prev_4_closes[1:]) + current_price) / 5
        # 等等，这里需要重新推导
        
        # 正确的买入触发价格计算：
        # 如果当前价 < MA5，需要涨到 MA5 才能站上
        if current_price < ma5_value:
            buy_trigger_price = ma5_value
            buy_need_pct = (ma5_value - current_price) / current_price * 100
        else:
            buy_trigger_price = current_price
            buy_need_pct = 0
        
        # 6. 计算止损触发价格（跌破MA5的价格）
        # 严格来说，当前价 >= MA5 时，跌破就是 < MA5
        # 但实际上当前价可能就是临界值
        stop_trigger_price = ma5_value
        if current_price > ma5_value:
            stop_need_pct = (current_price - ma5_value) / current_price * 100
        else:
            stop_need_pct = 0
        
        return MA5Result(
            current_price=current_price,
            prev_4_closes=prev_4_closes,
            ma5_value=ma5_value,
            is_above=is_above,
            buy_trigger_price=buy_trigger_price,
            buy_need_pct=buy_need_pct,
            stop_trigger_price=stop_trigger_price,
            stop_need_pct=stop_need_pct
        )
    
    def _get_prev_4_closes(self, symbol: str) -> List[float]:
        """
        获取前4个交易日收盘价
        
        从 daily_basic 获取：
        - trade_date: 交易日期
        - close: 当日收盘价
        
        取最近5条数据（今日+前4日），返回前4日的close
        """
        # 标准化代码
        ts_code = self._normalize_symbol(symbol)
        
        # 从 daily 接口获取最近5日数据（今日+前4日）
        # daily_basic 包含每日指标，也可以获取收盘价
        df = self.ts.daily(ts_code=ts_code, limit=5)
        
        if df is None or len(df) < 5:
            raise ValueError(f"无法获取 {symbol} 的历史数据，需要至少5个交易日")
        
        # 按日期升序排序（最早的在前）
        df = df.sort_values('trade_date')
        
        # 取前4日的收盘价（不包括今日）
        prev_4 = df['close'].iloc[:-1].tolist()
        
        return [float(p) for p in prev_4]
    
    def _get_current_price(self, symbol: str) -> float:
        """获取今日实时价格"""
        ts_code = self._normalize_symbol(symbol)
        
        # 获取今日数据
        from datetime import datetime
        today = datetime.now().strftime('%Y%m%d')
        df = self.ts.daily(ts_code=ts_code, trade_date=today)
        
        if df is None or df.empty:
            # 获取最新一条
            df = self.ts.daily(ts_code=ts_code, limit=1)
        
        if df is None or df.empty:
            raise ValueError(f"无法获取 {symbol} 的当前价格")
        
        return float(df['close'].iloc[0])
    
    def _normalize_symbol(self, symbol: str) -> str:
        """标准化股票代码为Tushare格式"""
        if '.' in symbol:
            code, exchange = symbol.split('.')
            if exchange == 'SS':
                return f"{code}.SH"
            return symbol
        return symbol


# ============ 策略触发价格计算 ============

def calculate_strategy_triggers(
    prev_4_closes: List[float],
    current_price: float
) -> Dict[str, Any]:
    """
    计算策略触发价格
    
    基于前4日收盘价和当前价，计算：
    1. 当前MA5值
    2. 需要涨到什么价格才站上MA5
    3. 跌到什么价格触发止损
    
    推导过程：
    MA5(today) = (close[-4] + close[-3] + close[-2] + close[-1] + P) / 5
    
    其中：
    - close[-4] 到 close[-1] 是前4日收盘价（已知）
    - P 是今日价格（变量）
    
    站上MA5条件：
    P >= MA5
    P >= (sum(prev_4) + P) / 5
    5P >= sum(prev_4) + P
    4P >= sum(prev_4)
    P >= sum(prev_4) / 4
    
    所以：
    - 只要今日价 >= 前4日平均收盘价，就站上MA5
    - 这是动态变化的，每个交易日的MA5都不同
    """
    sum_prev_4 = sum(prev_4_closes)
    ma5 = (sum_prev_4 + current_price) / 5
    
    # 站上MA5的临界价格
    # P >= sum(prev_4) / 4
    threshold_for_buy = sum_prev_4 / 4
    
    # 当前是否站上
    is_above = current_price >= ma5
    
    # 需要涨多少才能站上
    if current_price < ma5:
        buy_trigger = ma5
        buy_need_pct = (ma5 - current_price) / current_price * 100
    else:
        buy_trigger = current_price
        buy_need_pct = 0
    
    # 止损触发价（跌破MA5）
    stop_trigger = ma5
    if current_price > ma5:
        stop_need_pct = (current_price - ma5) / current_price * 100
    else:
        stop_need_pct = 0
    
    return {
        "prev_4_closes": prev_4_closes,
        "sum_prev_4": sum_prev_4,
        "avg_prev_4": sum_prev_4 / 4,
        "current_price": current_price,
        "ma5": ma5,
        "is_above": is_above,
        "buy_trigger_price": buy_trigger,
        "buy_need_pct": buy_need_pct,
        "stop_trigger_price": stop_trigger,
        "stop_need_pct": stop_need_pct
    }


# ============ 使用示例 ============

if __name__ == "__main__":
    import tushare as ts
    
    # 设置Tushare token
    ts.set_token("你的token")
    pro = ts.pro_api()
    
    # 创建计算器
    calc = MA5Calculator(pro)
    
    # 计算贵州茅台MA5
    result = calc.calculate_ma5("600519.SH")
    
    print(f"\n=== 贵州茅台 MA5 分析 ===")
    print(f"前4日收盘价: {result.prev_4_closes}")
    print(f"今日实时价: {result.current_price}")
    print(f"MA5值: {result.ma5_value:.2f}")
    print(f"是否站上MA5: {'是' if result.is_above else '否'}")
    print(f"\n买入触发价: {result.buy_trigger_price:.2f} (需涨 {result.buy_need_pct:.2f}%)")
    print(f"止损触发价: {result.stop_trigger_price:.2f} (距离 {result.stop_need_pct:.2f}%)")
