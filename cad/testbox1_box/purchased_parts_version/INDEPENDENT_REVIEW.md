# Independent review — purchased-parts version

11 November 2026. Separate checking agent. **77/77 checks passed against the final exported STEP and STL files.** Reproduce using `independent_purchased_check.py`; detailed results are in `independent_check_results.json`. The checker imports delivered geometry directly and does not import the builder's source functions or mesh-repair code.

This review supersedes the earlier assumed-payload and single-helper reviews. It verifies geometry and assembly access, not physical levitation, magnetic control authority, PLA temperature capability or a completed print.

## Purchased components checked

- [K&J D68-N52](https://www.kjmagnetics.com/d68-n52-neodymium-cylinder-magnet): diameter 9.525 mm, length 12.7 mm, stated dimensional tolerance ±0.1 mm and nominal mass 6.79 g. The moving reference and carrier now use this cylinder, not the earlier illustrative short disk.
- [K&J DC1](https://www.kjmagnetics.com/dc1-neodymium-disc-magnet): nominal diameter 19.05 mm, thickness 1.5875 mm. **Three or four disks are a fixed stack**, not modeled as spares. The tolerance scenario uses diameter 19.15 mm and four-disk thickness 6.75 mm.
- [TI DRV5056 datasheet](https://www.ti.com/lit/ds/symlink/drv5056.pdf): the ordered LPG parts use the modified TO-92 outline. The maximum body envelope is 4.1 × 3.25 × 1.62 mm; the package drawing's 5.05 mm dimension includes the lead shoulder. Native pin pitch is 1.27 ±0.05 mm. Pin functions are **1 VCC, 2 GND, 3 OUT**. This is a unipolar DRV5056, not a bipolar DRV5055.
- Nominal Amazon electromagnet envelope: diameter 25 mm × height 20 mm. A chosen 25.5 × 20.6 mm clearance scenario also fits, but those enlarged dimensions are an engineering allowance, not a published supplier tolerance.

The sensor outline and sensing-axis figure were visually inspected from the official TI PDF. The sensitive axis is normal to the marked flat package face. Lay the body flat with that face upward or downward as required by the measured local field; pointing its leads upward would orient the axis incorrectly. DRV5056 output increases for a south pole presented to its marked face. Both off-axis locations require an actual field/polarity/headroom check before fixing orientation.

## Actual export and printer checks

There are **four printed bodies in three print jobs**. Job 3 contains both the cassette and the separate moving carrier. These are four physical objects, not a claim of three printed pieces.

| Body/job | Bed envelope × height | Orientation |
|---|---|---|
| Job 1: integrated frame/base/tray | 180 × 160 × 190 mm | Broad base down |
| Job 2: cantilever/head | 90 × 103 × 40 mm | Broad arm top down |
| Job 3: stack cassette | 65 × 52 × 8 mm | Broad underside down |
| Job 3: D68 carrier | Less than 16 × 16 × 14.3 mm | Bottom foot down |

All four bodies reimport as valid single solids. The main assembly has 15 logical entries containing **19 actual solids**, because each lead reference contains three isolated pins. All 105 logical component pairs have zero overlapping volume. The optional top-stack assembly has 20 actual solids including its nonprinted retainer strip and has no interfering component pairs.

All seven delivered meshes—four individual STLs and three job STLs—are closed manifolds with the expected connected-component counts. Job 3 has two separate, nonintersecting objects. Their 17 mm separation leaves 1 mm between two 8 mm brims. All jobs fit a central 220 × 220 mm region of the stated Bambu printer bed. Broad bed contact and the explicitly supplied rotations were checked from the print STEP geometry; the frame is not balanced on a base edge.

The alternate upper stack pocket faces the bed in Job 2 and creates a roughly 20 mm roof span at 7 mm height. Use the documented removable manual support inside that pocket and inspect the sliced result. No actual slicer toolpath or physical print was validated here.

## Fit, wiring and retention checks

Both helper pockets are diameter 19.6 × 7 mm. Four tolerance-max disks, plus a 0.1 mm adhesive allowance, fit with 0.15 mm axial clearance and 0.45 mm diametral clearance. A three-disk stack also fits with a measured nonprinted shim. **Total nominal unfilled height is approximately 2.24 mm for three disks, or 0.65 mm for four.** Adding only a nominal fourth-disk thickness does not by itself remove the remaining clearance. Measure the actual disks, shim and adhesive together; secure a repeatable position and calibrate it. The seated reference location does not prevent an unsecured lower stack from attracting upward toward the coil.

The lower Hall seat is 14 mm radially off-axis at X104, Y65, floor Z168; the upper seat is likewise off-axis with floor Z198. Maximum bodies fit the 3.7 × 4.5 mm seats. Three millimetres of lead remain straight before the fan-out. Separate 1.6 mm solder lanes at 3 mm pitch leave 1.4 mm printed webs; the design does not attempt almost-zero-thickness dividers at native pin pitch. Lead references contain three separate continuous conductive bodies.

Body straps have actual through-holes, including through the upper locating rim. Their grooves lie below the thinnest package's upper face so a taut strap presses the package rather than bridging over an empty recess. Separate wire-strain-relief holes and underside routing clear the nominal centered coil. Use the specified tie dimensions and locate the coil with shims so it cannot drift into the narrow tie route.

Identify pins on the real component before installation. The channels are routing lanes, not a reliable left-to-right pin legend after a face flip. Solder and insulate the leads outside the PLA, let them cool, then install and verify continuity. Do not solder against printed seats.

The nominal coil inserts from below with the cassette removed; a 4 × 2 mm radial wire-exit envelope is open. The D68's maximum 9.625 × 12.8 mm envelope fits its open carrier. The nonprinted loop passes over the magnet and underneath the carrier through the modeled guides, providing upward retention rather than depending on friction alone. The corrected loop envelope does not intersect the magnet or carrier. Its modeled maximum is 3 mm width and 0.8 mm thickness, with the buckle below the carrier.

All four M3 × 45 cassette bolt paths, maximum 6 × 3 mm heads, upper washers and nuts clear. The 38 mm stack leaves 4.1 mm nominal thread protrusion after a 0.5 mm washer and 2.4 mm nut; the optional 1 mm strip reduces that to 3.1 mm at its two bolts. M4 × 30 frame fasteners, heads, both washers and nuts also clear. Optional retainer-strip holes match opposite M3 bolts at 38 mm pitch. The nonprinted strip and measured shims are additional assembly supplies, not extra printed bodies.

The entire moving carrier, D68 and positive loop were checked through the 10–20 mm **EM-face-to-magnet-face** gap in 1 mm steps. At the 10 mm command the loop reaches Z160.8 below the cassette underside Z162, leaving only **1.2 mm nominal clearance**. Buckles, ballast, wires or thicker ties must not extend above that envelope. The 1 mm central cassette floor is a thin printed impact stop, not a proven pull-in-impact barrier.

## Payload mass and operating conditions

The carrier's exported volume is approximately 1123.80 mm³. At an explicitly assumed solid PLA density of 1.30 g/cm³, it weighs 1.461 g. Combined with the supplier's nominal 6.79 g D68, approximately **1.749 g remains for the retaining loop, buckle, adhesive and ballast**. Weigh the complete moving assembly and adjust it to the proposal's 10 g; neither infill settings nor nominal catalog weights establish the final mass.

The lower four-disk placement leaves a modeled 3 mm helper-to-D68 face gap when the EM-face gap is 10 mm. The strong fixed and moving permanent magnets can therefore materially alter passive attraction. Verify zero-current release and available control authority, not only the ability to lift. The optional upper pocket permits relocating the same stack without new prints; it does not establish that its different magnetic plant works. Install only one helper stack, and recalibrate after moving it or changing three versus four disks.

PLA heating/creep, real force-versus-gap/current, sensor polarity and saturation, controller stability, physical shutdown and pull-in impact remain unmeasured. The earlier conditional beam estimate is not a qualification of the newly pocketed head or thin cassette floor. These files pass the stated geometry/export checks; they cannot guarantee sustained levitation or thermal suitability.
