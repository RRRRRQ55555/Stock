# 快速启动指南

## 🎯 5秒快速启动

### Windows 用户

#### 方式 1：双击启动（推荐）

1. 在项目根目录找到 `launch.py`
2. 双击打开
3. 浏览器自动打开 http://localhost:8080

#### 方式 2：命令行启动

打开 PowerShell，输入：
```powershell
cd e:\RQ\龙虾\Stock\stock_assistant
python launch.py
```

#### 方式 3：分开启动

**打开第一个 PowerShell 窗口：**
```powershell
cd e:\RQ\龙虾\Stock\stock_assistant
python start_backend.py
```

**打开第二个 PowerShell 窗口：**
```powershell
cd e:\RQ\龙虾\Stock\stock_assistant
python -m http.server 8080 --directory .
```

## 🌐 访问应用

启动后，在浏览器中打开以下地址：

| 功能 | 地址 |
|------|------|
| **主应用** | http://localhost:8080 |
| **API 文档** | http://localhost:8000/docs |

## 📖 功能说明

### 前端功能
- ✓ 股票代码搜索和选择
- ✓ 实时价格显示
- ✓ 技术指标计算
- ✓ 交易信号提醒
- ✓ 临界价格预测

### 后端功能
- ✓ 股票数据库（5491 只 A 股）
- ✓ 技术指标计算引擎
- ✓ WebSocket 实时推送
- ✓ RESTful API 接口
- ✓ 数据缓存优化

## 🛑 停止服务

在启动的终端窗口中按下：
```
Ctrl + C
```

## 🐛 故障排查

### 问题 1：端口已被占用
```powershell
# 改用其他端口
python -m http.server 8081 --directory .
```

### 问题 2：找不到 Python
- 检查是否已安装 Python 3.7+
- 运行 `python --version` 验证

### 问题 3：依赖缺失
```powershell
# 重新安装依赖
cd backend
pip install -r requirements.txt
```

### 问题 4：后端无法启动
```powershell
# 查看详细错误日志
python start_backend.py  # 不要用 -q 参数
```

## 📱 测试股票代码

在应用中输入以下代码进行测试：

```
600519.SH  - 贵州茅台
000858.SZ  - 五粮液
000651.SZ  - 格力电器
601988.SH  - 中国银行
```

## 🎓 学习资源

- **API 文档**: http://localhost:8000/docs (Swagger UI)
- **源代码**: 查看 `backend/` 和 `frontend/` 目录
- **项目结构**: 查看 README.md

## ✅ 验证安装

运行验证脚本检查系统状态：
```powershell
python verify.py
```

## 💡 提示

- 首次启动会加载所有股票数据（约5-10秒）
- 推荐使用 Chrome/Edge 浏览器
- 前端使用 React 18 + Tailwind CSS
- 后端使用 FastAPI + Uvicorn

## 🚀 下一步

1. **体验功能** - 在主应用中搜索和分析股票
2. **查看 API** - 访问 http://localhost:8000/docs 了解所有接口
3. **阅读文档** - 查看 STRATEGY_LOGIC.md 了解策略逻辑
4. **部署上线** - 使用 Docker 部署到服务器

---

有问题？查看 VERIFICATION_REPORT.md 了解详细信息。
