# Design references

Accessed 2026-10-15 unless noted. Manufacturer datasheets govern electrical limits; links identify candidate hardware, not approved purchases.

1. HMC E155, [Project](https://hmc-e155.github.io/project/) and [Final project requirements](https://hmc-e155.github.io/project/final-project-requirements.html). Scope and deliverables; confirm dates/budget with instructors.
2. HMC E155, [proposal](https://hmc-e155.github.io/project/specs/project-proposal-specs.html), [presentation](https://hmc-e155.github.io/project/specs/project-design-review-presentation-specs.html), [midpoint](https://hmc-e155.github.io/project/specs/project-midpoint-specs.html), [checkoff](https://hmc-e155.github.io/project/specs/project-checkoff-specs.html), and [portfolio](https://hmc-e155.github.io/project/specs/project-final-report-specs.html) rubrics.
3. HMC E155, [Lab 6: IoT and SPI](https://hmc-e155.github.io/lab/lab6/). Course ESP8266 UART/HTML protocol. The user called this Lab 7; the linked public course edition labels it Lab 6.
4. HMC E155, [Resources](https://hmc-e155.github.io/resources/) and [development board schematic](https://hmc-e155.github.io/assets/doc/E155%20Development%20Board%20Schematic.pdf). Board identities, labels, and routing reference.
5. STMicroelectronics, [STM32L432KC datasheet](https://hmc-e155.github.io/assets/doc/ds11451-stm32l432kc.pdf); RM0394 reference manual linked from the course resources. Register definitions were compile-checked against the local course CMSIS headers.
6. Lattice, [iCE40 oscillator usage guide](https://hmc-e155.github.io/assets/doc/FPGA-TN-02008-1-7-iCE40-Oscillator-Usage-Guide.pdf). Nominal 24 MHz oscillator and Yosys/Radiant primitive naming.
7. Microchip, [MCP3204/MCP3208 datasheet, DS21298E](https://ww1.microchip.com/downloads/en/DeviceDoc/21298e.pdf). Mode-0 conversion framing, acquisition, voltage and timing limits.
8. Texas Instruments, [DRV5055 datasheet](https://www.ti.com/lit/ds/symlink/drv5055.pdf). Linear analog Hall response, sensitivity, supply and bandwidth.
9. Texas Instruments, [INA240 datasheet](https://www.ti.com/lit/ds/symlink/ina240.pdf). Inline current-amplifier characteristics and PWM rejection.
10. Texas Instruments, [UCC2751x datasheet](https://www.ti.com/lit/ds/symlink/ucc27511.pdf). Candidate low-side gate driver.
11. Uzzors2k, [Magnetic levitation](http://uzzors2k.com/index.php?page=magneticlevitation). User-supplied inspiration. This page repeatedly timed out during research; its exact circuit, component ratings, and performance were **not verified or copied**. This repository's digital control and sensing design is independently specified.

Code in this repository was prepared with Codex assistance and requires team review, measured tuning, and course-policy compliance. It contains no claimed laboratory observations. Acknowledge actual collaborators and course assistance in the final portfolio.
