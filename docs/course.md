# ENGR 155 deliverables and evidence map

Reviewed the [project requirements](https://hmc-e155.github.io/project/final-project-requirements.html) and linked rubrics on 2026-10-15. Confirm the current year's dates and purchasing policy with the instructors: the posted calendar includes specific month/day entries without establishing that they are this year's schedule, and the budget section is marked under construction.

| Course item | Prepared here | Still requires team/hardware work |
|---|---|---|
| Proposal: concise design, measurable commitment, division of work, budget, calculations, interfaces | docs/proposal.md; design.md; hardware/bom.csv | Feasibility measurements, exact parts/prices, named owners, instructor review; paginate to the stated limit |
| Design review: overview plus a specific unsolved technical problem | docs/design-review.md | Team presentation and discussion |
| Midpoint: working hardware progress, circuit/logic/routine documentation | docs/midpoint.md; design.md; hardware/netlist.md | Real working demonstration, CAD schematic, factual status |
| Checkoff: specification-by-specification outcome with technical evidence | docs/checkoff.md | Execute and explain every acceptance test |
| Final portfolio: reproducible design, source, new hardware, results, references, team and acknowledgements | index.qmd; docs; firmware; fpga | Final CAD, data, photos/video, bios, acknowledgements, publication |

Both the MCU and FPGA have nontrivial roles. The Hall sensors, external ADC, power switch/current sensing, and cascaded control are the new hardware/system elements. Timer-based scheduling, calibrated estimation, and independent HDL supervision provide technical content beyond a web slider and PWM pin.

The [proposal rubric](https://hmc-e155.github.io/project/specs/project-proposal-specs.html), [midpoint rubric](https://hmc-e155.github.io/project/specs/project-midpoint-specs.html), [checkoff rubric](https://hmc-e155.github.io/project/specs/project-checkoff-specs.html), and [final portfolio rubric](https://hmc-e155.github.io/project/specs/project-final-report-specs.html) remain authoritative. They do not make unmeasured specifications successful. Keep results factual and source code readable. Follow the linked general lab documentation guidance for circuit labels, readable figures, and technical explanation.

## Relative six-week work plan

Role A is the sensor/control lead; Role B is the power/FPGA lead. Assign actual team names before submitting; both review integration and evidence. Adapt week boundaries to verified course deadlines.

| Week | Role A | Role B | Dependency / exit |
|---|---|---|---|
| 1 | Hall/object observability experiments, 6 h | Coil force/thermal characterization, 6 h | Usable object/gap/current interval; freeze proposal scope |
| 2 | MCU UART/SPI and independent current scaling, 5 h | ADC/PWM/interlock on supported load, 7 h | Digital captures and physical cutoff verified |
| 3 | Current calibration logging and web checks, 5 h | Quantized current PI tuning, 6 h | Stable measured current response |
| 4 | Hall holdout calibration and supported PD tuning, 8 h | Sensor timing/noise and current-decay improvements, 6 h | Riskiest sensing/control problem demonstrated at midpoint |
| 5 | Expand/test commanded gap interval, 6 h | Disturbance/fault/thermal tests, 6 h | All agreed performance targets evaluated |
| 6 | Quantitative results, portfolio, 6 h | Final CAD, photos/video, 6 h | Reproducible final checkoff and published team report |

Do not order extra channels or expand to two levitators before the single-object sensing and stability gates pass.
