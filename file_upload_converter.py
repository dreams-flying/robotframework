"""
Playwright 文件上传代码转换器
将 playwright codegen 生成的文件上传代码转换为正确的 input 元素操作

转换模式:
    转换前:
        page.get_by_role("button", name="选择", exact=True).click()
        page.get_by_role("button", name="选择", exact=True).set_input_files([...])

    转换后:
        # 删除 click() 行
        page.locator('input[type="file"]').set_input_files([...])

使用示例:
    python file_upload_converter.py input.py output.py
"""

import re
from typing import List, Optional


def convert_file_upload_operations(source_code: str) -> str:
    """
    转换文件上传操作

    识别并转换以下模式:
    1. 点击"选择"按钮的行 → 删除
    2. 在"选择"按钮上调用 set_input_files → 改为在 input[type="file"] 上调用
    """
    lines = source_code.split('\n')
    converted_lines = []
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()

        # 先检查是否是文件上传模式（包括空行）
        upload_pattern = try_convert_file_upload(lines, i)
        if upload_pattern:
            if upload_pattern.get('delete_first_line'):
                # 这是两行模式：删除 click 行和中间的空行，添加转换后的 set_input_files
                # 同时删除 click 行之前的空行（如果存在）
                if converted_lines and not converted_lines[-1].strip():
                    converted_lines.pop()  # 删除最后一个空行
                converted_lines.append(upload_pattern['code'])
                i = upload_pattern['next_index']
            else:
                # 单行模式：只转换当前行
                converted_lines.append(upload_pattern['code'])
                i += 1
            continue

        # 空行和注释：保持原样
        if not line.strip() or line.strip().startswith('#'):
            converted_lines.append(line)
            i += 1
            continue

        # 不匹配任何模式，保持原样
        converted_lines.append(line)
        i += 1

    return '\n'.join(converted_lines)


def try_convert_file_upload(lines: List[str], index: int) -> Optional[dict]:
    """
    尝试识别并转换文件上传模式

    模式 1: 两行模式（需要删除第一行）
        第1行: page.get_by_role("button", name="选择", exact=True).click()
        （可能有空行/注释）
        第N行: page.get_by_role("button", name="选择", exact=True).set_input_files([...])

    模式 2: 单行模式（只需转换）
        page.get_by_role("button", name="选择").set_input_files([...])

    返回: {'code': 转换后的代码, 'next_index': 下一行索引, 'delete_first_line': 是否删除第一行, 'skip_empty_lines': 要跳过的空行数}
    """
    if index >= len(lines):
        return None

    line1_original = lines[index]
    line1 = line1_original.strip()

    # 检查当前行是否包含 set_input_files
    if '.set_input_files(' in line1:
        # 这是 set_input_files 的行，需要转换
        return convert_set_input_files_line(lines, index)

    # 检查是否是点击"选择"按钮的行
    if not is_select_button_click(line1):
        return None

    # 向后查找 set_input_files 行（跳过空行和注释）
    next_code_index = index + 1
    empty_lines_between = []

    while next_code_index < len(lines):
        next_line = lines[next_code_index].strip()

        # 如果是空行或注释，记录并继续查找
        if not next_line or next_line.startswith('#'):
            empty_lines_between.append(next_code_index)
            next_code_index += 1
            continue

        # 找到了非空非注释行
        break

    # 检查找到的行是否是 set_input_files
    if next_code_index < len(lines):
        next_line = lines[next_code_index].strip()

        if '.set_input_files(' in next_line:
            # 检查两行是否操作同一个元素
            if is_same_element(line1, next_line):
                # 这是两行模式，转换 set_input_files 行，删除 click 行和中间的空行
                result = convert_set_input_files_line(lines, next_code_index)
                if result:
                    result['delete_first_line'] = True
                    result['next_index'] = next_code_index + 1  # 跳到 set_input_files 的下一行
                    result['empty_lines_to_delete'] = empty_lines_between  # 要删除的空行索引
                    return result

    return None


def is_select_button_click(line: str) -> bool:
    """
    判断是否是点击"选择"按钮的行

    匹配模式:
        - page.get_by_role("button", name="选择").click()
        - page.get_by_role("button", name="选择", exact=True).click()
        - page2.get_by_role("button", name="选择文件").click()
    """
    # 必须以 .click() 结尾
    if not line.endswith('.click()'):
        return False

    # 必须包含 get_by_role("button"
    if '.get_by_role("button"' not in line:
        return False

    # 必须包含 name= 且值包含"选择"或"browse"或"choose"
    select_keywords = ['选择', 'browse', 'choose', 'Browse', 'Choose', 'Select']

    # 匹配 name="xxx" 或 name='xxx'
    name_pattern = r'name=(["\'])(.*?)\1'
    match = re.search(name_pattern, line)

    if match:
        name_value = match.group(2)
        # 检查是否包含选择相关的关键词
        for keyword in select_keywords:
            if keyword in name_value:
                return True

    return False


def is_same_element(line1: str, line2: str) -> bool:
    """
    判断两行代码是否操作同一个元素

    比较定位器部分（.click() 或 .set_input_files() 之前的部分）
    """
    # 提取定位器部分（去掉末尾的方法调用）
    locator1 = re.sub(r'\.(click|set_input_files)\(.*\)\s*$', '', line1.strip())
    locator2 = re.sub(r'\.(click|set_input_files)\(.*\)\s*$', '', line2.strip())

    return locator1 == locator2


def convert_set_input_files_line(lines: List[str], index: int) -> Optional[dict]:
    """
    转换包含 set_input_files 的行

    转换前:
        page.get_by_role("button", name="选择").set_input_files(["file.pdf"])

    转换后:
        page.locator('input[type="file"]').set_input_files(["file.pdf"])
    """
    if index >= len(lines):
        return None

    line_original = lines[index]
    line = line_original.strip()

    # 检查是否包含 set_input_files
    if '.set_input_files(' not in line:
        return None

    # 提取缩进
    indent_match = re.match(r'(\s*)', line_original)
    indent = indent_match.group(1) if indent_match else ''

    # 提取 page 变量名和 set_input_files 参数
    # 匹配: page2.get_by_xxx(...).set_input_files([...])
    page_pattern = r'^(page\d*)\.'
    page_match = re.search(page_pattern, line)

    if not page_match:
        return None

    page_var = page_match.group(1)  # page 或 page2

    # 提取 set_input_files 的参数
    # 匹配: set_input_files(参数)
    params_pattern = r'\.set_input_files\((.*)\)\s*$'
    params_match = re.search(params_pattern, line)

    if not params_match:
        return None

    params = params_match.group(1)  # 参数部分

    # 生成转换后的代码
    converted = f"{indent}{page_var}.locator('input[type=\"file\"]').set_input_files({params})"

    return {
        'code': converted,
        'next_index': index + 1,
        'delete_first_line': False
    }


def add_helper_comment(code: str) -> str:
    """在代码开头添加说明注释"""
    comment = """# 文件上传代码已自动转换
# 原始的 get_by_role("button", name="选择") 已替换为 locator('input[type="file"]')

"""
    return comment + code


def process_file(input_file: str, output_file: str):
    """处理整个文件"""
    with open(input_file, 'r', encoding='utf-8') as f:
        source_code = f.read()

    # 转换代码
    converted_code = convert_file_upload_operations(source_code)

    # 如果有改动，添加注释
    if converted_code != source_code:
        # 不添加注释，保持简洁
        pass

    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(converted_code)

    print(f"✅ 转换完成: {input_file} -> {output_file}")


# ==================== 测试用例 ====================

def test_converter():
    """测试转换器"""

    test_input = '''    page2.get_by_role("button", name="发票上传").click()
    page2.get_by_role("button", name="选择", exact=True).click()
    page2.get_by_role("button", name="选择", exact=True).set_input_files(["C:/Users/admin/Desktop/文件/发票/服装.pdf"])
    page2.get_by_role("button", name="上传", exact=True).click()

    # 另一个上传
    page2.get_by_text("Upload File").click()
    page2.get_by_role("button", name="Browse").click()
    page2.get_by_role("button", name="Browse").set_input_files(["document.pdf"])
    page2.get_by_role("button", name="Submit").click()
'''

    expected_pattern = '''page2.locator('input[type="file"]').set_input_files('''

    result = convert_file_upload_operations(test_input)

    print("=" * 80)
    print("输入代码:")
    print("=" * 80)
    print(test_input)
    print("\n" + "=" * 80)
    print("输出代码:")
    print("=" * 80)
    print(result)
    print("\n" + "=" * 80)

    # 验证
    checks = [
        (expected_pattern in result, "转换为 locator('input[type=\"file\"]')"),
        (result.count('.click()\n    page') < test_input.count('.click()\n    page'), "删除了点击'选择'的行"),
        ('name="选择"' not in result or result.count('name="选择"') < test_input.count('name="选择"'), "减少了'选择'按钮的引用"),
    ]

    all_passed = True
    print("验证结果:")
    for passed, description in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {description}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 所有测试通过!")
    else:
        print("\n⚠️ 部分测试失败")

    return all_passed


if __name__ == '__main__':
    import sys

    if len(sys.argv) == 1:
        # 运行测试
        test_converter()
    elif len(sys.argv) == 3:
        # 处理文件
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        process_file(input_file, output_file)
    else:
        print("使用方法:")
        print("  python file_upload_converter.py                    # 运行测试")
        print("  python file_upload_converter.py input.py output.py # 转换文件")
