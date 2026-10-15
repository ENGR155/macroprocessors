# Build, simulate, and program

## MCU: GNU Arm toolchain

Install CMake, Ninja or Make, and GNU Arm Embedded GCC. Supply the **device** headers containing `stm32l432xx.h`/`system_stm32l4xx.h` and the **CMSIS core** headers containing `core_cm4.h`. Your course repository already contains both under `lab/lab07/lab07_mcu/lab07_proj`. Do not copy generated lab outputs into this repository.

From the repository root in PowerShell:

```powershell
$course = '..\hmc-e155\lab\lab07\lab07_mcu\lab07_proj'
cmake -S firmware -B build/mcu -G Ninja `
  -DCMAKE_TOOLCHAIN_FILE=arm-gcc.cmake `
  -DSTM32_DEVICE_INCLUDE="$((Resolve-Path "$course/STM32L4xx/Device/Include").Path)" `
  -DCMSIS_CORE_INCLUDE="$((Resolve-Path "$course/CMSIS_5/CMSIS/Core/Include").Path)"
cmake --build build/mcu
```

Outputs: `build/mcu/maglev.elf`, `maglev.hex`, and `maglev.map`. GNU extensions are used for the vector table. The linker reserves the main 48 KiB SRAM bank and at least 4 KiB stack; the separate 16 KiB SRAM2 is unused. Standard C library support is supplied by GNU Arm with `nosys` stubs; floating-point printf is unnecessary.

Program the HEX through ST-LINK using STM32CubeProgrammer or your lab's established programming workflow. Select STM32L432KC, connect/reset, load the built image, verify, then run with coil power disconnected. The ST-LINK serial port is not the ESP8266 link used here.

## MCU: SEGGER project integration

If using Embedded Studio, create an STM32L432KC Cortex-M4F C project, enable hard-float FPv4-SP-D16, and add `firmware/include`, device CMSIS, and core CMSIS paths. Add `main.c`, `board_stm32l432.c`, `config.c`, `control.c`, `protocol.c`, and `web.c`. Use the IDE's device startup/system files **instead of** `src/startup.c` and its linker script. Ensure its SysTick vector reaches `SysTick_Handler` and `SystemCoreClock` is provided once. `board_init` establishes its own 16 MHz peripheral clock. The provided CMake target is for GNU Arm; it is not a SEGGER project file.

## FPGA

With OSS CAD Suite (`yosys`, `nextpnr-ice40`, `icepack`) on PATH:

```powershell
./fpga/build.ps1
```

The script targets UP5K SG48 and nominal 24 MHz. Preserve the synthesis/resource report and nextpnr timing report. The default `LEV_COMMISSIONED=0` makes the output gate constant off; synthesize and verify **both default and commissioned configurations**. Do not judge operational resource use from the disabled build. Keep the default disabled until bring-up authorizes changing it. Load `fpga/build/top.bin` with the UPduino programming method used in your lab, after reviewing the pad map and disconnecting coil power.

For Lattice Radiant, create an iCE40UP5K-SG48 SystemVerilog project, add all `fpga/rtl/*.sv`, set `top` as top level, add the `fpga/rtl` include path and `RADIANT` define, translate `upduino.pcf` assignments into the Radiant pin editor, select LVCMOS33, and constrain the internal oscillator at 24 MHz. The wrapper selects `HSOSC` for Radiant and `SB_HFOSC` for Yosys. Check timing, resource use, oscillator inference, and unused-pin behavior before producing a bitstream.

## Host checks

Use a native C compiler, Icarus Verilog supporting SystemVerilog, Python 3, and NumPy (`python -m pip install -r tools/requirements.txt`):

```powershell
./tests/run.ps1 -CC gcc
```

This runs the C behavior tests, full FPGA integration simulation with a behavioral ADC, and calibration tests. On Linux/macOS use equivalent compiler commands from the script and link `-lm` when required. No FPGA primitive library is needed for `tb_system`; it instantiates `lev_core` under a simulated clock. Top-level oscillator/pin configuration still requires the board toolchain.

## Web controls

Keep the course ESP8266 firmware unchanged. Connect its UART and 3.3 V supply as documented, join its labeled Wi-Fi network, and open `http://192.168.4.1/`. Current-test and height modes are selected while stopped. Clear a fault, then arm explicitly after checks pass. Default configuration refuses arming. The browser is an operating interface, not a remote programming interface or a safety-rated stop.

## Portfolio

```powershell
quarto render
```

The local HTML appears under `_site`. Review it locally before using Quarto's normal GitHub Pages publishing workflow. No deployment action is included in the scripts. Add actual photos, video links, team biographies, schematics, and measured results before presenting it as the final report.
