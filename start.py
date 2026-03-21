#!/usr/bin/env python3
"""
启动脚本

一键启动技术指标前置预判工具的前端和后端服务
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# 配置
BACKEND_PORT = 8001  # 改为8001，避免8000端口被占用
FRONTEND_PORT = 3000

# 存储子进程
current_processes = []


def print_banner():
    """打印启动横幅"""
    print("""
============================================================

          技术指标前置预判工具 - 启动脚本

  通过反向数学推导计算技术指标临界价格，提前布局交易机会

============================================================
""")


def start_backend():
    """启动后端服务"""
    print("[1/3] 启动 FastAPI 后端服务...")

    backend_dir = Path(__file__).parent / "backend"
    
    # 检查后端目录
    if not backend_dir.exists():
        print("      [FAIL] 后端目录不存在")
        return False

    # 检查虚拟环境
    venv_path = backend_dir / "venv"
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        python_path = venv_path / "bin" / "python"

    # 如果没有虚拟环境，使用系统Python
    if not python_path.exists():
        print("      提示: 未找到虚拟环境，使用系统Python")
        python_cmd = "python"
    else:
        python_cmd = str(python_path)
        

    # 启动服务
    cmd = [
        python_cmd, "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", str(BACKEND_PORT),
        "--reload"
    ]

    try:
        process = subprocess.Popen(
            cmd,
            cwd=str(backend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'
        )

        current_processes.append(process)

        # 等待服务启动
        time.sleep(3)

        # 检查服务是否成功启动
        exit_code = process.poll()
        if exit_code is None:
            print(f"      [OK] 后端服务已启动: http://localhost:{BACKEND_PORT}")
            print(f"      [OK] API文档: http://localhost:{BACKEND_PORT}/docs")
            return True
        else:
            print(f"      [FAIL] 后端服务启动失败，退出码: {exit_code}")
            return False
    except Exception as e:
        print(f"      [FAIL] 启动后端失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def start_frontend():
    """启动前端服务"""
    print("[2/3] 启动 React 前端服务...")

    frontend_dir = Path(__file__).parent / "frontend"
    
    # 检查前端目录
    if not frontend_dir.exists():
        print("      [FAIL] 前端目录不存在")
        return False

    # 检查 npm 是否可用（尝试多种方式）
    npm_cmd = None
    
    # 尝试 1: 直接调用 npm
    for cmd_name in ["npm.cmd", "npm", "node"]:
        try:
            result = subprocess.run(
                [cmd_name, "--version"],
                capture_output=True,
                timeout=5,
                shell=True  # Windows 上可能需要 shell=True
            )
            if result.returncode == 0:
                npm_cmd = cmd_name
                break
        except Exception:
            continue
    
    if npm_cmd is None:
        print("      [FAIL] 未找到 npm，请先安装 Node.js")
        print("      安装命令: winget install OpenJS.NodeJS")
        return False
    
    print(f"      [OK] 找到 npm: {npm_cmd}")

    # 检查 node_modules
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print(f"      安装前端依赖 ({npm_cmd} install)...")
        try:
            result = subprocess.run(
                [npm_cmd, "install"],
                cwd=str(frontend_dir),
                check=True,
                capture_output=True,
                text=True,
                shell=True
            )
            print("      [OK] 前端依赖安装完成")
        except subprocess.CalledProcessError as e:
            print(f"      [FAIL] 安装前端依赖失败: {e}")
            return False

    # 启动服务
    cmd = [npm_cmd, "run", "dev"]

    try:
        # Windows下需要特殊处理
        if sys.platform == "win32":
            process = subprocess.Popen(
                cmd,
                cwd=str(frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace',
                shell=True,  # Windows 上需要 shell=True 来执行 .cmd 文件
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            process = subprocess.Popen(
                cmd,
                cwd=str(frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace',
                preexec_fn=os.setsid
            )

        current_processes.append(process)

        # 等待服务启动
        time.sleep(5)

        # 检查服务是否成功启动
        if process.poll() is None:
            print(f"      [OK] 前端服务已启动: http://localhost:{FRONTEND_PORT}")
            return True
        else:
            print("      [FAIL] 前端服务启动失败")
            return False
    except Exception as e:
        print(f"      [FAIL] 启动前端失败: {e}")
        return False


def print_access_info():
    """打印访问信息"""
    print("""
[3/3] 服务启动完成！

============================================================

访问地址:
   - 前端界面: http://localhost:3000
   - 后端API:  http://localhost:8001
   - API文档:  http://localhost:8001/docs

功能特性:
   - 临界价格触发矩阵 (MACD/均线/KDJ)
   - 多周期均线系统 (5/10/20/30/60/120/250日)
   - 多指标共振区间检测
   - 智能条件筛选器
   - 实时价格预警推送
   - 压力测试模拟器

快捷键:
   - Ctrl+C 停止所有服务

============================================================
""")


def signal_handler(sig, frame):
    """信号处理函数"""
    print("\n\n正在停止所有服务...")

    for process in current_processes:
        try:
            if sys.platform == "win32":
                process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except:
            process.terminate()

    # 等待进程结束
    time.sleep(2)

    # 强制结束未退出的进程
    for process in current_processes:
        if process.poll() is None:
            process.kill()

    print("[OK] 所有服务已停止")
    sys.exit(0)


def main():
    """主函数"""
    print_banner()

    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, signal_handler)

    # 启动服务
    backend_ok = start_backend()
    frontend_ok = start_frontend()

    if backend_ok or frontend_ok:
        print_access_info()

        # 保持运行
        print("按 Ctrl+C 停止所有服务\n")

        try:
            while True:
                time.sleep(1)

                # 检查进程状态
                for process in current_processes:
                    if process.poll() is not None:
                        print(f"\n警告: 子进程退出 (code: {process.returncode})")
                        break

        except KeyboardInterrupt:
            signal_handler(None, None)
    else:
        print("\n[FAIL] 服务启动失败，请检查错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()
