project(util)

file(GLOB SOURCES *.cc)
file(GLOB HEADERS *.h)

include_directories(.)

if(WIN32)
  add_library(util STATIC ${SOURCES} ${HEADERS})
else()
  add_library(util SHARED ${SOURCES} ${HEADERS})
endif()

target_link_libraries(util ${SDL2_LIBRARY})
target_link_libraries(util ${Boost_LIBRARIES})

install(TARGETS util DESTINATION ${INSTALL_FOLDER})
