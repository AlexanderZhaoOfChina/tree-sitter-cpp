
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
