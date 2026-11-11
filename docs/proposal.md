# Current proposal and demonstration specifications

The revised [LaTeX proposal](../overleaf_10mm/proposal.pdf) and [source](../overleaf_10mm/proposal.tex) describe FPGA position PI driving PWM directly, with MCU ADC/DMA, gap estimation, and web communication. The earlier [Word proposal](../Project%20Proposal.docx) is retained as a historical source. Later project discussions selected the electromagnet and clarified the helper magnet; see [Hardware](../hardware.qmd).

## Committed demonstration

The magnet, carrier, and object total **10 g**. Surface gap is measured downward from the electromagnet's bottom face to the suspended magnet's top face. The commanded range is **10–20 mm**.

| Category | Level | Proposal specification |
|---|---|---|
| Hardware and levitation | Proficiency | Use the webpage to move from 20 to 10 mm and back five times without contact |
| Hardware and levitation | Excellence | Complete five 20-to-10 mm round trips, reaching within ±5 mm of each requested gap |
| Control and webpage | Proficiency | Show requested gap, estimated gap, coil current, and fault state on a real-time webpage graph, with no visible latency during demonstration |
| Control and webpage | Proficiency | Allow position PI constant updates from the webpage |
| Control and webpage | Excellence | Demonstrate visibly noticeable webpage-controlled motion across the controllable range |

Excellence includes all proficiency checks. These are commitments from the proposal, not completed tests. Check them with a ruler, stopwatch, webpage, and scope or logic analyzer as appropriate. Record quantitative latency even though the graph criterion is phrased visually.

## Design and calculations

Two Hall sensors are mounted above and below the electromagnet. The MCU reads them and current on separate ADC channels at 5 kHz using SPI DMA, estimates gap at 1 kHz, and serves the interface through the ESP8266. The FPGA runs 1 kHz position PI and 20 kHz PWM, with a proposed 50 ms command watchdog and independent external shutdown.

The [calculation summary](../overleaf_10mm/calculation_summary.pdf) distinguishes center distance from surface gap and identifies assumed coil parameters. The 10 mm example is a stability analysis point; it does not replace the proposal's 10–20 mm surface-gap motion specification. The air-core example neither validates the selected electromagnet nor supplies safe controller gains.

## Sources and planning

- [Complete Overleaf package](../Magnetic_Levitation_Overleaf_10mm.zip)
- [Revised proposal PDF](../overleaf_10mm/proposal.pdf) and [LaTeX](../overleaf_10mm/proposal.tex)
- [Calculation PDF](../overleaf_10mm/calculation_summary.pdf) and [LaTeX](../overleaf_10mm/calculation_summary.tex)
- Project discussions: “Create magnetic levitation textbook…” (architecture, position PI correction, selected hardware, and SPI bring-up); “Add lifting calculations and specs” (two sensors and physical checkoff); “Convert to LaTeX proposal” (position-resolution notes).

The proposal retains a $49 budget allowance and six-week schedule. Weeks 1–2 cover force/driver/PWM and ADC/calibration; weeks 3–4 cover FPGA PI, frame, estimator, and timing; weeks 5–6 cover the webpage, shutdown, motion evidence, and report. These are planned assignments, not a completion record.
