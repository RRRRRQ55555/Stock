#!/usr/bin/env python3
"""
从 Tushare 获取所有 A 股列表并更新本地股票列表
"""

import os
import json
from dotenv import load_dotenv

# 加载环境变量
backend_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(backend_dir, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"[OK] 已加载 .env 文件: {env_path}")
else:
    load_dotenv()

# 检查Token
token = os.getenv("TUSHARE_TOKEN")
if not token:
    print("[FAIL] 未找到 Tushare Token!")
    print("[INFO] 请确保 .env 文件中包含: TUSHARE_TOKEN=你的token")
    exit(1)

print(f"[OK] Tushare Token 已配置: {token[:8]}...{token[-8:]}")

try:
    import tushare as ts
    ts.set_token(token)
    pro = ts.pro_api()
    
    print("\n[INFO] 正在从 Tushare 获取所有 A 股列表...")
    
    # 获取所有上市股票（包含沪A和深A）
    df = pro.stock_basic(
        exchange='',  # 不指定交易所，获取全部
        list_status='L',  # 只获取正常上市的股票
        fields='ts_code,name,exchange,list_status'
    )
    
    if df is None or df.empty:
        print("[FAIL] Tushare 返回空数据")
        exit(1)
    
    print(f"[OK] 从 Tushare 获取到 {len(df)} 只股票")
    
    # 转换为本地格式
    stock_list = []
    for _, row in df.iterrows():
        ts_code = row['ts_code']
        name = row['name']
        exchange = row['exchange']
        
        # 映射交易所代码
        exchange_map = {
            'SSE': 'SSE',  # 上交所
            'SZSE': 'SZSE',  # 深交所
            'BSE': 'BSE'  # 北交所
        }
        
        stock_list.append({
            "symbol": ts_code,
            "name": name,
            "exchange": exchange_map.get(exchange, exchange)
        })
    
    # 按股票代码排序
    stock_list.sort(key=lambda x: x['symbol'])
    
    # 保存到文件
    output_file = os.path.join(backend_dir, 'app', 'data', 'a_stock_list.json')
    
    # 备份旧文件
    if os.path.exists(output_file):
        backup_file = output_file + '.backup'
        with open(output_file, 'r', encoding='utf-8') as f:
            old_data = f.read()
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(old_data)
        print(f"[OK] 已备份原文件到: {backup_file}")
    
    # 写入新数据
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stock_list, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] 成功保存 {len(stock_list)} 只股票到: {output_file}")
    print(f"\n[INFO] 股票列表示例（前10只）:")
    for stock in stock_list[:10]:
        print(f"  {stock['symbol']} - {stock['name']} ({stock['exchange']})")
    
    print(f"\n[INFO] 总计: {len(stock_list)} 只A股")
    
except Exception as e:
    print(f"[FAIL] 获取股票列表失败: {e}")
    import traceback
    traceback.print_exc()
