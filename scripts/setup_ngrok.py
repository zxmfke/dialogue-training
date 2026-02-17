# -*- coding: utf-8 -*-
"""
使用 ngrok 内网穿透
首次使用需要先配置 token: python scripts/setup_ngrok.py YOUR_TOKEN
"""
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

def setup_ngrok():
    """配置 ngrok token"""
    if len(sys.argv) < 2:
        print("用法: python scripts/setup_ngrok.py YOUR_NGROK_TOKEN")
        print()
        print("获取 token:")
        print("1. 访问 https://dashboard.ngrok.com/signup")
        print("2. 登录后访问 https://dashboard.ngrok.com/get-started/your-authtoken")
        print("3. 复制 token 并运行: python scripts/setup_ngrok.py YOUR_TOKEN")
        return
    
    token = sys.argv[1]
    
    from pyngrok import ngrok
    ngrok.set_auth_token(token)
    
    print("✅ ngrok token 已配置！")
    print()
    print("现在可以运行: python scripts/start_with_ngrok.py")

if __name__ == "__main__":
    setup_ngrok()
