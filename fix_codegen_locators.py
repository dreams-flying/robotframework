#!/usr/bin/env python3
"""
Playwright Codegen 定位器失败 - 常见问题修复示例

5 种最常见的失败原因及解决方案
"""

from playwright.sync_api import sync_playwright, Page
import time
import re


# ============================================================================
# 失败原因 1：动态 ID（最常见）
# ============================================================================

def fix_dynamic_id():
    """修复动态 ID 问题"""

    print("\n" + "=" * 70)
    print("失败原因 1：动态 ID")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 假设打开某个页面
        # page.goto("https://your-portal.com")

        # ❌ Codegen 生成的失败代码
        print("\n❌ Codegen 生成（会失败）:")
        print('''
        page.locator("[id=\\"142258285_tree\\"]").click()
        page.locator("[id=\\"142258285_tree\\"]").get_by_text("上海").click()
        ''')

        # ✅ 解决方案 A：使用属性部分匹配
        print("\n✅ 方案 A：属性部分匹配")
        print("适用场景：ID 有固定模式（如固定前缀或后缀）")
        print('''
        # 匹配以 _tree 结尾的 ID
        page.locator("[id$='_tree']").click()

        # 匹配以 tree_ 开头的 ID
        page.locator("[id^='tree_']").click()

        # 匹配包含 tree 的 ID
        page.locator("[id*='tree']").click()
        ''')

        # ✅ 解决方案 B：动态获取 ID
        print("\n✅ 方案 B：动态获取 ID（推荐）")
        print("适用场景：触发元素有 data-target 等属性指向动态 ID")
        print('''
        # 步骤1：点击触发元素
        page.get_by_placeholder("Name/名称").click()

        # 步骤2：从 data-target 获取动态 ID
        trigger = page.get_by_placeholder("Name/名称")
        tree_id = trigger.get_attribute("data-target")
        print(f"动态 ID: {tree_id}")  # 输出: 142258285_tree

        # 步骤3：使用动态 ID 构建定位器
        page.locator(f"#{tree_id}").get_by_text("上海").click()
        ''')

        # ✅ 解决方案 C：完全避免使用 ID
        print("\n✅ 方案 C：避免使用 ID（最佳）")
        print("适用场景：元素有其他稳定特征（文本、role、类名等）")
        print('''
        # 直接使用文本定位
        page.get_by_placeholder("Name/名称").click()
        page.get_by_text("上海").first.click()

        # 或使用 role
        page.get_by_role("textbox", name="Name/名称").click()
        page.get_by_role("option", name="上海").click()
        ''')

        browser.close()


# ============================================================================
# 失败原因 2：元素在 iframe 中
# ============================================================================

def fix_iframe_locator():
    """修复 iframe 内元素定位问题"""

    print("\n" + "=" * 70)
    print("失败原因 2：元素在 iframe 中")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # ❌ Codegen 生成的失败代码（没有考虑 iframe）
        print("\n❌ Codegen 生成（会失败）:")
        print('''
        page.locator("#submitButton").click()  # 找不到，因为在 iframe 里
        ''')

        # ✅ 解决方案：使用 frame_locator
        print("\n✅ 正确做法：")
        print('''
        # 方法1：使用 name 或 id 定位 iframe
        iframe = page.frame_locator("iframe[name='contentFrame']")
        iframe.locator("#submitButton").click()

        # 方法2：使用 URL 定位 iframe
        iframe = page.frame_locator("iframe[src*='workflow']")
        iframe.locator("#submitButton").click()

        # 方法3：嵌套 iframe
        outer_frame = page.frame_locator("iframe#outerFrame")
        inner_frame = outer_frame.frame_locator("iframe#innerFrame")
        inner_frame.locator("#submitButton").click()
        ''')

        # 诊断技巧
        print("\n🔍 如何检测元素是否在 iframe 中：")
        print('''
        # 在浏览器控制台执行：
        console.log(document.querySelectorAll('iframe').length);

        # 或在 Playwright 中：
        frame_count = len(page.frames)
        print(f"页面有 {frame_count} 个框架")
        if frame_count > 1:
            print("元素可能在 iframe 中")
        ''')

        browser.close()


# ============================================================================
# 失败原因 3：元素加载时机问题
# ============================================================================

def fix_timing_issues():
    """修复元素加载时机问题"""

    print("\n" + "=" * 70)
    print("失败原因 3：元素还未加载完成")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # ❌ Codegen 生成的失败代码（没有等待）
        print("\n❌ Codegen 生成（可能失败）:")
        print('''
        page.goto("https://portal.com")
        page.locator("#dynamicContent").click()  # 元素可能还没加载
        ''')

        # ✅ 解决方案：添加等待
        print("\n✅ 正确做法：")
        print('''
        # 方法1：wait_for_selector（等待元素出现）
        page.goto("https://portal.com")
        page.wait_for_selector("#dynamicContent", state="visible", timeout=10000)
        page.locator("#dynamicContent").click()

        # 方法2：wait_for_load_state（等待页面状态）
        page.goto("https://portal.com")
        page.wait_for_load_state("networkidle")  # 等待网络空闲
        page.locator("#dynamicContent").click()

        # 方法3：locator.wait_for（等待定位器）
        page.goto("https://portal.com")
        locator = page.locator("#dynamicContent")
        locator.wait_for(state="visible", timeout=10000)
        locator.click()

        # 方法4：使用 Playwright 内置等待（推荐）
        # Playwright 的操作默认会等待元素可操作
        page.goto("https://portal.com")
        page.locator("#dynamicContent").click(timeout=10000)
        ''')

        # 常见等待状态
        print("\n📝 常用等待状态：")
        print('''
        - "attached"  : 元素已添加到 DOM
        - "detached"  : 元素已从 DOM 移除
        - "visible"   : 元素可见（默认）
        - "hidden"    : 元素隐藏

        页面加载状态：
        - "load"         : load 事件触发
        - "domcontentloaded" : DOMContentLoaded 事件触发
        - "networkidle"  : 网络空闲（500ms 内无网络请求）
        ''')

        browser.close()


# ============================================================================
# 失败原因 4：元素被遮挡或不可点击
# ============================================================================

def fix_clickability_issues():
    """修复元素不可点击问题"""

    print("\n" + "=" * 70)
    print("失败原因 4：元素被遮挡或不可点击")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # ❌ 可能失败的情况
        print("\n❌ 可能失败的情况:")
        print('''
        page.locator("button.submit").click()
        # 错误: Element is not visible
        # 错误: Element is outside of the viewport
        # 错误: Other element would receive the click
        ''')

        # ✅ 解决方案
        print("\n✅ 解决方案：")
        print('''
        # 方案1：滚动到元素可见
        button = page.locator("button.submit")
        button.scroll_into_view_if_needed()
        button.click()

        # 方案2：强制点击（忽略遮挡检查）
        page.locator("button.submit").click(force=True)
        # 注意：force=True 会跳过可操作性检查，谨慎使用

        # 方案3：等待遮挡元素消失
        # 假设有一个 loading 遮罩
        page.locator(".loading-overlay").wait_for(state="hidden")
        page.locator("button.submit").click()

        # 方案4：使用 JavaScript 点击（最后手段）
        page.locator("button.submit").evaluate("element => element.click()")

        # 方案5：点击前等待稳定
        page.wait_for_timeout(1000)  # 等待动画完成
        page.locator("button.submit").click()
        ''')

        # 诊断技巧
        print("\n🔍 诊断技巧：")
        print('''
        # 检查元素状态
        button = page.locator("button.submit")
        print(f"可见: {button.is_visible()}")
        print(f"启用: {button.is_enabled()}")
        print(f"数量: {button.count()}")

        # 检查是否被遮挡（在浏览器控制台）
        // 检查元素是否被其他元素遮挡
        const el = document.querySelector('button.submit');
        const box = el.getBoundingClientRect();
        const topElement = document.elementFromPoint(box.left, box.top);
        console.log('顶层元素:', topElement);  // 如果不是 button，说明被遮挡
        ''')

        browser.close()


# ============================================================================
# 失败原因 5：选择器匹配多个元素
# ============================================================================

def fix_multiple_matches():
    """修复选择器匹配多个元素的问题"""

    print("\n" + "=" * 70)
    print("失败原因 5：选择器匹配多个元素")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # ❌ Codegen 生成的问题代码
        print("\n❌ 问题代码:")
        print('''
        # 可能匹配到多个 "上海"
        page.get_by_text("上海").click()  # 不知道点击哪一个
        ''')

        # ✅ 解决方案
        print("\n✅ 解决方案：")
        print('''
        # 方案1：使用 .first / .last / .nth()
        page.get_by_text("上海").first.click()   # 第一个
        page.get_by_text("上海").last.click()    # 最后一个
        page.get_by_text("上海").nth(1).click()  # 第二个（索引从0开始）

        # 方案2：增加上下文（链式定位）
        # 在特定容器内查找
        page.locator("div.city-selector").get_by_text("上海").click()

        # 方案3：使用更精确的定位器
        # 添加额外条件
        page.locator("label:has-text('上海')").first.click()
        page.locator("div.radio > label:has-text('上海')").click()

        # 方案4：使用 filter 过滤
        page.get_by_text("上海").filter(has=page.locator("input[checked]")).click()

        # 方案5：遍历所有匹配并选择
        cities = page.get_by_text("上海").all()
        for city in cities:
            if city.is_visible():
                city.click()
                break
        ''')

        # 诊断技巧
        print("\n🔍 诊断匹配数量：")
        print('''
        # 检查匹配了多少个元素
        count = page.get_by_text("上海").count()
        print(f"找到 {count} 个匹配元素")

        # 列出所有匹配元素的信息
        elements = page.get_by_text("上海").all()
        for i, el in enumerate(elements):
            print(f"元素 {i}:")
            print(f"  可见: {el.is_visible()}")
            print(f"  文本: {el.inner_text()}")
            print(f"  ID: {el.get_attribute('id')}")
        ''')

        browser.close()


# ============================================================================
# 完整修复流程示例
# ============================================================================

def complete_fix_example():
    """完整的定位器修复流程示例"""

    print("\n" + "=" * 70)
    print("完整修复流程示例：城市选择")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("\n📋 场景：选择出发城市 '上海'")

        # ❌ Codegen 原始代码（有多个问题）
        print("\n❌ Codegen 原始代码:")
        print('''
        page.get_by_role("cell", name="WF_ATS_TRAVLE.FROMCITY").get_by_role("textbox").click()
        page.get_by_role("textbox", name="Name/名称").click()
        page.get_by_role("textbox", name="Name/名称").fill("上海")
        page.locator("[id=\\"142258285_tree\\"] i").click()              # ❌ 动态 ID
        page.locator("[id=\\"142258285_tree\\"]").get_by_text("上海").nth(1).click()  # ❌ 动态 ID
        ''')

        print("\n❌ 问题分析:")
        print("1. ID 是动态的，每次运行都会变")
        print("2. 没有等待树元素加载")
        print("3. 硬编码使用 nth(1)，可能不准确")

        # ✅ 修复后的代码
        print("\n✅ 修复后的代码:")
        print('''
def select_city_robust(page: Page, city: str):
    """健壮的城市选择方法"""

    # 步骤1：点击触发城市选择的文本框
    trigger = page.get_by_role("cell", name="WF_ATS_TRAVLE.FROMCITY").get_by_role("textbox")
    trigger.click()

    # 步骤2：等待搜索框出现并输入
    search_box = page.get_by_role("textbox", name="Name/名称")
    search_box.wait_for(state="visible", timeout=5000)
    search_box.click()
    search_box.fill(city)

    # 步骤3：等待树展开（短暂延迟或等待特定元素）
    page.wait_for_timeout(500)

    # 步骤4：动态获取树 ID（解决动态 ID 问题）
    tree_id = search_box.get_attribute("data-target")

    if tree_id:
        # 方法A：使用动态获取的 ID
        print(f"✓ 获取到树 ID: {tree_id}")
        tree_container = page.locator(f"#{tree_id}")
        tree_container.wait_for(state="visible")

        # 在树容器内查找目标城市的 label
        city_label = tree_container.locator(f"label:has-text('{city}')").first
        city_label.scroll_into_view_if_needed()
        city_label.click()
    else:
        # 方法B：不依赖 ID 的后备方案
        print("⚠️  未找到树 ID，使用后备方案")
        # 等待树容器可见（使用类名）
        page.wait_for_selector("div.ztree[id$='_tree']", state="visible")

        # 直接点击可见的城市文本
        city_options = page.get_by_text(city, exact=True).all()
        for option in city_options:
            if option.is_visible():
                option.click()
                break

    # 步骤5：验证选择成功
    page.wait_for_timeout(500)
    selected_value = trigger.input_value()
    print(f"✓ 已选择城市: {selected_value}")
    assert city in selected_value, f"选择失败：期望 {city}，实际 {selected_value}"

# 使用示例
# select_city_robust(page, "上海")
        ''')

        print("\n✨ 改进点:")
        print("1. ✅ 使用 data-target 动态获取 ID")
        print("2. ✅ 添加等待和状态检查")
        print("3. ✅ 提供后备方案（不依赖 ID）")
        print("4. ✅ 添加结果验证")
        print("5. ✅ 封装为可复用函数")

        browser.close()


# ============================================================================
# 通用修复模板
# ============================================================================

def generic_fix_template():
    """通用的 Codegen 代码修复模板"""

    print("\n" + "=" * 70)
    print("通用修复模板")
    print("=" * 70)

    template = '''
from playwright.sync_api import sync_playwright, Page
import time

def robust_automation(page: Page):
    """修复后的健壮自动化脚本模板"""

    # ========== 1. 导航和等待 ==========
    page.goto("https://your-url.com")

    # 等待页面完全加载
    page.wait_for_load_state("networkidle")
    # 或等待关键元素
    page.wait_for_selector("selector-of-key-element", state="visible")

    # ========== 2. 定位和操作元素 ==========
    # ✅ 优先使用 role 和 text
    page.get_by_role("button", name="登录").click()
    page.get_by_label("用户名").fill("admin")

    # ✅ 如果必须使用 CSS/XPath，添加等待
    element = page.locator("button.submit")
    element.wait_for(state="visible")
    element.click()

    # ✅ 处理动态 ID
    trigger = page.locator("input.trigger")
    dynamic_id = trigger.get_attribute("data-target")
    page.locator(f"#{dynamic_id}").click()

    # ✅ 处理多个匹配
    page.get_by_text("选项").first.click()  # 明确指定

    # ✅ 处理 iframe
    iframe = page.frame_locator("iframe#content")
    iframe.locator("button").click()

    # ✅ 处理遮挡
    button = page.locator("button.submit")
    page.locator(".loading").wait_for(state="hidden")  # 等待遮挡消失
    button.scroll_into_view_if_needed()
    button.click()

    # ========== 3. 错误处理 ==========
    try:
        page.locator("button").click(timeout=5000)
    except Exception as e:
        print(f"点击失败: {e}")
        # 尝试备用方案
        page.locator("button").click(force=True)

    # ========== 4. 验证结果 ==========
    success_msg = page.locator(".success-message").inner_text()
    assert "成功" in success_msg, f"操作失败: {success_msg}"

# 运行
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    try:
        robust_automation(page)
        print("✓ 自动化完成")
    except Exception as e:
        print(f"❌ 错误: {e}")
        # 截图用于调试
        page.screenshot(path="error.png")
    finally:
        browser.close()
    '''

    print(template)


# ============================================================================
# 主函数：运行所有示例
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║   Playwright Codegen 定位器失败 - 修复方案大全                      ║
╚══════════════════════════════════════════════════════════════════════╝

本脚本包含 5 种最常见失败原因的解决方案：

1. 动态 ID
2. 元素在 iframe 中
3. 元素加载时机问题
4. 元素被遮挡或不可点击
5. 选择器匹配多个元素

每个示例都包含：
- ❌ Codegen 生成的问题代码
- ✅ 正确的修复方案
- 🔍 诊断技巧

    """)

    # 运行所有示例（只打印说明，不实际执行浏览器操作）
    fix_dynamic_id()
    fix_iframe_locator()
    fix_timing_issues()
    fix_clickability_issues()
    fix_multiple_matches()
    complete_fix_example()
    generic_fix_template()

    print("\n" + "=" * 70)
    print("✓ 所有修复方案已展示")
    print("=" * 70)
    print("\n💡 建议：")
    print("1. 找到您遇到的失败类型")
    print("2. 复制对应的修复代码")
    print("3. 根据实际情况调整选择器")
    print("4. 测试多次确保稳定性")
    print("\n如需实际运行，请取消注释相应的 page.goto() 代码")
