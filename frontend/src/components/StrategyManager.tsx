/**
 * 交易策略管理组件
 * 
 * 帮助用户维持交易策略：
 * 1. 创建策略（入场条件 + 止损条件）
 * 2. 每日检查策略可行性
 * 3. 显示今日可入场区间和止损价格
 */

import React, { useState, useEffect } from 'react';
import { 
  getStrategies, 
  createStrategy, 
  checkStrategy, 
  checkAllStrategies,
  getStrategyTemplates,
  executeEntry,
  deleteStrategy
} from '../services/api';

interface Strategy {
  id: string;
  name: string;
  symbol: string;
  status: string;
  entry_description: string;
  stop_loss_description: string;
  take_profit_description?: string;
  entry_price?: number;
  entry_date?: string;
  stop_loss_price?: number;
  notes: string;
  created_at: string;
}

interface StrategyCheck {
  strategy_id: string;
  symbol: string;
  current_price: number;
  can_enter_today: boolean;
  entry_price_min?: number;
  entry_price_max?: number;
  entry_confidence: number;
  entry_distance_pct?: number;
  stop_loss_price?: number;
  stop_loss_distance_pct?: number;
  take_profit_price?: number;
  take_profit_distance_pct?: number;
  recommendation: string;
  risk_reward_ratio?: number;
}

interface StrategyTemplate {
  name: string;
  description: string;
  entry_conditions: any[];
  stop_loss_conditions: any[];
  tags: string[];
}

export const StrategyManager: React.FC = () => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [templates, setTemplates] = useState<StrategyTemplate[]>([]);
  const [checkResults, setCheckResults] = useState<{[key: string]: StrategyCheck}>({});
  const [loading, setLoading] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [bulkCheckResult, setBulkCheckResult] = useState<any>(null);
  
  // 表单状态
  const [formData, setFormData] = useState({
    name: '',
    symbol: '',
    stop_loss_pct: -5,
    take_profit_pct: 10,
    notes: ''
  });

  useEffect(() => {
    loadStrategies();
    loadTemplates();
  }, []);

  const loadStrategies = async () => {
    try {
      const data = await getStrategies();
      setStrategies(data.strategies);
    } catch (e) {
      console.error('加载策略失败:', e);
    }
  };

  const loadTemplates = async () => {
    try {
      const data = await getStrategyTemplates();
      setTemplates(data.templates);
    } catch (e) {
      console.error('加载模板失败:', e);
    }
  };

  const handleCheckStrategy = async (strategyId: string) => {
    try {
      const result = await checkStrategy(strategyId);
      setCheckResults({ ...checkResults, [strategyId]: result });
    } catch (e) {
      console.error('检查策略失败:', e);
    }
  };

  const handleCheckAll = async () => {
    setLoading(true);
    try {
      const result = await checkAllStrategies();
      setBulkCheckResult(result);
      
      // 更新单个策略的检查结果
      const newResults = { ...checkResults };
      result.all_results.forEach((r: any) => {
        if (r.strategy_id && !r.error) {
          newResults[r.strategy_id] = r;
        }
      });
      setCheckResults(newResults);
    } catch (e) {
      console.error('批量检查失败:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateStrategy = async () => {
    if (!formData.name || !formData.symbol) {
      alert('请填写策略名称和股票代码');
      return;
    }

    try {
      const request: any = {
        name: formData.name,
        symbol: formData.symbol,
        entry_conditions: [],
        stop_loss: {
          conditions: [],
          fixed_pct: formData.stop_loss_pct
        },
        notes: formData.notes
      };

      if (formData.take_profit_pct) {
        request.take_profit = {
          conditions: [],
          fixed_pct: formData.take_profit_pct
        };
      }

      // 如果使用模板
      if (selectedTemplate) {
        request.use_template = selectedTemplate;
      }

      await createStrategy(request);
      setShowCreate(false);
      setFormData({ name: '', symbol: '', stop_loss_pct: -5, take_profit_pct: 10, notes: '' });
      setSelectedTemplate('');
      loadStrategies();
    } catch (e) {
      console.error('创建策略失败:', e);
      alert('创建策略失败');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('确定要删除这个策略吗？')) return;
    
    try {
      await deleteStrategy(id);
      loadStrategies();
    } catch (e) {
      console.error('删除失败:', e);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: {[key: string]: string} = {
      'pending': 'bg-yellow-100 text-yellow-800',
      'entry_ready': 'bg-green-100 text-green-800',
      'entered': 'bg-blue-100 text-blue-800',
      'stop_loss': 'bg-red-100 text-red-800',
      'take_profit': 'bg-purple-100 text-purple-800',
      'expired': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusLabel = (status: string) => {
    const labels: {[key: string]: string} = {
      'pending': '等待入场',
      'entry_ready': '今日可入场',
      'entered': '已入场',
      'stop_loss': '已止损',
      'take_profit': '已止盈',
      'expired': '已过期'
    };
    return labels[status] || status;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">交易策略管理</h2>
        <div className="flex gap-2">
          <button
            onClick={handleCheckAll}
            disabled={loading}
            className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          >
            {loading ? '检查中...' : '今日策略检查'}
          </button>
          <button
            onClick={() => setShowCreate(true)}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            创建策略
          </button>
        </div>
      </div>

      {/* 批量检查结果摘要 */}
      {bulkCheckResult && (
        <div className="mb-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg">
          <div className="flex items-center gap-4">
            <div>
              <div className="text-sm text-gray-500">总策略数</div>
              <div className="text-2xl font-bold">{bulkCheckResult.total}</div>
            </div>
            <div className="border-l pl-4">
              <div className="text-sm text-green-600">今日可入场</div>
              <div className="text-2xl font-bold text-green-600">{bulkCheckResult.can_enter_today}</div>
            </div>
            <div className="border-l pl-4">
              <div className="text-sm text-blue-600">持仓监控中</div>
              <div className="text-2xl font-bold text-blue-600">{bulkCheckResult.already_entered}</div>
            </div>
          </div>
          
          {/* 今日机会 */}
          {bulkCheckResult.opportunities && bulkCheckResult.opportunities.length > 0 && (
            <div className="mt-3 pt-3 border-t">
              <div className="text-sm font-medium text-green-700 mb-2">今日交易机会：</div>
              <div className="space-y-1">
                {bulkCheckResult.opportunities.map((opp: any) => (
                  <div key={opp.strategy_id} className="flex items-center gap-2 text-sm">
                    <span className="font-medium">{opp.name}</span>
                    <span className="text-gray-500">({opp.symbol})</span>
                    {opp.entry_range && (
                      <span className="text-green-600">
                        入场区间: ${opp.entry_range.min?.toFixed(2)} - ${opp.entry_range.max?.toFixed(2)}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 策略列表 */}
      <div className="space-y-3">
        {strategies.length === 0 ? (
          <p className="text-gray-500 text-center py-8">暂无策略，点击"创建策略"开始</p>
        ) : (
          strategies.map((strategy) => {
            const checkResult = checkResults[strategy.id];
            return (
              <div key={strategy.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-bold text-lg">{strategy.name}</span>
                      <span className={`px-2 py-0.5 text-xs rounded ${getStatusColor(strategy.status)}`}>
                        {getStatusLabel(strategy.status)}
                      </span>
                      {checkResult?.can_enter_today && (
                        <span className="px-2 py-0.5 text-xs rounded bg-green-100 text-green-700">
                          今日可入场
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-600 mb-2">
                      {strategy.symbol} · 创建于 {new Date(strategy.created_at).toLocaleDateString()}
                    </div>
                    
                    <div className="text-sm space-y-1">
                      <div><span className="text-gray-500">入场：</span>{strategy.entry_description}</div>
                      <div><span className="text-gray-500">止损：</span>{strategy.stop_loss_description}</div>
                      {strategy.take_profit_description && (
                        <div><span className="text-gray-500">止盈：</span>{strategy.take_profit_description}</div>
                      )}
                    </div>

                    {/* 检查结果 */}
                    {checkResult && (
                      <div className="mt-3 p-3 bg-gray-50 rounded">
                        <div className="text-sm font-medium mb-2">今日分析（当前价: ${checkResult.current_price.toFixed(2)}）</div>
                        
                        {checkResult.can_enter_today && checkResult.entry_price_min && checkResult.entry_price_max && (
                          <div className="mb-2">
                            <span className="text-green-600 font-medium">
                              可入场区间: ${checkResult.entry_price_min.toFixed(2)} - ${checkResult.entry_price_max.toFixed(2)}
                            </span>
                            <span className="text-xs text-gray-500 ml-2">
                              (置信度: {(checkResult.entry_confidence * 100).toFixed(0)}%)
                            </span>
                          </div>
                        )}
                        
                        {checkResult.stop_loss_price && (
                          <div className="mb-2">
                            <span className="text-red-600">
                              止损价格: ${checkResult.stop_loss_price.toFixed(2)}
                            </span>
                            {checkResult.stop_loss_distance_pct && (
                              <span className="text-xs text-gray-500 ml-2">
                                (距离 {(checkResult.stop_loss_distance_pct > 0 ? '+' : '')}{checkResult.stop_loss_distance_pct.toFixed(2)}%)
                              </span>
                            )}
                          </div>
                        )}
                        
                        {checkResult.take_profit_price && (
                          <div className="mb-2">
                            <span className="text-purple-600">
                              止盈目标: ${checkResult.take_profit_price.toFixed(2)}
                            </span>
                          </div>
                        )}
                        
                        {checkResult.risk_reward_ratio && (
                          <div className="text-sm">
                            <span className="text-gray-500">盈亏比: </span>
                            <span className={checkResult.risk_reward_ratio >= 2 ? 'text-green-600 font-medium' : 'text-yellow-600'}>
                              {checkResult.risk_reward_ratio.toFixed(1)}:1
                              {checkResult.risk_reward_ratio >= 2 ? ' (优秀)' : checkResult.risk_reward_ratio >= 1.5 ? ' (良好)' : ' (一般)'}
                            </span>
                          </div>
                        )}
                        
                        <div className="mt-2 text-sm text-gray-700">
                          <span className="font-medium">建议：</span>{checkResult.recommendation}
                        </div>
                      </div>
                    )}

                    {strategy.notes && (
                      <div className="mt-2 text-sm text-gray-500 italic">
                        备注: {strategy.notes}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex flex-col gap-2 ml-4">
                    <button
                      onClick={() => handleCheckStrategy(strategy.id)}
                      className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                    >
                      检查策略
                    </button>
                    
                    {strategy.status === 'pending' && checkResult?.can_enter_today && (
                      <button
                        onClick={() => {
                          const price = prompt('请输入入场价格:', checkResult.entry_price_max?.toFixed(2) || '');
                          if (price) {
                            executeEntry(strategy.id, parseFloat(price)).then(() => {
                              loadStrategies();
                            });
                          }
                        }}
                        className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
                      >
                        执行入场
                      </button>
                    )}
                    
                    <button
                      onClick={() => handleDelete(strategy.id)}
                      className="px-3 py-1 text-xs text-red-600 hover:text-red-800"
                    >
                      删除
                    </button>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* 创建策略弹窗 */}
      {showCreate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg max-h-[90vh] overflow-auto">
            <h3 className="text-lg font-bold mb-4">创建交易策略</h3>
            
            <div className="space-y-4">
              {/* 模板选择 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  使用模板（可选）
                </label>
                <select
                  value={selectedTemplate}
                  onChange={(e) => setSelectedTemplate(e.target.value)}
                  className="w-full px-3 py-2 border rounded"
                >
                  <option value="">自定义策略</option>
                  {templates.map((t) => (
                    <option key={t.name} value={t.name}>
                      {t.name} - {t.description.substring(0, 30)}...
                    </option>
                  ))}
                </select>
                {selectedTemplate && (
                  <p className="text-xs text-gray-500 mt-1">
                    {templates.find(t => t.name === selectedTemplate)?.description}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  策略名称 *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border rounded"
                  placeholder="例如：茅台均线策略"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  股票代码 *
                </label>
                <input
                  type="text"
                  value={formData.symbol}
                  onChange={(e) => setFormData({ ...formData, symbol: e.target.value })}
                  className="w-full px-3 py-2 border rounded"
                  placeholder="例如：600519.SH 或 AAPL"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    止损百分比 (%)
                  </label>
                  <input
                    type="number"
                    value={formData.stop_loss_pct}
                    onChange={(e) => setFormData({ ...formData, stop_loss_pct: parseFloat(e.target.value) })}
                    className="w-full px-3 py-2 border rounded"
                  />
                  <p className="text-xs text-gray-500">例如：-5 表示跌5%止损</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    止盈百分比 (%)
                  </label>
                  <input
                    type="number"
                    value={formData.take_profit_pct}
                    onChange={(e) => setFormData({ ...formData, take_profit_pct: parseFloat(e.target.value) })}
                    className="w-full px-3 py-2 border rounded"
                  />
                  <p className="text-xs text-gray-500">例如：10 表示涨10%止盈</p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  备注
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="w-full px-3 py-2 border rounded"
                  rows={3}
                  placeholder="策略说明、交易计划等..."
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-6">
              <button
                onClick={() => setShowCreate(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                取消
              </button>
              <button
                onClick={handleCreateStrategy}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                创建策略
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StrategyManager;
