
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
