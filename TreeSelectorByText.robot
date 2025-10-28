*** Settings ***
Library    SeleniumLibrary

*** Keywords ***
Click Tree Expand Icon By Text
    [Documentation]    通过节点文字定位，点击右边的展开图标
    ...                适用于树形结构中 label 和 expand icon 是兄弟元素的情况
    [Arguments]    ${node_text}

    # 方法1: 通过 label 文字定位，然后找到后面的兄弟 span（推荐）
    ${expand_icon_locator}=    Set Variable    xpath=//label[normalize-space(text())='${node_text}']/following-sibling::span[contains(@class, 'jtree_expand')]

    # 等待元素可见并点击
    Wait Until Element Is Visible    ${expand_icon_locator}    timeout=10s

    # 检查节点状态 - 只有关闭状态才需要点击
    ${class_attr}=    Get Element Attribute    ${expand_icon_locator}    class
    ${is_closed}=    Run Keyword And Return Status    Should Contain    ${class_attr}    jtree_node_close

    # 如果是关闭状态，点击展开
    Run Keyword If    ${is_closed}
    ...    Click Element    ${expand_icon_locator}

    Run Keyword If    ${is_closed}
    ...    Sleep    1s

    [Return]    ${is_closed}

Click Tree Expand Icon By Text - Alternative 1
    [Documentation]    备选方案1: 通过 input 的 data-text 属性定位
    [Arguments]    ${node_text}

    ${expand_icon_locator}=    Set Variable    xpath=//input[@data-text='${node_text}']/following-sibling::span[contains(@class, 'jtree_expand')]

    Wait Until Element Is Visible    ${expand_icon_locator}    timeout=10s
    Click Element    ${expand_icon_locator}
    Sleep    1s

Click Tree Expand Icon By Text - Alternative 2
    [Documentation]    备选方案2: 通过父 div 中的 label 文字定位
    [Arguments]    ${node_text}

    # 先找到包含该文字的 div.radio-1，再找其中的 expand icon
    ${expand_icon_locator}=    Set Variable    xpath=//div[contains(@class, 'radio')]//label[text()='${node_text}']/../span[contains(@class, 'jtree_expand')]

    Wait Until Element Is Visible    ${expand_icon_locator}    timeout=10s
    Click Element    ${expand_icon_locator}
    Sleep    1s

Click Tree Expand Icon By Text - Alternative 3
    [Documentation]    备选方案3: 使用 contains 进行模糊匹配（更宽松）
    [Arguments]    ${node_text}

    ${expand_icon_locator}=    Set Variable    xpath=//label[contains(text(), '${node_text}')]/following-sibling::span[contains(@class, 'jtree_expand')]

    Wait Until Element Is Visible    ${expand_icon_locator}    timeout=10s
    Click Element    ${expand_icon_locator}
    Sleep    1s

Debug - Find Expand Icon Locator
    [Documentation]    调试关键字：查找有多少个匹配的展开图标
    [Arguments]    ${node_text}

    ${locator1}=    Set Variable    xpath=//label[normalize-space(text())='${node_text}']/following-sibling::span[contains(@class, 'jtree_expand')]
    ${locator2}=    Set Variable    xpath=//input[@data-text='${node_text}']/following-sibling::span[contains(@class, 'jtree_expand')]
    ${locator3}=    Set Variable    xpath=//label[contains(text(), '${node_text}')]/following-sibling::span[contains(@class, 'jtree_expand')]

    ${count1}=    Get Element Count    ${locator1}
    ${count2}=    Get Element Count    ${locator2}
    ${count3}=    Get Element Count    ${locator3}

    Log    方法1 (label精确匹配): 找到 ${count1} 个元素    console=True
    Log    方法2 (data-text属性): 找到 ${count2} 个元素    console=True
    Log    方法3 (label模糊匹配): 找到 ${count3} 个元素    console=True

    # 如果找到元素，打印详细信息
    Run Keyword If    ${count1} > 0
    ...    Log Element Details    ${locator1}

Log Element Details
    [Arguments]    ${locator}

    ${elements}=    Get WebElements    ${locator}
    ${index}=    Set Variable    1

    FOR    ${element}    IN    @{elements}
        ${class}=    Get Element Attribute    ${element}    class
        ${data_pid}=    Get Element Attribute    ${element}    data-pid
        ${data_ref}=    Get Element Attribute    ${element}    data-ref
        ${is_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${element}

        Log    [${index}] class: ${class}    console=True
        Log    [${index}] data-pid: ${data_pid}    console=True
        Log    [${index}] data-ref: ${data_ref}    console=True
        Log    [${index}] 可见: ${is_visible}    console=True
        Log    ----    console=True

        ${index}=    Evaluate    ${index} + 1
    END

Select Tree Node By Text Complete
    [Documentation]    完整流程：展开节点并选择（如果需要）
    [Arguments]    ${node_text}    ${should_select}=False

    # 1. 点击展开图标
    Log    正在展开节点: ${node_text}    console=True
    ${was_expanded}=    Click Tree Expand Icon By Text    ${node_text}

    # 2. 如果需要选择该节点，点击 label
    Run Keyword If    ${should_select}
    ...    Click Element    xpath=//label[normalize-space(text())='${node_text}']

*** Test Cases ***
测试1：点击"技术与大数据平台部"的展开图标
    [Documentation]    使用推荐方法点击展开图标
    Open Browser    http://your-url.com    chrome
    # ... 登录和导航到页面 ...

    # 打开成本中心选择树
    Click Element    xpath=//button[contains(., '选择成本中心')]
    Sleep    1s

    # 点击展开图标
    Click Tree Expand Icon By Text    技术与大数据平台部

    # 如果还需要选择子节点，继续操作
    # Click Tree Expand Icon By Text    某个子部门名称

    [Teardown]    Close Browser

测试2：调试定位器
    [Documentation]    先运行此测试查看各种定位方法找到多少个元素
    Open Browser    http://your-url.com    chrome
    # ... 登录和导航到页面 ...

    Click Element    xpath=//button[contains(., '选择成本中心')]
    Sleep    2s

    # 调试查看
    Debug - Find Expand Icon Locator    技术与大数据平台部

    # 不要关闭浏览器，方便查看结果
    Sleep    30s

    [Teardown]    Close Browser

测试3：多级展开（通过文字）
    [Documentation]    展开多级树节点
    Open Browser    http://your-url.com    chrome
    # ... 登录和导航 ...

    Click Element    xpath=//button[contains(., '选择成本中心')]
    Sleep    1s

    # 按顺序展开各级
    Click Tree Expand Icon By Text    一级部门名称
    Click Tree Expand Icon By Text    技术与大数据平台部
    Click Tree Expand Icon By Text    三级部门名称

    # 最后选择目标节点
    Click Element    xpath=//label[normalize-space(text())='目标部门名称']

    [Teardown]    Close Browser

*** Comments ***
# ============================================================================
# XPath 定位策略说明
# ============================================================================
#
# HTML 结构：
# <div class="radio-1">
#     <input data-text="技术与大数据平台部" ...>
#     <label>技术与大数据平台部</label>
#     <span class="jtree_expand jtree_node_open" data-pid="0102000008"></span>
# </div>
#
# 关键点：
# - label 和 span 是同级兄弟元素（siblings）
# - 使用 following-sibling 轴来定位后面的兄弟元素
#
# 推荐使用的 XPath（方法1）：
# //label[normalize-space(text())='技术与大数据平台部']/following-sibling::span[contains(@class, 'jtree_expand')]
#
# 优点：
# ✅ 通过文字定位（符合要求）
# ✅ 点击的是文字右边的 span 符号（符合要求）
# ✅ normalize-space() 处理空白字符，更健壮
# ✅ 使用 following-sibling 轴，只查找后面的兄弟元素
#
# 备选方案：
# 1. 通过 input 的 data-text 属性
# 2. 通过父 div 定位
# 3. 使用 contains 模糊匹配
#
# 节点状态：
# - jtree_node_close = 节点关闭（需要点击展开）
# - jtree_node_open = 节点打开（已展开，无需再点击）
# ============================================================================
