# Specification and evidence record

All hardware results below are **not tested** as of 2026-10-15. Replace status with a short factual explanation and evidence for each agreed specification before final checkoff. The candidate numerical targets must first be accepted in the proposal.

| ID | Proposed specification | Verification | Status |
|---|---|---|---|
| S1 | Suspend one magnetic object for ≥30 s | Continuous video plus actual gap/current trace | Not tested |
| S2 | Three targets within validated range, initially 8–14 mm | Independent gap reference; mean error ≤0.5 mm after settling | Not tested |
| S3 | Bounded current request and stable inner feedback | Meter/scope versus target across allowed range | Not tested |
| S4 | FPGA 20 kHz PWM and 10 kHz complete scans | Scope PWM and scan debug with actual ADC | Not tested |
| S5 | MCU 1 kHz control while serving pages | Measure maximum loop time and missed-tick behavior under web load | Not tested |
| S6 | Position model passes independent data | RMSE ≤0.25 mm, worst error ≤0.5 mm over accepted range | Not tested |
| S7 | Lost/frozen command removes drive within 20 ms nominal plus clock tolerance | Halt MCU / repeat exact packets; scope gate and current | Simulation passed; hardware not tested |
| S8 | External trip, reset, and permit loss disable drive | Open interlock/reset devices at several PWM phases | Simulation passed; hardware not tested |
| S9 | Web changes gap, selects supported current test, shows state, and stops | On-board ESP8266/MCU demonstration | C behavior tested; hardware not tested |
| S10 | Electrical/thermal limits hold for demonstration duration | Coil temperature, switch/clamp/current measurements | Not tested |

For each final specification, record what was demonstrated, the measurement conditions, uncertainty, any unmet part, and the reason. Bring source, schematics, block diagrams, build/configuration details, measurement plots, and completed explanations to the instructor checkoff. See the [checkoff rubric](https://hmc-e155.github.io/project/specs/project-checkoff-specs.html).
