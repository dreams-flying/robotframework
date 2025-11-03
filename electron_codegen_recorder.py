#!/usr/bin/env python3
"""
Playwright Electron Codegen 录制脚本 - 修复版

用于启动 Electron 应用（如 VS Code）并使用 Playwright Inspector 录制操作

使用方法：
    python electron_codegen_recorder.py

前置要求：
    pip install playwright
    playwright install
"""

import sys
import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, Playwright, Page


# ============================================================================
# 配置区域：根据您的实际情况修改
# ============================================================================

# VS Code 可执行文件路径配置
VSCODE_PATHS = {
    "win32": [
        r"C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        r"C:\Program Files\Microsoft VS Code\Code.exe",
        r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
    ],
    "darwin": [
        "/Applications/Visual Studio Code.app/Contents/MacOS/Electron",
    ],
    "linux": [
        "/usr/bin/code",
        "/usr/share/code/code",
        "/opt/visual-studio-code/code",
        "/snap/bin/code",
    ]
}

# 或者，直接指定您的 VS Code 路径（取消注释并修改）
# CUSTOM_VSCODE_PATH = "/path/to/your/vscode"


# ============================================================================
# 工具函数
# ============================================================================

def find_vscode_executable() -> str:
    """
    自动查找 VS Code 可执行文件路径

    Returns:
        str: VS Code 可执行文件的完整路径

    Raises:
        FileNotFoundError: 如果找不到 VS Code
    """
    # 1. 检查是否有自定义路径
    if 'CUSTOM_VSCODE_PATH' in globals() and globals()['CUSTOM_VSCODE_PATH']:
        custom_path = globals()['CUSTOM_VSCODE_PATH']
        if os.path.exists(custom_path):
            return custom_path

    # 2. 检查环境变量
    env_path = os.environ.get('VSCODE_PATH')
    if env_path and os.path.exists(env_path):
        return env_path

    # 3. 根据操作系统查找
    platform = sys.platform
    paths = VSCODE_PATHS.get(platform, [])

    # 在 Windows 上，替换 {username}
    if platform == "win32":
        username = os.environ.get('USERNAME', 'admin')
        paths = [p.replace('{username}', username) for p in paths]

    # 遍历所有可能的路径
    for path in paths:
        if os.path.exists(path):
            print(f"✓ 找到 VS Code: {path}")
            return path

    # 4. 如果都找不到，给出详细的错误信息
    print("\n" + "=" * 70)
    print("❌ 错误：找不到 VS Code 可执行文件")
    print("=" * 70)
    print("\n请尝试以下方法之一：\n")
    print("方法1：在脚本中设置自定义路径")
    print("    取消注释并修改脚本中的 CUSTOM_VSCODE_PATH 变量")
    print("\n方法2：设置环境变量")
    print("    export VSCODE_PATH='/path/to/your/code'  # Linux/Mac")
    print("    set VSCODE_PATH=C:\\path\\to\\Code.exe  # Windows")
    print("\n方法3：手动查找 VS Code 路径")
    if platform == "linux":
        print("    运行: which code")
    elif platform == "darwin":
        print("    运行: ls /Applications/Visual\\ Studio\\ Code.app/Contents/MacOS/")
    elif platform == "win32":
        print("    查看: C:\\Users\\YourUsername\\AppData\\Local\\Programs\\Microsoft VS Code\\")

    print("\n已尝试的路径:")
    for path in paths:
        print(f"  ✗ {path}")
    print("=" * 70 + "\n")

    raise FileNotFoundError("找不到 VS Code 可执行文件")


def wait_for_vscode_ready(page: Page, timeout: int = 15000):
    """
    等待 VS Code 主界面加载完成

    Args:
        page: Playwright Page 对象
        timeout: 超时时间（毫秒）
    """
    print("等待 VS Code 主界面加载...")

    # 尝试多个选择器，提高兼容性
    selectors = [
        'div.monaco-workbench',  # VS Code 主工作区
        'div.activitybar',       # 活动栏
        'div.editor-container',  # 编辑器容器
        '[id="workbench.parts.editor"]',  # 编辑器部分
    ]

    for selector in selectors:
        try:
            page.wait_for_selector(selector, state="attached", timeout=timeout)
            print(f"✓ 检测到界面元素: {selector}")
            return
        except Exception:
            continue

    # 如果所有选择器都失败，给一个警告但不抛出异常
    print("⚠️  警告：无法检测到 VS Code 特定元素，但应用可能已经加载完成")


# ============================================================================
# 主函数
# ============================================================================

def record_electron_app(playwright: Playwright, executable_path: str = None):
    """
    启动 Electron 应用并开始录制

    Args:
        playwright: Playwright 实例
        executable_path: Electron 应用的可执行文件路径（可选）
    """

    # --- 1. 确定可执行文件路径 ---
    if not executable_path:
        try:
            executable_path = find_vscode_executable()
        except FileNotFoundError:
            return

    print("\n" + "=" * 70)
    print("启动 VS Code (Electron 应用)")
    print("=" * 70)
    print(f"可执行文件: {executable_path}")
    print(f"操作系统: {sys.platform}")
    print("=" * 70 + "\n")

    # --- 2. 启动 Electron 应用 ---
    print("正在启动 Electron 应用...")

    try:
        # ✅ 正确方式：使用 electron API
        electron = playwright._impl._electron
        app = electron.launch(executable_path=executable_path)

        print("✓ Electron 应用已启动")

    except AttributeError:
        # 如果 _electron 不可用，尝试备用方法
        print("⚠️  当前 Playwright 版本可能不支持 _electron API")
        print("尝试使用 chromium launch 方法（可能不稳定）...\n")

        try:
            app = playwright.chromium.launch(
                executable_path=executable_path,
                headless=False
            )
            print("✓ 应用已启动（使用 chromium API）")
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            print("\n提示：请确保：")
            print("  1. 路径正确且文件存在")
            print("  2. 您有权限执行该文件")
            print("  3. Playwright 已正确安装 (playwright install)")
            return

    except Exception as e:
        print(f"❌ 启动 Electron 应用失败: {e}")
        print("\n提示：请确保：")
        print("  1. VS Code 路径正确")
        print("  2. 已安装 Playwright: pip install playwright")
        print("  3. 已安装浏览器: playwright install")
        return

    # --- 3. 等待并获取主窗口 ---
    page: Page = None

    try:
        print("\n等待应用主窗口...")

        # 方法1: 如果是 electron API，使用 first_window()
        if hasattr(app, 'first_window'):
            page = app.first_window()
            print("✓ 已获取主窗口（electron API）")

        # 方法2: 使用 context 等待 page 事件
        else:
            print("等待浏览器上下文创建...")

            # 轮询等待 contexts
            start_time = time.time()
            timeout = 20  # 秒

            while not app.contexts:
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"超时：{timeout}秒内未能检测到浏览器上下文")
                time.sleep(0.2)

            context = app.contexts[0]
            print("✓ 浏览器上下文已创建")

            # 等待页面
            print("等待主页面...")
            if context.pages:
                page = context.pages[0]
                print("✓ 使用现有页面")
            else:
                page = context.wait_for_event("page", timeout=20000)
                print("✓ 已捕获新页面")

        # 等待页面加载
        if page:
            wait_for_vscode_ready(page, timeout=15000)

            # 短暂延迟确保界面稳定
            print("等待界面稳定...")
            time.sleep(2)
            print("✓ VS Code 已就绪\n")

    except TimeoutError as e:
        print(f"❌ 超时错误: {e}")
        print("\n可能的原因：")
        print("  1. VS Code 启动较慢，请增加超时时间")
        print("  2. VS Code 启动时显示了欢迎页或设置向导")
        print("  3. 需要手动关闭弹窗或对话框")
        app.close()
        return

    except Exception as e:
        print(f"❌ 获取主窗口时出错: {e}")
        app.close()
        return

    # --- 4. 开始录制 ---
    if not page:
        print("❌ 错误：无法获取页面对象")
        app.close()
        return

    print("\n" + "=" * 70)
    print("🎬 准备开始录制")
    print("=" * 70)
    print("\nPlaywright Inspector 即将打开...")
    print("\n📝 使用说明：")
    print("  1. 点击 Inspector 窗口中的 '🔴 Record' 按钮")
    print("  2. 回到 VS Code 窗口执行您想录制的操作")
    print("  3. 操作完成后，Inspector 会显示生成的代码")
    print("  4. 复制生成的代码到您的脚本中")
    print("  5. 点击 'Resume' 或关闭 Inspector 继续")
    print("\n💡 提示：")
    print("  - 尽量点击文本而不是图标（生成的代码更稳定）")
    print("  - 避免依赖动态 ID 的元素")
    print("  - 使用搜索框可以提高定位器稳定性")
    print("=" * 70 + "\n")

    input("按 Enter 键打开 Playwright Inspector...")

    try:
        # 打开 Inspector 进行录制
        page.pause()

        print("\n✓ Inspector 已关闭或恢复执行")

    except KeyboardInterrupt:
        print("\n⚠️  用户中断录制")
    except Exception as e:
        print(f"\n❌ 录制过程中出错: {e}")

    # --- 5. 录制完成，展示下一步 ---
    print("\n" + "=" * 70)
    print("📋 下一步操作")
    print("=" * 70)
    print("\n1. 将 Inspector 中生成的代码粘贴到此处：")
    print("""
def recorded_actions(page: Page):
    \"\"\"
    在这里粘贴 Codegen 生成的代码
    \"\"\"
    # 示例：
    # page.get_by_role("button", name="File").click()
    # page.get_by_text("New File").click()
    pass
    """)

    print("\n2. 根据需要修复动态 ID 或不稳定的定位器")
    print("   参考: CODEGEN_FIX_CHEATSHEET.md")

    print("\n3. 测试您的代码：")
    print("   python your_script.py")

    print("\n" + "=" * 70)

    # 保持应用打开一段时间
    print("\nVS Code 将在 5 秒后关闭...")
    time.sleep(5)

    # --- 6. 清理 ---
    print("正在关闭应用...")
    try:
        app.close()
        print("✓ 应用已关闭")
    except Exception as e:
        print(f"⚠️  关闭应用时出错: {e}")


# ============================================================================
# 程序入口
# ============================================================================

def main():
    """主函数"""

    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   Playwright Electron Codegen 录制工具                               ║
║   适用于 VS Code 等 Electron 应用                                    ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)

    # 检查 Playwright 安装
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ 错误：未安装 Playwright")
        print("\n请运行以下命令安装：")
        print("  pip install playwright")
        print("  playwright install")
        return

    # 启动录制
    try:
        with sync_playwright() as playwright:
            record_electron_app(playwright)

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")

    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

    print("\n脚本执行完毕。")


if __name__ == "__main__":
    main()
