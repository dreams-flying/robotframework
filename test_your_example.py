"""
测试您提供的具体例子
验证"选择"按钮的 click() 行是否被正确删除
"""

# 您提供的原始代码
original = '''    page2.get_by_role("button", name="发票上传").click()
    page2.get_by_role("button", name="选择", exact=True).click()
    page2.get_by_role("button", name="选择", exact=True).set_input_files(["C:/Users/admin/Desktop/文件/发票/服装.pdf"])
    page2.get_by_role("button", name="上传", exact=True).click()
'''

# 期望的输出（第2行应该被删除）
expected = '''    page2.get_by_role("button", name="发票上传").click()
    page2.locator('input[type="file"]').set_input_files(["C:/Users/admin/Desktop/文件/发票/服装.pdf"])
    page2.get_by_role("button", name="上传", exact=True).click()
'''

from universal_playwright_converter import convert_all_operations

result = convert_all_operations(original)

print("=" * 80)
print("📝 原始代码 (4行):")
print("=" * 80)
for i, line in enumerate(original.split('\n'), 1):
    if line.strip():
        print(f"行{i}: {line}")
print()

print("=" * 80)
print("✨ 转换后的代码 (应该只有3行):")
print("=" * 80)
for i, line in enumerate(result.split('\n'), 1):
    if line.strip():
        print(f"行{i}: {line}")
print()

print("=" * 80)
print("🔍 验证:")
print("=" * 80)

# 计算行数
original_lines = [l for l in original.split('\n') if l.strip()]
result_lines = [l for l in result.split('\n') if l.strip()]

print(f"✓ 原始代码行数: {len(original_lines)}")
print(f"✓ 转换后行数: {len(result_lines)}")

# 检查关键点
checks = [
    (len(result_lines) == len(original_lines) - 1, f"行数减少1 (从{len(original_lines)}行到{len(result_lines)}行)"),
    ('page2.get_by_role("button", name="选择", exact=True).click()' not in result, '"选择"按钮的 .click() 被删除'),
    ('page2.locator(\'input[type="file"]\')' in result, '使用了正确的 input[type="file"] 定位器'),
    ('服装.pdf' in result, '保留了完整的文件路径'),
]

print()
all_passed = True
for passed, description in checks:
    status = "✅" if passed else "❌"
    print(f"{status} {description}")
    if not passed:
        all_passed = False

print()
if all_passed:
    print("🎉 转换完全正确！")
else:
    print("⚠️ 转换有问题")

# 对比输出
print()
print("=" * 80)
print("📊 逐行对比:")
print("=" * 80)
print("\n原始代码:")
print(original)
print("\n转换后:")
print(result)
print("\n期望输出:")
print(expected)

# 检查是否匹配期望
if result.strip() == expected.strip():
    print("\n✅ 转换结果与期望完全一致！")
else:
    print("\n⚠️ 转换结果与期望不完全一致")
    print("\n差异:")
    for i, (r, e) in enumerate(zip(result.split('\n'), expected.split('\n')), 1):
        if r != e:
            print(f"  行{i} 不同:")
            print(f"    结果: {repr(r)}")
            print(f"    期望: {repr(e)}")
