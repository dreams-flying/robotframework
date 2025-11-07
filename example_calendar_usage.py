"""
日历转换器使用示例

演示如何使用 calendar_converter.py 转换 Playwright 代码
"""

# ==================== 转换前的代码 ====================

original_code = '''
from playwright.sync_api import sync_playwright, Page

def fill_leave_application(
    page2: Page,
    date_day_5: int,
    start_time: str,
    date_day_20: int,
    end_time: str,
    leave_reason: str
):
    """填写请假申请表单"""

    # 选择开始日期
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.SDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name=date_day_5, exact=True).first.click()

    # 选择开始时间
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.STIME").get_by_label("").click()
    page2.get_by_role("option", name=start_time).click()

    # 选择结束日期
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.EDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name=date_day_20, exact=True).first.click()

    # 选择结束时间
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.ETIME").get_by_label("").click()
    page2.get_by_role("option", name=end_time).click()

    # 填写请假原因
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.APPCAUSE").get_by_role("textbox").fill(leave_reason)

    # 提交
    page2.get_by_role("button", name="提交").click()
'''

# ==================== 转换后的代码 ====================

converted_code = '''
from playwright.sync_api import sync_playwright, Page

# 日历和时间选择辅助函数
from calendar_helpers import select_calendar_date, select_calendar_time

def fill_leave_application(
    page2: Page,
    date_day_5: int,
    start_time: str,
    date_day_20: int,
    end_time: str,
    leave_reason: str
):
    """填写请假申请表单"""

    # 选择开始日期
    select_calendar_date(
        page2,
        page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.SDATE").get_by_placeholder("YYYYMMDD"),
        target_day=date_day_5
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
        target_day=date_day_20
    )

    # 选择结束时间
    select_calendar_time(
        page2,
        page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.ETIME").get_by_label(""),
        end_time
    )

    # 填写请假原因
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.APPCAUSE").get_by_role("textbox").fill(leave_reason)

    # 提交
    page2.get_by_role("button", name="提交").click()
'''


# ==================== 使用指南 ====================

def print_usage_guide():
    """打印使用指南"""

    print("=" * 80)
    print("日历转换器使用指南")
    print("=" * 80)

    print("\n📝 步骤1: 准备输入文件")
    print("-" * 80)
    print("将 Playwright codegen 生成的代码保存到文件中（例如：original.py）")

    print("\n📝 步骤2: 运行转换器")
    print("-" * 80)
    print("python calendar_converter.py original.py converted.py")

    print("\n📝 步骤3: 检查转换结果")
    print("-" * 80)
    print("打开 converted.py 查看转换后的代码")

    print("\n" + "=" * 80)
    print("转换模式说明")
    print("=" * 80)

    print("\n🔄 模式1: 日期选择")
    print("-" * 80)
    print("转换前:")
    print("    page2.get_by_placeholder(\"YYYYMMDD\").click()")
    print("    page2.get_by_role(\"cell\", name=date_day_5, exact=True).first.click()")
    print("\n转换后:")
    print("    select_calendar_date(")
    print("        page2,")
    print("        page2.get_by_placeholder(\"YYYYMMDD\"),")
    print("        target_day=date_day_5")
    print("    )")

    print("\n🔄 模式2: 时间选择")
    print("-" * 80)
    print("转换前:")
    print("    page2.get_by_label(\"\").click()")
    print("    page2.get_by_role(\"option\", name=start_time).click()")
    print("\n转换后:")
    print("    select_calendar_time(")
    print("        page2,")
    print("        page2.get_by_label(\"\"),")
    print("        start_time")
    print("    )")

    print("\n" + "=" * 80)
    print("高级用法")
    print("=" * 80)

    print("\n📅 指定月份和年份:")
    print("-" * 80)
    print("# 选择2025年11月6号")
    print("select_calendar_date(")
    print("    page2,")
    print("    page2.get_by_placeholder(\"YYYYMMDD\"),")
    print("    target_day=6,")
    print("    target_month=11,")
    print("    target_year=2025")
    print(")")

    print("\n" + "=" * 80)
    print("优势")
    print("=" * 80)
    print("✅ 自动处理多个日历组件冲突")
    print("✅ 智能月份翻页导航")
    print("✅ 处理重复日期数字（上月/当月/下月）")
    print("✅ 支持中文月份解析")
    print("✅ 鲁棒的错误处理和备用策略")
    print("✅ 详细的执行日志")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    print_usage_guide()
