# backend/diagnose.py
"""
环境诊断脚本
运行方式：cd backend && python diagnose.py
检查项目运行所需的所有前置条件
"""

import os
import sys
import socket
import subprocess
from pathlib import Path

# 颜色输出（Windows CMD支持）
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"


def print_pass(msg: str):
    print(f"{Colors.GREEN}[PASS]{Colors.RESET} {msg}")


def print_fail(msg: str):
    print(f"{Colors.RED}[FAIL]{Colors.RESET} {msg}")


def print_warn(msg: str):
    print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {msg}")


def check_python_version():
    """检查Python版本"""
    print("\n=== Python版本检查 ===")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major == 3 and version.minor >= 10:
        print_pass(f"Python版本: {version_str}")
        return True
    else:
        print_fail(f"Python版本过低: {version_str}，需要3.10+")
        print("  修复：从 https://www.python.org/downloads/ 下载安装Python 3.10+")
        return False


def check_pip_packages():
    """检查关键Python包"""
    print("\n=== Python包检查 ===")
    
    required_packages = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "playwright": "playwright",
        "pydantic": "pydantic",
    }
    
    all_ok = True
    for display_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print_pass(f"{display_name} 已安装")
        except ImportError:
            print_fail(f"{display_name} 未安装")
            print(f"  修复：pip install {display_name}")
            all_ok = False
    
    return all_ok


def check_playwright_browser():
    """检查Playwright浏览器是否已安装"""
    print("\n=== Playwright浏览器检查 ===")
    
    try:
        from playwright.sync_api import sync_playwright
        
        # 尝试启动浏览器
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            browser.close()
            print_pass("Playwright Chromium 浏览器可用")
            return True
    except Exception as e:
        error_msg = str(e)
        if "Executable doesn't exist" in error_msg or "browserType.launch" in error_msg:
            print_fail("Playwright 浏览器未安装")
            print("  修复：python -m playwright install chromium")
        else:
            print_fail(f"Playwright 浏览器启动失败: {error_msg}")
            print("  修复：python -m playwright install chromium")
        return False


def check_data_directory():
    """检查数据目录"""
    print("\n=== 数据目录检查 ===")
    
    backend_dir = Path(__file__).resolve().parent
    data_dir = backend_dir / "data"
    logs_dir = data_dir / "logs"
    
    # 检查data目录
    if data_dir.exists():
        print_pass(f"data目录存在: {data_dir}")
    else:
        print_warn(f"data目录不存在，将自动创建: {data_dir}")
        os.makedirs(data_dir, exist_ok=True)
    
    # 检查logs目录
    if logs_dir.exists():
        print_pass(f"logs目录存在: {logs_dir}")
    else:
        print_warn(f"logs目录不存在，将自动创建: {logs_dir}")
        os.makedirs(logs_dir, exist_ok=True)
    
    # 检查auth.json
    auth_file = data_dir / "douyin_auth.json"
    if auth_file.exists():
        file_size = auth_file.stat().st_size
        if file_size > 100:
            print_pass(f"登录态文件存在 ({file_size} bytes): {auth_file}")
        else:
            print_warn(f"登录态文件可能无效 (仅{file_size} bytes): {auth_file}")
            print("  建议：cd backend && python login_manual.py 重新登录")
    else:
        print_warn(f"登录态文件不存在: {auth_file}")
        print("  修复：cd backend && python login_manual.py 完成登录")
    
    return True


def check_port_available(port: int):
    """检查端口是否被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", port))
        sock.close()
        return True
    except OSError:
        return False


def check_ports():
    """检查服务端口"""
    print("\n=== 端口检查 ===")
    
    ports = {
        8000: "后端服务 (FastAPI)",
        5173: "前端开发服务器 (Vite)",
    }
    
    all_ok = True
    for port, service_name in ports.items():
        if check_port_available(port):
            print_pass(f"端口 {port} 可用 ({service_name})")
        else:
            print_warn(f"端口 {port} 已被占用 ({service_name})")
            print(f"  修复：关闭占用端口的程序，或修改配置使用其他端口")
            all_ok = False
    
    return all_ok


def check_node_npm():
    """检查Node.js和npm"""
    print("\n=== Node.js/npm检查 ===")
    
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print_pass(f"Node.js 版本: {version}")
        else:
            print_fail("Node.js 未安装")
            print("  修复：从 https://nodejs.org/ 下载安装Node.js 18+")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print_fail("Node.js 未安装或不可用")
        print("  修复：从 https://nodejs.org/ 下载安装Node.js 18+")
        return False
    
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print_pass(f"npm 版本: {version}")
            return True
        else:
            print_fail("npm 未安装")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print_fail("npm 未安装或不可用")
        return False


def check_frontend_deps():
    """检查前端依赖"""
    print("\n=== 前端依赖检查 ===")
    
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
    node_modules = frontend_dir / "node_modules"
    
    if node_modules.exists():
        print_pass(f"node_modules 存在: {node_modules}")
        return True
    else:
        print_warn(f"node_modules 不存在: {node_modules}")
        print("  修复：cd frontend && npm install")
        return False


def main():
    """运行所有诊断检查"""
    print("=" * 60)
    print("  抖音收藏AI知识库 - 环境诊断")
    print("=" * 60)
    
    results = {}
    
    # 运行所有检查
    results["python"] = check_python_version()
    results["packages"] = check_pip_packages()
    results["playwright"] = check_playwright_browser()
    results["data_dir"] = check_data_directory()
    results["ports"] = check_ports()
    results["node"] = check_node_npm()
    results["frontend"] = check_frontend_deps()
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("  诊断结果汇总")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check_name, result in results.items():
        status = f"{Colors.GREEN}OK{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {check_name:15s} : {status}")
    
    print(f"\n总计: {passed}/{total} 项检查通过")
    
    if passed == total:
        print(f"\n{Colors.GREEN}所有检查通过！可以运行 start.bat 启动服务。{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}部分检查未通过，请按照上述修复建议操作。{Colors.RESET}")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
