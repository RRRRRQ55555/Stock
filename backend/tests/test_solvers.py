"""
核心求解器单元测试

测试 MACD/MA/KDJ 反向求解器的数学正确性
"""

import sys
sys.path.insert(0, 'd:\\stock_assistant\\backend')

from app.core.macd_solver import MACDSolver, MACDState, calculate_macd_trigger
from app.core.ma_solver import MASolver, MAState, calculate_ma_trigger
from app.core.kdj_solver import KDJolver, KDJState, calculate_kdj_trigger


def test_macd_solver():
    """测试 MACD 求解器"""
    print("\n" + "="*50)
    print("测试 MACD 求解器")
    print("="*50)
    
    # 构建测试状态（模拟昨日收盘后的MACD状态）
    state = MACDState(
        ema_12=100.0,
        ema_26=98.0,
        signal=99.0,
        dif=2.0,
        close=100.0
    )
    
    solver = MACDSolver()
    
    # 计算当前MACD值
    dif, signal, hist = solver.calculate_macd(state, 100.0)
    print(f"当前价格 $100 时的 MACD: DIF={dif:.4f}, Signal={signal:.4f}")
    
    # 求解金叉临界价格
    golden_price = solver.solve_golden_cross_price(state)
    if golden_price:
        print(f"金叉临界价格: ${golden_price:.2f}")
        
        # 验证：在临界价格处的DIF应该接近Signal
        dif_check, signal_check, _ = solver.calculate_macd(state, golden_price)
        print(f"验证: DIF={dif_check:.4f}, Signal={signal_check:.4f}, 差值={abs(dif_check-signal_check):.6f}")
        assert abs(dif_check - signal_check) < 0.01, "金叉验证失败"
        print("✓ 金叉验证通过")
    else:
        print("当前已经是金叉状态，无需计算金叉价格")
    
    # 压力测试
    sim_result = solver.simulate_price(state, 105.0)
    print(f"\n压力测试 (假设价格 $105):")
    print(f"  DIF={sim_result['dif']}, Signal={sim_result['signal']}")
    print(f"  趋势: {sim_result['trend']}")
    
    print("\n✓ MACD求解器测试通过")


def test_ma_solver():
    """测试均线求解器"""
    print("\n" + "="*50)
    print("测试 均线求解器")
    print("="*50)
    
    # 模拟价格历史
    # 5日均线需要4个历史价格，10日均线需要9个历史价格
    prices_short = [98.0, 99.0, 100.0, 101.0]  # 4个价格
    prices_long = [95.0 + i * 0.3 for i in range(9)]  # 9个价格，轻微上涨趋势
    current_price = 102.0
    
    state = MAState(
        prices_short=prices_short,
        prices_long=prices_long,
        short_period=5,
        long_period=10,
        current_price=current_price
    )
    
    solver = MASolver(5, 10)
    
    # 计算当前均线值
    ma5 = solver.calculate_ma(prices_short, current_price, 5)
    ma10 = solver.calculate_ma(prices_long, current_price, 10)
    print(f"当前价格 ${current_price}")
    print(f"MA5={ma5:.4f}, MA10={ma10:.4f}")
    print(f"当前状态: {'多头排列' if ma5 > ma10 else '空头排列' if ma5 < ma10 else '均线粘合'}")
    
    # 求解临界价格
    result = solver.solve_trigger_prices(state)
    
    if result.golden_cross_price:
        print(f"\n金叉临界价格: ${result.golden_cross_price:.2f}")
        print(f"距离金叉: {result.distance_to_golden:.2f}%")
        
        # 验证
        ma5_check = solver.calculate_ma(prices_short, result.golden_cross_price, 5)
        ma10_check = solver.calculate_ma(prices_long, result.golden_cross_price, 10)
        print(f"验证: MA5={ma5_check:.4f}, MA10={ma10_check:.4f}, 差值={abs(ma5_check-ma10_check):.6f}")
        assert abs(ma5_check - ma10_check) < 0.01, "金叉验证失败"
        print("✓ 金叉验证通过")
    
    if result.death_cross_price:
        print(f"\n死叉临界价格: ${result.death_cross_price:.2f}")
        print(f"距离死叉: {result.distance_to_death:.2f}%")
    
    # 压力测试
    sim_result = solver.simulate_price(state, 110.0)
    print(f"\n压力测试 (假设价格 $110):")
    print(f"  MA5={sim_result['ma_short']}, MA10={sim_result['ma_long']}")
    print(f"  趋势: {sim_result['trend']}")
    
    print("\n✓ 均线求解器测试通过")


def test_kdj_solver():
    """测试 KDJ 求解器"""
    print("\n" + "="*50)
    print("测试 KDJ 求解器")
    print("="*50)
    
    # 模拟昨日收盘后的KDJ状态
    # 假设当前处于中等位置
    state = KDJState(
        k_yest=50.0,
        d_yest=50.0,
        h9=110.0,  # 9日最高价
        l9=90.0,   # 9日最低价
        current_price=100.0
    )
    
    solver = KDJolver()
    
    # 计算当前KDJ值
    k, d, j = solver.calculate_kdj(state, 100.0)
    print(f"当前价格 $100 时的 KDJ: K={k:.2f}, D={d:.2f}, J={j:.2f}")
    
    # 求解临界价格
    result = solver.solve_trigger_prices(state)
    
    if result.oversold_price:
        print(f"\n超卖临界价格 (J=0): ${result.oversold_price:.2f}")
        print(f"距离超卖区: {result.distance_to_oversold:.2f}%")
        
        # 验证
        k_check, d_check, j_check = solver.calculate_kdj(state, result.oversold_price)
        print(f"验证: K={k_check:.4f}, D={d_check:.4f}, J={j_check:.4f}")
        assert abs(j_check) < 0.1, "超卖验证失败"
        print("✓ 超卖验证通过")
    
    if result.overbought_price:
        print(f"\n超买临界价格 (J=100): ${result.overbought_price:.2f}")
        print(f"距离超买区: {result.distance_to_overbought:.2f}%")
        
        # 验证
        k_check, d_check, j_check = solver.calculate_kdj(state, result.overbought_price)
        print(f"验证: K={k_check:.4f}, D={d_check:.4f}, J={j_check:.4f}")
        assert abs(j_check - 100) < 0.1, "超买验证失败"
        print("✓ 超买验证通过")
    
    # 压力测试
    sim_result = solver.simulate_price(state, 95.0)
    print(f"\n压力测试 (假设价格 $95):")
    print(f"  K={sim_result['k']}, D={sim_result['d']}, J={sim_result['j']}")
    print(f"  区域: {sim_result['zone']}")
    
    sim_result2 = solver.simulate_price(state, 105.0)
    print(f"\n压力测试 (假设价格 $105):")
    print(f"  K={sim_result2['k']}, D={sim_result2['d']}, J={sim_result2['j']}")
    print(f"  区域: {sim_result2['zone']}")
    
    print("\n✓ KDJ求解器测试通过")


def test_integration():
    """测试指标引擎整合"""
    print("\n" + "="*50)
    print("测试 指标引擎整合")
    print("="*50)
    
    from app.core.indicator_engine import IndicatorEngine, TriggerMatrix
    
    engine = IndicatorEngine()
    
    # 构建状态
    macd_state = MACDState(
        ema_12=100.0,
        ema_26=98.0,
        signal=99.0,
        dif=2.0,
        close=100.0
    )
    
    ma_state = MAState(
        prices_short=[98.0, 99.0, 100.0, 101.0],
        prices_long=[95.0 + i * 0.3 for i in range(19)],
        short_period=5,
        long_period=20,
        current_price=102.0
    )
    
    kdj_state = KDJState(
        k_yest=50.0,
        d_yest=50.0,
        h9=110.0,
        l9=90.0,
        current_price=100.0
    )
    
    # 计算触发矩阵
    matrix = engine.calculate_trigger_matrix(
        symbol="TEST",
        current_price=100.0,
        macd_state=macd_state,
        ma_state=ma_state,
        kdj_state=kdj_state
    )
    
    print(f"股票: {matrix.symbol}")
    print(f"当前价格: ${matrix.current_price}")
    print(f"\nMACD:")
    print(f"  金叉价格: ${matrix.macd_golden_price:.2f}" if matrix.macd_golden_price else "  已是金叉状态")
    print(f"  死叉价格: ${matrix.macd_death_price:.2f}" if matrix.macd_death_price else "  无死叉价格")
    print(f"\nMA:")
    print(f"  金叉价格: ${matrix.ma_golden_price:.2f}" if matrix.ma_golden_price else "  已是金叉状态")
    print(f"  死叉价格: ${matrix.ma_death_price:.2f}" if matrix.ma_death_price else "  无死叉价格")
    print(f"\nKDJ:")
    print(f"  超卖价格: ${matrix.kdj_oversold_price:.2f}" if matrix.kdj_oversold_price else "  已是超卖状态")
    print(f"  超买价格: ${matrix.kdj_overbought_price:.2f}" if matrix.kdj_overbought_price else "  无超买价格")
    
    # 检查共振
    if matrix.resonance_zones:
        print(f"\n发现 {len(matrix.resonance_zones)} 个共振区间:")
        for zone in matrix.resonance_zones:
            print(f"  - 价格区间: ${zone['price_min']:.2f} - ${zone['price_max']:.2f}")
            print(f"    涉及指标: {', '.join(zone['indicators'])}")
            print(f"    置信度: {zone['confidence']:.1%}")
    
    # 压力测试
    stress_result = engine.stress_test(95.0, macd_state, ma_state, kdj_state)
    print(f"\n压力测试 (假设价格 $95):")
    print(f"  整体趋势: {stress_result['summary']['overall']}")
    print(f"  看涨信号: {stress_result['summary']['bullish_signals']}")
    print(f"  看跌信号: {stress_result['summary']['bearish_signals']}")
    
    print("\n✓ 指标引擎整合测试通过")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("技术指标反向求解器单元测试")
    print("="*60)
    
    try:
        test_macd_solver()
        test_ma_solver()
        test_kdj_solver()
        test_integration()
        
        print("\n" + "="*60)
        print("所有测试通过！")
        print("="*60)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
