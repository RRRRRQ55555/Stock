"""
简化数据服务

从本地JSON文件加载A股列表，搜索时不依赖外部API
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime

# 股票列表文件路径
DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STOCK_LIST_FILE = os.path.join(DATA_DIR, "data", "a_stock_list.json")

class SimpleDataService:
    """简化版数据服务"""
    
    def __init__(self):
        self._stock_list: List[Dict[str, str]] = []
        self._load_stock_list()
    
    def _load_stock_list(self):
        """从本地JSON文件加载股票列表"""
        try:
            with open(STOCK_LIST_FILE, 'r', encoding='utf-8') as f:
                self._stock_list = json.load(f)
            print(f"[OK] 从本地加载 {len(self._stock_list)} 只股票")
        except Exception as e:
            print(f"[WARN] 加载本地股票列表失败: {e}")
            # 使用内置列表作为备用
            self._stock_list = self._get_builtin_stocks()
    
    def _get_builtin_stocks(self) -> List[Dict[str, str]]:
        """内置股票列表（备用）"""
        return [
            {"symbol": "000001.SZ", "name": "平安银行", "exchange": "SZSE"},
            {"symbol": "000858.SZ", "name": "五粮液", "exchange": "SZSE"},
            {"symbol": "002594.SZ", "name": "比亚迪", "exchange": "SZSE"},
            {"symbol": "300750.SZ", "name": "宁德时代", "exchange": "SZSE"},
            {"symbol": "600036.SH", "name": "招商银行", "exchange": "SSE"},
            {"symbol": "600519.SH", "name": "贵州茅台", "exchange": "SSE"},
            {"symbol": "601318.SH", "name": "中国平安", "exchange": "SSE"},
        ]
    
    def search_symbols(self, query: str) -> List[Dict[str, str]]:
        """
        搜索股票代码（纯本地，不调用API）
        """
        if not query or len(query.strip()) == 0:
            return []
        
        query_lower = query.strip().lower()
        results = []
        
        for stock in self._stock_list:
            symbol = stock["symbol"].lower()
            name = stock["name"].lower()
            
            # 匹配规则：代码或名称包含查询字符串
            if query_lower in symbol or query_lower in name:
                results.append(stock)
        
        # 按相关性排序（完全匹配 > 开头匹配 > 包含）
        def get_score(stock):
            symbol = stock["symbol"].lower()
            name = stock["name"].lower()
            
            if query_lower == symbol:
                return 100
            if query_lower == name:
                return 90
            if symbol.startswith(query_lower):
                return 80
            if name.startswith(query_lower):
                return 70
            if query_lower in symbol:
                return 60
            return 50
        
        results.sort(key=get_score, reverse=True)
        
        print(f"[OK] 搜索 '{query}' 返回 {len(results)} 条结果")
        return results[:10]  # 最多返回10条
    
    def _normalize_symbol(self, symbol: str) -> str:
        """标准化股票代码格式"""
        # 处理后缀差异：.SS -> .SH
        if symbol.endswith('.SS'):
            return symbol.replace('.SS', '.SH')
        return symbol

    def get_stock_by_symbol(self, symbol: str) -> Optional[Dict[str, str]]:
        """根据代码获取股票信息"""
        # 标准化代码格式
        normalized = self._normalize_symbol(symbol)

        for stock in self._stock_list:
            if stock["symbol"] == normalized or stock["symbol"] == symbol:
                return stock
        return None

# 全局实例
simple_data_service = SimpleDataService()
