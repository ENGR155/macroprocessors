# Purchased-parts design — three print jobs

This version replaces the earlier generic sensor mounts and assumed moving magnet. It uses your **DRV5056A3QLPG / DRV5056A4QLPG**, **D68-N52 moving magnet**, and **three or four DC1 fixed helper disks**. The coil is the confirmed nominal **25 mm diameter × 20 mm** model. The stand, head and helper cassette are printed; the small moving-magnet carrier shares the cassette's plate.

**Four physical printed pieces; three print jobs. Load only the three `JOB` files below.** The individual component STLs are duplicate geometry for inspection/custom placement, not four additional jobs.

| Print job | File | Contents / oriented size |
|---|---|---|
| 1 | `JOB01_PRINT.stl` | One integrated base/upright/tray, 180 × 160 × 190 mm; broad base down |
| 2 | `JOB02_PRINT.stl` | One arm/vented head/upper Hall seat, 90 × 103 × 40 mm; broad arm top down |
| 3 | `JOB03_PRINT.stl` | **Two separate pieces**: helper cassette + D68 carrier, overall 98 × 52 × 14.3 mm; both broad undersides down |

All dimensions are mm and files are already oriented. Center each whole job on an HMC **Bambu X1 Carbon** plate at 100% scale; keep job 3's two objects in their supplied relative positions. Its cassette and carrier have 17 mm between them, enough for separate 8 mm brims with 1 mm remaining. Do not automatically rotate the head onto an edge. No native Fusion document was saved: open `testbox1_purchased_parts_assembly.step` in Fusion and save it into **testbox1 box**.

The selected manufacturing material is regular **PLA**. Geometry checks do not establish PLA's temperature/load suitability with this actual electromagnet. The vented head avoids an enclosed hot shell, but the coil, helper and cassette remain thermally coupled. Measured coil/contact temperatures and an instructor-approved operating limit remain required before relying on this assembly for sustained levitation. This release condition does not imply more printed versions.

## Purchased dimensions used

| Part | Manufacturer dimensions / implemented fit |
|---|---|
| D68-N52 moving magnet | Ø9.525 × 12.7, ±0.1 mm; supplier mass 6.79 g; carrier bore Ø10.0 |
| DC1 helper disks | Ø19.05 × 1.5875 each, ±0.1 mm; one active stack of 3–4 disks |
| Four-disk pocket | Ø19.6 × 7.0 deep; four worst-case disks total 6.75 high, leaving 0.25 axial clearance |
| DRV5056 QLPG body | Manufacturer maximum 4.1 wide × 3.25 body height × 1.62 thick, rotated flat |
| Hall body seat | 3.7 along X × 4.5 along Y; lead side opens toward +X; seat floor 2 mm below surrounding top |
| Hall leads | Native 1.27 mm pitch; first 3 mm remain straight before fanout; isolated solder channels use 3 mm pitch and 1.6 width |
| Electromagnet | Nominal Ø25 × 20; upper locating bore Ø26.0; 20.8 available height |

The sensor source is the **DRV5056** datasheet, not DRV5055. These are unipolar sensors: the marked-face field direction matters. Both seats accept either A3 or A4, with the marked broad face **up or down** by rotating around the lead direction. That reverses the outer pins' global Y order. Use the manufacturer's package view to identify **pin 1 VCC, pin 2 GND, pin 3 OUT**; do not wire by a guessed left/right order after flipping the device. Neither seat establishes sensor saturation margin or guarantees field cancellation.

The two Hall body centers are **X104, Y65**: 14 mm radially away from the coil/magnet axis X90/Y65. The lower body floor is Z168 and the upper floor is Z198. This deliberate offset places the lower device **beside** the four-disk stack rather than trying to fit it beneath a 6.35 mm stack in a 10 mm gap. It changes the magnetic measurement geometry; calibrate the actual complete assembly in its final polarity and fixed-helper configuration.

## Sensor installation and soldering

1. Identify the marked face and pins while the device is loose. Lay the body flat in its shaped seat: the 3.25 mm body length runs along X and the 4.1 mm width along Y. Its lead shoulder points toward **+X**, away from the axis and between the head's bolt columns. Each pocket provides a left stop and side locating shoulders, rather than a generic PCB allowance.
2. Leave at least **3 mm of lead straight after the body**. Support the lead with fine pliers away from the plastic package, then gently fan the two outer leads from 1.27 mm pitch to the three channels at Y62/65/68. There are no unprintable dividers at the original pitch: the initial shoulder/fanout area is one open bay. Solder joints go in the separated lanes near **X117–120**; keep solder and each insulated conductor within its own 1.6 mm-wide lane. Use individual insulation/heat-shrink, and keep the hot iron away from PLA and the sensor body. Solder while loose where practical, then install the formed leads.
3. Retain the body with a **nylon tie no wider than 2.5 mm**, through the 3 mm slots. A 2.7 mm transverse relief groove lowers the surrounding ledges: even the minimum 1.42 mm body thickness stands 0.22 mm above the groove floor, allowing the tie to press the body rather than bridge above it. These slots go completely through the printed part. Add a separate tie through the downstream slots to strain-relieve the insulated wires; electrical leads must not carry cable loads.
4. Route the resulting wires toward +X, then rearward outside the moving payload. Both lower and upper packages remain accessible before final tightening. Do not substitute a populated sensor PCB for the exact bare QLPG package without checking its dimensions. Place the local bypass capacitor at the leads/wiring as the circuit requires; the CAD does not invent a PCB or IC socket for the MCP3204.

For the default below-coil helper stack, the lower position is a reasonable starting place for the lower-gain **A4**, and the upper for **A3**. This is a starting assignment, not a validated field-range choice. With the alternate top stack, the stronger field may instead occur at the upper sensor. Swap the compatible packages or flip their marked faces based on measured polarity and output headroom.

## Default helper stack below the coil

The main assembly shows **four DC1 disks** in the central cassette pocket, floor Z163 and open top Z170. The 1 mm floor gives an underside at Z162. All four nominal disks occupy Z163–169.35; a worst-case four-disk stack reaches Z169.75. Keep the disks as one axial stack in the chosen polarity.

The EM and bolted cassette mechanically capture the stack. Fix its axial location with a measured nonmagnetic shim or retaining adhesive: nominal four-disk axial freedom is **0.65 mm**, worst-case **0.25 mm**. An unsecured stack can shift toward the electromagnet. For **three disks**, use a measured nonmagnetic spacer approximately one nominal disk thickness, 1.59 mm, **in addition to any final fit adjustment**, so the operating stack position remains repeatable. Determine the spacer from actual parts; do not force a nominal thickness into a worst-case stack.

Bolt the cassette through the head using **four M3 × 45 mm socket-head bolts**, with washers and nuts on top. The printed stack is now **38 mm**, not the earlier version's 33 mm. Use maximum lower head dimensions **Ø6 × 3 mm**. Their positions are radius 19 at 45/135/225/315 degrees. No mounting thread in the EM is assumed. The cassette supports the coil's outer lower rim positively. A measured nonmagnetic compliant shim in the Ø26 locating ring and the extra 0.8 mm ceiling clearance removes coil play without stressing the print.

**Control authority remains unverified with 3–4 helpers.** At the 10 mm EM-face command, the D68 top is only about **3 mm below the nominal bottom of the helper stack**. Passive magnetic attraction may be excessive, including at zero coil current. Neither CAD nor a contact holding-force rating establishes a controllable 10–20 mm range. Verify zero-current release, useful current authority, sensor polarity/headroom and complete-assembly force before free suspension.

## Alternate helper location above the coil

The head also includes a **Ø19.6 × 7.0 mm top pocket**, floor Z193. This permits moving the same 3–4-disk stack **above** the EM without another print. `OPTIONAL_top_stack_configuration.step` shows this alternate arrangement. Install only one active stack; the main and alternate STEP files are configurations, not instructions to double the number of magnets. Performance of either placement is unmeasured.

The top pocket has 2.2 mm of material above the EM's relief ceiling. Because job 2 prints inverted, add **manual build-plate-origin support inside this 19.6 mm pocket** in Bambu Studio. It is removable through its open mouth after printing. The upper sensor's smaller pocket also faces the plate; inspect its bridging/support in the slicer. No slicer execution or printer run was performed here.

For positive retention in the top position, fabricate the optional **nonprinted 50 × 8 × 1 mm nonmagnetic polycarbonate/nylon strip**, with two Ø3.4 holes **38 mm apart**. The supplied `OPTIONAL_retainer_cut_template.svg` is actual scale (verify its 20 mm scale bar), and `OPTIONAL_NONPRINT_retainer_strip.step` gives the exact solid. Fit the strip diagonally over the pocket between two opposite existing M3 bolts and clamp it below their upper washers/nuts. It is **not a fifth printed piece**. Add a measured nonmagnetic pad between the stack and strip to remove vertical freedom: nominal four disks need about **0.65 mm** to reach the strip underside at Z200; three disks need about **2.24 mm**. Include actual disk and strip thicknesses in the fit.

M3 × 45 retains more than one thread pitch past the nut with the 1 mm optional strip, 0.5 mm washer and 2.4 mm nut. Verify the actual supplied hardware. A closed tie underneath the arm is deliberately **not** specified for this top stack, because the coil occupies that route.

## D68 carrier and the 10 g moving assembly

The fourth printed piece is a light carrier for the **actual D68-N52**, not the old assumed Ø12.7 × 6 payload. Its Ø10 cup accepts a worst-case Ø9.625 magnet with nominal diametral clearance of 0.375 mm. The cup floor supports the magnet; the pole face stands **0.4 mm above the cup wall**.

Add a **nonprinted nylon retaining loop no wider than 3 mm and no thicker than 0.8 mm**. Route it over the magnet's top face, down the two molded side/foot guide recesses, and underneath the bottom groove. Put the buckle or knot **below the carrier**, away from the top and sides. This over-top loop positively captures the magnet against upward magnetic force; an open cup, glue alone or a circumferential friction tie is not the specified retention. The STEP includes a conservative routed loop envelope, not a detailed manufacturer's cable tie. Choose and inspect actual suitable retaining material; check that the magnet cannot pull out before use.

At the supplier's 6.79 g magnet mass, **3.21 g remains for everything else moving**. The carrier's actual solid volume is about **1123.80 mm³**. At an assumed solid PLA density **1.30 g/cm³**, that is **1.461 g**, leaving about **1.749 g for the loop, buckle, shims, adhesive, ballast and attached object**. This deliberately uses the solid carrier volume rather than assuming infill makes it light. Weigh the complete moving assembly and add nonmagnetic ballast to reach **10.00 g**. Do not use the predicted print mass as its measured mass.

## Gap and hardware

The command remains measured from the electromagnet face **Z170** to the D68 magnet's top, not to the carrier or tie. Commanded top positions are Z160–150 for a 10–20 mm gap. The bottom of the cassette is Z162. The retaining loop may stand 0.8 mm above the magnet face, so **nominal clearance at the 10 mm command is 1.2 mm** for the complete moving assembly, not the bare magnet's 2 mm. Tilt, controller overshoot, print/part tolerance and a thicker tie reduce that margin. A thicker tie or buckle above the magnet requires a revised clearance check.

The unchanged rear joint uses **four M4 × 30** bolts, nuts and front/rear washers through the 10 mm head flange and 12 mm upright. Use four **M3 × 45** bolts for the thicker helper cassette. Near-field fasteners should be verified nonmagnetic; stainless grade alone does not establish that. Fastener solids are not printed components.

Suggested slicer baseline for the standard **0.4 mm nozzle**: calibrated regular PLA profile, 0.20 mm layers, 6 walls, 6 top/bottom layers, 25–30% gyroid for the large stand/head. Carrier mass is bounded using solid volume; use a strong, well-bonded carrier rather than trying to save the final fraction of a gram. Center the jobs, use an appropriate brim for the tall frame, and keep 8 mm brims for job 3 if needed. Inspect the manually supported top pocket and all small channels in the slicer before starting the three jobs.

## Deliverables and limits

- `testbox1_purchased_parts_assembly.step`: complete default four-helper assembly with purchased component references.
- `four_printed_parts_assembled.step`: four fabrication solids only.
- `JOB01_PRINT.stl`, `JOB02_PRINT.stl`, `JOB03_PRINT.stl`: the **three jobs to print**; matching STEP files are included.
- Individual component STEP/STL, `component_manifest.json`, `dimensions.json`, reproducible `build_purchased.py`, and `payload_mass_budget.json`.
- Optional top configuration and nonprinted retainer template/STEP.
- Independent exported-file checks and review; real-CAD previews/evidence are supplied alongside.

Lead references contain three continuous, electrically isolated solids per sensor. Logical component entries therefore differ from physical BRep solid count; they are not extra parts to print. `conform_stl.py` corrects only mesher T-junctions by splitting an existing edge at an existing near-collinear vertex, without capping holes. Its audit record is `mesh_conformity.json`.

Primary dimensional sources: [TI DRV5056 datasheet, LPG drawing page 31](https://www.ti.com/lit/ds/symlink/drv5056.pdf), [K&J D68-N52](https://www.kjmagnetics.com/d68-n52-neodymium-cylinder-magnet), and [K&J DC1](https://www.kjmagnetics.com/dc1-neodymium-disc-magnet). These source dimensions and the supplied purchasing details replace the earlier generic assumptions. Printing/slicing, native Fusion execution, actual purchased-part metrology, thermal performance and successful levitation were not performed in this session.
