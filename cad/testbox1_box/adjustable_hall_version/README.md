# Vertical Hall adjustment — revised jobs 2 and 3

Both Hall sensors now move **vertically**, closer to or farther from the electromagnet. Each exact LPG sensor sits flat in a fitted horizontal pod on a sliding carriage. The carriage follows a keyed vertical rail with **five height holes at 8 mm spacing**. Selecting a hole sets coarse height; loosening the carriage bolt allows **±4 mm of continuous fine movement** before tightening it again. The five overlapping fine ranges provide **40 mm of continuous operating travel per sensor**.

The bare Hall body must remain horizontal so its sensing direction is vertical. Consequently the height-index holes are in the rail, and the fitted body seat is in the horizontal sliding pod; the Hall package is not pushed sideways into a vertical hole. Both mounts accept either DRV5056A3QLPG or DRV5056A4QLPG and permit the marked face up or down.

## Files to print

**Job 1 is unchanged, byte for byte. Do not reprint an existing base.** Its STL and STEP are copied directly from the purchased-parts version. The D68 carrier's individual STL/STEP are also unchanged.

| File | Contents / orientation |
|---|---|
| `JOB02_PRINT.stl` | Revised head with upper rail guide; broad arm top down, as previously |
| `JOB03_PRINT.stl` | Revised lower cassette with rail guide **plus the unchanged D68 carrier**, both broad bases down |
| `JOB04_PRINT.stl` | Four new pieces: upper rail, lower rail, upper sensor carriage and lower sensor carriage, already positioned |
| `03_four_DC1_stack_cassette_lower_LPG_seat_PRINT.stl` | **Cassette only**: use this instead of job 3 if the D68 carrier is already printed |

The supplied full assembly has **eight printed pieces in four total jobs**, including the existing base and carrier. Completing an existing purchased-parts build requires the changed head/cassette and the four small job-4 parts. Do not print both the combined job files and their duplicate individual components.

All files are millimetres at 100% scale and fit the HMC Bambu X1 Carbon. Center each whole job on its plate; preserve its supplied relative placements and orientations. Job 3's two components have 17 mm separation, leaving 1 mm between two 8 mm brims. Job 4's pieces are separate bodies; keep them in their supplied positions or move them in-plane without rotating them onto an edge.

## Actual height ranges

The sensor package stays at **X104, Y65**, 14 mm radially from the electromagnet axis X90/Y65. Only its height changes. Rail center is X145/Y65. Heights below specify the **body seat floor**, not an assumed exact die location.

| Mount | Body seat floor Z | Relative to electromagnet |
|---|---:|---|
| Upper | **203.5–243.5 mm** | 13.5–53.5 mm above EM top Z190 |
| Lower | **113.5–153.5 mm** | 16.5–56.5 mm below EM bottom Z170 |

The solid head and cassette limit the closest positions; the pods do not travel through those parts. The maximum sensor body extends 1.62 mm above its seat floor, and the exact sensitive point depends on package orientation. These are positioning ranges, not a field-range or accuracy claim.

| Hole counted from the rail's mounting shoulder | Upper index-hole Z | Upper seat-floor fine range | Lower index-hole Z | Lower seat-floor fine range |
|---:|---:|---:|---:|---:|
| 1, closest | 214.5 | 203.5–211.5 | 147.5 | 145.5–153.5 |
| 2 | 222.5 | 211.5–219.5 | 139.5 | 137.5–145.5 |
| 3 | 230.5 | 219.5–227.5 | 131.5 | 129.5–137.5 |
| 4 | 238.5 | 227.5–235.5 | 123.5 | 121.5–129.5 |
| 5, farthest | 246.5 | 235.5–243.5 | 115.5 | 113.5–121.5 |

The carriage slot is **11.4 mm overall × 3.4 mm wide**. With an M3 shaft it permits approximately ±4.2 mm to the physical slot ends; use the documented **±4 mm** range to retain 0.2 mm end clearance. The fixed shoulder stops inward overtravel at the nearest setting. Closed slots keep the carriage captive while its bolt remains fitted; removable outer end-stop bolts retain it when changing coarse holes.

## Hardware and assembly

Additional adjustment hardware:

| Purpose | Quantity / hardware |
|---|---|
| Fix rails to head/cassette guides | 2 × **M3 × 30**, 2 regular M3 nuts, 4 flat washers |
| Coarse/fine carriage lock | 2 × **M3 × 25**, 2 regular **2.4 mm-thick** M3 hex nuts, 2 front flat washers |
| Outer rail end stops | 2 × **M3 × 20**, 2 regular M3 nuts, 2 flat washers |
| Sensor and lead retention | Nylon ties no wider than **2.5 mm**, plus flexible insulated wiring |

Use nonmagnetic hardware where practical. The nut tracks are for ordinary M3 nuts, **not taller locknuts or Nyloc nuts**. Standard 5.5 mm across-flats nuts fit the 5.8 mm-wide track with their flats aligned across X; the track permits their vertical movement during fine adjustment. Do not substitute an oversized nut or force one into PLA.

1. Install the revised head and cassette using the existing M4 × 30 rear-joint hardware and four M3 × 45 head/cassette bolts. The Ø26 coil locating rim, coil support, 3–4-disk DC1 pocket, optional top pocket and their interfaces are preserved.
2. Insert the **upper rail from above** into the head's rectangular guide. Its widened root shoulder rests on the head at Z200. Align the mounting hole at Z195 and secure it with an M3 × 30 bolt, washers and nut. The rectangular section keys the rail against rotation; the through-bolt positively fixes its height. It is not a friction-only mounting.
3. Insert the **lower rail from below** through the cassette guide. Its shoulder seats against the cassette underside at Z162. Secure its mounting hole at Z166 with the second M3 × 30.
4. Leave the outer end-stop bolts removed. Slide the upper carriage onto the upper rail from the free top end, and the lower carriage onto the lower rail from the free bottom end. In both cases the fitted sensor pocket faces **up** and projects inward toward X104. Then install the M3 × 20 outer stop bolts at **Z266 upper / Z96 lower**, with washers/nuts. The integrated mounting shoulders and these cross-bolts prevent the carriages leaving either rail end.
5. Put a regular 2.4 mm M3 nut into each open rear vertical nut track. Insert the M3 × 25 fine-lock bolt with a front washer through the carriage's rounded slot, the chosen rail hole and the nut. The nut is held against turning by its flats but can move within the track as the carriage makes its fine adjustment. Both ends remain accessible.
6. Support the pod, loosen the fine bolt slightly, move it vertically within the current ±4 mm interval, and tighten it moderately. To change coarse hole, support the pod and remove/reinsert that bolt into the next hole; leave the outer stop bolt installed. After locking, check that the pod holds its selected height without damaging or crushing the print. Fine positioning is manual sliding and clamping, not a micrometer or lead screw.

The lock uses a through-bolt, washer and captive nut. The screw shaft locates in a fixed rail hole, while friction at the tightened carriage faces locks the continuous position within the closed slot. The key keeps the pod horizontal; no printed thread, unsupported snap-fit or unverified press-fit is required.

## Fitted Hall seats and moving wiring

The LPG body seat is **3.7 × 4.5 mm**, accepting the maximum 3.25 × 4.1 × 1.62 mm package laid flat. Its left stop and side shoulders locate the body. A 2.7 mm-wide transverse groove lowers the tie ledges, so a tie can press the actual body rather than bridge over the recess. Through-slots accept ties up to 2.5 mm wide. A separate downstream tie strain-relieves the insulated wires.

The leads point toward +X, away from the coil. Leave the first **3 mm straight** after the package, gently fan to the three 3 mm-pitch channels, and insulate solder joints individually. The initial 1.27 mm-pitch lead region is open: there are no impractically thin printed dividers. Follow the **DRV5056** package view: pin 1 VCC, pin 2 GND, pin 3 OUT. Flipping the marked face reverses the outer pins' global order; do not identify them by a guessed left/right direction.

Provide **at least 150 mm of free flexible three-conductor service lead for each pod**, measured between moving and fixed strain-relief points. Maintain at least a **10 mm bend radius**. Form a loose loop behind the pod in the Y–Z plane around **X120–132, Y80–110**, away from the rail at X145 and rear panel at Y130. Guide it by hand through the complete travel before energizing; no lead may become taut, catch an index hole or pull on a soldered pin. The extra slack must accommodate the whole 40 mm travel, not merely the ±4 mm fine setting.

The revised fixed head/cassette have new through-slots at X121–124 and Y80/87.8 for the fixed strain relief. `service_wiring.json` gives routing bounds including anchor terminations. The freely routed corridor is above the head at **Z201–260**, or below the cassette at **Z100–161**; the remaining bound regions contain the fixed anchors themselves and are not claimed as empty space. Flexible wire routing is a required assembly step, not a rigid printable component or an assertion that a box is collision-free.

Both purchased sensors are **unipolar DRV5056**, not DRV5055. Check marked-face polarity and output headroom before fastening the final position. Either A3 or A4 fits either pod; decide their positions/ranges using actual measurements. Moving either sensor changes the field/position calibration. Recalibrate after changing coarse height, fine height, package face, sensor variant or helper placement. See `POSITIONING_NOTES.md` for the accompanying setup notes.

## Printing and supports

Use the actual regular-PLA X1C profile and installed nozzle (baseline **0.4 mm**, 0.20 mm layers). Keep strong walls around guides, clamp slots and rail roots. Settings and supports have not been executed in a slicer or printer here.

- **Job 2:** broad head top is on the plate. The optional top-helper pocket faces the plate and needs removable manual build-plate-origin support inside its Ø19.6 × 7 mm cavity, as in the preceding version. The vertical rail opening prints upward through the ear. Do not fill it with trapped support.
- **Job 3:** cassette and existing D68 carrier sit on their broad undersides. The deeper fixed-helper pocket opens upward. All original payload fit/retention instructions remain applicable.
- **Job 4 rails:** both lie on their **front Y59 faces**. Their widened mounting shoulders extend only rearward, so the rail fronts are coplanar with the shoulders and touch the plate. The mounting/index holes print along the layer normal.
- **Job 4 upper carriage:** the pod underside and sleeve base are **coplanar** and sit flat on the plate. There is no raised upper pod needing support beneath it.
- **Job 4 lower carriage:** its sleeve base touches the plate, while the 36 mm inboard pod is **9 mm above it**. Add removable **build-plate-only support beneath that pod**, including beneath its tip. Leave the vertical keyed bore and open rear nut track clear; do not add inaccessible support inside them. Inspect the small slot/nut-track roofs in Studio before sending the job.

Remove support carefully and clear any loose strings from the 10.6 × 12.6 mm keyed guide bores. The rail is 10 × 12 mm, providing 0.3 mm nominal clearance per side. Confirm free sliding before installing the sensor; never force an uncalibrated or distorted fit against a soldered device. Nominal clearances do not replace printer calibration.

## Preserved magnetic and payload assembly

The nominal EM remains **Ø25 × 20**, face Z170 and top Z190. The lower Ø19.6 × 7 mm pocket captures **3–4 DC1 disks**; the optional upper pocket and nonprinted retainer arrangement remain available without another head print. Four disks leave 0.65 mm nominal axial freedom; three leave **2.2375 mm total**, so select measured nonmagnetic spacers/retention accordingly. Use only one active stack. Extra helper force can remove zero-current release/control authority; adjustment hardware does not establish a controllable plant.

For the optional top position, the nonprinted retainer is **50 × 8 × 1 mm** polycarbonate/nylon with two Ø3.4 holes at **38 mm centers**, fitted diagonally over the stack between two opposite existing M3 head bolts, below their washers/nuts. Its underside is Z200; nominal four disks need a measured 0.65 mm pad, three need 2.2375 mm. The actual-scale `OPTIONAL_retainer_cut_template.svg` and matching optional STEP are included. Check actual hardware and spacer thickness rather than forcing the nominal stack.

The unchanged D68 carrier holds the Ø9.525 × 12.7 magnet with the specified nonprinted **over-top retaining loop**, at most 3 mm wide × 0.8 mm thick, buckle below the carrier. The entire moving magnet/carrier/loop/ballast must be **10 g**. The unchanged solid-volume mass bound for the carrier is 1.461 g at assumed PLA density 1.30 g/cm³, leaving 1.749 g after the supplier's 6.79 g magnet for loop/ballast/other material; weigh the actual assembly.

The 10–20 mm command is still the distance from EM face to D68 top. The cassette underside is Z162; including the 0.8 mm moving loop leaves only **1.2 mm nominal margin** at the 10 mm command. The adjustable pods remain radially beside this payload sweep and do not redefine that gap.

Regular PLA's suitability at the actual coil/contact temperature, measured field headroom, fixed-helper control authority and stable free levitation remain unverified operating conditions. No physical run, thermal test or native Fusion regeneration was performed here.

## CAD and verification files

- `testbox1_adjustable_hall_assembly.step`: full assembly, parked at the nearest documented settings.
- `eight_printed_parts_assembled.step`: eight fabrication solids only.
- `JOB01_PRINT.*`: byte-identical prior base job; jobs 2/3 updated, job 4 adds four adjustment pieces.
- Individual assembled/print STEP/STL files, `adjustment_ranges.json`, `service_wiring.json`, `component_manifest.json`, and reproducible `build_adjustable.py`.
- `OPTIONAL_top_stack_configuration.step` / `OPTIONAL_NONPRINT_retainer_strip.step`: preserved alternate fixed-helper arrangement.
- Independent exported-file checks and review, plus CAD-derived assembly/detail previews supplied alongside.

Reference lead sets each contain three isolated solids, so logical component entries and BRep solid count differ. References and hardware are not extra print jobs. The model provides solid geometry for Fusion import, not a recreated feature timeline. Its generator copies the original job-1 and carrier files rather than regenerating their file headers.
