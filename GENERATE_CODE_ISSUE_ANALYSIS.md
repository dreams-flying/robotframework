# generate_operation_code 函数问题分析和修复

## 🐛 问题总结

### 原始代码示例
```python
page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.APPCAUSE").get_by_role("textbox").fill("参加学术会议")
page2.get_by_role("list").filter(has_text="上海上海").locator("span").click()
page2.get_by_role("tab", name="员工自助").click()
```

### 生成的错误代码
```python
# ❌ 问题1：定位器链不完整
page2.get_by_role('textbox').fill('参加学术会议')  # 丢失了前面的cell定位

# ❌ 问题2：定位器顺序错误或缺失
page2.filter(has_text='上海上海').locator('span').click()  # 丢失了get_by_role('list')

# ❌ 问题3：简单操作也可能出错
page2.click()  # 丢失了整个定位器
```

---

## 🔍 根本原因

### 问题1：定位器链提取逻辑

**错误的提取方法**：使用正则表达式逐个匹配，导致：
1. 嵌套的`get_by_role`调用被覆盖
2. 链式调用的顺序混乱
3. 某些定位器被遗漏

**示例**：
```python
# 原始代码
page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.APPCAUSE").get_by_role("textbox").fill("参加学术会议")

# extract_locator_chain 提取结果
[
    {'type': 'get_by_role', 'role': 'textbox', 'name': ''}  # ❌ 只保留了最后一个
]

# 应该提取的结果
[
    {'type': 'get_by_role', 'role': 'cell', 'name': 'WF_ATS_LEAVEINFO.APPCAUSE'},
    {'type': 'get_by_role', 'role': 'textbox', 'name': ''}
]
```

### 问题2：generate_operation_code 生成逻辑

**当定位器链不完整时**：
```python
# chain = [] 或 chain 只有部分信息
# 导致生成：
page2.click()  # 完全没有定位器
```

---

## ✅ 解决方案

有两种彻底的解决方案：

### 方案1：完全重写定位器提取（复杂但彻底）

```python
def extract_complete_locator_chain(code_line: str) -> str:
    """
    提取完整的定位器链 - 保留原始代码

    策略：不试图解析，直接提取从第一个定位器到最后一个操作之前的所有内容
    """
    # 移除变量和末尾的操作
    line = code_line.strip()

    # 移除page变量
    line = re.sub(r'^\s*page\d*\.', '', line)

    # 移除末尾的操作（click, fill, check等）
    line = re.sub(r'\.(click|fill|check|select_option|type|press)\([^)]*\)$', '', line)

    return line


def generate_operation_code_v2(op: Operation, original_line: str) -> str:
    """
    生成代码 - 使用原始代码

    策略：
    1. 从原始代码提取定位器链
    2. 替换末尾的操作和参数
    3. 替换page变量
    """
    # 提取原始定位器链
    locator_chain = extract_complete_locator_chain(original_line)

    # 根据操作类型生成末尾
    if op.operation_type == 'fill':
        param = find_matching_param(op.target_value, form_data)
        if param:
            action = f'.fill({param})'
        else:
            action = f".fill('{op.input_value}')"
    elif op.operation_type == 'click':
        action = '.click()'
    elif op.operation_type == 'check':
        action = '.check()'
    # ... 其他操作

    # 组合
    return f"{op.page_variable}.{locator_chain}{action}"
```

**优点**：
- ✅ 保留完整的定位器信息
- ✅ 不需要复杂的解析逻辑
- ✅ 准确性高

**缺点**：
- ⚠️ 需要保存原始代码行
- ⚠️ 难以做参数化替换

---

### 方案2：简化方案 - 直接复制原始代码（最简单）

```python
def generate_function_with_original_code(data: UniversalExtractedData, script_lines: List[str]) -> str:
    """
    使用原始代码生成函数

    策略：
    1. 保留原始操作代码
    2. 只替换参数化的值
    3. 添加popup和page变量处理
    """
    func_code = []

    # 函数签名
    func_code.append("def execute_automation(playwright: Playwright, ...):")
    func_code.append("    browser = playwright.chromium.launch(headless=False)")
    func_code.append("    context = browser.new_context()")
    func_code.append("    page = context.new_page()")
    func_code.append("")
    func_code.append("    page.goto(url)")
    func_code.append("")

    # popup处理
    for popup in data.popup_operations:
        func_code.append(f"    # Popup: {popup['code']}")
        func_code.append(f"    # (保留原始代码)")

    # 主操作序列 - 使用原始代码
    for op in data.operations:
        original_line = script_lines[op.line - 1].strip()

        # 简单参数化：替换hard-coded的值
        line = original_line
        if op.input_value and op.operation_type == 'fill':
            param = find_matching_param(op.target_value, form_data)
            if param:
                line = line.replace(f"'{op.input_value}'", param)
                line = line.replace(f'"{op.input_value}"', param)

        func_code.append(f"    {line}")

    return '\n'.join(func_code)
```

**优点**：
- ✅ 最简单
- ✅ 100%准确（保留原始代码）
- ✅ 容易实现

**缺点**：
- ⚠️ 参数化能力有限

---

## 💡 推荐方案：混合方案

结合两种方案的优点：

```python
class EnhancedOperation:
    """增强的操作对象 - 保存原始代码"""
    line: int
    original_code: str  # ✅ 新增：保存原始代码
    operation_type: str
    page_variable: str
    input_value: Optional[str]
    is_parameterizable: bool  # ✅ 是否可参数化


def universal_identify_variables_v2(script_content: str) -> UniversalExtractedData:
    """识别变量 - 保存原始代码"""
    lines = script_content.split('\n')

    for line_no, line in enumerate(lines, 1):
        op = EnhancedOperation(
            line=line_no,
            original_code=line.strip(),  # ✅ 保存原始代码
            operation_type=identify_operation_type(line),
            page_variable=extract_page_variable(line),
            input_value=extract_input_value(line),
            is_parameterizable=can_parameterize(line)
        )
        data.operations.append(op)


def generate_operation_code_v3(op: EnhancedOperation, form_data: Dict) -> str:
    """
    生成代码 - 混合方案

    策略：
    1. 优先使用原始代码
    2. 如果可参数化，做智能替换
    3. 保证准确性
    """
    code = op.original_code

    # 如果可参数化且找到匹配的参数
    if op.is_parameterizable and op.input_value:
        param = find_matching_param(op.original_code, form_data)
        if param:
            # 智能替换：保留定位器，只替换值
            code = code.replace(f"fill('{op.input_value}')", f"fill({param})")
            code = code.replace(f'fill("{op.input_value}")', f"fill({param})")

    return code
```

**优点**：
- ✅ 保证准确性（使用原始代码）
- ✅ 支持参数化（智能替换）
- ✅ 实现简单

---

## 🎯 立即可用的解决方案

最快的修复方法：

```python
def analyze_and_generate_fixed(script_content: str, output_prefix: str):
    """
    修复版本 - 保留原始代码
    """
    lines = script_content.split('\n')

    # 1. 识别需要参数化的行和值
    parameterizable_lines = {}
    form_data = {}

    for line_no, line in enumerate(lines, 1):
        if '.fill(' in line:
            # 提取填充值
            match = re.search(r'\.fill\(["\']([^"\']+)["\']\)', line)
            if match:
                value = match.group(1)
                # 检查前面是否有WF_字段
                if 'WF_' in line:
                    field_match = re.search(r'WF_[A-Z_]+\.[A-Z]+', line)
                    if field_match:
                        field = field_match.group(0).split('.')[-1]
                        form_data[field.lower()] = value
                        parameterizable_lines[line_no] = (field.lower(), value)

    # 2. 生成函数
    func_code = []
    func_code.append("def execute_automation(")
    func_code.append("    playwright: Playwright,")

    # 参数
    for param, default in form_data.items():
        func_code.append(f'    {param}: str = "{default}",')

    func_code.append("):")
    func_code.append("    browser = playwright.chromium.launch(headless=False)")
    func_code.append("    context = browser.new_context()")
    func_code.append("    page = context.new_page()")
    func_code.append("")

    # 3. 逐行处理
    in_function = False
    for line_no, line in enumerate(lines, 1):
        stripped = line.strip()

        # 跳过函数定义等
        if 'def run(' in stripped or 'browser =' in stripped or 'context =' in stripped:
            if 'def run(' in stripped:
                in_function = True
            continue

        if not in_function or not stripped:
            continue

        # 处理代码行
        if line_no in parameterizable_lines:
            # 参数化这一行
            param, value = parameterizable_lines[line_no]
            code_line = stripped.replace(f"'{value}'", param)
            code_line = code_line.replace(f'"{value}"', param)
            func_code.append(f"    {code_line}")
        elif any(skip in stripped for skip in ['browser.close', 'context.close', 'with sync_playwright']):
            continue
        else:
            # 保留原始代码
            func_code.append(f"    {stripped}")

    func_code.append("")
    func_code.append("    context.close()")
    func_code.append("    browser.close()")

    return '\n'.join(func_code)
```

---

## 📝 使用建议

**短期解决方案**（立即可用）：
```python
# 使用analyze_and_generate_fixed
# 保留原始代码，只做最小化的参数替换
```

**长期解决方案**（推荐）：
```python
# 实现EnhancedOperation类
# 保存原始代码的同时支持智能参数化
```

**临时解决方案**（最快）：
```python
# 手动编辑生成的函数
# 从原始脚本复制定位器链
```

---

## ✨ 总结

**核心问题**：
- 定位器链提取不完整
- 特别是嵌套的`get_by_role`调用

**根本解决方案**：
- 保存原始代码
- 不依赖复杂的解析
- 只做必要的参数化替换

**实施建议**：
1. 短期：使用混合方案（保留原始代码+智能替换）
2. 长期：完善定位器链提取逻辑

---

**文档版本**: 1.0
**创建时间**: 2025-11-05
**问题严重性**: 高
**修复优先级**: 紧急
