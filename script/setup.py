# setup.py - 自动设置脚本
import os
import sys
import subprocess
import venv
import platform


def create_and_setup_environment():
    """创建虚拟环境并安装依赖"""
    print("=" * 50)
    print("项目环境自动设置工具")
    print("=" * 50)

    # 1. 检查 Python 版本
    print("检查 Python 版本...")
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"当前 Python 版本: {python_version}")

    # 2. 定义环境路径
    venv_path = os.path.join(os.getcwd(), "venv")

    # 3. 检查是否已存在虚拟环境
    if os.path.exists(venv_path):
        print(f"虚拟环境已存在: {venv_path}")
        choice = input("是否重新创建？(y/n): ").lower()
        if choice == 'y':
            import shutil
            shutil.rmtree(venv_path)
            print("已删除旧环境")
        else:
            print("使用现有环境")
            return

    # 4. 创建虚拟环境
    print(f"创建虚拟环境: {venv_path}")
    venv.create(venv_path, with_pip=True)

    # 5. 获取虚拟环境的 Python 路径
    if platform.system() == "Windows":
        python_path = os.path.join(venv_path, "Scripts", "python.exe")
        pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        python_path = os.path.join(venv_path, "bin", "python")
        pip_path = os.path.join(venv_path, "bin", "pip")

    print(f"Python 路径: {python_path}")

    # 6. 升级 pip
    print("升级 pip...")
    subprocess.run([python_path, "-m", "pip", "install", "--upgrade", "pip"])

    # 7. 安装依赖
    print("安装项目依赖...")
    requirements_files = [
        "requirements.txt",
        "requirements-dev.txt",
        "pyproject.toml"
    ]

    for req_file in requirements_files:
        if os.path.exists(req_file):
            print(f"从 {req_file} 安装依赖...")
            if req_file == "pyproject.toml":
                # 使用 poetry 或 pip 安装
                subprocess.run([pip_path, "install", "-e", "."])
            else:
                subprocess.run([pip_path, "install", "-r", req_file])
            break

    print("\n" + "=" * 50)
    print("✅ 环境设置完成！")
    print("=" * 50)

    # 8. 提供激活命令
    if platform.system() == "Windows":
        print(f"\n激活虚拟环境:")
        print(f"  {venv_path}\\Scripts\\activate")
        print(f"\n或在 PyCharm 中设置解释器:")
        print(f"  File → Settings → Project → Python Interpreter")
        print(f"  添加: {python_path}")
    else:
        print(f"\n激活虚拟环境:")
        print(f"  source {venv_path}/bin/activate")

    print("\n启动 PyCharm 后:")
    print("1. 打开项目文件夹")
    print("2. 设置解释器为: venv/bin/python (或 venv\\Scripts\\python.exe)")
    print("=" * 50)


if __name__ == "__main__":
    create_and_setup_environment()