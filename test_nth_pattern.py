"""测试 .nth() 选择器支持"""

import sys
sys.path.insert(0, '/home/user/robotframework')

from calendar_converter import convert_calendar_operations

# 测试所有三种日期选择模式
test_input = '''
    # 测试1: 使用 .first 的日期选择
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.SDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name=date_day_5, exact=True).first.click()

    # 测试2: 不使用选择器的日期选择
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.EDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name=date_day_7, exact=True).click()

    # 测试3: 使用 .nth(1) 的日期选择
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.RETURNDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name=date_day_10, exact=True).nth(1).click()

    # 测试4: 使用 .nth(0) 的日期选择
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.STARTDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name=date_day_15, exact=True).nth(0).click()
    '''

result = convert_calendar_operations(test_input)

print("=" * 80)
print("转换结果：")
print("=" * 80)
print(result)
print("=" * 80)

# 验证所有四个日期参数都被转换
checks = [
    ('target_day=date_day_5', '第1个日期 (.first)'),
    ('target_day=date_day_7', '第2个日期 (无选择器)'),
    ('target_day=date_day_10', '第3个日期 (.nth(1))'),
    ('target_day=date_day_15', '第4个日期 (.nth(0))'),
    ('select_calendar_date', '日期选择函数'),
]

print("\n验证结果：")
all_passed = True
for check_str, description in checks:
    count = result.count(check_str)
    if check_str == 'select_calendar_date':
        # 应该有4个日期选择函数调用
        if count == 4:
            print(f"✅ {description}: 找到 {count} 次")
        else:
            print(f"❌ {description}: 找到 {count} 次，期望 4 次")
            all_passed = False
    else:
        if count >= 1:
            print(f"✅ {description}: 找到 '{check_str}'")
        else:
            print(f"❌ {description}: 未找到 '{check_str}'")
            all_passed = False

if all_passed:
    print("\n🎉 所有测试通过！")
else:
    print("\n⚠️ 部分测试失败")
