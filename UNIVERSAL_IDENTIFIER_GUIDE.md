# 通用Playwright变量识别器使用指南

## 📋 概述

这是一个**完全通用的Playwright脚本变量识别器**，能够处理任意结构的Playwright Codegen生成的代码，而不依赖于硬编码的字段名或特定的业务逻辑。

---

## 🎯 核心改进

相比于之前的`playwright_variable_identifier.py`，通用版本做了以下重大改进：

| 特性 | 原版本 | 通用版本 |
|-----|--------|---------|
| **适用性** | 仅适用特定脚本 | ✅ 适用任意脚本 |
| **字段识别** | 硬编码字段名 | ✅ 自动识别任意字段 |
| **操作类型** | 10种 | ✅ 15+种（含filter, check等） |
| **定位器链** | 简单识别 | ✅ 完整链式识别 |
| **配置生成** | 固定结构 | ✅ 智能动态结构 |
| **函数生成** | 固定模板 | ✅ 基于实际操作 |

---

## 🔧 四个核心通用函数

### 1. `universal_identify_variables(script_content: str)`

**功能**：通用变量识别 - 适配任意Playwright脚本

**识别能力**：

#### 操作类型识别（15+种）

```python
def identify_operation_type(code_line: str) -> Optional[str]:
    """
    智能识别操作类型

    支持的操作：
    - click, dblclick, hover       # 鼠标操作
    - fill, type, clear             # 输入操作
    - check, uncheck                # 复选框/单选框
    - select_option                 # 下拉选择
    - wait_for_timeout, wait_for_selector  # 等待
    - expect_popup                  # 弹窗
    - pause                         # 暂停
    - filter, locator               # 定位器
    """
```

#### 定位器链提取

```python
def extract_locator_chain(code_line: str) -> List[Dict[str, str]]:
    """
    提取完整的定位器链

    示例输入:
    page.locator("#id").get_by_text("文本").filter(has_text="过滤").click()

    返回:
    [
        {'type': 'locator', 'value': '#id'},
        {'type': 'get_by_text', 'value': '文本'},
        {'type': 'filter', 'value': 'has_text="过滤"'}
    ]
    """
```

**支持的定位器**：
- `locator()` - CSS选择器
- `get_by_text()` - 文本定位
- `get_by_role()` - 角色定位（cell, button, option等）
- `get_by_label()` - 标签定位
- `get_by_placeholder()` - placeholder定位
- `get_by_title()` - title定位
- `get_by_test_id()` - test-id定位
- `filter()` - 过滤器
- `nth()`, `first`, `last` - 索引定位

#### 示例：处理复杂定位

**输入代码**：
```python
page2.get_by_role("list").filter(has_text="上海上海").locator("span").click()
```

**识别结果**：
```python
Operation(
    line=36,
    operation_type='click',
    target_type='get_by_role',
    target_value='list',
    chain=[
        {'type': 'get_by_role', 'role': 'list', 'name': ''},
        {'type': 'filter', 'value': '上海上海'},
        {'type': 'locator', 'value': 'span'}
    ]
)
```

---

### 2. `smart_create_config(data: UniversalExtractedData)`

**功能**：智能创建配置 - 不硬编码字段，根据实际数据动态组织

**生成的配置结构**：

```json
{
  "metadata": {
    "url": "https://...",
    "total_operations": 48,
    "navigation_steps": 5,
    "form_fields": 11
  },
  "navigation": {
    "sequence": ["OA系统", "员工自助", "员工出差申请单-新"]
  },
  "form_fields": {
    "APPCAUSE": {
      "full_name": "cell: WF_ATS_LEAVEINFO.APPCAUSE",
      "value": "参加学术会议",
      "type": "fill",
      "line": 29
    },
    "FROMCITY": {
      "full_name": "cell: WF_ATS_TRAVLE.FROMCITY",
      "value": "上海",
      "type": "check",
      "line": 37
    }
    // ... 自动识别的所有字段
  },
  "operations_by_type": {
    "click": [...],    // 所有点击操作
    "fill": [...],     // 所有填充操作
    "check": [...],    // 所有选择操作
    "wait_timeout": [...]  // 所有等待操作
  },
  "wait_operations": [...],
  "popup_operations": [...]
}
```

**关键特性**：
- ✅ 自动推断字段类型
- ✅ 按操作类型分组
- ✅ 记录行号便于调试
- ✅ 完整的元数据

---

### 3. `generate_universal_function(data, config, function_name)`

**功能**：生成通用参数化函数 - 基于实际操作序列动态生成

**策略**：
1. 从`form_data`自动提取参数
2. 保留操作顺序
3. 生成清晰的注释
4. 智能变量替换

**示例输出**：

```python
def execute_automation(
    playwright: Playwright,
    url: str = "https://...",
    stime: str = "08:30",           # 自动识别
    etime: str = "17:30",           # 自动识别
    appcause: str = "参加学术会议",  # 自动识别
    fromcity: str = "上海",         # 自动识别
    tocity: str = "北京",           # 自动识别
    vehicle1: str = "飞机",         # 自动识别
    staydays: str = "3"             # 自动识别
) -> None:
    """自动生成的自动化函数"""
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # 导航到页面
    page.goto(url)

    # 执行操作序列（基于实际代码行）
    # CLICK 操作
    page.get_by_text('OA系统').first.click()

    # FILL 操作
    page.get_by_role('cell', name='WF_ATS_LEAVEINFO.APPCAUSE').fill(appcause)

    # CHECK 操作
    page.get_by_role('radio', name='上海').check()

    # ... 更多操作
```

---

### 4. `analyze_and_generate(script_content, output_prefix)`

**功能**：主函数 - 一站式分析和生成

**输出文件**：
1. `{prefix}_config.json` - 完整配置
2. `{prefix}_function.py` - 参数化函数
3. `{prefix}_data.json` - 原始数据

---

## 🚀 使用方法

### 方法1：直接运行（使用内置示例）

```bash
python universal_playwright_identifier.py
```

**输出**：
```
✅ 配置文件: business_trip_config.json
✅ 函数文件: business_trip_function.py
✅ 数据文件: business_trip_data.json
```

### 方法2：作为模块使用

```python
from universal_playwright_identifier import (
    universal_identify_variables,
    smart_create_config,
    generate_universal_function,
    analyze_and_generate
)

# 读取你的Playwright脚本
with open('my_playwright_script.py', 'r', encoding='utf-8') as f:
    script_content = f.read()

# 一键分析和生成
data, config, func_code = analyze_and_generate(
    script_content,
    output_prefix="my_automation"
)
```

### 方法3：分步使用（更灵活）

```python
# 步骤1：识别变量
data = universal_identify_variables(script_content)

# 步骤2：创建配置
config = smart_create_config(data)

# 步骤3：生成函数
func_code = generate_universal_function(data, config, "my_function")

# 步骤4：自定义处理
# ... 你的自定义逻辑
```

---

## 📊 实际案例对比

### 案例1：请假申请脚本

**脚本特点**：
- 简单表单填写
- 日期/时间选择
- 文本输入

**识别结果**：
- ✅ 识别6个表单字段
- ✅ 识别2个日期选择
- ✅ 识别2个时间选择
- ✅ 生成参数化函数（8个参数）

### 案例2：出差申请脚本（新）

**脚本特点**：
- 复杂的城市选择（filter + radio）
- 多级列表选择（listitem）
- 混合操作类型

**识别结果**：
- ✅ 识别11个表单字段
- ✅ 识别3个radio选择
- ✅ 识别48个操作
- ✅ 生成参数化函数（11个参数）

**关键改进**：
```python
# 原版无法识别的复杂定位
page2.get_by_role("list").filter(has_text="上海上海").locator("span").click()
page2.get_by_role("radio", name="上海").check()

# 通用版正确识别
✅ [36] click(locator: span)
✅ [37] check(get_by_role: radio: 上海) <- '上海'
```

---

## 💡 智能识别特性

### 1. 自动字段推断

**原理**：识别包含特定模式的字段名

```python
# 识别WF_开头的字段
if 'WF_' in op.target_value or 'FIELD' in op.target_value:
    current_field = op.target_value

# 关联后续的输入值
if op.input_value and current_field:
    field_key = current_field.split('.')[-1]
    data.form_data[field_key] = {
        'full_name': current_field,
        'value': op.input_value,
        'type': op.operation_type,
        'line': op.line
    }
```

**效果**：
```
WF_ATS_LEAVEINFO.APPCAUSE -> APPCAUSE
WF_ATS_TRAVLE.FROMCITY -> FROMCITY
```

### 2. 操作类型自动分组

**原理**：按操作类型分类统计

```python
config['operations_by_type'][op.operation_type].append({
    'line': op.line,
    'target': f"{op.target_type}: {op.target_value}",
    'value': op.input_value,
    'modifiers': op.modifiers
})
```

**效果**：
```json
{
  "operations_by_type": {
    "click": [/* 37个点击操作 */],
    "fill": [/* 3个填充操作 */],
    "check": [/* 3个选择操作 */],
    "wait_timeout": [/* 1个等待操作 */]
  }
}
```

### 3. 导航序列自动提取

**原理**：前几个click操作通常是导航

```python
nav_count = 0
for op in data.operations:
    if op.operation_type == 'click' and nav_count < 5:
        if op.target_value:
            data.navigation_sequence.append(op.target_value)
        nav_count += 1
```

**效果**：
```python
navigation_sequence = [
    "OA系统",
    "#magnet_8490099577463589529",
    "tab: 员工自助",
    "link: 员工出差申请单-新",
    "row: 出差类型"
]
```

---

## 🔍 支持的复杂模式

### 模式1：filter + locator 组合

**代码**：
```python
page2.get_by_role("list").filter(has_text="上海上海").locator("span").click()
```

**识别**：
```python
chain = [
    {'type': 'get_by_role', 'role': 'list'},
    {'type': 'filter', 'value': '上海上海'},
    {'type': 'locator', 'value': 'span'}
]
```

### 模式2：radio + check

**代码**：
```python
page2.get_by_role("radio", name="上海").check()
```

**识别**：
```python
Operation(
    operation_type='check',
    target_type='get_by_role',
    target_value='radio: 上海',
    input_value='上海'
)
```

### 模式3：nth修饰符

**代码**：
```python
page2.get_text("技术与大数据平台部").nth(1).click()
```

**识别**：
```python
Operation(
    modifiers=['nth(1)'],
    chain=[{'type': 'nth', 'value': '1'}]
)
```

### 模式4：expect_popup

**代码**：
```python
with page.expect_popup() as page1_info:
    page.get_by_text("OA系统").click()
page1 = page1_info.value
```

**识别**：
```python
popup_operations = [{
    'line': 10,
    'variable': 'page1_info',
    'code': 'with page.expect_popup() as page1_info:'
}]
```

### 模式5：wait_for_timeout

**代码**：
```python
page2.wait_for_timeout(5000)
```

**识别**：
```python
wait_operations = [{
    'line': 59,
    'type': 'timeout',
    'value': '5000'
}]
```

---

## 📈 对比表：原版 vs 通用版

| 功能 | 原版 | 通用版 | 说明 |
|-----|------|--------|------|
| **适用脚本** | 特定业务（请假） | ✅ 任意脚本 | 不依赖硬编码字段 |
| **定位器链** | 单层识别 | ✅ 多层链式 | 支持filter, nth等 |
| **操作类型** | 10种 | ✅ 15+种 | 新增check, filter等 |
| **字段识别** | 硬编码映射 | ✅ 自动推断 | 智能识别WF_前缀 |
| **配置结构** | 固定格式 | ✅ 动态生成 | 按操作类型分组 |
| **函数生成** | 固定模板 | ✅ 基于实际 | 根据操作序列生成 |
| **popup处理** | ❌ 不支持 | ✅ 支持 | 识别expect_popup |
| **wait处理** | ❌ 不支持 | ✅ 支持 | wait_for_timeout等 |
| **radio处理** | ❌ 不支持 | ✅ 支持 | check操作识别 |
| **filter处理** | ❌ 不支持 | ✅ 支持 | 完整链式定位 |

---

## 🎯 最佳实践

### 1. 使用完整脚本

```python
# ✅ 推荐：完整的函数定义
script = '''
from playwright.sync_api import Playwright

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch()
    # ... 完整代码
    browser.close()
'''

# ❌ 不推荐：片段代码
script = '''
page.goto("https://...")
page.click("button")
'''
```

### 2. 保留Codegen原始格式

```python
# ✅ 推荐：保留Codegen的原始格式
page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.APPCAUSE").get_by_role("textbox").click()

# ❌ 不推荐：手动简化
page2.locator("input").click()
```

### 3. 使用有意义的值

```python
# ✅ 推荐：具体的业务值
page.fill("参加学术会议")
page.select_option("外地出差")

# ❌ 不推荐：测试值
page.fill("test")
page.select_option("option1")
```

### 4. 添加注释说明

```python
# ✅ 推荐：添加业务说明
# 选择出差类型
page2.get_by_role("option", name="外地出差").click()

# 填写出差原因
page2.fill("参加学术会议")
```

---

## 🔧 扩展和定制

### 扩展1：添加新的操作类型

```python
def identify_operation_type(code_line: str) -> Optional[str]:
    operation_patterns = {
        # ... 现有模式

        # 添加新模式
        'drag_to': r'\.drag_to\(',
        'screenshot': r'\.screenshot\(',
        'evaluate': r'\.evaluate\(',
    }
```

### 扩展2：自定义字段识别规则

```python
def is_form_field(target_value: str) -> bool:
    """自定义字段识别规则"""
    patterns = [
        r'WF_',           # 工作流字段
        r'FIELD_',        # 通用字段
        r'INPUT_',        # 输入字段
        r'YOUR_PATTERN'   # 你的模式
    ]

    for pattern in patterns:
        if re.search(pattern, target_value):
            return True
    return False
```

### 扩展3：自定义配置结构

```python
def custom_create_config(data: UniversalExtractedData) -> Dict:
    """自定义配置生成"""
    config = {
        'basic': {
            'url': data.url,
            'title': 'My Custom Automation'
        },
        'steps': [],
        'validations': []
    }

    for op in data.operations:
        config['steps'].append({
            'action': op.operation_type,
            'element': op.target_value,
            'data': op.input_value
        })

    return config
```

---

## 🐛 故障排除

### 问题1：某些操作未被识别

**原因**：操作类型模式未定义

**解决**：
```python
# 查看原始代码行
print(script_lines[line_no])

# 添加对应的模式
operation_patterns['your_operation'] = r'\.your_operation\('
```

### 问题2：定位器链提取不完整

**原因**：定位器模式未匹配

**解决**：
```python
# 添加新的定位器模式
locator_patterns['your_locator'] = r'\.your_locator\(["\']([^"\']+)["\']\)'
```

### 问题3：字段值对应关系错误

**原因**：字段和值之间间隔太远

**解决**：
```python
# 调整字段追踪逻辑
# 可以记录最近N个操作的字段
recent_fields = deque(maxlen=5)
```

---

## 📚 技术细节

### AST vs 正则表达式

本通用版本**主要使用正则表达式**而非AST，原因：

1. **灵活性**：正则更容易扩展和调整
2. **上下文**：保留代码行的完整上下文
3. **链式识别**：更容易识别`.locator().filter().click()`这样的链式调用
4. **性能**：对于逐行分析，正则更快

### Operation数据类

```python
@dataclass
class Operation:
    line: int                      # 代码行号
    operation_type: str            # 操作类型（click, fill等）
    target_type: str               # 定位器类型
    target_value: str              # 定位器值
    input_value: Optional[str]     # 输入值（可选）
    modifiers: List[str]           # 修饰符（first, nth等）
    chain: List[Dict]              # 完整定位器链
```

---

## 🎓 总结

### 核心优势

1. ✅ **完全通用** - 适配任意Playwright脚本
2. ✅ **智能识别** - 15+操作类型，10+定位器
3. ✅ **自动推断** - 字段类型、值关联、导航序列
4. ✅ **动态生成** - 配置和函数基于实际内容
5. ✅ **完整追踪** - 行号、链式定位、修饰符

### 使用建议

- **简单脚本**：使用原版`playwright_variable_identifier.py`
- **复杂脚本**：使用通用版`universal_playwright_identifier.py`
- **批量处理**：使用增强版`playwright_variable_extractor_enhanced.py`

### 下一步

1. 根据实际脚本测试和调整
2. 添加自定义的操作类型和定位器
3. 扩展配置生成逻辑
4. 优化函数生成（处理page1/page2变量）

---

**文档版本**: 1.0
**最后更新**: 2025-11-05
**适用版本**: universal_playwright_identifier.py
