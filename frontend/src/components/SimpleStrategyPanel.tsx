import React, { useState, useEffect } from 'react';
const OPTIONS = [
  { id: 'macd_golden', name: 'MACD金叉', type: 'buy' },
  { id: 'macd_death', name: 'MACD死叉', type: 'sell' },
  { id: 'ma_above', name: '股价上穿均线', type: 'buy' },
  { id: 'ma_below', name: '股价下穿均线', type: 'sell' },
];
export const SimpleStrategyPanel = ({ symbol }: { symbol: string }) => {
  const [activeTab, setActiveTab] = useState<'buy' | 'sell'>('buy');
  const [selected, setSelected] = useState<Set<string>>(new Set());
  useEffect(() => {
    const saved = localStorage.getItem('strategy');
    if (saved) {
      const parsed = JSON.parse(saved);
      setSelected(new Set(parsed.selected || []));
      setActiveTab(parsed.activeTab || 'buy');
    }
  }, []);
  const toggle = (id: string) => {
    setSelected(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };
  const filtered = OPTIONS.filter(o => o.type === activeTab);
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-lg font-bold mb-4">策略配置</h2>
      <div className="flex border-b mb-4">
        <button onClick={() => setActiveTab('buy')} className={`flex-1 py-2 ${activeTab === 'buy' ? 'text-red-600 border-b-2 border-red-600' : 'text-gray-500'}`}>买入</button>
        <button onClick={() => setActiveTab('sell')} className={`flex-1 py-2 ${activeTab === 'sell' ? 'text-green-600 border-b-2 border-green-600' : 'text-gray-500'}`}>卖出</button>
      </div>
      <div className="space-y-2">
        {filtered.map(opt => (
          <div key={opt.id} onClick={() => toggle(opt.id)} className={`p-3 border rounded cursor-pointer ${selected.has(opt.id) ? 'bg-blue-50 border-blue-300' : 'bg-white'}`}>
            <div className="flex items-center">
              <input type="checkbox" checked={selected.has(opt.id)} onChange={() => {}} className="mr-3 h-4 w-4" />
              <span className="font-medium text-sm">{opt.name}</span>
            </div>
          </div>
        ))}
      </div>
      {selected.size > 0 && <div className="mt-4 p-2 bg-blue-50 rounded text-sm">已选择 {selected.size} 个条件</div>}
      {!symbol && <div className="mt-4 text-center text-gray-400 text-sm">请先选择股票</div>}
    </div>
  );
};
export default SimpleStrategyPanel;