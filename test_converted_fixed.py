# 日历和时间选择辅助函数
from calendar_helpers import select_calendar_date, select_calendar_time
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
    select_calendar_date(
        page2,
        page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.SDATE").get_by_placeholder("YYYYMMDD"),
        target_day=start_date_day
    )

    # 选择开始时间
    select_calendar_time(
        page2,
        page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.STIME").get_by_label(""),
        start_time
    )

    # 选择结束日期
    select_calendar_date(
        page2,
        page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.EDATE").get_by_placeholder("YYYYMMDD"),
        target_day=end_date_day
    )

    # 选择结束时间
    select_calendar_time(
        page2,
        page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.ETIME").get_by_label(""),
        end_time
    )

    # 填写目的地
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.DESTINATION").get_by_role("textbox").fill(destination)

    # 填写出差事由
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.APPCAUSE").get_by_role("textbox").fill(purpose)

    # 保存
    page2.get_by_role("button", name="保存").click()
