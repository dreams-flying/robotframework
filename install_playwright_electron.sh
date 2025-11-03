#!/bin/bash
# Playwright Electron API 自动安装脚本

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                       ║"
echo "║   Playwright Electron 自动安装脚本                                   ║"
echo "║                                                                       ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python
echo "========================================================================"
echo "步骤 1：检查 Python"
echo "========================================================================"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 未安装${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ ${PYTHON_VERSION}${NC}"
echo ""

# 卸载旧版本
echo "========================================================================"
echo "步骤 2：清理旧版本"
echo "========================================================================"
pip3 uninstall -y playwright 2>/dev/null
echo -e "${GREEN}✓ 清理完成${NC}"
echo ""

# 安装 Playwright
echo "========================================================================"
echo "步骤 3：安装 Playwright"
echo "========================================================================"
echo "正在安装 Playwright >= 1.40.0 ..."
pip3 install "playwright>=1.40.0"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Playwright 安装成功${NC}"
else
    echo -e "${RED}❌ Playwright 安装失败${NC}"
    exit 1
fi
echo ""

# 安装浏览器驱动
echo "========================================================================"
echo "步骤 4：安装浏览器驱动"
echo "========================================================================"
echo "正在安装 Chromium 驱动..."
python3 -m playwright install chromium

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 浏览器驱动安装成功${NC}"
else
    echo -e "${RED}❌ 浏览器驱动安装失败${NC}"
    exit 1
fi
echo ""

# 验证安装
echo "========================================================================"
echo "步骤 5：验证安装"
echo "========================================================================"

# 检查版本
PLAYWRIGHT_VERSION=$(pip3 show playwright 2>/dev/null | grep Version | awk '{print $2}')
echo "Playwright 版本: ${PLAYWRIGHT_VERSION}"

# 测试导入
echo "测试 Playwright 导入..."
python3 -c "from playwright.sync_api import sync_playwright; print('✓ 导入成功')"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Playwright 可以正常使用${NC}"
else
    echo -e "${RED}❌ Playwright 导入失败${NC}"
    exit 1
fi
echo ""

# 测试 Electron API
echo "========================================================================"
echo "步骤 6：测试 Electron API"
echo "========================================================================"

cat > /tmp/test_electron_api.py << 'EOTEST'
from playwright.sync_api import sync_playwright

success = False
method = 0

with sync_playwright() as p:
    # 测试方法 1
    if hasattr(p, '_impl') and hasattr(p._impl, '_electron'):
        print("✓ 方法 1 可用: playwright._impl._electron")
        method = 1
        success = True

    # 测试方法 2
    if hasattr(p, 'electron'):
        print("✓ 方法 2 可用: playwright.electron")
        if method == 0:
            method = 2
        success = True

    # 测试方法 3
    try:
        from playwright.sync_api import Electron
        print("✓ 方法 3 可用: Electron 类")
        if method == 0:
            method = 3
        success = True
    except ImportError:
        pass

if success:
    print(f"\n✓ Electron API 可用（方法 {method}）")
    exit(0)
else:
    print("\n❌ Electron API 不可用")
    exit(1)
EOTEST

python3 /tmp/test_electron_api.py
ELECTRON_TEST_RESULT=$?

if [ $ELECTRON_TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Electron API 测试通过${NC}"
else
    echo -e "${RED}❌ Electron API 测试失败${NC}"
    echo -e "${YELLOW}可能需要更新到更新的版本${NC}"
fi
echo ""

# 生成示例代码
echo "========================================================================"
echo "步骤 7：生成示例代码"
echo "========================================================================"

cat > electron_launch_example.py << 'EOEXAMPLE'
#!/usr/bin/env python3
"""
Playwright Electron 启动示例

使用方法：
    python electron_launch_example.py
"""

from playwright.sync_api import sync_playwright
import sys

def launch_vscode():
    """启动 VS Code 并打开 Playwright Inspector"""

    # VS Code 路径（请根据您的系统修改）
    vscode_paths = {
        "linux": "/usr/bin/code",
        "darwin": "/Applications/Visual Studio Code.app/Contents/MacOS/Electron",
        "win32": r"C:\Users\YourName\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    }

    vscode_path = vscode_paths.get(sys.platform)

    if not vscode_path:
        print(f"❌ 不支持的操作系统: {sys.platform}")
        return

    print(f"VS Code 路径: {vscode_path}")
    print("启动应用...")

    with sync_playwright() as playwright:
        try:
            # 方法 1：使用 _impl._electron（最常见）
            if hasattr(playwright, '_impl') and hasattr(playwright._impl, '_electron'):
                electron = playwright._impl._electron
                print("✓ 使用方法 1: playwright._impl._electron")

            # 方法 2：使用 playwright.electron
            elif hasattr(playwright, 'electron'):
                electron = playwright.electron
                print("✓ 使用方法 2: playwright.electron")

            else:
                print("❌ Electron API 不可用")
                return

            # 启动应用
            app = electron.launch(executable_path=vscode_path)
            print("✓ 应用已启动")

            # 获取主窗口
            page = app.first_window()
            print(f"✓ 主窗口已获取: {page.title()}")

            # 等待加载
            page.wait_for_load_state("domcontentloaded")
            print("✓ 页面已加载")

            # 打开 Inspector 进行录制
            print("\n" + "=" * 70)
            print("Playwright Inspector 即将打开...")
            print("在 Inspector 中点击 'Record' 按钮开始录制")
            print("=" * 70 + "\n")

            page.pause()

            # 关闭
            app.close()
            print("\n✓ 应用已关闭")

        except FileNotFoundError:
            print(f"❌ 找不到 VS Code: {vscode_path}")
            print("\n请修改脚本中的 vscode_path 为您的实际路径")
            print("或使用以下命令查找：")
            if sys.platform == "linux":
                print("  which code")
            elif sys.platform == "darwin":
                print("  ls '/Applications/Visual Studio Code.app/Contents/MacOS/'")

        except Exception as e:
            print(f"❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    launch_vscode()
EOEXAMPLE

chmod +x electron_launch_example.py
echo -e "${GREEN}✓ 示例代码已生成: electron_launch_example.py${NC}"
echo ""

# 总结
echo "========================================================================"
echo "安装完成！"
echo "========================================================================"
echo ""
echo "Playwright 版本: ${PLAYWRIGHT_VERSION}"
echo ""
echo "下一步："
echo "  1. 编辑 electron_launch_example.py，设置正确的 VS Code 路径"
echo "  2. 运行: python electron_launch_example.py"
echo "  3. 在 Inspector 中点击 'Record' 开始录制"
echo ""
echo "更多文档："
echo "  - ELECTRON_CODEGEN_QUICKSTART.md - 快速入门指南"
echo "  - ELECTRON_API_TROUBLESHOOTING.md - 故障排除指南"
echo "  - CODEGEN_FIX_CHEATSHEET.md - Codegen 修复速查表"
echo ""
echo "如遇问题，运行: python fix_electron_api.py"
echo "========================================================================"
