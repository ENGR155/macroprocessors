cmake_minimum_required(VERSION 3.20)
project(maglev C)
set(CMAKE_C_STANDARD 11)
if(NOT DEFINED STM32_DEVICE_INCLUDE OR NOT DEFINED CMSIS_CORE_INCLUDE)
  message(FATAL_ERROR "Set STM32_DEVICE_INCLUDE and CMSIS_CORE_INCLUDE to your CMSIS include directories")
endif()
add_executable(maglev.elf src/startup.c src/main.c src/board_stm32l432.c
  src/config.c src/control.c src/protocol.c src/web.c)
target_include_directories(maglev.elf PRIVATE include "${STM32_DEVICE_INCLUDE}" "${CMSIS_CORE_INCLUDE}")
target_compile_definitions(maglev.elf PRIVATE STM32L432xx)
target_compile_options(maglev.elf PRIVATE -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16
  -mfloat-abi=hard -Os -g3 -Wall -Wextra -Werror -ffunction-sections -fdata-sections)
target_link_options(maglev.elf PRIVATE -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16
  -mfloat-abi=hard -nostartfiles --specs=nosys.specs
  "-T${CMAKE_CURRENT_SOURCE_DIR}/stm32l432kc.ld" -Wl,--gc-sections,-Map=maglev.map)
target_link_libraries(maglev.elf PRIVATE m)
add_custom_command(TARGET maglev.elf POST_BUILD
  COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:maglev.elf> maglev.hex)
