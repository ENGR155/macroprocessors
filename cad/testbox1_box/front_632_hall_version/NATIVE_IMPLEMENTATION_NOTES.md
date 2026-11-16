# Native Fusion generation

Actual generation used `Fusion_Front632/Fusion_Front632.py` inside Autodesk Fusion. No security settings were changed, and the blocked external OCP library was not loaded. All helper coordinates are millimetres converted to Fusion's internal centimetres; STL export explicitly selects millimetres.

The native head imports the prior single-solid head seed, unions the full original 90 × 103 × 10 mm top plate and original upper cage rim, then recuts the Ø26 locating cavity/0.8 mm axial relief, upper magnet pocket, front rod guide, new clamp and four Ø4.1 mounting holes. Restoring the whole plate and rim removes every obsolete side-guide/counterbore opening from the prior head. The original rear flange, gussets and unchanged 4.5 mm rear mounting holes remain. The lower cassette and rod are built directly from box/cylinder Boolean primitives.

The finished rod and oversize print stock are distinct bodies. Native sketches/extrusions are used only for the nonprinted tilted sensor-loop references. Base and moving-carrier STEP/STL output files and plate 1 are copied byte-for-byte from the original inputs after geometry export. Their portable copies and the head seed reside in `native_inputs/`; those files are regeneration inputs, not additional print jobs.

`build_front_632.py` is a matching CadQuery source implementation; it was syntax checked but not used to generate this revision because its native DLL was blocked. The tested native Fusion script is the executable source for this delivery. The independent checker reimports delivered files rather than calling either generator's geometry functions.
