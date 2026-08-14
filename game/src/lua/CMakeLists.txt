project(lua)

file(GLOB SOURCES *.cc)
file(GLOB HEADERS *.h)

include_directories(.)

if(WIN32)
  add_library(lua STATIC ${SOURCES} ${HEADERS})
else()
  add_library(lua SHARED ${SOURCES} ${HEADERS})
endif()

target_link_libraries(lua ${LUA_LIBRARIES})

install(TARGETS lua DESTINATION ${INSTALL_FOLDER})
