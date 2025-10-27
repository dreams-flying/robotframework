// 在浏览器开发者工具的 Console 中运行此脚本
// 用于调试和查找树节点的 data-pid 值

// 方法1: 列出所有节点的 data-pid 和文本
function listAllTreeNodes() {
    const nodes = document.querySelectorAll('span[data-pid]');
    console.log(`找到 ${nodes.length} 个树节点：`);
    console.log('='.repeat(80));

    nodes.forEach((el, index) => {
        const pid = el.getAttribute('data-pid');
        const ref = el.getAttribute('data-ref');
        const className = el.className;
        const parentLi = el.closest('li');
        const text = parentLi ? parentLi.textContent.trim().split('\n')[0].trim() : 'N/A';

        console.log(`[${index + 1}] PID: ${pid} | Ref: ${ref}`);
        console.log(`    文本: ${text}`);
        console.log(`    状态: ${className}`);
        console.log('-'.repeat(80));
    });
}

// 方法2: 搜索包含特定文本的节点
function findNodeByText(searchText) {
    const nodes = document.querySelectorAll('span[data-pid]');
    const matches = [];

    nodes.forEach(el => {
        const parentLi = el.closest('li');
        const text = parentLi ? parentLi.textContent.trim() : '';

        if (text.includes(searchText)) {
            const pid = el.getAttribute('data-pid');
            const ref = el.getAttribute('data-ref');
            const className = el.className;

            matches.push({
                pid: pid,
                ref: ref,
                text: text.split('\n')[0].trim(),
                className: className,
                element: el
            });
        }
    });

    console.log(`找到 ${matches.length} 个匹配项：`);
    matches.forEach((match, index) => {
        console.log(`[${index + 1}] PID: ${match.pid}`);
        console.log(`    文本: ${match.text}`);
        console.log(`    状态: ${match.className}`);
        console.log(`    XPath: //span[@data-pid='${match.pid}']`);
    });

    return matches;
}

// 方法3: 点击指定 data-pid 的展开图标（测试用）
function clickExpandByPid(pid) {
    const expandIcon = document.querySelector(`span[data-pid='${pid}'][class*='jtree_expand']`);

    if (!expandIcon) {
        console.error(`未找到 data-pid='${pid}' 的展开图标`);
        return false;
    }

    console.log('找到展开图标:', expandIcon);
    console.log('当前状态:', expandIcon.className);

    // 模拟点击
    expandIcon.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
    expandIcon.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
    expandIcon.dispatchEvent(new MouseEvent('click', { bubbles: true }));

    console.log('已点击展开图标');
    return true;
}

// 方法4: 获取节点的层级结构
function getNodeHierarchy(pid) {
    const node = document.querySelector(`span[data-pid='${pid}']`);
    if (!node) {
        console.error(`未找到 data-pid='${pid}' 的节点`);
        return;
    }

    const path = [];
    let current = node.closest('li');

    while (current) {
        const pidSpan = current.querySelector(':scope > span[data-pid]');
        if (pidSpan) {
            const pid = pidSpan.getAttribute('data-pid');
            const text = current.textContent.trim().split('\n')[0].trim();
            path.unshift({ pid, text });
        }

        // 向上查找父级 li
        const parentUl = current.parentElement;
        current = parentUl ? parentUl.closest('li') : null;
    }

    console.log('节点层级结构:');
    path.forEach((item, index) => {
        console.log(`${'  '.repeat(index)}└─ [${item.pid}] ${item.text}`);
    });

    return path;
}

// 使用示例：
console.log('=== 树节点调试工具已加载 ===');
console.log('可用命令：');
console.log('1. listAllTreeNodes()        - 列出所有节点');
console.log('2. findNodeByText("关键字")  - 搜索节点');
console.log('3. clickExpandByPid("pid")   - 点击展开');
console.log('4. getNodeHierarchy("pid")   - 查看层级');
console.log('');
console.log('示例：findNodeByText("技术与大数据平台部")');
