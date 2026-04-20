import React, { useState, useEffect, useCallback, useRef } from 'react';
import { searchSymbols, getCurrentPrice } from '../services/api';
import { StockSymbol } from '../types';

interface StockSelectorProps {
  onSelect: (symbol: string) => void;
  selectedSymbol: string;
}

// 搜索缓存
const searchCache = new Map<string, StockSymbol[]>();
const CACHE_MAX_SIZE = 100;

// 搜索历史管理
const HISTORY_KEY = 'stock_search_history';
const HISTORY_MAX_SIZE = 20;

interface SearchHistoryItem {
  symbol: string;
  name: string;
  exchange?: string;
  timestamp: number;
}

const getSearchHistory = (): SearchHistoryItem[] => {
  try {
    const stored = localStorage.getItem(HISTORY_KEY);
    if (stored) {
      const history = JSON.parse(stored);
      // 清理超过30天的记录
      const thirtyDaysAgo = Date.now() - 30 * 24 * 60 * 60 * 1000;
      return history.filter((item: SearchHistoryItem) => item.timestamp > thirtyDaysAgo);
    }
  } catch {
    // 忽略localStorage错误
  }
  return [];
};

const saveSearchHistory = (history: SearchHistoryItem[]) => {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, HISTORY_MAX_SIZE)));
  } catch {
    // 忽略localStorage错误
  }
};

const addToHistory = (stock: StockSymbol) => {
  const history = getSearchHistory();
  
  // 移除重复项
  const filtered = history.filter(item => item.symbol !== stock.symbol);
  
  // 添加到开头
  const newItem: SearchHistoryItem = {
    symbol: stock.symbol,
    name: stock.name || stock.symbol,
    exchange: stock.exchange,
    timestamp: Date.now()
  };
  
  filtered.unshift(newItem);
  
  // 保存（限制数量）
  saveSearchHistory(filtered);
};

const clearSearchHistory = () => {
  try {
    localStorage.removeItem(HISTORY_KEY);
  } catch {
    // 忽略localStorage错误
  }
};

export const StockSelector: React.FC<StockSelectorProps> = ({
  onSelect,
  selectedSymbol,
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<StockSymbol[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [currentPrice, setCurrentPrice] = useState<number | null>(null);
  const [searchTime, setSearchTime] = useState<number | null>(null);
  const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([]);
  const abortControllerRef = useRef<AbortController | null>(null);
  
  // 加载搜索历史
  useEffect(() => {
    setSearchHistory(getSearchHistory());
  }, []);
  
  // 防抖搜索
  const debouncedSearch = useCallback(async (searchQuery: string) => {
    // 空查询不搜索
    if (!searchQuery || searchQuery.trim().length === 0) {
      setResults([]);
      setIsLoading(false);
      return;
    }
    
    const trimmedQuery = searchQuery.trim();
    
    // 检查缓存
    const cacheKey = trimmedQuery.toLowerCase();
    if (searchCache.has(cacheKey)) {
      setResults(searchCache.get(cacheKey) || []);
      setIsLoading(false);
      setSearchTime(0);
      return;
    }
    
    // 取消之前的请求
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    const startTime = performance.now();
    abortControllerRef.current = new AbortController();
    
    setIsLoading(true);
    try {
      const data = await searchSymbols(trimmedQuery, abortControllerRef.current.signal);
      
      // 更新缓存
      if (searchCache.size >= CACHE_MAX_SIZE) {
        const firstKey = searchCache.keys().next().value;
        searchCache.delete(firstKey);
      }
      searchCache.set(cacheKey, data);
      
      setResults(data);
      setSearchTime(performance.now() - startTime);
      console.log(`[搜索] "${trimmedQuery}" 找到 ${data.length} 条结果`);
    } catch (e) {
      if ((e as Error).name !== 'AbortError') {
        console.error('搜索失败:', e);
        setResults([]);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  // 搜索股票 - 只在query有内容时搜索
  useEffect(() => {
    if (query.trim().length === 0) {
      setResults([]);
      return;
    }
    
    const timer = setTimeout(() => {
      debouncedSearch(query);
    }, 300);  // 300ms防抖
    
    return () => clearTimeout(timer);
  }, [query, debouncedSearch]);
  
  // 获取当前价格 - 仅在选择时获取一次，不定时更新
  // 因为 API 限流问题，暂时禁用定时更新
  // useEffect(() => {
  //   if (!selectedSymbol) return;
  //   
  //   const fetchPrice = async () => {
  //     try {
  //       const data = await getCurrentPrice(selectedSymbol);
  //       setCurrentPrice(data.price);
  //     } catch (e) {
  //       console.error('获取价格失败:', e);
  //     }
  //   };
  //   
  //   fetchPrice();
  //   const interval = setInterval(fetchPrice, 5000); // 每5秒更新
  //   
  //   return () => clearInterval(interval);
  // }, [selectedSymbol]);
  
  const handleSelect = (symbol: string, stockInfo?: StockSymbol) => {
    setQuery('');
    setResults([]);
    setShowDropdown(false);
    
    // 添加到搜索历史
    if (stockInfo) {
      addToHistory(stockInfo);
      setSearchHistory(getSearchHistory());
    }
    
    onSelect(symbol);
  };
  
  const handleClearHistory = () => {
    clearSearchHistory();
    setSearchHistory([]);
  };
  
  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-4">
      <div className="flex items-center justify-between">
        <div className="flex-1 mr-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            股票代码
          </label>
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setShowDropdown(true);
              }}
              onFocus={() => setShowDropdown(true)}
              placeholder="输入股票代码或名称..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {isLoading && (
              <div className="absolute right-3 top-2">
                <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
              </div>
            )}
            
            {/* 下拉框 */}
            {showDropdown && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-80 overflow-auto">
                {/* 搜索历史 */}
                {query.trim().length === 0 && searchHistory.length > 0 && (
                  <div className="border-b border-gray-100">
                    <div className="px-3 py-2 bg-gray-50 text-xs text-gray-500 flex justify-between items-center">
                      <span>最近查看</span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleClearHistory();
                        }}
                        className="text-xs text-red-500 hover:text-red-700"
                      >
                        清空
                      </button>
                    </div>
                    {searchHistory.map((item) => (
                      <button
                        key={item.symbol}
                        onClick={() => handleSelect(item.symbol, { 
                          symbol: item.symbol, 
                          name: item.name,
                          exchange: item.exchange 
                        })}
                        className="w-full px-4 py-2 text-left hover:bg-blue-50 focus:outline-none flex items-center justify-between"
                      >
                        <div>
                          <span className="font-semibold">{item.symbol}</span>
                          <span className="ml-2 text-gray-600">{item.name}</span>
                          {item.exchange && (
                            <span className="ml-2 text-xs text-gray-400">{item.exchange}</span>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
                
                {/* 搜索结果 */}
                {query.trim().length > 0 && results.length > 0 && (
                  <div>
                    <div className="px-3 py-1 bg-gray-50 text-xs text-gray-400 flex justify-between items-center">
                      <span>找到 {results.length} 个结果</span>
                      {searchTime !== null && searchTime < 100 && (
                        <span>⚡ {searchTime.toFixed(0)}ms</span>
                      )}
                    </div>
                    {results.map((stock) => (
                      <button
                        key={stock.symbol}
                        onClick={() => handleSelect(stock.symbol, stock)}
                        className="w-full px-4 py-2 text-left hover:bg-blue-50 focus:outline-none"
                      >
                        <span className="font-semibold">{stock.symbol}</span>
                        <span className="ml-2 text-gray-600">{stock.name}</span>
                        <span className="ml-2 text-xs text-gray-400">{stock.exchange}</span>
                      </button>
                    ))}
                  </div>
                )}
                
                {/* 搜索中 */}
                {query.trim().length > 0 && isLoading && (
                  <div className="p-4 text-center">
                    <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
                    <p className="text-xs text-gray-400 mt-2">搜索中...</p>
                  </div>
                )}
                
                {/* 无结果提示 */}
                {query.trim().length > 0 && !isLoading && results.length === 0 && (
                  <div className="p-4 text-center text-gray-500">
                    未找到匹配的股票
                  </div>
                )}
                
                {/* 空状态提示 */}
                {query.trim().length === 0 && searchHistory.length === 0 && (
                  <div className="p-4 text-center text-gray-400 text-sm">
                    输入股票代码或名称开始搜索
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
        
        {/* 当前选中的股票 */}
        <div className="text-right">
          <div className="text-sm text-gray-500">当前选中</div>
          <div className="text-2xl font-bold text-gray-900">{selectedSymbol}</div>
        </div>
        
        {/* 当前价格 */}
        <div className="ml-6 text-right">
          <div className="text-sm text-gray-500">当前价格</div>
          <div className="text-2xl font-bold text-blue-600">
            {currentPrice ? `$${currentPrice.toFixed(2)}` : '-.--'}
          </div>
        </div>
      </div>
      
      {/* 点击外部关闭下拉框 */}
      {showDropdown && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setShowDropdown(false)}
        ></div>
      )}
    </div>
  );
};

export default StockSelector;
