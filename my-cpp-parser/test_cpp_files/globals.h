
#pragma once
#include <string>

namespace example {

// 全局常量
extern const int MAX_STUDENTS;

// 全局函数
void initializeSystem();
bool registerStudent(const std::string& name, int age, const std::string& studentId);

} // namespace example
