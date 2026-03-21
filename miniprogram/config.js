// 配置常量
const config = {
  // API 基础地址 - 生产环境
  // 注意：小程序正式版要求 HTTPS，开发阶段可临时使用 HTTP
  API_BASE: 'http://47.110.3.64:8000/api',

  // WebSocket 地址
  WS_URL: 'ws://47.110.3.64:8000/ws',
  
  // 刷新间隔（毫秒）
  REFRESH_INTERVAL: 30000,  // 矩阵数据刷新间隔
  PRICE_REFRESH_INTERVAL: 5000,  // 价格刷新间隔
  
  // 预警阈值
  ALERT_PROXIMITY_THRESHOLD: 1.0,  // 接近预警阈值（百分比）
  
  // 默认股票（空字符串表示默认不加载任何股票）
  DEFAULT_SYMBOL: '',
  
  // 分页配置
  PAGE_SIZE: 20,
  
  // 存储键名
  STORAGE_KEYS: {
    SEARCH_HISTORY: 'search_history',
    STRATEGIES: 'strategies',
    USER_PREFS: 'user_prefs'
  }
};

module.exports = config;
