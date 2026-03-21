# 测试搜索路由
from fastapi import APIRouter, Query

router = APIRouter()

@router.get("/search")
async def search_symbols(q: str = Query(..., min_length=1, max_length=20)):
    """搜索股票代码（纯本地搜索）"""
    from ..services.simple_data_service import simple_data_service
    
    # 确保查询是字符串
    query_str = str(q).strip() if q else ""
    if not query_str:
        return []
    
    print(f"[DEBUG] 搜索参数: '{query_str}' (类型: {type(query_str)})")
    
    results = simple_data_service.search_symbols(query_str)
    return results
