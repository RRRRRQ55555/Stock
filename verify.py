#!/usr/bin/env python3
"""
股票助手项目完整验证脚本
检查所有组件是否正常工作
"""

import sys
import requests
import time
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

# 颜色输出
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
END = '\033[0m'

def print_header(title):
    """打印标题"""
    print(f"\n{CYAN}{'='*70}{END}")
    print(f"{CYAN}  {title}{END}")
    print(f"{CYAN}{'='*70}{END}\n")

def check_service(url, name, timeout=3):
    """检查服务是否可用"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"{GREEN}✓ {name} - 正常{END}")
            return True
        else:
            print(f"{YELLOW}⚠ {name} - 响应代码: {response.status_code}{END}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"{RED}✗ {name} - 连接失败（服务未启动或地址错误）{END}")
        return False
    except requests.exceptions.Timeout:
        print(f"{RED}✗ {name} - 超时{END}")
        return False
    except Exception as e:
        print(f"{RED}✗ {name} - 错误: {str(e)}{END}")
        return False

def check_api_endpoint(url, name):
    """检查 API 端点"""
    try:
        response = requests.get(url, timeout=3)
        print(f"{GREEN}✓ {name} - 响应正常 ({response.status_code}){END}")
        return True
    except Exception as e:
        print(f"{RED}✗ {name} - 错误: {str(e)}{END}")
        return False

def check_files():
    """检查必要的文件"""
    print_header("📁 文件检查")
    
    base_dir = Path("e:/RQ/龙虾/Stock/stock_assistant")
    
    files_to_check = {
        "启动脚本": base_dir / "launch.py",
        "后端启动": base_dir / "start_backend.py",
        "前端入口": base_dir / "index.html",
        "后端主文件": base_dir / "backend" / "app" / "main.py",
        "前端配置": base_dir / "frontend" / "package.json",
    }
    
    all_exist = True
    for name, path in files_to_check.items():
        if path.exists():
            print(f"{GREEN}✓ {name:<15} - {path}{END}")
        else:
            print(f"{RED}✗ {name:<15} - 未找到: {path}{END}")
            all_exist = False
    
    return all_exist

def check_backend_services():
    """检查后端服务"""
    print_header("🔧 后端服务检查")
    
    results = []
    
    # 检查主服务
    print("主服务:")
    results.append(check_service("http://localhost:8000/health", "  健康检查端点"))
    results.append(check_service("http://localhost:8000/docs", "  API 文档"))
    
    print("\nAPI 端点:")
    results.append(check_api_endpoint("http://localhost:8000/api/stocks/list", "  股票列表 API"))
    
    return all(results)

def check_frontend_services():
    """检查前端服务"""
    print_header("🎨 前端服务检查")
    
    results = []
    
    print("前端应用:")
    results.append(check_service("http://localhost:8080", "  前端主页"))
    results.append(check_service("http://localhost:8080/index.html", "  index.html"))
    
    return all(results)

def check_python_dependencies():
    """检查 Python 依赖"""
    print_header("🐍 Python 依赖检查")
    
    dependencies = [
        ("fastapi", "FastAPI 框架"),
        ("uvicorn", "Uvicorn 服务器"),
        ("pydantic", "数据验证库"),
        ("numpy", "数值计算库"),
        ("pandas", "数据处理库"),
        ("requests", "HTTP 客户端"),
    ]
    
    all_installed = True
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"{GREEN}✓ {name:<20} ({module}){END}")
        except ImportError:
            print(f"{RED}✗ {name:<20} ({module}) - 未安装{END}")
            all_installed = False
    
    return all_installed

def check_ports():
    """检查端口是否被占用"""
    print_header("🔌 端口检查")
    
    ports = {
        8000: "后端 API",
        8080: "前端服务",
    }
    
    all_available = True
    for port, service in ports.items():
        try:
            response = requests.get(f"http://localhost:{port}", timeout=1)
            print(f"{GREEN}✓ 端口 {port} - {service} (已启动){END}")
        except:
            print(f"{YELLOW}⚠ 端口 {port} - {service} (未检测到){END}")
            all_available = False
    
    return all_available

def check_project_structure():
    """检查项目结构"""
    print_header("📂 项目结构检查")
    
    base_dir = Path("e:/RQ/龙虾/Stock/stock_assistant")
    
    dirs_to_check = {
        "后端目录": base_dir / "backend",
        "前端目录": base_dir / "frontend",
        "小程序目录": base_dir / "miniprogram",
        "API 目录": base_dir / "backend" / "app" / "api",
        "核心模块": base_dir / "backend" / "app" / "core",
    }
    
    all_exist = True
    for name, path in dirs_to_check.items():
        if path.exists():
            count = len(list(path.glob("*.py"))) if path.is_dir() else 0
            print(f"{GREEN}✓ {name:<15} - {path}{END}")
            if count > 0:
                print(f"   {BLUE}  ({count} 个 Python 文件){END}")
        else:
            print(f"{RED}✗ {name:<15} - 未找到{END}")
            all_exist = False
    
    return all_exist

def main():
    print(f"""
{CYAN}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║            股票技术指标前置预判工具 - 完整验证                    ║
║                                                                  ║
║  本脚本将逐一检查系统各个组件是否正常工作                        ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
{END}
    """)
    
    # 执行所有检查
    checks = [
        ("文件检查", check_files),
        ("项目结构", check_project_structure),
        ("Python 依赖", check_python_dependencies),
        ("端口状态", check_ports),
        ("后端服务", check_backend_services),
        ("前端服务", check_frontend_services),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"{RED}检查 {name} 时出错: {e}{END}")
            results[name] = False
    
    # 汇总
    print_header("✅ 验证汇总")
    
    for name, passed in results.items():
        status = f"{GREEN}✓ 通过{END}" if passed else f"{YELLOW}⚠ 需要检查{END}"
        print(f"{name:<15} {status}")
    
    all_passed = all(results.values())
    
    print(f"\n{CYAN}{'='*70}{END}")
    if all_passed:
        print(f"{GREEN}✓ 所有检查通过！系统可以正常使用。{END}")
    else:
        print(f"{YELLOW}⚠ 部分检查未通过，请查看上述详情。{END}")
    
    print(f"\n使用方式:")
    print(f"{BLUE}1. 启动所有服务: python launch.py{END}")
    print(f"{BLUE}2. 仅启动后端: python start_backend.py{END}")
    print(f"{BLUE}3. 访问前端: http://localhost:8080{END}")
    print(f"{BLUE}4. 查看 API 文档: http://localhost:8000/docs{END}")
    print(f"{CYAN}{'='*70}{END}\n")

if __name__ == "__main__":
    main()
