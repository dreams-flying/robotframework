"""
Playwright脚本增强型变量提取器

功能特性：
1. 全面的定位器提取（15+种定位器类型）
2. 完整的交互操作识别（点击、填充、选择、上传等）
3. 断言和等待识别
4. 上下文信息（行号、调用链）
5. 自动生成Robot Framework关键字
6. 自动生成配置文件
7. 可视化分析报告
8. 正则表达式识别
9. 变量赋值追踪
10. 智能参数化建议
"""

import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from pprint import pprint


@dataclass
class LocatorInfo:
    """定位器信息数据类"""
    type: str  # 定位器类型: get_by_text, locator, xpath等
    value: str  # 定位器的值
    line: int  # 代码行号
    context: str  # 上下文（父调用）
    operation: Optional[str] = None  # 后续操作: click, fill等
    operation_value: Optional[str] = None  # 操作的值


@dataclass
class ActionInfo:
    """操作信息数据类"""
    action_type: str  # 操作类型: click, fill, select_option等
    target: str  # 目标元素描述
    value: Optional[str] = None  # 操作值（如填充的文本）
    line: int = 0  # 行号
    locator_type: Optional[str] = None  # 定位器类型
    locator_value: Optional[str] = None  # 定位器值


@dataclass
class ExtractedData:
    """提取的完整数据结构"""
    url: Optional[str] = None
    urls: List[str] = field(default_factory=list)  # 所有访问的URL
    locators: List[LocatorInfo] = field(default_factory=list)
    actions: List[ActionInfo] = field(default_factory=list)
    form_fills: Dict[str, str] = field(default_factory=dict)  # 定位器 -> 填充值
    form_selects: Dict[str, List[str]] = field(default_factory=dict)  # 定位器 -> 选项
    uploaded_files: List[str] = field(default_factory=list)
    clicked_elements: List[str] = field(default_factory=list)
    assertions: List[Dict[str, Any]] = field(default_factory=list)
    waits: List[Dict[str, Any]] = field(default_factory=list)
    keyboard_inputs: List[str] = field(default_factory=list)
    regex_patterns: List[str] = field(default_factory=list)
    variables: Dict[str, str] = field(default_factory=dict)  # 变量名 -> 初始值
    navigation_texts: Set[str] = field(default_factory=set)

    def to_dict(self):
        """转换为字典（处理set类型）"""
        result = asdict(self)
        result['navigation_texts'] = list(self.navigation_texts)
        return result


class EnhancedPlaywrightExtractor(ast.NodeVisitor):
    """增强型Playwright脚本分析器"""

    # 支持的定位器方法
    LOCATOR_METHODS = {
        'get_by_text', 'get_by_role', 'get_by_label', 'get_by_placeholder',
        'get_by_alt_text', 'get_by_title', 'get_by_test_id', 'locator',
        'query_selector', 'query_selector_all', 'xpath', 'get_by_link',
        'frame_locator', 'content_frame', 'nth', 'first', 'last', 'filter'
    }

    # 交互操作方法
    ACTION_METHODS = {
        'click', 'dblclick', 'fill', 'type', 'press', 'select_option',
        'check', 'uncheck', 'set_checked', 'hover', 'drag_to', 'tap',
        'focus', 'blur', 'clear', 'upload_file', 'set_input_files'
    }

    # 等待方法
    WAIT_METHODS = {
        'wait_for_selector', 'wait_for_url', 'wait_for_load_state',
        'wait_for_timeout', 'wait_for_event', 'wait_for_function'
    }

    # 断言方法
    ASSERTION_METHODS = {
        'to_be_visible', 'to_be_hidden', 'to_be_enabled', 'to_be_disabled',
        'to_be_checked', 'to_contain_text', 'to_have_text', 'to_have_value',
        'to_have_url', 'to_have_title', 'to_have_count'
    }

    def __init__(self, script_content: str):
        self.script_content = script_content
        self.script_lines = script_content.splitlines()
        self.data = ExtractedData()
        self.current_locator_chain = []  # 追踪当前的定位器链
        self.variable_assignments = {}  # 变量名 -> AST节点

    def visit_Call(self, node: ast.Call):
        """访问函数调用节点"""
        call_name = self._get_call_name(node.func)
        line_no = node.lineno if hasattr(node, 'lineno') else 0

        # 1. 提取URL（从goto调用）
        if call_name == 'goto':
            url = self._extract_string_arg(node, 0)
            if url:
                if not self.data.url:
                    self.data.url = url
                self.data.urls.append(url)

        # 2. 识别定位器方法
        if call_name in self.LOCATOR_METHODS:
            locator_value = self._extract_locator_value(node)
            if locator_value:
                locator_info = LocatorInfo(
                    type=call_name,
                    value=locator_value,
                    line=line_no,
                    context=self._get_code_context(line_no)
                )
                self.data.locators.append(locator_info)
                self.current_locator_chain.append(locator_info)

                # 如果是导航相关的文本定位器
                if call_name in ('get_by_text', 'get_by_role', 'get_by_label', 'get_by_link'):
                    self.data.navigation_texts.add(locator_value)

        # 3. 识别操作方法
        if call_name in self.ACTION_METHODS:
            action = self._extract_action(node, call_name, line_no)
            if action:
                self.data.actions.append(action)

                # 特殊处理不同操作类型
                if call_name == 'fill' or call_name == 'type':
                    fill_value = self._extract_string_arg(node, 0)
                    if fill_value and self.current_locator_chain:
                        locator_desc = self._describe_locator(self.current_locator_chain[-1])
                        self.data.form_fills[locator_desc] = fill_value

                elif call_name == 'select_option':
                    options = self._extract_select_options(node)
                    if options and self.current_locator_chain:
                        locator_desc = self._describe_locator(self.current_locator_chain[-1])
                        self.data.form_selects[locator_desc] = options

                elif call_name == 'click':
                    if self.current_locator_chain:
                        clicked_desc = self._describe_locator(self.current_locator_chain[-1])
                        self.data.clicked_elements.append(clicked_desc)

                elif call_name in ('upload_file', 'set_input_files'):
                    files = self._extract_file_paths(node)
                    self.data.uploaded_files.extend(files)

                elif call_name == 'press':
                    key = self._extract_string_arg(node, 0)
                    if key:
                        self.data.keyboard_inputs.append(key)

        # 4. 识别等待方法
        if call_name in self.WAIT_METHODS:
            wait_info = self._extract_wait_info(node, call_name, line_no)
            if wait_info:
                self.data.waits.append(wait_info)

        # 5. 识别断言方法（expect）
        if call_name == 'expect':
            assertion = self._extract_assertion(node, line_no)
            if assertion:
                self.data.assertions.append(assertion)

        if call_name in self.ASSERTION_METHODS:
            # 这是expect().to_xxx()链式调用的一部分
            assertion = {
                'type': call_name,
                'line': line_no,
                'args': [self._extract_string_arg(node, i) for i in range(len(node.args))]
            }
            self.data.assertions.append(assertion)

        # 6. 识别正则表达式
        if call_name == 'compile' and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == 're':
                pattern = self._extract_string_arg(node, 0)
                if pattern:
                    self.data.regex_patterns.append(pattern)

        self.generic_visit(node)

        # 清理定位器链（避免过度积累）
        if call_name in self.ACTION_METHODS:
            self.current_locator_chain.clear()

    def visit_Assign(self, node: ast.Assign):
        """访问赋值语句"""
        if node.targets:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                var_name = target.id
                # 记录变量赋值
                if isinstance(node.value, ast.Constant):
                    self.data.variables[var_name] = str(node.value.value)
                elif isinstance(node.value, ast.Call):
                    call_name = self._get_call_name(node.value.func)
                    self.data.variables[var_name] = f"<{call_name}()>"
                self.variable_assignments[var_name] = node.value

        self.generic_visit(node)

    def _get_call_name(self, func_node) -> Optional[str]:
        """从函数节点获取函数名"""
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            return func_node.attr
        return None

    def _extract_string_arg(self, node: ast.Call, index: int) -> Optional[str]:
        """提取指定位置的字符串参数"""
        if len(node.args) > index and isinstance(node.args[index], ast.Constant):
            value = node.args[index].value
            if isinstance(value, str):
                return value
        return None

    def _extract_keyword_arg(self, node: ast.Call, key: str) -> Optional[str]:
        """提取指定关键字参数"""
        for kw in node.keywords:
            if kw.arg == key and isinstance(kw.value, ast.Constant):
                if isinstance(kw.value.value, str):
                    return kw.value.value
        return None

    def _extract_locator_value(self, node: ast.Call) -> Optional[str]:
        """提取定位器的值"""
        # 尝试位置参数
        value = self._extract_string_arg(node, 0)
        if value:
            return value

        # 尝试关键字参数（如 name="xxx", role="xxx"）
        for key in ['name', 'role', 'text', 'selector']:
            value = self._extract_keyword_arg(node, key)
            if value:
                return value

        return None

    def _extract_action(self, node: ast.Call, action_type: str, line: int) -> Optional[ActionInfo]:
        """提取操作信息"""
        action_value = self._extract_string_arg(node, 0) or self._extract_keyword_arg(node, 'value')

        target_desc = "unknown"
        locator_type = None
        locator_value = None

        if self.current_locator_chain:
            last_locator = self.current_locator_chain[-1]
            target_desc = self._describe_locator(last_locator)
            locator_type = last_locator.type
            locator_value = last_locator.value

        return ActionInfo(
            action_type=action_type,
            target=target_desc,
            value=action_value,
            line=line,
            locator_type=locator_type,
            locator_value=locator_value
        )

    def _extract_select_options(self, node: ast.Call) -> List[str]:
        """提取select_option的选项值"""
        options = []

        # 尝试提取value, label, index等参数
        for key in ['value', 'label', 'index']:
            opt = self._extract_keyword_arg(node, key)
            if opt:
                options.append(opt)

        # 尝试位置参数
        if node.args:
            arg = node.args[0]
            if isinstance(arg, ast.Constant):
                options.append(str(arg.value))
            elif isinstance(arg, (ast.List, ast.Tuple)):
                for elt in arg.elts:
                    if isinstance(elt, ast.Constant):
                        options.append(str(elt.value))

        return options

    def _extract_file_paths(self, node: ast.Call) -> List[str]:
        """提取文件路径"""
        files = []
        if node.args:
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                files.append(arg.value)
            elif isinstance(arg, (ast.List, ast.Tuple)):
                for elt in arg.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        files.append(elt.value)
        return files

    def _extract_wait_info(self, node: ast.Call, wait_type: str, line: int) -> Dict[str, Any]:
        """提取等待信息"""
        info = {
            'type': wait_type,
            'line': line
        }

        if wait_type == 'wait_for_selector':
            info['selector'] = self._extract_string_arg(node, 0)
        elif wait_type == 'wait_for_url':
            info['url'] = self._extract_string_arg(node, 0)
        elif wait_type == 'wait_for_timeout':
            if node.args and isinstance(node.args[0], ast.Constant):
                info['timeout'] = node.args[0].value
        elif wait_type == 'wait_for_load_state':
            info['state'] = self._extract_string_arg(node, 0) or 'load'

        return info

    def _extract_assertion(self, node: ast.Call, line: int) -> Optional[Dict[str, Any]]:
        """提取断言信息"""
        if node.args:
            target = node.args[0]
            return {
                'type': 'expect',
                'line': line,
                'target': ast.unparse(target) if hasattr(ast, 'unparse') else '<expression>'
            }
        return None

    def _describe_locator(self, locator: LocatorInfo) -> str:
        """生成定位器的可读描述"""
        return f"{locator.type}('{locator.value}')"

    def _get_code_context(self, line: int, context_lines: int = 1) -> str:
        """获取代码上下文"""
        if 0 < line <= len(self.script_lines):
            start = max(0, line - context_lines - 1)
            end = min(len(self.script_lines), line + context_lines)
            return '\n'.join(self.script_lines[start:end])
        return ""


class PlaywrightAnalyzer:
    """Playwright脚本分析器主类"""

    def __init__(self, script_path: str):
        self.script_path = Path(script_path)
        self.script_content = ""
        self.data: Optional[ExtractedData] = None

    def analyze(self) -> ExtractedData:
        """执行分析"""
        print(f"📊 正在分析脚本: {self.script_path}")

        # 读取文件
        with open(self.script_path, 'r', encoding='utf-8') as f:
            self.script_content = f.read()

        # 解析AST
        try:
            tree = ast.parse(self.script_content)
        except SyntaxError as e:
            print(f"❌ 语法错误: {e}")
            return ExtractedData()

        # 提取数据
        extractor = EnhancedPlaywrightExtractor(self.script_content)
        extractor.visit(tree)
        self.data = extractor.data

        print(f"✅ 分析完成！")
        return self.data

    def generate_summary_report(self) -> str:
        """生成摘要报告"""
        if not self.data:
            return "❌ 尚未执行分析"

        report = []
        report.append("=" * 80)
        report.append("📋 Playwright脚本分析报告")
        report.append("=" * 80)

        # 基本信息
        report.append(f"\n📄 脚本文件: {self.script_path}")
        if self.data.url:
            report.append(f"🌐 主URL: {self.data.url}")

        # 统计信息
        report.append(f"\n📊 统计信息:")
        report.append(f"  - 总URL数: {len(self.data.urls)}")
        report.append(f"  - 定位器数: {len(self.data.locators)}")
        report.append(f"  - 操作数: {len(self.data.actions)}")
        report.append(f"  - 表单填充: {len(self.data.form_fills)}")
        report.append(f"  - 下拉选择: {len(self.data.form_selects)}")
        report.append(f"  - 点击元素: {len(self.data.clicked_elements)}")
        report.append(f"  - 文件上传: {len(self.data.uploaded_files)}")
        report.append(f"  - 键盘输入: {len(self.data.keyboard_inputs)}")
        report.append(f"  - 等待操作: {len(self.data.waits)}")
        report.append(f"  - 断言: {len(self.data.assertions)}")
        report.append(f"  - 正则模式: {len(self.data.regex_patterns)}")

        # 操作流程
        if self.data.actions:
            report.append(f"\n🔄 操作流程 (共{len(self.data.actions)}步):")
            for i, action in enumerate(self.data.actions[:20], 1):  # 最多显示20步
                value_str = f" <- '{action.value}'" if action.value else ""
                report.append(f"  {i}. [{action.line:4d}行] {action.action_type}({action.target}){value_str}")
            if len(self.data.actions) > 20:
                report.append(f"  ... 还有 {len(self.data.actions) - 20} 步")

        # 导航文本
        if self.data.navigation_texts:
            report.append(f"\n🧭 导航关键文本 (共{len(self.data.navigation_texts)}个):")
            for text in list(self.data.navigation_texts)[:10]:
                report.append(f"  - {text}")
            if len(self.data.navigation_texts) > 10:
                report.append(f"  ... 还有 {len(self.data.navigation_texts) - 10} 个")

        # 表单数据
        if self.data.form_fills:
            report.append(f"\n📝 表单填充数据:")
            for locator, value in list(self.data.form_fills.items())[:10]:
                report.append(f"  - {locator} = '{value}'")

        # 定位器类型统计
        locator_type_counts = defaultdict(int)
        for loc in self.data.locators:
            locator_type_counts[loc.type] += 1

        if locator_type_counts:
            report.append(f"\n🎯 定位器类型分布:")
            for loc_type, count in sorted(locator_type_counts.items(), key=lambda x: x[1], reverse=True):
                report.append(f"  - {loc_type}: {count}次")

        # 参数化建议
        suggestions = self._generate_parameterization_suggestions()
        if suggestions:
            report.append(f"\n💡 参数化建议:")
            for suggestion in suggestions[:5]:
                report.append(f"  - {suggestion}")

        report.append("\n" + "=" * 80)
        return '\n'.join(report)

    def _generate_parameterization_suggestions(self) -> List[str]:
        """生成参数化建议"""
        suggestions = []

        # 检查重复的填充值
        fill_values = list(self.data.form_fills.values())
        if len(fill_values) > 1 and len(set(fill_values)) < len(fill_values):
            suggestions.append("发现重复的表单填充值，建议提取为配置参数")

        # 检查硬编码的URL
        if len(self.data.urls) > 1:
            suggestions.append(f"发现{len(self.data.urls)}个URL，建议使用环境变量配置")

        # 检查文件上传路径
        if self.data.uploaded_files:
            suggestions.append("发现文件上传操作，建议将文件路径参数化")

        # 检查导航文本
        if len(self.data.navigation_texts) > 5:
            suggestions.append("发现多个导航文本，建议创建导航配置字典")

        # 检查正则表达式
        if self.data.regex_patterns:
            suggestions.append("发现正则表达式，建议提取到配置文件中便于维护")

        return suggestions

    def generate_robot_keywords(self) -> str:
        """生成Robot Framework关键字"""
        if not self.data:
            return ""

        keywords = []
        keywords.append("*** Settings ***")
        keywords.append("Library    Browser")
        keywords.append("")
        keywords.append("*** Keywords ***")
        keywords.append("")

        # 生成导航关键字
        if self.data.url:
            keywords.append("打开测试页面")
            keywords.append(f"    [Arguments]    ${{url}}={self.data.url}")
            keywords.append("    New Browser    chromium    headless=False")
            keywords.append("    New Context")
            keywords.append("    New Page    ${url}")
            keywords.append("")

        # 为每个表单填充生成关键字
        for i, (locator, value) in enumerate(self.data.form_fills.items(), 1):
            kw_name = f"填充字段{i}"
            keywords.append(kw_name)
            keywords.append(f"    [Arguments]    ${{value}}={value}")

            # 解析定位器
            if 'get_by_placeholder' in locator:
                match = re.search(r"'([^']+)'", locator)
                if match:
                    keywords.append(f"    Fill Text    placeholder='{match.group(1)}'    ${{value}}")
            elif 'get_by_label' in locator:
                match = re.search(r"'([^']+)'", locator)
                if match:
                    keywords.append(f"    Fill Text    label='{match.group(1)}'    ${{value}}")
            else:
                keywords.append(f"    # TODO: 完善定位器 - {locator}")
                keywords.append(f"    Fill Text    <locator>    ${{value}}")
            keywords.append("")

        # 为每个点击生成关键字
        clicked_unique = list(dict.fromkeys(self.data.clicked_elements))  # 去重保持顺序
        for i, element in enumerate(clicked_unique, 1):
            kw_name = f"点击_{self._sanitize_keyword_name(element)}"[:50]  # 限制长度
            keywords.append(kw_name)

            if 'get_by_text' in element:
                match = re.search(r"'([^']+)'", element)
                if match:
                    keywords.append(f"    Click    text='{match.group(1)}'")
            elif 'get_by_role' in element:
                match = re.search(r"'([^']+)'", element)
                if match:
                    keywords.append(f"    Click    role={match.group(1)}")
            else:
                keywords.append(f"    # TODO: 完善定位器 - {element}")
                keywords.append(f"    Click    <locator>")
            keywords.append("")

        # 生成主测试流程
        keywords.append("执行完整测试流程")
        if self.data.url:
            keywords.append(f"    打开测试页面    {self.data.url}")

        # 按行号排序操作，生成调用序列
        sorted_actions = sorted(self.data.actions, key=lambda x: x.line)
        for action in sorted_actions[:20]:  # 限制数量
            if action.action_type == 'fill':
                kw_name = f"填充字段"
                if action.value:
                    keywords.append(f"    # {kw_name}    {action.value}")
            elif action.action_type == 'click':
                keywords.append(f"    # 点击_{self._sanitize_keyword_name(action.target)}"[:60])

        keywords.append("")
        return '\n'.join(keywords)

    def _sanitize_keyword_name(self, name: str) -> str:
        """清理关键字名称"""
        # 移除特殊字符，保留中文、字母、数字
        name = re.sub(r"[^\w\u4e00-\u9fff]", "_", name)
        return name.strip("_")

    def generate_config_dict(self) -> Dict[str, Any]:
        """生成配置字典"""
        if not self.data:
            return {}

        config = {
            "url": self.data.url or "",
            "urls": self.data.urls,
            "navigation": {
                text: {"type": "text", "value": text}
                for text in self.data.navigation_texts
            },
            "form_data": {
                "fills": self.data.form_fills,
                "selects": self.data.form_selects
            },
            "files": self.data.uploaded_files,
            "keyboard_inputs": self.data.keyboard_inputs,
            "regex_patterns": self.data.regex_patterns,
            "variables": self.data.variables,
            "statistics": {
                "total_locators": len(self.data.locators),
                "total_actions": len(self.data.actions),
                "total_waits": len(self.data.waits),
                "total_assertions": len(self.data.assertions)
            }
        }

        return config

    def save_analysis_results(self, output_dir: str = "."):
        """保存分析结果到多个文件"""
        output_path = Path(output_dir)
        base_name = self.script_path.stem

        print(f"\n💾 保存分析结果到: {output_path}")

        # 1. 保存摘要报告
        report_file = output_path / f"{base_name}_analysis_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_summary_report())
        print(f"  ✅ 摘要报告: {report_file}")

        # 2. 保存Robot Framework关键字
        robot_file = output_path / f"{base_name}_keywords.robot"
        with open(robot_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_robot_keywords())
        print(f"  ✅ Robot关键字: {robot_file}")

        # 3. 保存配置JSON
        config_file = output_path / f"{base_name}_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.generate_config_dict(), f, ensure_ascii=False, indent=2)
        print(f"  ✅ 配置文件: {config_file}")

        # 4. 保存完整数据JSON
        data_file = output_path / f"{base_name}_full_data.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data.to_dict(), f, ensure_ascii=False, indent=2, default=str)
        print(f"  ✅ 完整数据: {data_file}")

        # 5. 生成参数化测试用例模板
        test_file = output_path / f"{base_name}_test_template.robot"
        self._save_test_template(test_file)
        print(f"  ✅ 测试模板: {test_file}")

    def _save_test_template(self, file_path: Path):
        """生成参数化测试用例模板"""
        template = []
        template.append("*** Settings ***")
        template.append("Library    Browser")
        template.append(f"Resource    {self.script_path.stem}_keywords.robot")
        template.append("Suite Setup    打开测试页面")
        template.append("")
        template.append("*** Variables ***")
        if self.data.url:
            template.append(f"${{BASE_URL}}    {self.data.url}")

        # 添加表单数据变量
        for i, (locator, value) in enumerate(self.data.form_fills.items(), 1):
            var_name = f"FIELD{i}_VALUE"
            template.append(f"${{{var_name}}}    {value}")

        template.append("")
        template.append("*** Test Cases ***")
        template.append("测试基本流程")
        template.append("    [Documentation]    基于Playwright Codegen生成的测试流程")
        template.append("    [Tags]    smoke    auto-generated")
        template.append("    执行完整测试流程")
        template.append("    # TODO: 添加断言验证结果")
        template.append("")

        # 数据驱动测试示例
        if len(self.data.form_fills) > 0:
            template.append("数据驱动测试")
            template.append("    [Documentation]    参数化测试示例")
            template.append("    [Template]    执行完整测试流程")
            template.append("    # TODO: 添加测试数据")
            template.append("    # 数据1")
            template.append("    # 数据2")

        template.append("")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(template))


def analyze_playwright_script(script_path: str, output_dir: str = ".") -> ExtractedData:
    """
    主入口函数：分析Playwright脚本并生成所有输出

    Args:
        script_path: Playwright脚本文件路径
        output_dir: 输出目录路径

    Returns:
        ExtractedData: 提取的完整数据
    """
    analyzer = PlaywrightAnalyzer(script_path)
    data = analyzer.analyze()

    # 显示摘要报告
    print(analyzer.generate_summary_report())

    # 保存所有分析结果
    analyzer.save_analysis_results(output_dir)

    return data


# ================================================================
# 使用示例
# ================================================================
if __name__ == '__main__':
    import sys

    # 命令行参数支持
    if len(sys.argv) > 1:
        script_file = sys.argv[1]
        output_directory = sys.argv[2] if len(sys.argv) > 2 else "."
    else:
        # 默认示例文件
        script_file = 'codegen_script.py'
        output_directory = './analysis_output'

    # 确保输出目录存在
    Path(output_directory).mkdir(parents=True, exist_ok=True)

    print("🚀 Playwright脚本增强型分析器")
    print("=" * 80)

    try:
        # 执行分析
        extracted_data = analyze_playwright_script(script_file, output_directory)

        print("\n" + "=" * 80)
        print("✨ 分析完成！查看生成的文件了解详细信息。")
        print("=" * 80)

    except FileNotFoundError:
        print(f"❌ 错误: 找不到文件 '{script_file}'")
        print(f"💡 用法: python {sys.argv[0]} <playwright_script.py> [output_dir]")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
