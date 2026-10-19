param([string]$CC='cc',[string]$Iverilog='iverilog',[string]$Vvp='vvp')
$ErrorActionPreference='Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    New-Item -ItemType Directory -Force build | Out-Null
    & $CC -std=c11 -Wall -Wextra -Werror -Ifirmware/include tests/test_firmware.c firmware/src/control.c firmware/src/protocol.c firmware/src/web.c firmware/src/config.c -o build/test_firmware.exe
    if($LASTEXITCODE) { throw 'C compilation failed' }
    & ./build/test_firmware.exe
    if($LASTEXITCODE) { throw 'Firmware tests failed' }
    & $Iverilog -g2012 -s tb_system -o build/tb_system fpga/rtl/crc112.sv fpga/rtl/spi_frame.sv fpga/rtl/mcp3204_scan.sv fpga/rtl/current_pi.sv fpga/rtl/lev_core.sv fpga/tb/tb_system.sv
    if($LASTEXITCODE) { throw 'HDL compilation failed' }
    & $Vvp build/tb_system
    if($LASTEXITCODE) { throw 'HDL tests failed' }
    python -m unittest discover -s tests -p 'test_*.py' -v
    if($LASTEXITCODE) { throw 'Calibration tests failed' }
} finally { Pop-Location }
