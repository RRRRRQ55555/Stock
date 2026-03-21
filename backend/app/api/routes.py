"""
REST API 路由

提供临界价格计算、历史数据获取、压力测试等功能
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any

from ..models.schemas import (
    TriggerMatrixRequest,
    TriggerMatrixResponse,
    StressTestRequest,
    StressTestResponse,
    HistoricalDataRequest,
    HistoricalDataResponse,
    StockSymbol,
    AlertMessage,
    ConditionFilterRequest,
    ConditionFilterResponse,
    ConditionInput,
    GetScenariosResponse,
    ConditionScenario
)
from ..core.indicator_engine import IndicatorEngine
from ..core.macd_solver import MACDState
from ..core.ma_solver import MAState
from ..core.kdj_solver import KDJState
from ..core.rsi_solver import RSIState
from ..core.boll_solver import BOLLState
from ..core.wr_solver import WRState
from ..core.cci_solver import CCIState
from ..services.data_service import data_service
from ..services.simple_data_service import simple_data_service
from ..services.alert_service import alert_service, AlertRule
from ..core.condition_filter import (
    ConditionFilter, Condition, ConditionType,
    create_common_conditions
)


router = APIRouter()


# ============= 核心计算接口 =============

@router.post("/matrix", response_model=TriggerMatrixResponse)
async def calculate_trigger_matrix(request: TriggerMatrixRequest):
    """
    计算临界价格触发矩阵
    
    根据昨日收盘后的指标状态，计算触发各种技术信号所需的临界价格
    """
    try:
        # 构建求解器状态
        macd_state = MACDState(
            ema_12=request.macd.ema_12,
            ema_26=request.macd.ema_26,
            signal=request.macd.signal,
            dif=request.macd.dif,
            close=request.macd.close
        )
        
        ma_state = MAState(
            prices_short=request.ma.prices_short,
            prices_long=request.ma.prices_long,
            short_period=request.ma.short_period,
            long_period=request.ma.long_period,
            current_price=request.current_price
        )
        
        kdj_state = KDJState(
            k_yest=request.kdj.k_yest,
            d_yest=request.kdj.d_yest,
            h9=request.kdj.h9,
            l9=request.kdj.l9,
            current_price=request.current_price
        )
        
        # 使用引擎计算
        engine = IndicatorEngine()
        matrix = engine.calculate_trigger_matrix(
            symbol=request.symbol,
            current_price=request.current_price,
            macd_state=macd_state,
            ma_state=ma_state,
            kdj_state=kdj_state
        )
        
        return matrix.to_dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算失败: {str(e)}")


@router.post("/matrix/auto/{symbol}", response_model=TriggerMatrixResponse)
async def calculate_trigger_matrix_auto(
    symbol: str,
    current_price: Optional[float] = None,
    mock: bool = False
):
    """
    自动计算临界价格触发矩阵

    自动从Yahoo Finance获取历史数据并计算指标状态

    Args:
        mock: 是否使用模拟数据（用于测试，避免API限流）
    """
    try:
        # 获取指标种子数据（支持模拟数据模式）
        seed_data = await data_service.calculate_indicator_seed(symbol, use_mock=mock)

        # 如果没有提供当前价格，使用种子数据中的价格或获取实时价格
        if current_price is None:
            if mock:
                current_price = seed_data.last_close
            else:
                try:
                    current_price = await data_service.get_current_price(symbol)
                except:
                    # 如果获取失败，使用种子数据中的价格
                    current_price = seed_data.last_close

        # 更新种子数据中的当前价格
        seed_data.macd.current_price = current_price
        seed_data.ma.current_price = current_price
        seed_data.kdj.current_price = current_price
        seed_data.rsi.current_price = current_price
        seed_data.boll.current_price = current_price
        seed_data.wr.current_price = current_price
        seed_data.cci.current_price = current_price

        # 计算触发矩阵（包含所有指标）
        engine = IndicatorEngine()
        matrix = engine.calculate_trigger_matrix(
            symbol=symbol,
            current_price=current_price,
            macd_state=seed_data.macd,
            ma_state=seed_data.ma,
            kdj_state=seed_data.kdj,
            rsi_state=seed_data.rsi,
            boll_state=seed_data.boll,
            wr_state=seed_data.wr,
            cci_state=seed_data.cci
        )

        # 获取股票名称
        stock_info = simple_data_service.get_stock_by_symbol(symbol)
        stock_name = stock_info["name"] if stock_info else symbol

        # 构建返回结果
        result = matrix.to_dict()
        result["name"] = stock_name
        result["symbol"] = symbol
        result["current_price"] = current_price

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"自动计算失败: {str(e)}")


@router.post("/stress-test", response_model=StressTestResponse)
async def stress_test(request: StressTestRequest):
    """
    压力测试
    
    模拟在假设价格下的所有技术指标状态
    """
    try:
        # 构建求解器状态
        macd_state = MACDState(
            ema_12=request.macd.ema_12,
            ema_26=request.macd.ema_26,
            signal=request.macd.signal,
            dif=request.macd.dif,
            close=request.macd.close
        )
        
        ma_state = MAState(
            prices_short=request.ma.prices_short,
            prices_long=request.ma.prices_long,
            short_period=request.ma.short_period,
            long_period=request.ma.long_period,
            current_price=request.current_price
        )
        
        kdj_state = KDJState(
            k_yest=request.kdj.k_yest,
            d_yest=request.kdj.d_yest,
            h9=request.kdj.h9,
            l9=request.kdj.l9,
            current_price=request.current_price
        )
        
        # 执行压力测试
        engine = IndicatorEngine()
        result = engine.stress_test(
            hypothetical_price=request.hypothetical_price,
            macd_state=macd_state,
            ma_state=ma_state,
            kdj_state=kdj_state
        )
        
        return StressTestResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"压力测试失败: {str(e)}")


@router.post("/strategy/price-range/{symbol}")
async def calculate_strategy_price_range(
    symbol: str,
    buy_conditions: Dict[str, bool] = None,
    stop_conditions: Dict[str, bool] = None,
    current_price: float = None
):
    """
    计算策略满足的价格区间

    分析在什么价格区间，用户的买入/止损策略会被满足

    Args:
        buy_conditions: 买入条件设置，如 {"macdGolden": true, "maGolden": false}
        stop_conditions: 止损条件设置
        current_price: 当前价格（可选，自动获取）

    Returns:
        价格区间和距离分析
    """
    try:
        # 获取指标种子数据
        seed_data = await data_service.calculate_indicator_seed(symbol)

        # 获取当前价格
        if current_price is None:
            current_price = await data_service.get_current_price(symbol)

        # 获取股票名称
        stock_info = simple_data_service.get_stock_by_symbol(symbol)
        stock_name = stock_info["name"] if stock_info else symbol

        # 计算策略价格区间
        engine = IndicatorEngine()
        price_range = engine.calculate_strategy_range(
            current_price=current_price,
            macd_state=seed_data.macd,
            ma_state=seed_data.ma,
            kdj_state=seed_data.kdj,
            rsi_state=seed_data.rsi,
            buy_conditions=buy_conditions or {},
            stop_conditions=stop_conditions or {}
        )

        return {
            "symbol": symbol,
            "name": stock_name,
            "current_price": current_price,
            "buy_range": price_range.get("buy"),
            "stop_range": price_range.get("stop"),
            "recommendation": price_range.get("recommendation")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算策略价格区间失败: {str(e)}")


# ============= 数据接口 =============

@router.get("/historical/{symbol}", response_model=HistoricalDataResponse)
async def get_historical_data(
    symbol: str,
    period: str = Query("1y", description="时间周期"),
    interval: str = Query("1d", description="时间间隔")
):
    """
    获取历史K线数据
    
    从 Yahoo Finance 获取指定股票的历史数据
    """
    try:
        response = await data_service.get_historical_data(symbol, period, interval)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史数据失败: {str(e)}")


@router.get("/current-price/{symbol}")
async def get_current_price(symbol: str):
    """获取当前价格"""
    try:
        price = await data_service.get_current_price(symbol)

        # 获取股票名称
        stock_info = simple_data_service.get_stock_by_symbol(symbol)
        stock_name = stock_info["name"] if stock_info else symbol

        return {
            "symbol": symbol,
            "name": stock_name,
            "price": price,
            "timestamp": "now"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取当前价格失败: {str(e)}")


@router.get("/search")
async def search_symbols(q: str = Query(..., min_length=1, max_length=20)):
    """搜索股票代码（纯本地搜索）"""
    from ..services.simple_data_service import simple_data_service
    
    query_str = str(q).strip() if q else ""
    if not query_str:
        return []
    
    results = simple_data_service.search_symbols(query_str)
    return results


# ============= 预警接口 =============

@router.post("/alerts/subscribe/{symbol}")
async def subscribe_alerts(
    symbol: str,
    threshold_pct: float = Query(1.0, description="接近预警阈值(%)"),
    alert_types: List[str] = Query(["proximity", "triggered", "resonance"])
):
    """
    订阅股票预警
    
    当价格接近临界点或触发信号时接收通知
    """
    try:
        rule = AlertRule(
            symbol=symbol,
            alert_type=",".join(alert_types),
            threshold_pct=threshold_pct,
            enabled=True
        )
        alert_service.add_rule(rule)
        
        return {
            "status": "success",
            "message": f"已订阅 {symbol} 的预警",
            "threshold_pct": threshold_pct,
            "alert_types": alert_types
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"订阅失败: {str(e)}")


@router.post("/alerts/unsubscribe/{symbol}")
async def unsubscribe_alerts(symbol: str):
    """取消订阅股票预警"""
    alert_service.remove_rule(symbol)
    return {"status": "success", "message": f"已取消订阅 {symbol} 的预警"}


@router.get("/alerts/check/{symbol}")
async def check_alerts_manual(
    symbol: str,
    current_price: float
):
    """
    手动检查预警条件
    
    传入当前价格，检查是否满足预警条件
    """
    try:
        # 获取触发矩阵
        seed_data = await data_service.calculate_indicator_seed(symbol)
        
        # 更新当前价格
        seed_data.macd.current_price = current_price
        seed_data.ma.current_price = current_price
        seed_data.kdj.current_price = current_price
        
        # 计算矩阵
        engine = IndicatorEngine()
        matrix = engine.calculate_trigger_matrix(
            symbol=symbol,
            current_price=current_price,
            macd_state=seed_data.macd,
            ma_state=seed_data.ma,
            kdj_state=seed_data.kdj
        )
        
        # 检查预警
        alerts = await alert_service.check_alerts(symbol, current_price, matrix)
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "alerts": [alert.dict() for alert in alerts],
            "alert_count": len(alerts)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查预警失败: {str(e)}")


# ============= 批量接口 =============

@router.post("/matrix/batch")
async def calculate_trigger_matrix_batch(
    symbols: List[str],
    current_prices: Optional[List[float]] = None
):
    """
    批量计算临界价格矩阵
    
    同时计算多只股票的技术指标临界价格
    """
    try:
        results = {}
        
        for i, symbol in enumerate(symbols):
            try:
                # 获取指标种子数据
                seed_data = await data_service.calculate_indicator_seed(symbol)
                
                # 使用传入的价格或获取实时价格
                if current_prices and i < len(current_prices):
                    current_price = current_prices[i]
                else:
                    current_price = await data_service.get_current_price(symbol)
                
                # 更新种子数据
                seed_data.macd.current_price = current_price
                seed_data.ma.current_price = current_price
                seed_data.kdj.current_price = current_price
                
                # 计算
                engine = IndicatorEngine()
                matrix = engine.calculate_trigger_matrix(
                    symbol=symbol,
                    current_price=current_price,
                    macd_state=seed_data.macd,
                    ma_state=seed_data.ma,
                    kdj_state=seed_data.kdj
                )
                
                results[symbol] = matrix.to_dict()
                
            except Exception as e:
                results[symbol] = {"error": str(e)}
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量计算失败: {str(e)}")


# ============= 条件筛选器接口 =============

def _convert_condition_input(input_cond: ConditionInput) -> Condition:
    """转换请求条件为内部Condition对象"""
    try:
        cond_type = ConditionType(input_cond.condition_type)
    except ValueError:
        # 尝试映射常见别名
        type_map = {
            "price_above_ma": ConditionType.PRICE_ABOVE_MA,
            "price_below_ma": ConditionType.PRICE_BELOW_MA,
            "price_between_mas": ConditionType.PRICE_BETWEEN_MAS,
            "ma_golden": ConditionType.MA_GOLDEN_CROSS,
            "macd_golden": ConditionType.MACD_GOLDEN_CROSS,
            "macd_above_zero": ConditionType.MACD_ABOVE_ZERO,
            "macd_dif_gt_signal": ConditionType.MACD_DIF_GT_SIGNAL,
            "kdj_k_lt_d": ConditionType.KDJ_K_LT_D,
            "kdj_j_lt_zero": ConditionType.KDJ_J_LT_ZERO,
            "kdj_j_gt_100": ConditionType.KDJ_J_GT_100,
            "rsi_oversold": ConditionType.RSI_OVERSOLD,
            "rsi_overbought": ConditionType.RSI_OVERBOUGHT,
            "rsi_between": ConditionType.RSI_BETWEEN,
            "boll_above_upper": ConditionType.BOLL_ABOVE_UPPER,
            "boll_below_lower": ConditionType.BOLL_BELOW_LOWER,
            "boll_inside": ConditionType.BOLL_INSIDE,
            "wr_oversold": ConditionType.WR_OVERSOLD,
            "wr_overbought": ConditionType.WR_OVERBOUGHT,
            "cci_above_100": ConditionType.CCI_ABOVE_100,
            "cci_below_minus100": ConditionType.CCI_BELOW_MINUS100,
        }
        cond_type = type_map.get(input_cond.condition_type, ConditionType.PRICE_ABOVE_MA)
    
    return Condition(
        condition_type=cond_type,
        params=input_cond.params,
        weight=input_cond.weight
    )


@router.post("/filter", response_model=ConditionFilterResponse)
async def filter_by_conditions(request: ConditionFilterRequest):
    """
    条件筛选器
    
    根据用户自定义的技术指标组合，计算满足所有条件的"共振价格区间"
    
    示例条件：
    - price_above_ma: 股价 > MA5
    - price_below_ma: 股价 < MA10
    - macd_golden: MACD水上金叉
    - macd_above_zero: DIF > 0
    - kdj_oversold: KDJ J < 0
    - rsi_oversold: RSI < 30
    - boll_lower: 股价触及布林下轨
    """
    try:
        # 转换条件
        conditions = [_convert_condition_input(c) for c in request.conditions]
        
        if not conditions:
            raise HTTPException(status_code=400, detail="请提供至少一个条件")
        
        # 获取指标数据
        if request.use_auto_data:
            seed_data = await data_service.calculate_indicator_seed(request.symbol)
            
            # 使用传入的当前价格或从种子数据获取
            current_price = request.current_price or seed_data.last_close
            
            # 更新种子数据中的当前价格
            seed_data.macd.current_price = current_price
            seed_data.ma.current_price = current_price
            seed_data.kdj.current_price = current_price
            seed_data.rsi.current_price = current_price
            seed_data.boll.current_price = current_price
            seed_data.wr.current_price = current_price
            seed_data.cci.current_price = current_price
        else:
            # 使用用户提供的指标状态
            if not all([request.macd, request.ma, request.kdj]):
                raise HTTPException(status_code=400, detail="手动模式下需要提供macd、ma、kdj状态")
            
            current_price = request.current_price
            seed_data = type('obj', (object,), {
                'macd': MACDState(
                    ema_12=request.macd.ema_12,
                    ema_26=request.macd.ema_26,
                    signal=request.macd.signal,
                    dif=request.macd.dif,
                    close=request.macd.close,
                    current_price=current_price
                ),
                'ma': MAState(
                    prices_short=request.ma.prices_short,
                    prices_long=request.ma.prices_long,
                    short_period=request.ma.short_period,
                    long_period=request.ma.long_period,
                    current_price=current_price
                ),
                'kdj': KDJState(
                    k_yest=request.kdj.k_yest,
                    d_yest=request.kdj.d_yest,
                    h9=request.kdj.h9,
                    l9=request.kdj.l9,
                    current_price=current_price
                ),
                'rsi': None,
                'boll': None,
                'wr': None,
                'cci': None
            })()
        
        # 执行筛选
        filter_engine = ConditionFilter()
        result = filter_engine.filter(
            symbol=request.symbol,
            current_price=current_price,
            conditions=conditions,
            macd_state=seed_data.macd,
            ma_state=seed_data.ma,
            kdj_state=seed_data.kdj,
            rsi_state=getattr(seed_data, 'rsi', None),
            boll_state=getattr(seed_data, 'boll', None),
            wr_state=getattr(seed_data, 'wr', None),
            cci_state=getattr(seed_data, 'cci', None)
        )
        
        return ConditionFilterResponse(
            symbol=result.symbol,
            current_price=result.current_price,
            feasible_range=result.to_dict()["feasible_range"],
            confidence=result.overall_confidence,
            constraints=result.to_dict()["constraints"],
            satisfied=result.to_dict()["satisfied"],
            unsatisfied=result.to_dict()["unsatisfied"],
            recommendation=result.recommendation,
            target_price=result.target_price,
            distance_to_target=result.distance_to_target
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"条件筛选失败: {str(e)}")


@router.get("/filter/scenarios", response_model=GetScenariosResponse)
async def get_predefined_scenarios():
    """
    获取预定义的条件筛选场景
    
    返回常用的技术指标组合场景
    """
    scenarios = [
        ConditionScenario(
            name="多头排列+MACD金叉",
            description="均线多头排列且MACD水上金叉，适合追涨",
            conditions=[
                ConditionInput(condition_type="price_above_ma", params={"period": 5}, weight=1.0),
                ConditionInput(condition_type="price_above_ma", params={"period": 10}, weight=1.0),
                ConditionInput(condition_type="macd_golden", params={}, weight=1.0),
            ],
            tags=["趋势跟踪", "追涨"]
        ),
        ConditionScenario(
            name="超卖反弹",
            description="多个指标显示超卖状态，适合抄底",
            conditions=[
                ConditionInput(condition_type="kdj_oversold", params={}, weight=1.0),
                ConditionInput(condition_type="rsi_oversold", params={}, weight=1.0),
                ConditionInput(condition_type="boll_lower", params={}, weight=0.8),
            ],
            tags=["抄底", "反弹"]
        ),
        ConditionScenario(
            name="水上金叉",
            description="MACD水上金叉配合站上5日线，强趋势信号",
            conditions=[
                ConditionInput(condition_type="macd_above_zero", params={}, weight=1.0),
                ConditionInput(condition_type="macd_golden", params={}, weight=1.0),
                ConditionInput(condition_type="price_above_ma", params={"period": 5}, weight=0.8),
            ],
            tags=["趋势", "强势"]
        ),
        ConditionScenario(
            name="均线粘合突破",
            description="5日线接近20日线且即将金叉，突破信号",
            conditions=[
                ConditionInput(condition_type="price_between_mas", params={"short": 5, "long": 20}, weight=1.0),
                ConditionInput(condition_type="ma_golden", params={"short": 5, "long": 20}, weight=1.0),
            ],
            tags=["突破", "趋势转折"]
        ),
        ConditionScenario(
            name="波段底部",
            description="WR超卖+RSI超卖，寻找波段底部",
            conditions=[
                ConditionInput(condition_type="wr_oversold", params={}, weight=1.0),
                ConditionInput(condition_type="rsi_oversold", params={}, weight=1.0),
                ConditionInput(condition_type="kdj_oversold", params={}, weight=0.8),
            ],
            tags=["波段", "底部", "抄底"]
        ),
    ]
    
    return GetScenariosResponse(scenarios=scenarios)


@router.post("/filter/quick/{symbol}")
async def quick_filter(
    symbol: str,
    scenario: str,
    current_price: Optional[float] = None
):
    """
    快速筛选
    
    使用预定义场景进行一键筛选
    
    Args:
        scenario: 场景名称，如 "多头排列+MACD金叉", "超卖反弹", "水上金叉"
    """
    try:
        # 获取场景条件
        scenarios_data = await get_predefined_scenarios()
        scenario_map = {s.name: s for s in scenarios_data.scenarios}
        
        if scenario not in scenario_map:
            available = ", ".join(scenario_map.keys())
            raise HTTPException(status_code=400, detail=f"未知场景 '{scenario}'。可用场景: {available}")
        
        selected_scenario = scenario_map[scenario]
        
        # 构建筛选请求
        request = ConditionFilterRequest(
            symbol=symbol,
            current_price=current_price or 0.0,  # 会被覆盖
            conditions=selected_scenario.conditions,
            use_auto_data=True
        )
        
        # 执行筛选
        return await filter_by_conditions(request)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"快速筛选失败: {str(e)}")


# ============= 指标参数配置接口 =============

@router.get("/indicator-patterns")
async def get_indicator_patterns():
    """
    获取技术指标形态（黑话术语）
    
    返回所有预定义的技术指标形态，包括：
    - MACD形态：水上金叉、水下金叉、水上死叉、水下死叉等
    - 均线形态：多头排列、空头排列、金叉、死叉等
    - KDJ形态：金叉、死叉、超卖、超买等
    """
    # region agent log: Entry point - hypothesis A/D
    import json, time, os
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'debug-612b9c.log')
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({'sessionId':'612b9c','id':'api_entry','timestamp':int(time.time()*1000),'location':'routes.py:625','message':'API /indicator-patterns called','data':{'log_path':log_path},'runId':'debug1','hypothesisId':'A'}, ensure_ascii=False)+'\n')
    except Exception as log_err:
        print(f"[DEBUG] 无法写入日志: {log_err}")
    # endregion
    
    try:
        # region agent log: Before import - hypothesis D
        with open('debug-612b9c.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({'sessionId':'612b9c','id':'before_import','timestamp':int(time.time()*1000),'location':'routes.py:636','message':'About to import indicator_patterns','data':{},'runId':'debug1','hypothesisId':'D'}, ensure_ascii=False)+'\n')
        # endregion
        
        from ..core.indicator_patterns import (
            MACD_PATTERNS, MA_PATTERNS, KDJ_PATTERNS,
            RSI_PATTERNS, BOLL_PATTERNS, COMBO_PATTERNS,
            CATEGORY_NAMES
        )
        
        # region agent log: After import success - hypothesis D
        with open('debug-612b9c.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({'sessionId':'612b9c','id':'import_success','timestamp':int(time.time()*1000),'location':'routes.py:644','message':'Import successful','data':{'macd_count':len(MACD_PATTERNS)},'runId':'debug1','hypothesisId':'D'}, ensure_ascii=False)+'\n')
        # endregion
        
        def pattern_to_dict(p):
            return {
                "id": p.id,
                "name": p.name,
                "category": p.category.value,
                "description": p.description,
                "params": p.params,
                "bullish": p.bullish,
                "strength": p.strength,
            }
        
        result = {
            "categories": CATEGORY_NAMES,
            "macd": [pattern_to_dict(p) for p in MACD_PATTERNS],
            "ma": [pattern_to_dict(p) for p in MA_PATTERNS],
            "kdj": [pattern_to_dict(p) for p in KDJ_PATTERNS],
            "rsi": [pattern_to_dict(p) for p in RSI_PATTERNS],
            "boll": [pattern_to_dict(p) for p in BOLL_PATTERNS],
            "combo": [pattern_to_dict(p) for p in COMBO_PATTERNS],
        }
        
        # region agent log: Success - hypothesis A/C
        with open('debug-612b9c.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({'sessionId':'612b9c','id':'success_return','timestamp':int(time.time()*1000),'location':'routes.py:675','message':'Returning success','data':{'macd':len(result['macd']),'ma':len(result['ma']),'kdj':len(result['kdj'])},'runId':'debug1','hypothesisId':'A'}, ensure_ascii=False)+'\n')
        # endregion
        
        print(f"[OK] 返回 {len(result['macd'])} 个MACD形态, {len(result['ma'])} 个MA形态")
        return result
        
    except Exception as e:
        # region agent log: Exception caught - hypothesis C
        import traceback
        tb = traceback.format_exc()
        with open('debug-612b9c.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({'sessionId':'612b9c','id':'exception','timestamp':int(time.time()*1000),'location':'routes.py:683','message':'Exception caught','data':{'error':str(e),'traceback':tb[:500]},'runId':'debug1','hypothesisId':'C'}, ensure_ascii=False)+'\n')
        # endregion
        
        print(f"[ERROR] 获取指标形态失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取指标形态失败: {str(e)}")


@router.post("/strategy/simple-check/{symbol}")
async def simple_strategy_check(
    symbol: str,
    pattern_ids: List[str],
    custom_params: Optional[Dict[str, Dict[str, Any]]] = None,
    current_price: Optional[float] = None
):
    """
    简化策略检查
    
    根据选择的技术指标形态，计算今日股价能否达到要求，给出价格区间。
    
    Args:
        pattern_ids: 选择的形态ID列表
        custom_params: 自定义参数，如 {"macd_golden_above": {"fast": 6, "slow": 13}}
        current_price: 当前价格（可选，不提供则自动获取）
    """
    try:
        from ..core.indicator_patterns import create_entry_strategy_from_patterns
        from ..core.condition_filter import ConditionFilter
        from ..services.data_service import data_service
        
        # 获取指标数据
        seed_data = await data_service.calculate_indicator_seed(symbol)
        price = current_price or seed_data.last_close
        
        # 更新当前价格到各指标状态
        seed_data.macd.current_price = price
        seed_data.ma.current_price = price
        seed_data.kdj.current_price = price
        seed_data.rsi.current_price = price
        seed_data.boll.current_price = price
        
        # 创建条件列表
        conditions = create_entry_strategy_from_patterns(pattern_ids, custom_params)
        
        if not conditions:
            return {
                "can_execute": False,
                "current_price": price,
                "recommendation": "请选择至少一个技术指标形态",
                "confidence": 0,
                "satisfied_conditions": [],
                "unsatisfied_conditions": []
            }
        
        # 执行筛选
        filter_engine = ConditionFilter()
        result = filter_engine.filter(
            symbol=symbol,
            current_price=price,
            conditions=conditions,
            macd_state=seed_data.macd,
            ma_state=seed_data.ma,
            kdj_state=seed_data.kdj,
            rsi_state=seed_data.rsi,
            boll_state=seed_data.boll,
            wr_state=seed_data.wr,
            cci_state=seed_data.cci
        )
        
        # 整理结果
        satisfied = [c.description for c in result.satisfied_conditions]
        unsatisfied = [c.description for c, _ in result.unsatisfied_conditions]
        
        can_execute = result.feasible_min is not None or result.feasible_max is not None
        
        # 计算距离
        distance = None
        if can_execute and result.feasible_min and result.feasible_max:
            target = (result.feasible_min + result.feasible_max) / 2
            distance = (target - price) / price * 100
        
        # 生成建议
        if can_execute:
            if result.feasible_min and result.feasible_max:
                recommendation = f"今日股价可达到您的技术指标要求！"
                if distance and distance > 0:
                    recommendation += f" 目标区间在现价上方{distance:.1f}%，建议关注。"
                elif distance and distance < 0:
                    recommendation += f" 目标区间在现价下方{abs(distance):.1f}%，可能已有买入机会。"
            else:
                recommendation = "技术指标部分满足，建议观望。"
        else:
            if unsatisfied:
                recommendation = f"今日不符合技术指标要求，等待：{', '.join(unsatisfied[:2])}"
            else:
                recommendation = "今日不符合技术指标要求，继续观望。"
        
        return {
            "can_execute": can_execute,
            "current_price": price,
            "price_min": result.feasible_min,
            "price_max": result.feasible_max,
            "confidence": result.overall_confidence,
            "distance_pct": distance,
            "recommendation": recommendation,
            "satisfied_conditions": satisfied,
            "unsatisfied_conditions": unsatisfied,
            "constraints": [
                {
                    "description": c.condition.description if c.condition else "",
                    "range": str(c),
                    "confidence": c.confidence
                }
                for c in result.constraints
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"策略检查失败: {str(e)}")


@router.get("/indicator-params")
async def get_indicator_params():
    """
    获取所有支持的指标参数配置
    
    返回均线、MACD、KDJ、RSI、布林带等指标的可用参数组合
    """
    from ..core.ma_solver import COMMON_MA_PAIRS, COMMON_MA_PERIODS
    from ..core.macd_solver import COMMON_MACD_SETS
    
    return {
        "ma": {
            "periods": COMMON_MA_PERIODS,
            "pairs": COMMON_MA_PAIRS,
            "description": "支持5/10/20/30/60/120/250日等多种均线周期"
        },
        "macd": {
            "sets": COMMON_MACD_SETS,
            "description": "支持标准(12,26,9)、短线(6,13,5)、长线(24,52,18)等参数"
        },
        "kdj": {
            "sets": [
                {"name": "标准KDJ", "n": 9, "m1": 3, "m2": 3, "desc": "经典参数，信号稳定"},
                {"name": "短线KDJ", "n": 5, "m1": 3, "m2": 3, "desc": "短线参数，反应更灵敏"},
                {"name": "长线KDJ", "n": 21, "m1": 3, "m2": 3, "desc": "过滤噪音，适合趋势"},
            ],
            "description": "支持(9,3,3)/(5,3,3)/(21,3,3)等参数组合"
        },
        "rsi": {
            "periods": [6, 12, 24],
            "description": "支持6日(短线)/12日(标准)/24日(长线)RSI"
        },
        "bollinger": {
            "sets": [
                {"name": "标准布林带", "period": 20, "std_dev": 2.0, "desc": "经典参数"},
                {"name": "长线布林带", "period": 26, "std_dev": 2.0, "desc": "减少假突破"},
                {"name": "短线布林带", "period": 10, "std_dev": 1.5, "desc": "更紧密的轨道"},
            ],
            "description": "支持(20,2)/(26,2)/(10,1.5)等参数组合"
        }
    }


@router.post("/matrix/multi-ma/{symbol}")
async def calculate_multi_ma_matrix(
    symbol: str,
    periods: Optional[List[int]] = Query(None, description="均线周期列表，如 [5,10,20,30,60]"),
    mock: bool = False
):
    """
    计算多周期均线触发矩阵
    
    同时计算5/10/20/30/60/120/250日均线状态和各组合的交叉临界价格
    
    Args:
        periods: 均线周期列表，默认 [5, 10, 20, 30, 60]
        mock: 是否使用模拟数据
    """
    try:
        from ..core.ma_solver import MultiMASolver
        
        # 获取历史数据
        seed_data = await data_service.calculate_indicator_seed(symbol, use_mock=mock)
        hist_data = await data_service.get_historical_data(symbol, period="1y", interval="1d")
        
        if len(hist_data.data) < 60:
            raise ValueError("历史数据不足60天，无法计算多周期均线")
        
        # 提取收盘价
        prices = [d.close for d in hist_data.data]
        current_price = prices[-1]
        
        # 使用多周期求解器
        periods_to_use = periods or [5, 10, 20, 30, 60]
        solver = MultiMASolver(periods=periods_to_use)
        result = solver.solve_all_periods(price_history=prices[:-1], current_price=current_price)
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "periods": periods_to_use,
            "ma_values": {str(k): round(v, 4) for k, v in result.ma_values.items()},
            "pairs": {
                name: {
                    "golden_cross_price": round(r.golden_cross_price, 4) if r.golden_cross_price else None,
                    "death_cross_price": round(r.death_cross_price, 4) if r.death_cross_price else None,
                    "ma_short": round(r.ma_short_current, 4),
                    "ma_long": round(r.ma_long_current, 4),
                    "is_bullish": r.is_bullish,
                    "distance_to_golden": round(r.distance_to_golden, 2) if r.distance_to_golden else None,
                    "distance_to_death": round(r.distance_to_death, 2) if r.distance_to_death else None,
                }
                for name, r in result.pair_results.items()
            },
            "overall_trend": result.overall_trend,
            "alignment_score": round(result.alignment_score, 4),
            "best_cross_pair": solver.get_best_cross_pair(result.ma_values),
            "recommendation": generate_ma_recommendation(result)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"多周期均线计算失败: {str(e)}")


def generate_ma_recommendation(result) -> str:
    """生成均线分析建议"""
    trend_map = {
        "strong_bullish": "均线多头排列强烈，趋势向上",
        "bullish": "均线多头排列，短线强于长线",
        "neutral": "均线走平，处于盘整阶段",
        "bearish": "均线空头排列，短线弱于长线",
        "strong_bearish": "均线空头排列强烈，趋势向下",
        "unknown": "均线数据不足，无法判断趋势"
    }
    
    recommendation = trend_map.get(result.overall_trend, "趋势不明")
    
    if result.alignment_score > 0.95:
        recommendation += "，均线高度粘合，即将选择方向突破"
    elif result.alignment_score > 0.9:
        recommendation += "，均线较为粘合，关注突破信号"
    
    return recommendation
