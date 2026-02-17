# -*- coding: utf-8 -*-
import sys
import os

# 设置编码
sys.stdout.reconfigure(encoding='utf-8')

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.main import start_server

if __name__ == "__main__":
    print("=" * 50)
    print("话术演练场 - AI 陪练系统")
    print("=" * 50)
    print()
    print("服务地址:")
    print("  咨询师端: http://localhost:8000")
    print("  管理后台: http://localhost:8000/admin")
    print("  API 文档: http://localhost:8000/docs")
    print()
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    print()
    
    start_server()
