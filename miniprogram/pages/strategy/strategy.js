// 策略页逻辑 - 纯设置页面
const storage = require('../../utils/storage');

Page({
  data: {
    // 买入策略
    buyTemplate: 'custom', // conservative, aggressive, momentum, custom
    buyConditions: {
      macdGolden: false,
      maGolden: false,
      priceAboveMA5: false,
      priceAboveMA10: false,
      kdjOversold: false,
      rsiOversold: false
    },

    // 止损策略
    stopLossMode: 'technical', // technical, fixed
    stopConditions: {
      macdDeath: true,
      maDeath: false,
      priceBelowMA5: false,
      priceBelowMA20: false
    },
    fixedLossPct: '-8',

    // 保存状态提示
    saveStatus: ''
  },

  onLoad() {
    // 加载已保存的策略设置
    this.loadStrategySettings();
  },

  onShow() {
    // 每次显示页面时刷新设置
    this.loadStrategySettings();
  },

  // 加载策略设置
  loadStrategySettings() {
    const settings = storage.getUserPref('strategy_settings');
    if (settings) {
      this.setData({
        buyTemplate: settings.buyTemplate || 'custom',
        buyConditions: settings.buyConditions || this.data.buyConditions,
        stopLossMode: settings.stopLossMode || 'technical',
        stopConditions: settings.stopConditions || this.data.stopConditions,
        fixedLossPct: settings.fixedLossPct || '-8'
      });
    }
  },

  // 保存策略设置
  saveStrategySettings() {
    const {
      buyTemplate,
      buyConditions,
      stopLossMode,
      stopConditions,
      fixedLossPct
    } = this.data;

    const settings = {
      buyTemplate,
      buyConditions,
      stopLossMode,
      stopConditions,
      fixedLossPct
    };

    storage.setUserPref('strategy_settings', settings);

    // 显示保存提示
    this.setData({ saveStatus: '已自动保存' });
    setTimeout(() => {
      this.setData({ saveStatus: '' });
    }, 2000);
  },

  // ==================== 买入策略设置 ====================

  applyBuyTemplate(e) {
    const template = e.currentTarget.dataset.template;
    const templates = {
      conservative: {
        macdGolden: true,
        maGolden: true,
        priceAboveMA5: false,
        priceAboveMA10: false,
        kdjOversold: false,
        rsiOversold: false
      },
      aggressive: {
        macdGolden: false,
        maGolden: false,
        priceAboveMA5: true,
        priceAboveMA10: false,
        kdjOversold: true,
        rsiOversold: false
      },
      momentum: {
        macdGolden: false,
        maGolden: false,
        priceAboveMA5: false,
        priceAboveMA10: true,
        kdjOversold: false,
        rsiOversold: true
      },
      custom: {
        macdGolden: false,
        maGolden: false,
        priceAboveMA5: false,
        priceAboveMA10: false,
        kdjOversold: false,
        rsiOversold: false
      }
    };

    this.setData({
      buyTemplate: template,
      buyConditions: templates[template] || templates.custom
    });

    // 触觉反馈
    if (wx.vibrateShort) {
      wx.vibrateShort({ type: 'light' });
    }

    // 自动保存
    this.saveStrategySettings();
  },

  toggleBuyCondition(e) {
    const { key } = e.currentTarget.dataset;
    const newConditions = {
      ...this.data.buyConditions,
      [key]: !this.data.buyConditions[key]
    };

    // 检查是否为自定义
    const isCustom = !this.isStandardTemplate(newConditions);

    this.setData({
      buyConditions: newConditions,
      buyTemplate: isCustom ? 'custom' : this.data.buyTemplate
    });

    // 自动保存
    this.saveStrategySettings();
  },

  // 检查当前设置是否匹配某个标准模板
  isStandardTemplate(conditions) {
    const templates = {
      conservative: { macdGolden: true, maGolden: true, priceAboveMA5: false, priceAboveMA10: false, kdjOversold: false, rsiOversold: false },
      aggressive: { macdGolden: false, maGolden: false, priceAboveMA5: true, priceAboveMA10: false, kdjOversold: true, rsiOversold: false },
      momentum: { macdGolden: false, maGolden: false, priceAboveMA5: false, priceAboveMA10: true, kdjOversold: false, rsiOversold: true }
    };

    for (const [name, template] of Object.entries(templates)) {
      if (JSON.stringify(conditions) === JSON.stringify(template)) {
        return true;
      }
    }
    return false;
  },

  // ==================== 止损策略设置 ====================

  setStopLossMode(e) {
    const mode = e.currentTarget.dataset.mode;
    this.setData({ stopLossMode: mode });

    // 自动保存
    this.saveStrategySettings();
  },

  toggleStopCondition(e) {
    const { key } = e.currentTarget.dataset;
    this.setData({
      [`stopConditions.${key}`]: !this.data.stopConditions[key]
    });

    // 自动保存
    this.saveStrategySettings();
  },

  onFixedLossInput(e) {
    const value = e.detail.value;
    this.setData({ fixedLossPct: value });

    // 自动保存
    this.saveStrategySettings();
  }
});