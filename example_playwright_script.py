"""
示例Playwright脚本 - 用于演示增强型提取器

这个脚本包含了各种不同类型的定位器和操作，
用于测试提取器的完整功能。
"""

from playwright.sync_api import Playwright, sync_playwright, expect
import re


def run(playwright: Playwright) -> None:
    # 启动浏览器
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # ==================== URL导航 ====================
    # 访问主页
    page.goto("https://example-erp.com/login")

    # ==================== 登录流程 ====================
    # 使用placeholder定位器
    page.get_by_placeholder("请输入用户名").fill("admin")
    page.get_by_placeholder("请输入密码").fill("Admin@123")

    # 使用role定位器点击按钮
    page.get_by_role("button", name="登录").click()

    # 等待页面跳转
    page.wait_for_url("**/dashboard")

    # 断言登录成功
    expect(page.get_by_text("欢迎回来")).to_be_visible()

    # ==================== 导航到表单页面 ====================
    # 使用文本定位器导航
    page.get_by_text("业务管理").click()
    page.get_by_text("员工管理").click()
    page.get_by_text("新增员工").click()

    # ==================== 填写员工表单 ====================
    # 基本信息
    page.get_by_label("员工工号").fill("E20250001")
    page.get_by_label("员工姓名").fill("张三")
    page.get_by_label("邮箱地址").fill("zhangsan@example.com")
    page.get_by_label("手机号码").fill("13800138000")

    # 下拉选择
    page.get_by_label("所属部门").select_option("技术部")
    page.get_by_label("职位").select_option(label="高级工程师")

    # 日期选择器
    page.locator("input[name='hire_date']").fill("2025-01-01")

    # 单选框和复选框
    page.get_by_label("性别").check()
    page.locator("input[type='radio'][value='male']").check()
    page.get_by_label("接受短信通知").check()
    page.get_by_label("接受邮件通知").check()

    # ==================== 文件上传 ====================
    page.get_by_label("上传简历").set_input_files("./files/resume.pdf")
    page.get_by_test_id("photo-upload").set_input_files(["./files/photo.jpg"])

    # ==================== 复杂定位器 ====================
    # XPath定位器
    page.locator("xpath=//div[@class='form-section']//input[@type='text']").first.fill("备注信息")

    # CSS选择器
    page.query_selector("#salary-input").fill("15000")

    # 组合定位器
    page.locator("div.employee-form").get_by_placeholder("备注").fill("这是一个测试员工")

    # nth定位器
    page.get_by_role("textbox").nth(0).fill("第一个文本框")
    page.get_by_role("textbox").last.fill("最后一个文本框")

    # filter定位器
    page.get_by_role("button").filter(has_text="保存").click()

    # ==================== 键盘操作 ====================
    # 使用键盘快捷键
    page.get_by_placeholder("搜索").press("Control+A")
    page.get_by_placeholder("搜索").press("Delete")
    page.get_by_placeholder("搜索").type("搜索关键词")
    page.get_by_placeholder("搜索").press("Enter")

    # ==================== 鼠标操作 ====================
    # 双击
    page.get_by_text("详情").dblclick()

    # 悬停
    page.get_by_role("button", name="更多操作").hover()

    # 右键点击
    page.get_by_text("文件名").click(button="right")

    # ==================== 等待操作 ====================
    # 等待元素出现
    page.wait_for_selector(".success-message", timeout=5000)

    # 等待URL变化
    page.wait_for_url("**/employee/list")

    # 等待加载完成
    page.wait_for_load_state("networkidle")

    # 固定等待
    page.wait_for_timeout(1000)

    # ==================== 断言验证 ====================
    # 可见性断言
    expect(page.get_by_text("保存成功")).to_be_visible()

    # 文本内容断言
    expect(page.locator(".employee-name")).to_contain_text("张三")
    expect(page.get_by_test_id("employee-id")).to_have_text("E20250001")

    # 值断言
    expect(page.get_by_label("员工姓名")).to_have_value("张三")

    # URL断言
    expect(page).to_have_url(re.compile(r".*/employee/\d+"))

    # 数量断言
    expect(page.get_by_role("row")).to_have_count(10)

    # 启用/禁用状态
    expect(page.get_by_role("button", name="提交")).to_be_enabled()
    expect(page.get_by_role("button", name="删除")).to_be_disabled()

    # ==================== Frame操作 ====================
    # iframe定位
    frame = page.frame_locator("iframe[name='content']")
    frame.get_by_text("iframe内容").click()

    # ==================== 多标签页操作 ====================
    # 打开新标签页
    page.get_by_text("在新窗口打开").click()

    # 切换到新页面（实际使用中需要处理新窗口）
    # new_page = context.pages[-1]
    # new_page.get_by_text("新页面内容").click()

    # ==================== 表格操作 ====================
    # 定位表格中的特定单元格
    page.locator("table.employee-table").get_by_role("row").filter(has_text="张三").get_by_role("button", name="编辑").click()

    # ==================== 下拉菜单操作 ====================
    # 多选下拉
    page.get_by_label("技能标签").select_option(["Python", "JavaScript", "SQL"])

    # 按索引选择
    page.locator("select[name='level']").select_option(index=2)

    # ==================== 对话框处理 ====================
    # 点击会触发确认对话框的按钮
    page.on("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="删除").click()

    # ==================== 清空和聚焦 ====================
    # 清空输入框
    page.get_by_label("搜索").clear()

    # 聚焦元素
    page.get_by_label("邮箱").focus()

    # 失去焦点
    page.get_by_label("邮箱").blur()

    # ==================== 拖拽操作 ====================
    # 拖拽元素
    source = page.locator(".draggable-item")
    target = page.locator(".drop-zone")
    source.drag_to(target)

    # ==================== 正则表达式使用 ====================
    # 使用正则匹配文本
    page.get_by_text(re.compile(r"员工编号:\s*E\d+")).click()

    # 使用正则匹配URL
    page.goto(re.compile(r"https://.*\.example\.com/.*"))

    # ==================== 变量赋值 ====================
    # 获取文本内容保存到变量
    employee_name = page.locator(".employee-name").inner_text()
    employee_count = page.get_by_role("row").count()

    # 使用变量
    print(f"员工姓名: {employee_name}")
    print(f"员工数量: {employee_count}")

    # ==================== 条件操作 ====================
    # 根据元素状态执行操作
    if page.get_by_text("编辑模式").is_visible():
        page.get_by_role("button", name="保存").click()
    else:
        page.get_by_role("button", name="编辑").click()

    # ==================== 多次访问不同URL ====================
    page.goto("https://example-erp.com/reports")
    page.goto("https://example-erp.com/settings")
    page.goto("https://example-erp.com/profile")

    # ==================== 最后的清理 ====================
    # 登出
    page.get_by_role("button", name="退出登录").click()

    # 关闭浏览器
    context.close()
    browser.close()


# ==================== 主入口 ====================
with sync_playwright() as playwright:
    run(playwright)
