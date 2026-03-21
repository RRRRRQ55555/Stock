/**
 * 多周期均线矩阵组件
 * 
 * 显示5/10/20/30/60/120/250日均线状态
 * 展示各均线组合的交叉临界价格
 */

import React, { useState, useEffect } from 'react';
import { getMultiMAMatrix } from '../services/api';

interface MultiMAMatrixProps {
  symbol: string;
}

interface MAValues {
  [key: string]: number;
}

interface MAPair {
  golden_cross_price?: number;
  death_cross_price?: number;
  ma_short: number;
  ma_long: number;
  is_bullish: boolean;
  distance_to_golden?: number;
  distance_to_death?: number;
}

interface MultiMAData {
  ma_values: MAValues;
  pairs: { [key: string]: MAPair };
  overall_trend: string;
  alignment_score: number;
  best_cross_pair?: string;
  recommendation: string;
}

export const MultiMAMatrix: React.FC<MultiMAMatrixProps> = ({ symbol }) => {
  const [data, setData] = useState<MultiMAData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriods, setSelectedPeriods] = useState<number[]>([5, 10, 20, 30, 60]);

  useEffect(() => {
    loadData();
  }, [symbol, selectedPeriods]);

  const loadData = async () => {
    if (!symbol) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await getMultiMAMatrix(symbol, selectedPeriods);
      setData(result);
    } catch (e) {
      setError('加载多周期均线数据失败');
    } finally {
      setLoading(false);
    }
  };

  const togglePeriod = (period: number) => {
    if (selectedPeriods.includes(period)) {
      if (selectedPeriods.length > 2) {
        setSelectedPeriods(selectedPeriods.filter(p => p !== period));
      }
    } else {
      setSelectedPeriods([...selectedPeriods, period].sort((a, b) => a - b));
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'strong_bullish': return 'text-green-600';
      case 'bullish': return 'text-green-500';
      case 'bearish': return 'text-red-500';
      case 'strong_bearish': return 'text-red-600';
      default: return 'text-gray-500';
    }
  };

  const getTrendLabel = (trend: string) => {
    const labels: { [key: string]: string } = {
      'strong_bullish': '强势多头',
      'bullish': '多头排列',
      'neutral': '盘整',
      'bearish': '空头排列',
      'strong_bearish': '强势空头',
    };
    return labels[trend] || trend;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold text-gray-800">多周期均线系统</h2>
        <button
          onClick={loadData}
          disabled={loading}
          className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? '加载中...' : '刷新'}
        </button>
      </div>

      {/* 周期选择 */}
      <div className="mb-4">
        <label className="text-sm text-gray-500 mb-2 block">选择均线周期：</label>
        <div className="flex flex-wrap gap-2">
          {[5, 10, 20, 30, 60, 120, 250].map(period => (
            <button
              key={period}
              onClick={() => togglePeriod(period)}
              className={`px-3 py-1 text-sm rounded ${
                selectedPeriods.includes(period)
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              MA{period}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-50 text-red-600 rounded text-sm mb-4">
          {error}
        </div>
      )}

      {data && (
        <div className="space-y-4">
          {/* 均线数值 */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
            {Object.entries(data.ma_values).map(([period, value]) => (
              <div key={period} className="p-3 bg-gray-50 rounded">
                <div className="text-xs text-gray-500">MA{period}</div>
                <div className="text-lg font-semibold text-gray-800">
                  ${value.toFixed(2)}
                </div>
              </div>
            ))}
          </div>

          {/* 趋势分析 */}
          <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg">
            <div className="flex items-center gap-4">
              <div>
                <div className="text-sm text-gray-500">总体趋势</div>
                <div className={`text-xl font-bold ${getTrendColor(data.overall_trend)}`}>
                  {getTrendLabel(data.overall_trend)}
                </div>
              </div>
              <div className="border-l pl-4">
                <div className="text-sm text-gray-500">粘合度</div>
                <div className="text-xl font-bold text-gray-800">
                  {(data.alignment_score * 100).toFixed(1)}%
                </div>
              </div>
              {data.best_cross_pair && (
                <div className="border-l pl-4">
                  <div className="text-sm text-gray-500">最佳关注组合</div>
                  <div className="text-lg font-semibold text-blue-600">
                    {data.best_cross_pair}
                  </div>
                </div>
              )}
            </div>
            <div className="mt-3 text-sm text-gray-600">
              {data.recommendation}
            </div>
          </div>

          {/* 均线组合交叉分析 */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3">均线组合交叉分析</h3>
            <div className="space-y-2">
              {Object.entries(data.pairs).map(([pairName, pair]) => {
                const hasSignal = pair.golden_cross_price !== null || pair.death_cross_price !== null;
                return (
                  <div
                    key={pairName}
                    className={`p-3 rounded border ${
                      pair.is_bullish ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{pairName}</span>
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          pair.is_bullish ? 'bg-green-200 text-green-700' : 'bg-red-200 text-red-700'
                        }`}>
                          {pair.is_bullish ? '多头' : '空头'}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600">
                        {pair.ma_short.toFixed(2)} vs {pair.ma_long.toFixed(2)}
                      </div>
                    </div>
                    
                    {hasSignal && (
                      <div className="mt-2 text-sm">
                        {pair.golden_cross_price && (
                          <div className="text-green-600">
                            金叉临界: ${pair.golden_cross_price.toFixed(2)}
                            {pair.distance_to_golden !== undefined && (
                              <span className="ml-2 text-xs">
                                (距离 {pair.distance_to_golden > 0 ? '+' : ''}{pair.distance_to_golden.toFixed(2)}%)
                              </span>
                            )}
                          </div>
                        )}
                        {pair.death_cross_price && (
                          <div className="text-red-600">
                            死叉临界: ${pair.death_cross_price.toFixed(2)}
                            {pair.distance_to_death !== undefined && (
                              <span className="ml-2 text-xs">
                                (距离 {pair.distance_to_death > 0 ? '+' : ''}{pair.distance_to_death.toFixed(2)}%)
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MultiMAMatrix;
