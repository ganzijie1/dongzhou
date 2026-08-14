project(mengde_rl)

include_directories(..)

add_executable(mengde_rl main.cc)
target_link_libraries(mengde_rl core util lua)

install(TARGETS mengde_rl DESTINATION ${INSTALL_FOLDER})
