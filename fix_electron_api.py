#!/usr/bin/env python3
"""
Playwright Electron API 支持检测和修复工具

用于检测 Playwright 版本并提供正确的 Electron 启动方法
"""

import sys
import subprocess


def check_playwright_installation():
    """检查 Playwright 是否安装"""
    print("=" * 70)
    print("步骤 1：检查 Playwright 安装")
    print("=" * 70)

    try:
        import playwright
        version = playwright.__version__
        print(f"✓ Playwright 已安装")
        print(f"  版本: {version}")
        return version
    except ImportError:
        print("❌ Playwright 未安装")
        return None


def get_recommended_version():
    """获取推荐的 Playwright 版本"""
    return "1.40.0"  # 或更高版本，确保支持 Electron


def install_playwright():
    """安装或更新 Playwright"""
    print("\n" + "=" * 70)
    print("安装/更新 Playwright")
    print("=" * 70)

    recommended = get_recommended_version()
    print(f"\n推荐版本: {recommended} 或更高\n")

    commands = [
        ("安装 Playwright", [sys.executable, "-m", "pip", "install", f"playwright>={recommended}"]),
        ("安装浏览器驱动", [sys.executable, "-m", "playwright", "install"])
    ]

    for desc, cmd in commands:
        print(f"\n执行: {desc}")
        print(f"命令: {' '.join(cmd)}")
        print("-" * 70)

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✓ 成功")
            if result.stdout:
                print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ 失败: {e}")
            print(e.stderr if e.stderr else "")
            return False

    return True


def test_electron_api():
    """测试 Electron API 是否可用"""
    print("\n" + "=" * 70)
    print("步骤 2：测试 Electron API")
    print("=" * 70)

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            # 方法 1：检查 _impl._electron
            if hasattr(p, '_impl') and hasattr(p._impl, '_electron'):
                print("✓ 方法 1 可用: playwright._impl._electron")
                return 1

            # 方法 2：检查 electron 属性
            if hasattr(p, 'electron'):
                print("✓ 方法 2 可用: playwright.electron")
                return 2

            # 方法 3：尝试导入 Electron
            try:
                from playwright.sync_api import Electron
                print("✓ 方法 3 可用: from playwright.sync_api import Electron")
                return 3
            except ImportError:
                pass

            print("❌ 所有方法都不可用")
            return 0

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return 0


def generate_electron_script(method: int):
    """根据可用的方法生成正确的代码"""
    print("\n" + "=" * 70)
    print("步骤 3：生成正确的代码")
    print("=" * 70)

    if method == 0:
        print("\n❌ Electron API 不可用")
        print("\n请尝试：")
        print("1. 更新 Playwright: pip install --upgrade playwright")
        print("2. 重新安装: pip uninstall playwright && pip install playwright")
        print("3. 检查版本: pip show playwright")
        return

    print(f"\n使用方法 {method}:\n")

    if method == 1:
        code = '''
from playwright.sync_api import sync_playwright

def launch_electron_app(executable_path: str):
    """使用 _impl._electron API 启动 Electron 应用"""

    with sync_playwright() as playwright:
        # 获取 electron API
        electron = playwright._impl._electron

        # 启动应用
        app = electron.launch(executable_path=executable_path)

        # 获取主窗口
        page = app.first_window()

        # 您的操作...
        print(f"应用已启动，标题: {page.title()}")

        # 暂停以使用 Inspector
        page.pause()

        # 关闭应用
        app.close()

# 使用示例
if __name__ == "__main__":
    # 设置您的 VS Code 路径
    vscode_path = "/usr/bin/code"  # Linux
    # vscode_path = "/Applications/Visual Studio Code.app/Contents/MacOS/Electron"  # Mac
    # vscode_path = r"C:\\Users\\YourName\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"  # Windows

    launch_electron_app(vscode_path)
'''

    elif method == 2:
        code = '''
from playwright.sync_api import sync_playwright

def launch_electron_app(executable_path: str):
    """使用 playwright.electron API 启动 Electron 应用"""

    with sync_playwright() as playwright:
        # 获取 electron API
        electron = playwright.electron

        # 启动应用
        app = electron.launch(executable_path=executable_path)

        # 获取主窗口
        page = app.first_window()

        # 您的操作...
        print(f"应用已启动，标题: {page.title()}")

        # 暂停以使用 Inspector
        page.pause()

        # 关闭应用
        app.close()

# 使用示例
if __name__ == "__main__":
    vscode_path = "/usr/bin/code"
    launch_electron_app(vscode_path)
'''

    elif method == 3:
        code = '''
from playwright.sync_api import sync_playwright, Electron

def launch_electron_app(executable_path: str):
    """使用导入的 Electron 类启动应用"""

    with sync_playwright() as playwright:
        # 直接使用导入的 Electron
        electron: Electron = playwright.electron

        # 启动应用
        app = electron.launch(executable_path=executable_path)

        # 获取主窗口
        page = app.first_window()

        # 您的操作...
        print(f"应用已启动，标题: {page.title()}")

        # 暂停以使用 Inspector
        page.pause()

        # 关闭应用
        app.close()

# 使用示例
if __name__ == "__main__":
    vscode_path = "/usr/bin/code"
    launch_electron_app(vscode_path)
'''

    print(code)

    # 保存到文件
    filename = f"electron_launch_method_{method}.py"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)

    print(f"\n✓ 代码已保存到: {filename}")
    print(f"\n运行测试: python {filename}")


def show_alternative_solution():
    """显示备用解决方案（使用 chromium.launch）"""
    print("\n" + "=" * 70)
    print("备用方案：使用 chromium.launch (不推荐)")
    print("=" * 70)

    code = '''
from playwright.sync_api import sync_playwright
import time

def launch_electron_with_chromium(executable_path: str):
    """
    使用 chromium.launch 启动 Electron（备用方案）

    警告：此方法不稳定，仅在 electron API 完全不可用时使用
    """

    with sync_playwright() as playwright:
        # 使用 chromium API（不推荐）
        app = playwright.chromium.launch(
            executable_path=executable_path,
            headless=False
        )

        # 等待上下文
        print("等待浏览器上下文...")
        timeout = 20
        start_time = time.time()

        while not app.contexts:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"超时：{timeout}秒内未创建上下文")
            time.sleep(0.2)

        context = app.contexts[0]
        print("✓ 上下文已创建")

        # 获取页面
        if context.pages:
            page = context.pages[0]
        else:
            page = context.wait_for_event("page", timeout=20000)

        print(f"✓ 页面已获取: {page.title()}")

        # 等待加载
        page.wait_for_load_state("domcontentloaded")
        time.sleep(2)

        # 暂停以使用 Inspector
        page.pause()

        # 关闭
        app.close()

# 使用
if __name__ == "__main__":
    vscode_path = "/usr/bin/code"
    launch_electron_with_chromium(vscode_path)
'''

    print(code)

    with open("electron_launch_chromium_fallback.py", 'w', encoding='utf-8') as f:
        f.write(code)

    print("\n✓ 备用代码已保存到: electron_launch_chromium_fallback.py")


def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   Playwright Electron API 检测和修复工具                             ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)

    # 检查安装
    version = check_playwright_installation()

    if not version:
        print("\n需要安装 Playwright")
        response = input("\n是否现在安装? (y/n): ")
        if response.lower() == 'y':
            if install_playwright():
                print("\n✓ 安装成功！请重新运行此脚本。")
            else:
                print("\n❌ 安装失败，请手动安装：")
                print("  pip install playwright>=1.40.0")
                print("  playwright install")
        return

    # 检查版本
    major, minor = map(int, version.split('.')[:2])
    if major < 1 or (major == 1 and minor < 40):
        print(f"\n⚠️  警告：您的版本 ({version}) 可能较旧")
        print(f"   推荐版本: 1.40.0 或更高")
        response = input("\n是否更新? (y/n): ")
        if response.lower() == 'y':
            install_playwright()
            return

    # 测试 Electron API
    method = test_electron_api()

    if method > 0:
        # 生成正确的代码
        generate_electron_script(method)

        print("\n" + "=" * 70)
        print("✓ 诊断完成")
        print("=" * 70)
        print(f"\n您的 Playwright 支持 Electron API (方法 {method})")
        print("\n下一步：")
        print(f"1. 查看生成的脚本: electron_launch_method_{method}.py")
        print(f"2. 修改 vscode_path 为您的实际路径")
        print(f"3. 运行: python electron_launch_method_{method}.py")
    else:
        print("\n" + "=" * 70)
        print("❌ Electron API 不可用")
        print("=" * 70)
        print("\n可能的原因：")
        print("1. Playwright 版本太旧")
        print("2. 安装不完整")
        print("3. 使用的是不支持 Electron 的分支")

        print("\n解决方案：")
        print("1. 完全重新安装：")
        print("   pip uninstall playwright")
        print("   pip install playwright>=1.40.0")
        print("   playwright install")

        print("\n2. 检查安装状态：")
        print("   pip show playwright")
        print("   python -c 'from playwright.sync_api import sync_playwright; print(dir(sync_playwright()))'")

        # 显示备用方案
        show_alternative_solution()

        print("\n⚠️  如果以上方法都不行，可以使用备用方案（chromium.launch）")
        print("   但这个方法不稳定，仅作为最后手段")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
