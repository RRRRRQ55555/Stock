import React, { useState } from 'react';
import { StressTestRequest, StressTestResponse } from '../types';
import { stressTest } from '../services/api';

interface StressTesterProps {
  symbol: string;
  currentPrice: number;
  macdState: any;
  maState: any;
  kdjState: any;
}

export const StressTester: React.FC<StressTesterProps> = ({
  symbol,
  currentPrice,
  macdState,
  maState,
  kdjState,
}) => {
  const [hypotheticalPrice, setHypotheticalPrice] = useState<number>(currentPrice);
  const [result, setResult] = useState<StressTestResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const runStressTest = async () => {
    if (!macdState || !maState || !kdjState) return;
    
    setIsLoading(true);
    try {
      const request: StressTestRequest = {
        symbol,
        hypothetical_price: hypotheticalPrice,
        macd: macdState,
        ma: maState,
        kdj: kdjState,
      };
      
      const response = await stressTest(request);
      setResult(response);
    } catch (e) {
      console.error('压力测试失败:', e);
    } finally {
      setIsLoading(false);
    }
  };
  
  // 快速调整价格
  const adjustPrice = (percentage: number) => {
    const newPrice = currentPrice * (1 + percentage / 100);
    setHypotheticalPrice(Number(newPrice.toFixed(2)));
  };
  
  // 获取信号强度颜色
  const getSignalColor = (bullish: number, bearish: number) => {
    if (bullish > bearish) return 'text-green-600';
    if (bearish > bullish) return 'text-red-600';
    return 'text-gray-600';
  };
  
  return (
    <div className="card">
      <div className="card-header">压力测试模拟器</div>
      
      {/* 价格输入 */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          假设价格
        </label>
        <div className="flex items-center gap-4">
          <input
            type="number"
            value={hypotheticalPrice}
            onChange={(e) => setHypotheticalPrice(Number(e.target.value))}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            step="0.01"
          />
          <button
            onClick={runStressTest}
            disabled={isLoading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? '计算中...' : '模拟'}
          </button>
        </div>
        
        {/* 快速调整按钮 */}
        <div className="flex gap-2 mt-3">
          {[-10, -5, -2, -1, 0, 1, 2, 5, 10].map((pct) => (
            <button
              key={pct}
              onClick={() => adjustPrice(pct)}
              className={`px-3 py-1 text-sm rounded ${
                pct === 0
                  ? 'bg-gray-200 text-gray-700'
                  : pct > 0
                  ? 'bg-green-100 text-green-700 hover:bg-green-200'
                  : 'bg-red-100 text-red-700 hover:bg-red-200'
              }`}
            >
              {pct > 0 ? '+' : ''}{pct}%
            </button>
          ))}
        </div>
        
        {/* 当前价格对比 */}
        <div className="mt-2 text-sm text-gray-500">
          当前价格: ${currentPrice.toFixed(2)} |
          差额: {((hypotheticalPrice - currentPrice) / currentPrice * 100).toFixed(2)}%
        </div>
      </div>
      
      {/* 模拟结果 */}
      {result && (
        <div className="border-t pt-4">
          <div className="flex items-center justify-between mb-4 p-3 bg-gray-50 rounded-lg">
            <div>
              <div className="text-sm text-gray-500">综合判断</div>
              <div className={`text-xl font-bold ${getSignalColor(
                result.summary.bullish_signals,
                result.summary.bearish_signals
              )}`}>
                {result.summary.overall === 'bullish' && '看涨信号占优'}
                {result.summary.overall === 'bearish' && '看跌信号占优'}
                {result.summary.overall === 'neutral' && '信号平衡'}
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-4 text-sm">
                <span className="text-green-600">
                  看涨: {result.summary.bullish_signals}个信号
                </span>
                <span className="text-red-600">
                  看跌: {result.summary.bearish_signals}个信号
                </span>
              </div>
            </div>
          </div>
          
          {/* MACD 结果 */}
          <div className="mb-4 p-3 bg-purple-50 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="font-semibold text-purple-900">MACD</span>
              <span className={`text-sm ${
                result.macd.is_golden_cross ? 'text-green-600' : 
                result.macd.is_death_cross ? 'text-red-600' : 'text-gray-600'
              }`}>
                {result.macd.is_golden_cross ? '✓ 金叉' : 
                 result.macd.is_death_cross ? '✗ 死叉' : '— 维持'}
              </span>
            </div>
            <div className="text-sm text-gray-600 grid grid-cols-3 gap-2">
              <span>DIF: {result.macd.dif.toFixed(4)}</span>
              <span>Signal: {result.macd.signal.toFixed(4)}</span>
              <span>Hist: {result.macd.histogram.toFixed(4)}</span>
            </div>
          </div>
          
          {/* 均线结果 */}
          <div className="mb-4 p-3 bg-blue-50 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="font-semibold text-blue-900">均线</span>
              <span className={`text-sm ${
                result.ma.is_golden_cross ? 'text-green-600' : 
                result.ma.is_death_cross ? 'text-red-600' : 'text-gray-600'
              }`}>
                {result.ma.is_golden_cross ? '✓ 多头排列' : 
                 result.ma.is_death_cross ? '✗ 空头排列' : '— 均线粘合'}
              </span>
            </div>
            <div className="text-sm text-gray-600 grid grid-cols-2 gap-2">
              <span>MA短期: {result.ma.ma_short.toFixed(2)}</span>
              <span>MA长期: {result.ma.ma_long.toFixed(2)}</span>
            </div>
          </div>
          
          {/* KDJ 结果 */}
          <div className="p-3 bg-yellow-50 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="font-semibold text-yellow-900">KDJ</span>
              <span className={`text-sm ${
                result.kdj.zone === 'oversold' ? 'text-blue-600' : 
                result.kdj.zone === 'overbought' ? 'text-orange-600' : 'text-gray-600'
              }`}>
                {result.kdj.zone === 'oversold' ? '⬇ 超卖区' : 
                 result.kdj.zone === 'overbought' ? '⬆ 超买区' : '— 震荡区'}
              </span>
            </div>
            <div className="text-sm text-gray-600 grid grid-cols-3 gap-2">
              <span>K: {result.kdj.k.toFixed(2)}</span>
              <span>D: {result.kdj.d.toFixed(2)}</span>
              <span>J: {result.kdj.j.toFixed(2)}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StressTester;
