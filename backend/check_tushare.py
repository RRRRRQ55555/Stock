#!/usr/bin/env python3
"""
检查Tushare配置状态
"""

import os
from dotenv import load_dotenv

# 加载环境变量
backend_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(backend_dir, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"[OK] 已加载 .env 文件: {env_path}")
else:
    load_dotenv()
    print("[INFO] 使用系统环境变量")

# 检查Token
token = os.getenv("TUSHARE_TOKEN")
if token:
    print(f"[OK] Tushare Token 已配置: {token[:8]}...{token[-8:]}")
    
    # 测试Tushare连接
    try:
        import tushare as ts
        ts.set_token(token)
        pro = ts.pro_api()
        
        # 测试查询
        df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name', limit=5)
        if df is not None and not df.empty:
            print(f"[OK] Tushare 连接测试成功!")
            print(f"[OK] 获取到 {len(df)} 条测试数据")
            print("\n测试数据样例:")
            print(df.head())
        else:
            print("[WARN] Tushare 返回空数据，可能需要检查Token权限")
            
    except Exception as e:
        print(f"[FAIL] Tushare 连接失败: {e}")
else:
    print("[FAIL] 未找到 Tushare Token!")
    print("[INFO] 请确保 .env 文件中包含: TUSHARE_TOKEN=你的token")
