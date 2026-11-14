# Independent review — three-print PLA version

11 November 2026. Reviewed by a separate checking agent. **38/38 checks passed against the final exported files.** These results apply to this three-print folder, not to the older eleven-part assembly. Evidence: `independent_check_results.json`; reproduction: `independent_three_print_check.py`. The checker imports STEP and reads STL directly, without importing the builder's generator.

## Geometry and print orientation

Exactly three fabrication solids are present. All three are valid single solids and all three final STL meshes are closed, connected manifolds with matching dimensions. The complete assembly contains those three parts plus five reference envelopes; all eight solids are valid and all 28 component pairs have no overlapping solid volume.

| Print | Actual bed envelope × height | Actual flat bed contact |
|---|---|---|
| Integrated base/upright/tray | 180 × 160 × 190 mm | 28,800 mm²; broad base underside |
| Cantilever/head | 90 × 103 × 40 mm | 8,937.7 mm²; broad arm top face |
| Helper/sensor/guard cassette | 52 × 8 × 52 mm | 256 mm²; front end wall and both strips |

The delivered print orientations were checked by transforming the assembled STEP independently and comparing solid volume. The frame is **not standing on its base edge**. All parts fit inside a central 220 × 220 mm region and a 256 mm build height. Print one of each in separate jobs. Part 3's narrow footprint needs the specified 8 mm brim and reliable adhesion.

Design review removed the lower cage ring that would otherwise create long unsupported bridges. The four coil posts now grow from the inverted top plate. The cassette's two end walls connect its guard and upper plate; the closing wall spans only a 3 mm service gap. Small horizontal fastening holes, the 12 × 8 mm upper sensor recess and the shallow vertical helper recess still need inspection in the actual sliced preview. No Bambu Studio slicing, printer-profile validation or physical print was performed; a geometry review is not proof of toolpath quality.

The initial head STL contained a tessellation T-junction and failed mesh closure. The builder repaired the triangle conformity without changing the STEP geometry. The final delivered STL was reread and passed; the failure was not ignored or waived.

## Assembly and clearance

- Four M4 × 30 mounting paths, 7 mm socket heads, 9 mm washers on both sides and conservative nut envelopes clear the geometry. The 22 mm plastic stack plus two 0.8 mm washers and a 3.2 mm nut leaves 3.2 mm nominal thread protrusion. Nuts are accessible behind the upright; front key access clears the coil and side gussets.
- Four M3 × 40 cassette paths, maximum 6 × 3 mm lower socket heads, upper washers and upper nuts clear. **No lower washers:** a 7 mm washer would touch the guard. Maximum 6 mm heads have about 0.435 mm nominal lateral clearance. The 33 mm stack plus 0.5 mm upper washer and 2.4 mm nut leaves 4.1 mm nominal thread protrusion.
- The nominal 25 × 20 mm electromagnet can insert from below with the cassette removed. A chosen 25.5 × 20.6 mm tolerance scenario also fits the 26 mm bore and 20.8 mm cavity; this scenario is a design allowance, not a verified supplier tolerance. Fit measured nonmagnetic shims to locate the actual coil without forcing it or loading the sensor pocket.
- A 4 × 2 mm lead envelope exits radially through the open cage. The purchased coil's actual lead location and bend radius remain unverified.
- The 19.15 × 1.69 mm worst-case helper candidate fits the 19.6 × 1.9 mm pocket. Nominal axial freedom is 0.3125 mm; the magnet may lift toward the EM. Secure a measured, repeatable position with a suitable thin nonmagnetic shim/retaining adhesive and calibrate that installed position. Adhesive is part of the thickness stack.
- A 12 × 8 × 2 mm lower sensor/carrier envelope inserts laterally through the 3 mm service gap. The total 2 mm includes carrier, insulation and adhesive. The actual ordered Hall package may not fit this envelope; it must also be oriented for axial field sensing.
- The illustrative 12.7 mm diameter × 6 mm payload clears the entire 10–20 mm commanded EM-face gap in 1 mm steps. At the 10 mm command, its upper surface is Z160 and the guard underside is Z162: only **2 mm nominal margin**. The physical stop corresponds to an 8 mm EM-face gap. Payload tilt, different dimensions, tolerances and control overshoot were not validated.

The helper and sensor carriers are integrated into the three prints. Bolts, nuts, magnets, tape/shims and electronics remain required assembly items. The orange payload and green sensor bodies are reference envelopes and must not be printed as project hardware.

## Conditional stiffness estimate

For an idealized 5 N downward head load, 65 mm arm lever, 90 × 12 mm upright, 80 mm free upright length above the gussets, 90 × 10 mm arm and **assumed effective elastic modulus 500 MPa**, elementary beam calculations give:

- Upright rotation contribution to vertical head drop: 0.261 mm.
- Arm bending: 0.122 mm.
- Upright compression: 0.002 mm.
- Total idealized drop: approximately **0.385 mm**.

This calculation helped select a 12 mm upright and higher gussets instead of the earlier 8 mm upright. It is a scenario, not a qualified printed-PLA property or structural guarantee. Joint slip, transverse plate bending, gusset flexibility, layer adhesion, voids, creep and heat are excluded. The frame must be checked assembled under its actual load; the 2 mm stop margin must not be treated as available deflection allowance.

## Remaining release conditions

The design is now a checked three-print mechanical layout for the documented nominal coil/helper and assumed payload. **Regular PLA thermal suitability remains unestablished.** Open windows improve airflow but do not prove that the coil, helper contact, shims or loaded PLA remain within the actual filament's temperature capability. Confirm coil/contact temperatures and an appropriate operating limit before relying on a powered demonstration or unattended operation. No numerical safe duty cycle can be inferred from these files.

The Kuali notifications identify vendors/order status but not exact line items. Confirm the actual coil, sensor package and complete 10 g moving payload dimensions. Establish helper polarity, sensor headroom, useful force at 10–20 mm, stable control and physical shutdown on the real assembly. These operating requirements cannot be guaranteed by collision checks or by a CAD file. Fusion import/save and native timeline generation were not exercised.
