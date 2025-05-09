#!/usr/bin/env python
import os
import sys

print("==== 调试信息 ====")
print(f"Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")
print(f"目录内容:")
for item in os.listdir('.'):
    if os.path.isdir(item):
        print(f" - 目录: {item}")
    else:
        print(f" - 文件: {item} ({os.path.getsize(item)} 字节)")

# 尝试导入相关模块
try:
    import tree_sitter
    print(f"成功导入tree_sitter模块，版本: {tree_sitter.__version__ if hasattr(tree_sitter, '__version__') else '未知'}")
except ImportError as e:
    print(f"无法导入tree_sitter模块: {e}")

# 尝试创建test_cpp_files目录并写入文件
try:
    test_dir = "test_cpp_files"
    os.makedirs(test_dir, exist_ok=True)
    test_file_path = os.path.join(test_dir, "test.cpp")
    with open(test_file_path, "w") as f:
        f.write("// Test file\nint main() { return 0; }\n")
    print(f"成功创建测试文件: {test_file_path}")
except Exception as e:
    print(f"创建测试文件时出错: {e}")

# 尝试创建输出文件
try:
    output_file = "debug_output.md"
    with open(output_file, "w") as f:
        f.write("# Debug Output\n\nThis is a test file.\n")
    print(f"成功创建输出文件: {output_file} ({os.path.getsize(output_file)} 字节)")
except Exception as e:
    print(f"创建输出文件时出错: {e}")

print("==== 调试结束 ====") 