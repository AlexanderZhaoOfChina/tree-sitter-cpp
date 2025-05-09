
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
