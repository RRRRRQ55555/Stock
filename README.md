# 股票助手 (Stock Assistant)

一个基于技术指标的股票分析小程序，提供实时策略提醒和买卖信号。

## 功能特性

### 技术指标分析
- **MACD**: DIF、DEA、柱状图、金叉/死叉信号
- **均线 (MA)**: 5日/10日均线、多头排列/空头排列检测
- **KDJ**: K、D、J值计算，超买超卖信号
- **实时计算**: 基于历史数据计算触发价格

### 策略系统
- **买入策略**: 自定义技术指标组合条件
- **止损策略**: 技术指标止损或固定比例止损
- **实时匹配**: 根据当前价格自动匹配策略条件
- **价格区间**: 计算满足策略的价格区间

### 实时数据
- **WebSocket**: 实时推送股票价格更新
- **智能提醒**: 策略条件满足时自动提醒
- **策略看板**: 直观显示当前策略匹配状态

## 技术架构

### 后端
- **框架**: FastAPI + Python 3.11
- **数据源**: AKShare (A股数据)
- **计算引擎**: 自定义指标求解器
- **实时通信**: WebSocket

### 前端
- **平台**: 微信小程序
- **样式**: WXSS (优化后的专业金融设计系统)

## 快速开始 - 本地运行

### 系统要求

- **Node.js** v18 或更高版本
- **Python** 3.8 或更高版本  
- **Git** 最新版本

### 📋 运行步骤（重要：按顺序执行）

#### 第 1 步：克隆项目

```bash
git clone https://github.com/RRRRRQ55555/Stock.git
cd Stock/stock_assistant
```

#### 第 2 步：安装依赖

**安装前端依赖：**
```bash
cd frontend
npm install
cd ..
```

**安装后端依赖：**
```bash
cd backend
pip install -r requirements.txt
cd ..
```

#### 第 3 步：启动后端（第一个终端）

⚠️ **重要：先启动后端！**

```bash
cd backend
python app/main.py
```

**预期输出：**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

✅ 后端运行在 `http://localhost:8000`

#### 第 4 步：启动前端（第二个终端）

⚠️ **只有在后端成功启动后，才启动前端！**

打开**新的**命令行窗口，然后运行：

```bash
cd frontend
npm run dev
```

**预期输出：**
```
VITE v5.0.0  ready in 123 ms

➜  Local:   http://localhost:3000/
```

✅ 前端运行在 `http://localhost:3000`

#### 第 5 步：打开应用

在浏览器中打开：
```
http://localhost:3000
```

🎉 应用已启动！现在可以开始使用所有功能。

### ⚠️ 执行顺序提醒

```
【终端 1】启动后端 (8000 端口)
     ↓
 [等待 "Application startup complete" 消息]
     ↓
【终端 2】启动前端 (3000 端口)
     ↓
【浏览器】打开 http://localhost:3000
     ↓
✅ 应用可用
```

**如果顺序错误，前端无法连接后端！**

---

## 部署指南

### 在线应用

**无需安装，直接使用：**
```
https://stocktwo.vercel.app
```

### 后端部署

```bash
# 1. 安装依赖
cd backend
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置你的 API Key

# 3. 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 或使用 Docker
docker-compose up -d
```

### 小程序发布

1. 在微信开发者工具中导入 `miniprogram` 目录
2. 修改 `utils/api.js` 中的 API 地址为你的服务器地址
3. 点击「上传」提交审核
4. 审核通过后发布

---

## 项目结构

```
stock_assistant/
├── frontend/             # React 前端应用
│   ├── src/
│   │   ├── components/   # React 组件
│   │   ├── services/     # API 服务
│   │   ├── hooks/        # 自定义 hooks
│   │   ├── App.tsx       # 主应用
│   │   └── main.tsx      # 入口
│   ├── dist/             # 编译输出
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── backend/              # FastAPI 后端服务
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── core/         # 核心算法
│   │   ├── services/     # 业务逻辑
│   │   ├── models/       # 数据模型
│   │   └── main.py       # 入口
│   ├── requirements.txt
│   └── .env.example
├── miniprogram/          # 微信小程序
│   ├── pages/            # 页面
│   ├── utils/            # 工具函数
│   ├── app.js
│   └── app.json
├── vercel.json           # Vercel 部署配置
├── QUICK_DEMO_GUIDE.md   # 快速运行指南
├── README.md             # 本文件
└── ...其他文件
```

---


## 核心算法

### MACD 求解器
使用线性回归计算 DIF 和 Signal 的历史趋势，求解金叉/死叉的触发价格。

### 均线求解器
基于价格序列的数学关系，计算满足均线条件的目标价格。

### 策略引擎
多条件筛选器，计算满足所有技术指标条件的"共振价格区间"。

## 设计系统

采用专业金融应用设计系统：
- **颜色**: 专业深蓝配色 + A股红绿涨跌色
- **排版**: 等宽数字字体确保价格对齐
- **交互**: 微交互动画提升体验
- **无障碍**: 支持减少动画偏好

## License

MIT License
