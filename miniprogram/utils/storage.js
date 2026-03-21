// 本地存储封装
const config = require('../config');

const storage = {
  // ==================== 搜索历史 ====================
  
  /**
   * 获取搜索历史
   * @returns {Array} 搜索历史列表
   */
  getSearchHistory: () => {
    try {
      const history = wx.getStorageSync(config.STORAGE_KEYS.SEARCH_HISTORY);
      if (!history || !Array.isArray(history)) {
        return [];
      }
      
      // 清理超过30天的记录
      const now = Date.now();
      const thirtyDays = 30 * 24 * 60 * 60 * 1000;
      const filtered = history.filter(item => {
        return (now - new Date(item.timestamp).getTime()) < thirtyDays;
      });
      
      // 如果有清理，更新存储
      if (filtered.length !== history.length) {
        wx.setStorageSync(config.STORAGE_KEYS.SEARCH_HISTORY, filtered);
      }
      
      return filtered.sort((a, b) => 
        new Date(b.timestamp) - new Date(a.timestamp)
      );
    } catch (e) {
      console.error('获取搜索历史失败:', e);
      return [];
    }
  },

  /**
   * 添加搜索历史
   * @param {Object} item - 搜索项 {symbol, name}
   */
  addSearchHistory: (item) => {
    try {
      let history = storage.getSearchHistory();
      
      // 移除重复项
      history = history.filter(h => h.symbol !== item.symbol);
      
      // 添加新记录
      history.unshift({
        ...item,
        timestamp: new Date().toISOString()
      });
      
      // 限制最多50条
      if (history.length > 50) {
        history = history.slice(0, 50);
      }
      
      wx.setStorageSync(config.STORAGE_KEYS.SEARCH_HISTORY, history);
    } catch (e) {
      console.error('添加搜索历史失败:', e);
    }
  },

  /**
   * 清空搜索历史
   */
  clearSearchHistory: () => {
    try {
      wx.setStorageSync(config.STORAGE_KEYS.SEARCH_HISTORY, []);
    } catch (e) {
      console.error('清空搜索历史失败:', e);
    }
  },

  /**
   * 删除单条搜索历史
   * @param {string} symbol - 股票代码
   */
  removeSearchHistory: (symbol) => {
    try {
      let history = storage.getSearchHistory();
      history = history.filter(h => h.symbol !== symbol);
      wx.setStorageSync(config.STORAGE_KEYS.SEARCH_HISTORY, history);
    } catch (e) {
      console.error('删除搜索历史失败:', e);
    }
  },

  // ==================== 策略列表 ====================

  /**
   * 获取策略列表
   * @returns {Array} 策略列表
   */
  getStrategies: () => {
    try {
      const strategies = wx.getStorageSync(config.STORAGE_KEYS.STRATEGIES);
      return strategies || [];
    } catch (e) {
      console.error('获取策略列表失败:', e);
      return [];
    }
  },

  /**
   * 获取单个策略
   * @param {string} id - 策略ID
   * @returns {Object|null}
   */
  getStrategy: (id) => {
    try {
      const strategies = storage.getStrategies();
      return strategies.find(s => s.id === id) || null;
    } catch (e) {
      console.error('获取策略失败:', e);
      return null;
    }
  },

  /**
   * 保存策略（新增或更新）
   * @param {Object} strategy - 策略对象
   */
  saveStrategy: (strategy) => {
    try {
      let strategies = storage.getStrategies();
      
      const index = strategies.findIndex(s => s.id === strategy.id);
      if (index >= 0) {
        // 更新现有策略
        strategies[index] = {
          ...strategies[index],
          ...strategy,
          updatedAt: new Date().toISOString()
        };
      } else {
        // 新增策略
        strategies.push({
          ...strategy,
          id: strategy.id || Date.now().toString(),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        });
      }
      
      wx.setStorageSync(config.STORAGE_KEYS.STRATEGIES, strategies);
      return strategy.id || strategies[strategies.length - 1].id;
    } catch (e) {
      console.error('保存策略失败:', e);
      return null;
    }
  },

  /**
   * 删除策略
   * @param {string} id - 策略ID
   */
  deleteStrategy: (id) => {
    try {
      let strategies = storage.getStrategies();
      strategies = strategies.filter(s => s.id !== id);
      wx.setStorageSync(config.STORAGE_KEYS.STRATEGIES, strategies);
    } catch (e) {
      console.error('删除策略失败:', e);
    }
  },

  /**
   * 更新策略状态
   * @param {string} id - 策略ID
   * @param {string} status - 新状态
   * @param {Object} extra - 额外数据
   */
  updateStrategyStatus: (id, status, extra = {}) => {
    try {
      let strategies = storage.getStrategies();
      const index = strategies.findIndex(s => s.id === id);
      
      if (index >= 0) {
        strategies[index] = {
          ...strategies[index],
          status,
          ...extra,
          updatedAt: new Date().toISOString()
        };
        wx.setStorageSync(config.STORAGE_KEYS.STRATEGIES, strategies);
      }
    } catch (e) {
      console.error('更新策略状态失败:', e);
    }
  },

  // ==================== 用户偏好 ====================

  /**
   * 获取用户偏好
   * @returns {Object}
   */
  getUserPrefs: () => {
    try {
      const prefs = wx.getStorageSync(config.STORAGE_KEYS.USER_PREFS);
      return prefs || {};
    } catch (e) {
      console.error('获取用户偏好失败:', e);
      return {};
    }
  },

  /**
   * 设置用户偏好
   * @param {Object} prefs - 偏好设置
   */
  setUserPrefs: (prefs) => {
    try {
      const current = storage.getUserPrefs();
      wx.setStorageSync(config.STORAGE_KEYS.USER_PREFS, {
        ...current,
        ...prefs
      });
    } catch (e) {
      console.error('设置用户偏好失败:', e);
    }
  },

  /**
   * 获取特定偏好项
   * @param {string} key - 偏好键
   * @param {*} defaultValue - 默认值
   */
  getUserPref: (key, defaultValue = null) => {
    const prefs = storage.getUserPrefs();
    return prefs[key] !== undefined ? prefs[key] : defaultValue;
  },

  /**
   * 设置特定偏好项
   * @param {string} key - 偏好键
   * @param {*} value - 偏好值
   */
  setUserPref: (key, value) => {
    const prefs = storage.getUserPrefs();
    prefs[key] = value;
    storage.setUserPrefs(prefs);
  },

  // ==================== 通用方法 ====================

  /**
   * 获取存储项
   * @param {string} key - 存储键
   * @param {*} defaultValue - 默认值
   */
  get: (key, defaultValue = null) => {
    try {
      const value = wx.getStorageSync(key);
      return value !== undefined ? value : defaultValue;
    } catch (e) {
      console.error('获取存储失败:', e);
      return defaultValue;
    }
  },

  /**
   * 设置存储项
   * @param {string} key - 存储键
   * @param {*} value - 存储值
   */
  set: (key, value) => {
    try {
      wx.setStorageSync(key, value);
    } catch (e) {
      console.error('设置存储失败:', e);
    }
  },

  /**
   * 清空所有存储
   */
  clearAll: () => {
    try {
      wx.clearStorageSync();
    } catch (e) {
      console.error('清空存储失败:', e);
    }
  },

  /**
   * 获取存储信息
   */
  getStorageInfo: () => {
    try {
      return wx.getStorageInfoSync();
    } catch (e) {
      console.error('获取存储信息失败:', e);
      return null;
    }
  }
};

module.exports = storage;
