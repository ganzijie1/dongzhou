project(core)

file(GLOB SOURCES *.cc)
file(GLOB HEADERS *.h)

include_directories(.)

if(WIN32)
  add_library(core STATIC ${SOURCES} ${HEADERS})
else()
  add_library(core SHARED ${SOURCES} ${HEADERS})
endif()

target_link_libraries(core lua util)
target_link_libraries(core ${LUA_LIBRARIES})

install(TARGETS core DESTINATION ${INSTALL_FOLDER})
