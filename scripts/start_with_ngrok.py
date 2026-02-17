# -*- coding: utf-8 -*-
"""
使用 ngrok 内网穿透，让外网访问本地服务
"""
import os
import sys
import time
import subprocess

# 设置编码
sys.stdout.reconfigure(encoding='utf-8')

def start_with_ngrok():
    from pyngrok import ngrok
    
    print("=" * 60)
    print("🚀 启动话术演练场 + ngrok 内网穿透")
    print("=" * 60)
    print()
    
    # 1. 启动本地服务（后台）
    print("📡 启动本地服务...")
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    import threading
    from src.api.main import app
    import uvicorn
    
    def run_server():
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    time.sleep(3)  # 等待服务启动
    print("✅ 本地服务已启动: http://localhost:8000")
    print()
    
    # 2. 启动 ngrok
    print("🌐 启动 ngrok 内网穿透...")
    print("   正在创建公网隧道...")
    print()
    
    try:
        # 创建隧道
        public_url = ngrok.connect(8000, "http")
        
        print("=" * 60)
        print("🎉 部署成功！")
        print("=" * 60)
        print()
        print("📱 手机/外网访问地址：")
        print(f"   {public_url}")
        print()
        print("📱 管理后台：")
        print(f"   {public_url}/admin")
        print()
        print("⚠️  注意：")
        print("   1. 免费版 ngrok 每次重启 URL 会变")
        print("   2. 不要关闭此窗口，保持服务运行")
        print("   3. 按 Ctrl+C 停止服务")
        print()
        print("=" * 60)
        
        # 保持运行
        while True:
            time.sleep(1)
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        print()
        print("提示：首次使用需要联网下载 ngrok 二进制文件")
        print("如果失败，可以尝试访问 https://dashboard.ngrok.com 注册获取 token")
        input("按回车退出...")

if __name__ == "__main__":
    try:
        start_with_ngrok()
    except KeyboardInterrupt:
        print("\n\n👋 服务已停止")
        from pyngrok import ngrok
        ngrok.kill()
