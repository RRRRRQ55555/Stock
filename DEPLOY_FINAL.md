# 🎯 最终部署指南 - Vercel 直接部署

你已经准备好了！现在只需要两个简单的步骤就能上线。

---

## ✅ 方式选择

你有两种部署方式可选：

### 方式 A️⃣：使用 PowerShell 命令（推荐）

```powershell
$env:PATH = "D:\NodeJS;$env:PATH"
cd "e:\RQ\龙虾\Stock\stock_assistant"
npx vercel --prod
```

### 方式 B️⃣：使用部署脚本

直接双击运行：
```
vercel_deploy.bat
```

---

## 🚀 2 步快速部署

### 第 1️⃣ 步：首次登录 Vercel

如果这是你第一次使用 Vercel CLI，需要登录：

```powershell
$env:PATH = "D:\NodeJS;$env:PATH"
cd "e:\RQ\龙虾\Stock\stock_assistant"
npx vercel login
```

**说明**：
1. 选择登录方式（推荐用 GitHub）
2. 浏览器会打开认证页面
3. 完成后返回 PowerShell

### 第 2️⃣ 步：部署应用

```powershell
$env:PATH = "D:\NodeJS;$env:PATH"
cd "e:\RQ\龙虾\Stock\stock_assistant"
npx vercel --prod
```

**会问几个问题**，按照下面的回答：

```
? Set up and deploy "stock_assistant"? (Y/n)
→ y

? Which scope should we deploy to?
→ 选择你的用户名

? Link to existing project? (y/N)
→ N (选择 N 创建新项目)

? What's your project's name?
→ stock-assistant （或任意名称）

? In which directory is your code located?
→ . （当前目录）

? Want to modify these settings before deploying? (y/N)
→ N
```

---

## 🎉 完成！

部署完成后，你会看到：

```
✓ Production: https://stock-assistant-XXXXX.vercel.app
✓ Deployment Successful!
```

**这就是你的最终 URL！** 可以分享给任何人。

---

## 📊 预期时间

```
第一次部署:
1. 登录 Vercel        ~ 1 分钟
2. 部署应用           ~ 1 分钟
──────────────────────────────
总计                  ~ 2 分钟

之后的部署:
1. 运行部署命令       ~ 1 分钟
```

---

## ✨ 优点

✅ **无需 GitHub** - 直接部署，跳过 Git 推送
✅ **超快** - 2 分钟就能上线
✅ **自动配置** - Vercel 自动检测 React 项目
✅ **免费** - Vercel 对个人项目免费

---

## 🔍 部署后验证

打开你的 Vercel URL，检查：

- [ ] 页面能正常加载
- [ ] 能搜索股票（如：600000）
- [ ] 技术指标正常显示
- [ ] 没有控制台错误

---

## 💡 常见问题

### Q: 可以部署多次吗？
**A**: 可以！每次修改代码后都可以重新运行部署命令。

### Q: 如何更新应用？
```powershell
# 编辑代码 → 构建 → 重新部署
npm run build --prefix frontend
npx vercel --prod
```

### Q: 能回滚到之前的版本吗？
**A**: 可以。在 Vercel 仪表板上查看部署历史并回滚。

### Q: 如何添加自定义域名？
**A**: 在 Vercel 项目设置中添加 DNS 记录。

---

## 📋 完整步骤总结

```
第 1 次部署:
1. npx vercel login              (登录)
2. npx vercel --prod              (部署)
3. 回答几个配置问题              (自动填充默认值)
4. 获得 URL                        (完成！)

后续部署:
1. npx vercel --prod              (就这一个命令)
```

---

## 🎯 现在就开始

### 打开 PowerShell，复制粘贴：

```powershell
$env:PATH = "D:\NodeJS;$env:PATH"; cd "e:\RQ\龙虾\Stock\stock_assistant"; npx vercel login
```

登录完成后，运行：

```powershell
$env:PATH = "D:\NodeJS;$env:PATH"; cd "e:\RQ\龙虾\Stock\stock_assistant"; npx vercel --prod
```

**就这样！** 2 分钟后你就有一个在线应用了！

---

## 🎊 完成后

1. ✅ 复制你的 Vercel URL
2. ✅ 分享给评审者
3. ✅ 项目完成！

**恭喜！** 你的股票技术指标工具已经上线！ 🚀

