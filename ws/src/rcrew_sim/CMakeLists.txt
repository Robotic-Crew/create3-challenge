cmake_minimum_required(VERSION 3.8)
project(rcrew_sim)

find_package(ament_cmake REQUIRED)

install(DIRECTORY gui launch urdf worlds DESTINATION share/${PROJECT_NAME})

ament_package()
