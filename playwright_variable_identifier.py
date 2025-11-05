"""
Playwright变量识别和提取函数

这个脚本展示了如何从Playwright Codegen生成的代码中
识别和定义各种类型的变量。
"""

import re
import ast
from typing import Dict, List, Set, Any
from collections import defaultdict
from pprint import pprint


def identify_and_extract_variables(script_content: str) -> Dict[str, Any]:
    """
    识别并提取Playwright脚本中的所有变量

    参数:
        script_content: Playwright脚本内容（字符串）

    返回:
        包含所有识别的变量的字典，按类型分类
    """

    variables = {
        'url': None,                          # 主URL
        'navigation_texts': [],               # 导航文本（点击的文本）
        'form_fields': {},                    # 表单字段名 -> 值
        'dropdown_options': {},               # 下拉选择 -> 选项值
        'date_selections': [],                # 日期选择
        'time_selections': [],                # 时间选择
        'text_inputs': {},                    # 文本输入框 -> 输入值
        'locator_ids': [],                    # CSS选择器/ID
        'placeholders': set(),                # placeholder文本
        'roles': [],                          # role定位器
        'all_string_constants': set(),        # 所有字符串常量
    }

    # ==================== 方法1: 使用正则表达式识别 ====================

    # 1. 识别URL (goto方法)
    url_pattern = r'page\.goto\(["\']([^"\']+)["\']\)'
    url_match = re.search(url_pattern, script_content)
    if url_match:
        variables['url'] = url_match.group(1)
        print(f"✅ 识别URL: {url_match.group(1)}")

    # 2. 识别导航文本 (get_by_text, click等)
    text_patterns = [
        r'get_by_text\(["\']([^"\']+)["\']\)',
        r'get_by_role\([^,]+,\s*name=["\']([^"\']+)["\']\)',
        r'get_by_link\([^,]+,\s*name=["\']([^"\']+)["\']\)',
    ]
    for pattern in text_patterns:
        matches = re.findall(pattern, script_content)
        for match in matches:
            variables['navigation_texts'].append(match)
            print(f"✅ 识别导航文本: {match}")

    # 3. 识别下拉选项 (get_by_role("option", name="xxx"))
    option_pattern = r'get_by_role\("option",\s*name=["\']([^"\']+)["\']\)'
    option_matches = re.findall(option_pattern, script_content)
    for i, option in enumerate(option_matches):
        # 尝试找到对应的字段名（前一个get_by_role("cell")）
        variables['dropdown_options'][f'选项{i+1}'] = option
        print(f"✅ 识别下拉选项: {option}")

    # 4. 识别表单字段名 (get_by_role("cell", name="WF_XXX"))
    field_pattern = r'get_by_role\("cell",\s*name=["\']([^"\']+)["\']\)'
    field_matches = re.findall(field_pattern, script_content)
    for field in field_matches:
        if field not in variables['form_fields']:
            variables['form_fields'][field] = None  # 值会在后面填充
            print(f"✅ 识别表单字段: {field}")

    # 5. 识别文本输入值 (fill方法)
    fill_pattern = r'\.fill\(["\']([^"\']+)["\']\)'
    fill_matches = re.findall(fill_pattern, script_content)
    for i, value in enumerate(fill_matches):
        variables['text_inputs'][f'输入值{i+1}'] = value
        print(f"✅ 识别文本输入: {value}")

    # 6. 识别日期选择 (get_by_role("cell", name="5", exact=True))
    date_pattern = r'get_by_role\("cell",\s*name=["\'](\d+)["\']\s*,\s*exact=True\)'
    date_matches = re.findall(date_pattern, script_content)
    for date in date_matches:
        variables['date_selections'].append(date)
        print(f"✅ 识别日期选择: {date}")

    # 7. 识别时间选择 (从option中提取时间格式)
    time_pattern = r'get_by_role\("option",\s*name=["\'](\d{1,2}:\d{0,2})["\']\)'
    time_matches = re.findall(time_pattern, script_content)
    for time_val in time_matches:
        variables['time_selections'].append(time_val)
        print(f"✅ 识别时间选择: {time_val}")

    # 8. 识别CSS选择器/ID (locator("#xxx"))
    locator_pattern = r'\.locator\(["\']([^"\']+)["\']\)'
    locator_matches = re.findall(locator_pattern, script_content)
    for locator in locator_matches:
        variables['locator_ids'].append(locator)
        print(f"✅ 识别定位器: {locator}")

    # 9. 识别placeholder
    placeholder_pattern = r'get_by_placeholder\(["\']([^"\']+)["\']\)'
    placeholder_matches = re.findall(placeholder_pattern, script_content)
    for placeholder in placeholder_matches:
        variables['placeholders'].add(placeholder)
        print(f"✅ 识别placeholder: {placeholder}")

    # 10. 识别所有字符串常量（作为备份）
    all_strings = re.findall(r'["\']([^"\']+)["\']', script_content)
    variables['all_string_constants'] = set(all_strings)

    # ==================== 方法2: 使用AST深度分析 ====================

    print("\n" + "="*60)
    print("使用AST进行深度分析...")
    print("="*60)

    try:
        tree = ast.parse(script_content)
        ast_variables = analyze_with_ast(tree)

        # 合并AST分析结果
        if ast_variables:
            print("\n✅ AST分析补充了以下变量:")
            for key, value in ast_variables.items():
                if value and key not in ['all_string_constants']:
                    print(f"  - {key}: {len(value) if isinstance(value, (list, set, dict)) else value}")

    except SyntaxError as e:
        print(f"⚠️  AST解析失败: {e}")

    # 清理和去重
    variables['navigation_texts'] = list(dict.fromkeys(variables['navigation_texts']))  # 保持顺序去重
    variables['placeholders'] = list(variables['placeholders'])

    return variables


def analyze_with_ast(tree: ast.AST) -> Dict[str, Any]:
    """
    使用AST深度分析提取变量
    这个方法更准确，能识别变量的上下文关系
    """

    ast_vars = {
        'operations': [],  # 操作序列
        'field_value_pairs': {},  # 字段-值对应关系
    }

    class VariableVisitor(ast.NodeVisitor):
        def __init__(self):
            self.current_line = 0
            self.operations = []
            self.last_field = None  # 追踪最后一个字段，用于关联值

        def visit_Call(self, node: ast.Call):
            """访问函数调用"""
            func_name = self._get_func_name(node.func)

            # 记录操作
            operation = {
                'line': node.lineno if hasattr(node, 'lineno') else 0,
                'function': func_name,
                'args': []
            }

            # 提取参数
            for arg in node.args:
                if isinstance(arg, ast.Constant):
                    operation['args'].append(arg.value)

            # 提取关键字参数
            for kw in node.keywords:
                if isinstance(kw.value, ast.Constant):
                    operation[kw.arg] = kw.value.value

            if func_name:
                self.operations.append(operation)

                # 识别字段
                if func_name == 'get_by_role' and operation.get('name'):
                    field_name = operation.get('name')
                    if 'WF_' in field_name or 'LEAVEINFO' in field_name:
                        self.last_field = field_name

                # 识别字段对应的值
                if func_name in ['fill', 'click'] and self.last_field and operation['args']:
                    ast_vars['field_value_pairs'][self.last_field] = operation['args'][0]

            self.generic_visit(node)

        def _get_func_name(self, node):
            """获取函数名"""
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Attribute):
                return node.attr
            return None

    visitor = VariableVisitor()
    visitor.visit(tree)
    ast_vars['operations'] = visitor.operations

    return ast_vars


def create_variable_config(variables: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据识别的变量创建配置结构
    这是实际使用时推荐的配置格式
    """

    config = {
        # 基本配置
        "url": variables['url'],

        # 导航路径（按顺序）
        "navigation_path": variables['navigation_texts'][:3] if len(variables['navigation_texts']) >= 3 else variables['navigation_texts'],

        # 表单数据
        "form_data": {
            "leave_type": variables['dropdown_options'].get('选项1', '事假'),
            "start_date": variables['date_selections'][0] if variables['date_selections'] else '5',
            "start_time": variables['time_selections'][0] if variables['time_selections'] else '15:30',
            "end_date": variables['date_selections'][1] if len(variables['date_selections']) > 1 else '7',
            "end_time": variables['time_selections'][1] if len(variables['time_selections']) > 1 else '19:00',
            "location": list(variables['text_inputs'].values())[0] if variables['text_inputs'] else '上海',
            "reason": list(variables['text_inputs'].values())[1] if len(variables['text_inputs']) > 1 else '个人事宜',
        },

        # 定位器
        "locators": {
            "oa_system_text": "OA系统",
            "hr_system_id": variables['locator_ids'][0] if variables['locator_ids'] else "#magnet_8490099577463589529",
            "employee_self_service_tab": "员工自助",
            "leave_application_link": "员工请假申请单",
        },

        # 表单字段名称映射
        "field_names": {
            "leave_type": "WF_ATS_LEAVEINFO.LVTYPE",
            "start_date": "WF_ATS_LEAVEINFO.SDATE",
            "start_time": "WF_ATS_LEAVEINFO.STIME",
            "end_date": "WF_ATS_LEAVEINFO.EDATE",
            "end_time": "WF_ATS_LEAVEINFO.ETIME",
            "location": "WF_ATS_LEAVEINFO.PLACE",
        }
    }

    return config


def generate_parameterized_function(config: Dict[str, Any]) -> str:
    """
    生成参数化的Python函数
    """

    func_template = '''
def apply_for_leave(
    playwright: Playwright,
    url: str = "{url}",
    leave_type: str = "{leave_type}",
    start_date: str = "{start_date}",
    start_time: str = "{start_time}",
    end_date: str = "{end_date}",
    end_time: str = "{end_time}",
    location: str = "{location}",
    reason: str = "{reason}"
) -> None:
    """
    参数化的请假申请函数

    参数:
        playwright: Playwright实例
        url: 访问的URL
        leave_type: 请假类型（如：事假、病假）
        start_date: 开始日期（日数字，如：5）
        start_time: 开始时间（如：15:30）
        end_date: 结束日期（日数字，如：7）
        end_time: 结束时间（如：19:00）
        location: 请假地点
        reason: 请假事由
    """
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # 导航到主页
    page.goto(url)

    # 导航到OA系统
    with page.expect_popup() as page1_info:
        page.get_by_text("{nav_1}").first.click()
    page1 = page1_info.value

    # 导航到人力系统
    with page1.expect_popup() as page2_info:
        page1.locator("{hr_system_locator}").get_by_title("人力系统").locator("span").click()
    page2 = page2_info.value

    # 点击员工自助
    page2.get_by_role("tab", name="{nav_2}").click()

    # 点击员工请假申请单
    page2.get_by_role("link", name="{nav_3}").click()

    # 选择请假类型
    page2.get_by_role("cell", name="{field_leave_type}").get_by_label("").click()
    page2.get_by_role("option", name=leave_type).click()

    # 选择开始日期
    page2.get_by_role("cell", name="{field_start_date}").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name=start_date, exact=True).first.click()

    # 选择开始时间
    page2.get_by_role("cell", name="{field_start_time}").get_by_label("").click()
    page2.get_by_role("option", name=start_time).click()

    # 选择结束日期
    page2.get_by_role("cell", name="{field_end_date}").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name=end_date, exact=True).click()

    # 选择结束时间
    page2.get_by_role("cell", name="{field_end_time}").get_by_label("").click()
    page2.get_by_role("option", name=end_time).click()

    # 填写请假地点
    page2.get_by_role("cell", name="{field_location}").get_by_role("textbox").click()
    page2.get_by_role("cell", name="{field_location}").get_by_role("textbox").fill(location)

    # 填写请假事由
    page2.get_by_role("row", name="请假事由").get_by_role("textbox").click()
    page2.get_by_role("row", name="请假事由").get_by_role("textbox").fill(reason)

    # 关闭浏览器
    context.close()
    browser.close()


# 使用示例:
# with sync_playwright() as playwright:
#     apply_for_leave(
#         playwright,
#         leave_type="病假",
#         start_date="10",
#         start_time="09:00",
#         end_date="12",
#         end_time="18:00",
#         location="北京",
#         reason="身体不适"
#     )
'''

    # 填充模板
    return func_template.format(
        url=config['url'],
        leave_type=config['form_data']['leave_type'],
        start_date=config['form_data']['start_date'],
        start_time=config['form_data']['start_time'],
        end_date=config['form_data']['end_date'],
        end_time=config['form_data']['end_time'],
        location=config['form_data']['location'],
        reason=config['form_data']['reason'],
        nav_1=config['navigation_path'][0] if len(config['navigation_path']) > 0 else 'OA系统',
        nav_2=config['navigation_path'][1] if len(config['navigation_path']) > 1 else '员工自助',
        nav_3=config['navigation_path'][2] if len(config['navigation_path']) > 2 else '员工请假申请单',
        hr_system_locator=config['locators']['hr_system_id'],
        field_leave_type=config['field_names']['leave_type'],
        field_start_date=config['field_names']['start_date'],
        field_start_time=config['field_names']['start_time'],
        field_end_date=config['field_names']['end_date'],
        field_end_time=config['field_names']['end_time'],
        field_location=config['field_names']['location'],
    )


# ==================== 主函数 ====================

def main():
    """主函数：演示如何使用"""

    # 示例脚本内容
    script_content = '''
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
    page2.get_by_role("link", name="员工请假申请单").click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.LVTYPE").get_by_label("").click()
    page2.get_by_role("option", name="事假").click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.SDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name="5", exact=True).first.click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.STIME").get_by_label("").click()
    page2.get_by_role("option", name="15:30").click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.EDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name="7", exact=True).click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.ETIME").get_by_label("").click()
    page2.get_by_role("option", name="19:").click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.PLACE").get_by_role("textbox").click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.PLACE").get_by_role("textbox").fill("上海")
    page2.get_by_role("row", name="请假事由").get_by_role("textbox").click()
    page2.get_by_role("row", name="请假事由").get_by_role("textbox").fill("个人事宜")
    context.close()
    browser.close()
'''

    print("="*80)
    print("Playwright变量识别器")
    print("="*80)
    print()

    # 1. 识别和提取变量
    print("步骤1: 识别脚本中的所有变量...")
    print("-"*80)
    variables = identify_and_extract_variables(script_content)

    # 2. 显示识别结果
    print("\n" + "="*80)
    print("步骤2: 识别结果汇总")
    print("="*80)
    print(f"\n📊 识别统计:")
    print(f"  - URL: {1 if variables['url'] else 0}个")
    print(f"  - 导航文本: {len(variables['navigation_texts'])}个")
    print(f"  - 表单字段: {len(variables['form_fields'])}个")
    print(f"  - 下拉选项: {len(variables['dropdown_options'])}个")
    print(f"  - 日期选择: {len(variables['date_selections'])}个")
    print(f"  - 时间选择: {len(variables['time_selections'])}个")
    print(f"  - 文本输入: {len(variables['text_inputs'])}个")
    print(f"  - 定位器ID: {len(variables['locator_ids'])}个")

    print("\n📋 详细变量列表:")
    print("-"*80)
    pprint(variables, width=80)

    # 3. 创建配置
    print("\n" + "="*80)
    print("步骤3: 创建变量配置")
    print("="*80)
    config = create_variable_config(variables)
    pprint(config, width=80)

    # 4. 生成参数化函数
    print("\n" + "="*80)
    print("步骤4: 生成参数化函数")
    print("="*80)
    parameterized_func = generate_parameterized_function(config)
    print(parameterized_func)

    # 5. 保存结果
    print("\n" + "="*80)
    print("步骤5: 保存结果到文件")
    print("="*80)

    # 保存配置
    import json
    with open('leave_application_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print("✅ 配置已保存到: leave_application_config.json")

    # 保存参数化函数
    with open('leave_application_parameterized.py', 'w', encoding='utf-8') as f:
        f.write("from playwright.sync_api import Playwright, sync_playwright\n")
        f.write(parameterized_func)
    print("✅ 参数化函数已保存到: leave_application_parameterized.py")

    print("\n" + "="*80)
    print("✨ 完成！所有变量已识别并配置化。")
    print("="*80)


if __name__ == "__main__":
    main()
