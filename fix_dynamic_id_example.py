#!/usr/bin/env python3
"""
动态 ID 问题 - 完整修复示例
这是 Playwright Codegen 最常见的失败原因
"""

from playwright.sync_api import sync_playwright, Page

def example_codegen_original():
    """Codegen 生成的原始代码（会失败）"""
    print("=" * 70)
    print("❌ Codegen 生成的原始代码（会失败）")
    print("=" * 70)
    code = '''
page.get_by_role("cell", name="WF_ATS_TRAVLE.FROMCITY").get_by_role("textbox").click()
page.get_by_role("textbox", name="Name/名称").click()
page.get_by_role("textbox", name="Name/名称").fill("上海")
page.locator("[id=\\"142258285_tree\\"] i").click()              # ❌ 失败：ID 是动态的
page.locator("[id=\\"142258285_tree\\"]").get_by_text("上海").nth(1).click()  # ❌ 失败
    '''
    print(code)
    print("\n问题：142258285_tree 这个 ID 每次运行都会变化！\n")


def example_fix_method_1():
    """修复方法 1：使用部分匹配"""
    print("=" * 70)
    print("✅ 修复方法 1：使用部分匹配（ID 有固定模式时）")
    print("=" * 70)
    code = '''
page.get_by_role("textbox", name="Name/名称").click()
page.get_by_role("textbox", name="Name/名称").fill("上海")

# 使用 CSS 属性选择器的部分匹配
page.locator("[id$='_tree']").wait_for(state="visible")  # 匹配以 _tree 结尾的 ID
page.locator("[id$='_tree']").get_by_text("上海").first.click()

# 或者
page.locator("[id*='tree']").get_by_text("上海").first.click()  # 匹配包含 tree 的 ID
    '''
    print(code)
    print("\n适用场景：ID 虽然动态，但有固定的前缀或后缀（如 xxx_tree）\n")


def example_fix_method_2():
    """修复方法 2：动态获取 ID（推荐）"""
    print("=" * 70)
    print("✅ 修复方法 2：动态获取 ID（推荐）⭐⭐⭐")
    print("=" * 70)
    code = '''
# 步骤 1：点击触发元素
page.get_by_role("cell", name="WF_ATS_TRAVLE.FROMCITY").get_by_role("textbox").click()

# 步骤 2：获取搜索框
search_box = page.get_by_role("textbox", name="Name/名称")
search_box.click()
search_box.fill("上海")

# 步骤 3：从 data-target 属性动态获取树的真实 ID
tree_id = search_box.get_attribute("data-target")
print(f"✓ 动态获取到 ID: {tree_id}")  # 例如：142258285_tree

# 步骤 4：使用动态 ID 定位元素
if tree_id:
    tree_container = page.locator(f"#{tree_id}")
    tree_container.wait_for(state="visible", timeout=5000)
    tree_container.get_by_text("上海", exact=True).first.click()
else:
    # 后备方案
    page.locator("[id$='_tree']").get_by_text("上海").first.click()
    '''
    print(code)
    print("\n适用场景：触发元素有 data-target、data-id 等属性指向动态 ID")
    print("优点：最准确，适应性强\n")


def example_fix_method_3():
    """修复方法 3：完全避免使用 ID（最佳）"""
    print("=" * 70)
    print("✅ 修复方法 3：完全避免使用 ID（最佳实践）⭐⭐⭐")
    print("=" * 70)
    code = '''
# 步骤 1：点击触发元素
page.get_by_role("cell", name="WF_ATS_TRAVLE.FROMCITY").get_by_role("textbox").click()

# 步骤 2：输入搜索
search_box = page.get_by_role("textbox", name="Name/名称")
search_box.click()
search_box.fill("上海")

# 步骤 3：等待下拉列表出现（不依赖 ID）
page.wait_for_selector("div.ztree, div[class*='tree']", state="visible")

# 步骤 4：直接点击文本（Playwright 会找到可见的那个）
page.get_by_text("上海", exact=True).first.click()

# 或者使用更精确的上下文定位
page.locator("div.ztree, div[id$='_tree']").get_by_text("上海").first.click()
    '''
    print(code)
    print("\n适用场景：元素有其他稳定的特征（类名、文本、role 等）")
    print("优点：最简洁，最符合 Playwright 最佳实践\n")


def complete_working_example():
    """完整可运行的示例"""
    print("=" * 70)
    print("✅ 完整可运行示例")
    print("=" * 70)

    example_code = '''
from playwright.sync_api import sync_playwright, Page
import time

def select_city_robust(page: Page, city: str):
    """
    健壮的城市选择方法 - 处理动态 ID

    Args:
        page: Playwright Page 对象
        city: 要选择的城市名称
    """

    print(f"\\n开始选择城市: {city}")

    # 方法 1：尝试动态获取 ID（最准确）
    try:
        search_box = page.get_by_role("textbox", name="Name/名称")
        search_box.wait_for(state="visible", timeout=5000)
        search_box.click()
        search_box.fill(city)

        # 获取动态 ID
        tree_id = search_box.get_attribute("data-target")

        if tree_id:
            print(f"✓ 方法1成功：获取到动态 ID = {tree_id}")
            tree = page.locator(f"#{tree_id}")
            tree.wait_for(state="visible", timeout=3000)
            tree.get_by_text(city, exact=True).first.click()
            print(f"✓ 已选择城市: {city}")
            return True
    except Exception as e:
        print(f"⚠️  方法1失败: {e}")

    # 方法 2：使用部分匹配（后备）
    try:
        print("尝试方法2：部分匹配 ID")
        tree = page.locator("[id$='_tree']")
        tree.wait_for(state="visible", timeout=3000)
        tree.get_by_text(city, exact=True).first.click()
        print(f"✓ 已选择城市: {city}")
        return True
    except Exception as e:
        print(f"⚠️  方法2失败: {e}")

    # 方法 3：直接文本定位（最后手段）
    try:
        print("尝试方法3：直接文本定位")
        # 等待任何树容器出现
        page.wait_for_selector("div[class*='ztree'], div[id*='tree']",
                               state="visible", timeout=3000)

        # 找到所有匹配的城市文本，选择可见的第一个
        city_elements = page.get_by_text(city, exact=True).all()
        for el in city_elements:
            if el.is_visible():
                el.click()
                print(f"✓ 已选择城市: {city}")
                return True
    except Exception as e:
        print(f"❌ 方法3失败: {e}")

    print(f"❌ 所有方法都失败了，无法选择城市: {city}")
    return False


# 使用示例
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            # 打开页面
            page.goto("https://your-portal.com")
            page.wait_for_load_state("networkidle")

            # 导航到出差申请页面
            page.get_by_text("员工自助").click()
            page.get_by_text("出差申请").click()

            # 选择出发城市（使用健壮方法）
            select_city_robust(page, "上海")

            # 选择目的城市
            select_city_robust(page, "北京")

            print("\\n✓ 自动化完成")

        except Exception as e:
            print(f"\\n❌ 发生错误: {e}")
            page.screenshot(path="error.png")
        finally:
            input("\\n按 Enter 关闭浏览器...")
            browser.close()

if __name__ == "__main__":
    main()
    '''

    print(example_code)


def comparison_table():
    """对比表格"""
    print("\n" + "=" * 70)
    print("📊 三种方法对比")
    print("=" * 70)

    table = """
┌─────────────────┬──────────────┬──────────────┬────────────────┐
│ 方法            │ 稳定性       │ 性能         │ 实施难度       │
├─────────────────┼──────────────┼──────────────┼────────────────┤
│ 动态获取 ID     │ ⭐⭐⭐⭐⭐   │ ⭐⭐⭐⭐     │ ⭐⭐⭐         │
│ 部分匹配 ID     │ ⭐⭐⭐⭐     │ ⭐⭐⭐⭐     │ ⭐⭐⭐⭐       │
│ 避免使用 ID     │ ⭐⭐⭐       │ ⭐⭐⭐⭐⭐   │ ⭐⭐⭐⭐⭐     │
└─────────────────┴──────────────┴──────────────┴────────────────┘

推荐策略：
1. 首选「避免使用 ID」- 如果元素有稳定的 role/text/class
2. 次选「动态获取 ID」- 如果必须使用 ID，且有 data-target
3. 备选「部分匹配 ID」- 如果 ID 有固定模式

最佳实践：
✅ 组合使用多种方法（如示例代码中的 try-except 链）
✅ 优先使用 Playwright 推荐的 get_by_role/get_by_text
✅ 添加明确的等待和错误处理
✅ 使用 .first 明确指定第一个元素（避免 strict mode 错误）
    """
    print(table)


# ============================================================================
# 主函数
# ============================================================================

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   Playwright Codegen 动态 ID 问题 - 完整修复指南                     ║
║                                                                       ║
║   这是 Codegen 最常见的失败原因！                                    ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)

    example_codegen_original()
    input("\n按 Enter 查看修复方法 1...")

    example_fix_method_1()
    input("\n按 Enter 查看修复方法 2（推荐）...")

    example_fix_method_2()
    input("\n按 Enter 查看修复方法 3（最佳实践）...")

    example_fix_method_3()
    input("\n按 Enter 查看完整可运行示例...")

    complete_working_example()

    comparison_table()

    print("\n" + "=" * 70)
    print("✓ 完整指南已展示")
    print("=" * 70)
    print("\n💡 建议：")
    print("1. 复制上面的 select_city_robust() 函数到您的代码中")
    print("2. 根据实际情况调整定位器")
    print("3. 运行测试确保稳定性")
    print("\n如需实际运行示例，请取消注释 main() 函数中的 page.goto()")
