
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
