#!/usr/bin/env python3
"""
最简单的后端启动脚本
直接运行，不需要 Docker，不需要虚拟环境
"""

import sys
import os

# 添加 backend 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# 启动服务
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动股票助手后端服务...")
    print("📊 API 地址: http://localhost:8000")
    print("📚 文档地址: http://localhost:8000/docs")
    print("")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1
    )
