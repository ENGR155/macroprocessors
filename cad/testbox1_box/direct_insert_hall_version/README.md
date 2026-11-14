# Direct-insertion common Hall rod — one holder print

This revision follows the side-view sketch: **one printed rod carries both Hall sensors directly through transverse slots**. There are no separate rails, sliding carriages or sensor pods. The sensors move together when the rod is moved vertically. Their broad marked faces stay horizontal, preserving a vertical sensing axis.

## Print files

| File | Use |
|---|---|
| `JOB04_PRINT.stl` | **One connected holder**, 10 × 137 × 12 mm in its supplied flat print orientation. Print one copy. |
| `JOB02_PRINT.stl` | Revised head with the common rod's upper guide, clamp and nut-access pocket. |
| `JOB03_PRINT.stl` | Revised lower cassette guide plus the unchanged D68 carrier. |
| `03_cassette_common_rod_guide_PRINT.stl` | Cassette alone, if the D68 carrier is already printed. |
| `JOB01_PRINT.stl` | Unchanged base; reuse an existing one. |

The complete stand has five printed pieces in four jobs. **Only the holder is one print**, not the entire levitation stand. New guide locations in jobs 2 and 3 are required: this rod does not fit the preceding outboard rail/carriage guides. Job 1 and the D68 carrier are preserved byte-for-byte.

Keep the supplied orientations and 100% millimetre scale. For the X1 Carbon's regular PLA profile, retain the established 0.4 mm nozzle / 0.20 mm layer baseline, strong walls and calibrated settings. The holder lies on its broad front face and needs no separate support structure: its small transverse ports have short bridges. Inspect the sliced preview; no Bambu toolpath or physical print was tested here. Job 2 still needs removable support inside the optional top helper pocket. Do not fill its rod opening or rear nut-access pocket with trapped support. Job 3 prints flat with the magnet pocket upward.

## How the sensor slides into the rod

Each port is sized for the purchased **DRV5056A3QLPG or DRV5056A4QLPG**, not a sensor PCB. The maximum LPG body is 4.1 mm wide × 3.25 mm long × 1.62 mm thick. The inboard mouth is 4.5 mm wide × 1.9 mm high and engages 2 mm of the body. The body projects nominally 1.25 mm toward the coil. Slide it from the **−X / coil-facing side**, with its three native-pitch leads pointing through the rod toward +X.

A 3.6 mm-wide × 1.9 mm-high lead passage continues through to the opposite face. It clears the maximum 3.19 mm bare lead span, while its narrower width forms a body shoulder. Do not force the device, spread the pins inside the tunnel, or assume this is a calibrated press fit. The sensor's marked flat face may face up or down; identify pins from the TI package view before wiring. Pin 1 is VCC, pin 2 GND and pin 3 OUT. Flipping the face changes the outer pins' physical order.

Bare leads extend about **7 mm beyond the back of the rod** for solder access. A normal header, connector or bulky heat-shrink joint will not pass through the small lead tunnel. Install the rod and clamp first, select the coarse sensor ports, then install/wire the sensors. Use temporary test connections to choose a useful coarse location before final soldering. Slim individual leads may be fed separately if their actual insulated/joint envelope fits the passage. Otherwise a later coarse-port change requires removing the oversized joint or connector. The fully wired rod's ±4 mm sliding adjustment remains available.

## Sensor retention without pinching the leads

Use a separate **nonprinted nylon retaining loop for each sensor**, at most 2.5 mm wide × 0.8 mm thick. The loop crosses the proud front edge of the package, follows the sloped grooves on the rod's two sides, and returns in the rear groove **3 mm above the pin-exit level**. The rear return must stay in that raised groove; a straight horizontal wrap across the pin exits would pinch the three leads. Keep the buckle on a clear side, away from the pins and guide openings. The model includes the intended routed loop envelopes; actual ties and their buckles are assembly items.

The rear width shoulder and front loop retain the sensor together. Do not rely on friction alone. Add separate wire strain relief and flexible service slack; soldered sensor pins must not carry cable loads. Solder with heat controlled and the plastic protected, or use verified slim prewired leads that fit the passage. Never put the iron against the rod or IC body.

## Install and lock the common rod

1. Assemble the revised head and cassette with the existing M4 × 30 rear-joint and M3 × 45 head hardware. The original electromagnet, DC1 stack pockets, optional upper retainer and payload mounting remain.
2. **Before fitting either sensor**, pass the rod through both coaxial guides. The upper opening is 10.8 × 12.8 mm; the lower opening is 11.2 × 13.2 mm, allowing extra alignment clearance. The guide slots are near the coil at X113/Y65, rather than at the earlier X145 rail position. The keyed rectangle limits rotation.
3. Place one ordinary **M3 hex nut, 5.5 mm across flats × 2.4 mm thick**, in the rear track within the rod. Use the open-top pocket behind the upper guide to insert and hold it. A thicker locking nut will not fit. Prefer brass or verified nonmagnetic hardware near the sensors; ordinary steel hardware can change their magnetic readings.
4. From the front, insert an **M3 × 20 mm socket-head bolt** through the Ø7 tool recess, the upper guide and the rod's closed adjustment slot into that nut. The socket head sits at the end of the counterbore, at Y54. Use a sufficiently long Allen key. No front washer is required inside the counterbore.
5. Tightening pulls the rod against the upper guide's front bearing face; it does not require squeezing the whole rigid guide sleeve closed. The lower guide is a free alignment bearing. Tighten moderately and verify that the locked rod holds its height without crushing PLA.
6. Loosen the bolt slightly to move the rod, then tighten it before operation. Keep the shaft engaged in the closed slot: it provides positive capture while adjusting. The documented travel is **−4 to +4 mm** from the nominal position, with 0.2 mm allowance to the physical slot ends. Remove the bolt only while supporting an unwired rod for installation/removal.

## Coarse positions and coupled movement

Five body ports in each zone are spaced 8 mm apart. Choose one upper and one lower port. The **same fine displacement applies to both sensors**; they do not have independent fine adjustments.

| Zone | Port floor Z at nominal rod position | Combined coarse-plus-fine seat-floor range |
|---|---|---|
| Upper | 207.5, 215.5, 223.5, 231.5, 239.5 mm | 203.5–243.5 mm |
| Lower | 117.5, 125.5, 133.5, 141.5, 149.5 mm | 113.5–153.5 mm |

The electromagnet spans Z170–190. These are **body-seat floors**, not a measured Hall die position. The sensor body center is nominally X108.375/Y64.6 in the clamped configuration, approximately 18.38 mm radially from the magnet axis. This differs from the former carriage's X104 position, so its calibration must not be reused. The rod slides 8 mm continuously; the 40 mm figure is each zone's total reachable range using different coarse ports, not a single 40 mm sliding stroke or two independent movements.

Choose the coarse ports and common fine displacement from actual sensor readings across the intended coil current and payload travel. A3 and A4 have different gains; equal voltages do not establish equal fields. The adjustment is for finding usable signal headroom, with no assumed cancellation. Recalibrate after locking the final configuration.

## Wiring, magnets and limits

Use flexible insulated wire with a relaxed service loop accommodating the entire common stroke, and anchor it on the fixed frame away from the rod. Guide both wire sets by hand through the full movement before energizing. Flexible wire motion and actual connector sizes have not been physically verified.

The 3–4 DC1 helper stack, optional above-coil placement and D68-N52 carrier remain as in the purchased-parts version:

- The EM is nominally Ø25 × 20 mm. Its locating bore is Ø26 mm and available axial height is 20.8 mm; use measured nonmagnetic compliant shims to remove play.
- The lower helper pocket is Ø19.6 × 7 mm, floor Z163. Four nominal DC1 disks total 6.35 mm, leaving 0.65 mm axial freedom; four maximum-tolerance disks total 6.75 mm. Three nominal disks leave **2.2375 mm total** to fill. Choose shims from actual measurements rather than forcing a nominal stack. Bolt the cassette with four M3 × 45 socket-head bolts, upper washers and nuts. The rear head/frame joint uses four M4 × 30 bolts with washers and nuts.
- Use only one helper stack at a time. The optional top pocket has floor Z193 and the same dimensions. Its nonprinted retainer is 50 × 8 × 1 mm nonmagnetic polycarbonate/nylon, with two Ø3.4 holes at 38 mm centers, mounted diagonally under opposite upper M3 washers/nuts. The included template is actual scale; verify its scale bar.
- The D68 carrier has a Ø10 mm cup. Retain its magnet with a **nonprinted loop no wider than 3 mm and no thicker than 0.8 mm**, over the magnet face and under the base groove; buckle below the carrier. This is separate from the Hall-body loops. Do not rely on a friction-only cup. The nominal 6.79 g magnet and conservative 1.461 g solid-PLA carrier estimate leave about 1.749 g for retaining material and ballast. Weigh the complete moving assembly to establish **10 g**.

The electromagnet-to-D68-top command is still 10–20 mm. Including the specified 0.8 mm payload loop leaves 1.2 mm nominal clearance to the cassette underside at the nearest command. The helper stack's attraction, zero-current release, sensor headroom, PLA/contact temperature, clamp friction, real print fit and stable levitation remain operating measurements.

The final export checks are in `check_results.json` and `CHECK_REPORT.md`. They inspect the delivered STEP/STL files, native-pin access, coarse ports, retaining-loop clearances and conservative continuous movement. They do not establish magnetic or thermal performance. The separate review agents reached their service usage limit during this revision; the remaining model and exported-file audit were completed by the primary agent. No independent-agent final sign-off is claimed for this revision.

Open `testbox1_direct_insert_hall_assembly.step` in Fusion for the assembly. `five_printed_parts_assembled.step` contains fabrication bodies only. The files are solid geometry without a recreated Fusion feature timeline. `build_direct.py`, `purchased_geometry.py` and `conform_stl.py` support regeneration; unchanged base/carrier inputs and baseline hashes are included. [TI DRV5056 datasheet](https://www.ti.com/lit/ds/symlink/drv5056.pdf) remains the primary package/pin reference.
