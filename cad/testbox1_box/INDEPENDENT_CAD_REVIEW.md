# Independent CAD review — 10 November 2026

Reviewer: separate checking agent, independent of the model builder. Result: **67 geometry/export checks passed** against the delivered files. See `independent_check_results.json` for machine-readable evidence and `independent_check.py` to reproduce the checks. The checker reimports the exported STEP and reads the exported STLs; it does not import or reuse the builder's geometry functions.

This is a nominal mechanical prototype with checked geometry. Actual purchased component fit and successful levitation remain unverified. No physical prototype, thermal test, magnetic simulation, force measurement, or closed-loop suspension test was performed. Fusion access was denied, so opening, saving and regenerating this model in Fusion were not independently exercised.

## Sources and interpretation

The checked requirements come from `../../hardware.qmd`, `../../docs/proposal.md`, and `../../design.qmd`: Heyiarbeit JF-XP2520-12V electromagnet, nominal diameter 25 mm and height 20 mm; fixed N42 helper disk, 3/4 inch × 1/16 inch; total moving mass 10 g; commanded surface gap 10–20 mm measured from electromagnet lower face to moving magnet upper face. The project explicitly leaves the suspended magnet undecided and requires force, sensor and temperature characterization.

The [Uzzors2k reference](http://uzzors2k.com/index.php?page=magneticlevitation) was inspected using the retrieved page and both completed assembly photographs. Its broad transparent rear support, top cantilever, suspended electromagnet and wood base are reflected in this assembly. The current CAD uses separate bolted rear and top plates rather than a heat-bent sheet. The reference does not give structural frame dimensions; the 180 × 160 mm base, 90 mm frame width and 6 mm plates are design choices. The reference's 40 mm diameter × 25 mm coil is different from this project's 25 × 20 mm coil.

The [K&J DC1](https://www.kjmagnetics.com/dc1-neodymium-disc-magnet) is a candidate matching the documented helper, not an order-confirmed part. Parent-agent supplier research reports ±0.1 mm dimensional tolerance; the checker therefore tested a 19.15 mm diameter × 1.69 mm thick worst-case helper envelope. Kuali messages establish vendor/order status but provide no component line items.

The [TI DRV5055 datasheet](https://www.ti.com/lit/ds/symlink/drv5055.pdf) identifies package-dependent sensing direction. A package must be oriented with its sensitive axis along the desired field direction. A generic carrier envelope cannot establish saturation margin or correct purchased-package fit.

## Independently verified geometry

| Item | Checked result |
|---|---|
| STEP components | All 16 individual files reimport as one valid solid each; assembly reimports with 16 solids |
| Interference | All 120 component pairs have zero overlapping solid volume, including the nominal reference components |
| Manufacturing exports | All 11 fabricated-part STLs have closed two-triangle edge incidence, no duplicate-vertex degenerate triangles, and bounding dimensions matching STEP within 0.07 mm |
| Base | 180 × 160 × 18 mm |
| Rear acrylic | 90 × 6 × 172 mm; occupies z = 18–190 mm |
| Top acrylic | 90 × 97 × 6 mm; occupies z = 190–196 mm |
| Electromagnet reference | 25 mm diameter × 20 mm; bottom face z = 170 mm |
| Helper nominal reference | 19.05 mm diameter × 1.5875 mm; shown seated at z = 168.1 mm |
| Helper tolerance fit | 19.15 × 1.69 mm envelope fits; 0.45 mm diametral pocket clearance and 0.21 mm remaining axial clearance before any adhesive/shim |
| Payload sweep | Illustrative 12.7 mm diameter × 6 mm payload clears every fixed component at each 1 mm step over the complete 10–20 mm commanded gap |
| Lower stop | Guard bottom z = 162 mm; 2 mm clearance to payload top at the 10 mm minimum EM-face gap; contact would occur at an 8 mm EM-face gap |
| Hall envelope | Lower allowance z = 164–166 mm; cassette underside z = 167 mm gives 1 mm nominal clearance |
| Bolting | Four cassette, two guard, four head, two upper carrier and two arm/bracket vertical shaft paths are uninterrupted; conservative 7 mm diameter washer/nut envelopes outside each stack clear adjacent solids |
| Rear clamp | Base wood screws at x = 75/105 mm miss horizontal panel bolts at x = 60/120 mm |

Nominal bore clearance for the electromagnet is 0.6 mm diametral. It is clearance for the stated 25 mm envelope, not a supplier-tolerance guarantee. Export checks establish closed meshes and matching dimensions, not printer calibration, stiffness or printed strength.

## Corrections required and verified during review

1. Cassette fastener holes originally ended against the solid top plate. Matching top-plate holes were added.
2. Guard fasteners originally emerged into the cradle. Matching cradle/top-plate holes were added.
3. Rear vertical wood screws originally crossed the horizontal clamp bolts. Their x positions were separated.
4. Upper Hall-carrier fastener positions were moved outward and the carrier widened to clear the cradle flange and leave washer/nut space.
5. The cassette underside was raised to give the lower Hall allowance 1 mm clearance.

The exported solids, not merely the source, were checked after these corrections.

## Assembly and fabrication observations

The cassette provides positive support under the electromagnet, independent of an unverified mounting thread. A 10 × 6 mm side exit is present for its leads. Removal of the cassette permits helper reversal/replacement. The assembly needs the specified bolts, nuts and washers; they are assembly requirements even though their detailed solid geometry is omitted from the exported assembly.

Keep acrylic as cut/drilled sheet, plywood/hardwood as the named materials, and the protective lower guard as 2 mm polycarbonate. Do not treat every STL as an instruction to print every part in plastic. Printed PETG brackets and cradle require appropriate orientation, actual fastener fit and a load/temperature check. The small 1.1 mm helper-pocket floor is a fabrication detail to inspect in the slicer and finished part.

The broad rear panel/top overhang and wood base match the reference layout. A catch tray and package-independent sensor carriers add the project's requested mechanical provisions. No exact controller-board, supply or E-stop panel fit is established because those mounting envelopes were not supplied; the CAD deliberately does not invent them.

## Remaining limits that affect a one-shot build

- **Helper position:** The nominal helper has 0.3125 mm axial freedom. Magnetic attraction can lift it against the electromagnet, so the pictured seated-floor location is not a mechanically fixed operating position. Secure a repeatable location with a measured nonmagnetic shim or thin retaining adhesive after checking polarity, and include its thickness in the 1.9 mm pocket stack. With a 1.69 mm worst-case disk and 0.10 mm adhesive the nominal remaining axial clearance is 0.11 mm. Calibrate the actual installed assembly.
- **Gap definition:** Keep the electromagnet face as the 170 mm reference. The helper, sensor and guard occupy some of the space below it. The lower guard leaves only 2 mm nominal mechanical margin at the commanded 10 mm gap. Tolerance, payload tilt, control overshoot and any additional sensor mounting thickness reduce that margin. This CAD does not prove contact-free motion.
- **Purchased components:** Measure coil diameter/height/lead location, helper size, actual Hall package plus carrier, and complete moving payload before cutting or printing final parts. The lower Hall allowance is only 2 mm total height; a normal board plus a through-hole package may exceed it. The payload shown is explicitly hypothetical, not a selected or ordered part. A larger or taller moving carrier needs a renewed sweep check.
- **Magnetics and control:** A 10 g moving assembly needs approximately 0.0981 N upward force at equilibrium. A contact holding-force rating does not prove that force at 20 mm. Measure usable force versus gap/current with the helper installed, verify helper polarity and zero-current release, check Hall output headroom and calibration over the complete sweep, and demonstrate stable closed-loop operation and fault shutdown.
- **Heat and structure:** Verify coil temperature, cradle material temperature, fastening security and frame deflection on the physical assembly. The geometry check is not a structural analysis or thermal rating.
- **Fusion:** The STEP file is suitable for import into Fusion as solid geometry. Native Fusion timeline creation and any `.f3d` export must be reported separately only after actual Fusion execution; they were not validated here.

Approval is therefore **geometry/export pass for the documented nominal prototype**, with measured hardware fit and operating performance still open.
