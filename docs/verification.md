# Verification record — 2026-10-15

## Executed software and HDL checks

| Check | Result and scope |
|---|---|
| Native C compile with warnings treated as errors | Passed using Zig 0.16.0 / Clang on Windows |
| C behavior tests | Passed: CRC known vector/corruption, packet packing, control direction, saturation/anti-windup, current ramp, derivative initialization, missed-update fault, rail/fault handling, exact web routes, HTML termination and buffer bounds |
| Cortex-M4F source compilation | All seven C translation units compiled, using the course's CMSIS device/core headers and installed embedded runtime headers |
| SystemVerilog elaboration | Checked with slang and Icarus; final integration compiled with Icarus Verilog 13.0 |
| FPGA integration simulation | Passed: actual mode-0 ADC commands/channel ordering, telemetry CRC, enabled regulation, malformed/short packets, frozen-ID timeout, immediate external gate removal, latched faults, sampled overcurrent, scan timeout, and permanently disabled uncommissioned build |
| Calibration tests | Three Python/NumPy tests passed: recover an identifiable affine model, reject degenerate signals, expose an inadequate nonlinear fit through residuals |
| FPGA implementation | Active top-level design synthesized and routed for iCE40UP5K-SG48; final resource and timing summary below |

The final design uses the internal oscillator divided to nominal 24 MHz, while retaining nominal 20 kHz PWM and 10 kHz scans/current updates. Serial CRC and registered arithmetic/control paths avoid long combinational feedback paths. The ADC SPI clock is nominal 0.857 MHz to leave margin below its conservative 1 MHz limit.

Implementation tools: YoWASP Yosys 0.70 and nextpnr-ice40 0.11.1. Resource/timing checks explicitly override `top.COMMISSIONED=1`; source defaults remain disabled. Reproduce by adding `chparam -set COMMISSIONED 1 top` before `synth_ice40 -dsp` in a verification build, then routing with the supplied PCF and `--freq 24`. Do not flash a verification build as authorization to skip bring-up.

| Enabled top-level implementation | Final result |
|---|---:|
| UP5K logic cells | 1971 / 5280 (37%) |
| DSP blocks | 2 / 8 (25%) |
| Routed maximum internal clock estimate | 45.79 MHz |
| Required nominal internal clock | 24.00 MHz — passed |

These are tool estimates for the checked source, pin map, and placement, not measured board performance. The divided internal clock leaves substantial margin beyond the 24 MHz nominal rate. The default disabled top-level was also built and routed separately; the active result above is the meaningful resource check.

## Limits of these checks

No boards or instruments were attached. No real lift, height accuracy, thermal behavior, analog bandwidth, wiring continuity, current-sense scale, gate-off time, or external serial timing has been measured. The full GNU Arm CMake executable/runtime link and programming workflow have not been executed in this environment; object compilation is not a verified flash image. The linker/build files are provided for the installed course toolchain workflow and need its final build/program check.

Simulation uses ideal ADC values and a fixed clock, not a physical coil/field model. Static timing checks internal synchronous paths for the selected tool/device model; external interlock propagation and SPI setup/hold still require the scope tests in docs/bringup.md. Yosys reports its usual limited tri-state-support warning for MISO; the top-level pad is routed successfully and must be checked on the board.

The report is rendered and local navigation checked as part of delivery. Course-final evidence remains outstanding: actual parts and quotes, CAD schematics, measured results, team biographies, photographs, demo video, instructor checkoff, and publication. See docs/checkoff.md for the proposed test matrix.
