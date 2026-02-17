#!/bin/bash
# Auto-generated deployment script for Tencent Cloud
# Run: curl -fsSL https://pastebin.com/raw/xxxxx | sudo bash

echo "[1/6] Updating system..."
apt-get update -qq

echo "[2/6] Installing dependencies..."
apt-get install -y -qq git python3 python3-pip python3-venv nginx

echo "[3/6] Downloading application..."
mkdir -p /opt/dialogue-training
cd /opt/dialogue-training
rm -rf * 2>/dev/null
git clone -q https://github.com/zxmfke/dialogue-training.git .

echo "[4/6] Installing Python packages..."
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "[5/6] Creating service..."
cat > /etc/systemd/system/dialogue-training.service << 'ENDOFSERVICE'
[Unit]
Description=Dialogue Training AI
After=network.target
[Service]
Type=simple
WorkingDirectory=/opt/dialogue-training
ExecStart=/opt/dialogue-training/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000
Restart=always
[Install]
WantedBy=multi-user.target
ENDOFSERVICE

systemctl daemon-reload
systemctl enable -q dialogue-training
systemctl start dialogue-training

cat > /etc/nginx/sites-available/dialogue-training << 'ENDOFNGINX'
server {
    listen 80;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
ENDOFNGINX

ln -sf /etc/nginx/sites-available/dialogue-training /etc/nginx/sites-enabled/ 2>/dev/null
rm -f /etc/nginx/sites-enabled/default
nginx -t 2>/dev/null && systemctl restart nginx

echo "[6/6] Opening firewall..."
ufw allow 80/tcp 2>/dev/null
ufw allow 8000/tcp 2>/dev/null
ufw --force enable 2>/dev/null

IP=$(curl -s ip.sb 2>/dev/null || echo "YOUR_SERVER_IP")
echo ""
echo "========================================"
echo "DEPLOYMENT SUCCESS!"
echo "========================================"
echo ""
echo "Your app is running at:"
echo "  http://$IP/      (User)"
echo "  http://$IP/admin (Admin)"
echo ""
echo "To check status: systemctl status dialogue-training"
echo "To view logs:    journalctl -u dialogue-training -f"
echo "========================================"
