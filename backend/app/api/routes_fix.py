# 临时修复文件 - 搜索路由

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any

router = APIRouter()

@router.get("/search")
async def search_symbols(q: str = Query(..., min_length=1, max_length=20)):
    """搜索股票代码（纯本地搜索）"""
    from ..services.simple_data_service import simple_data_service
    
    query_str = str(q).strip() if q else ""
    if not query_str:
        return []
    
    results = simple_data_service.search_symbols(query_str)
    return results
