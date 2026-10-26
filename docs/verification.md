# Verification record - 2026-10-26

This record applies to the implementation of the updated Word proposal's shared-control option 2. It supersedes the former FPGA-owned ADC/16-byte protocol measurements.

## Executed checks

| Check | Result and scope |
|---|---|
| Native C, warnings treated as errors | Passed with Zig 0.16.0 / Clang on Windows |
| Firmware behavior and runtime | Passed: CRC known vector/corruption, 8-byte packet layout, retention of local ADC data, paired measured current, every-fifth-scan position updates, previous-command ACK, 8-bit sequence wrap, missed sample deadline, browser lease and timestamp wrap, stale-data arming refusal, direction, anti-windup, slew, velocity ceiling, one/two-Hall rails, 10 mm web bound, exact routes, and HTML bounds |
| Cortex-M4F source compilation | All eight C translation units compiled with warnings as errors using the course STM32L432/CMSIS headers and installed embedded runtime headers |
| FPGA integration simulation | Passed with Icarus Verilog 13.0: shared 1 MHz bus and separate ADC/FPGA chip selects, CH0/CH1/CH2 commands/data, one/two-Hall scans, 64-clock frames and telemetry CRC/ACK, paired-current PI/PWM, STOP, permit/external-fault gating, malformed/short/long/out-of-range frames, repeated IDs, sequence wrap, 50 ms watchdog, sampled overcurrent, safe fault clear, and default commissioning lockout |
| Current PI simulation | Passed: exact Q8.8 arithmetic, accumulated integral, signed error, duty saturation, conditional anti-windup/unwinding, and disable/history reset |
| Calibration | Five NumPy tests passed: two-Hall affine fit, one-Hall/current fit, one-Hall CSV without CH2, rejection of indistinguishable signals, and inadequate nonlinear residuals |
| FPGA enabled top level | Synthesized and routed for iCE40UP5K-SG48 with supplied constraints; 1099/5280 logic cells, 2/8 DSP blocks; routed internal clock estimate 46.59 MHz, passing the 24 MHz requirement |
| FPGA default disabled top level | Synthesized and routed separately; 644/5280 logic cells, 0/8 DSP blocks; routed internal clock estimate 52.99 MHz, passing 24 MHz |

The enabled FPGA check overrides `top.COMMISSIONED=1`, `top.CURRENT_KP_Q8=256`, and `top.CURRENT_KI_Q8=16` before synthesis. These are verification gains, not calibrated plant settings. Shipped source defaults remain disabled with zero gains. The arithmetic simulation uses those same nonzero test gains. Tools: YoWASP Yosys 0.70 and nextpnr-ice40 0.11.1.

Run `./tests/run.ps1` with GCC, Icarus/VVP, Python, and NumPy available; compiler/simulator paths can be supplied as parameters. The script runs firmware tests, both HDL benches, and calibration tests. The MCU source compilation additionally needs the course CMSIS/device headers and embedded C runtime. Build logs/tool downloads remain in ignored `build/`.

## Limits

No boards or instruments were attached. Source compilation is not a full GNU Arm runtime link or verified flash image. Timer/DMA interrupt execution, real SPI setup/hold, 200 us completion time including CRC and every-fifth-scan control work, ADC aperture skew, analog behavior, and physical shutdown latency require scope checks. Foreground HTML processing is separated from interrupt control, but actual interrupt execution time is not established by host tests.

The HDL bench models an MCU performing ADC transactions on the shared bus and supplying the resulting current code. It does not execute the STM32 machine code or model the levitation plant. The 50 ms watchdog is checked against 1200000 FPGA clocks; physical tolerance depends on the actual oscillator. FPGA timing/resource figures are tool estimates with test gains. Yosys reports its limited internal tri-state support warning; the top-level MISO pad routes, and its bus release is tested in simulation and still needs hardware verification.

No lift, indefinite suspension, visible motion, gap accuracy, coil heating, current calibration, or continuous-duty rating has been demonstrated. The example 8-10 mm interval, 1 mm/s slew, 10 mm/s filtered velocity ceiling, current limits, and control gains need measured validation. Complete [bring-up](bringup.md) and [the evidence record](checkoff.md) before commissioning.

The requested `graphify update .` was attempted; the installed launcher fails with `uv trampoline failed to canonicalize script path`. No graph refresh is claimed. Project analysis and checks used the actual source files.
