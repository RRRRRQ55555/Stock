# 技术指标前置预判工具 - 小程序版

## 项目简介

基于微信小程序原生框架开发的技术指标预判工具，通过反向数学推导计算技术指标临界价格，帮助交易者在信号触发前做出决策。

## 功能特性

### 首页功能
- **股票搜索**：支持按代码/名称搜索，带历史记录
- **实时价格**：显示当前股价和涨跌幅
- **临界价格触发矩阵**：
  - MACD 金叉/死叉临界价格
  - 均线金叉/死叉临界价格
  - KDJ 超卖/超买临界价格
- **共振区间检测**：多指标临界价格重合的高胜率区域
- **自动刷新**：每30秒自动更新数据
- **WebSocket 推送**：实时价格更新和预警通知

### 策略页功能
- **策略管理**：创建、查看、删除交易策略
- **预设场景**：支持多头排列+MACD金叉、超卖反弹等预设策略
- **可行性检查**：检查策略当前是否满足入场条件
- **入场/出场操作**：记录策略执行状态
- **本地存储**：策略数据本地持久化

## 技术架构

```
miniprogram/
├── pages/
│   ├── index/          # 首页 - 股票搜索+触发矩阵
│   └── strategy/       # 策略页 - 策略管理
├── utils/
│   ├── api.js          # API 请求封装
│   ├── websocket.js    # WebSocket 管理
│   └── storage.js      # 本地存储封装
├── app.js              # 小程序入口
├── app.json            # 全局配置
├── app.wxss            # 全局样式
└── config.js           # 配置文件
```

## 与后端配合

本小程序需要配合后端服务使用，后端地址通过 `config.js` 配置：

```javascript
const config = {
  API_BASE: 'http://localhost:8001/api',
  WS_URL: 'ws://localhost:8001/ws'
};
```

确保后端服务（FastAPI）已启动且可访问。

## 开发配置

### 开发环境要求
- 微信开发者工具
- 后端服务已启动（`python start.py`）

### 小程序开发设置
1. 打开微信开发者工具
2. 选择"小程序"项目
3. 导入 `miniprogram` 目录
4. 开启"不校验合法域名"选项（开发阶段）
5. 开始调试

### 网络配置

**开发环境**：
- 勾选"详情"->"本地设置"->"不校验合法域名"
- 确保手机和电脑在同一局域网（真机调试时）

**生产环境**：
- 小程序后台配置 request 合法域名
- 配置 socket 合法域名（WebSocket）
- 后端使用 HTTPS

## 使用说明

### 首页使用
1. 在搜索栏输入股票代码（如：000001.SZ）或名称
2. 查看临界价格触发矩阵
3. 关注共振区间提示
4. 下拉可刷新数据

### 策略页使用
1. 点击"新建策略"创建交易计划
2. 选择股票和预设场景
3. 系统计算可行价格区间
4. 每日使用"检查"功能查看策略可行性
5. 满足条件时执行入场/出场

## API 接口

小程序调用后端以下接口：

| 接口 | 说明 |
|------|------|
| POST /api/matrix/auto/{symbol} | 自动计算临界价格矩阵 |
| GET /api/current-price/{symbol} | 获取当前价格 |
| GET /api/search | 搜索股票 |
| GET /api/filter/scenarios | 获取预设场景 |
| POST /api/filter/quick/{symbol} | 快速筛选 |
| WS /ws | WebSocket 实时推送 |

## 注意事项

1. **Token 配置**：确保后端 `.env` 文件配置了有效的 Tushare Token
2. **网络权限**：真机调试需要开启网络权限
3. **WebSocket**：实时推送需要保持 WebSocket 连接
4. **本地存储**：策略数据存储在本地，换设备需重新创建

## 项目文件清单

### 核心文件
- `app.js` - 小程序入口，全局状态管理
- `app.json` - 页面路由和全局配置
- `app.wxss` - 全局样式变量
- `config.js` - API 地址等配置

### 工具层
- `utils/api.js` - 封装所有后端 API 调用
- `utils/websocket.js` - WebSocket 连接管理
- `utils/storage.js` - 本地存储封装

### 页面
- `pages/index/index.js/wxml/wxss/json` - 首页
- `pages/strategy/strategy.js/wxml/wxss/json` - 策略页

## 开源协议

MIT License
