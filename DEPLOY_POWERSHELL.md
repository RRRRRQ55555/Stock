# PowerShell 部署脚本使用指南

## 🚀 快速开始

### 方法 1：直接运行脚本（推荐）

1. **打开 PowerShell**
   - 按 `Windows + R`
   - 输入 `powershell`
   - 按 Enter

2. **进入项目目录**
   ```powershell
   cd "e:\RQ\龙虾\Stock\stock_assistant"
   ```

3. **临时允许脚本执行（仅此会话）**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
   ```

4. **运行部署脚本**
   ```powershell
   .\deploy.ps1
   ```

### 方法 2：手动执行命令

如果脚本执行遇到问题，复制以下命令逐行执行：

```powershell
# 1. 设置 Git 路径
$env:PATH = "D:\GIT\Git\bin;$env:PATH"

# 2. 进入项目目录
cd "e:\RQ\龙虾\Stock\stock_assistant"

# 3. 初始化 Git
git init

# 4. 配置用户信息
git config user.email "submission@example.com"
git config user.name "Stock Assistant Developer"

# 5. 添加所有文件
git add .

# 6. 提交代码
git commit -m "Stock technical indicator tool - ready for submission"

# 7. 添加远程仓库（替换 YOUR_REPO_URL）
git remote add origin YOUR_REPO_URL

# 8. 推送到 GitHub
git branch -M main
git push -u origin main
```

## 📋 前置准备

在运行脚本之前，确保完成：

- ✅ Git 已安装到 D:\GIT\Git
- ✅ Node.js 已安装到 D:\NodeJS
- ✅ 前端已编译（dist/ 文件夹存在）
- ✅ 有 GitHub 账户

## 🔑 GitHub 仓库 URL 格式

当脚本要求输入 URL 时，使用以下格式：

```
https://github.com/YOUR_USERNAME/stock-assistant.git
```

例如：
```
https://github.com/alice/stock-assistant.git
```

## ⚠️ 常见问题

### 问题 1：认证失败 / 推送被拒绝

**原因**：GitHub 账户未认证

**解决方案**：
1. 打开 https://github.com/settings/tokens/new
2. 勾选 `repo` 权限
3. 生成 token
4. 当 Git 要求密码时，粘贴 token 而不是密码

### 问题 2："执行策略不允许运行脚本"

**解决方案**：使用方法 1 中的第 3 步允许脚本执行

### 问题 3：仍然收到 Git 命令不存在

**解决方案**：手动指定完整路径
```powershell
& "D:\GIT\Git\bin\git.exe" --version
```

## 📱 之后的步骤

1. **确认 GitHub 推送成功**
   - 访问 https://github.com/YOUR_USERNAME/stock-assistant
   - 应该能看到所有文件

2. **部署到 Vercel**
   - 访问 https://vercel.com
   - 用 GitHub 登录
   - 点击 "Add New" → "Project"
   - 选择 "stock-assistant"
   - Root Directory 设置为 `frontend`
   - 点击 Deploy

3. **获取分享链接**
   - Vercel 会自动生成 URL
   - 例如：https://stock-assistant.vercel.app
   - 这就是你要提交给评审者的链接！

## 📞 获取帮助

如有问题，检查：
1. `deploy.ps1` 中的所有文件路径是否正确
2. Git 是否确实安装在 D:\GIT\Git
3. 网络连接是否正常

---

**✨ 一切就绪！现在可以开始部署了。**
