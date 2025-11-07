"""
调试文件上传转换问题
"""

test_code = '''    page2.get_by_role("button", name="发票上传").click()
    page2.get_by_role("button", name="选择", exact=True).click()
    page2.get_by_role("button", name="选择", exact=True).set_input_files(["C:/file.pdf"])
    page2.get_by_role("button", name="上传", exact=True).click()
'''

print("测试代码:")
print(test_code)

# 导入转换器
from universal_playwright_converter import convert_all_operations, try_convert_file_upload

# 逐行调试
lines = test_code.split('\n')
print(f"\n总共 {len(lines)} 行")

for i, line in enumerate(lines):
    print(f"\n行 {i}: {repr(line)}")
    if line.strip():
        result = try_convert_file_upload(lines, i)
        if result:
            print(f"  匹配! delete_first_line={result.get('delete_first_line')}, next_index={result.get('next_index')}")
            print(f"  转换后: {result.get('code')}")
        else:
            print(f"  不匹配")

print("\n" + "=" * 80)
print("完整转换:")
print("=" * 80)
result = convert_all_operations(test_code)
print(result)

# 检查
if 'name="选择"' in result:
    print("\n❌ 错误: '选择' 按钮的 click() 还在!")
else:
    print("\n✅ 正确: '选择' 按钮的 click() 已删除!")
