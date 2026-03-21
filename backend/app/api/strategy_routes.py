"""
交易策略管理路由

提供策略的CRUD、每日检查、执行入场/出场等功能
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime

from ..models.schemas import (
    CreateStrategyRequest,
    StrategyResponse,
    StrategyCheckResultResponse,
    ExecuteEntryRequest,
    ExecuteExitRequest,
    GetStrategiesResponse,
    GetStrategyTemplatesResponse,
    StrategyTemplate,
    ConditionInput,
)
from ..core.strategy_engine import (
    StrategyEngine,
    TradingStrategy,
    StrategyStatus,
    PREDEFINED_STRATEGIES,
    create_strategy_from_template,
)
from ..core.condition_filter import Condition, ConditionType
from ..services.data_service import data_service


router = APIRouter(prefix="/strategies", tags=["交易策略"])

# 内存存储策略（生产环境应该使用数据库）
strategy_storage: dict[str, TradingStrategy] = {}
strategy_engine = StrategyEngine()


# ============= 策略模板接口 =============

@router.get("/templates", response_model=GetStrategyTemplatesResponse)
async def get_strategy_templates():
    """
    获取预设交易策略模板
    
    提供常用的交易策略模板，可直接使用创建策略
    """
    templates = []
    for name, template in PREDEFINED_STRATEGIES.items():
        templates.append(StrategyTemplate(
            name=name,
            description=template["description"],
            entry_conditions=[
                ConditionInput(
                    condition_type=c.condition_type.value,
                    params=c.params,
                    weight=c.weight
                )
                for c in template["entry_conditions"]
            ],
            stop_loss_conditions=[
                ConditionInput(
                    condition_type=c.condition_type.value,
                    params=c.params,
                    weight=c.weight
                )
                for c in template["stop_loss_conditions"]
            ],
            tags=["预设模板"]
        ))
    
    return GetStrategyTemplatesResponse(templates=templates)


# ============= 策略CRUD接口 =============

@router.post("", response_model=StrategyResponse)
async def create_strategy(request: CreateStrategyRequest):
    """
    创建交易策略
    
    可以自定义条件，或使用预设模板创建
    
    示例：
    ```json
    {
        "name": "我的均线策略",
        "symbol": "600519.SH",
        "entry_conditions": [
            {"condition_type": "price_above_ma", "params": {"period": 5}, "weight": 1.0},
            {"condition_type": "macd_golden", "params": {}, "weight": 1.0}
        ],
        "stop_loss": {
            "conditions": [{"condition_type": "price_below_ma", "params": {"period": 20}}],
            "fixed_pct": -5
        },
        "take_profit": {
            "fixed_pct": 10,
            "r_ratio": 2
        }
    }
    ```
    """
    try:
        # 如果使用模板
        if request.use_template:
            strategy = create_strategy_from_template(request.use_template, request.symbol)
            if not strategy:
                raise HTTPException(status_code=400, detail=f"未知模板: {request.use_template}")
            strategy.name = request.name
            strategy.notes = request.notes
        else:
            # 自定义条件
            entry_conditions = [
                Condition(
                    condition_type=ConditionType(c.condition_type),
                    params=c.params,
                    weight=c.weight
                )
                for c in request.entry_conditions
            ]
            
            stop_conditions = [
                Condition(
                    condition_type=ConditionType(c.condition_type),
                    params=c.params,
                    weight=c.weight
                )
                for c in request.stop_loss.conditions
            ]
            
            strategy = strategy_engine.create_strategy(
                name=request.name,
                symbol=request.symbol,
                entry_conditions=entry_conditions,
                stop_loss_conditions=stop_conditions,
                notes=request.notes
            )
            
            # 设置止损参数
            if request.stop_loss.fixed_price:
                strategy.stop_loss.fixed_price = request.stop_loss.fixed_price
            if request.stop_loss.fixed_pct:
                strategy.stop_loss.fixed_pct = request.stop_loss.fixed_pct
        
        # 保存策略
        strategy_storage[strategy.id] = strategy
        
        return _strategy_to_response(strategy)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建策略失败: {str(e)}")


@router.get("", response_model=GetStrategiesResponse)
async def get_strategies(status: Optional[str] = None, symbol: Optional[str] = None):
    """
    获取策略列表
    
    Args:
        status: 按状态过滤（pending/entered/stop_loss/take_profit）
        symbol: 按股票代码过滤
    """
    strategies = list(strategy_storage.values())
    
    # 过滤
    if status:
        strategies = [s for s in strategies if s.status.value == status]
    if symbol:
        strategies = [s for s in strategies if s.symbol == symbol]
    
    # 统计
    by_status = {}
    for s in strategy_storage.values():
        status_key = s.status.value
        by_status[status_key] = by_status.get(status_key, 0) + 1
    
    return GetStrategiesResponse(
        strategies=[_strategy_to_response(s) for s in strategies],
        count=len(strategies),
        by_status=by_status
    )


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: str):
    """获取单个策略详情"""
    if strategy_id not in strategy_storage:
        raise HTTPException(status_code=404, detail="策略不存在")
    
    return _strategy_to_response(strategy_storage[strategy_id])


@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: str):
    """删除策略"""
    if strategy_id not in strategy_storage:
        raise HTTPException(status_code=404, detail="策略不存在")
    
    del strategy_storage[strategy_id]
    return {"status": "success", "message": "策略已删除"}


# ============= 策略检查接口 =============

@router.get("/{strategy_id}/check", response_model=StrategyCheckResultResponse)
async def check_strategy(strategy_id: str, current_price: Optional[float] = None):
    """
    检查策略今日状态
    
    返回：
    - 今日是否可入场及价格区间
    - 止损触发价格
    - 综合建议
    
    Args:
        current_price: 当前价格（不提供则自动获取）
    """
    if strategy_id not in strategy_storage:
        raise HTTPException(status_code=404, detail="策略不存在")
    
    strategy = strategy_storage[strategy_id]
    
    try:
        # 获取指标数据
        seed_data = await data_service.calculate_indicator_seed(strategy.symbol)
        
        # 使用传入价格或实时价格
        price = current_price or seed_data.last_close
        
        # 更新当前价格
        seed_data.macd.current_price = price
        seed_data.ma.current_price = price
        seed_data.kdj.current_price = price
        seed_data.rsi.current_price = price
        seed_data.boll.current_price = price
        seed_data.wr.current_price = price
        seed_data.cci.current_price = price
        
        # 执行策略检查
        result = strategy_engine.check_strategy(
            strategy=strategy,
            current_price=price,
            macd_state=seed_data.macd,
            ma_state=seed_data.ma,
            kdj_state=seed_data.kdj,
            rsi_state=seed_data.rsi,
            boll_state=seed_data.boll,
            wr_state=seed_data.wr,
            cci_state=seed_data.cci
        )
        
        return StrategyCheckResultResponse(
            strategy_id=strategy.id,
            symbol=strategy.symbol,
            current_price=result.current_price,
            check_date=result.check_date.isoformat(),
            can_enter_today=result.can_enter_today,
            entry_price_min=result.entry_price_min,
            entry_price_max=result.entry_price_max,
            entry_confidence=result.entry_confidence,
            entry_distance_pct=result.entry_distance_pct,
            stop_loss_price=result.stop_loss_price,
            stop_loss_distance_pct=result.stop_loss_distance_pct,
            take_profit_price=result.take_profit_price,
            take_profit_distance_pct=result.take_profit_distance_pct,
            recommendation=result.recommendation,
            risk_reward_ratio=result.risk_reward_ratio
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"策略检查失败: {str(e)}")


@router.post("/{strategy_id}/check-all")
async def check_all_strategies(symbol: Optional[str] = None):
    """
    批量检查所有策略
    
    返回每个策略的检查结果，方便快速查看今日交易机会
    
    Args:
        symbol: 指定股票代码，不指定则检查所有策略
    """
    strategies = list(strategy_storage.values())
    if symbol:
        strategies = [s for s in strategies if s.symbol == symbol]
    
    results = []
    for strategy in strategies:
        try:
            # 获取数据
            seed_data = await data_service.calculate_indicator_seed(strategy.symbol)
            price = seed_data.last_close
            
            # 更新价格
            seed_data.macd.current_price = price
            seed_data.ma.current_price = price
            seed_data.kdj.current_price = price
            
            # 检查
            check_result = strategy_engine.check_strategy(
                strategy=strategy,
                current_price=price,
                macd_state=seed_data.macd,
                ma_state=seed_data.ma,
                kdj_state=seed_data.kdj
            )
            
            results.append({
                "strategy_id": strategy.id,
                "name": strategy.name,
                "symbol": strategy.symbol,
                "status": strategy.status.value,
                "can_enter": check_result.can_enter_today,
                "entry_range": {
                    "min": check_result.entry_price_min,
                    "max": check_result.entry_price_max
                } if check_result.can_enter_today else None,
                "stop_loss": check_result.stop_loss_price,
                "recommendation": check_result.recommendation
            })
        except Exception as e:
            results.append({
                "strategy_id": strategy.id,
                "name": strategy.name,
                "error": str(e)
            })
    
    # 分类统计
    can_enter = [r for r in results if r.get("can_enter")]
    already_entered = [r for r in results if r.get("status") == "entered"]
    
    return {
        "total": len(results),
        "can_enter_today": len(can_enter),
        "already_entered": len(already_entered),
        "opportunities": can_enter,
        "monitoring": already_entered,
        "all_results": results
    }


# ============= 策略执行接口 =============

@router.post("/{strategy_id}/enter", response_model=StrategyResponse)
async def execute_entry(strategy_id: str, request: ExecuteEntryRequest):
    """
    执行策略入场
    
    记录实际入场价格和日期，开始跟踪止损
    """
    if strategy_id not in strategy_storage:
        raise HTTPException(status_code=404, detail="策略不存在")
    
    strategy = strategy_storage[strategy_id]
    
    if strategy.status != StrategyStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"策略状态为{strategy.status.value}，无法入场")
    
    # 执行入场
    updated_strategy = strategy_engine.execute_entry(strategy, request.price)
    strategy_storage[strategy_id] = updated_strategy
    
    return _strategy_to_response(updated_strategy)


@router.post("/{strategy_id}/exit", response_model=StrategyResponse)
async def execute_exit(strategy_id: str, request: ExecuteExitRequest):
    """
    执行策略出场
    
    出场原因：
    - stop_loss: 触发止损
    - take_profit: 触发止盈
    - manual: 手动平仓
    """
    if strategy_id not in strategy_storage:
        raise HTTPException(status_code=404, detail="策略不存在")
    
    strategy = strategy_storage[strategy_id]
    
    if strategy.status != StrategyStatus.ENTERED:
        raise HTTPException(status_code=400, detail="只有已入场的策略才能执行出场")
    
    # 执行出场
    updated_strategy = strategy_engine.execute_exit(strategy, request.price, request.reason)
    strategy_storage[strategy_id] = updated_strategy
    
    return _strategy_to_response(updated_strategy)


# ============= 辅助函数 =============

def _strategy_to_response(strategy: TradingStrategy) -> StrategyResponse:
    """将策略对象转换为响应模型"""
    return StrategyResponse(
        id=strategy.id,
        name=strategy.name,
        symbol=strategy.symbol,
        status=strategy.status.value,
        entry_description=strategy.entry.description,
        stop_loss_description=strategy.stop_loss.description,
        take_profit_description=strategy.take_profit.description if strategy.take_profit else None,
        entry_price=strategy.entry_price,
        entry_date=strategy.entry_date.isoformat() if strategy.entry_date else None,
        stop_loss_price=strategy.stop_loss_price,
        notes=strategy.notes,
        created_at=strategy.created_at.isoformat()
    )
