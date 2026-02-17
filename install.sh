#!/bin/bash
# 话术演练场 - 腾讯云一键部署脚本
# 使用方法：在服务器上运行: bash install.sh

set -e

echo "=========================================="
echo "🚀 话术演练场 - 一键部署"
echo "=========================================="
echo ""

# 更新系统
echo "📦 更新系统..."
apt-get update -y

# 安装依赖
echo "🔧 安装依赖..."
apt-get install -y git python3 python3-pip python3-venv nginx curl

# 创建应用目录
echo "📁 创建应用目录..."
mkdir -p /opt/dialogue-training
cd /opt/dialogue-training

# 克隆代码
echo "📥 下载代码..."
if [ -d ".git" ]; then
    git pull origin main
else
    git clone https://github.com/zxmfke/dialogue-training.git .
fi

# 创建虚拟环境
echo "🐍 创建 Python 环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo "📦 安装 Python 包..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# 创建数据目录
echo "📂 创建数据目录..."
mkdir -p data
mkdir -p src/knowledge

# 创建 systemd 服务
echo "⚙️ 创建服务..."
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
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

ln -sf /etc/nginx/sites-available/dialogue-training /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# 配置防火墙
echo "🔒 配置防火墙..."
ufw allow 80/tcp
ufw allow 8000/tcp
ufw --force enable

# 获取 IP
IP=$(curl -s ip.sb)

echo ""
echo "=========================================="
echo "✅ 部署成功！"
echo "=========================================="
echo ""
echo "🌐 访问地址:"
echo "   http://$IP/      (咨询师端)"
echo "   http://$IP/admin (管理后台)"
echo ""
echo "📊 管理命令:"
echo "   查看状态: systemctl status dialogue-training"
echo "   查看日志: journalctl -u dialogue-training -f"
echo "   重启服务: systemctl restart dialogue-training"
echo "   停止服务: systemctl stop dialogue-training"
echo ""
echo "=========================================="
