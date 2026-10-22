# Hall-sensed magnetic levitation — ENGR 155

Implementation design for one overhead electromagnet and one suspended magnetic object, using the **STM32L432KC + UPduino v3.1** course boards. The browser changes a downward gap setpoint; the MCU estimates gap and runs a 1 kHz position controller; the FPGA acquires three analog channels, runs a 10 kHz current PI loop, generates 20 kHz PWM, and supervises output independently.

**Status, 2026-10-15:** software/HDL implementation and bench plan; no hardware has been selected, assembled, or tested. Default builds cannot energize the coil. Example limits, geometry, calibration, and gains require measurements. See [verification](docs/verification.md) for executed checks and remaining validation.

## Start here

1. Read [design and timing](docs/design.md), then [hardware and wiring](docs/hardware.md).
2. Choose and characterize the object/coil/sensors using [bring-up](docs/bringup.md). Hall observability is the first experiment.
3. Follow [build and programming](docs/build.md). The existing course ESP8266 firmware is used unchanged.
4. Use [calibration](docs/calibration.md), then tune the inner loop before the outer loop.
5. Track deliverables with [course requirements](docs/course.md), [proposal](docs/proposal.md), and [checkoff](docs/checkoff.md).

## Repository map

| Location | Contents |
|---|---|
| `firmware/src` | CMSIS board driver, main scheduler, height controller, packet codec, embedded HTML |
| `firmware/include/config.h`, `firmware/src/config.c` | Measured scaling, local Hall model, controller gains, current/gap bounds |
| `fpga/rtl` | SPI command receiver, MCP3204 sequencer, fixed-point PI, PWM/fault supervisor, oscillator wrapper |
| `fpga/constraints/upduino.pcf` | Proposed pad assignment for explicit jumpers |
| `fpga/tb`, `tests` | Integration testbench and host-side C/Python tests |
| `tools/calibrate.py` | Offline Hall calibration with independent holdout validation |
| `hardware/bom.csv`, `hardware/netlist.md` | Candidate parts, budget allowances, circuit connectivity |
| `docs` | Implementation, experiments, schedule, and course deliverables |
| `*.qmd`, `_quarto.yml`, `assets` | Quarto project website, theme settings, and navigation |
| `data/results` | Measurement log schema; no fabricated measurements |

The report site can be rendered with `quarto render` and checked with `node tools/check-site.mjs`. See [website editing and preview](WEBSITE.md) for the page map and workflow. Enable GitHub Pages only after reviewing the contents and adding actual results, team details, CAD schematics, photographs, and a demo video. The project has not been published.

Codex state, `AGENTS.md`, scratch folders, build outputs, and local environment files are ignored. Firmware, HDL, documentation, and tests remain trackable. See [references](docs/references.md) for course and manufacturer sources.
