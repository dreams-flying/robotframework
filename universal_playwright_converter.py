"""
统一的 Playwright 代码转换器
自动转换 playwright codegen 生成的代码，包括:
  1. 日期选择 → select_calendar_date()
  2. 时间选择 → select_calendar_time()
  3. 文件上传 → 正确的 input[type="file"] 操作

使用示例:
    python universal_playwright_converter.py input.py output.py
"""

import re
from typing import List, Optional

# ==================== 导入子转换器 ====================

# 从 calendar_converter 导入函数
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from calendar_converter import try_convert_date_selection, try_convert_time_selection
except ImportError:
    print("⚠️ 警告: 无法导入 calendar_converter，日历和时间转换功能将不可用")
    try_convert_date_selection = None
    try_convert_time_selection = None


# ==================== 文件上传转换 ====================

def try_convert_file_upload(lines: List[str], index: int) -> Optional[dict]:
    """
    尝试识别并转换文件上传模式

    模式 1: 两行模式（需要删除第一行）
        第1行: page.get_by_role("button", name="选择", exact=True).click()
        （可能有空行/注释）
        第N行: page.get_by_role("button", name="选择", exact=True).set_input_files([...])

    模式 2: 单行模式（只需转换）
        page.get_by_role("button", name="选择").set_input_files([...])

    返回: {'code': 转换后的代码, 'next_index': 下一行索引, 'delete_first_line': 是否删除第一行}
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

    while next_code_index < len(lines):
        next_line = lines[next_code_index].strip()

        # 如果是空行或注释，继续查找
        if not next_line or next_line.startswith('#'):
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
                    return result

    return None


def is_select_button_click(line: str) -> bool:
    """判断是否是点击"选择"按钮的行"""
    if not line.endswith('.click()'):
        return False

    if '.get_by_role("button"' not in line:
        return False

    select_keywords = ['选择', 'browse', 'choose', 'Browse', 'Choose', 'Select']
    name_pattern = r'name=(["\'])(.*?)\1'
    match = re.search(name_pattern, line)

    if match:
        name_value = match.group(2)
        for keyword in select_keywords:
            if keyword in name_value:
                return True

    return False


def is_same_element(line1: str, line2: str) -> bool:
    """判断两行代码是否操作同一个元素"""
    locator1 = re.sub(r'\.(click|set_input_files)\(.*\)\s*$', '', line1.strip())
    locator2 = re.sub(r'\.(click|set_input_files)\(.*\)\s*$', '', line2.strip())
    return locator1 == locator2


def convert_set_input_files_line(lines: List[str], index: int) -> Optional[dict]:
    """转换包含 set_input_files 的行"""
    if index >= len(lines):
        return None

    line_original = lines[index]
    line = line_original.strip()

    if '.set_input_files(' not in line:
        return None

    # 提取缩进
    indent_match = re.match(r'(\s*)', line_original)
    indent = indent_match.group(1) if indent_match else ''

    # 提取 page 变量名
    page_pattern = r'^(page\d*)\.'
    page_match = re.search(page_pattern, line)

    if not page_match:
        return None

    page_var = page_match.group(1)

    # 提取 set_input_files 的参数
    params_pattern = r'\.set_input_files\((.*)\)\s*$'
    params_match = re.search(params_pattern, line)

    if not params_match:
        return None

    params = params_match.group(1)

    # 生成转换后的代码
    converted = f"{indent}{page_var}.locator('input[type=\"file\"]').set_input_files({params})"

    return {
        'code': converted,
        'next_index': index + 1,
        'delete_first_line': False
    }


# ==================== 统一转换器 ====================

def convert_all_operations(source_code: str) -> str:
    """
    统一转换所有操作：日期、时间、文件上传
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

        # 1. 检查日期选择模式
        if try_convert_date_selection:
            date_pattern = try_convert_date_selection(lines, i)
            if date_pattern:
                converted_lines.append(date_pattern['code'])
                i = date_pattern['next_index']
                continue

        # 2. 检查时间选择模式
        if try_convert_time_selection:
            time_pattern = try_convert_time_selection(lines, i)
            if time_pattern:
                converted_lines.append(time_pattern['code'])
                i = time_pattern['next_index']
                continue

        # 不匹配任何模式，保持原样
        converted_lines.append(line)
        i += 1

    return '\n'.join(converted_lines)


def add_helper_imports(code: str) -> str:
    """添加辅助函数导入"""
    # 检查是否需要添加导入
    needs_calendar = 'select_calendar_date' in code or 'select_calendar_time' in code

    if not needs_calendar:
        return code

    import_statement = """# 日历和时间选择辅助函数
from calendar_helpers import select_calendar_date, select_calendar_time

"""

    # 查找第一个非注释、非空行、非 import 的位置
    lines = code.split('\n')
    insert_index = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if stripped.startswith('import ') or stripped.startswith('from '):
            insert_index = i + 1
            continue
        insert_index = i
        break

    lines.insert(insert_index, import_statement.rstrip())
    return '\n'.join(lines)


def process_file(input_file: str, output_file: str):
    """处理整个文件"""
    with open(input_file, 'r', encoding='utf-8') as f:
        source_code = f.read()

    # 转换代码
    converted_code = convert_all_operations(source_code)

    # 如果转换了日历/时间代码，添加导入
    if converted_code != source_code:
        converted_code = add_helper_imports(converted_code)

    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(converted_code)

    # 统计转换信息
    date_count = converted_code.count('select_calendar_date')
    time_count = converted_code.count('select_calendar_time')
    file_count = converted_code.count("locator('input[type=\"file\"]')")

    print(f"✅ 转换完成: {input_file} -> {output_file}")
    if date_count > 0:
        print(f"   📅 日期选择: {date_count} 处")
    if time_count > 0:
        print(f"   ⏰ 时间选择: {time_count} 处")
    if file_count > 0:
        print(f"   📁 文件上传: {file_count} 处")


# ==================== 测试用例 ====================

def test_all_conversions():
    """测试所有转换功能"""

    test_input = '''    # 日期和时间选择
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.SDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name=date_day_5, exact=True).first.click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.STIME").get_by_label("").click()
    page2.get_by_role("option", name=start_time).click()

    # 文件上传
    page2.get_by_role("button", name="发票上传").click()
    page2.get_by_role("button", name="选择", exact=True).click()
    page2.get_by_role("button", name="选择", exact=True).set_input_files(["C:/file.pdf"])
    page2.get_by_role("button", name="上传", exact=True).click()

    # 其他操作
    page2.get_by_role("textbox").fill("some text")
'''

    result = convert_all_operations(test_input)

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
        ('select_calendar_date' in result, "✅ 转换日期选择"),
        ('select_calendar_time' in result, "✅ 转换时间选择"),
        ("locator('input[type=\"file\"]')" in result, "✅ 转换文件上传"),
        ('name="选择"' not in result or result.count('name="选择"') < test_input.count('name="选择"'), "✅ 删除了多余的'选择'按钮"),
    ]

    print("验证结果:")
    all_passed = True
    for passed, description in checks:
        if passed:
            print(description)
        else:
            print(description.replace("✅", "❌"))
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
        test_all_conversions()
    elif len(sys.argv) == 3:
        # 处理文件
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        process_file(input_file, output_file)
    else:
        print("使用方法:")
        print("  python universal_playwright_converter.py                    # 运行测试")
        print("  python universal_playwright_converter.py input.py output.py # 转换文件")
