# Graph Report - macroprocessors  (2026-11-15)

## Corpus Check
- 178 files · ~219,680 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 304 file(s) not represented in the graph (top: .step 175, .stl 67, .sat 32)

## Summary
- 781 nodes · 1403 edges · 68 communities (46 shown, 22 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 73 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `eff096d7`
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
- native_audit.py
- Build, simulate, and program
- build_adjustable.py
- about.qmd
- Proposal baseline and demonstration specifications
- build_purchased.py
- index.qmd
- tb_system
- progress.qmd
- Hall-sensed magnetic levitation — ENGR 155
- check-site.mjs
- build_three_print.py
- index.qmd
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
- CAD input evidence — November 10, 2026
- Independent review — purchased-parts version
- Magnetic levitation stand — testbox1 box
- Independent review — three-print PLA version
- Testbox1 box — three printed parts
- Implementation and control design
- pwm_20khz_core
- Exported-file review — front #6-32 Hall rod
- Hall/current calibration and controller tuning
- Communication contract v2
- Exported-file check report — direct-insertion common Hall rod
- Confirmed purchased parts — November 11, 2026
- Verification record - 2026-10-26
- Overleaf package
- Hardware basis — front Hall holder revision
- ENGR 155 deliverables and evidence map
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

## God Nodes (most connected - your core abstractions)
1. `run()` - 19 edges
2. `build()` - 14 edges
3. `main()` - 14 edges
4. `MCU-FPGA SPI wiring, communication, and debugging` - 14 edges
5. `prepare()` - 13 edges
6. `main()` - 13 edges
7. `build()` - 12 edges
8. `P()` - 12 edges
9. `box()` - 12 edges
10. `build()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `MCU: SEGGER project integration` --references--> `SysTick_Handler()`  [INFERRED]
  docs/build.md → firmware/src/board_stm32l432.c
- `MCU: SEGGER project integration` --references--> `board_init()`  [INFERRED]
  docs/build.md → firmware/src/board_stm32l432.c
- `MCU: SEGGER project integration` --references--> `TIM6_DAC_IRQHandler()`  [INFERRED]
  docs/build.md → firmware/src/board_stm32l432.c
- `MCU: SEGGER project integration` --references--> `DMA1_Channel2_IRQHandler()`  [INFERRED]
  docs/build.md → firmware/src/board_stm32l432.c
- `main()` --calls--> `lev_control_init()`  [INFERRED]
  tests/test_firmware.c → firmware/src/control.c

## Import Cycles
- None detected.

## Communities (68 total, 22 thin omitted)

### Community 0 - "math"
Cohesion: 0.06
Nodes (36): key(), norm(), repair(), box(), ck(), collisions(), cyl(), iv() (+28 more)

### Community 1 - "main"
Cohesion: 0.09
Nodes (22): clampf(), lev_arm(), lev_control_init(), lev_control_step(), lev_stop(), slew(), get16(), lev_crc16() (+14 more)

### Community 2 - "cadquery"
Cohesion: 0.06
Nodes (50): add(), box(), build(), cyl(), export(), hole(), slots_z(), bounds() (+42 more)

### Community 3 - "json"
Cohesion: 0.05
Nodes (16): label(), label(), label(), label(), run(), main(), render(), label() (+8 more)

### Community 4 - "Fusion_Front632.py"
Cohesion: 0.13
Nodes (29): run(), norm(), scan(), add_temp_component(), all_bodies(), baseline(), bb(), belt() (+21 more)

### Community 5 - "board_stm32l432.c"
Cohesion: 0.09
Nodes (28): MCU: SEGGER project integration, adc_start(), af(), board_init(), board_lock(), board_permit(), board_rx(), board_start_sampling() (+20 more)

### Community 6 - "MCU-FPGA SPI wiring, communication, and debugging"
Cohesion: 0.05
Nodes (35): Candidate hardware and proposed wiring, Logic wiring, Parts and early decision, Power circuit connectivity, 10. Instruments and debug information, 11. What must change in the existing implementation, 12. Proposal inconsistencies to keep separate from implementation, 1. What each device does (+27 more)

### Community 7 - "results.qmd"
Cohesion: 0.09
Nodes (21): Current Architecture, Gap and Position Control, Implementation Status, Resolution and Calibration, Stability Calculation, Earlier implementation reference, Earlier implementation reference, Earlier implementation reference (+13 more)

### Community 8 - "native_audit.py"
Cohesion: 0.22
Nodes (21): bbox(), box(), check_free(), ck(), collision_pairs(), copy(), cyl(), diff() (+13 more)

### Community 9 - "Build, simulate, and program"
Cohesion: 0.29
Nodes (6): Build, simulate, and program, FPGA, Host checks, MCU: GNU Arm toolchain, Portfolio, Web controls

### Community 10 - "build_adjustable.py"
Cohesion: 0.23
Nodes (16): add(), bed_transform(), bounds(), box(), build(), cyl(), export(), hall_ref() (+8 more)

### Community 11 - "about.qmd"
Cohesion: 0.13
Nodes (13): Acknowledgements, Authors, Ben Lertwachara, Stephen Kanti Mahanty, The Project, Website, Project Implementation, Reviewing the Work (+5 more)

### Community 12 - "Proposal baseline and demonstration specifications"
Cohesion: 0.40
Nodes (4): Committed demonstration, Design and calculations, Proposal baseline and demonstration specifications, Sources and planning

### Community 13 - "build_purchased.py"
Cohesion: 0.28
Nodes (12): add(), bed_transform(), bounds(), box(), build(), cyl(), export(), hall_ref() (+4 more)

### Community 14 - "index.qmd"
Cohesion: 0.18
Nodes (8): Current bench implementation, Data path and integration, Feedback and earlier HDL, PWM experiment, Bring-up progress, Current bench role, Earlier application sources, Position estimation and hardware webpage

### Community 15 - "tb_system"
Cohesion: 0.13
Nodes (8): top, lev_core, top, tb_system, command, read_adc, rejected, transfer

### Community 16 - "progress.qmd"
Cohesion: 0.14
Nodes (12): Current progress report — November 15, 2026, Earlier planning framework, Code written and next integration steps, Electromagnet and PWM testing, Electromagnet drive, Hall sensing, Hall sensors, ADC, and data width, Mechanical design and fabrication (+4 more)

### Community 17 - "Hall-sensed magnetic levitation — ENGR 155"
Cohesion: 0.50
Nodes (4): Earlier application implementation, Hall-sensed magnetic levitation — ENGR 155, Repository map, Start here

### Community 18 - "check-site.mjs"
Cohesion: 0.17
Nodes (7): collect(), content, issues, pages, root, rings, windings

### Community 19 - "build_three_print.py"
Cohesion: 0.35
Nodes (9): add(), bed_transform(), bounds(), box(), build(), cyl(), export(), hole() (+1 more)

### Community 20 - "index.qmd"
Cohesion: 0.20
Nodes (8): Assembled test setup, Characterization still required, Components in the current work, Current schematic, Authors, Documentation, Introduction, Project Status - November 15, 2026

### Community 21 - "E155 Magnetic Levitation — Quarto website"
Cohesion: 0.40
Nodes (4): Build and preview, Design and verification, E155 Magnetic Levitation — Quarto website, Edit the site

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
Cohesion: 0.25
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

### Community 40 - "Hall/current calibration and controller tuning"
Cohesion: 0.40
Nodes (4): Fit and validate, Gains and practical limits, Hall/current calibration and controller tuning, Measurements

### Community 41 - "Communication contract v2"
Cohesion: 0.50
Nodes (4): Communication contract v2, Eight-byte frames, ESP8266 to MCU, Shared MCU SPI bus

### Community 42 - "Exported-file check report — direct-insertion common Hall rod"
Cohesion: 0.50
Nodes (3): Confirmed geometry, Exported-file check report — direct-insertion common Hall rod, Interpretation and installation limits

### Community 43 - "Confirmed purchased parts — November 11, 2026"
Cohesion: 0.50
Nodes (3): Assembly interpretation, Confirmed purchased parts — November 11, 2026, Hall-sensor primary reference

### Community 44 - "Verification record - 2026-10-26"
Cohesion: 0.67
Nodes (3): Executed checks, Limits, Verification record - 2026-10-26

### Community 45 - "Overleaf package"
Cohesion: 0.50
Nodes (3): Important interpretation of the calculation, Overleaf package, What changed in the LaTeX proposal

### Community 58 - "README.md"
Cohesion: 0.25
Nodes (3): Current specification and evidence record, Proposal baseline, Design references

## Knowledge Gaps
- **11 isolated node(s):** `spi_word_tx`, `check_frames`, `crc48`, `current_pi`, `spi_frame` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 350 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Build, simulate, and program` connect `Build, simulate, and program` to `board_stm32l432.c`?**
  _High betweenness centrality (0.261) - this node is a cross-community bridge._
- **What connects `spi_word_tx`, `check_frames`, `crc48` to the rest of the system?**
  _11 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `math` be split into smaller, more focused modules?**
  _Cohesion score 0.055130784708249496 - nodes in this community are weakly interconnected._
- **Why does `MCU: SEGGER project integration` connect `board_stm32l432.c` to `Build, simulate, and program`?**
  _High betweenness centrality (0.259) - this node is a cross-community bridge._
- **Should `main` be split into smaller, more focused modules?**
  _Cohesion score 0.09219858156028368 - nodes in this community are weakly interconnected._
- **Why does `main()` connect `board_stm32l432.c` to `main`?**
  _High betweenness centrality (0.251) - this node is a cross-community bridge._
- **Should `cadquery` be split into smaller, more focused modules?**
  _Cohesion score 0.0639386189258312 - nodes in this community are weakly interconnected._