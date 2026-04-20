# 📊 股票技术指标前置预判工具

> 通过反向数学推导计算技术指标临界价格，提前布局交易机会

## 🎯 核心功能

- 📈 **临界价格计算** - 自动计算技术指标触发价格
- 🎨 **触发矩阵展示** - 可视化多指标状态矩阵
- ⚠️ **实时价格预警** - WebSocket 实时推送
- 🔍 **股票搜索** - 支持 5491 只 A 股查询
- 📊 **压力测试** - 假设价格下的指标分析
- 🌐 **共振区间** - 多指标共同触发的价格区间

## 🚀 一键在线部署

### **最简单的方式：Vercel 部署**

只需 3 步，5 分钟获得可分享的 URL！

```powershell
# 1. 推送到 GitHub
git init
git add .
git commit -m "Stock technical indicator tool"
git remote add origin https://github.com/YOUR_USERNAME/stock-assistant.git
git branch -M main
git push -u origin main

# 然后访问 Vercel 导入项目
# https://vercel.com → Import → 选择仓库 → Deploy
```

**配置信息**：
- Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `dist`

部署完成后，你会获得一个 URL 如：
```
https://stock-assistant-xyz.vercel.app
```

✅ **分享这个 URL 给评审者！**

详见：[DEPLOY_QUICK.md](./DEPLOY_QUICK.md) | [DEPLOY_VERCEL.md](./DEPLOY_VERCEL.md)

---

## 💻 本地开发

### 启动方式

**方式 1：开发模式**
```powershell
# 终端 1 - 后端
cd stock_assistant
python start_backend.py

# 终端 2 - 前端
cd stock_assistant/frontend
$env:PATH = "D:\NodeJS;$env:PATH"
npm install
npm run dev
```

访问：http://localhost:3000

**方式 2：生产模式**
```powershell
# 编译前端
cd stock_assistant/frontend
npm run build

# 启动后端（会提供编译后的前端文件）
cd ..
python start_backend.py
```

访问：http://localhost:8000

---

## 📦 项目结构

```
stock-assistant/
├── frontend/                      # React 前端
│   ├── src/
│   │   ├── components/           # React 组件
│   │   ├── services/             # API 服务
│   │   ├── types/                # TypeScript 类型
│   │   └── main.tsx
│   ├── dist/                     # 编译输出（可部署）
│   ├── index.html                # 入口 HTML
│   ├── vite.config.ts            # Vite 配置
│   └── package.json
├── backend/                       # FastAPI 后端
│   ├── app/
│   │   ├── api/                  # API 路由
│   │   ├── core/                 # 指标计算引擎
│   │   ├── services/             # 业务服务
│   │   └── main.py
│   ├── requirements.txt
│   └── .env                      # 环境变量
├── start_backend.py              # 后端启动脚本
├── vercel.json                   # Vercel 配置
└── README.md                     # 本文件
```

---

## 🔧 技术栈

**前端**：
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Axios
- Recharts

**后端**：
- FastAPI
- Uvicorn
- Pandas / NumPy
- Tushare / Yahoo Finance

---

## 📈 支持的技术指标

- MACD（移动平均线聚散指数）
- KDJ（随机指数）
- RSI（相对强弱指数）
- 布林带（Bollinger Bands）
- ATR（平均真实波幅）
- ADX（平均方向指数）
- CCI（商品路径指数）
- 移动平均线（MA）
- 还有 20+ 其他指标...

---

## 🌐 API 文档

后端运行时访问：http://localhost:8000/docs

主要端点：
- `GET /api/search?query={symbol}` - 搜索股票
- `POST /api/matrix/auto/{symbol}` - 计算临界矩阵
- `POST /api/stress-test` - 压力测试
- `WS /ws` - WebSocket 实时数据

---

## ⚙️ 环境配置

### Tushare Token（可选）

为了获得更好的数据源，配置 Tushare Token：

1. 访问 https://tushare.pro 注册
2. 获取你的 Token
3. 在 `backend/.env` 中添加：
   ```
   TUSHARE_TOKEN=你的_token
   ```

默认使用 Yahoo Finance 作为后备数据源。

---

## 🚀 部署选项

| 平台 | 费用 | 适用场景 | 难度 |
|------|------|--------|------|
| **Vercel** | 免费 | 前端静态网站 | ⭐ 最简单 |
| **Railway** | 免费/付费 | 前端+后端 | ⭐⭐⭐ |
| **Render** | 免费/付费 | 前端+后端 | ⭐⭐ |
| **Docker** | 自助 | 本地/云服务器 | ⭐⭐⭐⭐ |

推荐新手使用 **Vercel**（仅前端）。

---

## 📝 快速参考

```bash
# 安装依赖
npm install --prefix frontend
pip install -r backend/requirements.txt

# 开发构建
npm run dev --prefix frontend

# 生产构建
npm run build --prefix frontend

# 启动后端
python start_backend.py

# 运行测试
npm test --prefix frontend
```

---

## 🐛 常见问题

**Q: 如何只部署前端？**
A: 使用 Vercel（推荐）。详见 [DEPLOY_QUICK.md](./DEPLOY_QUICK.md)

**Q: 如何部署完整应用？**
A: 需要部署后端到 Railway/Render。详见 [DEPLOY_VERCEL.md](./DEPLOY_VERCEL.md)

**Q: 一直"加载中"怎么办？**
A: 这是 API 限流问题。配置 Tushare Token 或等待几分钟后重试。

**Q: 如何修改数据源？**
A: 编辑 `backend/app/services/data_service.py`，修改数据获取逻辑。

---

## 📞 支持

遇到问题？

1. 查看 [DEPLOY_VERCEL.md](./DEPLOY_VERCEL.md) 详细说明
2. 检查后端日志输出
3. 打开浏览器开发者工具（F12）查看前端错误

---

## 📄 许可证

MIT License - 自由使用和修改

---

## 🎯 下一步

1. ✅ [本地测试应用](http://localhost:3000)
2. ✅ [部署到 Vercel](./DEPLOY_QUICK.md)
3. ✅ [分享你的 URL](https://vercel.com)

**让我们开始吧！** 🚀

