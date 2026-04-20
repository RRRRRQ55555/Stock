# 🔧 部署故障排除指南

## 当前状态

✅ **本地代码已成功提交** 
- ✓ Git 初始化完成
- ✓ 所有文件已暂存（staged）
- ✓ 代码已本地提交（local commit）
- ✓ 已连接到 GitHub 远程仓库

⏳ **待推送到 GitHub**
- 等待网络连接恢复

---

## 🌐 网络连接问题排查

### 症状
```
fatal: unable to access 'https://github.com/...': Failed to connect
```

### 解决方案

#### 1️⃣ 检查网络连接
```powershell
# 测试 GitHub 连接
ping github.com

# 或者测试 DNS
nslookup github.com
```

#### 2️⃣ 如果 DNS 有问题，尝试换 DNS
```powershell
# 临时使用 Google DNS
# 进入 Windows 网络设置，或运行：
ipconfig /all
```

#### 3️⃣ 检查 Git 配置
```powershell
$env:PATH = "D:\GIT\Git\bin;$env:PATH"
cd "e:\RQ\龙虾\Stock\stock_assistant"

# 查看远程仓库配置
git remote -v

# 应该显示：
# origin  https://github.com/WhatsTheMatterrr/stock-assistant.git (fetch)
# origin  https://github.com/WhatsTheMatterrr/stock-assistant.git (push)
```

#### 4️⃣ 尝试重新连接
```powershell
$env:PATH = "D:\GIT\Git\bin;$env:PATH"
cd "e:\RQ\龙虾\Stock\stock_assistant"

# 第一步：看看是否能 fetch
git fetch origin

# 如果可以 fetch，则推送
git push origin main
```

---

## 📋 当网络恢复后的推送步骤

### 方式 1：使用 PowerShell（推荐）

```powershell
# 1. 添加 Git 到 PATH
$env:PATH = "D:\GIT\Git\bin;$env:PATH"

# 2. 进入项目目录
cd "e:\RQ\龙虾\Stock\stock_assistant"

# 3. 确认本地提交（应该看到本地领先 origin）
git status

# 4. 推送到 GitHub
git push origin main

# 5. 验证成功
git log --oneline -5
```

### 方式 2：使用 Batch 脚本

如果你已经创建了 `deploy.bat`：
```batch
cd /d "e:\RQ\龙虾\Stock\stock_assistant"
deploy.bat
```

---

## 🔍 验证推送是否成功

### 本地验证
```powershell
$env:PATH = "D:\GIT\Git\bin;$env:PATH"
cd "e:\RQ\龙虾\Stock\stock_assistant"

# 应该显示 "已经最新"
git status

# 应该显示本地提交已推送
git log -1
```

### 在 GitHub 网站验证

1. 打开 https://github.com/RRRRRQ55555/stock-assistant
2. 应该能看到所有文件和最新提交信息
3. 提交信息应该包含："Add PowerShell deployment scripts and documentation"

---

## 💡 替代方案（如果 HTTPS 推送持续失败）

### 方案 A：使用 SSH（更稳定）

```powershell
# 1. 生成 SSH 密钥（如果还没有）
ssh-keygen -t ed25519 -C "your_github_email@example.com"

# 2. 将公钥添加到 GitHub
#    打开 C:\Users\YOUR_USERNAME\.ssh\id_ed25519.pub
#    复制内容，粘贴到 https://github.com/settings/keys

# 3. 测试连接
ssh -T git@github.com

# 4. 更改远程 URL 为 SSH
git remote set-url origin git@github.com:WhatsTheMatterrr/stock-assistant.git

# 5. 推送
git push origin main
```

### 方案 B：使用 GitHub CLI（最简单）

```powershell
# 1. 安装 GitHub CLI（使用 Chocolatey 或从 https://cli.github.com 下载）
# choco install gh

# 2. 登录 GitHub
gh auth login

# 3. 推送
git push origin main
```

---

## 🚨 本地代码安全

你的代码已经保存在本地提交中。即使推送失败，数据也不会丢失。

### 查看本地提交
```powershell
$env:PATH = "D:\GIT\Git\bin;$env:PATH"
cd "e:\RQ\龙虾\Stock\stock_assistant"

# 查看最新 5 个提交
git log --oneline -5
```

### 查看最新提交内容
```powershell
# 查看刚刚添加的文件
git show HEAD --stat
```

---

## 📞 下一步

一旦 GitHub 推送成功（您会看到这样的输出）：

```
To https://github.com/WhatsTheMatterrr/stock-assistant.git
   abc1234..def5678  main -> main
```

就可以进行 **Vercel 部署**：

1. 打开 https://vercel.com
2. 用 GitHub 账户登录
3. 点击 "Add New" → "Project"
4. 选择 "stock-assistant" 仓库
5. 根目录设置为 `frontend`
6. 点击 Deploy

---

**⏳ 等待网络恢复后，请再次尝试 `git push origin main` 命令。**
