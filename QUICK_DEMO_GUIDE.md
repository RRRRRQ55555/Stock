# 🚀 快速运行演示指南

> 股票技术指标前置预判工具 - 完整运行手册

---

## 📌 目录

1. [在线演示](#在线演示)
2. [本地运行](#本地运行)
3. [从 GitHub 下载](#从-github-下载)
4. [常见问题](#常见问题)

---

## 🌐 在线演示

### 最快的方式 - 直接打开

**无需下载或安装，打开即用：**

👉 **https://stocktwo.vercel.app**

### 功能演示

点击打开后，你可以：

1. **搜索股票**
   - 输入股票代码（如：`600000`、`000001`）
   - 按 Enter 搜索
   - 显示实时股票数据

2. **查看技术指标**
   - 自动显示主要技术指标
   - 包括：移动平均线、MACD、RSI 等
   - 实时更新数据

3. **分析工具**
   - 矩阵分析
   - 技术指标自动诊断
   - 交互式图表

---

## 💻 本地运行

### 前置要求

在运行本地项目前，确保已安装：

- **Node.js** (v18+)：https://nodejs.org
- **Python** (v3.8+)：https://python.org
- **Git**：https://git-scm.com

### 第 1 步：从 GitHub 下载项目

#### 方法 A：使用 Git 克隆（推荐）

```bash
git clone https://github.com/RRRRRQ55555/Stock.git
cd Stock/stock_assistant
```

#### 方法 B：直接下载 ZIP

1. 打开：https://github.com/RRRRRQ55555/Stock
2. 点击 "Code" → "Download ZIP"
3. 解压文件
4. 打开命令行进入 `Stock/stock_assistant` 文件夹

---

### 第 2 步：安装前端依赖

进入前端目录：

```bash
cd frontend
npm install
```

等待安装完成...

---

### 第 3 步：安装后端依赖

```bash
cd ../backend
pip install -r requirements.txt
```

如果遇到问题，尝试：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

### 第 4 步：启动后端服务

在 `backend` 目录下运行：

```bash
python start_backend.py
```

或者：

```bash
python app/main.py
```

**预期输出**：

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

✅ 后端已启动在 `http://localhost:8000`

---

### 第 5 步：启动前端应用

打开新的命令行窗口，进入 `frontend` 目录：

```bash
cd frontend
npm run dev
```

**预期输出**：

```
VITE v5.0.0  ready in 123 ms

➜  Local:   http://localhost:3000/
```

✅ 前端已启动在 `http://localhost:3000`

---

### 第 6 步：打开应用

在浏览器中打开：

👉 **http://localhost:3000**

应用已启动！现在可以使用所有功能。

---

## 📥 从 GitHub 下载

### 完整的下载和运行步骤

#### **快速命令（复制粘贴）**

Windows (PowerShell):
```powershell
# 克隆项目
git clone https://github.com/RRRRRQ55555/Stock.git
cd Stock/stock_assistant

# 安装前端
cd frontend
npm install
cd ..

# 安装后端
cd backend
pip install -r requirements.txt
cd ..

# 启动后端（在一个终端）
python backend/app/main.py

# 启动前端（在另一个终端）
cd frontend
npm run dev
```

Mac/Linux:
```bash
# 克隆项目
git clone https://github.com/RRRRRQ55555/Stock.git
cd Stock/stock_assistant

# 安装依赖
cd frontend && npm install && cd ..
cd backend && pip install -r requirements.txt && cd ..

# 启动（需要两个终端）
# 终端 1：
python backend/app/main.py

# 终端 2：
cd frontend && npm run dev
```

---

### 目录结构说明

```
Stock/
├── stock_assistant/              # 主项目目录
│   ├── frontend/                 # React 前端
│   │   ├── src/                  # 源代码
│   │   ├── package.json          # 前端依赖
│   │   └── dist/                 # 构建输出
│   ├── backend/                  # FastAPI 后端
│   │   ├── app/                  # 应用核心
│   │   ├── requirements.txt      # Python 依赖
│   │   └── main.py               # 后端入口
│   ├── README.md                 # 项目说明
│   └── vercel.json               # Vercel 配置
└── ... 其他文件
```

---

## ✅ 验证安装成功

### 检查清单

- [ ] 前端页面成功加载（http://localhost:3000）
- [ ] 能输入股票代码进行搜索
- [ ] 显示技术指标和分析结果
- [ ] 没有红色错误提示
- [ ] 能点击不同的菜单和功能

### 如果有问题

检查：

1. **Node.js 版本**
   ```bash
   node --version  # 应该 >= v18
   ```

2. **Python 版本**
   ```bash
   python --version  # 应该 >= 3.8
   ```

3. **端口占用**
   - 前端需要 3000 端口
   - 后端需要 8000 端口
   - 确保这两个端口未被占用

4. **依赖安装**
   - 前端：`npm install` 完成无误
   - 后端：`pip install -r requirements.txt` 完成无误

---

## 🎯 完整运行时间表

| 步骤 | 时间 | 说明 |
|------|------|------|
| 1. 下载代码 | 2-3 分钟 | Git 克隆或 ZIP 下载 |
| 2. 安装前端依赖 | 3-5 分钟 | npm install |
| 3. 安装后端依赖 | 2-3 分钟 | pip install |
| 4. 启动后端 | 1 分钟 | python 启动 |
| 5. 启动前端 | 1 分钟 | npm run dev |
| 6. 打开应用 | 1 分钟 | 访问 localhost |
| **总计** | **10-15 分钟** | **首次运行** |

后续运行只需步骤 4-6，约 3-5 分钟。

---

## 📱 主要功能演示

### 1️⃣ 股票搜索

```
输入：600000
结果：浦发银行
      代码：600000
      实时价格：8.50 元
      涨跌：+2.5%
```

### 2️⃣ 技术指标分析

```
移动平均线 (MA)
- MA5：8.45 元
- MA10：8.32 元
- MA20：8.15 元

MACD 指标
- 快线 (DIF)：0.25
- 慢线 (DEA)：0.18
- 柱状图 (MACD)：0.07

RSI 相对强弱指数
- RSI(14)：62.5
- 状态：中等强度
```

### 3️⃣ 矩阵分析

自动生成技术指标矩阵，显示：
- 强势信号数
- 弱势信号数
- 综合评分

---

## 🔧 常见问题

### Q1：为什么前端启动很慢？

**A**：首次启动 Vite 需要时间编译。后续启动会快得多。

### Q2：无法连接后端？

**A**：
- 确认后端已启动（检查是否有 "Uvicorn running" 信息）
- 检查 8000 端口是否被占用
- 检查防火墙设置

### Q3：股票数据为什么是旧的？

**A**：
- 数据来自 Tushare API（中国股票数据）
- 可能需要配置 API Token
- 参考 `TUSHARE_SETUP.md`

### Q4：能改变 API 地址吗？

**A**：可以。修改 `frontend/.env` 文件：

```
VITE_API_URL=http://你的后端地址:8000
```

### Q5：能在手机上运行吗？

**A**：
- **在线版**：直接打开 https://stocktwo.vercel.app
- **本地版**：需要在同一网络中，改为 `http://你的电脑IP:3000`

---

## 📚 更多资源

| 资源 | 说明 |
|------|------|
| `README.md` | 项目完整说明 |
| `DEPLOY_FINAL.md` | 部署到 Vercel 指南 |
| `backend/` | 后端 API 源代码 |
| `frontend/src/` | 前端 React 源代码 |
| `TUSHARE_SETUP.md` | Tushare API 配置 |

---

## 🎉 现在就开始

### 最快开始方法

1. **在线试用**（推荐）
   ```
   直接打开：https://stocktwo.vercel.app
   ```

2. **本地运行**
   ```
   git clone https://github.com/RRRRRQ55555/Stock.git
   cd Stock/stock_assistant
   # 按照本指南的步骤进行
   ```

---

## 📞 需要帮助？

- 📖 查看 README.md 了解更多细节
- 🔧 查看各个 MD 文件获得特定功能帮助
- 💻 查看源代码了解实现细节

---

**祝你使用愉快！** 🚀

如有问题或建议，欢迎反馈！
