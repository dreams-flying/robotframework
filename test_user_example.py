#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试用户提供的实际例子"""

from file_upload_converter import convert_file_upload_operations

# 用户提供的原始代码
test_input = '''page2.get_by_role("button", name="发票上传").click()

        page2.get_by_role("button", name="选择", exact=True).click()

        page2.get_by_role("button", name="选择", exact=True).set_input_files(["C:/file.pdf"])

        page2.get_by_role("button", name="上传", exact=True).click()'''

# 期望的输出（根据用户提供的最终期望）
expected_output = '''page2.get_by_role("button", name="发票上传").click()
        page2.locator('input[type="file"]').set_input_files(["C:/file.pdf"])

        page2.get_by_role("button", name="上传", exact=True).click()'''

# 执行转换
result = convert_file_upload_operations(test_input)

# 显示结果
print("=" * 80)
print("原始代码（输入）:")
print("=" * 80)
print(test_input)
print("\n" + "=" * 80)
print("转换后代码（实际输出）:")
print("=" * 80)
print(result)
print("\n" + "=" * 80)
print("期望输出:")
print("=" * 80)
print(expected_output)
print("\n" + "=" * 80)

# 详细比较
print("详细比较:")
print("-" * 80)
input_lines = test_input.split('\n')
result_lines = result.split('\n')
expected_lines = expected_output.split('\n')

print(f"原始代码行数: {len(input_lines)}")
print(f"转换后行数: {len(result_lines)}")
print(f"期望行数: {len(expected_lines)}")

print("\n逐行对比:")
for i, (r, e) in enumerate(zip(result_lines, expected_lines), 1):
    if r == e:
        print(f"行 {i}: ✅ 匹配")
    else:
        print(f"行 {i}: ❌ 不匹配")
        print(f"  实际: {repr(r)}")
        print(f"  期望: {repr(e)}")

# 最终验证
if result == expected_output:
    print("\n" + "🎉 " * 20)
    print("✅ 完全匹配！转换成功！")
    print("🎉 " * 20)
else:
    print("\n" + "⚠️ " * 20)
    print("❌ 转换结果与期望不匹配")
    print("⚠️ " * 20)
