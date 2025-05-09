#!/usr/bin/env python
"""
一个用于查看Markdown报告的简单工具
"""
import sys
import os
import re

def convert_links(content):
    """将文件路径转换为可点击的链接"""
    def replace_path(match):
        path = match.group(1)
        return f"[{path}](file://{os.path.abspath(path)})"
    
    # 匹配文件路径并转换为链接
    pattern = r'(\w+\.[chp]+:\d+:\d+)'
    return re.sub(pattern, replace_path, content)

def view_markdown(file_path):
    """以正确的编码读取并显示Markdown文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 转换文件路径为链接
        content = convert_links(content)
        
        print("="*80)
        print(f"报告文件: {file_path}")
        print("="*80)
        print(content)
        print("="*80)
        
        # 输出一些统计信息
        classes = len(re.findall(r'\|\s+(\w+(?:::\w+)*)\s+\|', content))
        methods = len(re.findall(r'\|\s+(\w+(?:::\w+)*)\s+\|\s+(\w+)\s+\|', content))
        variables = len(re.findall(r'\|\s+(\w+(?:::\w+)*)\s+\|\s+(\w+)\s+\|\s+(\w+(?:::\w+)*)', content))
        
        print(f"统计信息:")
        print(f"- 类数量: {classes}")
        print(f"- 方法数量: {methods}")
        print(f"- 变量数量: {variables}")
        print("="*80)
    except Exception as e:
        print(f"读取文件时发生错误: {e}")

if __name__ == "__main__":
    # 如果没有提供文件路径参数，默认查看test_cpp_analysis.md
    file_path = sys.argv[1] if len(sys.argv) > 1 else "test_cpp_analysis.md"
    
    if not os.path.exists(file_path):
        print(f"错误: 文件 {file_path} 不存在")
        sys.exit(1)
    
    view_markdown(file_path) 