#include "app.h"
#include <iostream>

namespace myapp {

App::App(std::string name) : name_(std::move(name)) {}

void App::run() const {
    std::cout << "Running " << name_ << std::endl;
}

} // namespace myapp
