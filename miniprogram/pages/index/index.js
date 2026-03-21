// 首页逻辑
const api = require('../../utils/api');
const storage = require('../../utils/storage');
const websocket = require('../../utils/websocket');
const config = require('../../config');

// 获取应用实例
const app = getApp();

Page({
  data: {
    // 搜索相关
    searchQuery: '',
    searchSuggestions: [],
    searchHistory: [],

    // 热门股票快捷入口
    hotStocks: [
      { symbol: '000001.SZ', name: '平安银行' },
      { symbol: '600519.SS', name: '贵州茅台' },
      { symbol: '000858.SZ', name: '五粮液' },
      { symbol: '300750.SZ', name: '宁德时代' },
      { symbol: '002594.SZ', name: '比亚迪' },
      { symbol: '000333.SZ', name: '美的集团' }
    ],

    // 股票信息
    currentSymbol: '',
    currentStockName: '',
    currentPrice: {},
    updateTime: '',

    // 矩阵数据
    matrixData: null,

    // 状态
    loading: false,
    refreshing: false,
    autoRefreshTimer: null,

    // 状态样式
    macdStatusClass: 'neutral',
    macdStatusText: '计算中...',
    maStatusClass: 'neutral',
    maStatusText: '计算中...',
    kdjStatusClass: 'neutral',
    kdjStatusText: '计算中...',

    // 策略匹配结果
    strategySettings: null,

    // 策略看板数据 - 基于用户策略的匹配结果
    buyMatched: null,         // true=可买, false=观望, null=未设置
    buyMatchDetails: null,    // 详细匹配信息
    stopLossTriggered: false, // true=止损, false=持有
    stopLossDetails: null,      // 详细止损信息
    resonanceAlert: '',       // 共振预警文字
    dashboardExpanded: false  // 看板是否展开
  },

  onLoad(options) {
    console.log('首页加载 - 空状态版本');
    
    // 加载搜索历史
    this.loadSearchHistory();
    
    // 默认不加载任何股票
    this.setData({
      currentSymbol: '',
      currentStockName: '',
      matrixData: null,
      currentPrice: {},
      updateTime: ''
    });
    
    // 连接 WebSocket
    this.connectWebSocket();
  },

  onShow() {
    console.log('首页显示');
    // 重新连接 WebSocket（如果断开）
    if (!websocket.getStatus().isConnected) {
      this.connectWebSocket();
    }
  },

  onHide() {
    console.log('首页隐藏');
    // 页面隐藏时保持 WebSocket 连接，但降低刷新频率
  },

  onUnload() {
    console.log('首页卸载');
    // 清理定时器
    this.stopAutoRefresh();
    
    // 取消 WebSocket 订阅
    if (this.data.currentSymbol) {
      websocket.unsubscribe([this.data.currentSymbol]);
    }
  },

  // 下拉刷新
  onPullDownRefresh() {
    console.log('下拉刷新');
    this.setData({ refreshing: true });
    this.loadData().finally(() => {
      this.setData({ refreshing: false });
      wx.stopPullDownRefresh();
    });
  },

  // ==================== 数据加载 ====================

  async loadData() {
    const { currentSymbol } = this.data;
    if (!currentSymbol) return;

    this.setData({ loading: true });

    try {
      // 先获取矩阵数据（包含价格和名称）
      const matrixResult = await this.loadMatrixData(currentSymbol);
      // 再获取当前价格
      const priceResult = await this.loadCurrentPrice(currentSymbol);

      // 数据加载完成后，计算策略看板
      const { matrixData: md, currentPrice: cp } = this.data;
      if (md && cp && cp.price) {
        await this.calculateDashboardMetrics(md, cp.price);
      }

      // 更新更新时间
      this.setData({
        updateTime: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      });

      // 订阅 WebSocket
      websocket.subscribe([currentSymbol]);

      // 保存到全局
      app.setCurrentSymbol(currentSymbol);
      storage.setUserPref('last_symbol', currentSymbol);

    } catch (error) {
      console.error('加载数据失败:', error);
      wx.showToast({
        title: '连接失败，请检查网络配置',
        icon: 'none',
        duration: 3000
      });
    } finally {
      this.setData({ loading: false });
    }
  },

  async loadCurrentPrice(symbol) {
    try {
      const result = await api.getCurrentPrice(symbol);

      let currentPrice = null;
      if (result && result.price !== undefined) {
        currentPrice = {
          price: result.price,
          change: result.change || 0,
          changePercent: result.change_percent || 0
        };

        // 如果API返回了名称，更新股票名称
        if (result.name && !this.data.currentStockName) {
          this.setData({ currentStockName: result.name });
        }
      } else if (result && result.data) {
        const data = result.data;
        currentPrice = {
          price: data.price || data.close || 0,
          change: data.change || 0,
          changePercent: data.change_percent || 0
        };
      }

      if (currentPrice && currentPrice.price) {
        this.setData({ currentPrice });
      }
      return currentPrice;
    } catch (error) {
      console.error('获取当前价格失败:', error);
      return null;
    }
  },

  async loadMatrixData(symbol) {
    try {
      const result = await api.calculateMatrix(symbol);

      if (result) {
        // 预处理数据，添加显示用的字符串
        const processedResult = this.processMatrixData(result);

        // 获取股票名称（优先使用API返回的name）
        const stockName = result.name || result.symbol || symbol;

        this.setData({
          matrixData: processedResult,
          currentStockName: stockName
        });

        // 如果当前价格为空，使用矩阵中的价格
        if (!this.data.currentPrice || !this.data.currentPrice.price) {
          if (result.current_price) {
            this.setData({
              currentPrice: {
                price: result.current_price,
                change: 0,
                changePercent: 0
              }
            });
          }
        }

        // 更新指标状态
        this.updateIndicatorStatus(result);
      }

      return result;
    } catch (error) {
      console.error('获取矩阵数据失败:', error);
      return null;
    }
  },

  // 预处理矩阵数据，添加显示用的字符串
  processMatrixData(data) {
    const result = { ...data };
    const currentPrice = result.current_price || 0;

    // 处理 KDJ 数据
    if (result.kdj) {
      const kdj = result.kdj;
      
      // 格式化价格字符串
      kdj.oversold_price_str = kdj.oversold_price ? kdj.oversold_price.toFixed(2) : '--';
      kdj.overbought_price_str = kdj.overbought_price ? kdj.overbought_price.toFixed(2) : '--';
      
      // 计算超卖状态
      if (kdj.oversold_price && currentPrice > 0) {
        const isOversold = currentPrice <= kdj.oversold_price;
        kdj.oversold_class = isOversold ? 'text-success' : 'text-stock-down';
        
        if (isOversold) {
          kdj.oversold_text = '已超卖';
        } else {
          const distance = ((currentPrice - kdj.oversold_price) / currentPrice * 100).toFixed(2);
          kdj.oversold_text = `需跌 ${distance}%`;
        }
      }
      
      // 计算超买状态
      if (kdj.overbought_price && currentPrice > 0) {
        const isOverbought = currentPrice >= kdj.overbought_price;
        kdj.overbought_class = isOverbought ? 'text-error' : 'text-stock-up';
        
        if (isOverbought) {
          kdj.overbought_text = '已超买';
        } else {
          const distance = ((kdj.overbought_price - currentPrice) / currentPrice * 100).toFixed(2);
          kdj.overbought_text = `需涨 ${distance}%`;
        }
      }
      
      // 格式化 K/D/J 值
      kdj.k_str = kdj.k ? kdj.k.toFixed(2) : '--';
      kdj.d_str = kdj.d ? kdj.d.toFixed(2) : '--';
      kdj.j_str = kdj.j ? kdj.j.toFixed(2) : '--';
    }
    
    // 处理 MACD 数据 - 添加字符串格式
    if (result.macd) {
      result.macd.dif_str = result.macd.dif ? result.macd.dif.toFixed(4) : '--';
      result.macd.signal_str = result.macd.signal ? result.macd.signal.toFixed(4) : '--';
      result.macd.golden_cross_price_str = result.macd.golden_cross_price ? result.macd.golden_cross_price.toFixed(2) : '--';
      result.macd.death_cross_price_str = result.macd.death_cross_price ? result.macd.death_cross_price.toFixed(2) : '--';
      result.macd.distance_to_golden_str = result.macd.distance_to_golden ? Math.abs(result.macd.distance_to_golden).toFixed(2) : '--';
      result.macd.distance_to_death_str = result.macd.distance_to_death ? Math.abs(result.macd.distance_to_death).toFixed(2) : '--';
      
      // 金叉文本和样式
      if (result.macd.distance_to_golden !== undefined && result.macd.distance_to_golden !== null) {
        result.macd.golden_class = result.macd.distance_to_golden >= 0 ? 'text-stock-up' : 'text-stock-down';
        result.macd.golden_text = result.macd.distance_to_golden >= 0 ? '需涨' : '需跌';
      }
      
      // 死叉文本和样式
      if (result.macd.distance_to_death !== undefined && result.macd.distance_to_death !== null) {
        result.macd.death_class = result.macd.distance_to_death <= 0 ? 'text-stock-up' : 'text-stock-down';
        result.macd.death_text = result.macd.distance_to_death <= 0 ? '需涨' : '需跌';
      }
    }
    
    // 处理均线数据 - 添加字符串格式
    if (result.ma) {
      result.ma.ma_short_str = result.ma.ma_short ? result.ma.ma_short.toFixed(2) : '--';
      result.ma.ma_long_str = result.ma.ma_long ? result.ma.ma_long.toFixed(2) : '--';
      result.ma.golden_cross_price_str = result.ma.golden_cross_price ? result.ma.golden_cross_price.toFixed(2) : '--';
      result.ma.death_cross_price_str = result.ma.death_cross_price ? result.ma.death_cross_price.toFixed(2) : '--';
      result.ma.distance_to_golden_str = result.ma.distance_to_golden ? Math.abs(result.ma.distance_to_golden).toFixed(2) : '--';
      result.ma.distance_to_death_str = result.ma.distance_to_death ? Math.abs(result.ma.distance_to_death).toFixed(2) : '--';
      
      // 金叉文本和样式
      if (result.ma.distance_to_golden !== undefined && result.ma.distance_to_golden !== null) {
        result.ma.golden_class = result.ma.distance_to_golden >= 0 ? 'text-stock-up' : 'text-stock-down';
        result.ma.golden_text = result.ma.distance_to_golden >= 0 ? '需涨' : '需跌';
      }
      
      // 死叉文本和样式
      if (result.ma.distance_to_death !== undefined && result.ma.distance_to_death !== null) {
        result.ma.death_class = result.ma.distance_to_death <= 0 ? 'text-stock-up' : 'text-stock-down';
        result.ma.death_text = result.ma.distance_to_death <= 0 ? '需涨' : '需跌';
      }
    }
    
    // 处理共振数据 - 添加字符串格式
    if (result.resonance && Array.isArray(result.resonance)) {
      result.resonance = result.resonance.map(item => {
        const newItem = {
          ...item,
          price_min_str: item.price_min ? item.price_min.toFixed(2) : '--',
          price_max_str: item.price_max ? item.price_max.toFixed(2) : '--',
          price_center_str: item.price_center ? item.price_center.toFixed(2) : '--',
          confidence_str: item.confidence ? (item.confidence * 100).toFixed(0) : '--',
          type_class: item.type === 'resonance' ? 'tag-success' : 'tag-warning',
          type_text: item.type === 'resonance' ? '强共振' : '弱共振'
        };
        
        // 计算距离文本
        if (currentPrice > 0 && item.price_min !== undefined && item.price_max !== undefined) {
          const inRange = currentPrice >= item.price_min && currentPrice <= item.price_max;
          
          if (inRange) {
            newItem.distance_class = 'text-success';
            newItem.distance_text = '当前价格在共振区间内';
          } else {
            newItem.distance_class = 'text-warning';
            if (currentPrice < item.price_min) {
              const distance = ((item.price_min - currentPrice) / currentPrice * 100).toFixed(2);
              newItem.distance_text = `当前价格距离区间需涨 ${distance}%`;
            } else {
              const distance = ((currentPrice - item.price_max) / currentPrice * 100).toFixed(2);
              newItem.distance_text = `当前价格距离区间需跌 ${distance}%`;
            }
          }
        }
        
        return newItem;
      });
    }
    
    return result;
  },

  // ==================== 搜索功能 ====================

  loadSearchHistory() {
    const history = storage.getSearchHistory();
    this.setData({ searchHistory: history.slice(0, 10) }); // 只显示前10条
  },

  onSearchInput(e) {
    const query = e.detail.value;
    this.setData({ searchQuery: query });

    // 如果输入为空，清空建议
    if (!query.trim()) {
      this.setData({ searchSuggestions: [] });
      return;
    }

    // 防抖搜索
    clearTimeout(this.searchTimer);
    this.searchTimer = setTimeout(() => {
      this.searchSymbols(query);
    }, 300);
  },

  async searchSymbols(query) {
    if (!query.trim()) return;

    try {
      const results = await api.searchSymbols(query);
      
      if (results && Array.isArray(results)) {
        this.setData({ searchSuggestions: results.slice(0, 8) });
      } else if (results && results.data) {
        this.setData({ searchSuggestions: results.data.slice(0, 8) });
      }
    } catch (error) {
      console.error('搜索失败:', error);
    }
  },

  async onSearch() {
    const { searchQuery, symbol } = this.data;
    if (!searchQuery.trim()) {
      wx.showToast({ title: '请输入股票代码或名称', icon: 'none' });
      return;
    }

    // 如果输入的就是当前股票代码，直接刷新
    if (searchQuery.toUpperCase() === symbol) {
      this.refreshData();
      return;
    }

    try {
      wx.showLoading({ title: '搜索中...' });
      const results = await api.searchSymbols(searchQuery);
      wx.hideLoading();
      
      if (results && results.length > 0) {
        // 显示搜索结果供用户选择
        this.setData({ searchSuggestions: results.slice(0, 8) });
        
        if (results.length === 1) {
          // 只有一个结果，直接选中
          this.onSelectStock({ currentTarget: { dataset: results[0] }});
        }
      } else {
        wx.showToast({
          title: '未找到相关股票',
          icon: 'none'
        });
        this.setData({ searchSuggestions: [] });
      }
    } catch (error) {
      wx.hideLoading();
      console.error('搜索失败:', error);
      wx.showToast({ title: '搜索失败，请检查网络', icon: 'none' });
    }
  },

  onSelectStock(e) {
    const { symbol, name } = e.currentTarget.dataset;
    console.log('选择股票:', symbol, name);

    // 清空搜索
    this.setData({
      searchQuery: '',
      searchSuggestions: []
    });

    // 添加到搜索历史
    if (symbol && name) {
      storage.addSearchHistory({ symbol, name });
      this.loadSearchHistory();
    }

    // 切换股票
    if (symbol !== this.data.currentSymbol) {
      // 取消之前的订阅
      if (this.data.currentSymbol) {
        websocket.unsubscribe([this.data.currentSymbol]);
      }

      this.setData({
        currentSymbol: symbol,
        currentStockName: name || symbol,
        matrixData: null,
        currentPrice: {},
        buyMatchStatus: null,
        stopLossStatus: null
      });

      console.log('开始加载数据...');
      // 加载新数据
      this.loadData();
    }
  },

  // ==================== 策略匹配 ====================

  /**
   * 加载策略设置并检查匹配
   */
  checkStrategyMatch() {
    const settings = storage.getUserPref('strategy_settings');
    if (!settings) {
      this.setData({ strategySettings: null });
      return;
    }

    this.setData({ strategySettings: settings });

    const { matrixData, currentPrice } = this.data;
    if (!matrixData) return;

    const price = currentPrice.price || matrixData.current_price || 0;

    // 检查买入策略匹配
    const buyMatch = this.checkBuyStrategyMatch(settings, matrixData, price);
    this.setData({ buyMatchStatus: buyMatch });

    // 检查止损策略（这里只检查技术指标条件，固定比例止损需要成本价）
    const stopLoss = this.checkStopLossStrategy(settings, matrixData, price);
    this.setData({ stopLossStatus: stopLoss });
  },

  /**
   * 检查买入策略是否匹配
   */
  checkBuyStrategyMatch(settings, matrixData, price) {
    const buyConditions = settings.buyConditions || {};
    const conditions = [];
    const missing = [];

    // MACD 金叉
    if (buyConditions.macdGolden) {
      const macd = matrixData.macd;
      if (macd && macd.dif > macd.signal) {
        conditions.push({ name: 'MACD金叉', satisfied: true });
      } else {
        const dif = macd ? macd.dif?.toFixed(2) : '--';
        const signal = macd ? macd.signal?.toFixed(2) : '--';
        missing.push({ name: 'MACD金叉', reason: `DIF=${dif}, Signal=${signal}` });
      }
    }

    // 均线上穿
    if (buyConditions.maGolden) {
      const ma = matrixData.ma;
      if (ma && ma.is_bullish) {
        conditions.push({ name: '均线上穿', satisfied: true });
      } else {
        const shortMA = ma ? ma.ma_short?.toFixed(1) : '--';
        const longMA = ma ? ma.ma_long?.toFixed(1) : '--';
        missing.push({ name: '均线上穿', reason: `MA${ma?.short_period || 5}=${shortMA}, MA${ma?.long_period || 20}=${longMA}` });
      }
    }

    // 股价站上MA5
    if (buyConditions.priceAboveMA5) {
      const ma = matrixData.ma;
      if (ma && ma.ma_short && price >= ma.ma_short) { // 严格判断：当前价必须 >= MA5
        conditions.push({ name: '站上MA5', satisfied: true });
      } else {
        const ma5 = ma ? ma.ma_short?.toFixed(2) : '--';
        const distance = ma && ma.ma_short
          ? ((ma.ma_short - price) / price * 100).toFixed(1)
          : '--';
        missing.push({ name: '站上MA5', reason: `MA5=${ma5}, 需涨${distance}%` });
      }
    }

    // 股价站上MA10
    if (buyConditions.priceAboveMA10) {
      const ma = matrixData.ma;
      if (ma && ma.ma_long && price >= ma.ma_long * 0.99) { // 允许1%误差
        conditions.push({ name: '站上MA10', satisfied: true });
      } else {
        const ma10 = ma ? ma.ma_long?.toFixed(2) : '--';
        const distance = ma && ma.ma_long
          ? ((ma.ma_long - price) / price * 100).toFixed(1)
          : '--';
        missing.push({ name: '站上MA10', reason: `MA10=${ma10}, 需涨${distance}%` });
      }
    }

    // KDJ超卖反弹
    if (buyConditions.kdjOversold) {
      const kdj = matrixData.kdj;
      if (kdj && kdj.j < 0) {
        conditions.push({ name: 'KDJ超卖', satisfied: true });
      } else {
        const jValue = kdj ? kdj.j?.toFixed(1) : '--';
        missing.push({ name: 'KDJ超卖', reason: `J=${jValue}, 需J<0` });
      }
    }

    // RSI超卖
    if (buyConditions.rsiOversold) {
      // 这里假设 RSI 数据在 matrixData 中，如果有的话
      // 暂时用 KDJ 超卖作为替代指标
      const kdj = matrixData.kdj;
      if (kdj && kdj.j < 20) {
        conditions.push({ name: 'RSI低位', satisfied: true });
      } else {
        const jValue = kdj ? kdj.j?.toFixed(1) : '--';
        missing.push({ name: 'RSI低位', reason: `J=${jValue}, 未超卖` });
      }
    }

    // 判断是否全部满足
    const totalConditions = Object.values(buyConditions).filter(v => v).length;
    const matched = conditions.length === totalConditions && totalConditions > 0;

    return {
      matched,
      matchedCount: conditions.length,
      totalCount: totalConditions,
      matchedConditions: conditions,
      missingConditions: missing,
      template: settings.buyTemplate || 'custom'
    };
  },

  /**
   * 检查止损策略是否触发
   */
  checkStopLossStrategy(settings, matrixData, price) {
    const stopLossMode = settings.stopLossMode || 'technical';
    const stopConditions = settings.stopConditions || {};
    const triggered = [];

    if (stopLossMode === 'technical') {
      // MACD 死叉
      if (stopConditions.macdDeath) {
        const macd = matrixData.macd;
        if (macd && macd.dif < macd.signal) {
          triggered.push({ name: 'MACD死叉', severity: 'high' });
        }
      }

      // 均线死叉
      if (stopConditions.maDeath) {
        const ma = matrixData.ma;
        if (ma && ma.is_bearish) {
          triggered.push({ name: '均线死叉', severity: 'high' });
        }
      }

      // 跌破MA5
      if (stopConditions.priceBelowMA5) {
        const ma = matrixData.ma;
        if (ma && ma.ma_short && price < ma.ma_short) { // 严格判断
          triggered.push({ name: '跌破MA5', severity: 'high' });
        }
      }

      // 跌破MA10
      if (stopConditions.priceBelowMA20) {
        const ma = matrixData.ma;
        if (ma && ma.ma_long && price < ma.ma_long * 0.99) { // 允许1%误差
          triggered.push({ name: '跌破MA10', severity: 'medium' });
        }
      }

      return {
        mode: 'technical',
        triggered: triggered.length > 0,
        triggeredCount: triggered.length,
        triggeredConditions: triggered,
        message: triggered.length > 0
          ? `已触发 ${triggered.length} 个止损信号`
          : '技术指标正常，未触发止损'
      };
    } else {
      // 固定比例止损（需要成本价，这里只能做提示）
      const fixedLossPct = parseFloat(settings.fixedLossPct) || -8;
      return {
        mode: 'fixed',
        triggered: false, // 因为没有成本价，无法判断
        threshold: fixedLossPct,
        message: `固定止损: ${fixedLossPct}%（需要设置成本价才能判断）`
      };
    }
  },

  /**
   * 跳转到策略设置页
   */
  goToStrategySettings() {
    wx.navigateTo({
      url: '/pages/strategy/strategy'
    });
  },

  clearSearch() {
    this.setData({
      searchQuery: '',
      searchSuggestions: []
    });
  },

  clearSearchHistory() {
    wx.showModal({
      title: '提示',
      content: '确定清空搜索历史吗？',
      success: (res) => {
        if (res.confirm) {
          storage.clearSearchHistory();
          this.setData({ searchHistory: [] });
        }
      }
    });
  },

  // ==================== WebSocket ====================

  connectWebSocket() {
    // 注册回调
    websocket.onPriceUpdate(this.onPriceUpdate.bind(this));
    websocket.onAlert(this.onAlert.bind(this));
    websocket.onOpen(this.onWebSocketOpen.bind(this));

    // 连接
    websocket.connect();
  },

  onWebSocketOpen() {
    console.log('WebSocket 连接成功，订阅股票:', this.data.currentSymbol);
    if (this.data.currentSymbol) {
      websocket.subscribe([this.data.currentSymbol]);
    }
  },

  onPriceUpdate(data) {
    // 更新价格
    if (data.symbol === this.data.currentSymbol && data.price) {
      this.setData({
        currentPrice: {
          price: data.price,
          change: data.change || 0,
          changePercent: data.change_percent || 0
        },
        updateTime: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      });
    }
  },

  onAlert(data) {
    console.log('收到预警:', data);
    // 显示预警提示
    if (data.symbol === this.data.currentSymbol) {
      wx.showModal({
        title: '预警通知',
        content: data.message || '价格接近临界值',
        showCancel: false
      });
    }
  },

  // ==================== 自动刷新 ====================

  startAutoRefresh() {
    // 先清除之前的定时器
    this.stopAutoRefresh();

    // 设置新的定时器
    const timer = setInterval(() => {
      console.log('自动刷新数据');
      this.loadData();
    }, config.REFRESH_INTERVAL);

    this.setData({ autoRefreshTimer: timer });
  },

  stopAutoRefresh() {
    if (this.data.autoRefreshTimer) {
      clearInterval(this.data.autoRefreshTimer);
      this.setData({ autoRefreshTimer: null });
    }
  },

  refreshData() {
    // 手动刷新
    this.loadData();
    wx.showToast({
      title: '刷新成功',
      icon: 'success',
      duration: 1000
    });
  },

  // ==================== 状态更新 ====================

  updateIndicatorStatus(matrixData) {
    const { currentPrice } = this.data;
    const price = currentPrice.price || matrixData.current_price || 0;

    // MACD 状态
    if (matrixData.macd) {
      const macd = matrixData.macd;
      let macdClass = 'neutral';
      let macdText = '观望';

      if (macd.dif > macd.signal) {
        macdClass = 'bullish';
        macdText = '多头';
      } else if (macd.dif < macd.signal) {
        macdClass = 'bearish';
        macdText = '空头';
      }

      // 如果接近金叉
      if (macd.golden_cross_price && Math.abs((macd.golden_cross_price - price) / price * 100) < 2) {
        macdText = '即将金叉';
        macdClass = 'bullish';
      }

      this.setData({
        macdStatusClass: macdClass,
        macdStatusText: macdText
      });
    }

    // 均线状态
    if (matrixData.ma) {
      const ma = matrixData.ma;
      let maClass = 'neutral';
      let maText = '观望';

      if (ma.is_bullish) {
        maClass = 'bullish';
        maText = '多头排列';
      } else if (ma.is_bearish) {
        maClass = 'bearish';
        maText = '空头排列';
      }

      // 如果接近金叉
      if (ma.golden_cross_price && Math.abs((ma.golden_cross_price - price) / price * 100) < 2) {
        maText = '即将金叉';
        maClass = 'bullish';
      }

      this.setData({
        maStatusClass: maClass,
        maStatusText: maText
      });
    }

    // KDJ 状态
    if (matrixData.kdj) {
      const kdj = matrixData.kdj;
      let kdjClass = 'neutral';
      let kdjText = '中性';

      if (kdj.j > 100) {
        kdjClass = 'bearish';
        kdjText = '超买区';
      } else if (kdj.j < 0) {
        kdjClass = 'bullish';
        kdjText = '超卖区';
      }

      // 如果接近超卖
      if (kdj.oversold_price && price > kdj.oversold_price && (price - kdj.oversold_price) / price * 100 < 3) {
        kdjText = '接近超卖';
        kdjClass = 'bullish';
      }

      this.setData({
        kdjStatusClass: kdjClass,
        kdjStatusText: kdjText
      });
    }
  },

  // ==================== 策略看板 ====================

  /**
   * 计算策略看板 - 根据用户策略设置判断可买/止损
   */
  async calculateDashboardMetrics(matrixData, currentPrice) {
    if (!currentPrice || !matrixData) return;

    // 获取用户策略设置
    const strategySettings = storage.getUserPref('strategy_settings');

    try {
      // 调用后端API计算策略价格区间
      const rangeResult = await api.calculateStrategyRange(
        this.data.currentSymbol,
        {
          buy_conditions: strategySettings ? strategySettings.buyConditions : {},
          stop_conditions: strategySettings ? strategySettings.stopConditions : {},
          current_price: currentPrice
        }
      );

      // 统一字段名映射：buy_range -> buy, stop_range -> stop
      const normalizedRange = {
        symbol: rangeResult.symbol,
        name: rangeResult.name,
        current_price: rangeResult.current_price,
        buy: rangeResult.buy_range,
        stop: rangeResult.stop_range,
        recommendation: rangeResult.recommendation
      };

      this.setData({
        strategyRange: normalizedRange,
        buyMatched: normalizedRange.buy ? normalizedRange.buy.current_satisfied : null,
        stopLossTriggered: normalizedRange.stop ? normalizedRange.stop.current_triggered : false
      });

    } catch (error) {
      console.error('计算策略价格区间失败:', error);
      // 失败时使用本地计算
      this.calculateLocalMetrics(matrixData, currentPrice, strategySettings);
    }
  },

  /**
   * 本地计算策略（API失败时备用）
   */
  calculateLocalMetrics(matrixData, currentPrice, strategySettings) {
    if (!strategySettings) {
      this.setData({
        strategyRange: null,
        buyMatched: null,
        stopLossTriggered: false
      });
      return;
    }

    const buyMatch = this.checkBuyStrategyMatch(strategySettings, matrixData, currentPrice);
    const stopLoss = this.checkStopLossStrategy(strategySettings, matrixData, currentPrice);

    // 本地计算触发价格
    const buyConditions = strategySettings.buyConditions || {};
    const stopConditions = strategySettings.stopConditions || {};
    const criticalPrices = [];

    // 买入触发价格计算
    if (buyConditions.macdGolden && matrixData.macd && matrixData.macd.dif < matrixData.macd.signal) {
      const targetPrice = matrixData.macd.golden_cross_price || currentPrice * 1.02;
      criticalPrices.push({
        condition: 'MACD金叉',
        target_price: targetPrice,
        direction: 'above',
        distance_pct: ((targetPrice - currentPrice) / currentPrice * 100)
      });
    }
    if (buyConditions.maGolden && matrixData.ma && !matrixData.ma.is_bullish) {
      const targetPrice = matrixData.ma.golden_cross_price || currentPrice * 1.01;
      criticalPrices.push({
        condition: '均线上穿',
        target_price: targetPrice,
        direction: 'above',
        distance_pct: ((targetPrice - currentPrice) / currentPrice * 100)
      });
    }
    if (buyConditions.priceAboveMA5 && matrixData.ma && currentPrice < matrixData.ma.ma_short) {
      const targetPrice = matrixData.ma.ma_short;
      criticalPrices.push({
        condition: '站上MA5',
        target_price: targetPrice,
        direction: 'above',
        distance_pct: ((targetPrice - currentPrice) / currentPrice * 100)
      });
    }
    if (buyConditions.priceAboveMA10 && matrixData.ma && currentPrice < matrixData.ma.ma_long) {
      const targetPrice = matrixData.ma.ma_long;
      criticalPrices.push({
        condition: '站上MA10',
        target_price: targetPrice,
        direction: 'above',
        distance_pct: ((targetPrice - currentPrice) / currentPrice * 100)
      });
    }

    // 止损线计算
    let stopPrice = currentPrice * 0.9;
    if (stopConditions.macdDeath && matrixData.macd && matrixData.macd.death_cross_price) {
      stopPrice = Math.max(stopPrice, matrixData.macd.death_cross_price);
    }
    if (stopConditions.maDeath && matrixData.ma && matrixData.ma.death_cross_price) {
      stopPrice = Math.max(stopPrice, matrixData.ma.death_cross_price);
    }
    if (stopConditions.priceBelowMA5 && matrixData.ma && matrixData.ma.ma_short) {
      stopPrice = Math.max(stopPrice, matrixData.ma.ma_short);
    }
    if (stopConditions.priceBelowMA20 && matrixData.ma && matrixData.ma.ma_long) {
      stopPrice = Math.max(stopPrice, matrixData.ma.ma_long);
    }

    const localRange = {
      buy: {
        current_satisfied: buyMatch.matched,
        critical_prices: criticalPrices,
        unsatisfied_conditions: buyMatch.matched ? [] : (buyMatch.missingConditions || []).map(c => c.name)
      },
      stop: {
        current_triggered: stopLoss.triggered,
        stop_price: stopPrice.toFixed(2),
        triggered_conditions: (stopLoss.triggeredConditions || []).map(c => c.name || c),
        distance_to_stop: parseFloat(((currentPrice - stopPrice) / currentPrice * 100).toFixed(2))
      }
    };

    this.setData({
      strategyRange: localRange,
      buyMatched: buyMatch.matched,
      stopLossTriggered: stopLoss.triggered
    });
  },

  /**
   * 检查买入策略是否匹配
   */
  checkBuyStrategyMatch(settings, matrixData, currentPrice) {
    const buyConditions = settings.buyConditions || {};
    const conditions = [];
    const missing = [];

    // MACD 金叉
    if (buyConditions.macdGolden) {
      const macd = matrixData.macd;
      if (macd && macd.dif > macd.signal) {
        conditions.push({ name: 'MACD金叉', satisfied: true });
      } else {
        missing.push({ name: 'MACD金叉', reason: `DIF=${macd?.dif?.toFixed(2)}, Signal=${macd?.signal?.toFixed(2)}` });
      }
    }

    // 均线上穿
    if (buyConditions.maGolden) {
      const ma = matrixData.ma;
      if (ma && ma.is_bullish) {
        conditions.push({ name: '均线上穿', satisfied: true });
      } else {
        missing.push({ name: '均线上穿', reason: `MA${ma?.short_period || 5}=${ma?.ma_short?.toFixed(1)}, MA${ma?.long_period || 10}=${ma?.ma_long?.toFixed(1)}` });
      }
    }

    // 股价站上MA5
    if (buyConditions.priceAboveMA5) {
      const ma = matrixData.ma;
      if (ma && ma.ma_short && currentPrice >= ma.ma_short) { // 严格判断
        conditions.push({ name: '站上MA5', satisfied: true });
      } else {
        const distance = ma && ma.ma_short ? ((ma.ma_short - currentPrice) / currentPrice * 100).toFixed(1) : '--';
        missing.push({ name: '站上MA5', reason: `需涨${distance}%` });
      }
    }

    // 股价站上MA10
    if (buyConditions.priceAboveMA10) {
      const ma = matrixData.ma;
      if (ma && ma.ma_long && currentPrice >= ma.ma_long) { // 严格判断
        conditions.push({ name: '站上MA10', satisfied: true });
      } else {
        const distance = ma && ma.ma_long ? ((ma.ma_long - currentPrice) / currentPrice * 100).toFixed(1) : '--';
        missing.push({ name: '站上MA10', reason: `需涨${distance}%` });
      }
    }

    // KDJ超卖反弹
    if (buyConditions.kdjOversold) {
      const kdj = matrixData.kdj;
      if (kdj && kdj.j < 0) {
        conditions.push({ name: 'KDJ超卖', satisfied: true });
      } else {
        missing.push({ name: 'KDJ超卖', reason: `J=${kdj?.j?.toFixed(1)}, 需J<0` });
      }
    }

    // RSI超卖
    if (buyConditions.rsiOversold) {
      const rsi = matrixData.rsi;
      if (rsi && rsi.value < 30) {
        conditions.push({ name: 'RSI超卖', satisfied: true });
      } else {
        missing.push({ name: 'RSI超卖', reason: `RSI=${rsi?.value?.toFixed(1)}, 需<30` });
      }
    }

    const totalConditions = Object.values(buyConditions).filter(v => v).length;
    const matched = conditions.length === totalConditions && totalConditions > 0;

    return {
      matched,
      matchedCount: conditions.length,
      totalCount: totalConditions,
      matchedConditions: conditions,
      missingConditions: missing
    };
  },

  /**
   * 检查止损策略是否触发
   */
  checkStopLossStrategy(settings, matrixData, currentPrice) {
    const stopLossMode = settings.stopLossMode || 'technical';
    const stopConditions = settings.stopConditions || {};
    const triggered = [];

    if (stopLossMode === 'technical') {
      // MACD 死叉
      if (stopConditions.macdDeath) {
        const macd = matrixData.macd;
        if (macd && macd.dif < macd.signal) {
          triggered.push({ name: 'MACD死叉', severity: 'high' });
        }
      }

      // 均线死叉
      if (stopConditions.maDeath) {
        const ma = matrixData.ma;
        if (ma && !ma.is_bullish) {
          triggered.push({ name: '均线死叉', severity: 'high' });
        }
      }

      // 跌破MA5
      if (stopConditions.priceBelowMA5) {
        const ma = matrixData.ma;
        if (ma && ma.ma_short && currentPrice < ma.ma_short) { // 严格判断
          triggered.push({ name: '跌破MA5', severity: 'high' });
        }
      }

      // 跌破MA10
      if (stopConditions.priceBelowMA20) {
        const ma = matrixData.ma;
        if (ma && ma.ma_long && currentPrice < ma.ma_long) { // 严格判断
          triggered.push({ name: '跌破MA10', severity: 'medium' });
        }
      }

      return {
        mode: 'technical',
        triggered: triggered.length > 0,
        triggeredCount: triggered.length,
        triggeredConditions: triggered
      };
    } else {
      // 固定比例止损
      const fixedLossPct = parseFloat(settings.fixedLossPct) || -8;
      return {
        mode: 'fixed',
        threshold: fixedLossPct,
        message: `固定止损: ${fixedLossPct}%（需成本价才能计算）`
      };
    }
  },

  /**
   * 默认策略（无用户设置时）
   */
  setDefaultMetrics(matrixData, currentPrice) {
    let stopLossTriggered = false;

    // 默认：MACD死叉触发止损
    if (matrixData.macd && matrixData.macd.dif < matrixData.macd.signal) {
      stopLossTriggered = true;
    }

    this.setData({
      buyMatched: null,  // 未设置策略
      stopLossTriggered
    });
  },

  /**
   * 生成共振预警文字
   */
  generateResonanceAlert(matrixData, currentPrice) {
    if (!matrixData || !currentPrice) return '';

    const alerts = [];

    // 检查MACD和均线是否同时接近金叉
    if (matrixData.macd && matrixData.ma) {
      const macdGolden = matrixData.macd.golden_cross_price;
      const maGolden = matrixData.ma.golden_cross_price;

      if (macdGolden && maGolden) {
        const macdDist = Math.abs((macdGolden - currentPrice) / currentPrice * 100);
        const maDist = Math.abs((maGolden - currentPrice) / currentPrice * 100);

        if (macdDist < 2 && maDist < 2) {
          const higherPrice = Math.max(macdGolden, maGolden);
          alerts.push(`价格突破 ${higherPrice.toFixed(2)} 将形成双金叉`);
        }
      }
    }

    // 检查KDJ超卖
    if (matrixData.kdj && matrixData.kdj.oversold_price) {
      const kdjDist = ((currentPrice - matrixData.kdj.oversold_price) / currentPrice * 100);
      if (kdjDist > 0 && kdjDist < 3) {
        alerts.push(`KDJ接近超卖区，需跌至 ${matrixData.kdj.oversold_price.toFixed(2)}`);
      }
    }

    return alerts[0] || '';
  },

  /**
   * 清空当前股票
   */
  clearStock() {
    // 取消订阅
    if (this.data.currentSymbol) {
      websocket.unsubscribe([this.data.currentSymbol]);
    }

    this.setData({
      currentSymbol: '',
      currentStockName: '',
      currentPrice: {},
      matrixData: null,
      buyMatchStatus: null,
      stopLossStatus: null,
      buyDistance: null,
      buyProgress: 0,
      stopLossTriggered: false,
      stopDistance: null,
      resonanceAlert: ''
    });
  },

  /**
   * 切换看板详情展开/收起
   */
  toggleDashboardDetail() {
    this.setData({
      dashboardExpanded: !this.data.dashboardExpanded
    });

    // 如果展开，跳转到详细矩阵页面
    if (!this.data.dashboardExpanded) {
      // 这里可以导航到详细页面
      console.log('查看详情');
    }
  },

  /**
   * 设置预警
   */
  setAlert() {
    wx.showToast({
      title: '预警功能开发中',
      icon: 'none'
    });
  }
});
