"""
数据服务

提供股票数据获取、缓存和管理功能
支持 Tushare API 获取A股数据，Yahoo Finance 作为备选
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
from functools import lru_cache
import json
import os

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    # 尝试加载后端目录的 .env
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(backend_dir, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"[OK] 已加载环境变量: {env_path}")
    else:
        # 尝试当前目录
        load_dotenv()
except ImportError:
    pass  # python-dotenv 未安装

from ..models.schemas import PriceData, HistoricalDataResponse
from ..core.macd_solver import MACDState
from ..core.ma_solver import MAState
from ..core.kdj_solver import KDJState
from ..core.rsi_solver import RSIState
from ..core.boll_solver import BOLLState
from ..core.wr_solver import WRState
from ..core.cci_solver import CCIState

# 尝试导入 Tushare
try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False


@dataclass
class IndicatorSeedData:
    """
    指标种子数据
    
    用于计算临界价格所需的昨日收盘后的指标状态
    """
    macd: MACDState
    ma: MAState
    kdj: KDJState
    rsi: RSIState
    boll: BOLLState
    wr: WRState
    cci: CCIState
    last_close: float
    timestamp: datetime


class DataService:
    """数据服务"""
    
    def __init__(self, cache_dir: str = "./cache", tushare_token: str = None):
        """
        初始化数据服务
        
        Args:
            cache_dir: 本地缓存目录
            tushare_token: Tushare API Token (可选，优先使用环境变量 TUSHARE_TOKEN)
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # 内存缓存
        self._price_cache: Dict[str, Dict[str, Any]] = {}
        self._indicator_cache: Dict[str, IndicatorSeedData] = {}
        
        # 股票列表缓存
        self._stock_list: List[Dict[str, str]] = []
        self._stock_list_cache_time: Optional[datetime] = None
        self._stock_list_cache_duration: timedelta = timedelta(hours=24)  # 24小时刷新
        self._stock_index: Dict[str, List[int]] = {}  # 倒排索引: 字符 -> 股票索引列表
        
        # 请求控制
        self._last_request_time: Dict[str, float] = {}
        self._request_interval: float = 2.0  # 请求间隔2秒
        self._max_retries: int = 3  # 最大重试次数
        
        # 初始化 Tushare API（用于数据获取，不是搜索）
        self._tushare_pro = None
        self._tushare_enabled = False
        
        if TUSHARE_AVAILABLE:
            token = tushare_token or os.getenv("TUSHARE_TOKEN")
            if token:
                try:
                    ts.set_token(token)
                    self._tushare_pro = ts.pro_api()
                    self._tushare_enabled = True
                    print("[OK] Tushare API 初始化成功")
                except Exception as e:
                    print(f"[WARN] Tushare API 初始化失败: {e}")
            else:
                print("[INFO] 未配置 Tushare Token，使用Yahoo Finance获取数据")
    
    async def _load_stock_list_async(self):
        """异步加载股票列表"""
        try:
            await self._load_stock_list()
        except Exception as e:
            print(f"[WARN] 异步加载股票列表失败: {e}")
    
    def _load_stock_list(self) -> List[Dict[str, str]]:
        """
        加载股票列表到内存缓存
        
        优先从本地缓存加载，如果过期则从Tushare/API获取
        """
        # 检查内存缓存是否有效
        if self._stock_list and self._stock_list_cache_time:
            if datetime.now() - self._stock_list_cache_time < self._stock_list_cache_duration:
                return self._stock_list
        
        # 尝试从本地文件缓存加载
        cache_file = os.path.join(self.cache_dir, "stock_list.json")
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    cache_time = datetime.fromisoformat(cached_data.get('timestamp', '2000-01-01'))
                    
                    if datetime.now() - cache_time < self._stock_list_cache_duration:
                        self._stock_list = cached_data.get('stocks', [])
                        self._stock_list_cache_time = cache_time
                        self._build_search_index()
                        print(f"[OK] 从本地缓存加载 {len(self._stock_list)} 只股票")
                        return self._stock_list
        except Exception as e:
            print(f"[WARN] 读取本地缓存失败: {e}")
        
        # 从Tushare加载A股列表
        stocks = []
        if self._tushare_pro and self._tushare_enabled:
            try:
                print("[INFO] 正在从Tushare加载A股列表...")
                df = self._tushare_pro.stock_basic(
                    exchange='',
                    list_status='L',
                    fields='ts_code,symbol,name,area,industry,market,exchange,list_date'
                )
                
                if df is not None and not df.empty:
                    for _, row in df.iterrows():
                        exchange = "SSE" if row['exchange'] == "SSE" else "SZSE"
                        stocks.append({
                            "symbol": row['ts_code'],
                            "name": row['name'],
                            "exchange": exchange,
                            "area": row.get('area', ''),
                            "industry": row.get('industry', ''),
                            "market": row.get('market', ''),
                            "type": "A股"
                        })
                    print(f"[OK] 从Tushare加载 {len(stocks)} 只A股")
                else:
                    print("[WARN] Tushare返回空数据")
            except Exception as e:
                print(f"[WARN] Tushare加载股票列表失败: {e}")
                print("[INFO] 将使用内置股票列表作为备用")
        else:
            print("[INFO] Tushare未启用，使用内置股票列表")
        
        # 如果Tushare没有数据或失败，使用内置列表
        if not stocks:
            print("[INFO] 使用内置股票列表")
            stocks = self._get_builtin_stocks()
        else:
            # 添加常用港股
            hk_stocks = [
                {"symbol": "0700.HK", "name": "腾讯控股", "exchange": "HKEX", "type": "港股"},
                {"symbol": "3690.HK", "name": "美团", "exchange": "HKEX", "type": "港股"},
                {"symbol": "9988.HK", "name": "阿里巴巴-SW", "exchange": "HKEX", "type": "港股"},
                {"symbol": "2318.HK", "name": "中国平安", "exchange": "HKEX", "type": "港股"},
                {"symbol": "1299.HK", "name": "友邦保险", "exchange": "HKEX", "type": "港股"},
                {"symbol": "0005.HK", "name": "汇丰控股", "exchange": "HKEX", "type": "港股"},
                {"symbol": "0388.HK", "name": "香港交易所", "exchange": "HKEX", "type": "港股"},
                {"symbol": "2628.HK", "name": "中国人寿", "exchange": "HKEX", "type": "港股"},
            ]
            
            # 合并港股
            existing_symbols = {s['symbol'] for s in stocks}
            for stock in hk_stocks:
                if stock['symbol'] not in existing_symbols:
                    stocks.append(stock)
        
        # 更新内存缓存
        self._stock_list = stocks
        self._stock_list_cache_time = datetime.now()
        
        # 构建搜索索引
        self._build_search_index()
        
        # 保存到本地缓存
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'stocks': stocks
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[WARN] 保存股票列表缓存失败: {e}")
        
        return stocks
    
    def _build_search_index(self):
        """
        构建倒排索引加速搜索
        
        索引结构: {字符: [包含该字符的股票索引列表]}
        """
        self._stock_index = {}
        
        for idx, stock in enumerate(self._stock_list):
            # 索引股票代码和名称
            text_to_index = f"{stock['symbol']} {stock['name']}".lower()
            
            # 提取所有字符（包括中文单字）
            chars = set()
            for char in text_to_index:
                if char.isalnum() or '\u4e00' <= char <= '\u9fff':  # 字母数字或中文
                    chars.add(char)
            
            # 同时索引前缀（用于快速前缀匹配）
            words = text_to_index.split()
            for word in words:
                for i in range(1, min(len(word) + 1, 10)):  # 最多索引前10个字符
                    chars.add(word[:i])
            
            # 添加到倒排索引
            for char in chars:
                if char not in self._stock_index:
                    self._stock_index[char] = []
                self._stock_index[char].append(idx)
        
        print(f"[OK] 构建搜索索引完成，索引 {len(self._stock_index)} 个关键词")
    
    def _is_chinese_stock(self, symbol: str) -> bool:
        """判断是否为A股或港股"""
        # A股：6位数字，带.SH或.SZ后缀
        # 港股：.HK后缀
        if '.SH' in symbol or '.SZ' in symbol:
            return True
        if '.HK' in symbol:
            return True
        if symbol.endswith('.SS'):
            return True
        # 如果是纯6位数字，默认为A股
        if symbol.isdigit() and len(symbol) == 6:
            return True
        return False
    
    def _search_stocks_fast(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        使用倒排索引快速搜索股票（只返回A股和港股）
        
        时间复杂度: O(len(query) + 匹配结果数)
        比遍历全量数据快100倍以上
        """
        if not query or not self._stock_list:
            return []
        
        query_lower = query.lower().strip()
        
        # 如果缓存未加载，同步加载
        if not self._stock_list:
            self._load_stock_list()
        
        # 使用倒排索引查找
        if len(query_lower) >= 1:
            # 获取包含查询字符串的股票索引
            matched_indices = None
            
            # 优先完整匹配查询字符串
            if query_lower in self._stock_index:
                matched_indices = set(self._stock_index[query_lower])
            else:
                # 否则匹配所有字符的交集
                for char in query_lower:
                    if char in self._stock_index:
                        if matched_indices is None:
                            matched_indices = set(self._stock_index[char])
                        else:
                            matched_indices &= set(self._stock_index[char])
                    else:
                        # 有字符不在索引中，无匹配
                        return []
            
            if matched_indices is None:
                return []
            
            # 按相关性排序并过滤非中国股票
            results = []
            for idx in matched_indices:
                if idx < len(self._stock_list):
                    stock = self._stock_list[idx]
                    
                    # 只返回中国股票（A股和港股）
                    if not self._is_chinese_stock(stock['symbol']):
                        continue
                    
                    symbol_lower = stock['symbol'].lower()
                    name_lower = stock['name'].lower()
                    
                    # 计算相关性分数
                    score = 0
                    if query_lower == symbol_lower:
                        score = 100  # 代码完全匹配
                    elif query_lower == name_lower:
                        score = 90   # 名称完全匹配
                    elif symbol_lower.startswith(query_lower):
                        score = 80   # 代码前缀匹配
                    elif name_lower.startswith(query_lower):
                        score = 70   # 名称前缀匹配
                    elif query_lower in symbol_lower:
                        score = 60   # 代码包含
                    elif query_lower in name_lower:
                        score = 50   # 名称包含
                    
                    results.append((score, stock))
            
            # 按分数降序排序并限制数量
            results.sort(key=lambda x: x[0], reverse=True)
            return [stock for _, stock in results[:limit]]
        
        return []

    def _is_a_stock(self, symbol: str) -> bool:
        """
        判断是否为A股代码

        A股格式：
        - 6位数字 (如 000001, 600000)
        - 带交易所后缀 (如 000001.SZ, 600000.SH, 600000.SS)
        """
        # 去除后缀
        clean_symbol = symbol.split('.')[0]
        # 检查是否为6位数字
        return len(clean_symbol) == 6 and clean_symbol.isdigit()

    def _normalize_symbol(self, symbol: str) -> str:
        """
        标准化股票代码格式

        - .SS (Yahoo Finance) -> .SH (Tushare)
        - .SZ (通用) -> .SZ (Tushare)
        """
        if symbol.endswith('.SS'):
            return symbol.replace('.SS', '.SH')
        return symbol
    
    async def _rate_limited_request(self, symbol: str, request_func):
        """
        带频率限制的请求
        
        Args:
            symbol: 股票代码
            request_func: 请求函数
        """
        now = asyncio.get_event_loop().time()
        last_time = self._last_request_time.get(symbol, 0)
        
        # 等待直到满足请求间隔
        if now - last_time < self._request_interval:
            wait_time = self._request_interval - (now - last_time)
            await asyncio.sleep(wait_time)
        
        # 执行请求（带重试）
        for attempt in range(self._max_retries):
            try:
                self._last_request_time[symbol] = asyncio.get_event_loop().time()
                result = await request_func()
                return result
            except Exception as e:
                if "Rate limited" in str(e) or "Too Many Requests" in str(e):
                    if attempt < self._max_retries - 1:
                        wait_time = (attempt + 1) * 5  # 指数退避: 5s, 10s, 15s
                        print(f"Rate limited for {symbol}, waiting {wait_time}s before retry {attempt + 1}/{self._max_retries}")
                        await asyncio.sleep(wait_time)
                    else:
                        raise
                else:
                    raise
        
        raise ValueError(f"Max retries exceeded for {symbol}")
        
    def _convert_tushare_to_price_data(self, df: pd.DataFrame) -> List[PriceData]:
        """
        将 Tushare 数据格式转换为 PriceData 列表
        
        Tushare 日线数据字段：ts_code, trade_date, open, high, low, close, vol, amount...
        """
        price_data = []
        for _, row in df.iterrows():
            # Tushare 的 trade_date 格式是 YYYYMMDD
            if 'trade_date' in row:
                trade_date = str(int(row['trade_date']))
                timestamp = datetime.strptime(trade_date, '%Y%m%d')
            else:
                timestamp = datetime.now()
            
            price_data.append(PriceData(
                timestamp=timestamp,
                open=round(float(row['open']), 4),
                high=round(float(row['high']), 4),
                low=round(float(row['low']), 4),
                close=round(float(row['close']), 4),
                volume=int(float(row['vol'])) if 'vol' in row and not pd.isna(row['vol']) else None
            ))
        
        # 按日期升序排序（Tushare返回的是降序）
        price_data.sort(key=lambda x: x.timestamp)
        return price_data
    
    def _fetch_tushare_daily(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """
        使用 Tushare 获取A股日线数据

        Args:
            symbol: A股代码 (如 "000001.SZ" 或 "000001")
            period: 时间周期
        """
        if not self._tushare_pro:
            raise ValueError("Tushare API 未初始化")

        # 标准化代码格式 (.SS -> .SH)
        symbol = self._normalize_symbol(symbol)

        # 处理 symbol 格式
        ts_code = symbol
        if '.' not in symbol:
            # 根据股票代码前缀判断交易所
            if symbol.startswith('6'):
                ts_code = f"{symbol}.SH"
            else:
                ts_code = f"{symbol}.SZ"
        
        # 计算起始日期
        end_date = datetime.now()
        period_map = {
            "1mo": 30,
            "3mo": 90,
            "6mo": 180,
            "1y": 365,
            "2y": 730,
            "5y": 1825,
        }
        days = period_map.get(period, 365)
        start_date = end_date - timedelta(days=days)
        
        # 调用 Tushare API
        df = self._tushare_pro.daily(
            ts_code=ts_code,
            start_date=start_date.strftime('%Y%m%d'),
            end_date=end_date.strftime('%Y%m%d')
        )
        
        if df is None or df.empty:
            raise ValueError(f"Tushare 无法获取 {symbol} 的数据")
        
        return df
    
    async def get_historical_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> HistoricalDataResponse:
        """
        获取历史数据
        
        优先使用 Tushare 获取A股数据，Yahoo Finance 作为备选
        
        Args:
            symbol: 股票代码 (如 "000001.SZ" 或 "AAPL")
            period: 时间周期 (1mo, 3mo, 6mo, 1y, 2y, 5y)
            interval: 时间间隔 (1d)
            
        Returns:
            HistoricalDataResponse
        """
        async def _fetch():
            # 标准化代码
            normalized_symbol = self._normalize_symbol(symbol)

            # 如果是A股且 Tushare 已初始化，优先使用 Tushare
            if self._is_a_stock(normalized_symbol) and self._tushare_pro:
                try:
                    print(f"[INFO] 使用 Tushare 获取A股数据: {normalized_symbol}")
                    loop = asyncio.get_event_loop()
                    df = await loop.run_in_executor(
                        None,
                        lambda: self._fetch_tushare_daily(normalized_symbol, period)
                    )
                    price_data = self._convert_tushare_to_price_data(df)
                    
                    return HistoricalDataResponse(
                        symbol=symbol,
                        period=period,
                        interval=interval,
                        data=price_data
                    )
                except Exception as e:
                    print(f"[WARN] Tushare 获取失败，尝试 Yahoo Finance: {e}")
                    # 失败时回退到 Yahoo Finance
            
            # 使用 Yahoo Finance（美股或Tushare失败时）
            loop = asyncio.get_event_loop()
            ticker = yf.Ticker(symbol)
            df = await loop.run_in_executor(None, lambda: ticker.history(period=period, interval=interval))
            
            if df.empty:
                raise ValueError(f"无法获取 {symbol} 的数据")
            
            # 转换为 PriceData 列表
            price_data = []
            for timestamp, row in df.iterrows():
                price_data.append(PriceData(
                    timestamp=timestamp.to_pydatetime(),
                    open=round(row['Open'], 4),
                    high=round(row['High'], 4),
                    low=round(row['Low'], 4),
                    close=round(row['Close'], 4),
                    volume=int(row['Volume']) if not pd.isna(row['Volume']) else None
                ))
            
            return HistoricalDataResponse(
                symbol=symbol,
                period=period,
                interval=interval,
                data=price_data
            )
        
        try:
            return await self._rate_limited_request(symbol, _fetch)
        except Exception as e:
            raise ValueError(f"获取历史数据失败: {str(e)}")
    
    def _calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """计算EMA"""
        return prices.ewm(span=period, adjust=False).mean()
    
    def _calculate_macd(self, closes: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        计算 MACD
        
        Returns:
            (DIF, Signal, Histogram)
        """
        ema_12 = self._calculate_ema(closes, 12)
        ema_26 = self._calculate_ema(closes, 26)
        
        dif = ema_12 - ema_26
        signal = self._calculate_ema(dif, 9)
        histogram = dif - signal
        
        return dif, signal, histogram
    
    def _calculate_ma(self, closes: pd.Series, period: int) -> pd.Series:
        """计算简单移动平均"""
        return closes.rolling(window=period).mean()
    
    def _calculate_kdj(self, df: pd.DataFrame, period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        计算 KDJ
        
        Args:
            df: DataFrame 包含 High, Low, Close
            period: 计算周期
            
        Returns:
            (K, D, J)
        """
        # 计算 RSV
        low_list = df['Low'].rolling(window=period, min_periods=period).min()
        high_list = df['High'].rolling(window=period, min_periods=period).max()
        
        rsv = (df['Close'] - low_list) / (high_list - low_list) * 100
        
        # 计算 K, D
        K = rsv.ewm(com=2, adjust=False).mean()
        D = K.ewm(com=2, adjust=False).mean()
        
        # 计算 J
        J = 3 * K - 2 * D
        
        return K, D, J
    
    def _calculate_rsi(self, closes: pd.Series, period: int = 14) -> pd.DataFrame:
        """
        计算 RSI
        
        Args:
            closes: 收盘价序列
            period: 计算周期，默认14
            
        Returns:
            DataFrame 包含 RSI, avg_gain, avg_loss
        """
        # 计算价格变动
        delta = closes.diff()
        
        # 分离上涨和下跌
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # 使用 Wilder 的平滑方法
        avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
        avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()
        
        # 计算 RS 和 RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return pd.DataFrame({
            'rsi': rsi,
            'avg_gain': avg_gain,
            'avg_loss': avg_loss
        })
    
    def _calculate_boll(self, df: pd.DataFrame, period: int = 20, k: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        计算布林带 (BOLL)
        
        Args:
            df: DataFrame 包含 Close
            period: 周期，默认20
            k: 标准差倍数，默认2.0
            
        Returns:
            (中轨MB, 上轨UP, 下轨DN)
        """
        # 中轨 = N日简单移动平均
        mb = df['Close'].rolling(window=period).mean()
        
        # 计算标准差
        std = df['Close'].rolling(window=period).std()
        
        # 上轨和下轨
        up = mb + k * std
        dn = mb - k * std
        
        return mb, up, dn
    
    def _generate_mock_data(self, symbol: str) -> IndicatorSeedData:
        """
        生成模拟数据（用于API限流时的降级方案）
        
        生成合理的模拟价格数据用于测试
        """
        print(f"Using mock data for {symbol}")
        
        # 基础价格（根据symbol生成固定但合理的基准）
        base_price = hash(symbol) % 100 + 50  # 50-150范围内的价格
        
        # 模拟MACD状态
        macd_state = MACDState(
            ema_12=base_price * 1.02,
            ema_26=base_price * 0.98,
            signal=base_price * 0.99,
            dif=base_price * 0.04,
            close=base_price
        )
        
        # 模拟MA状态
        ma_state = MAState(
            prices_short=[base_price * (1 + i * 0.01) for i in range(-4, 0)],
            prices_long=[base_price * (1 + i * 0.005) for i in range(-9, 0)],
            short_period=5,
            long_period=10,
            current_price=base_price
        )
        
        # 模拟KDJ状态
        kdj_state = KDJState(
            k_yest=50.0,
            d_yest=50.0,
            h9=base_price * 1.05,
            l9=base_price * 0.95,
            current_price=base_price
        )
        
        # 模拟RSI状态
        rsi_state = RSIState(
            avg_gain=0.5,
            avg_loss=0.5,
            gains=[0.5] * 13,
            losses=[0.5] * 13,
            period=14,
            current_price=base_price
        )
        
        # 模拟布林带状态
        boll_state = BOLLState(
            prices=[base_price * (1 + i * 0.005) for i in range(-19, 0)],
            period=20,
            k=2.0,
            current_price=base_price
        )
        
        # 模拟威廉指标状态
        wr_state = WRState(
            h_n=base_price * 1.08,
            l_n=base_price * 0.92,
            wr_yest=-50.0,
            period=14,
            current_price=base_price
        )
        
        # 模拟CCI状态
        cci_state = CCIState(
            tp_history=[base_price] * 13,
            md=1.0,
            period=14,
            current_price=base_price,
            current_high=base_price * 1.02,
            current_low=base_price * 0.98
        )
        
        return IndicatorSeedData(
            macd=macd_state,
            ma=ma_state,
            kdj=kdj_state,
            rsi=rsi_state,
            boll=boll_state,
            wr=wr_state,
            cci=cci_state,
            last_close=base_price,
            timestamp=datetime.now()
        )
    
    async def calculate_indicator_seed(
        self,
        symbol: str,
        force_refresh: bool = False,
        use_mock: bool = False
    ) -> IndicatorSeedData:
        """
        计算指标种子数据
        
        获取昨日收盘后的 MACD/MA/KDJ 状态，用于今日临界价格计算
        
        Args:
            symbol: 股票代码
            force_refresh: 是否强制刷新缓存
            use_mock: 是否使用模拟数据（用于API限流时的降级）
            
        Returns:
            IndicatorSeedData
        """
        # 检查缓存
        cache_key = f"{symbol}_seed"
        if not force_refresh and cache_key in self._indicator_cache:
            cached = self._indicator_cache[cache_key]
            # 检查缓存是否过期（假设每天刷新）
            if cached.timestamp.date() == datetime.now().date():
                return cached
        
        # 如果使用模拟数据模式
        if use_mock:
            mock_data = self._generate_mock_data(symbol)
            self._indicator_cache[cache_key] = mock_data
            return mock_data
        
        try:
            # 获取历史数据（至少50天）
            hist_data = await self.get_historical_data(symbol, period="3mo", interval="1d")
        except Exception as e:
            if "Rate limited" in str(e) or "Too Many Requests" in str(e):
                print(f"API rate limited for {symbol}, falling back to mock data")
                mock_data = self._generate_mock_data(symbol)
                self._indicator_cache[cache_key] = mock_data
                return mock_data
            raise
        
        if len(hist_data.data) < 30:
            raise ValueError(f"数据不足，需要至少30个交易日数据")
        
        # 转换为 DataFrame
        df = pd.DataFrame([
            {
                'Open': d.open,
                'High': d.high,
                'Low': d.low,
                'Close': d.close,
                'Volume': d.volume
            }
            for d in hist_data.data
        ])
        
        # 计算 MACD
        dif, signal, histogram = self._calculate_macd(df['Close'])
        ema_12 = self._calculate_ema(df['Close'], 12)
        ema_26 = self._calculate_ema(df['Close'], 26)
        
        # 计算 MA
        ma_5 = self._calculate_ma(df['Close'], 5)
        ma_20 = self._calculate_ma(df['Close'], 20)
        
        # 计算 KDJ
        k, d, j = self._calculate_kdj(df)
        
        # 计算 RSI
        rsi = self._calculate_rsi(df['Close'])
        
        # 计算布林带
        boll_mb, boll_up, boll_dn = self._calculate_boll(df)
        
        # 获取昨日数据（倒数第二个元素）
        last_idx = -2  # 昨日
        
        # 构建 MACD 状态
        macd_state = MACDState(
            ema_12=ema_12.iloc[last_idx],
            ema_26=ema_26.iloc[last_idx],
            signal=signal.iloc[last_idx],
            dif=dif.iloc[last_idx],
            close=df['Close'].iloc[last_idx]
        )
        
        # 构建 MA 状态 - 基于历史收盘价 + 今日实时价计算
        # MA5 = (前4日收盘价 + 今日实时价) / 5
        # MA10 = (前9日收盘价 + 今日实时价) / 10
        prices = df['Close'].tolist()
        
        # 获取前N-1个交易日收盘价（不包括今日/最新）
        # df 是按日期升序排列的，最后一个是今日/最新
        if len(prices) >= 10:
            prev_4_closes = prices[-5:-1]   # 前4日（用于MA5）
            prev_9_closes = prices[-10:-1]  # 前9日（用于MA10）
        elif len(prices) >= 5:
            prev_4_closes = prices[-5:-1]   # 前4日
            prev_9_closes = prices[:-1]     # 所有历史数据（除了最新）
        else:
            # 数据不足，使用所有历史数据（除了最新）
            prev_4_closes = prices[:-1] if len(prices) > 1 else prices
            prev_9_closes = prices[:-1] if len(prices) > 1 else prices
        
        # 获取今日实时价格（而不是用历史数据的最后一根收盘价）
        try:
            # 尝试使用Tushare获取实时价格
            if self._tushare_pro:
                current_price = self._fetch_tushare_current_price(symbol)
                print(f"[INFO] 使用实时价格计算MA5: {current_price}")
            else:
                current_price = df['Close'].iloc[-1]
                print(f"[INFO] 使用历史收盘价计算MA5: {current_price}")
        except Exception as e:
            print(f"[WARN] 获取实时价格失败，使用历史收盘价: {e}")
            current_price = df['Close'].iloc[-1]
        
        ma_state = MAState(
            prices_short=prev_4_closes,   # 前4日收盘价
            prices_long=prev_9_closes,    # 前9日收盘价
            short_period=5,
            long_period=10,
            current_price=current_price   # 今日实时价
        )
        
        # 构建 KDJ 状态
        # 获取最近9日的高低价
        recent_9 = df.iloc[last_idx-8:last_idx+1]
        h9 = recent_9['High'].max()
        l9 = recent_9['Low'].min()
        
        kdj_state = KDJState(
            k_yest=k.iloc[last_idx],
            d_yest=d.iloc[last_idx],
            h9=h9,
            l9=l9,
            current_price=df['Close'].iloc[-1]
        )
        
        # 构建 RSI 状态
        # 计算最近14日的涨跌幅
        changes = df['Close'].diff().dropna()
        gains = changes[changes > 0].tolist()
        losses = [-x for x in changes[changes < 0].tolist()]
        
        # 确保列表长度一致
        avg_gain = rsi['avg_gain'].iloc[last_idx] if 'avg_gain' in rsi else (sum(gains[-13:]) / 13 if gains else 0.5)
        avg_loss = rsi['avg_loss'].iloc[last_idx] if 'avg_loss' in rsi else (sum(losses[-13:]) / 13 if losses else 0.5)
        
        rsi_state = RSIState(
            avg_gain=avg_gain,
            avg_loss=avg_loss,
            gains=gains[-13:] if len(gains) >= 13 else gains + [0.5] * (13 - len(gains)),
            losses=losses[-13:] if len(losses) >= 13 else losses + [0.5] * (13 - len(losses)),
            period=14,
            current_price=df['Close'].iloc[-1]
        )
        
        # 构建布林带状态
        boll_state = BOLLState(
            prices=prices[-19:-1],  # 前19日价格
            period=20,
            k=2.0,
            current_price=df['Close'].iloc[-1]
        )
        
        # 构建威廉指标状态
        recent_14 = df.iloc[last_idx-13:last_idx+1]
        h14 = recent_14['High'].max()
        l14 = recent_14['Low'].min()
        
        wr_state = WRState(
            h_n=h14,
            l_n=l14,
            wr_yest=-50,  # 简化，使用中性值
            period=14,
            current_price=df['Close'].iloc[-1]
        )
        
        # 构建CCI状态
        # 计算典型价格和平均绝对偏差
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        tp_history = tp.iloc[-19:-1].tolist()
        
        cci_state = CCIState(
            tp_history=tp_history,
            md=1.0,  # 简化，使用默认值
            period=14,
            current_price=df['Close'].iloc[-1],
            current_high=df['High'].iloc[last_idx],
            current_low=df['Low'].iloc[last_idx]
        )
        
        # 构建种子数据
        seed_data = IndicatorSeedData(
            macd=macd_state,
            ma=ma_state,
            kdj=kdj_state,
            rsi=rsi_state,
            boll=boll_state,
            wr=wr_state,
            cci=cci_state,
            last_close=df['Close'].iloc[last_idx],
            timestamp=datetime.now()
        )
        
        # 缓存
        self._indicator_cache[cache_key] = seed_data
        
        return seed_data
    
    def _fetch_tushare_current_price(self, symbol: str) -> float:
        """
        使用 Tushare 获取A股最新价格
        """
        if not self._tushare_pro:
            raise ValueError("Tushare API 未初始化")

        # 标准化代码格式 (.SS -> .SH)
        symbol = self._normalize_symbol(symbol)

        # 处理 symbol 格式
        ts_code = symbol
        if '.' not in symbol:
            if symbol.startswith('6'):
                ts_code = f"{symbol}.SH"
            else:
                ts_code = f"{symbol}.SZ"
        
        # 调用 Tushare 每日行情接口
        today = datetime.now().strftime('%Y%m%d')
        df = self._tushare_pro.daily(ts_code=ts_code, trade_date=today)
        
        if df is None or df.empty:
            # 尝试获取最近一个交易日
            df = self._tushare_pro.daily(ts_code=ts_code, limit=1)
        
        if df is None or df.empty:
            raise ValueError(f"Tushare 无法获取 {symbol} 的当前价格")
        
        return round(float(df['close'].iloc[0]), 4)
    
    async def get_current_price(self, symbol: str) -> float:
        """
        获取当前价格
        
        优先使用 Tushare 获取A股实时数据，Yahoo Finance 作为备选
        """
        normalized_symbol = self._normalize_symbol(symbol)
        loop = asyncio.get_event_loop()
        now = loop.time()
        cache_ttl = 60.0
        cached = self._price_cache.get(normalized_symbol)
        if cached and (now - cached["t"]) < cache_ttl:
            return cached["price"]

        async def _fetch():
            # 如果是A股且 Tushare 已初始化，优先使用 Tushare
            if self._is_a_stock(normalized_symbol) and self._tushare_pro:
                try:
                    print(f"[INFO] 使用 Tushare 获取A股当前价格: {normalized_symbol}")
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(
                        None,
                        lambda: self._fetch_tushare_current_price(normalized_symbol)
                    )
                except Exception as e:
                    print(f"[WARN] Tushare 获取当前价格失败，尝试 Yahoo Finance: {e}")
            
            # 使用 Yahoo Finance
            loop = asyncio.get_event_loop()
            ticker = yf.Ticker(symbol)
            
            # 获取今日数据（在线程中运行）
            today_data = await loop.run_in_executor(
                None, 
                lambda: ticker.history(period="1d", interval="1m")
            )
            if not today_data.empty:
                return round(today_data['Close'].iloc[-1], 4)
            
            # 回退到日线数据
            hist = await loop.run_in_executor(
                None,
                lambda: ticker.history(period="1d")
            )
            if not hist.empty:
                return round(hist['Close'].iloc[-1], 4)
            
            raise ValueError(f"无法获取 {symbol} 的当前价格")
        
        try:
            price = await self._rate_limited_request(symbol, _fetch)
            self._price_cache[normalized_symbol] = {
                "price": price,
                "t": loop.time(),
            }
            return price
        except Exception as e:
            raise ValueError(f"获取当前价格失败: {str(e)}")
    
    def search_symbols(self, query: str) -> List[Dict[str, str]]:
        """
        搜索股票代码（已弃用，使用simple_data_service）
        
        使用本地倒排索引，毫秒级响应
        支持A股、港股搜索
        """
        if not query or len(query.strip()) == 0:
            return []
        
        trimmed_query = query.strip()
        
        # 确保股票列表已加载（同步加载，阻塞直到完成）
        if not self._stock_list:
            print(f"[INFO] 股票列表未加载，正在加载...")
            self._load_stock_list()
        
        # 如果加载后仍然为空，返回内置的热门股票
        if not self._stock_list:
            print(f"[WARN] 股票列表为空，使用备用数据")
            # 使用内置的备用股票列表
            fallback_stocks = [
                {"symbol": "000001.SZ", "name": "平安银行", "exchange": "SZSE"},
                {"symbol": "000858.SZ", "name": "五粮液", "exchange": "SZSE"},
                {"symbol": "002594.SZ", "name": "比亚迪", "exchange": "SZSE"},
                {"symbol": "300750.SZ", "name": "宁德时代", "exchange": "SZSE"},
                {"symbol": "600036.SH", "name": "招商银行", "exchange": "SSE"},
                {"symbol": "600519.SH", "name": "贵州茅台", "exchange": "SSE"},
                {"symbol": "601318.SH", "name": "中国平安", "exchange": "SSE"},
                {"symbol": "000333.SZ", "name": "美的集团", "exchange": "SZSE"},
                {"symbol": "600276.SH", "name": "恒瑞医药", "exchange": "SSE"},
                {"symbol": "0700.HK", "name": "腾讯控股", "exchange": "HKEX"},
                {"symbol": "3690.HK", "name": "美团", "exchange": "HKEX"},
                {"symbol": "9988.HK", "name": "阿里巴巴-SW", "exchange": "HKEX"},
            ]
            
            # 简单匹配
            query_lower = trimmed_query.lower()
            results = [
                stock for stock in fallback_stocks
                if query_lower in stock["symbol"].lower() 
                or query_lower in stock["name"].lower()
            ]
            return results[:10]
        
        # 使用快速倒排索引搜索
        start_time = datetime.now()
        results = self._search_stocks_fast(trimmed_query, limit=10)
        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        
        print(f"[OK] 搜索 '{trimmed_query}' 返回 {len(results)} 条结果，耗时 {elapsed:.1f}ms")
        
        return results
    
    async def get_multi_indicator_data(
        self,
        symbols: List[str]
    ) -> Dict[str, IndicatorSeedData]:
        """
        批量获取多股票的指标种子数据
        
        Args:
            symbols: 股票代码列表
            
        Returns:
            股票代码到种子数据的映射
        """
        results = {}
        
        for symbol in symbols:
            try:
                seed_data = await self.calculate_indicator_seed(symbol)
                results[symbol] = seed_data
            except Exception as e:
                print(f"获取 {symbol} 数据失败: {e}")
                continue
        
        return results


# 全局数据服务实例（自动从环境变量加载 Tushare Token）
_tushare_token = os.getenv("TUSHARE_TOKEN")
data_service = DataService(tushare_token=_tushare_token)
