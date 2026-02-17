import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

HOST = '81.71.98.214'
PORT = 22
KEY_PATH = r'C:\Users\zhengxm\Documents\notes\tencent_cloud\openclaw_zxm.pem'

def try_deploy(username):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        private_key = paramiko.RSAKey.from_private_key_file(KEY_PATH)
        
        print(f"Trying to connect as {username}...")
        client.connect(hostname=HOST, port=PORT, username=username, pkey=private_key, timeout=30)
        print(f"Connected as {username}!")
        
        # Run deployment commands
        print("Updating system...")
        stdin, stdout, stderr = client.exec_command('apt-get update -y', get_pty=True, timeout=300)
        print(stdout.read().decode('utf-8', errors='ignore')[-500:])
        
        print("Installing dependencies...")
        stdin, stdout, stderr = client.exec_command('apt-get install -y git python3 python3-pip python3-venv nginx', get_pty=True, timeout=300)
        print(stdout.read().decode('utf-8', errors='ignore')[-500:])
        
        print("Cloning repository...")
        client.exec_command('mkdir -p /opt/dialogue-training')
        stdin, stdout, stderr = client.exec_command(
            'cd /opt/dialogue-training && git clone https://github.com/zxmfke/dialogue-training.git . 2>&1 || git pull 2>&1',
            get_pty=True, timeout=120
        )
        print(stdout.read().decode('utf-8', errors='ignore'))
        
        print("Setting up Python environment...")
        client.exec_command('cd /opt/dialogue-training && python3 -m venv venv')
        stdin, stdout, stderr = client.exec_command(
            'cd /opt/dialogue-training && venv/bin/pip install --upgrade pip -q && venv/bin/pip install -r requirements.txt -q',
            get_pty=True, timeout=300
        )
        print(f"Pip install exit code: {stdout.channel.recv_exit_status()}")
        
        print("Creating directories...")
        client.exec_command('mkdir -p /opt/dialogue-training/data')
        client.exec_command('mkdir -p /opt/dialogue-training/src/knowledge')
        
        print("Creating systemd service...")
        service_content = '''[Unit]
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
'''
        stdin, stdout, stderr = client.exec_command(f'cat > /etc/systemd/system/dialogue-training.service << EOF\n{service_content}EOF')
        
        print("Starting service...")
        client.exec_command('systemctl daemon-reload')
        client.exec_command('systemctl enable dialogue-training')
        stdin, stdout, stderr = client.exec_command('systemctl restart dialogue-training', get_pty=True)
        print(stdout.read().decode('utf-8', errors='ignore'))
        
        print("Configuring Nginx...")
        nginx_content = '''server {
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
'''
        stdin, stdout, stderr = client.exec_command(f'cat > /etc/nginx/sites-available/dialogue-training << EOF\n{nginx_content}EOF')
        client.exec_command('ln -sf /etc/nginx/sites-available/dialogue-training /etc/nginx/sites-enabled/ 2>/dev/null; rm -f /etc/nginx/sites-enabled/default')
        stdin, stdout, stderr = client.exec_command('nginx -t && systemctl restart nginx', get_pty=True)
        print(stdout.read().decode('utf-8', errors='ignore'))
        
        print("Configuring firewall...")
        client.exec_command('ufw allow 80/tcp')
        client.exec_command('ufw allow 8000/tcp')
        client.exec_command('ufw --force enable')
        
        print("Checking service status...")
        stdin, stdout, stderr = client.exec_command('systemctl is-active dialogue-training')
        status = stdout.read().decode().strip()
        print(f"Service status: {status}")
        
        if status == 'active':
            print()
            print("=" * 60)
            print("DEPLOYMENT SUCCESS!")
            print("=" * 60)
            print()
            print(f"Access URLs:")
            print(f"  http://{HOST}/      (User App)")
            print(f"  http://{HOST}/admin (Admin Panel)")
            print()
        else:
            print("Service may not be running. Check logs with: journalctl -u dialogue-training -f")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"Failed as {username}: {e}")
        return False

if __name__ == '__main__':
    # Try root first, then ubuntu
    if not try_deploy('root'):
        print("\nTrying ubuntu user...")
        if not try_deploy('ubuntu'):
            print("\nBoth users failed. Please check:")
            print("1. Is the private key correct?")
            print("2. Is the security group allowing SSH (port 22)?")
            print("3. Is the username correct (root or ubuntu)?")
            sys.exit(1)
