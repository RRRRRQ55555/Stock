# 📱 部署到 Vercel - 详细步骤

## 🎯 目标
将 React 前端应用部署到 Vercel，获得可分享的 URL

## ✅ 已完成
- ✓ 前端代码已编译到 `frontend/dist/`
- ✓ TypeScript 配置已修复
- ✓ `index.html` 入口文件已创建
- ✓ `vercel.json` 配置已添加

---

## 🚀 部署流程（3 步，10 分钟）

### **第 1 步：推送代码到 GitHub**

```powershell
# 打开 PowerShell，进入项目目录
cd "e:\RQ\龙虾\Stock\stock_assistant"

# 初始化 Git（如果还没有）
git init
git config user.email "你的邮箱@example.com"
git config user.name "你的名字"

# 添加所有文件
git add .

# 提交
git commit -m "Stock technical indicator tool - ready for deployment"

# 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/stock-assistant.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

**如果还没有 GitHub 账户**：
1. 访问 https://github.com/signup
2. 注册账户
3. 创建新仓库 `stock-assistant`

### **第 2 步：连接 Vercel**

1. **访问 Vercel**：https://vercel.com
2. **注册/登录**：选择 "Sign Up with GitHub"
3. **授权 GitHub**：允许 Vercel 访问你的账户
4. **导入项目**：
   - 点击 "Add New..."
   - 选择 "Project"
   - 选择 `stock-assistant` 仓库

### **第 3 步：配置构建设置**

在 Vercel 的项目导入页面，填写：

| 字段 | 值 |
|------|-----|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

**点击 "Deploy"** ✅

---

## 🌐 获得你的 URL

部署完成后，Vercel 会给你一个 URL，类似：
```
https://stock-assistant-xyz123.vercel.app
```

这就是你可以分享给评审者的链接！

---

## 🔧 部署后的工作

### 配置 API 基础 URL

前端需要连接到后端 API。有两个选择：

#### **选项 A：使用云端后端（推荐）**

如果你想要完整的在线应用（包括 API），需要同时部署后端。

参考：[部署后端到 Railway](#后端部署到railway)

#### **选项 B：使用本地后端（仅测试用）**

```javascript
// 在 frontend/src/services/api.ts
const API_BASE = process.env.VITE_API_BASE || 'http://localhost:8000';
```

---

## 🐍 后端部署到 Railway（可选）

如果想要完整的在线应用：

### 1. 创建 Railway 账户

访问 https://railway.app，用 GitHub 登录

### 2. 创建新项目

点击 "New Project" → "Deploy from GitHub"

### 3. 配置后端

选择你的 `stock-assistant` 仓库，Railway 会自动检测 Python 项目

### 4. 环境变量

添加到 Railway：
```
TUSHARE_TOKEN=你的_TUSHARE_TOKEN
```

### 5. 启动命令

```
python start_backend.py
```

### 6. 获得后端 URL

Railway 会提供类似：
```
https://stock-assistant-backend.railway.app
```

### 7. 更新前端配置

在 Vercel 项目设置中，添加环境变量：
```
VITE_API_BASE=https://stock-assistant-backend.railway.app
```

---

## ✨ 最终结果

访问你的 Vercel 应用 URL，应该能看到：

1. ✅ 技术指标前置预判工具界面
2. ✅ 股票搜索功能
3. ✅ 触发矩阵显示
4. ✅ 实时数据更新

---

## 🐛 常见问题

### Q: "Build failed" 错误？

**A:** 检查：
1. 前端 `dist/` 目录是否存在
2. `vercel.json` 配置是否正确
3. 清空 Vercel 缓存后重新部署

### Q: 前端能访问但数据不显示？

**A:** 这是因为：
- API 还没部署（选项 B）
- 或者 CORS 未配置

解决：部署后端或使用本地后端

### Q: 如何更新已部署的应用？

**A:** 推送新的 commit 到 GitHub 即可：

```powershell
git add .
git commit -m "Update message"
git push origin main
```

Vercel 会自动重新部署！

---

## 📚 完整项目文件清单

需要提交给评审者的：

```
stock-assistant/
├── frontend/
│   ├── src/                    # React 源代码
│   ├── dist/                   # 编译后的静态文件 ✓
│   ├── index.html              # 入口 HTML ✓
│   ├── package.json            # 依赖配置
│   ├── vite.config.ts          # Vite 构建配置
│   └── tsconfig.json           # TypeScript 配置
├── backend/                    # FastAPI 后端（可选部署）
├── vercel.json                 # Vercel 配置 ✓
├── package.json
├── requirements.txt
└── README.md
```

---

## 🎓 你现在拥有：

✅ **可在线访问的产品** - 完整的URL
✅ **可分享的链接** - 直接给评审者
✅ **完全免费** - Vercel 提供免费托管
✅ **自动更新** - 推送代码即自动重新部署
✅ **HTTPS 安全** - 自动配置 SSL 证书

---

## 🚀 总结

1. 推送代码到 GitHub
2. 在 Vercel 导入项目
3. 配置 Root Directory 为 `frontend`
4. 点击 Deploy
5. 获得你的 URL！

就这么简单！ 🎉

