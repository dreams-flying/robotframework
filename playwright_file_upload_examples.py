"""
Playwright 文件上传实用示例
包含多种文件上传场景的完整代码示例
"""

from playwright.sync_api import sync_playwright, Page
import os
import tempfile
from pathlib import Path


# ==================== 示例 1: 基本文件上传 ====================

def example1_basic_upload():
    """最基本的文件上传示例"""
    print("\n" + "=" * 60)
    print("示例 1: 基本文件上传")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 创建测试文件
        test_file = "test_upload.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("这是测试文件内容")

        try:
            # 访问文件上传测试页面
            page.goto("https://the-internet.herokuapp.com/upload")

            # ✅ 方法1: 直接设置文件
            page.locator('#file-upload').set_input_files(test_file)

            # 点击上传按钮
            page.locator('#file-submit').click()

            # 验证上传成功
            page.wait_for_selector("text=File Uploaded!")
            print("✅ 文件上传成功！")

        finally:
            # 清理测试文件
            if os.path.exists(test_file):
                os.remove(test_file)
            browser.close()


# ==================== 示例 2: 使用 file_chooser 事件 ====================

def example2_file_chooser():
    """使用 file chooser 事件处理文件上传"""
    print("\n" + "=" * 60)
    print("示例 2: 使用 file_chooser 事件")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 创建测试文件
        test_file = "test_chooser.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("使用 file_chooser 上传的文件")

        try:
            page.goto("https://the-internet.herokuapp.com/upload")

            # ✅ 监听 file chooser 事件
            with page.expect_file_chooser() as fc_info:
                # 点击触发文件选择的元素
                page.locator('#file-upload').click()

            # 获取 file chooser 并设置文件
            file_chooser = fc_info.value
            file_chooser.set_files(test_file)

            # 提交
            page.locator('#file-submit').click()
            page.wait_for_selector("text=File Uploaded!")
            print("✅ 使用 file_chooser 上传成功！")

        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
            browser.close()


# ==================== 示例 3: 上传多个文件 ====================

def example3_multiple_files():
    """上传多个文件"""
    print("\n" + "=" * 60)
    print("示例 3: 上传多个文件")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 创建多个测试文件
        test_files = []
        for i in range(3):
            filename = f"test_file_{i+1}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"这是测试文件 {i+1}")
            test_files.append(filename)

        try:
            # 注意：这个测试网站只支持单文件，这里仅演示API用法
            page.goto("https://the-internet.herokuapp.com/upload")

            # ✅ 上传多个文件（传入文件列表）
            page.locator('#file-upload').set_input_files(test_files)

            print(f"✅ 已选择 {len(test_files)} 个文件")

            # 验证选择的文件数量
            file_count = page.evaluate("""
                document.querySelector('#file-upload').files.length
            """)
            print(f"   浏览器中选中的文件数: {file_count}")

        finally:
            # 清理测试文件
            for f in test_files:
                if os.path.exists(f):
                    os.remove(f)
            browser.close()


# ==================== 示例 4: 上传虚拟文件（Buffer）====================

def example4_upload_buffer():
    """不需要实际文件，直接上传内容"""
    print("\n" + "=" * 60)
    print("示例 4: 上传虚拟文件（Buffer）")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            page.goto("https://the-internet.herokuapp.com/upload")

            # ✅ 直接提供文件内容，不需要实际文件
            page.locator('#file-upload').set_input_files({
                'name': 'virtual_file.txt',
                'mimeType': 'text/plain',
                'buffer': b'This is virtual file content - no actual file needed!'
            })

            page.locator('#file-submit').click()
            page.wait_for_selector("text=File Uploaded!")
            print("✅ 虚拟文件上传成功！")

        finally:
            browser.close()


# ==================== 示例 5: 使用绝对路径 ====================

def example5_absolute_path():
    """使用绝对路径上传文件（推荐）"""
    print("\n" + "=" * 60)
    print("示例 5: 使用绝对路径")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 创建测试文件
        test_file = "test_absolute.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("使用绝对路径上传")

        try:
            page.goto("https://the-internet.herokuapp.com/upload")

            # ✅ 方法1: 使用 os.path.abspath
            abs_path = os.path.abspath(test_file)
            print(f"   绝对路径: {abs_path}")
            page.locator('#file-upload').set_input_files(abs_path)

            # ✅ 方法2: 使用 Path 对象
            # path_obj = Path(__file__).parent / test_file
            # page.locator('#file-upload').set_input_files(str(path_obj))

            page.locator('#file-submit').click()
            page.wait_for_selector("text=File Uploaded!")
            print("✅ 使用绝对路径上传成功！")

        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
            browser.close()


# ==================== 示例 6: 上传隐藏的 input 元素 ====================

def example6_hidden_input():
    """处理隐藏的文件输入元素"""
    print("\n" + "=" * 60)
    print("示例 6: 上传隐藏的 input 元素")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        test_file = "test_hidden.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("测试隐藏input上传")

        try:
            page.goto("https://the-internet.herokuapp.com/upload")

            # 先隐藏 input 元素，模拟真实场景
            page.evaluate("""
                document.querySelector('#file-upload').style.display = 'none';
            """)
            print("   已隐藏 input 元素")

            # ✅ 方法1: 使用 force=True 强制设置
            page.locator('#file-upload').set_input_files(test_file)
            print("   ✅ 即使元素隐藏，set_input_files 也能工作！")

            # 提交
            page.locator('#file-submit').click()
            page.wait_for_selector("text=File Uploaded!")
            print("✅ 隐藏元素上传成功！")

        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
            browser.close()


# ==================== 示例 7: 动态生成并上传文件 ====================

def example7_dynamic_file():
    """动态生成文件内容并上传"""
    print("\n" + "=" * 60)
    print("示例 7: 动态生成文件并上传")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # ✅ 使用临时文件
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.txt',
            delete=False,
            encoding='utf-8'
        ) as f:
            # 动态生成内容
            import datetime
            content = f"Generated at: {datetime.datetime.now()}\n"
            content += "This file was created dynamically!\n"
            f.write(content)
            temp_file_path = f.name

        try:
            page.goto("https://the-internet.herokuapp.com/upload")

            print(f"   临时文件路径: {temp_file_path}")
            page.locator('#file-upload').set_input_files(temp_file_path)

            page.locator('#file-submit').click()
            page.wait_for_selector("text=File Uploaded!")
            print("✅ 动态生成的文件上传成功！")

        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            browser.close()


# ==================== 示例 8: 验证上传的文件名 ====================

def example8_verify_filename():
    """验证选择的文件名"""
    print("\n" + "=" * 60)
    print("示例 8: 验证上传的文件名")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        test_file = "test_verification.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("验证文件名测试")

        try:
            page.goto("https://the-internet.herokuapp.com/upload")

            # 上传文件
            page.locator('#file-upload').set_input_files(test_file)

            # ✅ 验证选择的文件
            selected_file = page.evaluate("""
                () => {
                    const input = document.querySelector('#file-upload');
                    return input.files.length > 0 ? input.files[0].name : null;
                }
            """)

            print(f"   选择的文件名: {selected_file}")
            assert selected_file == test_file, f"文件名不匹配: {selected_file} != {test_file}"
            print("✅ 文件名验证通过！")

            # 提交
            page.locator('#file-submit').click()
            page.wait_for_selector("text=File Uploaded!")

        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
            browser.close()


# ==================== 示例 9: 清空已选择的文件 ====================

def example9_clear_files():
    """清空已选择的文件"""
    print("\n" + "=" * 60)
    print("示例 9: 清空已选择的文件")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        test_file = "test_clear.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("测试清空文件")

        try:
            page.goto("https://the-internet.herokuapp.com/upload")

            # 先选择文件
            page.locator('#file-upload').set_input_files(test_file)
            file_count = page.evaluate("document.querySelector('#file-upload').files.length")
            print(f"   已选择文件数: {file_count}")

            # ✅ 清空文件（传入空列表）
            page.locator('#file-upload').set_input_files([])
            file_count_after = page.evaluate("document.querySelector('#file-upload').files.length")
            print(f"   清空后文件数: {file_count_after}")

            assert file_count_after == 0, "文件未清空"
            print("✅ 文件清空成功！")

        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
            browser.close()


# ==================== 辅助函数：创建可复用的上传函数 ====================

def upload_file_helper(page: Page, locator: str, file_path: str, submit_button: str = None):
    """
    可复用的文件上传辅助函数

    Args:
        page: Playwright Page 对象
        locator: 文件输入元素的定位器
        file_path: 要上传的文件路径
        submit_button: 提交按钮的定位器（可选）
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    # 使用绝对路径
    abs_path = os.path.abspath(file_path)

    # 上传文件
    page.locator(locator).set_input_files(abs_path)

    # 验证文件已选择
    file_count = page.evaluate(f"""
        document.querySelector('{locator}').files.length
    """)

    if file_count == 0:
        raise Exception("文件未成功选择")

    print(f"✅ 文件已选择: {os.path.basename(file_path)}")

    # 如果提供了提交按钮，点击它
    if submit_button:
        page.locator(submit_button).click()
        print("✅ 已点击提交按钮")


def example10_using_helper():
    """使用辅助函数上传文件"""
    print("\n" + "=" * 60)
    print("示例 10: 使用可复用的辅助函数")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        test_file = "test_helper.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("使用辅助函数上传")

        try:
            page.goto("https://the-internet.herokuapp.com/upload")

            # ✅ 使用辅助函数
            upload_file_helper(
                page=page,
                locator='#file-upload',
                file_path=test_file,
                submit_button='#file-submit'
            )

            page.wait_for_selector("text=File Uploaded!")
            print("✅ 使用辅助函数上传成功！")

        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
            browser.close()


# ==================== 主函数 ====================

def main():
    """运行所有示例"""
    print("\n" + "=" * 80)
    print(" Playwright 文件上传示例集合")
    print("=" * 80)

    examples = [
        ("基本文件上传", example1_basic_upload),
        ("使用 file_chooser 事件", example2_file_chooser),
        ("上传多个文件", example3_multiple_files),
        ("上传虚拟文件（Buffer）", example4_upload_buffer),
        ("使用绝对路径", example5_absolute_path),
        ("上传隐藏的 input", example6_hidden_input),
        ("动态生成文件", example7_dynamic_file),
        ("验证文件名", example8_verify_filename),
        ("清空已选择的文件", example9_clear_files),
        ("使用辅助函数", example10_using_helper),
    ]

    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\n输入示例编号运行（1-10），或输入 'all' 运行所有示例，输入 'q' 退出:")

    while True:
        choice = input("\n请选择: ").strip().lower()

        if choice == 'q':
            print("退出程序")
            break
        elif choice == 'all':
            for name, func in examples:
                try:
                    func()
                except Exception as e:
                    print(f"❌ {name} 执行失败: {e}")
            break
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            name, func = examples[int(choice) - 1]
            try:
                func()
            except Exception as e:
                print(f"❌ {name} 执行失败: {e}")
        else:
            print("无效选择，请重新输入")


if __name__ == '__main__':
    main()
