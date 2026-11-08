# Overleaf package

Upload `Magnetic_Levitation_Overleaf_10mm.zip` with **New Project > Upload Project**.
Choose `proposal.tex` as the Main document for the proposal, or
`calculation_summary.tex` for the standalone calculation notes. Use pdfLaTeX.
Both files are complete documents. No BibTeX run or shell escape is required.
Compiled PDF previews are included in the ZIP's `previews` folder.

The proposal includes the vector figure with:

```latex
\includegraphics[width=\linewidth]{assets/system_architecture.pdf}
```

Keep the `assets` folder with the `.tex` files when uploading. The two PDF
previews are compiled from the corresponding `.tex` files.

## What changed in the LaTeX proposal

- The original Word file was read, not edited.
- The stability calculation now uses the nominal 10 mm center-distance
  calculation discussed in chat, with position PI driving duty directly.
- Related architecture, diagram, and schedule passages now consistently put
  position PI and PWM in the FPGA. There is no current-feedback controller.
- The MCU still performs ADC acquisition with DMA, the gap estimate, and the
  web interface through the ESP8266. Current is measured for compensation,
  telemetry, and protection.
- Hall sensors are above and below the coil. The live graph and PI-constant
  updates are included, as requested earlier in the conversation.
- Informal drafting reminders have been incorporated into the appropriate
  resolution, verification, and web-interface paragraphs.
- The project's mass, motion range, demonstration position band, budget,
  hardware list, and six-week project schedule are retained.

## Important interpretation of the calculation

The force model uses center distance `z`, while the project specifies surface
gap `d`. Actual geometry gives `z = d + Delta_g`. Numerical values at `z=10 mm`
are not a validated result for a finite assembly at `d=10 mm`.

The 500-turn coil, 10 mm radius, 0.050 A m^2 magnet moment, and 8 ohm resistance
are the proposal's sizing assumptions, not selected hardware. Inductance
`L=10 mH` and negligible passive mechanical damping are additional explicit
assumptions. With those parameters, the calculation predicts instability;
the example gains are not recommended firmware settings.

The original embedded Word image is retained as
`assets/original_proposal_diagram.png` for reference. It contains superseded
current-control labels and is not the figure used in the updated proposal.
The updated `system_architecture.pdf` and PNG show the current design.

Mathematical details and source links are inside both documents.
