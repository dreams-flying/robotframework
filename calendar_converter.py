"""
日历和时间选择代码转换器
将 Playwright codegen 生成的日期/时间选择代码转换为辅助函数调用

使用示例:
    python calendar_converter.py input.py output.py
"""

import re
from typing import List, Tuple, Optional


def convert_calendar_operations(source_code: str) -> str:
    """
    转换日历和时间选择操作

    输入示例:
        page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.SDATE").get_by_placeholder("YYYYMMDD").click()
        page2.get_by_role("cell", name=date_day_5, exact=True).first.click()

    输出:
        select_calendar_date(
            page2,
            page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.SDATE").get_by_placeholder("YYYYMMDD"),
            target_day=date_day_5
        )
    """
    lines = source_code.split('\n')
    converted_lines = []
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()

        # 跳过空行和注释
        if not line.strip() or line.strip().startswith('#'):
            converted_lines.append(line)
            i += 1
            continue

        # 检查是否是日期选择模式
        date_pattern = try_convert_date_selection(lines, i)
        if date_pattern:
            converted_lines.append(date_pattern['code'])
            i = date_pattern['next_index']
            continue

        # 检查是否是时间选择模式
        time_pattern = try_convert_time_selection(lines, i)
        if time_pattern:
            converted_lines.append(time_pattern['code'])
            i = time_pattern['next_index']
            continue

        # 不匹配任何模式，保持原样
        converted_lines.append(line)
        i += 1

    return '\n'.join(converted_lines)


def try_convert_date_selection(lines: List[str], index: int) -> Optional[dict]:
    """
    尝试识别并转换日期选择模式

    模式:
        第1行: xxx.get_by_placeholder("YYYYMMDD").click()
        第2行: page.get_by_role("cell", name=date_param, exact=True).first.click()

    返回: {'code': 转换后的代码, 'next_index': 下一行索引} 或 None
    """
    if index >= len(lines) - 1:
        return None

    line1_original = lines[index]  # ✅ 保留原始行（含缩进）
    line2_original = lines[index + 1]  # ✅ 保留原始行（含缩进）

    line1 = line1_original.strip()  # 用于内容检查
    line2 = line2_original.strip()  # 用于内容检查

    # 检查第1行：是否是点击 YYYYMMDD 占位符的日期输入框
    if '.get_by_placeholder("YYYYMMDD").click()' not in line1:
        return None

    # 检查第2行：是否是点击日期单元格
    # 匹配以下所有模式:
    #   - page2.get_by_role("cell", name=date_day_5, exact=True).first.click()
    #   - page2.get_by_role("cell", name=date_day_7, exact=True).click()
    #   - page2.get_by_role("cell", name=date_day_8, exact=True).nth(1).click()
    # ✅ .first 和 .nth(数字) 都是可选的
    cell_pattern = r'(page\d*)\s*\.get_by_role\("cell",\s*name=([a-zA-Z_]\w*),\s*exact=True\)(?:\.(?:first|nth\(\d+\)))?\.click\(\)'
    match2 = re.search(cell_pattern, line2)

    if not match2:
        return None

    # 提取信息
    page_var = match2.group(1)  # page2
    date_param = match2.group(2)  # date_day_5

    # ✅ 从原始行提取缩进和定位器（去掉 .click()）
    locator_match = re.match(r'(\s*)(.*?)\.click\(\)\s*$', line1_original)
    if not locator_match:
        return None

    indent = locator_match.group(1)  # ✅ 从原始行获取缩进
    locator_code = locator_match.group(2)

    # 生成转换后的代码
    converted = f"{indent}select_calendar_date(\n"
    converted += f"{indent}    {page_var},\n"
    converted += f"{indent}    {locator_code},\n"
    converted += f"{indent}    target_day={date_param}\n"
    converted += f"{indent})"

    return {
        'code': converted,
        'next_index': index + 2  # 跳过两行
    }


def try_convert_time_selection(lines: List[str], index: int) -> Optional[dict]:
    """
    尝试识别并转换时间选择模式

    模式:
        第1行: xxx.get_by_label("").click() 或 xxx.click()
        第2行: page.get_by_role("option", name=time_param).click()

    返回: {'code': 转换后的代码, 'next_index': 下一行索引} 或 None
    """
    if index >= len(lines) - 1:
        return None

    line1_original = lines[index]  # ✅ 保留原始行（含缩进）
    line2_original = lines[index + 1]  # ✅ 保留原始行（含缩进）

    line1 = line1_original.strip()  # 用于内容检查
    line2 = line2_original.strip()  # 用于内容检查

    # 检查第2行：是否是点击时间选项
    # 匹配: page2.get_by_role("option", name=start_time).click()
    option_pattern = r'(page\d*)\s*\.get_by_role\("option",\s*name=([a-zA-Z_]\w*)\)\.click\(\)'
    match2 = re.search(option_pattern, line2)

    if not match2:
        return None

    # 检查第1行：是否是点击某个输入框
    if not line1.endswith('.click()'):
        return None

    # 额外检查：如果第1行是日期选择器，则跳过（避免误匹配）
    if '.get_by_placeholder("YYYYMMDD")' in line1:
        return None

    # 提取信息
    page_var = match2.group(1)  # page2
    time_param = match2.group(2)  # start_time

    # ✅ 从原始行提取缩进和定位器（去掉 .click()）
    locator_match = re.match(r'(\s*)(.*?)\.click\(\)\s*$', line1_original)
    if not locator_match:
        return None

    indent = locator_match.group(1)  # ✅ 从原始行获取缩进
    locator_code = locator_match.group(2)

    # 生成转换后的代码
    converted = f"{indent}select_calendar_time(\n"
    converted += f"{indent}    {page_var},\n"
    converted += f"{indent}    {locator_code},\n"
    converted += f"{indent}    {time_param}\n"
    converted += f"{indent})"

    return {
        'code': converted,
        'next_index': index + 2  # 跳过两行
    }


def add_helper_functions_import(code: str) -> str:
    """在代码开头添加辅助函数导入"""
    import_statement = """# 日历和时间选择辅助函数
from calendar_helpers import select_calendar_date, select_calendar_time

"""

    # 查找第一个非注释、非空行、非 import 的位置
    lines = code.split('\n')
    insert_index = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        # 跳过开头的注释和空行
        if not stripped or stripped.startswith('#'):
            continue
        # 如果遇到 import，继续查找
        if stripped.startswith('import ') or stripped.startswith('from '):
            insert_index = i + 1
            continue
        # 找到第一个非 import 行
        insert_index = i
        break

    # 插入 import
    lines.insert(insert_index, import_statement.rstrip())
    return '\n'.join(lines)


def process_file(input_file: str, output_file: str):
    """处理整个文件"""
    with open(input_file, 'r', encoding='utf-8') as f:
        source_code = f.read()

    # 转换代码
    converted_code = convert_calendar_operations(source_code)

    # 添加辅助函数导入（如果转换了任何代码）
    if converted_code != source_code:
        converted_code = add_helper_functions_import(converted_code)

    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(converted_code)

    print(f"✅ 转换完成: {input_file} -> {output_file}")


# ==================== 测试用例 ====================

def test_converter():
    """测试转换器"""

    test_input = '''    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.SDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name=date_day_5, exact=True).first.click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.STIME").get_by_label("").click()
    page2.get_by_role("option", name=start_time).click()

    # 其他操作
    page2.get_by_role("textbox").fill(some_value)

    # 另一个日期选择
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.EDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name=date_day_20, exact=True).first.click()
'''

    expected_output = '''    select_calendar_date(
        page2,
        page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.SDATE").get_by_placeholder("YYYYMMDD"),
        target_day=date_day_5
    )
    select_calendar_time(
        page2,
        page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.STIME").get_by_label(""),
        start_time
    )

    # 其他操作
    page2.get_by_role("textbox").fill(some_value)

    # 另一个日期选择
    select_calendar_date(
        page2,
        page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.EDATE").get_by_placeholder("YYYYMMDD"),
        target_day=date_day_20
    )
'''

    result = convert_calendar_operations(test_input)

    print("=" * 60)
    print("输入代码:")
    print("=" * 60)
    print(test_input)
    print("\n" + "=" * 60)
    print("输出代码:")
    print("=" * 60)
    print(result)
    print("\n" + "=" * 60)

    # 简单验证
    assert 'select_calendar_date' in result
    assert 'select_calendar_time' in result
    assert 'target_day=date_day_5' in result
    assert 'target_day=date_day_20' in result

    print("✅ 测试通过!")


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
        print("  python calendar_converter.py                    # 运行测试")
        print("  python calendar_converter.py input.py output.py # 转换文件")
