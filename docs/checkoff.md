# Specification and evidence record

Hardware results remain untested as of 2026-10-26. These entries follow the revised Word proposal's shared-control option 2. A finite run supports a continuous-operation assessment but cannot establish indefinite operation by itself.

| ID | Proposal target or implementation check | Verification | Status |
|---|---|---|---|
| S1 | Sustainable suspension of a permanent magnet with ballast | Extended run through thermal equilibrium; video, current and independent gap trace | Hardware not tested |
| S2 | Visible commanded motion, maximum gap 10 mm | Ruler/camera reference; report actual gap and speed across validated interval | Hardware not tested |
| S3 | Bounded current request and stable inner feedback | Meter/scope versus target across allowed range | PI simulation passed; hardware not tested |
| S4 | 20 kHz PWM, 5 kHz ADC scans/current updates | Scope shared SPI chip selects, accepted-packet debug, and PWM | Integration simulation passed; hardware not tested |
| S5 | 1 kHz position control while serving pages | Measure worst-case DMA/control ISR time, including every fifth scan, under web load | Runtime unit tests passed; hardware not tested |
| S6 | Current-compensated position sensing with one or two Hall sensors | Independent holdout sweeps; report residuals and transient error | Calibration algorithms tested; no measurements |
| S7 | Lost/frozen commands remove drive after 50 ms nominal plus clock tolerance | Halt MCU / repeat exact packets; scope gate and current decay separately | Integration simulation passed; hardware not tested |
| S8 | External trip, reset, and permit loss disable drive | Open interlock/reset at several PWM phases | Integration simulation passed; hardware not tested |
| S9 | Web changes bounded gap, selects supported current test, shows state, and stops | On-board ESP8266/MCU demonstration | C behavior tested; hardware not tested |
| S10 | Electrical/thermal limits permit continuous operation | Coil temperature, switch/clamp/shunt ratings, supply and current measurements | Hardware not tested |

Preserve configuration hash, wiring revision, measurement conditions, uncertainty, actual results, and reasons for any unmet target. Current FPGA gains and the example 8-10 mm interval/speed limits must be replaced with validated values before commissioning. See [verification](verification.md) for the software checks and their limits.
