cmake_minimum_required(VERSION 2.8.3)
project(ha_python_ws_api)

add_definitions(-std=c++11)

find_package(catkin REQUIRED
    COMPONENTS
)

catkin_package(
        INCLUDE_DIRS include
)

###########
## Build ##
###########

include_directories(
        include
)

install(DIRECTORY include/
	DESTINATION ${CATKIN_GLOBAL_INCLUDE_DESTINATION}
	FILES_MATCHING PATTERN "*.h"
)
