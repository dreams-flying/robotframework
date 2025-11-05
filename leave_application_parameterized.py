from playwright.sync_api import Playwright, sync_playwright

def apply_for_leave(
    playwright: Playwright,
    url: str = "https://h5-office.bestpay.com.cn/sec-iam-plus-h5/index.html#/portal/list",
    leave_type: str = "事假",
    start_date: str = "5",
    start_time: str = "15:30",
    end_date: str = "7",
    end_time: str = "19:",
    location: str = "上海",
    reason: str = "个人事宜"
) -> None:
    """
    参数化的请假申请函数

    参数:
        playwright: Playwright实例
        url: 访问的URL
        leave_type: 请假类型（如：事假、病假）
        start_date: 开始日期（日数字，如：5）
        start_time: 开始时间（如：15:30）
        end_date: 结束日期（日数字，如：7）
        end_time: 结束时间（如：19:00）
        location: 请假地点
        reason: 请假事由
    """
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # 导航到主页
    page.goto(url)

    # 导航到OA系统
    with page.expect_popup() as page1_info:
        page.get_by_text("OA系统").first.click()
    page1 = page1_info.value

    # 导航到人力系统
    with page1.expect_popup() as page2_info:
        page1.locator("#magnet_8490099577463589529").get_by_title("人力系统").locator("span").click()
    page2 = page2_info.value

    # 点击员工自助
    page2.get_by_role("tab", name="员工自助").click()

    # 点击员工请假申请单
    page2.get_by_role("link", name="员工请假申请单").click()

    # 选择请假类型
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.LVTYPE").get_by_label("").click()
    page2.get_by_role("option", name=leave_type).click()

    # 选择开始日期
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.SDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name=start_date, exact=True).first.click()

    # 选择开始时间
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.STIME").get_by_label("").click()
    page2.get_by_role("option", name=start_time).click()

    # 选择结束日期
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.EDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name=end_date, exact=True).click()

    # 选择结束时间
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.ETIME").get_by_label("").click()
    page2.get_by_role("option", name=end_time).click()

    # 填写请假地点
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.PLACE").get_by_role("textbox").click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.PLACE").get_by_role("textbox").fill(location)

    # 填写请假事由
    page2.get_by_role("row", name="请假事由").get_by_role("textbox").click()
    page2.get_by_role("row", name="请假事由").get_by_role("textbox").fill(reason)

    # 关闭浏览器
    context.close()
    browser.close()


# 使用示例:
# with sync_playwright() as playwright:
#     apply_for_leave(
#         playwright,
#         leave_type="病假",
#         start_date="10",
#         start_time="09:00",
#         end_date="12",
#         end_time="18:00",
#         location="北京",
#         reason="身体不适"
#     )
