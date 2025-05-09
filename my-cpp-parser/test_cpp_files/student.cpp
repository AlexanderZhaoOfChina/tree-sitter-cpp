
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
