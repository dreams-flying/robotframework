#!/usr/bin/env python3
"""
Pywinauto + Swapy 完整示例代码
Windows 桌面应用自动化 - 从录制到执行

作者: Claude Code
日期: 2025-01-04
"""

# ============================================================================
# 安装依赖
# ============================================================================
"""
pip install pywinauto
pip install pillow  # 可选：用于图像识别
pip install pyautogui  # 可选：用于高级自动化

# Swapy 下载地址（独立工具，不需要 pip 安装）
https://github.com/pywinauto/SWAPY/releases
"""

# ============================================================================
# 示例 1：记事本自动化（完整流程）
# ============================================================================

from pywinauto import Application
from pywinauto.keyboard import send_keys
import time

def automate_notepad_complete():
    """
    完整的记事本自动化示例
    演示从启动应用到保存文件的完整流程
    """

    print("=" * 70)
    print("示例 1：记事本自动化")
    print("=" * 70)

    # 步骤 1：启动应用
    print("\n步骤 1：启动记事本...")
    app = Application(backend='uia').start('notepad.exe')

    # 等待应用启动
    time.sleep(1)

    # 步骤 2：获取主窗口
    print("步骤 2：连接到主窗口...")
    # 方法 A：通过窗口标题
    main_window = app.window(title_re='.*Notepad')  # 兼容不同语言版本
    # 或
    # main_window = app['Notepad']

    # 步骤 3：在文本框中输入内容
    print("步骤 3：输入文本...")
    edit = main_window.child_window(class_name="Edit")
    edit.type_keys("Hello from Pywinauto!{ENTER}")
    edit.type_keys("This is line 2.{ENTER}")
    edit.type_keys("这是第三行（支持中文）。{ENTER}")

    time.sleep(1)

    # 步骤 4：使用菜单
    print("步骤 4：通过菜单保存文件...")
    # 方法 A：使用菜单项
    main_window.menu_select("File->Save As")

    # 等待"另存为"对话框
    time.sleep(1)

    # 步骤 5：填写文件名
    print("步骤 5：填写文件名...")
    save_dialog = app.window(title_re='Save As')

    # 方法 B：通过控件类型查找
    filename_edit = save_dialog.child_window(class_name="Edit", found_index=0)
    filename_edit.set_text("test_pywinauto.txt")

    # 步骤 6：点击保存按钮
    print("步骤 6：点击保存...")
    save_button = save_dialog.child_window(title="Save", class_name="Button")
    save_button.click()

    time.sleep(1)

    # 步骤 7：关闭应用
    print("步骤 7：关闭应用...")
    main_window.close()

    print("\n✓ 完成！文件已保存为 test_pywinauto.txt")
    print("=" * 70)


# ============================================================================
# 示例 2：计算器自动化（使用 Swapy 生成的代码）
# ============================================================================

def automate_calculator_swapy_style():
    """
    计算器自动化 - Swapy 风格
    这是使用 Swapy 工具录制后生成的代码样式
    """

    print("\n" + "=" * 70)
    print("示例 2：计算器自动化（Swapy 风格）")
    print("=" * 70)

    # Swapy 生成的代码通常是这样的：
    print("\n启动计算器...")
    app = Application(backend='uia').start('calc.exe')

    time.sleep(1)

    # Swapy 会帮你找到这些 AutomationId
    print("执行计算: 8 + 2 = ?")

    # 连接到主窗口
    calc_window = app.window(class_name='ApplicationFrameWindow')

    # 通过 AutomationId 定位按钮（这些 ID 是 Swapy 帮你找到的）
    calc_window.child_window(auto_id="num8Button", control_type="Button").click()
    time.sleep(0.3)

    calc_window.child_window(auto_id="plusButton", control_type="Button").click()
    time.sleep(0.3)

    calc_window.child_window(auto_id="num2Button", control_type="Button").click()
    time.sleep(0.3)

    calc_window.child_window(auto_id="equalButton", control_type="Button").click()
    time.sleep(0.3)

    # 读取结果
    result_text = calc_window.child_window(auto_id="CalculatorResults").window_text()
    print(f"✓ 计算结果: {result_text}")

    time.sleep(2)

    # 关闭
    calc_window.close()
    print("=" * 70)


# ============================================================================
# 示例 3：使用 Swapy 查找元素（手动步骤）
# ============================================================================

def how_to_use_swapy():
    """
    如何使用 Swapy 查找元素

    Swapy 使用步骤：
    1. 下载并运行 Swapy.exe
    2. 点击 "Record" 按钮
    3. 将十字准星拖到目标元素上
    4. Swapy 会显示该元素的所有属性
    5. 右侧会生成 Pywinauto 代码
    6. 复制代码到你的脚本中

    示例：Swapy 生成的代码片段
    """

    print("\n" + "=" * 70)
    print("示例 3：Swapy 使用方法")
    print("=" * 70)

    # 这是 Swapy 生成的典型代码
    swapy_generated_code = '''
# Swapy 自动生成的代码示例：

from pywinauto import Application

# 1. 连接到已运行的应用
app = Application(backend='uia').connect(title='Calculator')

# 2. 获取主窗口
main_window = app.window(title='Calculator', class_name='ApplicationFrameWindow')

# 3. 点击按钮（Swapy 会告诉你具体的 AutomationId）
button_8 = main_window.child_window(auto_id="num8Button", control_type="Button")
button_8.click()

# 4. 输入文本
text_box = main_window.child_window(auto_id="MyTextBox", control_type="Edit")
text_box.set_text("Hello World")

# 5. 读取文本
result = main_window.child_window(auto_id="ResultField").window_text()
print(f"结果: {result}")
    '''

    print(swapy_generated_code)
    print("=" * 70)


# ============================================================================
# 示例 4：高级技巧 - 元素查找方法
# ============================================================================

def advanced_element_finding():
    """
    高级元素查找技巧
    演示多种定位元素的方法
    """

    print("\n" + "=" * 70)
    print("示例 4：高级元素查找方法")
    print("=" * 70)

    # 启动记事本用于演示
    app = Application(backend='uia').start('notepad.exe')
    time.sleep(1)
    main_window = app.window(title_re='.*Notepad')

    # 方法 1：通过类名
    print("\n方法 1：通过类名查找")
    edit_by_class = main_window.child_window(class_name="Edit")
    print(f"  找到元素: {edit_by_class.element_info.name}")

    # 方法 2：通过控件类型
    print("\n方法 2：通过控件类型查找")
    edit_by_type = main_window.child_window(control_type="Edit")
    print(f"  找到元素: {edit_by_type.element_info.control_type}")

    # 方法 3：通过标题（部分匹配）
    print("\n方法 3：通过标题部分匹配")
    window_by_title = app.window(title_re='.*Note.*')
    print(f"  找到窗口: {window_by_title.window_text()}")

    # 方法 4：通过索引（当有多个相同元素时）
    print("\n方法 4：通过索引查找")
    # edit_by_index = main_window.child_window(class_name="Edit", found_index=0)
    # print(f"  找到第一个 Edit 控件")

    # 方法 5：链式查找（父 -> 子 -> 孙）
    print("\n方法 5：链式查找")
    # 先找父容器，再找子元素
    # container = main_window.child_window(class_name="Container")
    # button_in_container = container.child_window(title="OK")

    # 方法 6：使用 print_control_identifiers 查看所有元素
    print("\n方法 6：打印所有可用控件")
    print("  调用 main_window.print_control_identifiers() 可以查看:")
    print("  - 所有子控件的属性")
    print("  - AutomationId")
    print("  - 类名")
    print("  - 控件类型")

    # 实际调用（会输出很多信息）
    # main_window.print_control_identifiers()

    # 关闭
    main_window.close()
    print("\n=" * 70)


# ============================================================================
# 示例 5：实际应用场景 - 批量处理文件
# ============================================================================

def batch_process_files():
    """
    实际应用：批量在记事本中处理文件
    """

    print("\n" + "=" * 70)
    print("示例 5：批量处理文件")
    print("=" * 70)

    files_to_process = [
        "file1.txt",
        "file2.txt",
        "file3.txt"
    ]

    for filename in files_to_process:
        print(f"\n处理文件: {filename}")

        # 启动记事本
        app = Application(backend='uia').start('notepad.exe')
        time.sleep(1)

        main_window = app.window(title_re='.*Notepad')

        # 输入内容
        edit = main_window.child_window(class_name="Edit")
        edit.type_keys(f"Processing {filename}{ENTER}")
        edit.type_keys(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}{ENTER}")

        # 保存
        main_window.menu_select("File->Save As")
        time.sleep(1)

        save_dialog = app.window(title_re='Save As')
        filename_edit = save_dialog.child_window(class_name="Edit", found_index=0)
        filename_edit.set_text(filename)

        save_button = save_dialog.child_window(title="Save", class_name="Button")
        save_button.click()

        time.sleep(1)

        # 关闭
        main_window.close()

        print(f"  ✓ {filename} 已保存")

    print("\n✓ 批量处理完成！")
    print("=" * 70)


# ============================================================================
# 示例 6：错误处理和重试机制
# ============================================================================

def robust_automation_with_retry():
    """
    健壮的自动化代码 - 包含错误处理和重试
    """

    print("\n" + "=" * 70)
    print("示例 6：带错误处理的健壮自动化")
    print("=" * 70)

    from pywinauto.timings import TimeoutError
    import traceback

    max_retries = 3
    retry_delay = 2

    for attempt in range(1, max_retries + 1):
        try:
            print(f"\n尝试 {attempt}/{max_retries}...")

            # 启动应用
            app = Application(backend='uia').start('notepad.exe')

            # 等待窗口出现（带超时）
            main_window = app.window(title_re='.*Notepad')
            main_window.wait('ready', timeout=10)  # 等待最多 10 秒

            # 检查窗口是否可见
            if not main_window.is_visible():
                raise Exception("窗口不可见")

            # 输入文本
            edit = main_window.child_window(class_name="Edit")
            edit.wait('enabled', timeout=5)  # 等待控件启用
            edit.type_keys("成功！")

            print("  ✓ 操作成功")

            time.sleep(2)
            main_window.close()

            # 成功，跳出循环
            break

        except TimeoutError as e:
            print(f"  ✗ 超时错误: {e}")
            if attempt < max_retries:
                print(f"  等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            else:
                print("  ✗ 已达到最大重试次数")

        except Exception as e:
            print(f"  ✗ 错误: {e}")
            traceback.print_exc()
            if attempt < max_retries:
                time.sleep(retry_delay)

            # 确保清理
            try:
                if 'main_window' in locals():
                    main_window.close()
            except:
                pass

    print("\n=" * 70)


# ============================================================================
# 示例 7：使用 inspect.exe 查找元素（Windows SDK 工具）
# ============================================================================

def how_to_use_inspect_tool():
    """
    如何使用 Windows SDK 的 Inspect.exe 工具

    Inspect.exe 是 Windows SDK 自带的工具，类似 Swapy

    位置：
    C:\\Program Files (x86)\\Windows Kits\\10\\bin\\<version>\\x64\\inspect.exe

    使用方法：
    1. 运行 inspect.exe
    2. 将鼠标悬停在目标元素上
    3. 查看右侧属性面板
    4. 记录 AutomationId、ClassName、Name 等属性
    5. 在代码中使用这些属性定位元素
    """

    print("\n" + "=" * 70)
    print("示例 7：使用 Inspect.exe 查找元素")
    print("=" * 70)

    print("""
    Inspect.exe 使用步骤：

    1. 找到 Inspect.exe:
       C:\\Program Files (x86)\\Windows Kits\\10\\bin\\<version>\\x64\\inspect.exe

       或者使用 Accessibility Insights:
       https://accessibilityinsights.io/downloads/

    2. 运行工具，鼠标移到目标元素

    3. 查看属性：
       - AutomationId: "num8Button"
       - ClassName: "Button"
       - Name: "Eight"
       - ControlType: Button

    4. 在代码中使用：
    """)

    code_example = '''
    # 使用 Inspect.exe 找到的属性
    button = window.child_window(
        auto_id="num8Button",      # AutomationId
        control_type="Button",     # ControlType
        # class_name="Button",     # ClassName
        # title="Eight"            # Name
    )
    button.click()
    '''

    print(code_example)
    print("=" * 70)


# ============================================================================
# 示例 8：连接到已运行的应用
# ============================================================================

def connect_to_running_app():
    """
    连接到已经运行的应用（而不是启动新的）
    """

    print("\n" + "=" * 70)
    print("示例 8：连接到已运行的应用")
    print("=" * 70)

    try:
        # 方法 1：通过进程名连接
        print("\n方法 1：通过进程名连接")
        app = Application(backend='uia').connect(path='notepad.exe')
        print("  ✓ 已连接到 notepad.exe")

        # 方法 2：通过窗口标题连接
        print("\n方法 2：通过窗口标题连接")
        app = Application(backend='uia').connect(title_re='.*Notepad')
        print("  ✓ 已连接到标题包含 'Notepad' 的窗口")

        # 方法 3：通过进程 ID 连接
        print("\n方法 3：通过进程 ID 连接")
        # 首先需要知道 PID
        # import psutil
        # for proc in psutil.process_iter(['pid', 'name']):
        #     if proc.info['name'] == 'notepad.exe':
        #         app = Application(backend='uia').connect(process=proc.info['pid'])

        # 获取窗口
        main_window = app.window(title_re='.*Notepad')
        print(f"  ✓ 窗口标题: {main_window.window_text()}")

    except Exception as e:
        print(f"  ✗ 连接失败: {e}")
        print("  提示：请先手动打开记事本")

    print("\n=" * 70)


# ============================================================================
# 示例 9：完整的实战示例 - 自动化 Windows 设置
# ============================================================================

def automate_windows_settings():
    """
    实战示例：自动化打开 Windows 设置并导航
    """

    print("\n" + "=" * 70)
    print("示例 9：自动化 Windows 设置")
    print("=" * 70)

    try:
        # 启动 Windows 设置
        print("\n启动 Windows 设置...")
        app = Application(backend='uia').start('ms-settings:')

        time.sleep(2)

        # 连接到设置窗口
        settings_window = app.window(title_re='Settings')
        print("✓ 已连接到设置窗口")

        # 查找搜索框
        print("\n查找并点击搜索框...")
        search_box = settings_window.child_window(auto_id="SearchBox", control_type="Edit")
        search_box.click()
        search_box.type_keys("display")

        time.sleep(2)

        print("✓ 已搜索 'display'")

        time.sleep(3)

        # 关闭
        settings_window.close()
        print("\n✓ 完成！")

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        print("  提示：这个示例需要 Windows 10/11")

    print("=" * 70)


# ============================================================================
# 主函数 - 运行所有示例
# ============================================================================

def main():
    """运行所有示例"""

    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   Pywinauto + Swapy 完整教程                                         ║
║   Windows 桌面应用自动化                                             ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)

    print("\n可用示例：")
    print("  1. 记事本自动化（完整流程）")
    print("  2. 计算器自动化（Swapy 风格）")
    print("  3. Swapy 使用方法")
    print("  4. 高级元素查找方法")
    print("  5. 批量处理文件")
    print("  6. 错误处理和重试机制")
    print("  7. 使用 Inspect.exe 工具")
    print("  8. 连接到已运行的应用")
    print("  9. 自动化 Windows 设置")
    print("  0. 运行所有示例")

    choice = input("\n请选择示例编号 (0-9): ").strip()

    examples = {
        '1': automate_notepad_complete,
        '2': automate_calculator_swapy_style,
        '3': how_to_use_swapy,
        '4': advanced_element_finding,
        '5': batch_process_files,
        '6': robust_automation_with_retry,
        '7': how_to_use_inspect_tool,
        '8': connect_to_running_app,
        '9': automate_windows_settings,
    }

    if choice == '0':
        # 运行所有示例（除了需要用户交互的）
        for func in [
            how_to_use_swapy,
            how_to_use_inspect_tool,
            # automate_notepad_complete,  # 取消注释以运行
            # automate_calculator_swapy_style,  # 取消注释以运行
        ]:
            func()
    elif choice in examples:
        examples[choice]()
    else:
        print("\n无效的选择")

    print("\n" + "=" * 70)
    print("感谢使用！")
    print("=" * 70)


if __name__ == "__main__":
    # 运行主函数
    # main()

    # 或者直接运行特定示例：

    # 示例 1：记事本自动化
    # automate_notepad_complete()

    # 示例 2：计算器自动化
    # automate_calculator_swapy_style()

    # 示例 3：Swapy 使用说明
    how_to_use_swapy()

    # 示例 7：Inspect.exe 使用说明
    how_to_use_inspect_tool()
