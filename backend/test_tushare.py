#!/usr/bin/env python3
"""
Tushare 集成测试脚本

测试 A股数据获取功能
"""

import asyncio
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from app.services.data_service import data_service, DataService


async def test_tushare():
    """测试 Tushare 数据获取"""
    
    print("="*60)
    print("Tushare 集成测试")
    print("="*60)
    
    # 检查 Tushare 是否可用
    token = os.getenv("TUSHARE_TOKEN")
    if not token:
        print("\n[WARN] 未设置 TUSHARE_TOKEN 环境变量")
        print("       请运行: $env:TUSHARE_TOKEN='你的token'")
        print("\n使用模拟数据进行测试...")
    else:
        print(f"\n[OK] 检测到 Tushare Token")
        # 重新初始化以加载 Token
        data_service.__init__(tushare_token=token)
    
    # 测试 A股代码识别
    print("\n1. 测试 A股代码识别")
    test_codes = ["000001.SZ", "000001", "AAPL", "600000.SH"]
    for code in test_codes:
        is_a = data_service._is_a_stock(code)
        print(f"   {code}: {'是A股' if is_a else '非A股'}")
    
    # 测试数据获取
    print("\n2. 测试数据获取")
    test_symbols = ["000001.SZ", "600000.SH"]
    
    for symbol in test_symbols:
        print(f"\n   测试 {symbol}:")
        try:
            # 获取历史数据
            hist = await data_service.get_historical_data(symbol, period="1mo")
            print(f"   [OK] 获取到 {len(hist.data)} 条历史数据")
            
            if hist.data:
                latest = hist.data[-1]
                print(f"   [OK] 最新价格: {latest.close} ({latest.timestamp.strftime('%Y-%m-%d')})")
            
            # 获取指标种子数据
            seed = await data_service.calculate_indicator_seed(symbol, use_mock=not token)
            print(f"   [OK] MACD DIF: {seed.macd.dif:.4f}")
            print(f"   [OK] MA Short: {seed.ma.prices_short[-1]:.2f}")
            print(f"   [OK] KDJ K: {seed.kdj.k_yest:.2f}")
            
        except Exception as e:
            print(f"   [FAIL] {e}")
    
    # 测试股票搜索
    print("\n3. 测试股票搜索")
    queries = ["000001", "茅台", "银行"]
    for query in queries:
        print(f"\n   搜索 '{query}':")
        try:
            results = data_service.search_symbols(query)
            for stock in results[:3]:
                print(f"   - {stock['symbol']}: {stock['name']} ({stock['exchange']})")
        except Exception as e:
            print(f"   [FAIL] {e}")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_tushare())
