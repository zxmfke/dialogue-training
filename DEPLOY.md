# 🚀 部署指南

## 方法一：ngrok 内网穿透（推荐快速体验，5分钟）

### 1. 注册 ngrok
- 访问 https://dashboard.ngrok.com/signup
- 用 GitHub 账号一键登录

### 2. 获取 Token
- 登录后访问 https://dashboard.ngrok.com/get-started/your-authtoken
- 复制你的 authtoken

### 3. 配置并启动
```bash
cd "C:\coding\话术演练场"

# 配置 token（只需一次）
python scripts/setup_ngrok.py YOUR_NGROK_TOKEN

# 启动服务
python scripts/start_with_ngrok.py
```

### 4. 手机访问
运行后会显示类似：
```
📱 手机/外网访问地址：
   https://xxxx.ngrok-free.app
```
直接用手机浏览器打开即可！

---

## 方法二：Render 免费托管（推荐长期运行）

### 1. 推送代码到 GitHub
```bash
# 在 GitHub 创建仓库后
git remote add origin https://github.com/你的用户名/dialogue-training.git
git branch -M main
git push -u origin main
```

### 2. 部署到 Render
1. 访问 https://render.com
2. 用 GitHub 登录
3. 点击 "New Web Service"
4. 选择你的 GitHub 仓库 `dialogue-training`
5. 配置：
   - Name: dialogue-training
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
6. 点击 "Create Web Service"

### 3. 获取域名
Render 会自动分配域名：`https://dialogue-training-xxx.onrender.com`

---

## 方法三：云服务器（正式运营）

### 1. 购买服务器
推荐阿里云/腾讯云/华为云，最低配置（1核2G）约 50元/月

### 2. 连接服务器并部署
```bash
# SSH 连接服务器
ssh root@你的服务器IP

# 安装依赖
apt update
apt install python3-pip git nginx -y

# 拉取代码
git clone https://github.com/你的用户名/dialogue-training.git
cd dialogue-training
pip3 install -r requirements.txt

# 后台运行
nohup python3 scripts/start_api.py > app.log 2>&1 &
```

### 3. 配置 Nginx 反向代理
```bash
# 编辑配置文件
nano /etc/nginx/sites-available/dialogue-training
```

写入：
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 你的域名
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

启用配置：
```bash
ln -s /etc/nginx/sites-available/dialogue-training /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 4. 配置域名解析
- 在域名服务商添加 A 记录指向服务器 IP
- 访问 `http://your-domain.com`

---

## 🔐 安全建议

1. **修改默认配置**
   - 编辑 `config/agent.yaml` 修改敏感词库
   - 设置强密码（如添加登录功能）

2. **HTTPS 配置**
   - 云服务器：使用 Let's Encrypt 免费 SSL
   - Render：自动提供 HTTPS
   - ngrok：自动提供 HTTPS

3. **数据备份**
   ```bash
   # 定期备份数据目录
   tar -czvf backup-$(date +%Y%m%d).tar.gz data/
   ```

---

## 📱 手机访问测试

部署成功后，手机浏览器访问：
- 咨询师端：`https://你的域名/`
- 管理后台：`https://你的域名/admin`

建议添加到手机桌面（像 App 一样使用）：
- iOS: Safari → 分享 → "添加到主屏幕"
- Android: Chrome → 菜单 → "添加到主屏幕"

---

## 🆘 常见问题

**Q: ngrok 启动失败？**  
A: 需要先运行 `python scripts/setup_ngrok.py YOUR_TOKEN` 配置 token

**Q: 手机访问慢？**  
A: ngrok 免费版在国外，建议用 Render 或国内云服务器

**Q: 如何更新代码？**  
A: 修改后运行 `git add . && git commit -m "xxx" && git push`，Render 会自动重新部署

---

## 📝 版本管理

日常使用 Git：
```bash
# 查看修改
git status

# 提交修改
git add .
git commit -m "描述这次修改"
git push origin main

# 查看历史
git log --oneline

# 回滚到某个版本
git reset --hard 版本号
```
