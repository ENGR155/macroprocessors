# Printable stand version

Open `testbox1_box_printable.step` in Fusion to see the complete 11-part stand with every structural component assigned a printable polymer alternative. This assembly omits the electromagnet, helper magnet, Hall devices and assumed payload: those are purchased parts or electronics, not print jobs. The original full CAD assembly remains one folder up.

Individual, bed-oriented STL files are in `parts/`. Every part was reoriented to put its broad face on Z=0 and centered on the bed. The listed X/Y extents fit a 220 × 220 mm printer; the base uses nearly the full bed at 180 × 160 mm. Check your printer's actual usable area before slicing. The large base will take substantial filament and print time.

Suggested first prototype: PETG, 0.2 mm layers, 5 perimeters, 40% gyroid infill, 6 bottom/top layers. Use 6 perimeters and 50% infill for the cantilever/head cradle and bracket parts. Keep the base flat. Rotate the upright panel in the slicer to print its 90 × 172 mm broad face down. Print and fit one cradle, bracket and cassette before committing to the full set. Use a brim where the slicer predicts a narrow footprint. No supports are expected for the supplied bed orientations, but inspect the bridge/slot previews.

Fasteners remain separate hardware. Use the nonmagnetic head hardware and lengths listed in the parent README. The 2 mm lower guard and 2 mm Hall package allowance are unchanged; confirm the actual sensor/carrier thickness before printing. Material settings are starting points, not a measured strength rating. Check layer direction, bolt tightening, frame sag and heat around the coil before operating. Successful levitation still requires the project's force, temperature, Hall range and control tests.

The STEP preserves the full assembled coordinates. For printing, use the per-part STLs, which are independently centered and oriented on the bed. `print_manifest.json` records each bed footprint. Edit the parent `build_cad.py` and regenerate geometry if the purchased payload, sensor package or gap changes.
