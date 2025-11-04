#!/usr/bin/env python3
"""
PyInspect Enhanced - Windows UI 元素检查器（增强版）

新增功能：
1. 自动生成 Pywinauto 代码
2. 代码复制到剪贴板
3. 三栏布局（控件树、属性、代码）
4. 右键菜单
5. 代码模板选择
6. 高亮当前选中元素
"""

from PyQt5.QtCore import QLocale, QCoreApplication, QSettings, Qt
from PyQt5.QtCore import QAbstractTableModel, QVariant
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QVBoxLayout,
                              QHBoxLayout, QLabel, QComboBox, QTreeView,
                              QTableView, QPushButton, QTextEdit, QSplitter,
                              QMessageBox, QMenu, QAction, QTabWidget)
import sys
import warnings
import pyperclip  # 用于复制到剪贴板

warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2
from pywinauto import backend


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    w = EnhancedWindow()
    w.show()
    sys.exit(app.exec_())


class CodeGenerator:
    """代码生成器 - 生成 Pywinauto 代码"""

    @staticmethod
    def generate_locator_code(props_dict, backend_type='uia'):
        """生成元素定位代码"""
        if not props_dict:
            return "# 请在左侧选择一个控件"

        # 提取关键属性
        automation_id = CodeGenerator._get_prop(props_dict, 'automation_id')
        class_name = CodeGenerator._get_prop(props_dict, 'class_name')
        control_type = CodeGenerator._get_prop(props_dict, 'control_type')
        name = CodeGenerator._get_prop(props_dict, 'name')

        # 生成代码
        code_lines = []
        code_lines.append("# " + "=" * 60)
        code_lines.append("# 元素定位代码")
        code_lines.append("# " + "=" * 60)
        code_lines.append("")

        # 方法 1：使用 automation_id（最推荐）
        if automation_id and automation_id != 'None':
            code_lines.append("# 方法 1：使用 AutomationId（推荐）⭐⭐⭐")
            code_lines.append(f"element = window.child_window(auto_id=\"{automation_id}\")")
            code_lines.append("")

        # 方法 2：使用类名和控件类型
        if class_name and class_name != 'None':
            code_lines.append("# 方法 2：使用类名")
            if control_type and control_type != 'None':
                code_lines.append(f"element = window.child_window(")
                code_lines.append(f"    class_name=\"{class_name}\",")
                code_lines.append(f"    control_type=\"{control_type}\"")
                code_lines.append(f")")
            else:
                code_lines.append(f"element = window.child_window(class_name=\"{class_name}\")")
            code_lines.append("")

        # 方法 3：使用名称
        if name and name != 'None':
            code_lines.append("# 方法 3：使用名称")
            code_lines.append(f"element = window.child_window(title=\"{name}\")")
            code_lines.append("")

        # 方法 4：组合方式（最精确）
        code_lines.append("# 方法 4：组合定位（最精确）⭐⭐⭐⭐⭐")
        code_lines.append(f"element = window.child_window(")
        if automation_id and automation_id != 'None':
            code_lines.append(f"    auto_id=\"{automation_id}\",")
        if control_type and control_type != 'None':
            code_lines.append(f"    control_type=\"{control_type}\",")
        if class_name and class_name != 'None':
            code_lines.append(f"    class_name=\"{class_name}\"")
        code_lines.append(f")")

        return "\n".join(code_lines)

    @staticmethod
    def generate_complete_script(props_dict, backend_type='uia', action='click'):
        """生成完整的可执行脚本"""
        if not props_dict:
            return "# 请在左侧选择一个控件"

        automation_id = CodeGenerator._get_prop(props_dict, 'automation_id')
        class_name = CodeGenerator._get_prop(props_dict, 'class_name')
        control_type = CodeGenerator._get_prop(props_dict, 'control_type')
        name = CodeGenerator._get_prop(props_dict, 'name')

        # 生成完整脚本
        code = f"""#!/usr/bin/env python3
\"\"\"
自动生成的 Pywinauto 脚本
Backend: {backend_type}
\"\"\"

from pywinauto import Application
import time

# ============================================================================
# 配置
# ============================================================================

APP_PATH = 'notepad.exe'  # 修改为你的应用路径
BACKEND = '{backend_type}'

# ============================================================================
# 主函数
# ============================================================================

def main():
    # 1. 启动应用（或连接到已运行的应用）
    print("启动应用...")
    app = Application(backend=BACKEND).start(APP_PATH)
    # 或连接到已运行的应用：
    # app = Application(backend=BACKEND).connect(path=APP_PATH)

    time.sleep(2)

    # 2. 获取主窗口
    print("连接到主窗口...")
    main_window = app.window(title_re='.*')  # 修改为实际窗口标题

    # 3. 定位元素
    print("定位元素...")
"""

        # 添加定位代码
        if automation_id and automation_id != 'None':
            code += f"""
    # 使用 AutomationId 定位（推荐）
    element = main_window.child_window(auto_id="{automation_id}")
"""
        elif class_name and class_name != 'None':
            code += f"""
    # 使用类名定位
    element = main_window.child_window(class_name="{class_name}")
"""
        else:
            code += f"""
    # 使用组合定位
    element = main_window.child_window(
        control_type="{control_type if control_type != 'None' else 'Edit'}",
        class_name="{class_name if class_name != 'None' else 'Edit'}"
    )
"""

        # 添加操作代码
        code += f"""
    # 4. 等待元素可用
    element.wait('visible', timeout=10)

    # 5. 执行操作
    print("执行操作...")
"""

        if action == 'click':
            code += """    element.click()
"""
        elif action == 'type':
            code += """    element.type_keys("Hello World!")
"""
        elif action == 'set_text':
            code += """    element.set_text("Hello World!")
"""
        elif action == 'get_text':
            code += """    text = element.window_text()
    print(f"文本内容: {{text}}")
"""

        code += """
    print("✓ 操作完成！")

    # 6. 清理
    time.sleep(2)
    # main_window.close()

if __name__ == "__main__":
    main()
"""

        return code

    @staticmethod
    def _get_prop(props_dict, key):
        """从属性字典中获取值"""
        for prop in props_dict:
            if prop[0] == key:
                return prop[1]
        return None


class EnhancedWindow(QWidget):
    """增强版主窗口"""

    def __init__(self):
        super(EnhancedWindow, self).__init__()

        self.setMinimumSize(1400, 900)
        self.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.setWindowTitle("PyInspect Enhanced - Windows UI 元素检查器")

        self.settings = QSettings('py_inspect_enhanced', 'MainWindow')

        # 当前选中的属性字典
        self.current_props = None
        self.current_backend = 'uia'

        # 初始化 UI
        self._init_ui()

        # 恢复窗口位置
        geometry = self.settings.value('Geometry', bytes('', 'utf-8'))
        self.restoreGeometry(geometry)

    def _init_ui(self):
        """初始化 UI"""

        # 主布局
        main_layout = QVBoxLayout()

        # ===== 顶部工具栏 =====
        toolbar_layout = QHBoxLayout()

        # Backend 选择
        toolbar_layout.addWidget(QLabel("Backend:"))
        self.backend_combo = QComboBox()
        for _backend in backend.registry.backends.keys():
            self.backend_combo.addItem(_backend)
        self.backend_combo.setCurrentText('uia')
        self.backend_combo.activated[str].connect(self._on_backend_changed)
        toolbar_layout.addWidget(self.backend_combo)

        toolbar_layout.addStretch()

        # 帮助按钮
        help_btn = QPushButton("❓ 帮助")
        help_btn.clicked.connect(self._show_help)
        toolbar_layout.addWidget(help_btn)

        main_layout.addLayout(toolbar_layout)

        # ===== 主内容区域（使用 Splitter 实现可调整大小的三栏布局）=====
        splitter = QSplitter(Qt.Horizontal)

        # ----- 左侧：控件树 -----
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("📂 控件树"))

        self.tree_view = QTreeView()
        self.tree_view.setColumnWidth(0, 250)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_tree_context_menu)
        left_layout.addWidget(self.tree_view)

        left_panel.setLayout(left_layout)
        splitter.addWidget(left_panel)

        # ----- 中间：属性表格 -----
        middle_panel = QWidget()
        middle_layout = QVBoxLayout()
        middle_layout.addWidget(QLabel("📋 元素属性"))

        self.table_view = QTableView()
        self.table_view.setColumnWidth(1, 320)
        middle_layout.addWidget(self.table_view)

        middle_panel.setLayout(middle_layout)
        splitter.addWidget(middle_panel)

        # ----- 右侧：代码生成 -----
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("💻 生成的代码"))

        # 代码标签页
        self.code_tabs = QTabWidget()

        # Tab 1: 定位代码
        self.locator_code_edit = QTextEdit()
        self.locator_code_edit.setReadOnly(True)
        self.locator_code_edit.setFont(QFont("Courier New", 10))
        self.code_tabs.addTab(self.locator_code_edit, "定位代码")

        # Tab 2: 完整脚本
        self.script_code_edit = QTextEdit()
        self.script_code_edit.setReadOnly(True)
        self.script_code_edit.setFont(QFont("Courier New", 10))
        self.code_tabs.addTab(self.script_code_edit, "完整脚本")

        right_layout.addWidget(self.code_tabs)

        # 操作按钮
        button_layout = QHBoxLayout()

        # 操作类型选择
        button_layout.addWidget(QLabel("操作:"))
        self.action_combo = QComboBox()
        self.action_combo.addItems(['click', 'type', 'set_text', 'get_text'])
        self.action_combo.currentTextChanged.connect(self._update_code)
        button_layout.addWidget(self.action_combo)

        button_layout.addStretch()

        # 复制按钮
        copy_locator_btn = QPushButton("📋 复制定位代码")
        copy_locator_btn.clicked.connect(self._copy_locator_code)
        button_layout.addWidget(copy_locator_btn)

        copy_script_btn = QPushButton("📋 复制完整脚本")
        copy_script_btn.clicked.connect(self._copy_script_code)
        button_layout.addWidget(copy_script_btn)

        right_layout.addLayout(button_layout)

        right_panel.setLayout(right_layout)
        splitter.addWidget(right_panel)

        # 设置初始比例 (30% : 30% : 40%)
        splitter.setSizes([350, 350, 500])

        main_layout.addWidget(splitter)

        # ===== 底部状态栏 =====
        status_layout = QHBoxLayout()
        self.status_label = QLabel("✓ 就绪 - 在左侧选择一个控件查看属性和生成代码")
        status_layout.addWidget(self.status_label)
        main_layout.addLayout(status_layout)

        self.setLayout(main_layout)

        # 初始化控件树
        self._initialize_tree('uia')

    def _initialize_tree(self, backend_type='uia'):
        """初始化控件树"""
        self.current_backend = backend_type
        try:
            self.status_label.setText(f"🔄 正在加载 {backend_type} 控件树...")
            QApplication.processEvents()

            self.element_info = backend.registry.backends[backend_type].element_info_class()
            self.tree_model = MyTreeModel(self.element_info, backend_type)
            self.tree_model.setHeaderData(0, Qt.Horizontal, '控件')
            self.tree_view.setModel(self.tree_model)
            self.tree_view.clicked.connect(self._on_element_selected)

            self.status_label.setText(f"✓ 就绪 ({backend_type}) - 在左侧选择一个控件")
        except Exception as e:
            self.status_label.setText(f"✗ 错误: {str(e)}")

    def _on_backend_changed(self, backend_type):
        """Backend 改变时重新加载"""
        self._initialize_tree(backend_type)

    def _on_element_selected(self, index):
        """元素被选中时"""
        data = index.data()
        self.current_props = self.tree_model.props_dict.get(data)

        # 更新属性表格
        self.table_model = MyTableModel(self.current_props, self)
        self.table_view.setModel(self.table_model)
        self.table_view.setColumnWidth(1, 320)

        # 更新代码
        self._update_code()

        # 更新状态
        self.status_label.setText(f"✓ 已选择: {data}")

    def _update_code(self):
        """更新生成的代码"""
        if not self.current_props:
            return

        action = self.action_combo.currentText()

        # 生成定位代码
        locator_code = CodeGenerator.generate_locator_code(
            self.current_props,
            self.current_backend
        )
        self.locator_code_edit.setPlainText(locator_code)

        # 生成完整脚本
        script_code = CodeGenerator.generate_complete_script(
            self.current_props,
            self.current_backend,
            action
        )
        self.script_code_edit.setPlainText(script_code)

    def _copy_locator_code(self):
        """复制定位代码到剪贴板"""
        code = self.locator_code_edit.toPlainText()
        if code:
            pyperclip.copy(code)
            QMessageBox.information(self, "成功", "✓ 定位代码已复制到剪贴板！")

    def _copy_script_code(self):
        """复制完整脚本到剪贴板"""
        code = self.script_code_edit.toPlainText()
        if code:
            pyperclip.copy(code)
            QMessageBox.information(self, "成功", "✓ 完整脚本已复制到剪贴板！")

    def _show_tree_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu()

        refresh_action = QAction("🔄 刷新", self)
        refresh_action.triggered.connect(lambda: self._initialize_tree(self.current_backend))
        menu.addAction(refresh_action)

        menu.addSeparator()

        copy_name_action = QAction("📋 复制元素名称", self)
        copy_name_action.triggered.connect(self._copy_element_name)
        menu.addAction(copy_name_action)

        menu.exec_(self.tree_view.viewport().mapToGlobal(position))

    def _copy_element_name(self):
        """复制元素名称"""
        index = self.tree_view.currentIndex()
        if index.isValid():
            data = index.data()
            pyperclip.copy(data)
            self.status_label.setText(f"✓ 已复制: {data}")

    def _show_help(self):
        """显示帮助"""
        help_text = """
PyInspect Enhanced - 使用帮助

功能：
1. 📂 控件树 - 浏览应用的 UI 结构
2. 📋 属性查看 - 查看元素的详细属性
3. 💻 代码生成 - 自动生成 Pywinauto 代码

使用步骤：
1. 选择 Backend (uia/win32)
2. 在控件树中展开并选择元素
3. 查看属性和生成的代码
4. 点击"复制"按钮复制代码到剪贴板
5. 在你的脚本中使用

提示：
- automation_id 是最稳定的定位方式
- 可以右键点击树进行刷新
- 完整脚本可以直接运行（修改 APP_PATH）
        """
        QMessageBox.information(self, "帮助", help_text)

    def closeEvent(self, event):
        """关闭时保存窗口状态"""
        geometry = self.saveGeometry()
        self.settings.setValue('Geometry', geometry)
        super(EnhancedWindow, self).closeEvent(event)


# ============================================================================
# 数据模型（沿用原代码）
# ============================================================================

class MyTreeModel(QStandardItemModel):
    def __init__(self, element_info, backend):
        QStandardItemModel.__init__(self)
        root_node = self.invisibleRootItem()
        self.props_dict = {}
        self.backend = backend
        self.branch = QStandardItem(self.__node_name(element_info))
        self.branch.setEditable(False)
        root_node.appendRow(self.branch)
        self.__generate_props_dict(element_info)
        self.__get_next(element_info, self.branch)

    def __get_next(self, element_info, parent):
        for child in element_info.children():
            self.__generate_props_dict(child)
            child_item = QStandardItem(self.__node_name(child))
            child_item.setEditable(False)
            parent.appendRow(child_item)
            self.__get_next(child, child_item)

    def __node_name(self, element_info):
        if 'uia' == self.backend:
            return '%s "%s" (%s)' % (str(element_info.control_type),
                                     str(element_info.name),
                                     id(element_info))
        elif 'atspi' == self.backend:
            return '%s "%s" (%s)' % (str(element_info.control_type),
                                     str(element_info.name),
                                     id(element_info))
        return '"%s" (%s)' % (str(element_info.name), id(element_info))

    def __generate_props_dict(self, element_info):
        props = [
            ['control_id', str(element_info.control_id)],
            ['class_name', str(element_info.class_name)],
            ['enabled', str(element_info.enabled)],
            ['handle', str(element_info.handle)],
            ['name', str(element_info.name)],
            ['process_id', str(element_info.process_id)],
            ['rectangle', str(element_info.rectangle)],
            ['rich_text', str(element_info.rich_text)],
            ['visible', str(element_info.visible)]
        ]

        props_win32 = [] if (self.backend == 'win32') else []

        props_uia = [
            ['automation_id', str(element_info.automation_id)],
            ['control_type', str(element_info.control_type)],
            ['element', str(element_info.element)],
            ['framework_id', str(element_info.framework_id)],
            ['runtime_id', str(element_info.runtime_id)]
        ] if (self.backend == 'uia') else []

        props_atspi = [
            ['control_type', str(element_info.control_type)],
            ['runtime_id', str(element_info.runtime_id)]
        ] if (self.backend == 'atspi') else []

        props.extend(props_uia)
        props.extend(props_win32)
        props.extend(props_atspi)
        node_dict = {self.__node_name(element_info): props}
        self.props_dict.update(node_dict)


class MyTableModel(QAbstractTableModel):
    def __init__(self, datain, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain if datain else []
        self.header_labels = ['属性', '值']

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        return len(self.arraydata[0]) if self.arraydata else 0

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.arraydata[index.row()][index.column()])

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)


if __name__ == "__main__":
    main()
