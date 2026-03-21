// WebSocket 管理器
const config = require('../config');

class WebSocketManager {
  constructor() {
    this.socket = null;
    this.callbacks = {};
    this.reconnectTimer = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 5000;
    this.isConnected = false;
    this.subscribedSymbols = new Set();
  }

  /**
   * 连接 WebSocket
   */
  connect() {
    if (this.socket) {
      console.log('WebSocket 已存在，无需重复连接');
      return;
    }

    console.log('正在连接 WebSocket...');

    this.socket = wx.connectSocket({
      url: config.WS_URL,
      protocols: [],
      success: () => {
        console.log('WebSocket 连接请求已发送');
      },
      fail: (err) => {
        console.error('WebSocket 连接请求失败:', err);
        this.handleReconnect();
      }
    });

    this.bindEvents();
  }

  /**
   * 绑定事件处理
   */
  bindEvents() {
    // 连接成功
    this.socket.onOpen(() => {
      console.log('WebSocket 连接成功');
      this.isConnected = true;
      this.reconnectAttempts = 0;

      // 重新订阅之前的股票
      if (this.subscribedSymbols.size > 0) {
        this.subscribe(Array.from(this.subscribedSymbols));
      }

      // 触发连接成功回调
      this.triggerCallback('open');
    });

    // 收到消息
    this.socket.onMessage((res) => {
      try {
        const data = JSON.parse(res.data);
        console.log('WebSocket 收到消息:', data.type);
        this.handleMessage(data);
      } catch (e) {
        console.error('WebSocket 消息解析失败:', e);
      }
    });

    // 连接关闭
    this.socket.onClose((res) => {
      console.log('WebSocket 连接关闭:', res);
      this.isConnected = false;
      this.socket = null;

      // 触发关闭回调
      this.triggerCallback('close', res);

      // 尝试重连
      this.handleReconnect();
    });

    // 连接错误
    this.socket.onError((err) => {
      console.error('WebSocket 错误:', err);
      this.triggerCallback('error', err);
    });
  }

  /**
   * 处理重连
   */
  handleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('WebSocket 重连次数已达上限，停止重连');
      return;
    }

    this.reconnectAttempts++;
    console.log(`WebSocket ${this.reconnectInterval / 1000}秒后尝试第${this.reconnectAttempts}次重连...`);

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, this.reconnectInterval);
  }

  /**
   * 处理消息
   */
  handleMessage(data) {
    const { type } = data;

    switch (type) {
      case 'price_update':
        this.triggerCallback('price_update', data);
        break;
      case 'alert':
        this.triggerCallback('alert', data);
        break;
      case 'matrix_update':
        this.triggerCallback('matrix_update', data);
        break;
      case 'stress_test_result':
        this.triggerCallback('stress_test_result', data);
        break;
      case 'subscribe_confirm':
        console.log('订阅确认:', data);
        break;
      case 'pong':
        // 心跳响应
        break;
      case 'error':
        console.error('服务器错误:', data);
        this.triggerCallback('error', data);
        break;
      default:
        console.log('未知消息类型:', type, data);
    }
  }

  /**
   * 发送消息
   */
  send(data) {
    if (!this.isConnected || !this.socket) {
      console.warn('WebSocket 未连接，无法发送消息');
      return false;
    }

    try {
      this.socket.send({
        data: JSON.stringify(data)
      });
      return true;
    } catch (e) {
      console.error('WebSocket 发送消息失败:', e);
      return false;
    }
  }

  /**
   * 订阅股票
   * @param {string[]} symbols - 股票代码数组
   */
  subscribe(symbols) {
    if (!Array.isArray(symbols)) {
      symbols = [symbols];
    }

    // 记录订阅的股票
    symbols.forEach(symbol => this.subscribedSymbols.add(symbol));

    return this.send({
      type: 'subscribe',
      symbols
    });
  }

  /**
   * 取消订阅股票
   * @param {string[]} symbols - 股票代码数组
   */
  unsubscribe(symbols) {
    if (!Array.isArray(symbols)) {
      symbols = [symbols];
    }

    // 移除记录
    symbols.forEach(symbol => this.subscribedSymbols.delete(symbol));

    return this.send({
      type: 'unsubscribe',
      symbols
    });
  }

  /**
   * 请求触发矩阵
   * @param {string} symbol - 股票代码
   */
  getMatrix(symbol) {
    return this.send({
      type: 'get_matrix',
      symbol
    });
  }

  /**
   * 实时压力测试
   * @param {string} symbol - 股票代码
   * @param {number} price - 假设价格
   */
  stressTest(symbol, price) {
    return this.send({
      type: 'stress_test',
      symbol,
      price
    });
  }

  /**
   * 发送心跳
   */
  ping() {
    return this.send({
      type: 'ping'
    });
  }

  /**
   * 关闭连接
   */
  close() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    this.subscribedSymbols.clear();

    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }

    this.isConnected = false;
    this.reconnectAttempts = 0;
  }

  /**
   * 注册回调函数
   * @param {string} event - 事件名称
   * @param {Function} callback - 回调函数
   */
  on(event, callback) {
    if (!this.callbacks[event]) {
      this.callbacks[event] = [];
    }
    this.callbacks[event].push(callback);

    // 返回取消订阅函数
    return () => {
      this.off(event, callback);
    };
  }

  /**
   * 移除回调函数
   * @param {string} event - 事件名称
   * @param {Function} callback - 回调函数
   */
  off(event, callback) {
    if (!this.callbacks[event]) return;

    const index = this.callbacks[event].indexOf(callback);
    if (index > -1) {
      this.callbacks[event].splice(index, 1);
    }
  }

  /**
   * 触发回调
   */
  triggerCallback(event, data) {
    if (!this.callbacks[event]) return;

    this.callbacks[event].forEach(callback => {
      try {
        callback(data);
      } catch (e) {
        console.error(`WebSocket ${event} 回调执行失败:`, e);
      }
    });
  }

  /**
   * 注册价格更新回调
   * @param {Function} callback
   */
  onPriceUpdate(callback) {
    return this.on('price_update', callback);
  }

  /**
   * 注册预警回调
   * @param {Function} callback
   */
  onAlert(callback) {
    return this.on('alert', callback);
  }

  /**
   * 注册矩阵更新回调
   * @param {Function} callback
   */
  onMatrixUpdate(callback) {
    return this.on('matrix_update', callback);
  }

  /**
   * 注册压力测试结果回调
   * @param {Function} callback
   */
  onStressTestResult(callback) {
    return this.on('stress_test_result', callback);
  }

  /**
   * 注册连接成功回调
   * @param {Function} callback
   */
  onOpen(callback) {
    return this.on('open', callback);
  }

  /**
   * 注册连接关闭回调
   * @param {Function} callback
   */
  onClose(callback) {
    return this.on('close', callback);
  }

  /**
   * 注册错误回调
   * @param {Function} callback
   */
  onError(callback) {
    return this.on('error', callback);
  }

  /**
   * 获取连接状态
   */
  getStatus() {
    return {
      isConnected: this.isConnected,
      subscribedSymbols: Array.from(this.subscribedSymbols),
      reconnectAttempts: this.reconnectAttempts
    };
  }
}

// 创建单例实例
const websocketManager = new WebSocketManager();

module.exports = websocketManager;
