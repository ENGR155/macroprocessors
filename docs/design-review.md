# Design review speaking outline

Use the [course presentation rubric](https://hmc-e155.github.io/project/specs/project-design-review-presentation-specs.html). This is content for a 10-minute team review, not a slide deck or a completed presentation.

| Time | Content / visual |
|---|---|
| 0:00–1:00 | Show desired suspension and commanded vertical motion; define downward gap |
| 1:00–3:00 | Present measurable targets and the MCU/FPGA/interface block diagram |
| 3:00–5:00 | Explain Hall mixing: object field + coil field, sequential ADC apertures, current transients |
| 5:00–7:00 | Show the actual clamped-object calibration sweeps and residuals when available; discuss estimator conditioning |
| 7:00–9:00 | Ask classmates to compare improving sensor placement versus restricting the interval; solicit specific sampling/model suggestions |
| 9:00–10:00 | State the next experiment and take questions |

Technical question: **How can we detect whether a compensated Hall estimate is responding to object motion or merely to changing coil current?** Hold position fixed during a measured current step, then compare transient apparent motion against the true motion sensitivity/noise floor. Discuss whether alternate placement, filtering, or timing reduces this error without destabilizing the position loop. Include real data when it exists; no illustrative curve should be labeled a measurement.
