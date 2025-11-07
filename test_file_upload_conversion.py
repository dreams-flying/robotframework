"""
测试文件上传转换 - 用户提供的具体例子
"""

# 原始代码（转换前）
original_code = '''
    page2.get_by_role("button", name="发票上传").click()
    page2.get_by_role("button", name="选择", exact=True).click()
    page2.get_by_role("button", name="选择", exact=True).set_input_files(["C:/Users/admin/Desktop/文件/发票/服装.pdf"])
    page2.get_by_role("button", name="上传", exact=True).click()
'''

# 期望的输出（转换后）
expected_output = '''
    page2.get_by_role("button", name="发票上传").click()
    page2.locator('input[type="file"]').set_input_files(["C:/Users/admin/Desktop/文件/发票/服装.pdf"])
    page2.get_by_role("button", name="上传", exact=True).click()
'''

# 使用转换器
from file_upload_converter import convert_file_upload_operations

result = convert_file_upload_operations(original_code)

print("=" * 80)
print("转换前（原始代码）:")
print("=" * 80)
print(original_code)

print("\n" + "=" * 80)
print("转换后（实际结果）:")
print("=" * 80)
print(result)

print("\n" + "=" * 80)
print("期望输出:")
print("=" * 80)
print(expected_output)

print("\n" + "=" * 80)
print("验证:")
print("=" * 80)

# 验证关键点
checks = [
    ('page2.locator(\'input[type="file"]\')' in result, "✅ 使用了 locator('input[type=\"file\"]')"),
    (result.count('.click()') == original_code.count('.click()') - 1, "✅ 删除了一个 .click() (选择按钮)"),
    ('name="选择"' not in result, "✅ 移除了所有 name=\"选择\" 的引用"),
    ('服装.pdf' in result, "✅ 保留了文件路径参数"),
]

all_passed = True
for passed, description in checks:
    print(description if passed else description.replace("✅", "❌"))
    if not passed:
        all_passed = False

if all_passed:
    print("\n🎉 转换完全符合预期!")
else:
    print("\n⚠️ 转换结果与预期不完全一致")

# 对比差异
print("\n" + "=" * 80)
print("详细对比:")
print("=" * 80)
original_lines = original_code.strip().split('\n')
result_lines = result.strip().split('\n')

for i, (orig, conv) in enumerate(zip(original_lines, result_lines), 1):
    if orig.strip() == conv.strip():
        print(f"行 {i}: ✓ 相同")
    else:
        print(f"行 {i}: ✗ 不同")
        print(f"  原始: {orig.strip()}")
        print(f"  转换: {conv.strip()}")
