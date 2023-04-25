cmake_minimum_required(VERSION 3.0.2)
project(mscv_slam_dev_service)

## Compile as C++11, supported in ROS Kinetic and newer
# add_compile_options(-std=c++11)

## System dependencies are found with CMake's conventions
# find_package(Boost REQUIRED COMPONENTS system)
find_package(OpenCV 4 REQUIRED)
find_package(Pangolin REQUIRED)
find_package(Eigen3 REQUIRED)

###########
## Build ##
###########

## Specify additional locations of header files
## Your package locations should be listed before other locations
include_directories(
  ~/Dev/ORB_SLAM3/
  ~/Dev/ORB_SLAM3/include
  ~/Dev/ORB_SLAM3/include/CameraModels
  ~/Dev/ORB_SLAM3/Thirdparty/Sophus
  ${Pangolin_INCLUDE_DIRS}
  ${OpenCV_INCLUDE_DIRS}
)

## Declare a C++ library
# add_library(${PROJECT_NAME}
#   src/${PROJECT_NAME}/mscv_slam_service.cpp
# )

## Add cmake target dependencies of the library
## as an example, code may need to be generated before libraries
## either from message generation or dynamic reconfigure
# add_dependencies(${PROJECT_NAME} ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})

## Declare a C++ executable
## With catkin_make all packages are built within a single CMake context
## The recommended prefix ensures that target names across packages don't collide
add_executable(mono_service mono_service.cc)
add_executable(mono_nuc mono_nuc.cc)

## Rename C++ executable without prefix
## The above recommended prefix causes long target names, the following renames the
## target back to the shorter version for ease of user use
## e.g. "rosrun someones_pkg node" instead of "rosrun someones_pkg someones_pkg_node"
# set_target_properties(${PROJECT_NAME}_node PROPERTIES OUTPUT_NAME node PREFIX "")

## Add cmake target dependencies of the executable
## same as for the library above
# add_dependencies(${PROJECT_NAME} ${${PROJECT_NAME}_EXPORTED_TARGETS})

## Specify libraries to link a library or executable target against
target_link_libraries(mono_service
  ${EIGEN3_LIBS}
  ${Pangolin_LIBRARIES}
  ${OpenCV_LIBRARIES}
  ~/Dev/ORB_SLAM3/lib/libORB_SLAM3.so
)

target_link_libraries(mono_nuc
  ${EIGEN3_LIBS}
  ${Pangolin_LIBRARIES}
  ${OpenCV_LIBRARIES}
  ~/Dev/ORB_SLAM3/lib/libORB_SLAM3.so
)
