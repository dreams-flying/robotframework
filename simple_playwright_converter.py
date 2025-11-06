"""
简单而实用的Playwright代码转换器

策略：保留原始代码，只做必要的参数化
不试图解析复杂的定位器链，保证100%准确性
"""

import re
from typing import Dict, List, Tuple
from pathlib import Path


def extract_parameterizable_fills(script_content: str) -> Dict[str, Tuple[str, List[int]]]:
    """
    提取可参数化的fill操作

    返回: {参数名: (默认值, [行号列表])}
    """
    params = {}
    lines = script_content.split('\n')

    for line_no, line in enumerate(lines, 1):
        # 查找fill操作
        if '.fill(' in line:
            fill_match = re.search(r'\.fill\(["\']([^"\']+)["\']\)', line)
            if fill_match:
                value = fill_match.group(1)

                # 尝试在同一行找到WF_字段名
                field_match = re.search(r'name=["\']WF_[A-Z_]+\.([A-Z]+)["\']', line)
                if field_match:
                    field_name = field_match.group(1).lower()

                    if field_name not in params:
                        params[field_name] = (value, [])
                    params[field_name][1].append(line_no)

    return params


def convert_playwright_to_parameterized(script_content: str, function_name: str = "execute_automation") -> str:
    """
    转换Playwright脚本为参数化函数

    核心策略：
    1. 保留所有原始代码（保证正确性）
    2. 只替换fill操作中的hard-coded值
    3. 自动处理popup和page变量
    """
    lines = script_content.split('\n')

    # 1. 提取可参数化的字段
    params = extract_parameterizable_fills(script_content)

    # 2. 识别popup操作和page变量
    popup_vars = []  # [(page_var_name, parent_var, popup_info_var, trigger_line)]
    for line_no, line in enumerate(lines, 1):
        if 'expect_popup' in line:
            popup_match = re.search(r'with\s+(\w+)\.expect_popup\(\)\s+as\s+(\w+):', line)
            if popup_match:
                parent_var = popup_match.group(1)
                popup_info_var = popup_match.group(2)

                # 下一行通常是触发操作
                if line_no < len(lines):
                    trigger_line = line_no + 1

                # 再下一行通常是赋值: page1 = page1_info.value
                if line_no + 1 < len(lines):
                    assign_line = lines[line_no + 1].strip()
                    assign_match = re.match(r'(\w+)\s*=\s*\w+\.value', assign_line)
                    if assign_match:
                        page_var_name = assign_match.group(1)
                        popup_vars.append((page_var_name, parent_var, popup_info_var, trigger_line))

    # 3. 生成函数代码
    func_lines = []

    # 函数签名
    func_lines.append(f"def {function_name}(")
    func_lines.append("    playwright: Playwright,")
    func_lines.append('    url: str = "https://h5-office.bestpay.com.cn/sec-iam-plus-h5/index.html#/portal/list",')

    # 添加参数
    for param_name, (default_value, _) in sorted(params.items()):
        func_lines.append(f'    {param_name}: str = "{default_value}",')

    # 移除最后一个逗号，添加闭括号
    if func_lines[-1].endswith(','):
        func_lines[-1] = func_lines[-1][:-1]
    func_lines.append(") -> None:")

    # 文档字符串
    func_lines.append('    """')
    func_lines.append('    自动化执行函数 - 从Playwright Codegen转换')
    func_lines.append('')
    func_lines.append('    参数:')
    func_lines.append('        playwright: Playwright实例')
    func_lines.append('        url: 访问的URL')
    for param_name, (default_value, _) in sorted(params.items()):
        func_lines.append(f'        {param_name}: {param_name}字段的值（默认: {default_value}）')
    func_lines.append('    """')

    # 浏览器设置
    func_lines.append('    browser = playwright.chromium.launch(headless=False)')
    func_lines.append('    context = browser.new_context()')
    func_lines.append('    page = context.new_page()')
    func_lines.append('')
    func_lines.append('    # 导航到页面')
    func_lines.append('    page.goto(url)')
    func_lines.append('')

    # 4. 处理代码主体
    in_function = False
    skip_until = 0  # 用于跳过popup块内的行
    processed_popups = set()  # 已处理的popup

    for line_no, line in enumerate(lines, 1):
        stripped = line.strip()

        # 跳过已处理的行
        if line_no <= skip_until:
            continue

        # 检测函数开始
        if 'def run(' in stripped or 'def main(' in stripped:
            in_function = True
            continue

        # 跳过初始化代码和重复操作
        if any(skip in stripped for skip in [
            'browser = playwright',
            'context = browser.new_context',
            'page = context.new_page',
            'page.goto(',           # 跳过原始goto（已有参数化版本）
            'with sync_playwright',
            'browser.close',
            'context.close',
            'run(playwright)',      # 跳过原函数调用
        ]):
            continue

        if not in_function or not stripped or stripped.startswith('#'):
            continue

        # 检查是否是popup操作
        is_popup_start = False
        for popup_info in popup_vars:
            page_var, parent_var, popup_info_var, trigger_line = popup_info
            if line_no == trigger_line - 1 and popup_info_var not in processed_popups:
                # 这是popup开始
                is_popup_start = True
                processed_popups.add(popup_info_var)

                # 添加popup块
                func_lines.append(f'    # Popup操作: {page_var}')
                func_lines.append(f'    with {parent_var}.expect_popup() as {popup_info_var}:')

                # 添加触发操作（下一行）
                if trigger_line <= len(lines):
                    trigger_code = lines[trigger_line - 1].strip()

                    # 参数化trigger代码
                    for param_name, (value, line_nums) in params.items():
                        if trigger_line in line_nums:
                            trigger_code = trigger_code.replace(f"'{value}'", param_name)
                            trigger_code = trigger_code.replace(f'"{value}"', param_name)

                    func_lines.append(f'        {trigger_code}')

                # 添加赋值
                func_lines.append(f'    {page_var} = {popup_info_var}.value')
                func_lines.append('')

                # 跳过popup相关的3行（with语句、触发操作、赋值）
                skip_until = trigger_line + 1
                break

        if is_popup_start:
            continue

        # 处理普通代码行
        code_line = stripped

        # 参数化fill操作
        for param_name, (value, line_nums) in params.items():
            if line_no in line_nums:
                code_line = code_line.replace(f"fill('{value}')", f"fill({param_name})")
                code_line = code_line.replace(f'fill("{value}")', f"fill({param_name})")

        # 添加代码行
        func_lines.append(f'    {code_line}')

    # 添加清理代码
    func_lines.append('')
    func_lines.append('    # 清理')
    func_lines.append('    context.close()')
    func_lines.append('    browser.close()')

    return '\n'.join(func_lines)


def convert_file(input_file: str, output_file: str = None, function_name: str = "execute_automation"):
    """
    转换文件

    参数:
        input_file: 输入的Playwright脚本文件
        output_file: 输出文件（可选，默认为input_file_converted.py）
        function_name: 生成的函数名
    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"❌ 错误: 找不到文件 '{input_file}'")
        return

    # 读取脚本
    with open(input_path, 'r', encoding='utf-8') as f:
        script_content = f.read()

    print(f"📖 读取脚本: {input_file}")

    # 转换
    converted_code = convert_playwright_to_parameterized(script_content, function_name)

    # 确定输出文件
    if output_file is None:
        output_file = input_path.parent / f"{input_path.stem}_converted.py"
    else:
        output_file = Path(output_file)

    # 写入
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('from playwright.sync_api import Playwright, sync_playwright\n')
        f.write('import re\n\n')
        f.write(converted_code)
        f.write('\n\n')
        f.write('# 使用示例:\n')
        f.write('# with sync_playwright() as playwright:\n')
        f.write(f'#     {function_name}(playwright)\n')

    print(f"✅ 转换完成: {output_file}")
    print(f"\n📊 参数化信息:")

    # 显示提取的参数
    params = extract_parameterizable_fills(script_content)
    for param_name, (value, line_nums) in sorted(params.items()):
        print(f"  - {param_name}: '{value}' (在 {len(line_nums)} 处使用)")

    return str(output_file)


def convert_from_string(script_content: str) -> str:
    """
    从字符串转换

    参数:
        script_content: Playwright脚本内容

    返回:
        转换后的代码
    """
    converted_code = convert_playwright_to_parameterized(script_content)

    full_code = 'from playwright.sync_api import Playwright, sync_playwright\n'
    full_code += 'import re\n\n'
    full_code += converted_code

    return full_code


# ==================== 测试 ====================

if __name__ == "__main__":
    import sys

    # 测试脚本
    test_script = '''
import re
from playwright.sync_api import Playwright, sync_playwright, expect

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://h5-office.bestpay.com.cn/sec-iam-plus-h5/index.html#/portal/list")
    with page.expect_popup() as page1_info:
        page.get_by_text("OA系统").first.click()
    page1 = page1_info.value
    with page1.expect_popup() as page2_info:
        page1.locator("#magnet_8490099577463589529").get_by_title("人力系统").locator("span").click()
    page2 = page2_info.value
    page2.get_by_role("tab", name="员工自助").click()
    page2.get_by_role("link", name="员工出差申请单-新").click()
    page2.get_by_role("row", name="出差类型").get_by_label("").click()
    page2.get_by_role("option", name="外地出差").click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.SDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name="5", exact=True).first.click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.STIME").get_by_label("").click()
    page2.get_by_role("option", name="08:30").click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.EDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name="7", exact=True).click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.ETIME").get_by_label("").click()
    page2.get_by_role("option", name="17:30").click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.APPCAUSE").get_by_role("textbox").click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.APPCAUSE").get_by_role("textbox").fill("参加学术会议")
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.COST").get_by_role("textbox").click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.COST").get_by_role("textbox").fill("3500")
    page2.get_by_role("textbox", name="否").click()
    page2.get_by_role("option", name="否").click()
    page2.get_by_role("button", name="了解").click()
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.FROMCITY").get_by_role("textbox").click()
    page2.get_by_role("list").filter(has_text="上海上海").locator("span").click()
    page2.get_by_role("radio", name="上海").check()
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.TOCITY").get_by_role("textbox").click()
    page2.get_by_role("list").filter(has_text="北京北京").locator("span").click()
    page2.get_by_role("radio", name="北京").check()
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.VEHICLE1").get_by_label("").click()
    page2.get_by_role("option", name="飞机").click()
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.ISSTAY").get_by_label("").click()
    page2.get_by_role("option", name="是").click()
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.STAYDAYS").get_by_role("textbox").click()
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.STAYDAYS").get_by_role("textbox").fill("3")
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.BZ_COMP").get_by_role("textbox").click()
    page2.get_by_role("radio", name="天翼支付科技有限公司（本部）").check()
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.BZ_REIMBU").get_by_role("textbox").click()
    page2.get_by_role("listitem").filter(has_text="天翼支付科技有限公司（本部）").locator("span").click()
    page2.get_by_role("listitem").filter(has_text=re.compile(r"^技术与大数据平台部$")).locator("span").click()
    page2.get_by_text("技术与大数据平台部").nth(1).click()
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.PRODUCTA").get_by_label("").click()
    page2.get_by_role("option", name="全产品线摊销").click()
    page2.get_by_role("row", name="是否为研发事项出差 研发项目名称").get_by_label("").click()
    page2.get_by_role("option", name="是").click()
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.RDPROJECT").get_by_role("textbox").click()
    page2.get_by_text("年中国电信天翼电子商务有限公司线下支付能力研发项目").click()
    page2.wait_for_timeout(5000)
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
'''

    print("="*80)
    print("🔧 简单实用的Playwright转换器")
    print("="*80)
    print()

    # 转换
    converted = convert_from_string(test_script)

    # 保存
    with open('business_trip_simple_converted.py', 'w', encoding='utf-8') as f:
        f.write(converted)

    print("✅ 转换完成！")
    print("📄 输出文件: business_trip_simple_converted.py")
    print()

    # 显示参数
    params = extract_parameterizable_fills(test_script)
    print("📊 提取的参数:")
    for param_name, (value, line_nums) in sorted(params.items()):
        print(f"  - {param_name}: '{value}'")
