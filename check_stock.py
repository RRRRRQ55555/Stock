#!/usr/bin/env python3
"""检查股票是否站上MA5"""

import requests
import json

# 贵州茅台
symbol = "600519.SS"

# 调用策略计算API
url = f"http://localhost:8000/api/v1/strategy/price-range/{symbol}"

# 只检查站上MA5条件
params = {
    "buy_conditions": json.dumps({
        "priceAboveMA5": True
    }),
    "stop_conditions": json.dumps({})
}

try:
    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    print(f"\n=== 贵州茅台 ({symbol}) 分析 ===\n")

    current_price = data.get('current_price')
    ma_data = data.get('buy_range', {}).get('critical_prices', [])
    ma_short = None

    # 从返回数据中找MA5值
    for item in ma_data:
        if item.get('condition') == '站上MA5':
            ma_short = item.get('target_price')
            distance = item.get('distance_pct')
            break

    print(f"当前价格: {current_price} 元")

    if ma_short:
        print(f"MA5 值: {ma_short} 元")
        print(f"判断阈值 (MA5 * 0.99): {ma_short * 0.99:.2f} 元")
        print(f"\n站上MA5条件:")
        print(f"  需要: 当前价 >= {ma_short * 0.99:.2f} 元")
        print(f"  实际: 当前价 = {current_price} 元")

        if current_price >= ma_short * 0.99:
            print(f"  ✅ 结果: 已站上MA5")
        else:
            print(f"  ❌ 结果: 未站上MA5")
            print(f"  📈 需要上涨: {distance:.2f}%")
    else:
        # MA5值可能在矩阵数据中
        matrix = data
        ma_short = matrix.get('ma', {}).get('ma_short')
        if ma_short:
            print(f"MA5 值: {ma_short} 元")
            print(f"判断阈值 (MA5 * 0.99): {ma_short * 0.99:.2f} 元")

            if current_price >= ma_short * 0.99:
                print(f"\n✅ 已站上MA5")
            else:
                distance = (ma_short - current_price) / current_price * 100
                print(f"\n❌ 未站上MA5，需要上涨: {distance:.2f}%")
        else:
            print("无法获取MA5数据")

    print(f"\n买入策略状态: {data.get('buy_range', {}).get('current_satisfied', 'N/A')}")
    print(f"整体建议: {data.get('recommendation', 'N/A')}")
    print(f"\n完整响应:\n{json.dumps(data, indent=2, ensure_ascii=False)[:1000]}...")

except Exception as e:
    print(f"请求失败: {e}")
    print(f"请确保服务已启动: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
