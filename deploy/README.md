# 阿里云服务器部署指南

## 📋 前提条件

- 阿里云ECS实例（建议配置：2核4G，CentOS 8/Ubuntu 20.04）
- 已配置安全组（开放80/443/8000端口）
- 拥有服务器root或sudo权限
- 本地开发环境已验证通过

## 🔧 服务器环境配置

### 1. 连接服务器

```bash
ssh root@your_server_ip
```

### 2. 系统更新

```bash
# CentOS
yum update -y

# Ubuntu
apt update && apt upgrade -y
```

### 3. 安装Python环境

```bash
# 安装Python 3.11
yum install -y python3.11 python3.11-pip git

# 或使用conda安装
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc
conda create -n stock python=3.11
conda activate stock
```

### 4. 安装Nginx

```bash
# CentOS
yum install -y nginx

# Ubuntu
apt install -y nginx

# 启动Nginx
systemctl start nginx
systemctl enable nginx
```

## 📦 代码部署

### 1. 上传代码到服务器

**方式A：使用Git（推荐）**

```bash
cd /opt
git clone https://github.com/yourusername/stock_assistant.git
# 或者使用SSH密钥
```

**方式B：使用scp本地上传**

```bash
# 在本地PowerShell执行
scp -r d:\stock_assistant\backend root@your_server_ip:/opt/stock_assistant/
```

### 2. 安装依赖

```bash
cd /opt/stock_assistant/backend
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
nano .env
```

编辑 `.env` 文件：
```env
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
TUSHARE_TOKEN=your_actual_token_here
CACHE_DIR=./cache
CACHE_TTL=3600
ALERT_PROXIMITY_THRESHOLD=1.0
ALERT_MIN_INTERVAL=300
MACD_FAST_PERIOD=12
MACD_SLOW_PERIOD=26
MACD_SIGNAL_PERIOD=9
MA_SHORT_PERIOD=5
MA_LONG_PERIOD=10
KDJ_PERIOD=9
```

**⚠️ 重要：务必替换TUSHARE_TOKEN为真实token！**

## ⚙️ 服务配置

### 1. 创建systemd服务

```bash
cp /opt/stock_assistant/deploy/stock-backend.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable stock-backend
systemctl start stock-backend
```

查看服务状态：
```bash
systemctl status stock-backend
journalctl -u stock-backend -f  # 查看日志
```

### 2. 配置Nginx反向代理

```bash
cp /opt/stock_assistant/deploy/nginx-stock.conf /etc/nginx/conf.d/
nginx -t  # 测试配置
systemctl reload nginx
```

## 🔒 安全配置

### 1. 防火墙配置

```bash
# 开放必要端口
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --reload
```

### 2. 配置HTTPS（可选但推荐）

使用Let's Encrypt免费证书：

```bash
yum install -y certbot python3-certbot-nginx
# 或
apt install -y certbot python3-certbot-nginx

# 申请证书
certbot --nginx -d your-domain.com
```

## 🧪 验证部署

### 1. 测试后端API

```bash
curl http://your_server_ip:8000/api/health
curl http://your_server_ip:8000/api/matrix/auto/000001.SS
```

### 2. 更新小程序配置

修改 `miniprogram/config.js`：
```javascript
const config = {
  API_BASE: 'http://your_server_ip:8000/api',  // 或你的域名
  WS_URL: 'ws://your_server_ip:8000/ws',
  // ...
};
```

在微信开发者工具中重新编译测试。

## 🔄 更新部署

当代码更新时，执行：

```bash
cd /opt/stock_assistant
git pull origin main  # 如果使用git
systemctl restart stock-backend
```

## 📊 监控与日志

### 查看服务日志
```bash
journalctl -u stock-backend -f
```

### 查看Nginx日志
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 性能监控
```bash
# 查看CPU/内存
htop

# 查看端口占用
netstat -tlnp | grep 8000
```

## 🆘 故障排查

### 服务启动失败
1. 检查日志：`journalctl -u stock-backend -n 50`
2. 检查端口占用：`lsof -i :8000`
3. 检查环境变量：`cat /opt/stock_assistant/backend/.env`

### WebSocket连接失败
1. 检查Nginx配置是否包含WebSocket支持
2. 检查防火墙是否开放端口
3. 检查小程序配置中的WS_URL

### API响应慢
1. 检查服务器带宽和延迟
2. 检查Tushare API调用频率
3. 查看是否有大量并发连接

## 📞 联系方式

部署过程中遇到问题：
1. 查看服务日志
2. 检查阿里云安全组配置
3. 确认Tushare token有效
