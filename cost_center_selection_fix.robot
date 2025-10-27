*** Settings ***
Library    SeleniumLibrary

*** Keywords ***
Select Cost Center By Data PID
    [Documentation]    点击成本中心树节点的展开图标，使用 data-pid 属性精确定位
    [Arguments]    ${data_pid}    ${cost_center_name}

    # 步骤1: 使用 data-pid 精确定位展开图标
    ${expand_icon_locator}=    Set Variable    xpath=//span[@data-pid='${data_pid}' and contains(@class, 'jtree_expand')]

    # 步骤2: 点击展开图标
    Wait Until Element Is Visible    ${expand_icon_locator}    timeout=10s
    Click Element    ${expand_icon_locator}
    Sleep    1s

    # 步骤3: 点击展开后的成本中心名称
    ${cost_center_label}=    Set Variable    xpath=//span[@data-pid='${data_pid}']/following-sibling::label[contains(., '${cost_center_name}')]
    Wait Until Element Is Visible    ${cost_center_label}    timeout=10s
    Click Element    ${cost_center_label}

Select Cost Center Reliable
    [Documentation]    完整的成本中心选择流程，包括多级展开
    [Arguments]    ${trigger_button_locator}

    # 点击"选择成本中心"按钮打开树选择器
    Click Element    ${trigger_button_locator}
    Sleep    1s

    # 如果需要展开多级节点，按顺序展开
    # 示例: 展开"技术与大数据平台部"
    ${tech_dept_pid}=    Set Variable    0102000008
    ${tech_dept_name}=    Set Variable    技术与大数据平台部

    # 点击展开图标
    ${expand_icon}=    Set Variable    xpath=//span[@data-pid='${tech_dept_pid}' and contains(@class, 'jtree_expand')]
    Wait Until Element Is Visible    ${expand_icon}    timeout=10s

    # 检查是否需要展开（如果是 jtree_node_close 状态才需要点击）
    ${class_attr}=    Get Element Attribute    ${expand_icon}    class
    Run Keyword If    'jtree_node_close' in '''${class_attr}'''    Click Element    ${expand_icon}
    Sleep    1s

    # 然后选择下级的成本中心
    # 这里需要根据实际的下级节点的 data-pid 来继续展开或选择

*** Test Cases ***
示例：选择成本中心
    [Documentation]    演示如何使用 data-pid 精确选择成本中心
    Open Browser    http://your-url.com    chrome
    # ... 登录等前置步骤 ...

    # 使用精确的 data-pid 定位
    ${trigger}=    Set Variable    xpath=//button[contains(., '选择成本中心')]
    Select Cost Center Reliable    ${trigger}

*** Comments ***
# 关键点说明：
# 1. data-pid 属性对每个树节点是唯一的，比文本定位更可靠
# 2. jtree_node_close 表示节点未展开，jtree_node_open 表示已展开
# 3. 展开图标和节点文本是兄弟关系，都在同一个 <li> 下
# 4. 如果需要选择多级，需要知道每一级的 data-pid 值

# 调试方法：
# 在浏览器开发者工具中执行：
# document.querySelectorAll('span[data-pid]').forEach(el => {
#     console.log('PID:', el.getAttribute('data-pid'), 'Text:', el.parentElement.textContent.trim());
# });
# 这样可以列出所有节点的 data-pid 和对应的文本
