#!/usr/bin/env python
import os
import sys
import traceback
from cpp_parser import CppParser

def main():
    try:
        # 创建一个测试目录
        test_dir = "test_cpp_files"
        print(f"创建测试目录: {test_dir}")
        os.makedirs(test_dir, exist_ok=True)
        
        # 创建测试C++文件
        print("创建测试C++文件...")
        create_test_files(test_dir)
        print(f"测试文件创建完成，共创建了 {len(os.listdir(test_dir))} 个文件")
        
        # 编译Tree-sitter库
        print("编译Tree-sitter C++语言支持...")
        CppParser.build_tree_sitter_lib()
        print("Tree-sitter C++语言库编译完成")
        
        # 解析测试目录
        print(f"解析测试C++文件...")
        parser = CppParser(test_dir)
        parser.parse_directory()
        
        # 显示详细的调试信息
        parser._debug_print_state()
        
        # 生成报告
        output_file = "test_cpp_analysis.md"
        print(f"生成分析报告: {output_file}")
        parser.generate_markdown(output_file)
        
        # 检查输出文件
        if os.path.exists(output_file):
            print(f"报告生成成功，文件大小: {os.path.getsize(output_file)} 字节")
        else:
            print(f"错误：报告文件 {output_file} 未生成")
        
        print(f"完成! 请查看 {output_file}")
    
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        traceback.print_exc()

def create_test_files(test_dir):
    """创建测试C++文件"""
    print("创建测试C++文件...")
    
    # 创建一个头文件
    with open(os.path.join(test_dir, "person.h"), "w", encoding='utf-8') as f:
        f.write("""
// 一个简单的人员类
namespace example {

class Person {
public:
    Person(const std::string& name, int age);
    virtual ~Person();
    
    std::string getName() const;
    int getAge() const;
    virtual void printInfo() const;
    
private:
    std::string m_name;
    int m_age;
};

} // namespace example
""")
    
    # 创建实现文件
    with open(os.path.join(test_dir, "person.cpp"), "w", encoding='utf-8') as f:
        f.write("""
#include "person.h"
#include <iostream>

namespace example {

Person::Person(const std::string& name, int age)
    : m_name(name), m_age(age) {
}

Person::~Person() {
}

std::string Person::getName() const {
    return m_name;
}

int Person::getAge() const {
    return m_age;
}

void Person::printInfo() const {
    std::cout << "Name: " << m_name << ", Age: " << m_age << std::endl;
}

} // namespace example
""")
    
    # 创建派生类头文件
    with open(os.path.join(test_dir, "student.h"), "w", encoding='utf-8') as f:
        f.write("""
#pragma once
#include "person.h"
#include <vector>

namespace example {
namespace education {

class Student : public Person {
public:
    Student(const std::string& name, int age, const std::string& studentId);
    virtual ~Student() override;
    
    std::string getStudentId() const;
    void addCourse(const std::string& course);
    const std::vector<std::string>& getCourses() const;
    
    void printInfo() const override;
    
private:
    std::string m_studentId;
    std::vector<std::string> m_courses;
};

} // namespace education
} // namespace example
""")
    
    # 创建派生类实现文件
    with open(os.path.join(test_dir, "student.cpp"), "w", encoding='utf-8') as f:
        f.write("""
#include "student.h"
#include <iostream>

namespace example {
namespace education {

Student::Student(const std::string& name, int age, const std::string& studentId)
    : Person(name, age), m_studentId(studentId) {
}

Student::~Student() {
}

std::string Student::getStudentId() const {
    return m_studentId;
}

void Student::addCourse(const std::string& course) {
    m_courses.push_back(course);
}

const std::vector<std::string>& Student::getCourses() const {
    return m_courses;
}

void Student::printInfo() const {
    Person::printInfo();
    std::cout << "Student ID: " << m_studentId << std::endl;
    std::cout << "Courses: ";
    for (const auto& course : m_courses) {
        std::cout << course << " ";
    }
    std::cout << std::endl;
}

} // namespace education
} // namespace example
""")
    
    # 创建一个全局变量和函数的文件
    with open(os.path.join(test_dir, "globals.h"), "w", encoding='utf-8') as f:
        f.write("""
#pragma once
#include <string>

namespace example {

// 全局常量
extern const int MAX_STUDENTS;

// 全局函数
void initializeSystem();
bool registerStudent(const std::string& name, int age, const std::string& studentId);

} // namespace example
""")
    
    with open(os.path.join(test_dir, "globals.cpp"), "w", encoding='utf-8') as f:
        f.write("""
#include "globals.h"
#include "student.h"
#include <vector>
#include <iostream>

namespace example {

// 全局变量定义
const int MAX_STUDENTS = 100;
std::vector<education::Student> g_students;

void initializeSystem() {
    std::cout << "System initialized. Max students: " << MAX_STUDENTS << std::endl;
    g_students.clear();
}

bool registerStudent(const std::string& name, int age, const std::string& studentId) {
    if (g_students.size() >= MAX_STUDENTS) {
        return false;
    }
    
    g_students.emplace_back(name, age, studentId);
    return true;
}

} // namespace example
""")
    
    # 创建主程序文件
    with open(os.path.join(test_dir, "main.cpp"), "w", encoding='utf-8') as f:
        f.write("""
#include "person.h"
#include "student.h"
#include "globals.h"
#include <iostream>

int main() {
    // 初始化系统
    example::initializeSystem();
    
    // 创建并注册一些学生
    example::registerStudent("Alice", 20, "S001");
    example::registerStudent("Bob", 22, "S002");
    example::registerStudent("Charlie", 21, "S003");
    
    // 创建一个学生并添加课程
    example::education::Student student("Diana", 19, "S004");
    student.addCourse("Mathematics");
    student.addCourse("Computer Science");
    student.addCourse("Physics");
    
    // 打印学生信息
    student.printInfo();
    
    return 0;
}
""")

    # 创建一个测试文件
    with open(os.path.join(test_dir, "test.cpp"), "w", encoding='utf-8') as f:
        f.write("""
// 测试文件
int main() {
    return 0;
}
""")

if __name__ == "__main__":
    main() 