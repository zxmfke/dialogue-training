#!/bin/bash
# 话术演练场 - 腾讯云一键部署脚本
# 使用方法：在腾讯云服务器上运行此脚本

set -e

echo "=========================================="
echo "🚀 话术演练场 - 腾讯云一键部署"
echo "=========================================="
echo ""

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 root 用户运行此脚本"
    echo "   运行: sudo bash deploy.sh"
    exit 1
fi

# 更新系统
echo "📦 更新系统包..."
apt-get update -y
apt-get upgrade -y

# 安装必要软件
echo "🔧 安装必要软件..."
apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    curl \
    wget \
    vim

# 创建应用目录
echo "📁 创建应用目录..."
mkdir -p /opt/dialogue-training
cd /opt/dialogue-training

# 克隆代码（或者从本地复制）
echo "📥 下载应用代码..."
if [ -d ".git" ]; then
    git pull origin main
else
    git clone https://github.com/zxmfke/dialogue-training.git .
fi

# 创建虚拟环境
echo "🐍 创建 Python 虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo "📦 安装 Python 依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建数据目录
echo "📂 创建数据目录..."
mkdir -p data
mkdir -p src/knowledge

# 创建 systemd 服务
echo "⚙️ 创建系统服务..."
cat > /etc/systemd/system/dialogue-training.service << 'EOF'
[Unit]
Description=Dialogue Training AI Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/dialogue-training
Environment=PATH=/opt/dialogue-training/venv/bin
ExecStart=/opt/dialogue-training/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
systemctl daemon-reload
systemctl enable dialogue-training
systemctl start dialogue-training

# 配置 Nginx
echo "🌐 配置 Nginx..."
cat > /etc/nginx/sites-available/dialogue-training << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

ln -sf /etc/nginx/sites-available/dialogue-training /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# 配置防火墙
echo "🔒 配置防火墙..."
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw --force enable

echo ""
echo "=========================================="
echo "✅ 部署成功！"
echo "=========================================="
echo ""
echo "🌐 访问地址:"
echo "   咨询师端: http://$(curl -s ip.sb)/"
echo "   管理后台: http://$(curl -s ip.sb)/admin"
echo ""
echo "📊 服务状态:"
echo "   systemctl status dialogue-training"
echo ""
echo "📜 查看日志:"
echo "   journalctl -u dialogue-training -f"
echo ""
echo "🔄 重启服务:"
echo "   systemctl restart dialogue-training"
echo ""
echo "=========================================="
