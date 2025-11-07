"""
测试文件：转换前的原始代码
"""

from playwright.sync_api import sync_playwright, Page


def fill_business_trip_form(
    page2: Page,
    start_date_day: int,
    start_time: str,
    end_date_day: int,
    end_time: str,
    destination: str,
    purpose: str
):
    """填写出差申请表单"""

    # 选择开始日期
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.SDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name=start_date_day, exact=True).first.click()

    # 选择开始时间
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.STIME").get_by_label("").click()
    page2.get_by_role("option", name=start_time).click()

    # 选择结束日期
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.EDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name=end_date_day, exact=True).first.click()

    # 选择结束时间
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.ETIME").get_by_label("").click()
    page2.get_by_role("option", name=end_time).click()

    # 填写目的地
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.DESTINATION").get_by_role("textbox").fill(destination)

    # 填写出差事由
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.APPCAUSE").get_by_role("textbox").fill(purpose)

    # 保存
    page2.get_by_role("button", name="保存").click()
