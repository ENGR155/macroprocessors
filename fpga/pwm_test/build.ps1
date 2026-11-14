param([ValidateRange(0,1200)][int]$HighTicks = 600)
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    foreach ($tool in 'yosys','nextpnr-ice40','icepack') {
        if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
            throw "Missing $tool. Add OSS CAD Suite to PATH, or use Radiant with pwm_20khz_top.sv."
        }
    }
    New-Item -ItemType Directory -Force build | Out-Null
    & yosys -p "read_verilog -sv -DYOSYS pwm_20khz_top.sv; chparam -set HIGH_TICKS $HighTicks pwm_20khz_top; synth_ice40 -top pwm_20khz_top -json build/pwm_20khz_top.json"
    if ($LASTEXITCODE) { throw 'Synthesis failed' }
    & nextpnr-ice40 --up5k --package sg48 --json build/pwm_20khz_top.json --pcf pwm_20khz_top.pcf --asc build/pwm_20khz_top.asc --freq 24
    if ($LASTEXITCODE) { throw 'Place and route failed' }
    & icepack build/pwm_20khz_top.asc build/pwm_20khz_top.bin
    if ($LASTEXITCODE) { throw 'Bitstream packaging failed' }
    Write-Output "Built build/pwm_20khz_top.bin: nominal 20 kHz, $($HighTicks / 12)% duty."
} finally { Pop-Location }
