"""
文件上传调试工具
帮助诊断和解决 "Node is not an HTMLInputElement" 错误

使用方法:
    python debug_file_upload.py
"""

from playwright.sync_api import sync_playwright
import sys


def debug_file_upload_interactive():
    """交互式文件上传调试工具"""

    print("\n" + "=" * 80)
    print(" Playwright 文件上传调试工具")
    print(" 帮助解决: Node is not an HTMLInputElement 错误")
    print("=" * 80)

    # 获取用户输入
    url = input("\n请输入页面 URL: ").strip()
    if not url:
        url = "https://the-internet.herokuapp.com/upload"
        print(f"使用默认 URL: {url}")

    locator_str = input("请输入你当前使用的定位器 (按 Enter 跳过): ").strip()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print(f"\n正在打开页面: {url}")
        page.goto(url)
        page.wait_for_load_state('networkidle')

        print("\n" + "=" * 80)
        print(" 诊断结果")
        print("=" * 80)

        # 1. 检查用户提供的定位器
        if locator_str:
            print(f"\n📍 步骤 1: 检查你的定位器 '{locator_str}'")
            print("-" * 80)
            try:
                locator = page.locator(locator_str)
                count = locator.count()

                if count == 0:
                    print(f"❌ 没有找到匹配的元素")
                else:
                    print(f"✅ 找到 {count} 个匹配的元素")

                    for i in range(min(count, 3)):  # 最多显示3个
                        print(f"\n   元素 #{i+1}:")
                        element = locator.nth(i)

                        # 获取元素信息
                        tag_name = element.evaluate("el => el.tagName")
                        print(f"      标签名: {tag_name}")

                        if tag_name.lower() == 'input':
                            input_type = element.evaluate("el => el.type")
                            print(f"      Input 类型: {input_type}")

                            if input_type.lower() == 'file':
                                print(f"      ✅ 这是正确的 file input！")
                            else:
                                print(f"      ❌ Input 类型不是 'file'")
                        else:
                            print(f"      ❌ 这不是 INPUT 元素！")
                            print(f"      💡 这就是为什么报错 'not an HTMLInputElement'")

                        # 显示 HTML
                        try:
                            outer_html = element.evaluate("el => el.outerHTML.substring(0, 200)")
                            print(f"      HTML: {outer_html}...")
                        except:
                            pass

            except Exception as e:
                print(f"❌ 检查定位器时出错: {e}")

        # 2. 查找所有 file input
        print(f"\n📂 步骤 2: 查找页面上所有的 <input type='file'> 元素")
        print("-" * 80)

        try:
            file_inputs = page.locator('input[type="file"]').all()
            print(f"找到 {len(file_inputs)} 个文件输入元素\n")

            if len(file_inputs) == 0:
                print("❌ 页面上没有 <input type='file'> 元素")
                print("   可能的原因:")
                print("   1. 页面还未完全加载")
                print("   2. 文件上传使用了非标准方式")
                print("   3. Input 元素是动态创建的")
            else:
                for i, inp in enumerate(file_inputs, 1):
                    print(f"文件输入 #{i}:")

                    # 获取属性
                    elem_id = inp.get_attribute('id')
                    elem_name = inp.get_attribute('name')
                    elem_class = inp.get_attribute('class')

                    # 检查可见性
                    is_visible = inp.is_visible()
                    display = inp.evaluate("el => window.getComputedStyle(el).display")

                    print(f"   ID: {elem_id or '(无)'}")
                    print(f"   Name: {elem_name or '(无)'}")
                    print(f"   Class: {elem_class or '(无)'}")
                    print(f"   可见: {is_visible} (display: {display})")

                    # 生成推荐的定位器
                    print(f"\n   💡 推荐的定位器:")
                    if elem_id:
                        print(f"      page.locator('#{elem_id}').set_input_files('file.pdf')")
                    elif elem_name:
                        print(f"      page.locator('input[name=\"{elem_name}\"]').set_input_files('file.pdf')")
                    else:
                        if len(file_inputs) == 1:
                            print(f"      page.locator('input[type=\"file\"]').set_input_files('file.pdf')")
                        else:
                            print(f"      page.locator('input[type=\"file\"]').nth({i-1}).set_input_files('file.pdf')")

                    print()

        except Exception as e:
            print(f"❌ 查找 file input 时出错: {e}")

        # 3. 检查是否有可点击的元素触发文件选择
        print(f"\n🔘 步骤 3: 查找可能触发文件选择的按钮")
        print("-" * 80)

        try:
            # 查找包含常见上传关键词的按钮
            upload_keywords = ["上传", "选择文件", "upload", "choose file", "browse", "添加文件"]

            buttons_found = False
            for keyword in upload_keywords:
                try:
                    buttons = page.get_by_role("button").filter(has_text=keyword).all()
                    if buttons:
                        buttons_found = True
                        print(f"\n找到包含 '{keyword}' 的按钮:")
                        for btn in buttons[:2]:  # 最多显示2个
                            text = btn.text_content()
                            print(f"   - '{text}'")
                            print(f"     这可能只是触发按钮，真正的 input 元素在其他地方")
                except:
                    pass

            if not buttons_found:
                print("未找到明显的上传按钮")

        except Exception as e:
            print(f"查找按钮时出错: {e}")

        # 4. 给出修复建议
        print("\n" + "=" * 80)
        print(" 🔧 修复建议")
        print("=" * 80)

        file_inputs_count = page.locator('input[type="file"]').count()

        if file_inputs_count == 0:
            print("\n❌ 问题: 页面上没有找到 <input type='file'> 元素")
            print("\n解决方案:")
            print("1. 等待页面完全加载:")
            print("   page.wait_for_selector('input[type=\"file\"]')")
            print("\n2. 检查 input 是否是动态创建的")
            print("\n3. 页面可能使用了非标准上传方式")

        elif file_inputs_count == 1:
            print("\n✅ 问题: 定位器选中了错误的元素")
            print("\n解决方案: 使用以下代码")
            print("\n修复前 (错误):")
            if locator_str:
                print(f"   page.locator('{locator_str}').set_input_files('file.pdf')")
            else:
                print("   page.get_by_role('button', name='Upload').set_input_files('file.pdf')")

            print("\n修复后 (正确):")
            print("   page.locator('input[type=\"file\"]').set_input_files('file.pdf')")

            # 如果有 id，提供更具体的建议
            first_input = page.locator('input[type="file"]').first
            elem_id = first_input.get_attribute('id')
            if elem_id:
                print(f"   # 或者更具体的:")
                print(f"   page.locator('#{elem_id}').set_input_files('file.pdf')")

        else:
            print(f"\n✅ 问题: 定位器选中了错误的元素")
            print(f"⚠️ 注意: 页面有 {file_inputs_count} 个文件输入元素")
            print("\n解决方案: 使用更具体的定位器")
            print("\n选项 1: 通过索引选择")
            print("   page.locator('input[type=\"file\"]').first.set_input_files('file.pdf')")
            print("   page.locator('input[type=\"file\"]').nth(1).set_input_files('file.pdf')")

            print("\n选项 2: 通过 id 或 name 选择")
            for i in range(min(file_inputs_count, 3)):
                inp = page.locator('input[type="file"]').nth(i)
                elem_id = inp.get_attribute('id')
                elem_name = inp.get_attribute('name')
                if elem_id:
                    print(f"   page.locator('#{elem_id}').set_input_files('file.pdf')  # 第 {i+1} 个")
                elif elem_name:
                    print(f"   page.locator('input[name=\"{elem_name}\"]').set_input_files('file.pdf')  # 第 {i+1} 个")

        # 5. 提供完整的示例代码
        print("\n" + "=" * 80)
        print(" 📝 完整示例代码")
        print("=" * 80)

        print("\nfrom playwright.sync_api import sync_playwright")
        print("import os")
        print("\nwith sync_playwright() as p:")
        print("    browser = p.chromium.launch(headless=False)")
        print("    page = browser.new_page()")
        print(f"    page.goto('{url}')")
        print()
        print("    # 上传文件")
        print("    file_path = os.path.abspath('your_file.pdf')")

        if file_inputs_count > 0:
            first_input = page.locator('input[type="file"]').first
            elem_id = first_input.get_attribute('id')
            if elem_id:
                print(f"    page.locator('#{elem_id}').set_input_files(file_path)")
            else:
                print(f"    page.locator('input[type=\"file\"]').set_input_files(file_path)")
        else:
            print("    # 等待 input 元素出现")
            print("    page.wait_for_selector('input[type=\"file\"]')")
            print("    page.locator('input[type=\"file\"]').set_input_files(file_path)")

        print()
        print("    # 提交（如果需要）")
        print("    # page.get_by_role('button', name='Submit').click()")
        print()
        print("    browser.close()")

        print("\n" + "=" * 80)
        input("\n按 Enter 关闭浏览器...")
        browser.close()


def debug_specific_url(url: str, locator_str: str = None):
    """
    调试特定 URL 的文件上传

    Args:
        url: 要调试的页面 URL
        locator_str: 当前使用的定位器（可选）
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)

        print("=" * 80)
        print(f"调试 URL: {url}")
        print("=" * 80)

        # 查找所有 file input
        file_inputs = page.locator('input[type="file"]').all()
        print(f"\n找到 {len(file_inputs)} 个文件输入元素:")

        for i, inp in enumerate(file_inputs, 1):
            elem_id = inp.get_attribute('id') or '(无)'
            elem_name = inp.get_attribute('name') or '(无)'
            is_visible = inp.is_visible()

            print(f"\n#{i}:")
            print(f"  ID: {elem_id}")
            print(f"  Name: {elem_name}")
            print(f"  可见: {is_visible}")

        # 如果提供了定位器，检查它
        if locator_str:
            print(f"\n检查定位器: {locator_str}")
            try:
                locator = page.locator(locator_str)
                count = locator.count()
                print(f"匹配 {count} 个元素")

                if count > 0:
                    tag_name = locator.first.evaluate("el => el.tagName")
                    print(f"标签名: {tag_name}")
            except Exception as e:
                print(f"错误: {e}")

        input("\n按 Enter 关闭...")
        browser.close()


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print(" Playwright 文件上传调试工具")
    print("=" * 80)
    print("\n选择模式:")
    print("  1. 交互式调试（推荐）")
    print("  2. 快速测试 (使用默认测试网站)")
    print("  3. 退出")

    choice = input("\n请选择 (1-3): ").strip()

    if choice == '1':
        debug_file_upload_interactive()
    elif choice == '2':
        print("\n使用测试网站: https://the-internet.herokuapp.com/upload")
        debug_specific_url("https://the-internet.herokuapp.com/upload")
    elif choice == '3':
        print("退出")
        sys.exit(0)
    else:
        print("无效选择")
        main()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
