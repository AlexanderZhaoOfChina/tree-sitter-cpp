
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
