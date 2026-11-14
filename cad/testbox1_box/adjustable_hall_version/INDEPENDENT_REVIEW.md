# Independent review — vertically adjustable Hall holders

12 November 2026. Separate checking agent. **137/137 checks passed against the final exported files.** Reproduce with `independent_adjustable_check.py`; detailed evidence is in `independent_check_results.json`. The checker imports STEP and reads STL directly, without importing the builder's geometry or mesh-repair code.

`baseline_sha256.json` records the original purchased-version hashes. The audit compares against the original files when available and falls back to those recorded hashes when run from an extracted standalone package.

## What changed and what was preserved

Both DRV5056 LPG packages now sit in separate sliding printed holders on **vertical** indexed rails. Their centers remain at X104, Y65, 14 mm radially from the electromagnet axis. Their broad marked faces remain horizontal; height adjustment does not rotate the sensors. These are mechanical positioning options, not a guarantee against saturation or a calibrated field-cancellation arrangement.

The base/frame and D68 carrier's assembled STEP, print STEP and print STL files, and both Job 1 files, are **byte-identical** to the purchased-parts version. The already printed base therefore remains applicable. Jobs 2 and 3 have changed outboard guide ears. Job 4 adds four separate objects: two indexed rails and two sensor carriages. There are **eight total printed bodies in four jobs**, including the retained base; the extra job is not a claim of one extra physical piece.

The D68-N52 payload, its positive nylon retaining loop and the three/four-DC1 stack provisions remain. Only one helper stack is installed at a time, either below the EM or in the optional upper location.

## Actual adjustment range

Each rail has five index holes at 8 mm pitch. The clamp's rounded slot is 11.4 mm overall with a 3.4 mm width and 8 mm straight centerline. A 3 mm shaft permits the documented **±4 mm fine adjustment** at each selected index, retaining 0.2 mm end clearance. Adjacent index ranges meet, giving **40 mm total operating height range per sensor**. Moving to another index requires relocating the bolt; this is not one uninterrupted 40 mm fine-adjustment slot.

| Quantity | Upper holder | Lower holder |
|---|---|---|
| Index-hole Z positions | 214.5, 222.5, 230.5, 238.5, 246.5 mm | 147.5, 139.5, 131.5, 123.5, 115.5 mm |
| Operating carriage-center range | 210.5–250.5 mm | 111.5–151.5 mm |
| Operating sensor-seat floor range | 203.5–243.5 mm | 113.5–153.5 mm |
| Maximum LPG body top | Floor + 1.62 mm | Floor + 1.62 mm |

The EM occupies Z170–190. If the marked face points upward, its modeled upper surface is Z205.12–245.12 for the upper sensor and Z115.12–155.12 for the lower. Thus the nearest marked-face distances are 15.12 mm above the EM's top and 14.88 mm below its bottom. Flipping the package changes which body surface is marked and changes the outer-pin physical order. The internal Hall element is inside the package: these body/face dimensions are not a measured magnetic distance calibration.

The physical extra slot clearance permits approximately 0.2 mm beyond the outer operating limits. The stronger continuous sweep test covers upper carriage centers 210.5–250.7 and lower centers 111.3–151.5. Integrated root shoulders prevent travel farther inward. Removable endstop cross-bolts prevent the carriages leaving the free rail ends.

## Geometry and motion verification

All eight fabrication bodies are valid single solids. The parked assembly has 19 logical entries containing 23 actual solids, because each formed-lead reference contains three isolated pins. All 171 logical component pairs are nonintersecting. All twelve delivered STLs—eight individual files and four job files—are closed manifolds with their expected connected-component counts.

The continuous motion proof uses conservative swept solids covering **every intermediate Z position**, not just endpoint snapshots. It retains the sleeve's rail bore and sweeps its complete outer profile, pod, maximum package, formed pins and specified body/lead-tie envelopes. These volumes clear the stand, coil, both possible helper-stack locations, optional retainer strip, fixed hardware and a conservative keepout containing the payload's entire 10–20 mm motion. Endpoint enclosure checks verify the delivered moving geometry lies inside those conservative sweeps.

Every index was also checked at both fine endpoints and its center with the actual 5.5 mm across-flats hex nut, shaft, head and washer geometry. The rear-open nut track permits insertion at either fine extreme. It accepts a regular 2.4 mm-thick M3 nut, **not a thicker locking nut**. The nut track's nominal side clearance is 0.15 mm, so printed fit still needs inspection and light cleanup if required.

The 10 × 12 mm keyed rails have 10.6 × 12.6 mm bores: 0.3 mm nominal clearance per side. Fixed rail cross-bolts positively retain the rails in their ears. Endstop heads physically intercept an escaping sleeve, and the carriages can be installed from the free ends with those bolts removed. Hardware shaft/tip envelopes clear the operational motion. During adjustment keep the pod supported, the coil unpowered and the sensor wires unloaded; tighten the clamp before operation.

## Sensor mounting and wiring

The [TI DRV5056 datasheet](https://www.ti.com/lit/ds/symlink/drv5056.pdf) supplies the LPG maximum body dimensions: 4.1 × 3.25 × 1.62 mm. Those bodies fit both holders in either face orientation. The body straps pass through actual holes, and the ledge grooves allow a strap to contact the package rather than bridge above it. All three solder lanes remain open. Their 1.6 mm widths at 3 mm pitch leave 1.4 mm printed webs, following a shared native-pitch shoulder bay and 3 mm of straight lead before fan-out. The three formed conductive paths remain separate.

Identify the real pins before soldering: 1 VCC, 2 GND, 3 OUT. The DRV5056 is unipolar and its response depends on the marked-face polarity. A face flip changes the physical outer-pin order. Solder and insulate away from PLA, then secure the package and wire strain relief. Moving the printed holder must not bend the bare package leads.

The rigid formed leads are included in the complete motion proof. **The real flexible service cable is not motion-certified.** The audit checks fixed anchor holes and clear free routing regions at X120–132, Y80–110, upper Z201–260 and lower Z100–161. Anchor terminations pass through the modeled slots; the larger routing bounds in the wiring notes include those terminations and are not wholly empty volumes.

Provide at least 150 mm of free flexible lead between moving and fixed strain relief, with the documented 10 mm bend radius and slack at both extreme positions. That length is a geometric allowance, not a physical cable test. Route and hand-check the actual loop throughout all index/fine settings before powering the assembly.

## Printing and structural observations

Every job fits the central 220 × 220 mm region and the stated printer height. Actual broad bed contact and print orientations were checked. Rails lie on their front faces, with no hovering shoulder. The upper carriage's pod and sleeve bottoms are coplanar. The lower carriage's pod underside is 9 mm above its sleeve's bed-contact plane and **requires removable buildplate-origin support beneath the pod**. The head's optional upper helper pocket also needs the documented manual support. No actual Bambu toolpath or physical print was validated.

Job 4 has a minimum 12 mm gap between its rails. Use no more than a 5 mm outer brim there if a brim is needed; a blanket 8 mm brim would merge neighboring brims. Inspect support reach and small slot/nut-track roofs in the sliced preview.

The new ear material is added outside the original coil support. Indexed rail holes leave 3.3 mm edge ligaments and 4.6 mm between holes. The lower ear joins the cassette through a short 4 mm overlap region. These dimensions are geometrically connected and printable; they are not a measured stiffness or impact rating. Clamp friction, printed clearances, layer adhesion, ear compliance and PLA creep/heating remain unqualified.

## Retained operating limits

The four-disk maximum stack plus 0.1 mm adhesive allowance fits either 7 mm helper pocket. Three disks require a measured nonprinted shim; nominal unfilled heights are 2.2375 mm for three disks and 0.65 mm for four. Fix and calibrate the actual stack position.

The complete payload retains its 1.2 mm nominal minimum clearance at the commanded 10 mm EM-face gap. The carrier's solid mass estimate remains 1.461 g at assumed PLA density 1.30 g/cm³, leaving about 1.749 g beyond the supplier's 6.79 g D68 for the tie, buckle and ballast. Weigh the entire moving assembly to establish the 10 g target.

Position adjustment does not prove usable Hall output at every setting. A3 and A4 have different gains; equal voltages do not mean equal fields, and mechanical symmetry does not establish cancellation. Confirm headroom across actual current and payload motion, then recalibrate at the locked heights. Permanent-magnet zero-current release/control authority, coil/contact temperatures, PLA suitability, stable levitation, physical shutdown and the thin cassette's impact behavior remain physical validation requirements.
