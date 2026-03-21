#!/usr/bin/env python3
"""
验证MA5/MA10计算是否正确
"""

import requests
import json

symbol = "600519.SS"  # 贵州茅台
url = f"http://localhost:8000/api/matrix/auto/{symbol}"

try:
    response = requests.post(url, json={"mock": False}, timeout=10)
    data = response.json()

    print(f"\n=== {symbol} 均线计算验证 ===\n")

    current_price = data.get('current_price')
    ma_data = data.get('ma', {})
    ma_short = ma_data.get('ma_short')  # MA5
    ma_long = ma_data.get('ma_long')      # MA10
    short_period = ma_data.get('short_period')
    long_period = ma_data.get('long_period')

    print(f"当前价格: {current_price} 元")
    print(f"MA{short_period}: {ma_short} 元")
    print(f"MA{long_period}: {ma_long} 元")
    print()

    # 反推前N-1日收盘价之和
    if ma_short and current_price and short_period:
        sum_prev_short = ma_short * short_period - current_price
        avg_prev_short = sum_prev_short / (short_period - 1)
        print(f"MA{short_period} 计算验证:")
        print(f"  公式: ({sum_prev_short:.2f} + {current_price}) / {short_period} = {ma_short}")
        print(f"  前{short_period-1}日收盘价之和: {sum_prev_short:.2f} 元")
        print(f"  前{short_period-1}日平均: {avg_prev_short:.2f} 元/日")
        print()

    if ma_long and current_price and long_period:
        sum_prev_long = ma_long * long_period - current_price
        avg_prev_long = sum_prev_long / (long_period - 1)
        print(f"MA{long_period} 计算验证:")
        print(f"  公式: ({sum_prev_long:.2f} + {current_price}) / {long_period} = {ma_long}")
        print(f"  前{long_period-1}日收盘价之和: {sum_prev_long:.2f} 元")
        print(f"  前{long_period-1}日平均: {avg_prev_long:.2f} 元/日")
        print()

    # 站上MA5判断
    if ma_short and current_price:
        threshold_strict = ma_short  # 严格大于
        threshold_loose = ma_short * 0.99  # 允许1%误差

        print(f"站上MA{short_period} 判断:")
        print(f"  当前价: {current_price}")
        print(f"  MA{short_period}: {ma_short}")
        print(f"  严格判断 (>= MA5): {current_price} >= {ma_short} ? {current_price >= ma_short}")
        print(f"  宽松判断 (>= MA5×0.99): {current_price} >= {threshold_loose:.2f} ? {current_price >= threshold_loose}")
        print()

        if current_price >= ma_short:
            print(f"  ✅ 严格意义上：已站上MA{short_period}")
        elif current_price >= threshold_loose:
            print(f"  ⚠️ 宽松判断：已站上MA{short_period} (允许1%误差)")
        else:
            print(f"  ❌ 未站上MA{short_period}")
            distance = (ma_short - current_price) / current_price * 100
            print(f"     需要上涨: {distance:.2f}%")

except Exception as e:
    print(f"请求失败: {e}")
    print("请确保服务已启动: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
