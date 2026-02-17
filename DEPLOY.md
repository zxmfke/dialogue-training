# 部署指南

## 🚀 方案一：Render 部署（推荐）

### 自动部署（推荐）
1. Fork 本仓库到你的 GitHub 账户
2. 在 Render 创建 Web Service，选择 GitHub 仓库
3. 配置：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
4. 点击 Create，等待部署完成

### 手动部署
1. 访问 https://dashboard.render.com
2. New + → Web Service
3. 选择 GitHub 仓库 `zxmfke/dialogue-training`
4. 配置如上，点击 Create

---

## 🚀 方案二：腾讯云服务器部署（一键脚本）

### 要求
- 腾讯云服务器（1核2G以上）
- Ubuntu 20.04/22.04 或 CentOS 8
- 开放 80 和 8000 端口

### 部署步骤

```bash
# 1. SSH 连接服务器
ssh root@你的服务器IP

# 2. 下载并运行部署脚本
curl -fsSL https://raw.githubusercontent.com/zxmfke/dialogue-training/main/deploy.sh | bash

# 或者手动执行
apt-get update && apt-get install -y git
mkdir -p /opt && cd /opt
git clone https://github.com/zxmfke/dialogue-training.git
cd dialogue-training
bash deploy.sh
```

### 部署后管理

```bash
# 查看服务状态
systemctl status dialogue-training

# 查看日志
journalctl -u dialogue-training -f

# 重启服务
systemctl restart dialogue-training

# 停止服务
systemctl stop dialogue-training
```

---

## 🐳 方案三：Docker 部署

```bash
# 1. 安装 Docker
curl -fsSL https://get.docker.com | sh

# 2. 克隆代码
git clone https://github.com/zxmfke/dialogue-training.git
cd dialogue-training

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f
```

---

## 🔐 配置 HTTPS（推荐）

### 使用 Let's Encrypt

```bash
# 安装 Certbot
apt-get install certbot python3-certbot-nginx

# 申请证书
certbot --nginx -d your-domain.com

# 自动续期
certbot renew --dry-run
```

---

## 📱 访问应用

部署成功后访问：
- 咨询师端: `http://你的服务器IP/` 或 `https://your-domain.com/`
- 管理后台: `http://你的服务器IP/admin` 或 `https://your-domain.com/admin`

手机访问时建议添加到主屏幕：
- iOS: Safari → 分享 → 添加到主屏幕
- Android: Chrome → 菜单 → 添加到主屏幕

---

## 🆘 常见问题

### Q: Render 部署失败？
A: 检查 requirements.txt 格式，确保没有 sqlite3-python（这是 Python 标准库）

### Q: 服务器部署后无法访问？
A: 检查防火墙设置：
```bash
ufw status
ufw allow 80/tcp
ufw allow 8000/tcp
```

### Q: 如何更新代码？
A: 
```bash
cd /opt/dialogue-training
git pull
systemctl restart dialogue-training
```

### Q: 如何备份数据？
A: 
```bash
# 备份数据目录
tar -czvf backup-$(date +%Y%m%d).tar.gz /opt/dialogue-training/data/
```

---

## 📝 环境变量配置

创建 `.env` 文件：

```bash
# API 配置
OPENAI_API_KEY=your_api_key_here
MODEL=gpt-4

# 安全配置
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=*

# 数据库（可选）
DATABASE_URL=sqlite:///data/app.db
```

---

## 🎯 生产环境优化

1. **使用 Gunicorn + Uvicorn**
   ```bash
   pip install gunicorn
   gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

2. **配置 Redis 缓存**（可选）

3. **使用 CDN 加速静态资源**

4. **配置监控告警**
   ```bash
   # 安装监控
   pip install prometheus-client
   ```

---

需要帮助？请提交 Issue 或联系开发者。
