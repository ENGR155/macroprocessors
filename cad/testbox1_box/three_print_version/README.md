# Testbox1 box — three printed parts

**Superseded by `../purchased_parts_version/`.** The purchased-parts revision fits the confirmed DRV5056 sensors, D68-N52 moving magnet and 3–4 DC1 helper stack. Use its three `JOB` files and assembly instructions. This older version uses generic sensor allowances and a one-disk helper pocket.

This version replaces the earlier eleven-part sheet/wood design. It contains **exactly three connected printable solids**, with matching STEP files and three individually oriented STL files. All structural pieces, tray, sensor carriers and helper retention are integrated into those three parts. Bolts, nuts, magnets, electronics, tape/shims and wiring are ordinary assembly items, not extra printed parts.

The design retains the reference's broad rear support, forward cantilever and suspended head, while replacing its wood and acrylic with the requested printed structure. Overall assembled nominal size is **180 × 160 × 200 mm**. It fits the HMC Bambu X1 Carbon's 256 mm cube and stays inside a conservative 220 × 220 mm central bed region. Use the regular **PLA** printer profile with the installed nozzle confirmed in Bambu Studio; the suggested baseline below assumes the standard **0.4 mm** nozzle.

**PLA thermal suitability has not been established.** The vented head reduces enclosure and contact, but the coil and fixed helper still transfer heat to the cassette and upper locating rim. Geometric validation does not establish a safe continuous coil duty. The actual assembly must stay within the selected PLA's temperature/load capability; obtain the measured coil/contact temperature and instructor-approved operating limit before energizing it unattended or relying on a final demonstration. This is a release condition on operation, not another printed version or a request for extra test prints.

## Print these three files

| File | Bed envelope and height | Orientation already encoded |
|---|---|---|
| `01_frame_base_upright_tray_PRINT.stl` | 180 × 160 × 190 | Base broad underside flat on bed |
| `02_cantilever_vented_head_upper_sensor_PRINT.stl` | 90 × 103 × 40 | Broad top face of arm flat on bed; head/coil opening points upward during printing |
| `03_helper_cassette_lower_sensor_guard_PRINT.stl` | 52 × 8 × 52 | Front Y39 face down; cassette and guard strips joined by an end wall both contact bed |

Print **one copy of each**, in three print jobs. Keep the supplied orientations rather than using automatic minimum-footprint orientation. Center each part on the plate. Check that Studio reports millimetres and 100% scale. The matching `_PRINT.step` files contain the same oriented geometry for CAD/slicer import; `_assembled.step` files contain assembly positions and should not replace the oriented STL files on the plate.

Suggested strength baseline: 0.20 mm layers, 6 walls, 6 top/bottom layers, 25–30% gyroid infill, calibrated PLA profile. Use an **8 mm outer brim** for part 3 and a brim for the tall base if the Makerspace profile calls for it. Material/profile selection and cooling remain printer-specific; these settings have not been sliced or executed in this session.

Part 1's gussets narrow upward, so they do not need support. Part 2 has no lower cage ring spanning between columns: the four columns grow directly from the inverted arm. Short horizontal M4-hole roofs and the upper sensor recess require only small bridges (the recess is 12 × 8 mm). Part 3's far end wall bridges the **3 mm sensor gap**, not the full 52 mm cassette width. The shallow helper pocket faces sideways in its print orientation. Inspect those small bridges and pocket perimeters in Studio before sending the three jobs; do not place support in the 3 mm sensor-service gap. All three remain single connected solids; there are no loose inserts hidden in the meshes.

## Mechanical assembly

1. Bolt part 2 onto the upright of part 1 with **four M4 × 30 mm bolts**, flat washers and nuts. The flange is in front of the upright; the top arm seats on its top. Bolt axes are X60/120 and Z172/184 mm. The 10 mm flange and 12 mm upright form a 22 mm stack. Nuts are accessible behind the upright. Tighten evenly with broad washers; avoid crushing PLA or preloading the cantilever out of square.
2. Insert the **nominal Ø25 × 20 mm electromagnet** upward through the open underside of the head. Its leads leave through one of the large side windows. The upper locating rim has a **Ø26.0 mm bore**, allowing 1.0 mm nominal diametral clearance. The cavity reaches Z190.8, giving 0.8 mm axial allowance above a coil resting with its face at Z170. Use measured thin nonmagnetic compliant shims/tape to remove radial and axial play without forcing an oversized part or stressing the frame. Shims are assembly consumables, not additional printed parts. Confirm their heat rating and include them in the final measured sensor calibration.
3. Put the helper disk into part 3's upward-facing **Ø19.6 × 1.9 mm pocket**. The documented candidate is Ø19.05 × 1.5875 mm N42; the pocket also clears the supplier candidate's Ø19.15 × 1.6875 mm worst case. Select polarity with the actual electromagnet and payload. Fix the helper to a repeatable location using a measured nonmagnetic shim or retaining adhesive: nominal axial freedom is 0.3125 mm, so an unsecured disk may lift toward the EM instead of remaining on the pocket floor. Do not fill the entire clearance with an unmeasured glue layer.
4. Fit the lower Hall device and leads into the **12 × 8 × 2 mm total allowance** above the integrated guard. Slide it in from either open X side through the 3 mm-high service slot. Retain it with nonmagnetic tape/adhesive or nylon ties through the guard's small slots. All sensor, board, insulation and mounting thickness above the guard must fit within that 2 mm total; a normal populated PCB may exceed it. Confirm the ordered sensor package. Orient its sensitive axis vertically, not merely its leads. The remaining clearance to the cassette is nominally 1 mm.
5. Close the head with part 3 using **four M3 × 40 mm socket-head bolts** and upper washers/nuts. Lower bolt heads must be **no more than Ø6 × 3 mm**, and **do not use lower washers**: a 7 mm lower washer would interfere with the guard. The heads sit beneath the cassette alongside the narrower guard, with approximately 0.435 mm lateral nominal clearance. The cassette, columns and arm form a 33 mm stack. Bolts retain the coil positively against its support cassette without depending on an unknown EM mounting thread. Keep wiring away from the lower guard and moving payload.
6. Secure the upper Hall device in the recessed **12 × 8 × 2 mm top pocket**, using nonmagnetic tape/adhesive; its wire groove runs rearward. This sensor allowance is part of the arm itself, so it requires no fourth print. Add soft nonmagnetic lining to the integrated catch tray, route and strain-relieve cables through the rear slots, and keep the supply and driver external.

Required fasteners: 4 M4 × 30, 4 M4 nuts, 8 M4 flat washers; 4 M3 × 40 socket heads meeting the maximum head envelope, 4 M3 nuts, 4 upper M3 washers. Use verified nonmagnetic head fasteners where practical; not all stainless screws are nonmagnetic. Fastener solids are omitted from the main assembly but their paths and conservative head/nut envelopes are independently checked.

## Dimensions and motion

| Feature | Nominal geometry |
|---|---|
| Base | 180 × 160 × 8 mm |
| Upright | 90 wide × 12 thick; Z8–190 |
| Front root gussets | 35 mm depth; reach Z110 |
| Arm | 90 × 103 × 10 mm; Z190–200 |
| Electromagnet face | Z170 |
| Helper shown seated | Bottom Z168.1, top Z169.6875 |
| Lower guard | Z162–164, 2 mm thick |
| Lower Hall allowance | Z164–166; cassette underside Z167 |
| Payload shown | **Assumed** Ø12.7 × 6; top Z155 (15 mm gap) |
| Catch tray | 70 × 70; 64 × 64 clear interior; 1.5 mm floor above base |

The proposal's **10–20 mm surface gap** is from the EM face Z170 to the moving payload top Z160–150. The lower guard's underside is Z162, giving **2 mm nominal clearance** at the 10 mm command and a physical stop at an 8 mm EM-face gap. That clearance is not permission for arbitrary payload tilt or controller overshoot. With the helper at the modeled pocket floor, its face-to-payload gap is **8.1–18.1 mm**, a different quantity. Recalibrate using the actual fixed helper position.

The pictured moving body remains an envelope, because the ordered moving magnet has not been established. The complete moving magnet, carrier and object must total **10 g**. A larger payload, different sensor package or altered guard requires a new collision check; the reference bodies are not extra objects to print.

## CAD and evidence

- `testbox1_PLA_three_print_assembly.step`: named, colored complete assembly, including five clearly named reference envelopes.
- `three_print_parts_assembled.step`: exactly three fabrication solids in assembled positions.
- Three `_PRINT.stl`: the only printable deliverables; three matching `_PRINT.step` and `_assembled.step` files.
- `component_manifest.json`: print orientations, dimensions, solid validity and material/thermal status.
- `dimensions.json` and `build_three_print.py`: reproducible geometry. Named parameter values drive major dimensions; supporting coordinates are explicit in the generator. Changing the JSON alone does not regenerate geometry.
- `conform_stl.py` and `mesh_conformity.json`: reproducible export correction for one OCCT tessellation T-junction. One long triangle edge is split at an existing neighboring vertex (maximum deviation 0.0000024 mm); no hole is capped and the STEP geometry is unchanged. This correction runs automatically during regeneration.
- Independent review/check outputs: separate agent reimports exported files, checks solids, mesh closure, assembly fit, mounting envelopes and print orientation.
- `assembly_preview.png` and `cad_isometric.svg`: views of the actual exported CAD, not generated concept art.

Import the STEP into Fusion as a new design and save under **testbox1 box**. No native Fusion timeline or F3D export was produced in this session, and the model has not been uploaded to the Fusion folder. The STEP contains editable solid bodies but no parametric feature history.

The known geometry is derived from the project portfolio and revised proposal: nominal JF-XP2520-12V coil, documented 3/4 × 1/16-inch helper, 10 g moving mass and 10–20 mm EM-face gap. Kuali notifications identify vendors/order status but do not establish exact part line items or dimensions. The printed frame dimensions are engineering choices adapted to those nominal envelopes; the reference photograph gives no frame dimensions.

Remaining release conditions are actual component fit, sensor package/axis/headroom, fixed helper polarity/location, coil force over the commanded range, coil/contact temperature and stable control with physical shutdown. The checked CAD does not establish that regular PLA will tolerate the delivered coil or that an unmeasured electromagnet will levitate 10 g at a 20 mm gap. Those facts cannot be guaranteed by a file or by increasing the number of geometry checks.
