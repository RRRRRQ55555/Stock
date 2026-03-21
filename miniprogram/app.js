// 小程序入口文件
const config = require('./config');

App({
  // 全局数据
  globalData: {
    userInfo: null,
    systemInfo: null,
    networkType: null,
     currentSymbol: '', 
    apiBase: config.API_BASE,
    wsUrl: config.WS_URL
  },

  onLaunch() {
    console.log('小程序启动');
    
    // 获取系统信息
    this.getSystemInfo();
    
    // 监听网络状态
    this.listenNetworkStatus();
    
    // 初始化本地存储
    this.initStorage();
  },

  onShow() {
    console.log('小程序显示');
  },

  onHide() {
    console.log('小程序隐藏');
  },

  onError(msg) {
    console.error('小程序错误:', msg);
  },

  // 获取系统信息
  getSystemInfo() {
    wx.getSystemInfo({
      success: (res) => {
        this.globalData.systemInfo = res;
        console.log('系统信息:', res);
      }
    });
  },

  // 监听网络状态
  listenNetworkStatus() {
    wx.getNetworkType({
      success: (res) => {
        this.globalData.networkType = res.networkType;
        console.log('网络类型:', res.networkType);
      }
    });

    wx.onNetworkStatusChange((res) => {
      this.globalData.networkType = res.networkType;
      console.log('网络状态变化:', res);
    });
  },

  // 初始化本地存储
  initStorage() {
    // 检查并初始化搜索历史
    const searchHistory = wx.getStorageSync(config.STORAGE_KEYS.SEARCH_HISTORY);
    if (!searchHistory) {
      wx.setStorageSync(config.STORAGE_KEYS.SEARCH_HISTORY, []);
    }

    // 检查并初始化策略列表
    const strategies = wx.getStorageSync(config.STORAGE_KEYS.STRATEGIES);
    if (!strategies) {
      wx.setStorageSync(config.STORAGE_KEYS.STRATEGIES, []);
    }

    console.log('本地存储初始化完成');
  },

  // 设置当前股票代码
  setCurrentSymbol(symbol) {
    this.globalData.currentSymbol = symbol;
  },

  // 获取当前股票代码
  getCurrentSymbol() {
    return this.globalData.currentSymbol;
  }
});
