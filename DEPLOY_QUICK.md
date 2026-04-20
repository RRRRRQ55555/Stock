# 🚀 30 秒快速部署指南

## ✅ 前置条件
- GitHub 账户（免费注册：https://github.com/signup）
- Vercel 账户（用 GitHub 登录：https://vercel.com）

## 📋 3 步完成

### 1️⃣ **推送代码到 GitHub**

```powershell
cd "e:\RQ\龙虾\Stock\stock_assistant"
git init
git add .
git commit -m "Stock technical indicator tool"
git remote add origin https://github.com/YOUR_USERNAME/stock-assistant.git
git branch -M main
git push -u origin main
```

### 2️⃣ **在 Vercel 导入**

1. 打开 https://vercel.com
2. 点击 "Add New" → "Project"
3. 选择你的 `stock-assistant` 仓库

### 3️⃣ **配置部署**

| 设置项 | 值 |
|--------|-----|
| Root Directory | `frontend` |
| Build Command | `npm run build` |
| Output Directory | `dist` |

**点击 Deploy** ✅

---

## 🎉 完成！

你的应用会在这个 URL 上线：
```
https://stock-assistant-[随机].vercel.app
```

分享这个 URL 给评审者！

---

## 需要帮助？

详见：[DEPLOY_VERCEL.md](./DEPLOY_VERCEL.md)

