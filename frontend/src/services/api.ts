/**
 * API 客户端
 * 
 * 与后端 FastAPI 服务通信
 */

import axios from 'axios';
import {
  TriggerMatrixRequest,
  TriggerMatrixResponse,
  StressTestRequest,
  StressTestResponse,
  StockSymbol,
  HistoricalDataResponse,
  ConditionFilterRequest,
  ConditionFilterResponse,
  GetScenariosResponse,
} from '../types';

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// ============ 核心计算接口 ============

/**
 * 计算临界价格矩阵（手动输入状态）
 */
export const calculateTriggerMatrix = async (
  request: TriggerMatrixRequest
): Promise<TriggerMatrixResponse> => {
  const response = await api.post<TriggerMatrixResponse>('/matrix', request);
  return response.data;
};

/**
 * 自动计算临界价格矩阵（自动获取历史数据）
 */
export const calculateTriggerMatrixAuto = async (
  symbol: string,
  currentPrice?: number
): Promise<TriggerMatrixResponse> => {
  const url = currentPrice 
    ? `/matrix/auto/${symbol}?current_price=${currentPrice}`
    : `/matrix/auto/${symbol}`;
  const response = await api.post<TriggerMatrixResponse>(url);
  return response.data;
};

/**
 * 执行压力测试
 */
export const stressTest = async (
  request: StressTestRequest
): Promise<StressTestResponse> => {
  const response = await api.post<StressTestResponse>('/stress-test', request);
  return response.data;
};

/**
 * 批量计算临界价格矩阵
 */
export const calculateTriggerMatrixBatch = async (
  symbols: string[],
  currentPrices?: number[]
): Promise<Record<string, TriggerMatrixResponse>> => {
  const response = await api.post<Record<string, TriggerMatrixResponse>>(
    '/matrix/batch',
    symbols,
    { params: { current_prices: currentPrices } }
  );
  return response.data;
};

// ============ 数据接口 ============

/**
 * 获取历史K线数据
 */
export const getHistoricalData = async (
  symbol: string,
  period: string = '1y',
  interval: string = '1d'
): Promise<HistoricalDataResponse> => {
  const response = await api.get<HistoricalDataResponse>(
    `/historical/${symbol}`,
    { params: { period, interval } }
  );
  return response.data;
};

/**
 * 获取当前价格
 */
export const getCurrentPrice = async (symbol: string): Promise<{ symbol: string; price: number }> => {
  const response = await api.get<{ symbol: string; price: number }>(`/current-price/${symbol}`);
  return response.data;
};

/**
 * 搜索股票代码
 */
export const searchSymbols = async (query: string, signal?: AbortSignal): Promise<StockSymbol[]> => {
  const response = await api.get<StockSymbol[]>('/search', { 
    params: { query },
    signal 
  });
  return response.data;
};

// ============ 预警接口 ============

/**
 * 订阅股票预警
 */
export const subscribeAlerts = async (
  symbol: string,
  thresholdPct: number = 1.0,
  alertTypes: string[] = ['proximity', 'triggered', 'resonance']
): Promise<{ status: string; message: string }> => {
  const response = await api.post(`/alerts/subscribe/${symbol}`, null, {
    params: { threshold_pct: thresholdPct, alert_types: alertTypes },
  });
  return response.data;
};

/**
 * 取消订阅股票预警
 */
export const unsubscribeAlerts = async (
  symbol: string
): Promise<{ status: string; message: string }> => {
  const response = await api.post(`/alerts/unsubscribe/${symbol}`);
  return response.data;
};

/**
 * 手动检查预警条件
 */
export const checkAlertsManual = async (
  symbol: string,
  currentPrice: number
): Promise<{ symbol: string; current_price: number; alerts: any[]; alert_count: number }> => {
  const response = await api.get(`/alerts/check/${symbol}`, {
    params: { current_price: currentPrice },
  });
  return response.data;
};

// ============ 健康检查 ============

/**
 * 检查服务健康状态
 */
export const healthCheck = async (): Promise<{ status: string; service: string; version: string }> => {
  const response = await axios.get('/health');
  return response.data;
};

// ============ 条件筛选器接口 ============

/**
 * 条件筛选 - 自定义条件
 */
export const filterByConditions = async (
  request: ConditionFilterRequest
): Promise<ConditionFilterResponse> => {
  const response = await api.post<ConditionFilterResponse>('/filter', request);
  return response.data;
};

/**
 * 获取预定义筛选场景
 */
export const getPredefinedScenarios = async (): Promise<GetScenariosResponse> => {
  const response = await api.get<GetScenariosResponse>('/filter/scenarios');
  return response.data;
};

/**
 * 快速筛选 - 使用预定义场景
 */
export const quickFilter = async (
  symbol: string,
  scenario: string,
  currentPrice?: number
): Promise<ConditionFilterResponse> => {
  const url = currentPrice
    ? `/filter/quick/${symbol}?scenario=${encodeURIComponent(scenario)}&current_price=${currentPrice}`
    : `/filter/quick/${symbol}?scenario=${encodeURIComponent(scenario)}`;
  const response = await api.post<ConditionFilterResponse>(url);
  return response.data;
};

/**
 * 获取指标参数配置
 */
export const getIndicatorParams = async (): Promise<any> => {
  const response = await api.get('/indicator-params');
  return response.data;
};

/**
 * 计算多周期均线矩阵
 */
export const getMultiMAMatrix = async (
  symbol: string,
  periods?: number[],
  mock?: boolean
): Promise<any> => {
  let url = `/matrix/multi-ma/${symbol}`;
  const params: string[] = [];
  
  if (periods && periods.length > 0) {
    periods.forEach(p => params.push(`periods=${p}`));
  }
  if (mock) {
    params.push('mock=true');
  }
  
  if (params.length > 0) {
    url += '?' + params.join('&');
  }
  
  const response = await api.post(url);
  return response.data;
};

// ============= 交易策略API =============

/**
 * 获取策略模板
 */
export const getStrategyTemplates = async (): Promise<any> => {
  const response = await api.get('/strategies/templates');
  return response.data;
};

/**
 * 获取策略列表
 */
export const getStrategies = async (status?: string, symbol?: string): Promise<any> => {
  const params: any = {};
  if (status) params.status = status;
  if (symbol) params.symbol = symbol;
  
  const response = await api.get('/strategies', { params });
  return response.data;
};

/**
 * 创建策略
 */
export const createStrategy = async (data: any): Promise<any> => {
  const response = await api.post('/strategies', data);
  return response.data;
};

/**
 * 检查单个策略
 */
export const checkStrategy = async (strategyId: string): Promise<any> => {
  const response = await api.get(`/strategies/${strategyId}/check`);
  return response.data;
};

/**
 * 批量检查所有策略
 */
export const checkAllStrategies = async (symbol?: string): Promise<any> => {
  const params: any = {};
  if (symbol) params.symbol = symbol;
  
  const response = await api.post('/strategies/check-all', null, { params });
  return response.data;
};

/**
 * 执行入场
 */
export const executeEntry = async (strategyId: string, price: number, notes?: string): Promise<any> => {
  const response = await api.post(`/strategies/${strategyId}/enter`, { price, notes });
  return response.data;
};

/**
 * 执行出场
 */
export const executeExit = async (strategyId: string, price: number, reason: string, notes?: string): Promise<any> => {
  const response = await api.post(`/strategies/${strategyId}/exit`, { price, reason, notes });
  return response.data;
};

/**
 * 删除策略
 */
export const deleteStrategy = async (strategyId: string): Promise<any> => {
  const response = await api.delete(`/strategies/${strategyId}`);
  return response.data;
};

/**
 * 获取技术指标形态（黑话）
 */
export const getIndicatorPatterns = async (): Promise<any> => {
  const response = await api.get('/indicator-patterns');
  return response.data;
};

/**
 * 简化策略检查
 */
export const checkStrategySimple = async (
  symbol: string,
  patternIds: string[],
  customParams?: Record<string, Record<string, any>>,
  currentPrice?: number
): Promise<any> => {
  const response = await api.post(`/strategy/simple-check/${symbol}`, {
    pattern_ids: patternIds,
    custom_params: customParams,
    current_price: currentPrice
  });
  return response.data;
};

export default api;
