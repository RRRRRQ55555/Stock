import requests
import json

# 测试API - 检查MA5计算
symbol = "000001.SZ"  # 平安银行
current_price = 10.5  # 假设当前价格低于MA5

url = "http://localhost:8000/api/v1/strategy/calculate-range"
params = {
    "symbol": symbol,
    "current_price": current_price,
    "buy_conditions": json.dumps({
        "priceAboveMA5": True
    }),
    "stop_conditions": json.dumps({})
}

try:
    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    print("=== API响应 ===")
    ma_short = data.get('ma', {}).get('ma_short')
    print(f"MA5值: {ma_short}")
    print(f"当前价: {current_price}")
    print(f"是否站上MA5: {current_price >= ma_short * 0.99 if ma_short else 'N/A'}")
    print(f"是否可买: {data.get('buy', {}).get('current_satisfied')}")
    print(f"未满足条件: {data.get('buy', {}).get('unsatisfied_conditions')}")
    print(f"\n完整响应:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"请求失败: {e}")
