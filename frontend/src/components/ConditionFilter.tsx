/**
 * 条件筛选器组件
 * 
 * 允许用户自定义技术指标组合，计算满足所有条件的"共振价格区间"
 */

import React, { useState, useEffect } from 'react';
import { 
  ConditionInput, 
  ConditionFilterResponse, 
  ConditionScenario,
  ConstraintDetail,
  UnsatisfiedCondition 
} from '../types';
import { filterByConditions, getPredefinedScenarios, quickFilter } from '../services/api';

// 可用的条件类型
const AVAILABLE_CONDITIONS = [
  { type: 'price_above_ma', label: '股价 > MA', params: { period: 5 }, desc: '股价站上N日均线' },
  { type: 'price_below_ma', label: '股价 < MA', params: { period: 10 }, desc: '股价低于N日均线' },
  { type: 'price_between_mas', label: '股价在MA区间', params: { short: 5, long: 20 }, desc: '股价在短期和长期均线之间' },
  { type: 'ma_golden', label: '均线金叉', params: { short: 5, long: 20 }, desc: '短期均线上穿长期均线' },
  { type: 'macd_golden', label: 'MACD金叉', params: {}, desc: 'MACD水上金叉' },
  { type: 'macd_above_zero', label: 'MACD水上', params: {}, desc: 'DIF > 0' },
  { type: 'kdj_oversold', label: 'KDJ超卖', params: {}, desc: 'KDJ J < 0' },
  { type: 'rsi_oversold', label: 'RSI超卖', params: {}, desc: 'RSI < 30' },
  { type: 'rsi_overbought', label: 'RSI超买', params: {}, desc: 'RSI > 70' },
  { type: 'boll_lower', label: '触及布林下轨', params: {}, desc: '股价触及布林带下轨' },
  { type: 'wr_oversold', label: 'WR超卖', params: {}, desc: 'WR >= -20' },
  { type: 'wr_overbought', label: 'WR超买', params: {}, desc: 'WR <= -80' },
];

interface ConditionFilterProps {
  symbol: string;
  currentPrice?: number;
}

export const ConditionFilter: React.FC<ConditionFilterProps> = ({ 
  symbol, 
  currentPrice: propCurrentPrice 
}) => {
  const [scenarios, setScenarios] = useState<ConditionScenario[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<string>('');
  const [conditions, setConditions] = useState<ConditionInput[]>([]);
  const [result, setResult] = useState<ConditionFilterResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPrice, setCurrentPrice] = useState<number>(propCurrentPrice || 0);
  const [activeTab, setActiveTab] = useState<'scenarios' | 'custom'>('scenarios');

  // 加载预定义场景
  useEffect(() => {
    loadScenarios();
  }, []);

  // 更新当前价格
  useEffect(() => {
    if (propCurrentPrice) {
      setCurrentPrice(propCurrentPrice);
    }
  }, [propCurrentPrice]);

  const loadScenarios = async () => {
    try {
      const data = await getPredefinedScenarios();
      setScenarios(data.scenarios);
    } catch (err) {
      console.error('加载场景失败:', err);
    }
  };

  // 使用场景进行快速筛选
  const handleQuickFilter = async (scenarioName: string) => {
    if (!symbol) {
      setError('请先选择股票');
      return;
    }

    setLoading(true);
    setError(null);
    setSelectedScenario(scenarioName);

    try {
      const data = await quickFilter(symbol, scenarioName, currentPrice > 0 ? currentPrice : undefined);
      setResult(data);
      setCurrentPrice(data.current_price);
    } catch (err: any) {
      setError(err.response?.data?.detail || '筛选失败');
    } finally {
      setLoading(false);
    }
  };

  // 使用自定义条件筛选
  const handleCustomFilter = async () => {
    if (!symbol) {
      setError('请先选择股票');
      return;
    }
    if (conditions.length === 0) {
      setError('请至少添加一个条件');
      return;
    }

    setLoading(true);
    setError(null);
    setSelectedScenario('');

    try {
      const request = {
        symbol,
        current_price: currentPrice > 0 ? currentPrice : 0,
        conditions,
        use_auto_data: true
      };
      const data = await filterByConditions(request);
      setResult(data);
      setCurrentPrice(data.current_price);
    } catch (err: any) {
      setError(err.response?.data?.detail || '筛选失败');
    } finally {
      setLoading(false);
    }
  };

  // 添加条件
  const addCondition = (conditionType: string, params: Record<string, any> = {}) => {
    const newCondition: ConditionInput = {
      condition_type: conditionType,
      params: { ...params },
      weight: 1.0
    };
    setConditions([...conditions, newCondition]);
  };

  // 移除条件
  const removeCondition = (index: number) => {
    setConditions(conditions.filter((_, i) => i !== index));
  };

  // 更新条件参数
  const updateConditionParam = (index: number, key: string, value: any) => {
    const updated = [...conditions];
    updated[index].params[key] = value;
    setConditions(updated);
  };

  // 获取置信度颜色
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  // 获取置信度标签
  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return '高';
    if (confidence >= 0.5) return '中';
    return '低';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4">智能条件筛选器</h2>
      
      {/* 标签切换 */}
      <div className="flex border-b border-gray-200 mb-4">
        <button
          className={`px-4 py-2 font-medium text-sm transition-colors ${
            activeTab === 'scenarios'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('scenarios')}
        >
          预设场景
        </button>
        <button
          className={`px-4 py-2 font-medium text-sm transition-colors ${
            activeTab === 'custom'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('custom')}
        >
          自定义条件
        </button>
      </div>

      {/* 当前价格显示/输入 */}
      <div className="mb-4 flex items-center gap-4">
        <label className="text-sm text-gray-600">当前价格:</label>
        <input
          type="number"
          value={currentPrice}
          onChange={(e) => setCurrentPrice(parseFloat(e.target.value) || 0)}
          className="px-3 py-1 border rounded text-sm w-32"
          placeholder="自动获取"
        />
        {currentPrice > 0 && (
          <span className="text-sm text-gray-500">¥{currentPrice.toFixed(2)}</span>
        )}
      </div>

      {/* 预设场景模式 */}
      {activeTab === 'scenarios' && (
        <div className="space-y-3">
          <p className="text-sm text-gray-500 mb-2">选择预设的技术指标组合场景:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {scenarios.map((scenario) => (
              <button
                key={scenario.name}
                onClick={() => handleQuickFilter(scenario.name)}
                disabled={loading}
                className={`p-4 border rounded-lg text-left transition-all hover:shadow-md ${
                  selectedScenario === scenario.name
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-blue-300'
                }`}
              >
                <div className="font-medium text-gray-800 mb-1">{scenario.name}</div>
                <div className="text-xs text-gray-500 mb-2">{scenario.description}</div>
                <div className="flex flex-wrap gap-1">
                  {scenario.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 自定义条件模式 */}
      {activeTab === 'custom' && (
        <div className="space-y-4">
          {/* 条件列表 */}
          <div className="space-y-2">
            <p className="text-sm text-gray-500">已添加的条件:</p>
            {conditions.length === 0 ? (
              <p className="text-sm text-gray-400 italic">点击下方按钮添加条件</p>
            ) : (
              conditions.map((cond, index) => {
                const condDef = AVAILABLE_CONDITIONS.find(c => c.type === cond.condition_type);
                return (
                  <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                    <span className="text-sm font-medium">{condDef?.label || cond.condition_type}</span>
                    {Object.entries(cond.params).map(([key, value]) => (
                      <span key={key} className="text-xs text-gray-500">
                        {key}: {value}
                      </span>
                    ))}
                    <button
                      onClick={() => removeCondition(index)}
                      className="ml-auto text-red-500 hover:text-red-700 text-sm"
                    >
                      移除
                    </button>
                  </div>
                );
              })
            )}
          </div>

          {/* 添加条件按钮 */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {AVAILABLE_CONDITIONS.map((cond) => (
              <button
                key={cond.type}
                onClick={() => addCondition(cond.type, cond.params)}
                className="p-2 text-sm border rounded hover:bg-gray-50 text-left"
                title={cond.desc}
              >
                + {cond.label}
              </button>
            ))}
          </div>

          {/* 执行筛选按钮 */}
          <button
            onClick={handleCustomFilter}
            disabled={loading || conditions.length === 0}
            className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? '计算中...' : '执行筛选'}
          </button>
        </div>
      )}

      {/* 错误提示 */}
      {error && (
        <div className="mt-4 p-3 bg-red-50 text-red-600 rounded text-sm">
          {error}
        </div>
      )}

      {/* 结果展示 */}
      {result && (
        <div className="mt-6 space-y-4 border-t border-gray-200 pt-4">
          <h3 className="font-bold text-gray-800">筛选结果</h3>
          
          {/* 可行区间 */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600 mb-2">满足所有条件的共振价格区间</div>
            <div className="flex items-baseline gap-2">
              {result.feasible_range.min !== null ? (
                <span className="text-xl font-bold text-gray-800">
                  ¥{result.feasible_range.min.toFixed(2)}
                </span>
              ) : (
                <span className="text-xl font-bold text-gray-400">-∞</span>
              )}
              <span className="text-gray-500">~</span>
              {result.feasible_range.max !== null ? (
                <span className="text-xl font-bold text-gray-800">
                  ¥{result.feasible_range.max.toFixed(2)}
                </span>
              ) : (
                <span className="text-xl font-bold text-gray-400">+∞</span>
              )}
            </div>
          </div>

          {/* 置信度和推荐 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-gray-50 rounded">
              <div className="text-xs text-gray-500 mb-1">匹配置信度</div>
              <div className={`text-2xl font-bold ${getConfidenceColor(result.confidence)}`}>
                {(result.confidence * 100).toFixed(1)}%
              </div>
              <div className={`text-xs ${getConfidenceColor(result.confidence)}`}>
                {getConfidenceLabel(result.confidence)}
              </div>
            </div>
            <div className="p-3 bg-gray-50 rounded">
              <div className="text-xs text-gray-500 mb-1">目标价格</div>
              {result.target_price ? (
                <>
                  <div className="text-2xl font-bold text-blue-600">
                    ¥{result.target_price.toFixed(2)}
                  </div>
                  <div className={`text-xs ${
                    (result.distance_to_target || 0) > 0 ? 'text-red-500' : 'text-green-500'
                  }`}>
                    {(result.distance_to_target || 0) > 0 ? '还需上涨 ' : '还需下跌 '}
                    {Math.abs(result.distance_to_target || 0).toFixed(2)}%
                  </div>
                </>
              ) : (
                <div className="text-gray-400">--</div>
              )}
            </div>
          </div>

          {/* 推荐建议 */}
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
            <div className="text-sm font-medium text-yellow-800 mb-1">智能建议</div>
            <div className="text-sm text-yellow-700">{result.recommendation}</div>
          </div>

          {/* 条件详情 */}
          <div className="space-y-2">
            <div className="text-sm font-medium text-gray-700">各条件约束详情:</div>
            {result.constraints.map((constraint, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm">
                <span>{constraint.description}</span>
                <div className="flex items-center gap-3">
                  <span className="text-blue-600 font-medium">{constraint.range}</span>
                  <span className="text-xs text-gray-500">可信度: {(constraint.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>

          {/* 满足/未满足的条件 */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm font-medium text-green-700 mb-2">
                已满足 ({result.satisfied.length})
              </div>
              {result.satisfied.length === 0 ? (
                <p className="text-xs text-gray-400 italic">暂无</p>
              ) : (
                <ul className="space-y-1">
                  {result.satisfied.map((item, index) => (
                    <li key={index} className="text-xs text-green-600 flex items-center gap-1">
                      <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                      {item}
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div>
              <div className="text-sm font-medium text-red-700 mb-2">
                未满足 ({result.unsatisfied.length})
              </div>
              {result.unsatisfied.length === 0 ? (
                <p className="text-xs text-gray-400 italic">全部满足！</p>
              ) : (
                <ul className="space-y-1">
                  {result.unsatisfied.map((item, index) => (
                    <li key={index} className="text-xs text-red-600 flex items-center justify-between">
                      <span className="flex items-center gap-1">
                        <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                        {item.condition}
                      </span>
                      <span className="text-gray-500">距离: {item.distance_pct}%</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConditionFilter;
