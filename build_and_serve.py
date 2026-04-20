#!/usr/bin/env python3
"""
构建前端并启动 HTTP 服务器
"""

import subprocess
import os
import sys
import http.server
import socketserver
import webbrowser
from pathlib import Path

# 颜色输出
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
END = '\033[0m'

def print_step(msg):
    print(f"{BLUE}{'='*60}{END}")
    print(f"{GREEN}✓ {msg}{END}")
    print(f"{BLUE}{'='*60}{END}\n")

def run_command(cmd, cwd=None):
    """运行命令"""
    print(f"{YELLOW}执行: {' '.join(cmd)}{END}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=False)
    if result.returncode != 0:
        print(f"{RED}❌ 命令执行失败!{END}")
        return False
    return True

def main():
    frontend_dir = Path(__file__).parent / "frontend"
    dist_dir = frontend_dir / "dist"
    
    print(f"""
{GREEN}
╔══════════════════════════════════════════════════════════╗
║         股票助手 - 前端构建和服务启动工具                   ║
╚══════════════════════════════════════════════════════════╝
{END}
    """)
    
    # 检查前端目录
    if not frontend_dir.exists():
        print(f"{RED}❌ 前端目录不存在: {frontend_dir}{END}")
        sys.exit(1)
    
    print_step("第一步：编译 TypeScript")
    
    # 编译 TypeScript
    tsc_path = frontend_dir / "node_modules" / "typescript" / "bin" / "tsc.js"
    if not tsc_path.exists():
        print(f"{YELLOW}⚠️ TypeScript 编译器未找到，跳过编译{END}")
    else:
        if not run_command(["node", str(tsc_path)], cwd=str(frontend_dir)):
            print(f"{RED}编译失败，但继续进行...{END}")
    
    print_step("第二步：构建 Vite 项目")
    
    # 构建前端
    vite_path = frontend_dir / "node_modules" / ".bin" / "vite.cmd"
    if not vite_path.exists():
        print(f"{RED}❌ Vite 未找到: {vite_path}{END}")
        print("请确保已运行: cd frontend && npm install")
        sys.exit(1)
    
    # 直接使用 node 执行 vite
    vite_js = frontend_dir / "node_modules" / "vite" / "bin" / "vite.js"
    if not run_command(["node", str(vite_js), "build"], cwd=str(frontend_dir)):
        print(f"{RED}构建失败!{END}")
        sys.exit(1)
    
    # 检查 dist 目录
    if not dist_dir.exists():
        print(f"{RED}❌ 构建失败，dist 目录未生成{END}")
        sys.exit(1)
    
    print_step(f"第三步：启动 HTTP 服务器")
    print(f"{GREEN}📁 前端文件位置: {dist_dir}{END}")
    
    # 启动 HTTP 服务器
    os.chdir(dist_dir)
    port = 8080
    
    class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # 添加 CORS 头
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            super().end_headers()
        
        def do_GET(self):
            # SPA 路由支持
            if self.path != '/' and not '.' in self.path.split('/')[-1]:
                self.path = '/index.html'
            super().do_GET()
    
    with socketserver.TCPServer(("", port), MyHTTPRequestHandler) as httpd:
        url = f"http://localhost:{port}"
        print(f"""
{GREEN}
╔══════════════════════════════════════════════════════════╗
║              🚀 服务已启动！                               ║
║                                                          ║
║  🌐 访问地址: {url:<45} ║
║  📁 服务目录: {str(dist_dir):<46} ║
║                                                          ║
║  按 Ctrl+C 停止服务                                      ║
╚══════════════════════════════════════════════════════════╝
{END}
        """)
        
        # 自动打开浏览器
        try:
            webbrowser.open(url)
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n{YELLOW}服务已停止{END}")

if __name__ == "__main__":
    main()
