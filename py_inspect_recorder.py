#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInspect Recorder - Windows 桌面自动化录制工具
类似 Playwright Codegen，一边操作一边生成 Pywinauto 代码

功能：
1. 实时录制用户操作（点击、输入）
2. 自动识别操作的 UI 元素
3. 生成 Pywinauto 代码
4. 支持开始/停止/清空录制
5. 一键复制生成的代码

依赖安装：
pip install pywinauto PyQt5 pynput pyperclip
"""

import sys
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTextEdit, QLabel,
                             QComboBox, QMessageBox, QSplitter, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor
from pywinauto import Desktop, Application
from pywinauto.controls.uiawrapper import UIAWrapper
from pynput import mouse, keyboard
import pyperclip


class RecorderThread(QThread):
    """录制线程 - 监听鼠标和键盘事件"""

    # 信号
    operation_detected = pyqtSignal(dict)  # 操作检测信号
    status_changed = pyqtSignal(str)  # 状态变化信号

    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.backend = 'uia'
        self.mouse_listener = None
        self.keyboard_listener = None
        self.last_click_time = 0
        self.click_delay = 0.5  # 防抖：0.5秒内的重复点击忽略
        self.typed_text = ""
        self.last_element = None

    def start_recording(self):
        """开始录制"""
        self.is_recording = True
        self.typed_text = ""
        self.last_element = None
        self.status_changed.emit("🔴 录制中...")

        # 启动鼠标监听
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.mouse_listener.start()

        # 启动键盘监听
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.keyboard_listener.start()

    def stop_recording(self):
        """停止录制"""
        self.is_recording = False
        self.status_changed.emit("⏸️ 已停止")

        # 如果有未提交的文本输入，先提交
        if self.typed_text and self.last_element:
            self._emit_type_operation()

        # 停止监听
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None

    def on_mouse_click(self, x, y, button, pressed):
        """鼠标点击事件"""
        if not self.is_recording:
            return

        # 只处理按下事件，忽略释放事件
        if not pressed:
            return

        # 只处理左键点击
        if button != mouse.Button.left:
            return

        # 防抖：忽略短时间内的重复点击
        current_time = time.time()
        if current_time - self.last_click_time < self.click_delay:
            return
        self.last_click_time = current_time

        # 如果有累积的文本输入，先提交
        if self.typed_text and self.last_element:
            self._emit_type_operation()

        try:
            # 获取鼠标位置的元素
            element = Desktop(backend=self.backend).from_point(x, y)

            if element and isinstance(element, UIAWrapper):
                # 提取元素属性
                props = self._extract_element_properties(element)
                props['action'] = 'click'
                props['position'] = (x, y)

                # 发送操作信号
                self.operation_detected.emit(props)

                # 记录当前元素（用于后续的键盘输入）
                self.last_element = element
                self.typed_text = ""

        except Exception as e:
            self.status_changed.emit(f"⚠️ 元素识别失败: {str(e)[:50]}")

    def on_key_press(self, key):
        """键盘按下事件"""
        if not self.is_recording:
            return

        try:
            # 处理普通字符
            if hasattr(key, 'char') and key.char:
                self.typed_text += key.char
            # 处理特殊键
            elif key == keyboard.Key.space:
                self.typed_text += ' '
            elif key == keyboard.Key.enter:
                # Enter 键：提交输入
                if self.typed_text and self.last_element:
                    self._emit_type_operation()
            elif key == keyboard.Key.backspace:
                # 退格键
                if self.typed_text:
                    self.typed_text = self.typed_text[:-1]
            elif key == keyboard.Key.tab:
                # Tab 键：提交当前输入并记录 Tab
                if self.typed_text and self.last_element:
                    self._emit_type_operation()
                self.operation_detected.emit({
                    'action': 'key',
                    'key': 'Tab'
                })
        except Exception as e:
            pass

    def on_key_release(self, key):
        """键盘释放事件"""
        pass

    def _emit_type_operation(self):
        """提交累积的文本输入"""
        if self.typed_text and self.last_element:
            try:
                props = self._extract_element_properties(self.last_element)
                props['action'] = 'type'
                props['text'] = self.typed_text
                self.operation_detected.emit(props)
            except:
                pass
            finally:
                self.typed_text = ""

    def _extract_element_properties(self, element):
        """提取元素属性"""
        try:
            props = {}
            props['control_type'] = element.element_info.control_type
            props['automation_id'] = element.element_info.automation_id
            props['class_name'] = element.element_info.class_name
            props['name'] = element.element_info.name
            props['process_id'] = element.element_info.process_id

            # 获取父窗口信息
            try:
                top_window = element.top_level_parent()
                props['window_title'] = top_window.window_text()
            except:
                props['window_title'] = "Unknown"

            return props
        except Exception as e:
            return {'error': str(e)}

    def run(self):
        """线程主循环"""
        while True:
            time.sleep(0.1)
            if not self.is_recording:
                break


class CodeGenerator:
    """代码生成器"""

    @staticmethod
    def generate_locator(props, backend='uia'):
        """生成元素定位代码"""
        automation_id = props.get('automation_id', '')
        class_name = props.get('class_name', '')
        name = props.get('name', '')
        control_type = props.get('control_type', '')

        # 优先使用 AutomationId
        if automation_id:
            return f'element = window.child_window(auto_id="{automation_id}")'

        # 其次使用 Name
        elif name:
            return f'element = window.child_window(title="{name}")'

        # 使用 class_name + control_type
        elif class_name:
            return f'element = window.child_window(class_name="{class_name}", control_type="{control_type}")'

        # 最后使用 control_type
        else:
            return f'element = window.child_window(control_type="{control_type}")'

    @staticmethod
    def generate_action(props):
        """生成操作代码"""
        action = props.get('action', 'click')

        if action == 'click':
            return "element.click()"
        elif action == 'type':
            text = props.get('text', '')
            # 转义特殊字符
            text = text.replace('"', '\\"')
            return f'element.type_keys("{text}")'
        elif action == 'key':
            key = props.get('key', '')
            key_map = {
                'Tab': '{TAB}',
                'Enter': '{ENTER}',
                'Esc': '{ESC}'
            }
            key_code = key_map.get(key, key)
            return f'element.type_keys("{key_code}")'
        else:
            return f"# Unknown action: {action}"

    @staticmethod
    def generate_complete_script(operations, backend='uia'):
        """生成完整脚本"""
        if not operations:
            return "# 没有录制到任何操作\n"

        script = []
        script.append("#!/usr/bin/env python3")
        script.append("# -*- coding: utf-8 -*-")
        script.append("# 自动生成的 Pywinauto 脚本\n")
        script.append("from pywinauto import Application")
        script.append("import time\n")
        script.append("def main():")
        script.append("    # 连接到应用程序")

        # 获取第一个操作的窗口信息
        first_op = operations[0]
        window_title = first_op.get('window_title', '.*')
        process_id = first_op.get('process_id', 0)

        script.append(f"    app = Application(backend='{backend}').connect(process={process_id})")
        script.append(f"    window = app.window(title_re='.*{window_title}.*')")
        script.append("    window.wait('visible', timeout=10)\n")
        script.append("    # 执行操作")

        # 生成每个操作
        for i, op in enumerate(operations):
            script.append(f"\n    # 操作 {i+1}: {op.get('action', 'unknown')}")

            # 生成定位代码
            locator = CodeGenerator.generate_locator(op, backend)
            script.append(f"    {locator}")
            script.append("    element.wait('visible', timeout=10)")

            # 生成操作代码
            action = CodeGenerator.generate_action(op)
            script.append(f"    {action}")
            script.append("    time.sleep(0.5)  # 等待操作完成")

        script.append("\n    print('✅ 操作执行完成')\n")
        script.append("if __name__ == '__main__':")
        script.append("    main()")

        return "\n".join(script)


class RecorderWindow(QMainWindow):
    """录制器主窗口"""

    def __init__(self):
        super().__init__()
        self.operations = []  # 录制的操作列表
        self.recorder_thread = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("PyInspect Recorder - Windows 桌面自动化录制工具")
        self.setGeometry(100, 100, 1200, 800)

        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 控制面板
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)

        # 分割器
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：操作列表
        operations_group = QGroupBox("📋 录制的操作")
        operations_layout = QVBoxLayout()
        self.operations_text = QTextEdit()
        self.operations_text.setReadOnly(True)
        self.operations_text.setFont(QFont("Courier", 10))
        operations_layout.addWidget(self.operations_text)
        operations_group.setLayout(operations_layout)
        splitter.addWidget(operations_group)

        # 右侧：生成的代码
        code_group = QGroupBox("💻 生成的代码")
        code_layout = QVBoxLayout()
        self.code_text = QTextEdit()
        self.code_text.setReadOnly(True)
        self.code_text.setFont(QFont("Courier", 10))
        code_layout.addWidget(self.code_text)

        # 代码操作按钮
        code_buttons = QHBoxLayout()
        copy_btn = QPushButton("📋 复制代码")
        copy_btn.clicked.connect(self.copy_code)
        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.clicked.connect(self.clear_operations)
        code_buttons.addWidget(copy_btn)
        code_buttons.addWidget(clear_btn)
        code_buttons.addStretch()
        code_layout.addLayout(code_buttons)

        code_group.setLayout(code_layout)
        splitter.addWidget(code_group)

        splitter.setSizes([400, 800])
        main_layout.addWidget(splitter)

        # 状态栏
        self.statusBar().showMessage("⏸️ 就绪 - 点击「开始录制」开始")

    def create_control_panel(self):
        """创建控制面板"""
        group = QGroupBox("⚙️ 控制面板")
        layout = QHBoxLayout()

        # Backend 选择
        layout.addWidget(QLabel("Backend:"))
        self.backend_combo = QComboBox()
        self.backend_combo.addItems(['uia', 'win32'])
        self.backend_combo.setCurrentText('uia')
        layout.addWidget(self.backend_combo)

        layout.addSpacing(20)

        # 录制控制按钮
        self.start_btn = QPushButton("🔴 开始录制")
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.start_btn.clicked.connect(self.start_recording)
        layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏸️ 停止录制")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_recording)
        layout.addWidget(self.stop_btn)

        layout.addStretch()

        # 帮助按钮
        help_btn = QPushButton("❓ 帮助")
        help_btn.clicked.connect(self.show_help)
        layout.addWidget(help_btn)

        group.setLayout(layout)
        return group

    def start_recording(self):
        """开始录制"""
        # 创建录制线程
        self.recorder_thread = RecorderThread()
        self.recorder_thread.backend = self.backend_combo.currentText()
        self.recorder_thread.operation_detected.connect(self.on_operation_detected)
        self.recorder_thread.status_changed.connect(self.on_status_changed)

        # 启动录制
        self.recorder_thread.start()
        self.recorder_thread.start_recording()

        # 更新UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.backend_combo.setEnabled(False)

        self.statusBar().showMessage("🔴 录制中... (在任意应用程序上进行操作)")

    def stop_recording(self):
        """停止录制"""
        if self.recorder_thread:
            self.recorder_thread.stop_recording()
            self.recorder_thread.quit()
            self.recorder_thread.wait()
            self.recorder_thread = None

        # 更新UI
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.backend_combo.setEnabled(True)

        self.statusBar().showMessage("⏸️ 已停止录制")

    def on_operation_detected(self, props):
        """处理检测到的操作"""
        # 添加到操作列表
        self.operations.append(props)

        # 更新操作列表显示
        action = props.get('action', 'unknown')
        window_title = props.get('window_title', 'Unknown')

        if action == 'click':
            name = props.get('name', props.get('automation_id', props.get('class_name', 'Unknown')))
            op_text = f"[{len(self.operations)}] 点击: {name} (窗口: {window_title})"
        elif action == 'type':
            text = props.get('text', '')
            op_text = f"[{len(self.operations)}] 输入: \"{text}\""
        elif action == 'key':
            key = props.get('key', '')
            op_text = f"[{len(self.operations)}] 按键: {key}"
        else:
            op_text = f"[{len(self.operations)}] 未知操作"

        self.operations_text.append(op_text)

        # 滚动到底部
        cursor = self.operations_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.operations_text.setTextCursor(cursor)

        # 更新生成的代码
        self.update_generated_code()

    def on_status_changed(self, status):
        """处理状态变化"""
        self.statusBar().showMessage(status)

    def update_generated_code(self):
        """更新生成的代码"""
        backend = self.backend_combo.currentText()
        code = CodeGenerator.generate_complete_script(self.operations, backend)
        self.code_text.setPlainText(code)

    def copy_code(self):
        """复制代码到剪贴板"""
        code = self.code_text.toPlainText()
        if code:
            try:
                pyperclip.copy(code)
                self.statusBar().showMessage("✅ 代码已复制到剪贴板", 3000)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"复制失败: {str(e)}")
        else:
            QMessageBox.warning(self, "提示", "没有可复制的代码")

    def clear_operations(self):
        """清空操作"""
        reply = QMessageBox.question(
            self, "确认", "确定要清空所有录制的操作吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.operations.clear()
            self.operations_text.clear()
            self.code_text.clear()
            self.statusBar().showMessage("🗑️ 已清空所有操作")

    def show_help(self):
        """显示帮助"""
        help_text = """
<h3>PyInspect Recorder 使用说明</h3>

<h4>📖 基本步骤：</h4>
<ol>
  <li><b>点击「开始录制」</b> - 启动录制模式</li>
  <li><b>在任意应用程序上操作</b> - 点击按钮、输入文字等</li>
  <li><b>点击「停止录制」</b> - 结束录制</li>
  <li><b>复制生成的代码</b> - 点击「复制代码」按钮</li>
</ol>

<h4>🎯 支持的操作：</h4>
<ul>
  <li>✅ 鼠标左键点击</li>
  <li>✅ 键盘文本输入</li>
  <li>✅ 特殊键（Tab、Enter）</li>
</ul>

<h4>⚙️ Backend 选择：</h4>
<ul>
  <li><b>UIA</b> - 推荐，支持现代应用</li>
  <li><b>Win32</b> - 适用于老旧应用</li>
</ul>

<h4>💡 提示：</h4>
<ul>
  <li>录制时避免过快连续点击</li>
  <li>输入文字后按 Enter 或点击其他元素来提交输入</li>
  <li>生成的代码可能需要手动调整</li>
</ul>
        """
        QMessageBox.information(self, "帮助", help_text)

    def closeEvent(self, event):
        """关闭窗口时停止录制"""
        if self.recorder_thread and self.recorder_thread.is_recording:
            self.stop_recording()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = RecorderWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
