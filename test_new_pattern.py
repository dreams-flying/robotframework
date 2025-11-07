"""测试新的模式（.first 可选）"""

import sys
sys.path.insert(0, '/home/user/robotframework')

from calendar_converter import convert_calendar_operations

test_input = '''
    page2.get_by_role("tab", name="员工自助").click()
    page2.get_by_role("link", name="员工请假申请单").click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.LVTYPE").get_by_label("").click()
    page2.get_by_role("option", name=leave_type).click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.SDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name=date_day_5, exact=True).first.click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.STIME").get_by_label("").click()
    page2.get_by_role("option", name=start_time).click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.EDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name=date_day_7, exact=True).click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.ETIME").get_by_label("").click()
    page2.get_by_role("option", name=end_time_19).click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.PLACE").get_by_role("textbox").click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.PLACE").get_by_role("textbox").fill(place)
    page2.get_by_role("row", name="请假事由").get_by_role("textbox").click()
    page2.get_by_role("row", name="请假事由").get_by_role("textbox").fill(field_line_33)
    '''

result = convert_calendar_operations(test_input)

print("=" * 80)
print("转换结果：")
print("=" * 80)
print(result)
print("=" * 80)

# 验证
checks = [
    ('target_day=date_day_5', '第一个日期参数'),
    ('target_day=date_day_7', '第二个日期参数'),
    ('select_calendar_date', '日期选择函数'),
    ('select_calendar_time', '时间选择函数'),
    ('start_time', '开始时间参数'),
    ('end_time_19', '结束时间参数'),
]

print("\n验证结果：")
all_passed = True
for check_str, description in checks:
    if check_str in result:
        print(f"✅ {description}: 找到 '{check_str}'")
    else:
        print(f"❌ {description}: 未找到 '{check_str}'")
        all_passed = False

if all_passed:
    print("\n🎉 所有测试通过！")
else:
    print("\n⚠️ 部分测试失败")
