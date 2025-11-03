#!/usr/bin/env python3
"""
Playwright Codegen 定位器失败诊断工具
使用方法：
1. 将 Codegen 生成的失败代码粘贴到此文件
2. 运行此脚本进行诊断
3. 根据输出的建议修复定位器
"""

from playwright.sync_api import sync_playwright, Page
import time

def diagnose_locator_issues():
    """诊断定位器问题的通用方法"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # ========================================
        # 步骤1：打开目标页面
        # ========================================
        print("=" * 60)
        print("步骤1：导航到目标页面")
        print("=" * 60)

        # TODO: 替换为您的实际 URL
        target_url = "https://your-portal.com"
        page.goto(target_url)
        print(f"✓ 已打开页面: {target_url}")

        # 等待页面加载完成
        page.wait_for_load_state('networkidle')
        print("✓ 页面加载完成")

        # ========================================
        # 步骤2：测试失败的定位器
        # ========================================
        print("\n" + "=" * 60)
        print("步骤2：测试 Codegen 生成的定位器")
        print("=" * 60)

        # TODO: 粘贴您的 Codegen 失败代码（示例）
        # 例如：
        # page.locator("[id=\"142258285_tree\"]").click()

        test_locators = [
            # 示例1：动态 ID（最常见失败原因）
            {
                "name": "动态ID定位器",
                "locator": "[id=\"142258285_tree\"]",
                "reason": "ID 可能是动态生成的"
            },
            # 示例2：CSS 类名
            {
                "name": "CSS类定位器",
                "locator": "button.submit-btn",
                "reason": "类名可能在不同环境下不同"
            },
            # 示例3：XPath
            {
                "name": "XPath定位器",
                "locator": "xpath=//div[@id='tree']//label",
                "reason": "DOM结构可能已改变"
            }
        ]

        for test in test_locators:
            print(f"\n测试定位器: {test['name']}")
            print(f"  定位器: {test['locator']}")
            print(f"  可能原因: {test['reason']}")

            try:
                locator = page.locator(test['locator'])
                count = locator.count()
                print(f"  ✓ 找到 {count} 个匹配元素")

                if count == 0:
                    print("  ❌ 失败：未找到元素")
                    diagnose_why_not_found(page, test['locator'])
                elif count > 1:
                    print(f"  ⚠️  警告：找到多个元素 ({count} 个)")
                    print("     建议：使用 .first 或 .nth() 指定具体元素")
                else:
                    # 检查元素可见性
                    is_visible = locator.is_visible()
                    print(f"  可见性: {'✓ 可见' if is_visible else '❌ 不可见'}")

                    # 获取元素信息
                    if is_visible:
                        text = locator.inner_text() if locator.inner_text() else "(无文本)"
                        print(f"  元素文本: {text}")

            except Exception as e:
                print(f"  ❌ 错误: {str(e)}")

        # ========================================
        # 步骤3：智能诊断和建议
        # ========================================
        print("\n" + "=" * 60)
        print("步骤3：智能诊断")
        print("=" * 60)

        suggest_better_locators(page)

        # 保持浏览器打开以便手动检查
        print("\n" + "=" * 60)
        print("浏览器将保持打开，按 Enter 继续...")
        print("=" * 60)
        input()

        browser.close()


def diagnose_why_not_found(page: Page, failed_locator: str):
    """深度诊断为什么定位器找不到元素"""
    print("\n  🔍 深度诊断：")

    # 检查1：页面是否完全加载
    try:
        page.wait_for_load_state('domcontentloaded', timeout=5000)
        print("    ✓ DOM 已加载")
    except:
        print("    ❌ DOM 未完全加载（可能需要增加等待时间）")

    # 检查2：是否在 iframe 中
    frames = page.frames
    print(f"    页面框架数: {len(frames)}")
    if len(frames) > 1:
        print("    ⚠️  页面包含 iframe，元素可能在 iframe 内")
        print("    建议：使用 page.frame_locator() 或 frame.locator()")

    # 检查3：提取定位器关键信息
    if "id=" in failed_locator:
        # 提取 ID
        import re
        match = re.search(r'id="([^"]+)"', failed_locator)
        if match:
            element_id = match.group(1)
            print(f"    目标 ID: {element_id}")

            # 检查是否存在类似的 ID
            similar_ids = page.locator(f"[id*='{element_id.split('_')[0]}']").count()
            if similar_ids > 0:
                print(f"    ✓ 找到 {similar_ids} 个包含相似 ID 的元素")
                print(f"    建议：使用部分匹配 [id*='前缀'] 或 [id$='后缀']")
            else:
                print("    ❌ 未找到任何相似 ID 的元素")
                print("    原因：ID 可能完全是动态的")

    # 检查4：页面是否需要登录
    if page.url != page.url:  # URL changed
        print("    ⚠️  页面 URL 已改变（可能跳转到登录页）")

    # 检查5：控制台错误
    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg) if msg.type == "error" else None)
    if console_errors:
        print(f"    ⚠️  页面有 {len(console_errors)} 个控制台错误")


def suggest_better_locators(page: Page):
    """建议更好的定位器策略"""
    print("\n💡 推荐的定位器策略：\n")

    strategies = [
        {
            "name": "策略1：使用 Role + Name",
            "example": 'page.get_by_role("button", name="提交")',
            "pros": "最稳定，抗 HTML 变化",
            "cons": "需要元素有正确的 ARIA role"
        },
        {
            "name": "策略2：使用 Text",
            "example": 'page.get_by_text("员工自助")',
            "pros": "直观，易维护",
            "cons": "文本变化会失效"
        },
        {
            "name": "策略3：使用 Test ID",
            "example": 'page.get_by_test_id("submit-button")',
            "pros": "专为测试设计，最可靠",
            "cons": "需要开发添加 data-testid"
        },
        {
            "name": "策略4：动态获取 ID",
            "example": 'tree_id = page.locator("input").get_attribute("data-target")',
            "pros": "处理动态 ID",
            "cons": "需要额外步骤"
        },
        {
            "name": "策略5：使用部分匹配",
            "example": 'page.locator("[id$=\'_tree\']")  # 匹配结尾',
            "pros": "适合 ID 有固定模式",
            "cons": "可能匹配多个元素"
        }
    ]

    for i, strategy in enumerate(strategies, 1):
        print(f"{i}. {strategy['name']}")
        print(f"   示例: {strategy['example']}")
        print(f"   优点: {strategy['pros']}")
        print(f"   缺点: {strategy['cons']}")
        print()


def check_element_interactability(page: Page, selector: str):
    """检查元素的可交互性"""
    print(f"\n检查元素可交互性: {selector}")

    try:
        locator = page.locator(selector)

        # 检查存在性
        count = locator.count()
        print(f"  元素数量: {count}")

        if count == 0:
            return

        element = locator.first

        # 检查各种状态
        checks = {
            "可见 (visible)": element.is_visible,
            "启用 (enabled)": element.is_enabled,
            "可编辑 (editable)": element.is_editable,
        }

        for check_name, check_func in checks.items():
            try:
                result = check_func()
                status = "✓" if result else "❌"
                print(f"  {status} {check_name}: {result}")
            except Exception as e:
                print(f"  ❌ {check_name}: 检查失败 - {str(e)}")

        # 获取元素属性
        try:
            attrs = ['id', 'class', 'name', 'type', 'data-target']
            print("\n  元素属性:")
            for attr in attrs:
                value = element.get_attribute(attr)
                if value:
                    print(f"    {attr}: {value}")
        except:
            pass

    except Exception as e:
        print(f"  ❌ 错误: {str(e)}")


# ========================================
# 特定场景：修复动态 ID
# ========================================

def fix_dynamic_id_example(page: Page):
    """示例：如何修复动态 ID 定位器"""

    print("\n" + "=" * 60)
    print("示例：修复动态 ID 定位器")
    print("=" * 60)

    # ❌ Codegen 生成的失败代码
    print("\n❌ Codegen 生成的代码（会失败）:")
    print('    page.locator("[id=\\"142258285_tree\\"]").click()')

    # ✅ 修复方法1：使用部分匹配
    print("\n✅ 修复方法1：使用部分匹配")
    print('    page.locator("[id$=\'_tree\']").click()  # 匹配以 _tree 结尾的 ID')

    # ✅ 修复方法2：动态获取
    print("\n✅ 修复方法2：动态获取 ID")
    print('''
    # 从触发元素获取 data-target
    trigger = page.get_by_placeholder("Name/名称")
    tree_id = trigger.get_attribute("data-target")
    page.locator(f"#{tree_id}").click()
    ''')

    # ✅ 修复方法3：避免使用 ID
    print("\n✅ 修复方法3：完全避免使用 ID")
    print('''
    # 使用更稳定的定位器
    page.get_by_placeholder("Name/名称").click()
    page.get_by_text("上海").first.click()
    ''')


# ========================================
# 主函数
# ========================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║   Playwright Codegen 定位器失败诊断工具                  ║
╚══════════════════════════════════════════════════════════╝

请按照提示操作：
1. 修改 target_url 为您的实际页面地址
2. 将失败的定位器代码粘贴到 test_locators 列表中
3. 运行脚本查看诊断结果

按 Enter 开始...
    """)
    input()

    try:
        diagnose_locator_issues()
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
