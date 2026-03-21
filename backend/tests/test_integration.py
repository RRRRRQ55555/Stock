"""
集成测试

使用真实股票数据验证临界价格计算准确性
"""

import asyncio
import sys
sys.path.insert(0, 'd:\\stock_assistant\\backend')

from app.services.data_service import data_service
from app.core.indicator_engine import IndicatorEngine


async def test_with_real_stock(symbol: str = "AAPL"):
    """使用真实股票数据测试"""
    print(f"\n{'='*60}")
    print(f"集成测试: {symbol}")
    print('='*60)
    
    try:
        # 1. 获取指标种子数据
        print("\n1. 获取指标种子数据...")
        seed_data = await data_service.calculate_indicator_seed(symbol)
        
        print(f"   MACD状态:")
        print(f"     EMA12: {seed_data.macd.ema_12:.4f}")
        print(f"     EMA26: {seed_data.macd.ema_26:.4f}")
        print(f"     Signal: {seed_data.macd.signal:.4f}")
        print(f"     DIF: {seed_data.macd.dif:.4f}")
        
        print(f"   KDJ状态:")
        print(f"     K: {seed_data.kdj.k_yest:.2f}")
        print(f"     D: {seed_data.kdj.d_yest:.2f}")
        print(f"     H9: {seed_data.kdj.h9:.2f}")
        print(f"     L9: {seed_data.kdj.l9:.2f}")
        
        # 2. 获取当前价格
        print("\n2. 获取当前价格...")
        current_price = await data_service.get_current_price(symbol)
        print(f"   {symbol} 当前价格: ${current_price:.2f}")
        
        # 3. 计算触发矩阵
        print("\n3. 计算触发矩阵...")
        
        # 更新种子数据中的当前价格
        seed_data.macd.current_price = current_price
        seed_data.ma.current_price = current_price
        seed_data.kdj.current_price = current_price
        
        engine = IndicatorEngine()
        matrix = engine.calculate_trigger_matrix(
            symbol=symbol,
            current_price=current_price,
            macd_state=seed_data.macd,
            ma_state=seed_data.ma,
            kdj_state=seed_data.kdj
        )
        
        # 4. 输出结果
        print("\n4. 临界价格计算结果:")
        
        print(f"\n   MACD:")
        if matrix.macd_golden_price:
            print(f"     金叉临界价格: ${matrix.macd_golden_price:.2f}")
            print(f"     距离金叉: {matrix.distance_to_golden:.2f}%")
        else:
            print(f"     当前已是金叉状态")
            
        if matrix.macd_death_price:
            print(f"     死叉临界价格: ${matrix.macd_death_price:.2f}")
            print(f"     距离死叉: {matrix.distance_to_death:.2f}%")
        else:
            print(f"     当前非死叉状态")
        
        print(f"\n   均线 (5/20):")
        if matrix.ma_golden_price:
            print(f"     金叉临界价格: ${matrix.ma_golden_price:.2f}")
            print(f"     距离金叉: {matrix.distance_to_golden:.2f}%")
        else:
            print(f"     当前已是多头排列")
            
        if matrix.ma_death_price:
            print(f"     死叉临界价格: ${matrix.ma_death_price:.2f}")
            print(f"     距离死叉: {matrix.distance_to_death:.2f}%")
        else:
            print(f"     当前非空头排列")
        
        print(f"\n   KDJ:")
        if matrix.kdj_oversold_price:
            print(f"     超卖临界价格: ${matrix.kdj_oversold_price:.2f}")
            print(f"     距离超卖: {matrix.distance_to_oversold:.2f}%")
        else:
            print(f"     当前已是超卖状态")
            
        if matrix.kdj_overbought_price:
            print(f"     超买临界价格: ${matrix.kdj_overbought_price:.2f}")
            print(f"     距离超买: {matrix.distance_to_overbought:.2f}%")
        else:
            print(f"     当前非超买状态")
        
        # 5. 共振区间
        print(f"\n5. 共振区间检测:")
        if matrix.resonance_zones:
            print(f"   发现 {len(matrix.resonance_zones)} 个共振区间:")
            for i, zone in enumerate(matrix.resonance_zones, 1):
                print(f"\n   区间 {i}:")
                print(f"     价格范围: ${zone['price_min']:.2f} - ${zone['price_max']:.2f}")
                print(f"     中心价格: ${zone['price_center']:.2f}")
                print(f"     涉及指标: {', '.join(zone['indicators'])}")
                print(f"     置信度: {zone['confidence']:.1%}")
        else:
            print("   暂无共振区间")
        
        # 6. 压力测试
        print(f"\n6. 压力测试 (假设价格上涨 5%):")
        stress_price = current_price * 1.05
        stress_result = engine.stress_test(
            hypothetical_price=stress_price,
            macd_state=seed_data.macd,
            ma_state=seed_data.ma,
            kdj_state=seed_data.kdj
        )
        
        print(f"   假设价格: ${stress_price:.2f}")
        print(f"   MACD: DIF={stress_result['macd']['dif']:.4f}, Signal={stress_result['macd']['signal']:.4f}")
        print(f"   趋势: {stress_result['macd']['trend']}")
        print(f"   均线: MA5={stress_result['ma']['ma_short']:.2f}, MA10={stress_result['ma']['ma_long']:.2f}")
        print(f"   趋势: {stress_result['ma']['trend']}")
        print(f"   KDJ: K={stress_result['kdj']['k']:.2f}, D={stress_result['kdj']['d']:.2f}, J={stress_result['kdj']['j']:.2f}")
        print(f"   区域: {stress_result['kdj']['zone']}")
        print(f"\n   综合结论: {stress_result['summary']['overall']}")
        print(f"   看涨信号: {stress_result['summary']['bullish_signals']}个")
        print(f"   看跌信号: {stress_result['summary']['bearish_signals']}个")
        
        print(f"\n{'='*60}")
        print(f"✓ {symbol} 测试完成!")
        print('='*60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ {symbol} 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_multiple_stocks():
    """测试多只股票"""
    print("\n" + "="*60)
    print("批量集成测试")
    print("="*60)
    
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
    results = {}
    
    for symbol in symbols:
        try:
            success = await test_with_real_stock(symbol)
            results[symbol] = "通过" if success else "失败"
        except Exception as e:
            results[symbol] = f"错误: {str(e)}"
    
    # 输出汇总
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    for symbol, result in results.items():
        status = "✓" if result == "通过" else "✗"
        print(f"  {status} {symbol}: {result}")
    
    passed = sum(1 for r in results.values() if r == "通过")
    print(f"\n总计: {passed}/{len(symbols)} 通过")
    
    return passed == len(symbols)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("技术指标前置预判工具 - 集成测试")
    print("="*60)
    
    async def main():
        # 单只股票测试
        success1 = await test_with_real_stock("AAPL")
        
        # 多只股票测试
        success2 = await test_multiple_stocks()
        
        if success1 and success2:
            print("\n" + "="*60)
            print("所有测试通过!")
            print("="*60)
            return 0
        else:
            print("\n" + "="*60)
            print("部分测试失败")
            print("="*60)
            return 1
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
