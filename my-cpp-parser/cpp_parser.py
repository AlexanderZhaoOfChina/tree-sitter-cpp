#!/usr/bin/env python
import os
import sys
import json
from tree_sitter import Language, Parser
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Set
import re
from pathlib import Path
import logging

# 定义数据结构
@dataclass
class Variable:
    name: str
    type: str
    full_type_path: str
    location: Tuple[str, int, int]  # 文件路径, 行, 列
    parent_class: Optional[str] = None

@dataclass
class Method:
    name: str
    location: Tuple[str, int, int]  # 文件路径, 行, 列
    parent_class: Optional[str] = None
    return_type: Optional[str] = None
    parameters: List[Variable] = None

@dataclass
class Class:
    name: str
    full_path: str
    location: Tuple[str, int, int]  # 文件路径, 行, 列
    methods: List[Method] = None
    variables: List[Variable] = None
    parent_classes: List[str] = None

    def __post_init__(self):
        if self.methods is None:
            self.methods = []
        if self.variables is None:
            self.variables = []
        if self.parent_classes is None:
            self.parent_classes = []

class CppParser:
    def __init__(self, cpp_dir: str):
        # 初始化Tree-sitter
        self.parser = Parser()
        
        # 检查是否存在已编译的语言库
        language_path = 'build/my-languages.so'
        if not os.path.exists(language_path):
            print(f"未找到编译后的语言库，正在编译...")
            self.build_tree_sitter_lib()
        
        # 加载C++语言支持
        self.language = Language(language_path, 'cpp')
        self.parser.set_language(self.language)
        
        # 存储结果
        self.classes: Dict[str, Class] = {}
        self.global_variables: List[Variable] = []
        self.global_methods: List[Method] = []
        
        # 存储包含路径映射
        self.include_map: Dict[str, str] = {}
        
        # 代码根目录
        self.cpp_dir = os.path.abspath(cpp_dir)
        
        # 已处理的文件集合
        self.processed_files: Set[str] = set()
        
        # 类型映射，用于解析类型完整路径
        self.type_map: Dict[str, str] = {}
        
        # 命名空间栈
        self.namespace_stack: List[str] = []
        
    @staticmethod
    def build_tree_sitter_lib():
        """编译Tree-sitter C++语言支持"""
        from tree_sitter import Language
        import os
        
        print("开始编译Tree-sitter C++语言支持...")
        
        # 确保build目录存在
        build_dir = "build"
        language_so = os.path.join(build_dir, "my-languages.so")
        os.makedirs(build_dir, exist_ok=True)
        
        # 获取当前脚本目录和tree-sitter-cpp目录的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tree_sitter_cpp_dir = os.path.abspath(os.path.join(current_dir, '..'))
        
        print(f"当前目录: {current_dir}")
        print(f"tree-sitter-cpp目录: {tree_sitter_cpp_dir}")
        
        # 检查源文件是否存在
        grammar_js = os.path.join(tree_sitter_cpp_dir, "grammar.js")
        if not os.path.exists(grammar_js):
            print(f"错误: 找不到grammar.js文件: {grammar_js}")
            raise FileNotFoundError(f"找不到grammar.js文件: {grammar_js}")
        
        # 编译语言库
        try:
            Language.build_library(
                language_so,
                [tree_sitter_cpp_dir]
            )
            print(f"Tree-sitter C++语言库编译成功: {language_so}")
            return language_so
        except Exception as e:
            print(f"编译Tree-sitter C++语言库时出错: {e}")
            raise
    
    def parse_file(self, file_path: str):
        """解析单个C++源文件"""
        if file_path in self.processed_files:
            return
        
        print(f"正在解析文件: {file_path}")
        
        self.processed_files.add(file_path)
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            tree = self.parser.parse(content)
            root_node = tree.root_node
            
            # 重置当前文件的命名空间栈
            self.namespace_stack = []
            
            # 解析文件
            self._traverse_node(root_node, content, file_path)
            
            # 文件解析完成后，修复可能缺失的命名空间信息
            self._fix_missing_namespaces()
            
        except Exception as e:
            print(f"解析文件 {file_path} 时出错: {e}")
    
    def _traverse_node(self, node, content: bytes, file_path: str, current_class: Optional[Class] = None):
        """遍历语法树节点"""
        # 检查节点类型
        if node.type == 'namespace_definition':
            # 查找命名空间名称
            namespace_name = None
            for child in node.children:
                if child.type == 'identifier':
                    namespace_name = content[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
                    self.namespace_stack.append(namespace_name)
                    print(f"进入命名空间: {namespace_name}, 当前栈: {self.namespace_stack}")
                    break
            
            # 处理命名空间内的声明
            for child in node.children:
                if child.type == 'declaration_list':
                    for decl in child.children:
                        self._traverse_node(decl, content, file_path, current_class)
                    break
            
            # 退出命名空间
            if namespace_name:
                self.namespace_stack.pop()
        
        elif node.type == 'class_specifier' or node.type == 'struct_specifier':
            # 处理类定义
            class_name = None
            for child in node.children:
                if child.type == 'type_identifier':
                    class_name = content[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
                    break
            
            if class_name:
                # 查找基类
                base_classes = []
                for child in node.children:
                    if child.type == 'base_class_clause':
                        for base_child in child.children:
                            if base_child.type == 'type_identifier':
                                base_name = content[base_child.start_byte:base_child.end_byte].decode('utf-8', errors='ignore')
                                # 尝试使用完整路径
                                if base_name in self.type_map:
                                    base_name = self.type_map[base_name]
                                base_classes.append(base_name)
                            elif base_child.type == 'qualified_identifier':
                                base_name = content[base_child.start_byte:base_child.end_byte].decode('utf-8', errors='ignore')
                                base_classes.append(base_name)
                
                # 创建完整路径，确保包含命名空间
                ns_prefix = '::'.join(self.namespace_stack) if self.namespace_stack else ""
                full_path = f"{ns_prefix}::{class_name}" if ns_prefix else class_name
                
                print(f"找到类: {class_name}, 命名空间: {ns_prefix}, 完整路径: {full_path}")
                
                # 创建类对象
                class_obj = Class(
                    name=class_name,
                    full_path=full_path,
                    location=(file_path, node.start_point[0] + 1, node.start_point[1] + 1),
                    parent_classes=base_classes
                )
                
                # 存储类对象
                self.classes[full_path] = class_obj
                
                # 将类名映射到完整路径 - 这很重要，用于正确引用类型
                self.type_map[class_name] = full_path
                
                # 如果我们有命名空间，也添加一个从完整名称到类型的映射
                if ns_prefix:
                    qualified_name = f"{ns_prefix}::{class_name}"
                    self.type_map[qualified_name] = full_path
                
                # 处理类内部的字段和方法
                for child in node.children:
                    if child.type == 'field_declaration_list':
                        for field in child.children:
                            self._traverse_node(field, content, file_path, class_obj)
        
        elif node.type == 'function_definition':
            # 处理函数/方法定义
            method_name = None
            return_type = None
            
            # 查找方法名
            for child in node.children:
                if child.type == 'function_declarator':
                    for decl_child in child.children:
                        if decl_child.type in ['identifier', 'field_identifier']:
                            method_name = content[decl_child.start_byte:decl_child.end_byte].decode('utf-8', errors='ignore')
                            break
                elif child.type in ['primitive_type', 'type_identifier', 'qualified_identifier']:
                    return_type = content[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
            
            if method_name:
                # 创建方法对象
                if current_class:
                    # 类方法
                    method = Method(
                        name=method_name,
                        location=(file_path, node.start_point[0] + 1, node.start_point[1] + 1),
                        parent_class=current_class.full_path,
                        return_type=return_type
                    )
                    current_class.methods.append(method)
                else:
                    # 全局方法
                    ns_prefix = '::'.join(self.namespace_stack) if self.namespace_stack else ""
                    full_name = f"{ns_prefix}::{method_name}" if ns_prefix else method_name
                    
                    method = Method(
                        name=full_name,
                        location=(file_path, node.start_point[0] + 1, node.start_point[1] + 1),
                        return_type=return_type
                    )
                    self.global_methods.append(method)
        
        elif node.type == 'field_declaration':
            # 处理类成员变量
            if current_class:
                type_name = None
                for child in node.children:
                    if child.type in ['primitive_type', 'type_identifier', 'qualified_identifier']:
                        type_name = content[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
                        break
                
                if type_name:
                    # 尝试使用完整的类型路径
                    full_type = type_name
                    if type_name in self.type_map:
                        full_type = self.type_map[type_name]
                    
                    # 查找变量名
                    for child in node.children:
                        if child.type == 'field_identifier':
                            var_name = content[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
                            
                            var = Variable(
                                name=var_name,
                                type=type_name,
                                full_type_path=full_type,
                                location=(file_path, child.start_point[0] + 1, child.start_point[1] + 1),
                                parent_class=current_class.full_path
                            )
                            current_class.variables.append(var)
        
        elif node.type == 'declaration':
            # 处理变量声明
            type_name = None
            for child in node.children:
                if child.type in ['primitive_type', 'type_identifier', 'qualified_identifier']:
                    type_name = content[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
                    break
            
            if type_name:
                # 尝试使用完整的类型路径
                full_type = type_name
                if type_name in self.type_map:
                    full_type = self.type_map[type_name]
                
                # 查找变量名
                for child in node.children:
                    if child.type == 'init_declarator':
                        for decl_child in child.children:
                            if decl_child.type == 'identifier':
                                var_name = content[decl_child.start_byte:decl_child.end_byte].decode('utf-8', errors='ignore')
                                
                                # 添加命名空间前缀
                                ns_prefix = '::'.join(self.namespace_stack) if self.namespace_stack else ""
                                full_name = f"{ns_prefix}::{var_name}" if ns_prefix else var_name
                                
                                var = Variable(
                                    name=full_name,
                                    type=type_name,
                                    full_type_path=full_type,
                                    location=(file_path, decl_child.start_point[0] + 1, decl_child.start_point[1] + 1)
                                )
                                self.global_variables.append(var)
        
        # 对于未特别处理的节点，继续递归遍历
        else:
            for child in node.children:
                self._traverse_node(child, content, file_path, current_class)
    
    def _resolve_type_path(self, type_name: str) -> str:
        """解析类型的完整路径"""
        # 如果是原始类型，直接返回
        primitive_types = {'int', 'char', 'float', 'double', 'bool', 'void', 'unsigned', 'signed', 'long', 'short'}
        if type_name in primitive_types:
            return type_name
        
        # 如果类型已经包含命名空间，直接返回
        if '::' in type_name:
            return type_name
        
        # 如果在类型映射中找到，返回映射的完整路径
        if type_name in self.type_map:
            return self.type_map[type_name]
        
        # 默认情况下返回原始类型名
        return type_name
    
    def parse_directory(self, directory: str = None):
        """解析整个目录中的C++文件"""
        if directory is None:
            directory = self.cpp_dir
        
        print(f"开始解析目录: {directory}")
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(('.cpp', '.cc', '.cxx', '.h', '.hpp', '.hxx')):
                    file_path = os.path.join(root, file)
                    self.parse_file(file_path)
        
        # 在解析完所有文件后，修复命名空间问题
        self._fix_missing_namespaces()
        
        # 显示解析结果
        class_count = len(self.classes)
        method_count = sum(len(cls.methods) for cls in self.classes.values()) + len(self.global_methods)
        var_count = sum(len(cls.variables) for cls in self.classes.values()) + len(self.global_variables)
        
        print(f"解析完成，共找到 {class_count} 个类, {method_count} 个方法, {var_count} 个变量")
        
        # 输出找到的类
        for cls_path, cls in self.classes.items():
            print(f"类: {cls_path}, 文件: {os.path.basename(cls.location[0])}")
        
        # 输出包含命名空间的全局方法和变量
        for method in self.global_methods:
            print(f"全局方法: {method.name}, 文件: {os.path.basename(method.location[0])}")
        
        for var in self.global_variables:
            print(f"全局变量: {var.name}, 类型: {var.full_type_path}, 文件: {os.path.basename(var.location[0])}")
    
    def generate_markdown(self, output_file: str):
        """生成Markdown报告文件"""
        # 记录已处理的项目，避免重复
        processed_methods = set()
        processed_variables = set()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # 写入标题
            f.write('# C++ 代码分析报告\n\n')
            
            # 写入类表格
            f.write('## 类\n\n')
            f.write('| 类 | 源文件位置 | 基类 |\n')
            f.write('|---|---|---|\n')
            
            for class_path, class_obj in sorted(self.classes.items()):
                file_path, line, col = class_obj.location
                rel_path = os.path.relpath(file_path, self.cpp_dir)
                
                # 处理基类，如果是已知类，显示完整路径
                formatted_base_classes = []
                for base in class_obj.parent_classes:
                    # 如果基类在我们的类型映射中，使用完整路径
                    if base in self.type_map:
                        formatted_base_classes.append(self.type_map[base])
                    else:
                        formatted_base_classes.append(base)
                
                base_classes = ', '.join(formatted_base_classes) if formatted_base_classes else '-'
                f.write(f'| {class_obj.full_path} | {rel_path}:{line}:{col} | {base_classes} |\n')
            
            # 写入方法表格
            f.write('\n## 方法\n\n')
            f.write('| 类 | 方法 | 返回类型 | 源文件位置 |\n')
            f.write('|---|---|---|---|\n')
            
            # 类方法
            for class_path, class_obj in sorted(self.classes.items()):
                for method in sorted(class_obj.methods, key=lambda m: m.name):
                    file_path, line, col = method.location
                    rel_path = os.path.relpath(file_path, self.cpp_dir)
                    
                    # 处理返回类型
                    return_type = method.return_type if method.return_type else '-'
                    if return_type in self.type_map:
                        return_type = self.type_map[return_type]
                    
                    # 避免重复
                    method_key = f"{class_obj.full_path}::{method.name}::{rel_path}:{line}:{col}"
                    if method_key in processed_methods:
                        continue
                    processed_methods.add(method_key)
                    
                    f.write(f'| {class_obj.full_path} | {method.name} | {return_type} | {rel_path}:{line}:{col} |\n')
            
            # 全局方法
            for method in sorted(self.global_methods, key=lambda m: m.name):
                file_path, line, col = method.location
                rel_path = os.path.relpath(file_path, self.cpp_dir)
                
                # 处理返回类型
                return_type = method.return_type if method.return_type else '-'
                if return_type in self.type_map:
                    return_type = self.type_map[return_type]
                
                # 避免重复
                method_key = f"global::{method.name}::{rel_path}:{line}:{col}"
                if method_key in processed_methods:
                    continue
                processed_methods.add(method_key)
                
                f.write(f'| 全局 | {method.name} | {return_type} | {rel_path}:{line}:{col} |\n')
            
            # 写入变量表格
            f.write('\n## 变量\n\n')
            f.write('| 类 | 变量名 | 变量类型 | 变量位置 |\n')
            f.write('|---|---|---|---|\n')
            
            # 类变量
            for class_path, class_obj in sorted(self.classes.items()):
                for var in sorted(class_obj.variables, key=lambda v: v.name):
                    file_path, line, col = var.location
                    rel_path = os.path.relpath(file_path, self.cpp_dir)
                    
                    # 处理变量类型
                    var_type = var.full_type_path
                    
                    # 避免重复
                    var_key = f"{class_obj.full_path}::{var.name}::{rel_path}:{line}:{col}"
                    if var_key in processed_variables:
                        continue
                    processed_variables.add(var_key)
                    
                    f.write(f'| {class_obj.full_path} | {var.name} | {var_type} | {rel_path}:{line}:{col} |\n')
            
            # 全局变量
            for var in sorted(self.global_variables, key=lambda v: v.name):
                file_path, line, col = var.location
                rel_path = os.path.relpath(file_path, self.cpp_dir)
                
                # 处理变量类型
                var_type = var.full_type_path
                
                # 避免重复
                var_key = f"global::{var.name}::{rel_path}:{line}:{col}"
                if var_key in processed_variables:
                    continue
                processed_variables.add(var_key)
                
                f.write(f'| 全局 | {var.name} | {var_type} | {rel_path}:{line}:{col} |\n')

    def _debug_print_state(self):
        """打印当前解析器状态的调试信息"""
        print("\n============ 调试信息 ============")
        
        print(f"\n已处理的文件 ({len(self.processed_files)}):")
        for file_path in sorted(self.processed_files):
            print(f"  {os.path.basename(file_path)}")
        
        print(f"\n类型映射 ({len(self.type_map)}):")
        for name, full_path in sorted(self.type_map.items()):
            print(f"  {name} -> {full_path}")
        
        print(f"\n类定义 ({len(self.classes)}):")
        for full_path, cls in sorted(self.classes.items()):
            file_path, line, col = cls.location
            print(f"  {full_path} ({os.path.basename(file_path)}:{line}) - 基类: {', '.join(cls.parent_classes) if cls.parent_classes else 'None'}")
            
            if cls.methods:
                print(f"    方法 ({len(cls.methods)}):")
                for method in sorted(cls.methods, key=lambda m: m.name):
                    file_path, line, col = method.location
                    print(f"      {method.name} ({os.path.basename(file_path)}:{line}) - 返回类型: {method.return_type}")
            
            if cls.variables:
                print(f"    变量 ({len(cls.variables)}):")
                for var in sorted(cls.variables, key=lambda v: v.name):
                    file_path, line, col = var.location
                    print(f"      {var.name} ({os.path.basename(file_path)}:{line}) - 类型: {var.full_type_path}")
        
        print(f"\n全局方法 ({len(self.global_methods)}):")
        for method in sorted(self.global_methods, key=lambda m: m.name):
            file_path, line, col = method.location
            print(f"  {method.name} ({os.path.basename(file_path)}:{line}) - 返回类型: {method.return_type}")
        
        print(f"\n全局变量 ({len(self.global_variables)}):")
        for var in sorted(self.global_variables, key=lambda v: v.name):
            file_path, line, col = var.location
            print(f"  {var.name} ({os.path.basename(file_path)}:{line}) - 类型: {var.full_type_path}")
        
        print("\n============ 调试结束 ============\n")

    def _fix_missing_namespaces(self):
        """修复可能缺失的命名空间信息"""
        # 创建新的类映射，确保所有类都有正确的命名空间
        new_classes = {}
        
        # 先处理类型映射
        for class_name, full_path in list(self.type_map.items()):
            if '::' not in full_path and class_name == full_path:
                # 这里应该尝试找到命名空间
                # 检查此类的文件路径，尝试分析文件内容寻找命名空间
                for path, cls in self.classes.items():
                    if cls.name == class_name:
                        file_path, line, _ = cls.location
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()
                                # 检查类定义前的几行，寻找namespace语句
                                start_line = max(0, line - 10)
                                end_line = min(len(lines), line + 2)
                                
                                current_ns = []
                                for i in range(start_line, end_line):
                                    if i < len(lines):
                                        line_text = lines[i].strip()
                                        # 检查namespace声明
                                        if "namespace" in line_text and "{" in line_text:
                                            ns_match = re.search(r'namespace\s+(\w+)', line_text)
                                            if ns_match:
                                                current_ns.append(ns_match.group(1))
                                
                                if current_ns:
                                    # 找到命名空间，更新类路径
                                    ns_prefix = "::".join(current_ns)
                                    new_full_path = f"{ns_prefix}::{class_name}"
                                    self.type_map[class_name] = new_full_path
                                    print(f"修复命名空间: {class_name} -> {new_full_path}")
                                    
                                    # 更新类对象
                                    cls.full_path = new_full_path
                                    new_classes[new_full_path] = cls
                                    continue
                        except Exception as e:
                            print(f"尝试修复命名空间时出错: {e}")
            
            # 如果没有特殊处理，保留原始类
            if full_path in self.classes:
                new_classes[full_path] = self.classes[full_path]
        
        # 更新类映射
        if new_classes:
            self.classes = new_classes

def main():
    if len(sys.argv) < 2:
        print("用法: python cpp_parser.py <C++源码目录> [输出Markdown文件]")
        sys.exit(1)
    
    cpp_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'cpp_analysis.md'
    
    # 编译Tree-sitter语言支持
    print("编译Tree-sitter C++语言支持...")
    CppParser.build_tree_sitter_lib()
    
    # 创建解析器并解析代码
    print(f"开始解析C++代码: {cpp_dir}")
    parser = CppParser(cpp_dir)
    parser.parse_directory()
    
    # 生成报告
    print(f"生成分析报告: {output_file}")
    parser.generate_markdown(output_file)
    
    print("完成!")

if __name__ == "__main__":
    main() 