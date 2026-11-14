# Exported-file check report — direct-insertion common Hall rod

12 November 2026. The final `check_direct.py` run reports **149 checks passed, no failures**. Results are recorded in `check_results.json`. The check script reads delivered STEP/STL files and does not import `build_direct.py`. It was written and run by the primary agent after the separate builder/checker agents reached their service usage limit. No independent-agent final sign-off is claimed for this revision.

## Confirmed geometry

- Five fabrication bodies are valid single solids. Job 4 is exactly one connected rod; its print mesh is a closed manifold. All individual and job meshes passed the expected connected-object count and closed-edge checks.
- Job 1 and the D68 carrier match recorded hashes of the earlier purchased-parts files. Their geometry and approved bytes are preserved.
- The bare sensor package enters through each transverse 4.5 × 1.9 mm body mouth. The 3.6 mm-wide rear bay clears the conservative 3.19 mm native lead span, including pitch/width limits and a vertical-play envelope. Larger solder joints and connectors are not claimed to fit that tunnel.
- Both selected sensor references and their retaining-loop envelopes fit without volume interference. All ten port locations were checked against the actual rod; no forced snap fit is assumed. Actual package shape and printed surface finish still affect installation.
- The entire common rod is conservatively enclosed by a solid swept prism for −4.2 to +4.2 mm travel. That prism clears the head, cassette, chosen enlarged EM envelope, both helper configurations and the full payload travel. The documented operating range is the smaller **−4 to +4 mm**.
- Each port's complete body, native-pin and retaining-loop bounding sweep clears stationary geometry and a keepout containing the payload's entire 10–20 mm travel. These per-zone checks cover all 25 upper/lower port combinations under the same coupled displacement. They do not establish independent fine movement.
- The M3 shaft, socket head and actual regular hex-nut envelope clear the rod and head at both physical and operating slot extremes. The nut's top insertion path is clear through the open service pocket. Printed fit and locking friction are not measured by these checks.
- Four maximum-tolerance DC1 disks plus 0.1 mm adhesive allowance fit each helper pocket. The enlarged Ø25.5 × 20.6 mm coil scenario remains clear; this chosen allowance is not a published supplier tolerance.

## Interpretation and installation limits

The rod is nominally 10 × 12 × 137 mm. Upper guide clearance is 0.4 mm per side; the lower guide has 0.6 mm nominal clearance per side. In the shown clamped state the rod moves 0.4 mm toward the upper front guide wall; the lower front clearance then becomes 0.2 mm. Assembly alignment and real printer dimensional error must be inspected rather than forced.

The top and bottom sensor coarse ports are 8 mm apart, and the **same 8 mm fine stroke moves both sensors together**. Each zone's union of coarse/fine settings reaches 40 mm, but it is not one continuous 40 mm slider stroke. The sensor bodies retain a horizontal marked face and a vertical sensing normal; polarity may require flipping the body.

The native leads pass through the rod. Standard bulky connectors/heat-shrink joints will not necessarily pass. Choose coarse positions before final wiring, or use independently verified slim wiring. Selecting a different port after wiring may require undoing the joints. The wired rod can still make its fine movement with suitable flexible service slack.

Retaining loops are nonprinted assembly items. Their side paths rise to a rear return above the pin exits; a straight wrap at the pin height is not the specified route. The model checks intended loop envelopes, not the shape of an unspecified buckle, flexible-wire drape or installer routing. Confirm both loops and wires physically before operation.

No slicer toolpath, physical print, magnetic-field map, sensor saturation test, force/current test, clamp load test or thermal test was performed. These are nominal geometry/mesh checks, not a guarantee of first-build levitation or PLA suitability near the coil.
