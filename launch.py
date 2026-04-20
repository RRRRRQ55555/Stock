#!/usr/bin/env python3
"""
启动股票助手产品（一键启动前后端）
"""

import subprocess
import os
import sys
import time
import http.server
import socketserver
import threading
import webbrowser
from pathlib import Path

# 颜色输出
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
CYAN = '\033[96m'
END = '\033[0m'

class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """安静的 HTTP 请求处理器"""
    
    def log_message(self, format, *args):
        """不输出访问日志"""
        pass
    
    def end_headers(self):
        # 添加 CORS 头
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

def start_backend():
    """启动后端服务"""
    backend_script = Path(__file__).parent / "start_backend.py"
    if backend_script.exists():
        return subprocess.Popen(
            [sys.executable, str(backend_script)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    return None

def start_frontend_server(port=8080):
    """启动前端 HTTP 服务器"""
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    with socketserver.TCPServer(("", port), QuietHTTPRequestHandler) as httpd:
        return httpd

def main():
    project_dir = Path(__file__).parent
    
    print(f"""
{CYAN}
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║            🚀 股票技术指标前置预判工具 - 启动器                  ║
║                                                                ║
║        一键启动前后端服务，开始使用股票分析工具！              ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
{END}
    """)

    # 启动后端
    print(f"{YELLOW}[1/2] 启动后端服务...{END}")
    backend_process = start_backend()
    
    # 等待后端启动
    time.sleep(3)
    
    if backend_process and backend_process.poll() is None:
        print(f"{GREEN}✓ 后端服务已启动 (PID: {backend_process.pid}){END}")
        print(f"{BLUE}  📊 API 地址: http://localhost:8000{END}")
        print(f"{BLUE}  📚 API 文档: http://localhost:8000/docs{END}\n")
    else:
        print(f"{RED}⚠️ 后端启动可能失败，继续启动前端...{END}\n")

    # 启动前端
    print(f"{YELLOW}[2/2] 启动前端服务...{END}")
    
    frontend_port = 8080
    
    def run_frontend():
        try:
            httpd = start_frontend_server(frontend_port)
            httpd.serve_forever()
        except Exception as e:
            print(f"{RED}前端服务错误: {e}{END}")

    frontend_thread = threading.Thread(target=run_frontend, daemon=True)
    frontend_thread.start()
    
    time.sleep(1)
    
    frontend_url = f"http://localhost:{frontend_port}"
    print(f"{GREEN}✓ 前端服务已启动{END}")
    print(f"{BLUE}  🌐 访问地址: {frontend_url}{END}\n")

    print(f"""
{CYAN}
╔════════════════════════════════════════════════════════════════╗
║                    ✨ 服务启动成功！✨                        ║
║                                                                ║
║  🎯 开始使用:                                                  ║
║     点击下方链接或在浏览器中打开:                              ║
║     {frontend_url:<58} ║
║                                                                ║
║  📚 查看 API 文档:                                             ║
║     http://localhost:8000/docs                               ║
║                                                                ║
║  ⏹️  停止服务: 按 Ctrl+C                                       ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
{END}
    """)

    # 尝试打开浏览器
    try:
        webbrowser.open(frontend_url)
    except:
        pass

    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}正在关闭服务...{END}")
        if backend_process and backend_process.poll() is None:
            backend_process.terminate()
            backend_process.wait()
        print(f"{GREEN}✓ 服务已停止{END}")

if __name__ == "__main__":
    main()
