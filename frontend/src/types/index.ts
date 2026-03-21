/**
 * TypeScript 类型定义
 */

// ============ 基础类型 ============

export interface StockSymbol {
  symbol: string;
  name?: string;
  exchange?: string;
}

export interface PriceData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

// ============ 指标状态 ============

export interface MACDStateInput {
  ema_12: number;
  ema_26: number;
  signal: number;
  dif: number;
  close: number;
}

export interface MAStateInput {
  prices_short: number[];
  prices_long: number[];
  short_period: number;
  long_period: number;
}

export interface KDJStateInput {
  k_yest: number;
  d_yest: number;
  h9: number;
  l9: number;
}

// ============ 请求类型 ============

export interface TriggerMatrixRequest {
  symbol: string;
  current_price: number;
  macd: MACDStateInput;
  ma: MAStateInput;
  kdj: KDJStateInput;
}

export interface StressTestRequest {
  symbol: string;
  hypothetical_price: number;
  macd: MACDStateInput;
  ma: MAStateInput;
  kdj: KDJStateInput;
}

// ============ 响应类型 ============

export interface MACDResult {
  golden_cross_price?: number;
  death_cross_price?: number;
  dif: number;
  signal: number;
  distance_to_golden?: number;
  distance_to_death?: number;
}

export interface MAResult {
  golden_cross_price?: number;
  death_cross_price?: number;
  ma_short: number;
  ma_long: number;
  short_period: number;
  long_period: number;
  is_bullish: boolean;
  distance_to_golden?: number;
  distance_to_death?: number;
}

export interface KDJResult {
  oversold_price?: number;
  overbought_price?: number;
  k: number;
  d: number;
  j: number;
  zone: 'oversold' | 'neutral' | 'overbought';
  distance_to_oversold?: number;
  distance_to_overbought?: number;
}

export interface ResonanceZone {
  type: string;
  indicators: string[];
  price_min: number;
  price_max: number;
  price_center: number;
  confidence: number;
  distance_pct?: number;
}

export interface TriggerMatrixResponse {
  symbol: string;
  current_price: number;
  timestamp: string;
  macd: MACDResult;
  ma: MAResult;
  kdj: KDJResult;
  resonance: ResonanceZone[];
}

export interface StressTestResponse {
  hypothetical_price: number;
  macd: {
    hypothetical_price: number;
    dif: number;
    signal: number;
    histogram: number;
    is_golden_cross: boolean;
    is_death_cross: boolean;
    trend: string;
  };
  ma: {
    hypothetical_price: number;
    ma_short: number;
    ma_long: number;
    is_golden_cross: boolean;
    is_death_cross: boolean;
    trend: string;
  };
  kdj: {
    hypothetical_price: number;
    k: number;
    d: number;
    j: number;
    zone: string;
  };
  summary: {
    bullish_signals: number;
    bearish_signals: number;
    overall: 'bullish' | 'bearish' | 'neutral';
  };
}

// ============ WebSocket 消息 ============

export interface PriceUpdate {
  type: 'price_update';
  symbol: string;
  price: number;
  timestamp: string;
  change_pct?: number;
}

export interface AlertMessage {
  type: 'alert';
  symbol: string;
  alert_type: 'proximity' | 'triggered' | 'resonance';
  message: string;
  critical_price?: number;
  current_price: number;
  distance_pct?: number;
  timestamp: string;
}

export interface MatrixUpdate {
  type: 'matrix_update';
  symbol: string;
  matrix: TriggerMatrixResponse;
  timestamp: string;
}

export type WebSocketMessage = PriceUpdate | AlertMessage | MatrixUpdate;

// ============ 组件 Props ============

export interface TriggerCardProps {
  title: string;
  triggerPrice?: number;
  currentPrice: number;
  distance?: number;
  status: 'approaching' | 'triggered' | 'neutral';
  type: 'golden' | 'death' | 'oversold' | 'overbought';
}

export interface GaugeProps {
  value: number;
  min: number;
  max: number;
  label: string;
  unit?: string;
  color?: string;
}

// ============ 条件筛选器类型 ============

export interface ConditionInput {
  condition_type: string;
  params: Record<string, any>;
  weight: number;
}

export interface ConstraintDetail {
  description: string;
  range: string;
  confidence: number;
}

export interface UnsatisfiedCondition {
  condition: string;
  distance_pct: number;
}

export interface ConditionFilterRequest {
  symbol: string;
  current_price: number;
  conditions: ConditionInput[];
  use_auto_data: boolean;
}

export interface ConditionFilterResponse {
  symbol: string;
  current_price: number;
  feasible_range: {
    min: number | null;
    max: number | null;
  };
  confidence: number;
  constraints: ConstraintDetail[];
  satisfied: string[];
  unsatisfied: UnsatisfiedCondition[];
  recommendation: string;
  target_price?: number;
  distance_to_target?: number;
}

export interface ConditionScenario {
  name: string;
  description: string;
  conditions: ConditionInput[];
  tags: string[];
}

export interface GetScenariosResponse {
  scenarios: ConditionScenario[];
}
