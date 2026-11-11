# Magnetic levitation stand — testbox1 box

Open `testbox1_box_maglev.step` in Fusion. It is an actual named, colored, 16-component solid assembly in millimetres, with 11 fabrication components and five clearly named reference envelopes. Save it to your **testbox1 box** Fusion folder. This deliverable has not been uploaded to that folder: Fusion control was unavailable in this session. No native F3D was created or runtime-tested here.

The design follows the Uzzors2k stand's plywood slab, broad clear rear panel, forward clear cantilever and hanging electromagnet. Its dimensions are adapted design choices, not recovered dimensions of the photographed original. The original coil was 40 × 25 mm; this model uses your project's 25 × 20 mm electromagnet.

## Files

- `testbox1_box_maglev.step`: complete assembly, including illustrative reference objects.
- `fabricated_parts_assembled.step`: fabrication solids only, in assembled positions.
- `parts/`: individual STEP files and fabrication STL files. Coordinates retain their assembly positions; orient each printable part on its broad flat face in your slicer. Acrylic/wood parts are sheet/wood fabrication, not intended to print despite having mesh exports.
- `assembly_preview.png`, `cad_isometric.svg`: views generated from the exported CAD geometry.
- `dimensioned_assembly.pdf` / `.png`: front/side assembly drawing. All dimensions mm.
- `component_manifest.json` and `parameters.json`: dimensions and component metadata. **The JSON is a dimension record, not a parametric driver.** Edit the coordinate-based `build_cad.py` and regenerate to change the geometry.
- `independent_check.py`, `independent_check_results.json`, and independent review report: exported-file checks by a separate agent.
- `INPUT_EVIDENCE.md`: purchase and document evidence, with remaining unknowns.
- `Fusion_Import_Testbox.py`: optional Fusion API importer; creates a new design, imports STEP, adds reference parameters and exports local F3D when run successfully. This script has not been executed in Fusion. It does not create editable modeling features or link its reference parameters to imported solids.

The easiest Fusion route is **File > Open > Open from my computer**, select the STEP, then **Save** and select your folder. For the optional script, create a Fusion Python script using Utilities > Add-Ins > Scripts and Add-Ins; replace its script contents with this file and keep the STEP and parameters JSON beside it. Run through Fusion, not by double-clicking the Python file.

## Verified dimensions and assumptions

| Item | Model |
|---|---:|
| Overall nominal envelope | 180 W × 160 D × 200 H |
| Plywood base | 180 × 160 × 18 |
| Rear acrylic panel | 90 × 172 × 6; bottom Z18, top Z190 |
| Top acrylic cantilever | 90 × 97 × 6; Z190–196 |
| Electromagnet envelope | Ø25 × 20; face Z170; top Z190 |
| Cradle bore | Ø25.6; 0.6 nominal diametral clearance |
| Helper candidate | Ø19.05 × 1.5875 N42, axial magnetization |
| Helper pocket | Ø19.6 × 1.9 deep; floor Z168.1 |
| Worst-case candidate helper | Ø19.15 × 1.6875; 0.45 diametral / 0.2125 axial clearance |
| Lower guard | 2 thick; bottom Z162; upper face Z164 |
| Lower Hall package + carrier allowance | 12 × 8 × 2; Z164–166; 1 mm above to cassette |
| Catch tray | 70 × 70 × 6; internal 64 × 64; floor 1.5 |
| Illustrated moving payload | **Assumed** Ø12.7 × 6; top Z155 (15 mm surface gap) |

Your proposal's **10–20 mm surface gap** is measured from the electromagnet face Z170 to the payload top Z160–150. The fixed helper's modeled bottom is Z168.1, so the helper-to-payload face distance is **8.1–18.1 mm**, a different quantity. The 2 mm thick lower guard stops a rising object at an 8 mm EM-face gap; its underside is 2 mm above the nearest commanded payload top. That is nominal CAD clearance, not an allowance for uncontrolled overshoot.

The helper is removable and reversible. The pocket and electromagnet together mechanically capture it; fix its actual axial position with a thin nonmagnetic shim or suitable retaining adhesive after deciding polarity. Its unshimmed 0.3125 mm clearance means attraction may pull it off the pocket floor toward the EM. Calibrate using the actual installed position. The helper's effect on force and Hall saturation is not established by this CAD.

## Assembly and hardware

Use nonmagnetic fasteners near the head (verified nonmagnetic brass or suitable nylon); do not assume every stainless screw is nonmagnetic. Metal fasteners can influence sensing. Screws, washers and nuts are specified below but not modeled.

| Joint | Quantity / suggested hardware |
|---|---|
| Base to wood clamp | 2 countersunk Ø4 × 40 wood screws; pilot holes Ø2.5 in wood; base clearance Ø4.5; flush underside heads |
| Wood clamp to acrylic rear | 2 M4 × 45 + washers and nuts; axes X60/120, Z31 |
| Rear panel to angle brackets | 2 M4 × 20 + washers and nuts |
| Angle brackets to arm | 2 M4 × 20 + washers and nuts |
| Cradle flange to arm | 4 M3 × 20 + washers and nuts |
| Helper cassette through cradle and arm | 4 M3 × 35 + washers and nuts |
| Lower guard through standoffs, cassette, cradle, arm | 2 M3 × 40 + washers and nuts |
| Upper Hall carrier to arm | 2 M3 × 16 + washers and nuts |
| Catch tray to base | 4 Ø3 × 16 wood screws; Ø2.5 base pilots |
| Sensor retention / wire routing | Nylon ties, thin nonmagnetic adhesive/shims, insulating wire sleeve |

1. Fabricate the base and hardwood clamp. Install base screws flush; clamp's vertical screws are at X75/105 to avoid the horizontal X60/120 bolts. Secure the rear sheet to the clamp with washers on acrylic. Tighten lightly to avoid cracking it.
2. Bolt the two angle brackets to the rear sheet and cantilever. Panels meet at Z190 and are positively fastened with brackets, not glued edge-to-edge. Arm bore Ø26 remains open above the coil.
3. Bolt the cradle flange beneath the arm. Insert the coil from below. Its side leads exit the 10 × 6 cradle window toward the rear. Actual lead/cable size still needs checking.
4. Put the helper in the cassette, select polarity on the bench, and secure its final location. Install the cassette below the EM using four long through-bolts. Its top supports the coil outer rim; this is positive axial retention without guessing an EM mounting thread.
5. Attach Hall devices to their carriers with insulated leads and nylon retention. The lower 2 mm allowance includes **everything above the guard**, not just PCB thickness. A conventional populated board may exceed it; verify package and total height before fabrication. Orient each sensor's sensitive axis vertically and adjust laterally in slots. The carriers are generic allowances, not exact package sockets. Upper carrier is independently removable.
6. Bolt the lower guard using the two standoff paths. Confirm the Hall assembly clears the cassette by at least 1 mm at the modeled dimensions. Keep all wires outside the payload's swept path. Secure the catch tray and line it with nonmagnetic foam.

Use the protective guard as a stop, not as a support for commanded motion. If payload dimensions, Hall package height or guard position change, regenerate and rerun the clearance checks. The 10 g requirement applies to the **whole moving assembly**, including magnet, carrier and object; the orange body is only an envelope.

## Fabrication and validation limits

The coil bore is deliberately loose; add a nonmagnetic compliant shim to remove lateral play after measuring the delivered coil. Verify actual coil diameter/height, lead exit, magnet part number and payload before cutting. No ordered sensor package, final payload geometry, coil temperature or force-versus-gap data was available. The head and brackets are nominally modeled as PETG for prototyping; use a material and retention method appropriate to measured coil temperature. CAD does not establish thermal lifetime, stiffness or safe lifting capacity.

The separate checker reimports the exported STEP/STLs and checks solid validity, interferences, fit, mounting paths and the illustrative payload sweep. These geometric checks do **not** prove levitation. Bench acceptance still requires stable 10 g suspension over the full 10–20 mm range, helper polarity and Hall headroom checks, force/current and temperature characterization, tuning and working independent shutdown. The portfolio explicitly records these measurements as incomplete.

Generator environment: Python 3.12, CadQuery 2.8.0, cadquery-ocp 7.9.3.1.1, Matplotlib, NumPy and VTK. Dependencies are not included in the delivery ZIP. Rebuild with `python build_cad.py`; create drawings with `python make_preview.py`, then create the final depth-buffered preview with `python render_preview.py`; check exported files with `python independent_check.py` in an environment containing the required libraries.
