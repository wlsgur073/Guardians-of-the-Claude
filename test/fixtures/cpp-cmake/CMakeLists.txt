cmake_minimum_required(VERSION 3.16)
project(myapp CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)

add_executable(myapp src/main.cpp src/app.cpp)
