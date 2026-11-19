# Graph Report - macroprocessors  (2026-11-17)

## Corpus Check
- 251 files · ~3,169,086 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 315 file(s) not represented in the graph (top: .step 175, .stl 67, .sat 32)

## Summary
- 2001 nodes · 4225 edges · 105 communities (76 shown, 29 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 260 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `77892990`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- math
- main
- cadquery
- json
- Fusion_Front632.py
- board_stm32l432.c
- MCU-FPGA SPI wiring, communication, and debugging
- results.qmd
- cmsis_gcc.h
- Build, simulate, and program
- build_adjustable.py
- about.qmd
- cmsis_armclang_ltm.h
- build_purchased.py
- index.qmd
- tb_system
- progress.qmd
- Hall-sensed magnetic levitation — ENGR 155
- test_dashboard.mjs
- build_three_print.py
- hardware.qmd
- E155 Magnetic Levitation — Quarto website
- Vertical Hall adjustment — revised jobs 2 and 3
- Front Hall rod with #6-32 hardware
- Purchased-parts design — three print jobs
- Staged bring-up and acceptance gates
- One byte from the FPGA to SEGGER
- Independent review — vertically adjustable Hall holders
- Direct-insertion common Hall rod — one holder print
- counter
- Independent CAD review — 10 November 2026
- __DSB
- CAD input evidence — November 10, 2026
- Independent review — purchased-parts version
- Magnetic levitation stand — testbox1 box
- Independent review — three-print PLA version
- Testbox1 box — three printed parts
- Implementation and control design
- pwm_20khz_core
- Exported-file review — front #6-32 Hall rod
- cmsis_armclang.h
- cmsis_compiler.h
- Exported-file check report — direct-insertion common Hall rod
- Confirmed purchased parts — November 11, 2026
- stdint
- Overleaf package
- Hardware basis — front Hall holder revision
- cmsis_iccarm.h
- tb_current_pi
- spi_byte.sv
- tb_spi_byte
- POSITIONING_NOTES.md
- NATIVE_IMPLEMENTATION_NOTES.md
- SOURCE_DIMENSIONS.md
- printed_version/README.md
- Design review speaking outline
- midpoint.md
- README.md
- spi_byte_tx.sv
- crc48.sv
- current_pi.sv
- spi_frame.sv
- core_cm85.h
- core_armv81mml.h
- core_cm55.h
- core_armv8mml.h
- core_cm33.h
- core_cm35p.h
- monitor.c
- core_armv8mbl.h
- core_cm23.h
- independent_adjustable_check.py
- calibrate.py
- cmsis_armcc.h
- core_cm3.h
- core_sc300.h
- core_cm0plus.h
- core_cm1.h
- pmu_armv8.h
- build_direct.py
- direct_insert_hall_version/purchased_geometry.py
- board_permit
- control.c
- lev_web_request
- check_direct.py
- board.h
- __PACKED_STRUCT
- __PACKED_STRUCT
- __ROR
- field_to_position.sv
- spi_word_tx.sv
- T_UINT32
- T_UINT32
- core_cm0.h
- web_server.cpp
- MicroPEs live position and PID monitor

## God Nodes (most connected - your core abstractions)
1. `__DSB()` - 96 edges
2. `__ISB()` - 75 edges
3. `run()` - 19 edges
4. `build()` - 14 edges
5. `main()` - 14 edges
6. `MCU-FPGA SPI wiring, communication, and debugging` - 14 edges
7. `prepare()` - 13 edges
8. `main()` - 13 edges
9. `build()` - 12 edges
10. `P()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `MCU: SEGGER project integration` --references--> `SysTick_Handler()`  [INFERRED]
  docs/build.md → firmware/src/board_stm32l432.c
- `MCU: SEGGER project integration` --references--> `TIM6_DAC_IRQHandler()`  [INFERRED]
  docs/build.md → firmware/src/board_stm32l432.c
- `MCU: SEGGER project integration` --references--> `DMA1_Channel2_IRQHandler()`  [INFERRED]
  docs/build.md → firmware/src/board_stm32l432.c
- `board_init()` --calls--> `__DSB()`  [INFERRED]
  firmware/src/board_stm32l432.c → mcu/CMSIS_5/CMSIS/Core/Include/cmsis_gcc.h
- `board_init()` --calls--> `__ISB()`  [INFERRED]
  firmware/src/board_stm32l432.c → mcu/CMSIS_5/CMSIS/Core/Include/cmsis_gcc.h

## Import Cycles
- None detected.

## Communities (105 total, 29 thin omitted)

### Community 0 - "math"
Cohesion: 0.13
Nodes (16): key(), norm(), repair(), key(), norm(), repair(), key(), norm() (+8 more)

### Community 1 - "main"
Cohesion: 0.19
Nodes (12): get16(), lev_crc16(), lev_pack(), lev_unpack(), put16(), lev_runtime_feedback(), cfg(), main() (+4 more)

### Community 2 - "cadquery"
Cohesion: 0.12
Nodes (30): add(), box(), build(), cyl(), export(), hole(), slots_z(), body() (+22 more)

### Community 3 - "json"
Cohesion: 0.10
Nodes (10): label(), label(), label(), label(), main(), render(), label(), label() (+2 more)

### Community 4 - "Fusion_Front632.py"
Cohesion: 0.08
Nodes (50): run(), norm(), scan(), add_temp_component(), all_bodies(), baseline(), bb(), belt() (+42 more)

### Community 5 - "board_stm32l432.c"
Cohesion: 0.22
Nodes (18): MCU: SEGGER project integration, adc_start(), af(), board_init(), board_lock(), board_rx(), board_tx(), board_unlock() (+10 more)

### Community 6 - "MCU-FPGA SPI wiring, communication, and debugging"
Cohesion: 0.07
Nodes (30): 10. Instruments and debug information, 11. What must change in the existing implementation, 12. Proposal inconsistencies to keep separate from implementation, 1. What each device does, 2. Connect the digital hardware, 3. Configure the SPI link, 4. Connect the ADC and the DRV5056 sensors, 5. Recommended replacement packet contract (+22 more)

### Community 7 - "results.qmd"
Cohesion: 0.09
Nodes (21): Current Architecture, Gap and Position Control, Implementation Status, Resolution and Calibration, Stability Calculation, Earlier implementation reference, Earlier implementation reference, Earlier implementation reference (+13 more)

### Community 8 - "cmsis_gcc.h"
Cohesion: 0.03
Nodes (131): __CLREX(), __CLZ(), __cmsis_start(), __disable_fault_irq(), __disable_irq(), __enable_fault_irq(), __enable_irq(), __get_APSR() (+123 more)

### Community 9 - "Build, simulate, and program"
Cohesion: 0.29
Nodes (6): Build, simulate, and program, FPGA, Host checks, MCU: GNU Arm toolchain, Portfolio, Web controls

### Community 10 - "build_adjustable.py"
Cohesion: 0.23
Nodes (16): add(), bed_transform(), bounds(), box(), build(), cyl(), export(), hall_ref() (+8 more)

### Community 11 - "about.qmd"
Cohesion: 0.13
Nodes (13): Acknowledgements, Authors, Ben Lertwachara, Stephen Kanti Mahanty, The Project, Website, Project Implementation, Reviewing the Work (+5 more)

### Community 12 - "cmsis_armclang_ltm.h"
Cohesion: 0.03
Nodes (114): __CLZ(), __disable_fault_irq(), __disable_irq(), __enable_fault_irq(), __enable_irq(), __get_APSR(), __get_BASEPRI(), __get_CONTROL() (+106 more)

### Community 13 - "build_purchased.py"
Cohesion: 0.28
Nodes (12): add(), bed_transform(), bounds(), box(), build(), cyl(), export(), hall_ref() (+4 more)

### Community 14 - "index.qmd"
Cohesion: 0.14
Nodes (12): Current bench implementation, Data path and integration, Feedback and earlier HDL, PWM experiment, Authors, Documentation, Introduction, Project Status - November 15, 2026 (+4 more)

### Community 15 - "tb_system"
Cohesion: 0.13
Nodes (8): top, lev_core, top, tb_system, command, read_adc, rejected, transfer

### Community 16 - "progress.qmd"
Cohesion: 0.11
Nodes (16): Current progress report — November 15, 2026, Earlier planning framework, Committed demonstration, Design and calculations, Proposal baseline and demonstration specifications, Sources and planning, Code written and next integration steps, Electromagnet and PWM testing (+8 more)

### Community 17 - "Hall-sensed magnetic levitation — ENGR 155"
Cohesion: 0.50
Nodes (4): Earlier application implementation, Hall-sensed magnetic levitation — ENGR 155, Repository map, Start here

### Community 18 - "test_dashboard.mjs"
Cohesion: 0.07
Nodes (20): collect(), content, issues, pages, root, unpublishedFolders, rings, windings (+12 more)

### Community 19 - "build_three_print.py"
Cohesion: 0.35
Nodes (9): add(), bed_transform(), bounds(), box(), build(), cyl(), export(), hole() (+1 more)

### Community 20 - "hardware.qmd"
Cohesion: 0.15
Nodes (9): Candidate hardware and proposed wiring, Logic wiring, Parts and early decision, Power circuit connectivity, Assembled test setup, Characterization still required, Components in the current work, Current schematic (+1 more)

### Community 21 - "E155 Magnetic Levitation — Quarto website"
Cohesion: 0.33
Nodes (5): Build and preview, Design and verification, E155 Magnetic Levitation — Quarto website, Edit the site, Publishing

### Community 22 - "Vertical Hall adjustment — revised jobs 2 and 3"
Cohesion: 0.22
Nodes (8): Actual height ranges, CAD and verification files, Files to print, Fitted Hall seats and moving wiring, Hardware and assembly, Preserved magnetic and payload assembly, Printing and supports, Vertical Hall adjustment — revised jobs 2 and 3

### Community 23 - "Front Hall rod with #6-32 hardware"
Cohesion: 0.22
Nodes (8): Files and printing, Front Hall rod with #6-32 hardware, Hardware sizing and assembly, Install and remove wired Hall sensors, Magnets above and below the electromagnet, Position adjustment, Sand the common rod to fit, What has and has not been established

### Community 24 - "Purchased-parts design — three print jobs"
Cohesion: 0.22
Nodes (8): Alternate helper location above the coil, D68 carrier and the 10 g moving assembly, Default helper stack below the coil, Deliverables and limits, Gap and hardware, Purchased dimensions used, Purchased-parts design — three print jobs, Sensor installation and soldering

### Community 25 - "Staged bring-up and acceptance gates"
Cohesion: 0.25
Nodes (8): 1. Establish sensing feasibility before a parts commitment, 2. Characterize coil and driver, 3. Verify digital paths with coil power disconnected, 4. Calibrate and prove the physical cutoff, 5. Tune the inner current loop, 6. Fit Hall calibration and tune the position loop, 7. Demonstrate and preserve evidence, Staged bring-up and acceptance gates

### Community 26 - "One byte from the FPGA to SEGGER"
Cohesion: 0.22
Nodes (8): 1. Carrier switches and pins, 2. FPGA: paste this entire file, 3. MCU: paste this as your only main, 4. See the printed byte in SEGGER, 5. See the variable directly, even without printf, 6. Prove that the displayed value comes from the FPGA, One byte from the FPGA to SEGGER, Verification performed

### Community 27 - "Independent review — vertically adjustable Hall holders"
Cohesion: 0.25
Nodes (7): Actual adjustment range, Geometry and motion verification, Independent review — vertically adjustable Hall holders, Printing and structural observations, Retained operating limits, Sensor mounting and wiring, What changed and what was preserved

### Community 28 - "Direct-insertion common Hall rod — one holder print"
Cohesion: 0.25
Nodes (7): Coarse positions and coupled movement, Direct-insertion common Hall rod — one holder print, How the sensor slides into the rod, Install and lock the common rod, Print files, Sensor retention without pinching the leads, Wiring, magnets and limits

### Community 29 - "counter"
Cohesion: 0.25
Nodes (4): adc_spi, counter, pwm, sweep_8bit

### Community 30 - "Independent CAD review — 10 November 2026"
Cohesion: 0.29
Nodes (6): Assembly and fabrication observations, Corrections required and verified during review, Independent CAD review — 10 November 2026, Independently verified geometry, Remaining limits that affect a one-shot build, Sources and interpretation

### Community 31 - "__DSB"
Cohesion: 0.05
Nodes (97): SCB_CleanDCache(), SCB_CleanDCache_by_Addr(), SCB_CleanInvalidateDCache(), SCB_CleanInvalidateDCache_by_Addr(), SCB_DisableDCache(), SCB_DisableICache(), SCB_EnableDCache(), SCB_EnableICache() (+89 more)

### Community 32 - "CAD input evidence — November 10, 2026"
Cohesion: 0.33
Nodes (5): CAD input evidence — November 10, 2026, External sources, Fusion destination, Project sources read, Purchase emails read

### Community 33 - "Independent review — purchased-parts version"
Cohesion: 0.33
Nodes (5): Actual export and printer checks, Fit, wiring and retention checks, Independent review — purchased-parts version, Payload mass and operating conditions, Purchased components checked

### Community 34 - "Magnetic levitation stand — testbox1 box"
Cohesion: 0.33
Nodes (5): Assembly and hardware, Fabrication and validation limits, Files, Magnetic levitation stand — testbox1 box, Verified dimensions and assumptions

### Community 35 - "Independent review — three-print PLA version"
Cohesion: 0.33
Nodes (5): Assembly and clearance, Conditional stiffness estimate, Geometry and print orientation, Independent review — three-print PLA version, Remaining release conditions

### Community 36 - "Testbox1 box — three printed parts"
Cohesion: 0.33
Nodes (5): CAD and evidence, Dimensions and motion, Mechanical assembly, Print these three files, Testbox1 box — three printed parts

### Community 37 - "Implementation and control design"
Cohesion: 0.40
Nodes (5): Current controller and shutdown, Implementation and control design, Position sensing and motion, Subsystems, Timing budget

### Community 38 - "pwm_20khz_core"
Cohesion: 0.40
Nodes (4): pwm_20khz_core, pwm_20khz_top, tb_pwm_20khz, check_frames

### Community 39 - "Exported-file review — front #6-32 Hall rod"
Cohesion: 0.40
Nodes (4): Checks performed on actual exports, Exported-file review — front #6-32 Hall rod, Practical limits, Review responsibilities

### Community 40 - "cmsis_armclang.h"
Cohesion: 0.05
Nodes (67): __CLZ(), __disable_fault_irq(), __disable_irq(), __enable_fault_irq(), __enable_irq(), __get_APSR(), __get_BASEPRI(), __get_CONTROL() (+59 more)

### Community 41 - "cmsis_compiler.h"
Cohesion: 0.08
Nodes (39): T_UINT16_READ(), T_UINT16_WRITE(), T_UINT32(), T_UINT32_READ(), T_UINT32_WRITE(), ITM_CheckChar(), ITM_ReceiveChar(), ITM_SendChar() (+31 more)

### Community 42 - "Exported-file check report — direct-insertion common Hall rod"
Cohesion: 0.50
Nodes (3): Confirmed geometry, Exported-file check report — direct-insertion common Hall rod, Interpretation and installation limits

### Community 43 - "Confirmed purchased parts — November 11, 2026"
Cohesion: 0.50
Nodes (3): Assembly interpretation, Confirmed purchased parts — November 11, 2026, Hall-sensor primary reference

### Community 44 - "stdint"
Cohesion: 0.08
Nodes (29): ITM_CheckChar(), ITM_ReceiveChar(), ITM_SendChar(), __NVIC_ClearPendingIRQ(), NVIC_DecodePriority(), __NVIC_EnableIRQ(), NVIC_EncodePriority(), __NVIC_GetActive() (+21 more)

### Community 45 - "Overleaf package"
Cohesion: 0.50
Nodes (3): Important interpretation of the calculation, Overleaf package, What changed in the LaTeX proposal

### Community 47 - "cmsis_iccarm.h"
Cohesion: 0.06
Nodes (51): __CLZ(), __get_APSR(), __get_MSPLIM(), __get_PSPLIM(), __iar_u32(), __iar_uint16_read(), __iar_uint16_write(), __iar_uint32_read() (+43 more)

### Community 58 - "README.md"
Cohesion: 0.09
Nodes (16): Fit and validate, Gains and practical limits, Hall/current calibration and controller tuning, Measurements, Current specification and evidence record, ENGR 155 deliverables and evidence map, Relative six-week work plan, Proposal baseline (+8 more)

### Community 69 - "core_cm85.h"
Cohesion: 0.08
Nodes (53): DCB_GetAuthCtrl(), DCB_SetAuthCtrl(), DIB_GetAuthStatus(), ITM_CheckChar(), ITM_ReceiveChar(), ITM_SendChar(), __NVIC_ClearPendingIRQ(), NVIC_ClearTargetState() (+45 more)

### Community 70 - "core_armv81mml.h"
Cohesion: 0.10
Nodes (45): DCB_GetAuthCtrl(), DCB_SetAuthCtrl(), DIB_GetAuthStatus(), ITM_CheckChar(), ITM_ReceiveChar(), ITM_SendChar(), __NVIC_ClearPendingIRQ(), NVIC_ClearTargetState() (+37 more)

### Community 71 - "core_cm55.h"
Cohesion: 0.10
Nodes (45): DCB_GetAuthCtrl(), DCB_SetAuthCtrl(), DIB_GetAuthStatus(), ITM_CheckChar(), ITM_ReceiveChar(), ITM_SendChar(), __NVIC_ClearPendingIRQ(), NVIC_ClearTargetState() (+37 more)

### Community 72 - "core_armv8mml.h"
Cohesion: 0.10
Nodes (44): DCB_GetAuthCtrl(), DCB_SetAuthCtrl(), DIB_GetAuthStatus(), ITM_CheckChar(), ITM_ReceiveChar(), ITM_SendChar(), __NVIC_ClearPendingIRQ(), NVIC_ClearTargetState() (+36 more)

### Community 73 - "core_cm33.h"
Cohesion: 0.10
Nodes (44): DCB_GetAuthCtrl(), DCB_SetAuthCtrl(), DIB_GetAuthStatus(), ITM_CheckChar(), ITM_ReceiveChar(), ITM_SendChar(), __NVIC_ClearPendingIRQ(), NVIC_ClearTargetState() (+36 more)

### Community 74 - "core_cm35p.h"
Cohesion: 0.10
Nodes (44): DCB_GetAuthCtrl(), DCB_SetAuthCtrl(), DIB_GetAuthStatus(), ITM_CheckChar(), ITM_ReceiveChar(), ITM_SendChar(), __NVIC_ClearPendingIRQ(), NVIC_ClearTargetState() (+36 more)

### Community 75 - "monitor.c"
Cohesion: 0.12
Nodes (21): board_init(), main(), read_fpga_word(), spi_reset(), uart_receive(), gain(), maglev_monitor_feed(), maglev_monitor_init() (+13 more)

### Community 76 - "core_armv8mbl.h"
Cohesion: 0.12
Nodes (37): DCB_GetAuthCtrl(), DCB_SetAuthCtrl(), DIB_GetAuthStatus(), __NVIC_ClearPendingIRQ(), NVIC_ClearTargetState(), NVIC_DecodePriority(), __NVIC_DisableIRQ(), __NVIC_EnableIRQ() (+29 more)

### Community 77 - "core_cm23.h"
Cohesion: 0.12
Nodes (37): DCB_GetAuthCtrl(), DCB_SetAuthCtrl(), DIB_GetAuthStatus(), __NVIC_ClearPendingIRQ(), NVIC_ClearTargetState(), NVIC_DecodePriority(), __NVIC_DisableIRQ(), __NVIC_EnableIRQ() (+29 more)

### Community 78 - "independent_adjustable_check.py"
Cohesion: 0.09
Nodes (14): box(), ck(), collisions(), cyl(), iv(), mesh(), orient_flat(), box() (+6 more)

### Community 79 - "calibrate.py"
Cohesion: 0.13
Nodes (6): run(), CalibrationTests, evaluate(), fit(), load(), main()

### Community 80 - "cmsis_armcc.h"
Cohesion: 0.14
Nodes (21): __get_APSR(), __get_BASEPRI(), __get_CONTROL(), __get_FAULTMASK(), __get_FPSCR(), __get_IPSR(), __get_MSP(), __get_PRIMASK() (+13 more)

### Community 81 - "core_cm3.h"
Cohesion: 0.19
Nodes (21): ITM_CheckChar(), ITM_ReceiveChar(), ITM_SendChar(), __NVIC_ClearPendingIRQ(), NVIC_DecodePriority(), __NVIC_DisableIRQ(), __NVIC_EnableIRQ(), NVIC_EncodePriority() (+13 more)

### Community 82 - "core_sc300.h"
Cohesion: 0.19
Nodes (21): ITM_CheckChar(), ITM_ReceiveChar(), ITM_SendChar(), __NVIC_ClearPendingIRQ(), NVIC_DecodePriority(), __NVIC_DisableIRQ(), __NVIC_EnableIRQ(), NVIC_EncodePriority() (+13 more)

### Community 83 - "core_cm0plus.h"
Cohesion: 0.25
Nodes (15): __NVIC_ClearPendingIRQ(), NVIC_DecodePriority(), __NVIC_DisableIRQ(), __NVIC_EnableIRQ(), NVIC_EncodePriority(), __NVIC_GetEnableIRQ(), __NVIC_GetPendingIRQ(), __NVIC_GetPriority() (+7 more)

### Community 84 - "core_cm1.h"
Cohesion: 0.25
Nodes (15): __NVIC_ClearPendingIRQ(), NVIC_DecodePriority(), __NVIC_DisableIRQ(), __NVIC_EnableIRQ(), NVIC_EncodePriority(), __NVIC_GetEnableIRQ(), __NVIC_GetPendingIRQ(), __NVIC_GetPriority() (+7 more)

### Community 85 - "pmu_armv8.h"
Cohesion: 0.23
Nodes (14): ARM_PMU_CNTR_Disable(), ARM_PMU_CNTR_Enable(), ARM_PMU_CNTR_Increment(), ARM_PMU_CYCCNT_Reset(), ARM_PMU_Disable(), ARM_PMU_Enable(), ARM_PMU_EVCNTR_ALL_Reset(), ARM_PMU_Get_CCNTR() (+6 more)

### Community 86 - "build_direct.py"
Cohesion: 0.19
Nodes (8): bounds(), export(), flat(), loop(), pins(), preserve(), ribbon(), slot_body()

### Community 87 - "direct_insert_hall_version/purchased_geometry.py"
Cohesion: 0.28
Nodes (12): add(), bed_transform(), bounds(), box(), build(), cyl(), export(), hall_ref() (+4 more)

### Community 88 - "board_permit"
Cohesion: 0.29
Nodes (4): board_permit(), board_start_sampling(), on_adc(), on_reply()

### Community 89 - "control.c"
Cohesion: 0.25
Nodes (8): clampf(), lev_arm(), lev_control_init(), lev_control_step(), lev_stop(), slew(), lev_runtime_init(), lev_runtime_sample()

### Community 91 - "check_direct.py"
Cohesion: 0.31
Nodes (6): b(), box(), ck(), cyl(), mesh(), sweep()

### Community 94 - "__PACKED_STRUCT"
Cohesion: 0.40
Nodes (4): T_UINT16_READ(), T_UINT16_WRITE(), T_UINT32_READ(), T_UINT32_WRITE()

### Community 95 - "__PACKED_STRUCT"
Cohesion: 0.40
Nodes (4): T_UINT16_READ(), T_UINT16_WRITE(), T_UINT32_READ(), T_UINT32_WRITE()

### Community 96 - "__ROR"
Cohesion: 0.40
Nodes (5): __ROR(), __SXTAB16(), __SXTAB16_RORn(), __SXTB16(), __SXTB16_RORn()

### Community 102 - "core_cm0.h"
Cohesion: 0.25
Nodes (15): __NVIC_ClearPendingIRQ(), NVIC_DecodePriority(), __NVIC_DisableIRQ(), __NVIC_EnableIRQ(), NVIC_EncodePriority(), __NVIC_GetEnableIRQ(), __NVIC_GetPendingIRQ(), __NVIC_GetPriority() (+7 more)

### Community 103 - "web_server.cpp"
Cohesion: 0.23
Nodes (5): exchange(), handlePid(), isWireNumber(), sendJson(), setup()

### Community 104 - "MicroPEs live position and PID monitor"
Cohesion: 0.25
Nodes (7): Flash the ESP8266, HTTP and UART, MicroPEs live position and PID monitor, Position and PID, Run it, Verification, Wire the boards

## Knowledge Gaps
- **16 isolated node(s):** `field_to_position`, `spi_word_tx`, `spi_word_tx`, `check_frames`, `crc48` (+11 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 409 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MCU: SEGGER project integration` connect `board_stm32l432.c` to `Build, simulate, and program`?**
  _High betweenness centrality (0.151) - this node is a cross-community bridge._
- **Are the 94 inferred relationships involving `__DSB()` (e.g. with `board_init()` and `SCB_CleanDCache()`) actually correct?**
  _`__DSB()` has 94 INFERRED edges - model-reasoned connections that need verification._
- **What connects `field_to_position`, `spi_word_tx`, `spi_word_tx` to the rest of the system?**
  _16 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `math` be split into smaller, more focused modules?**
  _Cohesion score 0.13012477718360071 - nodes in this community are weakly interconnected._
- **Why does `Build, simulate, and program` connect `Build, simulate, and program` to `board_stm32l432.c`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Are the 71 inferred relationships involving `__ISB()` (e.g. with `board_init()` and `SCB_CleanDCache()`) actually correct?**
  _`__ISB()` has 71 INFERRED edges - model-reasoned connections that need verification._
- **Should `cadquery` be split into smaller, more focused modules?**
  _Cohesion score 0.11740890688259109 - nodes in this community are weakly interconnected._