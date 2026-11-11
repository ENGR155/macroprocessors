# Current specification and evidence record

Updated November 10, 2026 from the revised LaTeX proposal and project discussions. All levitation and revised-controller acceptance checks remain pending.

| ID | Commitment | Evidence | Status |
|---|---|---|---|
| P1 | 10 g total moving mass; five webpage-commanded 20–10–20 mm round trips without contact | Mass measurement, ruler/camera, uninterrupted video | Not demonstrated |
| E1 | Five round trips reaching within ±5 mm of each requested gap | Independent endpoint gap readings | Not demonstrated |
| P2 | Real-time requested/estimated gap graph, current, and fault state; no visible latency | Webpage and physical motion shown together; measured latency | Not demonstrated |
| P3 | Update position PI constants from the webpage | Accepted gains and coordinated application at update boundary | Not demonstrated |
| E2 | Visibly noticeable webpage-controlled movement across the controllable range | Motion demonstration | Not demonstrated |

Excellence includes proficiency. These reproduce the [current proposal](proposal.qmd), rather than the earlier shared-control implementation criteria.

Additional engineering validation covers sensor resolution and independent holdout accuracy, 5 kHz acquisition/1 kHz estimation and control/20 kHz PWM, current and thermal limits, and direct E-stop/overcurrent shutdown. Verify the proposed 50 ms valid-command watchdog separately from current decay. The simple SPI byte reception is progress on communication, not acceptance of the complete controller.

Keep the wiring revision, firmware/HDL version, configuration, conditions, instrument uncertainty, and raw data with each result. See [Results](../results.qmd) and the [earlier application verification](verification.md).
