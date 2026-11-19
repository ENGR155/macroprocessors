# Hall-sensed magnetic levitation — ENGR 155

**Report update - November 15, 2026:** CAD has been iterated, the printed setup assembled, parts received, Hall sensors wired to the MCP3204 and tested, and the electromagnet exercised with MOSFET-driven sweeping PWM. The current bench setup uses FPGA-owned ADC SPI and a separate MCU-to-FPGA SPI readout; 16-bit live readout and feedback integration remain in progress. See the new [progress report](progress.qmd), [current design](design.qmd), [hardware](hardware.qmd), and [results](results.qmd), including updated schematics and CAD illustrations. The full application described below is an earlier implementation and is not the current bench configuration.

**Live bench monitor.** The STM32 supplies FPGA position data over UART to the ESP8266, which serves the JavaScript dashboard. The [wiring and setup guide](web_monitor/README.md) covers flashing both boards, the position scale, CSV export, and connecting a PID controller.

## Earlier application implementation

Earlier shared-control option 2, for one overhead electromagnet and a suspended permanent magnet with ballast, using the **STM32L432KC + UPduino v3.1** course boards. The browser changes a downward gap setpoint; the MCU estimates gap and runs a 1 kHz position controller; the MCU samples current and one or two Hall channels at 5 kHz with SPI DMA; the FPGA runs a 5 kHz current PI loop, generates 20 kHz PWM, and supervises output independently. The original Word proposal is absent from this checkout; see the [available proposal record](docs/proposal.qmd).

**Status, 2026-10-26:** software/HDL implementation and bench plan; no hardware has been selected, assembled, or tested. Default builds cannot energize the coil. Example limits, geometry, calibration, and gains require measurements. See [verification](docs/verification.md) for executed checks and remaining validation.

The revised design uses one shared 1 MHz MCU SPI bus with separate ADC/FPGA chip selects, 8-byte measured/requested-current packets, a 50 ms FPGA watchdog, and a 10 mm gap ceiling. Read [the updated design](docs/design.md) and [wire contract](docs/protocol.md) before building; both devices must be rebuilt together.

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
| `fpga/rtl` | 8-byte SPI command receiver, fixed-point PI, PWM/fault supervisor, oscillator wrapper |
| `fpga/constraints/upduino.pcf` | Proposed pad assignment for explicit jumpers |
| `fpga/tb`, `tests` | Shared-bus integration/PI testbenches and host-side C/Python tests |
| `tools/calibrate.py` | Offline Hall calibration with independent holdout validation |
| `hardware/bom.csv`, `hardware/netlist.md` | Candidate parts, budget allowances, circuit connectivity |
| `docs` | Implementation, experiments, schedule, and course deliverables |
| `*.qmd`, `_quarto.yml`, `assets` | Quarto project website, theme settings, and navigation |
| `data/results` | Measurement log schema; no fabricated measurements |

The report site can be rendered with `quarto render` and checked with `node tools/check-site.mjs`. See [website editing and preview](WEBSITE.md) for the page map and workflow. The `gh-pages` branch contains a prior website build; a local render does not publish changes. Current CAD illustrations and schematics are included, while assembly photographs, calibrated traces, and a levitation demonstration video remain to be added.

Codex state, `AGENTS.md`, scratch folders, build outputs, and local environment files are ignored. Firmware, HDL, documentation, and tests remain trackable. See [references](docs/references.md) for course and manufacturer sources.
