#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试 PyInspect Recorder 生成的代码
帮助诊断元素定位失败的问题

使用方法：
1. 将 Recorder 生成的代码粘贴到下方
2. 运行此脚本查看详细错误信息
"""

from pywinauto import Application, Desktop
from pywinauto.findwindows import ElementNotFoundError
import time
import sys

def debug_element_locator(window, locator_dict, backend='uia'):
    """
    调试元素定位器

    参数：
        window: 父窗口
        locator_dict: 定位器字典，如 {'auto_id': 'btnSave'}
        backend: 后端类型
    """
    print(f"\n{'='*60}")
    print(f"🔍 调试定位器: {locator_dict}")
    print(f"{'='*60}")

    try:
        # 尝试定位元素
        element = window.child_window(**locator_dict)

        # 检查元素是否存在
        if element.exists(timeout=2):
            print("✅ 元素找到！")

            # 打印元素信息
            try:
                print(f"\n📋 元素属性:")
                print(f"  - Automation ID: {element.element_info.automation_id}")
                print(f"  - Class Name: {element.element_info.class_name}")
                print(f"  - Control Type: {element.element_info.control_type}")
                print(f"  - Name: {element.element_info.name}")
                print(f"  - Visible: {element.is_visible()}")
                print(f"  - Enabled: {element.is_enabled()}")
            except Exception as e:
                print(f"⚠️ 无法获取元素属性: {e}")

            # 检查元素是否可点击
            try:
                element.wait('visible', timeout=2)
                print(f"\n✅ 元素可见")
            except Exception as e:
                print(f"\n❌ 元素不可见: {e}")

            try:
                element.wait('enabled', timeout=2)
                print(f"✅ 元素已启用")
            except Exception as e:
                print(f"❌ 元素未启用: {e}")

            # 尝试点击
            try:
                print(f"\n🖱️ 尝试点击...")
                element.click()
                print(f"✅ 点击成功！")
                return True
            except Exception as e:
                print(f"❌ 点击失败: {e}")

                # 尝试备选方案
                print(f"\n🔄 尝试备选点击方法...")
                try:
                    element.click_input()
                    print(f"✅ click_input() 成功！")
                    return True
                except Exception as e2:
                    print(f"❌ click_input() 失败: {e2}")

                return False
        else:
            print("❌ 元素不存在！")

            # 搜索相似元素
            print(f"\n🔍 搜索相似元素...")
            try:
                all_children = window.children()
                print(f"找到 {len(all_children)} 个子元素\n")

                # 按控制类型分组
                for key, value in locator_dict.items():
                    if key == 'control_type':
                        matching = [c for c in all_children
                                  if c.element_info.control_type == value]
                        print(f"相同 control_type ({value}) 的元素: {len(matching)} 个")
                        for i, c in enumerate(matching[:5]):  # 最多显示5个
                            print(f"  [{i+1}] AutomationId: {c.element_info.automation_id}, "
                                  f"Name: {c.element_info.name}")
            except Exception as e:
                print(f"⚠️ 无法搜索相似元素: {e}")

            return False

    except Exception as e:
        print(f"❌ 定位器错误: {e}")
        return False


def suggest_better_locator(window, original_locator):
    """建议更好的定位器"""
    print(f"\n💡 建议的定位器：")

    # 如果只有 class_name 和 control_type，尝试找其他属性
    if 'auto_id' not in original_locator and 'title' not in original_locator:
        try:
            # 尝试获取所有匹配的元素
            elements = window.child_window(**original_locator).wrapper_object()

            if hasattr(elements, 'element_info'):
                auto_id = elements.element_info.automation_id
                name = elements.element_info.name

                if auto_id:
                    print(f"  ✅ 推荐使用 AutomationId: auto_id='{auto_id}'")
                elif name:
                    print(f"  ✅ 推荐使用 Name: title='{name}'")
                else:
                    print(f"  ⚠️ 建议手动使用 PyInspect Enhanced 检查元素")
        except:
            pass


def test_window_connection(process_id=None, title=None, backend='uia'):
    """测试窗口连接"""
    print(f"\n{'='*60}")
    print(f"🔗 测试窗口连接")
    print(f"{'='*60}")

    try:
        if process_id:
            print(f"尝试连接 Process ID: {process_id}")
            app = Application(backend=backend).connect(process=process_id)
            print(f"✅ 连接成功")
        elif title:
            print(f"尝试连接窗口标题: {title}")
            app = Application(backend=backend).connect(title_re=f'.*{title}.*')
            print(f"✅ 连接成功")
        else:
            print(f"❌ 需要提供 process_id 或 title")
            return None

        # 获取窗口
        if title:
            window = app.window(title_re=f'.*{title}.*')
        else:
            window = app.top_window()

        window.wait('visible', timeout=5)
        print(f"✅ 窗口已找到并可见")
        print(f"   标题: {window.window_text()}")

        return window

    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print(f"\n💡 可能的原因：")
        print(f"  1. 应用程序已关闭（Process ID 失效）")
        print(f"  2. 窗口标题不匹配")
        print(f"  3. Backend 选择错误（尝试切换 uia ↔ win32）")
        return None


# ============ 示例：调试你的代码 ============

def debug_your_code():
    """
    将 Recorder 生成的代码粘贴到这里进行调试
    """

    # 步骤 1: 连接应用（修改这里）
    # ❌ Recorder 生成的方式（Process ID 会失效）
    # app = Application(backend='uia').connect(process=12345)

    # ✅ 推荐的方式 1：启动应用
    # app = Application(backend='uia').start('notepad.exe')

    # ✅ 推荐的方式 2：通过窗口标题连接
    # app = Application(backend='uia').connect(title_re='.*记事本.*')

    # 调试示例：记事本
    print("="*60)
    print("🐛 开始调试...")
    print("="*60)

    # 选择一个方式
    backend = 'uia'  # 或 'win32'

    # 方式 1: 如果应用正在运行，通过标题连接
    window_title = '记事本'  # 修改为你的应用窗口标题
    window = test_window_connection(title=window_title, backend=backend)

    # 方式 2: 如果应用未运行，启动它
    # app = Application(backend='uia').start('notepad.exe')
    # window = app.window(title_re='.*记事本.*')

    if not window:
        print("\n❌ 无法连接窗口，调试终止")
        return

    # 步骤 2: 测试定位器（将 Recorder 生成的定位器粘贴到这里）

    # 示例 1: 测试 AutomationId 定位器
    debug_element_locator(
        window,
        {'auto_id': 'btnSave'},  # 修改为你的定位器
        backend=backend
    )

    # 示例 2: 测试 Class + Control Type 定位器
    debug_element_locator(
        window,
        {'class_name': 'Edit', 'control_type': 'Edit'},
        backend=backend
    )

    # 示例 3: 测试 Title 定位器
    debug_element_locator(
        window,
        {'title': '保存'},
        backend=backend
    )


def interactive_debug():
    """交互式调试"""
    print("="*60)
    print("🎯 PyInspect Recorder 代码调试工具")
    print("="*60)

    # 1. 选择 Backend
    print("\n1️⃣ 选择 Backend:")
    print("  1 - UIA (推荐，现代应用)")
    print("  2 - Win32 (老旧应用)")
    backend_choice = input("请选择 (1/2，默认 1): ").strip() or "1"
    backend = 'uia' if backend_choice == "1" else 'win32'
    print(f"✅ 使用 Backend: {backend}")

    # 2. 连接窗口
    print("\n2️⃣ 连接应用窗口:")
    print("  1 - 通过窗口标题连接（推荐）")
    print("  2 - 通过 Process ID 连接")
    print("  3 - 启动新应用")
    conn_choice = input("请选择 (1/2/3): ").strip()

    window = None
    if conn_choice == "1":
        title = input("请输入窗口标题（部分匹配即可）: ").strip()
        window = test_window_connection(title=title, backend=backend)
    elif conn_choice == "2":
        pid = input("请输入 Process ID: ").strip()
        try:
            window = test_window_connection(process_id=int(pid), backend=backend)
        except ValueError:
            print("❌ Process ID 必须是数字")
    elif conn_choice == "3":
        exe_path = input("请输入应用程序路径（如 notepad.exe）: ").strip()
        try:
            app = Application(backend=backend).start(exe_path)
            window = app.top_window()
            window.wait('visible', timeout=5)
            print(f"✅ 应用已启动，窗口标题: {window.window_text()}")
        except Exception as e:
            print(f"❌ 启动失败: {e}")

    if not window:
        print("\n❌ 无法连接窗口，请检查应用是否运行")
        return

    # 3. 测试定位器
    print("\n3️⃣ 测试元素定位器:")
    print("请输入定位器类型:")
    print("  1 - AutomationId")
    print("  2 - Class Name + Control Type")
    print("  3 - Title/Name")
    print("  4 - 查看所有子元素")

    while True:
        loc_choice = input("\n请选择 (1/2/3/4，输入 q 退出): ").strip()

        if loc_choice.lower() == 'q':
            break

        if loc_choice == "1":
            auto_id = input("请输入 AutomationId: ").strip()
            debug_element_locator(window, {'auto_id': auto_id}, backend)

        elif loc_choice == "2":
            class_name = input("请输入 Class Name: ").strip()
            control_type = input("请输入 Control Type: ").strip()
            debug_element_locator(window, {
                'class_name': class_name,
                'control_type': control_type
            }, backend)

        elif loc_choice == "3":
            title = input("请输入 Title/Name: ").strip()
            debug_element_locator(window, {'title': title}, backend)

        elif loc_choice == "4":
            try:
                children = window.children()
                print(f"\n找到 {len(children)} 个子元素：\n")
                for i, child in enumerate(children[:20]):  # 最多显示20个
                    try:
                        print(f"[{i+1}] Type: {child.element_info.control_type:20} "
                              f"AutoId: {child.element_info.automation_id:20} "
                              f"Name: {child.element_info.name}")
                    except:
                        pass
                if len(children) > 20:
                    print(f"\n... 还有 {len(children)-20} 个元素")
            except Exception as e:
                print(f"❌ 获取子元素失败: {e}")


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║  PyInspect Recorder 代码调试工具                             ║
╚══════════════════════════════════════════════════════════════╝

使用方式：

方式 1 - 交互式调试（推荐）
    直接运行此脚本，按提示操作

方式 2 - 修改代码调试
    编辑 debug_your_code() 函数，粘贴 Recorder 生成的代码

方式 3 - 导入为模块
    from debug_recorder_code import debug_element_locator
    debug_element_locator(window, {'auto_id': 'btnSave'})

""")

    choice = input("选择方式 (1-交互式 / 2-修改代码调试，默认 1): ").strip() or "1"

    if choice == "1":
        interactive_debug()
    else:
        debug_your_code()

    print("\n" + "="*60)
    print("🎉 调试完成！")
    print("="*60)
