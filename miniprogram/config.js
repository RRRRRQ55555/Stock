// 配置常量
const config = {
  // ==========================================
  // 服务器配置 - 阿里云服务器
  // ==========================================
  // 
  // 开发环境（本地测试）
  // API_BASE: 'http://localhost:8000/api',
  // WS_URL: 'ws://localhost:8000/ws',
  // 
  // 生产环境（阿里云服务器）
  // 体验版/正式版在真机上会校验「服务器域名」：须 https + 已备案域名，不能填 IP；HTTP 仅开发者工具勾「不校验」时可用。
  // 上线流程：域名解析到服务器 → Nginx(443) 配证书并反代到 8000 → 小程序后台配置 request/wss 合法域名 → 下面改为 https://你的域名/api 与 wss://你的域名/ws
  API_BASE: 'http://121.40.101.189:8000/api',
  WS_URL: 'ws://121.40.101.189:8000/ws',
  
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
