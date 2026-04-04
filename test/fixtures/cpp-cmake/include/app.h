#ifndef APP_H
#define APP_H

#include <string>

namespace myapp {

class App {
public:
    explicit App(std::string name);
    void run() const;

private:
    std::string name_;
};

} // namespace myapp

#endif // APP_H
