# C++ 源码解析器

这是一个基于Tree-sitter-cpp的C++源码解析器，用于解析C++代码并提取类、方法和变量等信息，并以Markdown表格形式输出。

## 功能特点

- 解析C++源码文件，包括头文件（.h, .hpp, .hxx）和实现文件（.cpp, .cc, .cxx）
- 提取所有类定义，包括类名、位置和基类信息
- 提取所有方法，包括方法名、返回类型和位置
- 提取所有变量，包括变量名、类型和位置
- 支持命名空间解析，正确处理命名空间路径
- 生成Markdown格式的分析报告，包含可点击的源文件链接

## 依赖项

- Python 3.6+
- tree-sitter (0.20.0+)

## 安装

1. 安装依赖项：

```bash
pip install -r requirements.txt
```

2. 编译Tree-sitter C++语言支持（首次运行时会自动执行）

## 使用方法

### 命令行使用

解析指定目录下的C++源码文件并生成报告：

```bash
python cpp_parser.py <C++源码目录> [输出Markdown文件]
```

例如：

```bash
python cpp_parser.py /path/to/cpp/project output.md
```

如果不指定输出文件，默认生成 `cpp_analysis.md`。

### 查看生成的报告

我们提供了一个特别的查看工具，可以正确显示Unicode字符并提供统计信息：

```bash
python view_report.py [报告文件路径]
```

如果不指定报告文件路径，默认查看 `test_cpp_analysis.md`。

### 运行测试示例

可以运行测试脚本来验证解析器的功能：

```bash
python test_cpp_parser.py
```

这将创建一些测试C++文件，解析它们，并生成一个 `test_cpp_analysis.md` 报告文件。

## 输出格式

生成的Markdown文件包含三个主要部分：

1. **类**：所有类定义的表格，包括类名、源文件位置和基类
2. **方法**：所有方法的表格，包括所属类、方法名、返回类型和源文件位置
3. **变量**：所有变量的表格，包括所属类、变量名、变量类型和变量位置

对于类和变量类型，如果是类，将会给出完整的命名空间路径。

## 项目文件结构

- `cpp_parser.py`：主解析器代码
- `test_cpp_parser.py`：测试脚本，用于生成测试数据和验证解析器功能
- `view_report.py`：查看生成的报告，支持Unicode并提供统计信息
- `requirements.txt`：依赖项列表
- `README.md`：项目文档

## 限制

- 对于复杂的模板类可能解析不完整
- 不支持解析函数参数的详细信息
- 对于某些特殊的C++语法可能无法完全识别
- 需要依赖tree-sitter的解析能力 