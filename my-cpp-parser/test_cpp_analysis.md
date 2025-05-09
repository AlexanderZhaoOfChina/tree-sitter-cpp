# C++ 代码分析报告

## 类

| 类 | 源文件位置 | 基类 |
|---|---|---|
| example::Person | person.h:5:1 | - |
| example::education::Student | student.h:9:1 | example::Person |

## 方法

| 类 | 方法 | 返回类型 | 源文件位置 |
|---|---|---|---|
| 全局 | initializeSystem | void | globals.cpp:13:1 |
| 全局 | main | int | main.cpp:7:1 |
| 全局 | main | int | test.cpp:3:1 |
| 全局 | registerStudent | bool | globals.cpp:18:1 |

## 变量

| 类 | 变量名 | 变量类型 | 变量位置 |
|---|---|---|---|
| example::Person | m_age | int | person.h:16:9 |
| example::Person | m_name | std::string | person.h:15:17 |
| example::education::Student | m_courses | std::vector<std::string> | student.h:22:30 |
| example::education::Student | m_studentId | std::string | student.h:21:17 |
| 全局 | MAX_STUDENTS | int | globals.cpp:10:11 |
