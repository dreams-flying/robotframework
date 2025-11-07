"""
日历和时间选择辅助函数
用于简化 Playwright 自动化中的日期和时间选择操作
"""

from playwright.sync_api import Page
from datetime import datetime
from typing import Optional


def parse_chinese_month(month_text: str) -> Optional[int]:
    """
    将中文月份转换为数字

    ✅ 按长度从长到短匹配，避免"十一月"被"一月"误匹配
    """
    month_patterns = [
        ('十二月', 12),
        ('十一月', 11),
        ('十月', 10),
        ('九月', 9),
        ('八月', 8),
        ('七月', 7),
        ('六月', 6),
        ('五月', 5),
        ('四月', 4),
        ('三月', 3),
        ('二月', 2),
        ('一月', 1),
    ]

    for pattern, num in month_patterns:
        if pattern in month_text:
            return num
    return None


def select_calendar_date(
    page: Page,
    date_field_locator,
    target_day: int,
    target_month: Optional[int] = None,
    target_year: Optional[int] = None,
    max_attempts: int = 12
):
    """
    智能选择日历日期，自动处理月份翻页、日期去重和多日历场景

    参数:
        page: Playwright Page 对象
        date_field_locator: 日期输入框定位器
        target_day: 目标日期（1-31）
        target_month: 目标月份（1-12），None表示当前月
        target_year: 目标年份，None表示当前年
        max_attempts: 最大翻页次数

    示例:
        # 选择当前月的5号
        select_calendar_date(page2, page2.get_by_placeholder("YYYYMMDD"), 5)

        # 选择2025年11月6号
        select_calendar_date(page2, page2.get_by_placeholder("YYYYMMDD"), 6, 11, 2025)
    """
    # 1. 点击日期输入框，打开日历
    date_field_locator.click()

    # 2. 等待日历显示
    page.wait_for_selector('.datetimepicker:visible .datetimepicker-days', state='visible', timeout=3000)

    # 3. 如果没有指定月份，直接选择当前月的日期
    if target_month is None:
        try:
            # 获取当前可见的日历
            visible_calendar = page.locator('.datetimepicker:visible').first

            # 在可见日历的作用域内选择日期
            day_locator = visible_calendar.locator(
                f'.datetimepicker-days tbody .day:not(.old):not(.new):text-is("{target_day}")'
            )

            if day_locator.count() > 0:
                day_locator.first.click()
                print(f"✅ 成功选择当前月日期: {target_day}日")
                return
            else:
                print(f"⚠️ 当前月不存在日期 {target_day}")
                return

        except Exception as e:
            print(f"⚠️ 选择当前月日期失败: {e}")
            # 备用策略
            visible_calendar = page.locator('.datetimepicker:visible').first
            visible_calendar.get_by_role("cell", name=str(target_day), exact=True).first.click()
            return

    # 4. 如果指定了月份，需要先导航到目标月份
    if target_year is None:
        target_year = datetime.now().year

    attempts = 0

    while attempts < max_attempts:
        try:
            # 每次循环都重新获取可见日历（防止DOM更新后引用失效）
            visible_calendar = page.locator('.datetimepicker:visible').first

            # 读取当前显示的月份和年份
            header = visible_calendar.locator('.datetimepicker-days .switch')
            header_text = header.text_content()

            # 解析年份和月份（格式如 "十一月 2025"）
            parts = header_text.strip().split()
            current_month = parse_chinese_month(parts[0])
            current_year = int(parts[1]) if len(parts) > 1 else target_year

            if current_month is None:
                print(f"⚠️ 无法解析月份: {header_text}")
                break

            print(f"📅 当前日历显示: {current_year}年{current_month}月 (原文:{parts[0]})，目标: {target_year}年{target_month}月")

            # 判断是否到达目标月份
            if current_year == target_year and current_month == target_month:
                # ✅ 找到目标月份，选择日期
                day_locator = visible_calendar.locator(
                    f'.datetimepicker-days tbody .day:not(.old):not(.new):text-is("{target_day}")'
                )

                # 检查日期是否存在
                if day_locator.count() > 0:
                    day_locator.first.click()
                    print(f"✅ 成功选择日期: {target_year}年{target_month}月{target_day}日")
                    return
                else:
                    print(f"⚠️ 日期 {target_day} 在 {target_month} 月不存在")
                    return

            # 判断需要向前翻还是向后翻
            need_next = False
            if current_year < target_year:
                need_next = True
            elif current_year == target_year and current_month < target_month:
                need_next = True

            # 记录翻页前的月份
            old_header_text = header_text

            if need_next:
                # 向后翻页（下一个月）
                visible_calendar.locator('.datetimepicker-days .next').click()
                print(f"→ 点击下一月")
            else:
                # 向前翻页（上一个月）
                visible_calendar.locator('.datetimepicker-days .prev').click()
                print(f"← 点击上一月")

            # 等待月份实际改变
            try:
                for wait_attempt in range(10):
                    page.wait_for_timeout(100)
                    visible_calendar = page.locator('.datetimepicker:visible').first
                    new_header = visible_calendar.locator('.datetimepicker-days .switch')
                    new_header_text = new_header.text_content()

                    if new_header_text != old_header_text:
                        print(f"   ✓ 日历已更新: {old_header_text} → {new_header_text}")
                        break

                    if wait_attempt == 9:
                        print(f"   ⚠️ 日历未更新，强制继续")

            except Exception as e:
                print(f"   ⚠️ 等待日历更新时出错: {e}")
                page.wait_for_timeout(500)

            attempts += 1

        except Exception as e:
            print(f"⚠️ 翻页过程出错: {e}")
            attempts += 1
            if attempts >= max_attempts:
                print(f"❌ 达到最大翻页次数，使用备用策略")
                try:
                    visible_calendar = page.locator('.datetimepicker:visible').first
                    visible_calendar.get_by_role("cell", name=str(target_day), exact=True).first.click()
                except:
                    print(f"❌ 备用策略也失败了")
                return

    print(f"⚠️ 未能在 {max_attempts} 次尝试内找到目标月份")


def select_calendar_time(
    page: Page,
    time_field_locator,
    time_value: str
):
    """
    选择时间下拉框的值

    参数:
        page: Playwright Page 对象
        time_field_locator: 时间输入框定位器
        time_value: 时间值（如 "09:00", "14:30"）

    示例:
        select_calendar_time(
            page2,
            page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.STIME").get_by_label(""),
            "09:00"
        )
    """
    try:
        # 1. 点击时间输入框，打开下拉框
        time_field_locator.click()

        # 2. 等待选项出现
        page.wait_for_selector('[role="option"]', state='visible', timeout=2000)

        # 3. 选择时间选项
        page.get_by_role("option", name=time_value).click()

        print(f"✅ 成功选择时间: {time_value}")

    except Exception as e:
        print(f"⚠️ 选择时间失败: {e}")
        # 备用策略：直接使用 first
        try:
            time_field_locator.click()
            page.wait_for_timeout(300)
            page.get_by_role("option", name=time_value).first.click()
        except:
            print(f"❌ 备用策略也失败了")
