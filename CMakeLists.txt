cmake_minimum_required(VERSION 2.8.3)
project(ha_python_ws_api)

# Find other CMake/Catkin packages needed for build
find_package(catkin REQUIRED COMPONENTS
	rospy
)

# Enable Python module support
catkin_python_setup()

# Specify package build info export
catkin_package(
  CATKIN_DEPENDS rospy
)

catkin_install_python(
    PROGRAMS
        bin/example.py
    DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})
