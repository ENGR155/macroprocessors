$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    New-Item -ItemType Directory -Force build | Out-Null
    & yosys -p 'read_verilog -sv -Irtl rtl/crc112.sv rtl/spi_frame.sv rtl/mcp3204_scan.sv rtl/current_pi.sv rtl/lev_core.sv rtl/top.sv; synth_ice40 -dsp -top top -json build/top.json'
    if ($LASTEXITCODE) { throw 'Synthesis failed' }
    & nextpnr-ice40 --up5k --package sg48 --json build/top.json --pcf constraints/upduino.pcf --asc build/top.asc --freq 24
    if ($LASTEXITCODE) { throw 'Place and route failed' }
    & icepack build/top.asc build/top.bin
    if ($LASTEXITCODE) { throw 'Bitstream packaging failed' }
} finally { Pop-Location }
