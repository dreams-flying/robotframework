"""
通用Playwright变量识别器 - 修复版

修复了generate_operation_code函数的关键问题
"""

import re
import ast
import json
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from pprint import pprint


@dataclass
class Operation:
    """操作数据类"""
    line: int
    operation_type: str
    target_type: str
    target_value: str
    input_value: Optional[str] = None
    modifiers: List[str] = field(default_factory=list)
    chain: List[Dict] = field(default_factory=list)
    page_variable: str = 'page'  # 新增：追踪使用的page变量


@dataclass
class UniversalExtractedData:
    """通用提取数据结构"""
    url: Optional[str] = None
    operations: List[Operation] = field(default_factory=list)
    navigation_sequence: List[str] = field(default_factory=list)
    form_data: Dict[str, Any] = field(default_factory=dict)
    all_texts: Set[str] = field(default_factory=set)
    all_locators: Set[str] = field(default_factory=set)
    wait_operations: List[Dict] = field(default_factory=list)
    popup_operations: List[Dict] = field(default_factory=list)
    page_variables: List[str] = field(default_factory=lambda: ['page'])  # 新增


def identify_operation_type(code_line: str) -> Optional[str]:
    """智能识别操作类型"""
    operation_patterns = {
        'click': r'\.click\(',
        'dblclick': r'\.dblclick\(',
        'fill': r'\.fill\(',
        'type': r'\.type\(',
        'check': r'\.check\(',
        'uncheck': r'\.uncheck\(',
        'select_option': r'(\.select_option\(|get_by_role\("option")',
        'wait_timeout': r'\.wait_for_timeout\(',
        'wait_selector': r'\.wait_for_selector\(',
        'expect_popup': r'expect_popup\(',
        'pause': r'\.pause\(',
        'filter': r'\.filter\(',
        'locator': r'\.locator\(',
    }

    for op_type, pattern in operation_patterns.items():
        if re.search(pattern, code_line):
            return op_type
    return None


def extract_locator_chain(code_line: str) -> List[Dict[str, str]]:
    """
    提取定位器链 - 修复版

    正确识别链式调用的顺序
    """
    chain = []

    # 移除行首的page变量和空白
    line = re.sub(r'^\s*page\d*\.', '', code_line.strip())

    # 按顺序匹配定位器
    # 使用更精确的模式

    # 1. locator
    for match in re.finditer(r'\.locator\(["\']([^"\']+)["\']\)', line):
        chain.append({
            'type': 'locator',
            'value': match.group(1),
            'pos': match.start()
        })

    # 2. get_by_role
    for match in re.finditer(r'\.get_by_role\("([^"]+)"(?:,\s*name=["\']([^"\']+)["\']\))?', line):
        role = match.group(1)
        name = match.group(2) if match.lastindex >= 2 else None
        chain.append({
            'type': 'get_by_role',
            'role': role,
            'name': name if name else '',
            'pos': match.start()
        })

    # 3. get_by_text
    for match in re.finditer(r'\.get_by_text\(["\']([^"\']+)["\']\)', line):
        chain.append({
            'type': 'get_by_text',
            'value': match.group(1),
            'pos': match.start()
        })

    # 4. get_by_label
    for match in re.finditer(r'\.get_by_label\(["\']([^"\']+)["\']\)', line):
        chain.append({
            'type': 'get_by_label',
            'value': match.group(1),
            'pos': match.start()
        })

    # 5. get_by_placeholder
    for match in re.finditer(r'\.get_by_placeholder\(["\']([^"\']+)["\']\)', line):
        chain.append({
            'type': 'get_by_placeholder',
            'value': match.group(1),
            'pos': match.start()
        })

    # 6. get_by_title
    for match in re.finditer(r'\.get_by_title\(["\']([^"\']+)["\']\)', line):
        chain.append({
            'type': 'get_by_title',
            'value': match.group(1),
            'pos': match.start()
        })

    # 7. filter
    for match in re.finditer(r'\.filter\(has_text=["\']([^"\']+)["\']\)', line):
        chain.append({
            'type': 'filter',
            'value': match.group(1),
            'pos': match.start()
        })

    # 8. first, last
    for match in re.finditer(r'\.(first|last)\b', line):
        chain.append({
            'type': match.group(1),
            'value': '',
            'pos': match.start()
        })

    # 9. nth
    for match in re.finditer(r'\.nth\((\d+)\)', line):
        chain.append({
            'type': 'nth',
            'value': match.group(1),
            'pos': match.start()
        })

    # 按位置排序，确保正确的调用顺序
    chain.sort(key=lambda x: x.get('pos', 0))

    # 移除pos字段
    for item in chain:
        if 'pos' in item:
            del item['pos']

    return chain


def extract_page_variable(code_line: str) -> str:
    """提取代码行使用的page变量名"""
    match = re.match(r'^\s*(page\d*|context\d*)\.', code_line)
    if match:
        return match.group(1)
    return 'page'


def universal_identify_variables(script_content: str) -> UniversalExtractedData:
    """通用变量识别函数 - 修复版"""
    data = UniversalExtractedData()
    lines = script_content.split('\n')

    print("🔍 开始通用变量识别...\n")

    # 追踪popup变量映射
    popup_map = {}  # page1_info -> page1

    for line_no, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        # 提取使用的page变量
        page_var = extract_page_variable(line)

        # 识别URL
        if 'page.goto(' in line or 'page1.goto(' in line or 'page2.goto(' in line:
            url_match = re.search(r'\.goto\(["\']([^"\']+)["\']\)', line)
            if url_match:
                data.url = url_match.group(1)
                print(f"✅ [{line_no:3d}] URL: {data.url}")

        # 识别popup操作和变量映射
        if 'expect_popup' in line:
            popup_match = re.search(r'with\s+(\w+)\.expect_popup\(\)\s+as\s+(\w+):', line)
            if popup_match:
                parent_page = popup_match.group(1)
                popup_var = popup_match.group(2)
                data.popup_operations.append({
                    'line': line_no,
                    'variable': popup_var,
                    'parent': parent_page,
                    'code': line
                })
                print(f"✅ [{line_no:3d}] Popup: {popup_var} (from {parent_page})")

        # 识别popup变量赋值: page1 = page1_info.value
        if ' = ' in line and '.value' in line:
            assign_match = re.match(r'^\s*(\w+)\s*=\s*(\w+)\.value', line)
            if assign_match:
                page_name = assign_match.group(1)
                popup_var = assign_match.group(2)
                popup_map[popup_var] = page_name
                if page_name not in data.page_variables:
                    data.page_variables.append(page_name)
                print(f"✅ [{line_no:3d}] Page变量: {page_name} = {popup_var}.value")

        # 识别wait操作
        if 'wait_for_timeout' in line:
            timeout_match = re.search(r'wait_for_timeout\((\d+)\)', line)
            if timeout_match:
                data.wait_operations.append({
                    'line': line_no,
                    'type': 'timeout',
                    'value': timeout_match.group(1)
                })
                print(f"✅ [{line_no:3d}] Wait: {timeout_match.group(1)}ms")

        # 识别操作
        op_type = identify_operation_type(line)
        if op_type and op_type not in ['expect_popup']:  # expect_popup单独处理
            # 提取定位器链
            chain = extract_locator_chain(line)

            # 确定主定位器
            target_type = chain[0]['type'] if chain else 'unknown'
            target_value = ''

            if chain:
                if target_type == 'get_by_role':
                    target_value = f"{chain[0]['role']}"
                    if chain[0].get('name'):
                        target_value += f": {chain[0]['name']}"
                else:
                    target_value = chain[0].get('value', '')

            # 提取输入值
            input_value = None
            if op_type == 'fill':
                fill_match = re.search(r'\.fill\(["\']([^"\']+)["\']\)', line)
                if fill_match:
                    input_value = fill_match.group(1)
            elif op_type == 'select_option' or 'get_by_role("option"' in line:
                option_match = re.search(r'name=["\']([^"\']+)["\']', line)
                if option_match:
                    input_value = option_match.group(1)
            elif op_type == 'check':
                radio_match = re.search(r'name=["\']([^"\']+)["\']', line)
                if radio_match:
                    input_value = radio_match.group(1)

            # 提取修饰符
            modifiers = []
            if '.first' in line:
                modifiers.append('first')
            if '.last' in line:
                modifiers.append('last')
            nth_match = re.search(r'\.nth\((\d+)\)', line)
            if nth_match:
                modifiers.append(f'nth({nth_match.group(1)})')

            # 创建操作对象
            operation = Operation(
                line=line_no,
                operation_type=op_type,
                target_type=target_type,
                target_value=target_value,
                input_value=input_value,
                modifiers=modifiers,
                chain=chain,
                page_variable=page_var  # 记录page变量
            )

            data.operations.append(operation)

            op_desc = f"{op_type}({target_type}: {target_value})"
            if input_value:
                op_desc += f" <- '{input_value}'"
            print(f"✅ [{line_no:3d}] [{page_var}] {op_desc}")

            # 收集文本和定位器
            if input_value:
                data.all_texts.add(input_value)
            if target_value:
                data.all_locators.add(target_value)

    # 构建导航序列
    nav_count = 0
    for op in data.operations:
        if op.operation_type == 'click' and nav_count < 5:
            if op.input_value:
                data.navigation_sequence.append(op.input_value)
            elif op.target_value:
                data.navigation_sequence.append(op.target_value)
            nav_count += 1

    # 构建表单数据
    current_field = None
    for op in data.operations:
        if 'WF_' in op.target_value or 'FIELD' in op.target_value:
            current_field = op.target_value

        if op.input_value and current_field:
            field_key = current_field.split('.')[-1] if '.' in current_field else current_field
            data.form_data[field_key] = {
                'full_name': current_field,
                'value': op.input_value,
                'type': op.operation_type,
                'line': op.line
            }

    print(f"\n✅ 识别完成！共识别 {len(data.operations)} 个操作")
    print(f"✅ Page变量: {', '.join(data.page_variables)}")

    return data


def smart_create_config(data: UniversalExtractedData) -> Dict[str, Any]:
    """智能创建配置"""
    config = {
        'metadata': {
            'url': data.url,
            'total_operations': len(data.operations),
            'navigation_steps': len(data.navigation_sequence),
            'form_fields': len(data.form_data),
            'page_variables': data.page_variables,
        },
        'navigation': {
            'sequence': data.navigation_sequence,
        },
        'form_fields': {},
        'operations_by_type': defaultdict(list),
        'wait_operations': data.wait_operations,
        'popup_operations': data.popup_operations,
    }

    for op in data.operations:
        config['operations_by_type'][op.operation_type].append({
            'line': op.line,
            'page': op.page_variable,
            'target': f"{op.target_type}: {op.target_value}",
            'value': op.input_value,
            'modifiers': op.modifiers
        })

    for field_key, field_info in data.form_data.items():
        config['form_fields'][field_key] = field_info

    config['operations_by_type'] = dict(config['operations_by_type'])

    return config


def generate_operation_code(op: Operation, form_data: Dict) -> str:
    """
    根据Operation对象生成代码行 - 修复版

    关键修复：
    1. 正确的定位器链顺序
    2. 正确的page变量
    3. 正确的参数化
    """
    # 构建定位器链 - 按chain的顺序
    locator_parts = []

    for loc in op.chain:
        if loc['type'] == 'locator':
            locator_parts.append(f".locator('{loc['value']}')")
        elif loc['type'] == 'get_by_text':
            locator_parts.append(f".get_by_text('{loc['value']}')")
        elif loc['type'] == 'get_by_role':
            if loc.get('name'):
                locator_parts.append(f".get_by_role('{loc['role']}', name='{loc['name']}')")
            else:
                locator_parts.append(f".get_by_role('{loc['role']}')")
        elif loc['type'] == 'get_by_label':
            locator_parts.append(f".get_by_label('{loc['value']}')")
        elif loc['type'] == 'get_by_placeholder':
            locator_parts.append(f".get_by_placeholder('{loc['value']}')")
        elif loc['type'] == 'get_by_title':
            locator_parts.append(f".get_by_title('{loc['value']}')")
        elif loc['type'] == 'filter':
            locator_parts.append(f".filter(has_text='{loc['value']}')")
        elif loc['type'] == 'first':
            locator_parts.append('.first')
        elif loc['type'] == 'last':
            locator_parts.append('.last')
        elif loc['type'] == 'nth':
            locator_parts.append(f".nth({loc['value']})")

    # 如果没有定位器链，使用默认
    if not locator_parts and op.target_value:
        if op.target_type == 'get_by_role':
            parts = op.target_value.split(': ', 1)
            if len(parts) == 2:
                locator_parts = [f".get_by_role('{parts[0]}', name='{parts[1]}')"]
            else:
                locator_parts = [f".get_by_role('{op.target_value}')"]
        else:
            locator_parts = [f".{op.target_type}('{op.target_value}')"]

    # 操作
    if op.operation_type == 'click':
        action = '.click()'
    elif op.operation_type == 'fill':
        # 检查是否应该使用参数
        param_name = find_matching_param(op.target_value, form_data)
        if param_name and op.input_value:
            action = f'.fill({param_name})'
        else:
            action = f".fill('{op.input_value}')" if op.input_value else '.fill("")'
    elif op.operation_type == 'check':
        action = '.check()'
    elif op.operation_type == 'select_option':
        param_name = find_matching_param(op.target_value, form_data)
        if param_name:
            action = f'.select_option({param_name})'
        else:
            action = f".select_option('{op.input_value}')" if op.input_value else '.select_option()'
    elif op.operation_type == 'wait_timeout':
        action = f'.wait_for_timeout({op.input_value})'
    else:
        action = f'.{op.operation_type}()'

    # 组合 - 使用正确的page变量
    code = f"{op.page_variable}{''.join(locator_parts)}{action}"

    return code


def find_matching_param(target_value: str, form_data: Dict) -> Optional[str]:
    """查找匹配的参数名"""
    for field_key, field_info in form_data.items():
        if field_info['full_name'] in target_value:
            return field_key.lower()
    return None


def generate_universal_function(
    data: UniversalExtractedData,
    config: Dict[str, Any],
    function_name: str = "execute_automation"
) -> str:
    """
    生成通用参数化函数 - 修复版

    关键修复：
    1. 正确处理popup变量
    2. 正确的操作序列
    3. 正确的代码生成
    """
    # 提取参数
    params = []
    params.append('playwright: Playwright')

    if data.url:
        params.append(f'url: str = "{data.url}"')

    for field_key, field_info in data.form_data.items():
        param_name = field_key.lower().replace('_', '_')
        default_value = field_info['value']
        params.append(f'{param_name}: str = "{default_value}"')

    # 生成函数签名
    func_code = []
    func_code.append(f"def {function_name}(")
    for i, param in enumerate(params):
        if i < len(params) - 1:
            func_code.append(f"    {param},")
        else:
            func_code.append(f"    {param}")
    func_code.append(") -> None:")

    # 文档字符串
    func_code.append('    """')
    func_code.append(f'    自动生成的自动化函数')
    func_code.append('')
    func_code.append('    参数:')
    func_code.append('        playwright: Playwright实例')
    if data.url:
        func_code.append(f'        url: 访问URL')
    for field_key, field_info in data.form_data.items():
        param_name = field_key.lower()
        func_code.append(f'        {param_name}: {field_key}字段的值')
    func_code.append('    """')

    # 函数体
    func_code.append('    browser = playwright.chromium.launch(headless=False)')
    func_code.append('    context = browser.new_context()')
    func_code.append('    page = context.new_page()')
    func_code.append('')

    # 导航
    if data.url:
        func_code.append('    # 导航到页面')
        func_code.append('    page.goto(url)')
        func_code.append('')

    # 处理popup操作 - 在代码前声明
    popup_section_added = False
    if data.popup_operations:
        func_code.append('    # Popup操作')
        for i, popup in enumerate(data.popup_operations):
            parent = popup['parent']
            popup_var = popup['variable']
            # 推断page变量名（通常是去掉_info）
            page_var = popup_var.replace('_info', '')

            func_code.append(f'    with {parent}.expect_popup() as {popup_var}:')
            # 找到触发popup的click操作
            trigger_op = None
            for op in data.operations:
                if op.line == popup['line'] + 1:  # popup下一行通常是触发操作
                    trigger_op = op
                    break

            if trigger_op:
                trigger_code = generate_operation_code(trigger_op, data.form_data)
                func_code.append(f'        {trigger_code}')
            else:
                func_code.append(f'        pass  # TODO: 添加触发popup的操作')

            func_code.append(f'    {page_var} = {popup_var}.value')
            func_code.append('')
        popup_section_added = True

    # 执行操作序列
    func_code.append('    # 执行操作序列')

    # 跳过已经在popup中处理的操作
    popup_trigger_lines = set()
    for popup in data.popup_operations:
        popup_trigger_lines.add(popup['line'] + 1)

    current_section = None
    for op in sorted(data.operations, key=lambda x: x.line):
        # 跳过popup触发操作（已在popup块中处理）
        if op.line in popup_trigger_lines:
            continue

        # 添加分段注释
        if op.operation_type != current_section:
            func_code.append(f'    # {op.operation_type.upper()} 操作')
            current_section = op.operation_type

        # 生成操作代码
        code_line = generate_operation_code(op, data.form_data)
        func_code.append(f'    {code_line}')

    # wait操作
    for wait_op in data.wait_operations:
        func_code.append(f"    page.wait_for_timeout({wait_op['value']})")

    # 关闭
    func_code.append('')
    func_code.append('    # 清理')
    func_code.append('    context.close()')
    func_code.append('    browser.close()')

    return '\n'.join(func_code)


def analyze_and_generate(script_content: str, output_prefix: str = "automation"):
    """主函数：分析脚本并生成所有输出"""
    print("="*80)
    print("🚀 通用Playwright脚本分析器 - 修复版")
    print("="*80)
    print()

    # 1. 识别变量
    print("步骤1: 识别变量...")
    print("-"*80)
    data = universal_identify_variables(script_content)

    # 2. 创建配置
    print("\n" + "="*80)
    print("步骤2: 创建配置...")
    print("="*80)
    config = smart_create_config(data)

    print(f"\n📊 配置摘要:")
    print(f"  - URL: {config['metadata']['url']}")
    print(f"  - 总操作数: {config['metadata']['total_operations']}")
    print(f"  - 导航步骤: {config['metadata']['navigation_steps']}")
    print(f"  - 表单字段: {config['metadata']['form_fields']}")
    print(f"  - Page变量: {', '.join(config['metadata']['page_variables'])}")

    # 3. 生成函数
    print("\n" + "="*80)
    print("步骤3: 生成参数化函数...")
    print("="*80)
    func_code = generate_universal_function(data, config)

    # 4. 保存结果
    print("\n" + "="*80)
    print("步骤4: 保存结果...")
    print("="*80)

    # 保存配置
    config_file = f'{output_prefix}_config_fixed.json'
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"✅ 配置文件: {config_file}")

    # 保存函数
    func_file = f'{output_prefix}_function_fixed.py'
    with open(func_file, 'w', encoding='utf-8') as f:
        f.write('from playwright.sync_api import Playwright, sync_playwright\n\n')
        f.write(func_code)
        f.write('\n\n')
        f.write('# 使用示例:\n')
        f.write('# with sync_playwright() as playwright:\n')
        f.write('#     execute_automation(playwright)\n')
    print(f"✅ 函数文件: {func_file}")

    # 保存完整数据
    data_file = f'{output_prefix}_data_fixed.json'
    data_dict = {
        'url': data.url,
        'page_variables': data.page_variables,
        'operations': [
            {
                'line': op.line,
                'page': op.page_variable,
                'type': op.operation_type,
                'target_type': op.target_type,
                'target_value': op.target_value,
                'input_value': op.input_value,
                'modifiers': op.modifiers,
                'chain': op.chain
            }
            for op in data.operations
        ],
        'navigation_sequence': data.navigation_sequence,
        'form_data': data.form_data,
        'wait_operations': data.wait_operations,
        'popup_operations': data.popup_operations
    }
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=2)
    print(f"✅ 数据文件: {data_file}")

    print("\n" + "="*80)
    print("✨ 完成！")
    print("="*80)

    return data, config, func_code


# ==================== 测试 ====================

if __name__ == "__main__":
    # 出差申请脚本
    business_trip_script = '''
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
'''

    # 分析并生成
    analyze_and_generate(business_trip_script, output_prefix="business_trip")
