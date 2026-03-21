import React, { useState, useEffect, useCallback } from 'react';
import StockSelector from './components/StockSelector';
import TriggerMatrix from './components/TriggerMatrix';
import ResonanceZone from './components/ResonanceZone';
import SimpleStrategyPanel from './components/SimpleStrategyPanel';
import { calculateTriggerMatrixAuto } from './services/api';
import { TriggerMatrixResponse } from './types';

function App() {
  const [selectedSymbol, setSelectedSymbol] = useState<string>('600519.SH');
  const [matrix, setMatrix] = useState<TriggerMatrixResponse | null>(null);
  const [currentPrice, setCurrentPrice] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(false);
  
  // 加载矩阵数据
  const loadMatrix = useCallback(async () => {
    if (!selectedSymbol) return;
    
    setIsLoading(true);
    try {
      const data = await calculateTriggerMatrixAuto(selectedSymbol);
      setMatrix(data);
      setCurrentPrice(data.current_price);
    } catch (e) {
      console.error('加载矩阵失败:', e);
    } finally {
      setIsLoading(false);
    }
  }, [selectedSymbol]);
  
  // 选择股票时重新加载
  useEffect(() => {
    loadMatrix();
  }, [selectedSymbol, loadMatrix]);
  
  // 定时刷新矩阵（每30秒）
  useEffect(() => {
    const interval = setInterval(() => {
      if (selectedSymbol) {
        loadMatrix();
      }
    }, 30000);
    
    return () => clearInterval(interval);
  }, [selectedSymbol, loadMatrix]);
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-xl">
                Ξ
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">技术指标前置预判工具</h1>
                <p className="text-sm text-gray-500">反向求解临界价格，提前布局交易机会</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {/* 刷新按钮 */}
              <button
                onClick={loadMatrix}
                disabled={isLoading}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 text-sm"
              >
                {isLoading ? '加载中...' : '刷新数据'}
              </button>
            </div>
          </div>
        </div>
      </header>
      
      {/* 主要内容 */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左侧：股票选择和触发矩阵 */}
          <div className="lg:col-span-2 space-y-6">
            <StockSelector
              selectedSymbol={selectedSymbol}
              onSelect={setSelectedSymbol}
            />
            
            <TriggerMatrix matrix={matrix} isLoading={isLoading} />
            
            {/* 共振区间 */}
            {matrix && (
              <ResonanceZone
                zones={matrix.resonance}
                currentPrice={matrix.current_price}
              />
            )}
          </div>
          
          {/* 右侧：个人策略配置 */}
          <div className="space-y-6">
            {selectedSymbol && (
              <SimpleStrategyPanel symbol={selectedSymbol} />
            )}
          </div>
        </div>
      </main>
      
      {/* 底部说明 */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="text-center text-sm text-gray-500">
            <p className="mb-2">
              <strong>使用说明：</strong>
              本工具通过反向数学推导计算技术指标临界价格，帮助您在信号触发前做出交易决策。
            </p>
            <p>
              数据仅供参考，投资有风险，交易需谨慎。
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
