# Front Hall rod with #6-32 hardware

This revision replaces jobs 2, 3 and 4 together. The Hall rod is now at the **front**, opposite the upright, and carries both purchased DRV5056 LPG sensors. Both sensors move vertically together. The sensor seats have lateral release openings, so the sensor and ordinary soldered wires can be removed together after releasing the retaining loop. Both helper-magnet pockets are available in the same assembly.

## Files and printing

- `JOB02_PRINT.stl`: revised head, upper front guide and accessible #6-32 clamp.
- `JOB03_PRINT.stl`: revised lower cassette/front guide plus the existing D68 moving-magnet carrier. Use the individual `03_..._PRINT.stl` for the cassette alone if the carrier is already printed.
- `JOB04_PRINT.stl`: **one common sensor rod**, including material to sand away for fitting.
- `JOB01_PRINT.stl`: existing base, unchanged. Reuse an existing print.
- `testbox1_front_632_hall_assembly.step`: full assembly as solid geometry. `five_printed_parts_assembled.step`: fabrication bodies only. The assembly shows the rod **after sanding**, while job 4 contains the larger sanding stock.
- `testbox1_front_632_hall_assembly.f3d`: native Fusion archive generated in Fusion. It contains direct solid components rather than a parametric feature history. The native generator is in `Fusion_Front632/`; the alternate CadQuery source is included for reference but its installed external kernel was blocked during this session.

Use the supplied print orientations at **100% scale, millimetres**. Changing scale to fit a screw would change the electromagnet and sensor fits. The existing X1 Carbon regular PLA baseline is a 0.4 mm nozzle, 0.20 mm layers, 6 walls and 30% gyroid infill, with the makerspace's actual filament/plate profile. Inspect the sliced preview before submission. No Bambu toolpath or physical print has been tested here.

The head prints inverted. Its top magnet pocket requires removable support from the build plate; remove that support fully. Avoid support trapped in the rod guide and nut-access path. The cassette prints with its magnet pocket upward. The rod lies flat in the supplied orientation; its small openings require short bridges rather than a separate printed support part. Keep any brim clear of neighboring objects on job 3, and remove brim and elephant-foot material from bearing surfaces.

## Hardware sizing and assembly

The changed interfaces use **#6-32 UNC machine screws and ordinary #6-32 hex machine screw nuts**, including the user's Midwest Fastener 03748 or similar. A #6-32 screw has a nominal 0.138 in (3.5052 mm) major diameter. Printed clearance holes are larger; do not tap those clearance holes. The nut provides the thread.

The nominal nut basis is **5/16 in across flats × 7/64 in thick** (7.9375 × 2.778125 mm). The captive-nut track includes printing allowance. This is a standard-size basis, not a measured manufacturer's tolerance drawing of the user's nut batch. Remove burrs and verify the actual nut enters freely before tightening. Zinc-plated 03748 nuts are steel; calibrate the sensors with the final hardware installed.

| Connection | Machine screws | Nuts |
|---|---|---|
| Head to existing upright | 4 × #6-32 × 1-1/4 in (31.75 mm) | 4 × #6-32 |
| Lower cassette through head | 4 × #6-32 × 2 in (50.8 mm) | 4 × #6-32 |
| Common rod clamp | 1 × #6-32 × 3/4 in (19.05 mm) | 1 × #6-32 in the rod track |

Use pan-head machine screws. The unchanged base has larger existing rear holes. Use #6 flat washers under the rear screw heads and nuts, and at both ends of the four cassette bolts. A clamp washer is accommodated as described by the hardware audit. The checked maximum washer envelope is Ø9.906 × 1.651 mm. Do not substitute countersunk screws at flat seats. The model does not depend on cutting a thread into PLA. Revised holes are **Ø4.1 mm (about 0.1614 in)**, larger than a 5/32 in printed-clearance baseline.

## Sand the common rod to fit

The rod is intentionally supplied with extra material on its guide faces. **Do not force the as-printed rod through the upper guide.** Sand the broad bearing faces evenly with a flat backing, checking both guide openings frequently. Remove print ridges and any first-layer lip. Keep the rod rectangular and straight; avoid rounding it until it can rotate.

The printed stock is **13 × 11 × 137 mm**. The intended finished target is **12.4 × 10.4 × 137 mm**, nominally removing 0.3 mm from each of the four long outer faces. The upper guide is 12.8 × 10.8 mm and the lower guide is 13.2 × 11.2 mm. Thus the stock deliberately interferes with the upper guide by 0.1 mm per side; the lower guide starts with extra alignment clearance. Fit against both actual openings rather than sanding blindly to a nominal number. The finished target provides running clearance, while the screw/nut clamp holds the selected height. An exact interference fit would prevent the requested adjustment. Actual PLA shrinkage and the printer's hole accuracy still affect how much sanding is needed.

Install and fit the unwired rod before the sensors. Insert its #6-32 nut through the accessible nut track, then fit the clamp screw from the open front. Loosening the screw permits vertical motion; tightening draws the rod against the bearing face. Tighten moderately so the nut does not crush the plastic. The clamp shaft remains in the closed vertical slot during normal adjustment.

## Install and remove wired Hall sensors

Use the bare LPG modified TO-92 package supplied for DRV5056A3QLPG/A4QLPG. The broad marked flat face stays **horizontal** for sensing along the vertical magnetic axis. The face may point up or down as required by polarity. Identify the pins from TI's package view: 1 VCC, 2 GND, 3 OUT. Flipping the case reverses the outer pins' physical order.

Each position has a **4.3 mm-wide × 1.9 mm-high body seat**, a 3.8 mm native-pin bay, and a **3 mm-high opening through the right side (+X)**. The sensor is retained by its body shoulder and a removable nylon loop, not by loading its soldered pins. Use a nylon loop no wider than **2.5 mm** and no thicker than **0.8 mm**. Its return at the wire exits is raised above the pins; the side spans slope down to the proud sensor-body edge. A straight horizontal wrap would pinch the leads. Keep the buckle clear of the openings, the neighboring parts and the pins.

To remove a sensor without desoldering:

1. Turn off the apparatus and support the sensor/wires.
2. Release the sensor's retaining loop and the nearby wire strain relief.
3. Slide the sensor sideways through the open release path. Its attached wires follow out through the same open side; solder joints do not have to pass through a tight closed body hole.
4. Move it to a different port or replace the holder, then refit its loop and strain relief.

The openings are for ordinary small wire-to-pin joints as requested. No oversized connector envelope is specified. Keep individual joints insulated against shorts and provide flexible slack for the full rod stroke. Solder with the sensor removed from the PLA and the heat kept away from the holder. Flexible wire motion, real tie buckles and actual solder joints still need an assembly check.

## Position adjustment

There are five upper and five lower positions, with 8 mm spacing. Nominal seat-floor Z coordinates are:

| Zone | Seat-floor Z, mm |
|---|---|
| Upper | 207.5, 215.5, 223.5, 231.5, 239.5 |
| Lower | 117.5, 125.5, 133.5, 141.5, 149.5 |

The common fine adjustment is **−4 to +4 mm**. It moves both installed sensors by the same amount. The 40 mm total reachable range per zone comes from choosing a coarse port and adding the fine stroke; it is not a continuous 40 mm sliding stroke. Z is measured from the base underside. These are seat floors, not the Hall die's exact position. The electromagnet spans nominal Z170–190 mm. The finished clamped sensor center is X90/Y44.625 mm, approximately **20.375 mm in front of the coil axis**. This changes the field from earlier holder revisions, so recalibrate at the final position.

## Magnets above and below the electromagnet

Both fixed DC1 pockets are available together. Each is nominal Ø19.6 × 7 mm for the purchased Ø19.05 × 1.5875 mm disks. The assembly illustration allocates the user's **four total disks** between the pockets. It does not imply that eight disks were purchased. Capacity for a stack is separate from the number to install.

The lower cassette retains its stack beneath the coil. The upper pocket uses the included **nonprinted 50 × 10 × 1 mm retainer strip**, with two Ø4.1 mm holes at 38 mm centers, secured diagonally under the appropriate retaining-bolt washers/nuts. Use nonmagnetic strip material; `NONPRINT_632_retainer_cut_template.svg` is a cutting template, not another print job. Check its scale mark when printing on paper. Both pockets need measured nonmagnetic shims to prevent axial movement. Four maximum-tolerance disks can total 6.75 mm; four nominal disks total 6.35 mm. Fewer disks need more total shim thickness. Measure each actual stack and retaining arrangement rather than forcing nominal shims.

Adding, flipping or redistributing magnets changes both the sensor field and the levitation force. **Neither top placement nor simultaneous top/bottom placement is proven to prevent saturation.** Check the A3/A4 outputs across coil current and intended payload motion, and verify that the moving magnet releases at zero current. The two sensor gains differ; matching voltages does not mean matching fields.

The nominal Ø25 × 20 mm electromagnet fit and the D68 moving-magnet carrier remain. Measure the actual coil and use appropriate nonmagnetic compliant shims for its locating clearance. The D68 carrier still needs its separate nonprinted retaining loop and a measured total moving mass. The 10–20 mm command gap is from the coil's lower face to the top of the moving D68 magnet.

## What has and has not been established

The exported-file review reports describe the actual STEP/STL checks, intentional sanding interference, hardware clearances and motion paths. CAD fit does not establish clamp friction, PLA temperature suitability, force versus current/gap, zero-current release, Hall signal headroom or stable levitation. Those depend on the physical hardware and control system. See `HARDWARE_EVIDENCE.md` for the source basis.
