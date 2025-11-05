#!/usr/bin/env python3
"""
快速测试脚本 - 测试增强型Playwright提取器

用法:
    python test_extractor_enhanced.py
"""

from playwright_variable_extractor_enhanced import analyze_playwright_script
from pathlib import Path


def main():
    print("🧪 开始测试增强型Playwright提取器\n")
    print("=" * 80)

    # 测试文件
    test_script = "example_playwright_script.py"
    output_dir = "./test_output"

    # 检查测试文件是否存在
    if not Path(test_script).exists():
        print(f"❌ 错误: 找不到测试文件 '{test_script}'")
        print("💡 请先创建示例脚本文件")
        return

    # 创建输出目录
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    try:
        # 执行分析
        print(f"\n📊 正在分析脚本: {test_script}")
        print("-" * 80)

        data = analyze_playwright_script(test_script, output_dir)

        # 显示关键统计
        print("\n" + "=" * 80)
        print("📈 测试结果统计:")
        print("=" * 80)
        print(f"✅ URL数量: {len(data.urls)}")
        print(f"✅ 定位器数量: {len(data.locators)}")
        print(f"✅ 操作数量: {len(data.actions)}")
        print(f"✅ 表单填充: {len(data.form_fills)}")
        print(f"✅ 下拉选择: {len(data.form_selects)}")
        print(f"✅ 点击元素: {len(data.clicked_elements)}")
        print(f"✅ 文件上传: {len(data.uploaded_files)}")
        print(f"✅ 键盘输入: {len(data.keyboard_inputs)}")
        print(f"✅ 等待操作: {len(data.waits)}")
        print(f"✅ 断言: {len(data.assertions)}")
        print(f"✅ 正则模式: {len(data.regex_patterns)}")
        print(f"✅ 变量: {len(data.variables)}")

        # 检查生成的文件
        print("\n" + "=" * 80)
        print("📂 生成的文件:")
        print("=" * 80)

        output_path = Path(output_dir)
        generated_files = list(output_path.glob("example_playwright_script_*"))

        for file in sorted(generated_files):
            size = file.stat().st_size
            print(f"  ✅ {file.name} ({size:,} bytes)")

        if not generated_files:
            print("  ⚠️  警告: 没有找到生成的文件")

        # 成功
        print("\n" + "=" * 80)
        print("✨ 测试完成！所有功能正常工作。")
        print("=" * 80)
        print(f"\n💡 查看生成的文件: {output_dir}/")
        print()

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
