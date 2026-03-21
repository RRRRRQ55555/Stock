// API 请求封装
const config = require('../config');

// 请求拦截器
const request = (options) => {
  return new Promise((resolve, reject) => {
    wx.request({
      url: config.API_BASE + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        ...options.header
      },
      timeout: config.networkTimeout?.request || 30000,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else if (res.statusCode === 401) {
          // 未授权，可以在这里处理登录
          reject({ code: 401, message: '未授权' });
        } else {
          reject({
            code: res.statusCode,
            message: res.data?.detail || '请求失败',
            data: res.data
          });
        }
      },
      fail: (err) => {
        console.error('请求失败:', err);
        reject({
          code: -1,
          message: '网络请求失败，请检查网络连接',
          error: err
        });
      }
    });
  });
};

// API 接口封装
const api = {
  // ==================== 矩阵计算接口 ====================
  
  /**
   * 自动计算临界价格触发矩阵
   * @param {string} symbol - 股票代码
   */
  calculateMatrix: (symbol) => request({
    url: `/matrix/auto/${symbol}`,
    method: 'POST'
  }),

  /**
   * 批量计算临界价格矩阵
   * @param {string[]} symbols - 股票代码数组
   */
  calculateMatrixBatch: (symbols) => request({
    url: '/matrix/batch',
    method: 'POST',
    data: { symbols }
  }),

  /**
   * 计算多周期均线矩阵
   * @param {string} symbol - 股票代码
   */
  getMultiMAMatrix: (symbol) => request({
    url: `/matrix/multi-ma/${symbol}`,
    method: 'POST'
  }),

  // ==================== 数据接口 ====================

  /**
   * 获取历史数据
   * @param {string} symbol - 股票代码
   * @param {string} period - 时间周期 (1d, 5d, 1mo, 3mo, 6mo, 1y)
   * @param {string} interval - 时间间隔 (1m, 15m, 1h, 1d)
   */
  getHistoricalData: (symbol, period = '1mo', interval = '1d') => request({
    url: `/historical/${symbol}?period=${period}&interval=${interval}`
  }),

  /**
   * 获取当前价格
   * @param {string} symbol - 股票代码
   */
  getCurrentPrice: (symbol) => request({
    url: `/current-price/${symbol}`
  }),

  /**
   * 搜索股票
   * @param {string} query - 搜索关键词
   */
  searchSymbols: (query) => request({
    url: `/search?q=${encodeURIComponent(query)}`
  }),

  // ==================== 压力测试接口 ====================

  /**
   * 压力测试 - 模拟假设价格下的指标状态
   * @param {Object} data - 测试数据
   */
  stressTest: (data) => request({
    url: '/stress-test',
    method: 'POST',
    data
  }),

  /**
   * 计算策略价格区间
   * @param {string} symbol - 股票代码
   * @param {Object} data - 策略条件
   */
  calculateStrategyRange: (symbol, data) => request({
    url: `/strategy/price-range/${symbol}`,
    method: 'POST',
    data
  }),

  // ==================== 条件筛选接口 ====================

  /**
   * 获取预定义场景列表
   */
  getPredefinedScenarios: () => request({
    url: '/filter/scenarios'
  }),

  /**
   * 条件筛选 - 根据技术指标组合计算共振价格区间
   * @param {Object} data - 筛选条件
   */
  filterByConditions: (data) => request({
    url: '/filter',
    method: 'POST',
    data
  }),

  /**
   * 快速筛选 - 使用预设场景一键筛选
   * @param {string} symbol - 股票代码
   * @param {string} scenario - 场景名称
   */
  quickFilter: (symbol, scenario) => request({
    url: `/filter/quick/${symbol}?scenario=${encodeURIComponent(scenario)}`,
    method: 'POST'
  }),

  // ==================== 预警接口 ====================

  /**
   * 订阅股票预警
   * @param {string} symbol - 股票代码
   * @param {Object} params - 订阅参数
   */
  subscribeAlerts: (symbol, params = {}) => request({
    url: `/alerts/subscribe/${symbol}`,
    method: 'POST',
    data: params
  }),

  /**
   * 取消订阅股票预警
   * @param {string} symbol - 股票代码
   */
  unsubscribeAlerts: (symbol) => request({
    url: `/alerts/unsubscribe/${symbol}`,
    method: 'POST'
  }),

  /**
   * 手动检查预警条件
   * @param {string} symbol - 股票代码
   */
  checkAlertsManual: (symbol) => request({
    url: `/alerts/check/${symbol}`
  }),

  // ==================== 策略管理接口 ====================

  /**
   * 获取策略模板
   */
  getStrategyTemplates: () => request({
    url: '/strategies/templates'
  }),

  /**
   * 创建策略
   * @param {Object} data - 策略数据
   */
  createStrategy: (data) => request({
    url: '/strategies',
    method: 'POST',
    data
  }),

  /**
   * 获取策略列表
   * @param {Object} params - 查询参数
   */
  getStrategies: (params = {}) => request({
    url: '/strategies',
    data: params
  }),

  /**
   * 获取单个策略详情
   * @param {string} id - 策略ID
   */
  getStrategy: (id) => request({
    url: `/strategies/${id}`
  }),

  /**
   * 删除策略
   * @param {string} id - 策略ID
   */
  deleteStrategy: (id) => request({
    url: `/strategies/${id}`,
    method: 'DELETE'
  }),

  /**
   * 检查策略今日状态
   * @param {string} id - 策略ID
   */
  checkStrategy: (id) => request({
    url: `/strategies/${id}/check`
  }),

  /**
   * 批量检查所有策略
   */
  checkAllStrategies: () => request({
    url: '/strategies/check-all',
    method: 'POST'
  }),

  /**
   * 执行策略入场
   * @param {string} id - 策略ID
   * @param {Object} data - 入场数据
   */
  executeEntry: (id, data) => request({
    url: `/strategies/${id}/enter`,
    method: 'POST',
    data
  }),

  /**
   * 执行策略出场
   * @param {string} id - 策略ID
   * @param {Object} data - 出场数据
   */
  executeExit: (id, data) => request({
    url: `/strategies/${id}/exit`,
    method: 'POST',
    data
  }),

  // ==================== 指标配置接口 ====================

  /**
   * 获取技术指标形态
   */
  getIndicatorPatterns: () => request({
    url: '/indicator-patterns'
  }),

  /**
   * 获取指标参数配置
   */
  getIndicatorParams: () => request({
    url: '/indicator-params'
  }),

  /**
   * 简化策略检查
   * @param {string} symbol - 股票代码
   * @param {Object} data - 检查参数
   */
  simpleStrategyCheck: (symbol, data) => request({
    url: `/strategy/simple-check/${symbol}`,
    method: 'POST',
    data
  })
};

module.exports = api;
