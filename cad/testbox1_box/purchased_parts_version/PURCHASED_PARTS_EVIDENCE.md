# Confirmed purchased parts — November 11, 2026

The user provided these exact product links and confirmed that **three or four DC1 disks will form the fixed helper stack**. This supersedes the earlier one-disk/spare assumption. Mounts are derived from the published envelopes; actual printing tolerance and operating performance remain separate.

| Purchased item | Published mechanical facts used | Role |
|---|---|---|
| [K&J D68-N52](https://www.kjmagnetics.com/d68-n52-neodymium-cylinder-magnet) | 3/8-inch diameter × 1/2-inch length = 9.525 × 12.7 mm; ±0.1 mm; axial magnetization; published mass 6.79 g | Moving magnet; maximum published envelope 9.625 × 12.8 mm. The 10 g target leaves 3.21 g for its carrier, retention and added payload. |
| [K&J DC1](https://www.kjmagnetics.com/dc1-neodymium-disc-magnet), quantity four | 19.05 × 1.5875 mm, N42, axially magnetized, ±0.1 mm dimensional tolerance | Three or four stacked fixed helpers. Four nominal disks total 6.35 mm; maximum tolerance stack is 6.75 mm. Three nominal disks total 4.7625 mm and require a measured nonmagnetic packing shim in a four-disk holder. |
| [TI DRV5056A3QLPG](https://www.digikey.com/en/products/detail/texas-instruments/DRV5056A3QLPG/9860877) and [DRV5056A4QLPG](https://www.digikey.com/en/products/detail/texas-instruments/DRV5056A4QLPG/9860878) | Same LPG modified TO-92-3 mechanical package | Both seats must fit either sensor. The sensor bodies lie flat; soldered flying leads are permitted by the user. |
| [Heyiarbeit B08Z3J8Z4X](https://www.amazon.com/dp/B08Z3J8Z4X) | Seller identifies JF-XP2520-12V, 25 mm diameter × 20 mm height | Stationary electromagnet. The listing does not establish dimensional tolerances, usable force at a gap, or temperature under this project's duty. The mount avoids depending on an unverified mounting thread. |
| [Microchip MCP3204-CI/P](https://www.digikey.com/en/products/detail/microchip-technology/MCP3204-CI-P/305926) | 14-PDIP, 7.62 mm lead-row spacing | ADC stays on an electrically appropriate socket/breadboard/perfboard. Its bare pins are not a mechanical screw interface. No unspecified board footprint should be represented as verified. |

## Hall-sensor primary reference

[TI DRV5056 datasheet, revision C](https://www.ti.com/lit/ds/symlink/drv5056.pdf): package drawing LPG0003A and Figures 6-1/6-2. Maximum body envelope is 4.1 × 3.25 × 1.62 mm; leads have 1.27 ±0.05 mm pitch and extend 15.1–15.5 mm. The body-plus-shoulder dimension reaches 5.05 mm. LPG pins are 1 VCC, 2 GND and 3 OUT. The sensing axis is normal to the marked flat face. These are **DRV5056 unipolar sensors**, not the DRV5055 devices described in earlier project notes. Positive response requires the appropriate south-pole/field direction at the marked face; mounts permit reversal and calibration. Solder and insulate leads away from the PLA before installing them. Closely spaced printed partitions are avoided near the native lead pitch; leads fan out into wider, printable channels.

## Assembly interpretation

The proposal's 10–20 mm gap remains the electromagnet bottom face to the moving D68 magnet's top face. It is not the gap from the bottom of the helper stack or from a retention strap. The thicker helper stack requires the lower Hall mount beside the stack; placing it underneath would consume the intended travel clearance. Four printed bodies are arranged into three jobs by printing the small moving carrier alongside the cassette on job three.

The stronger fixed stack can affect zero-current attraction as well as Hall baseline and headroom. CAD does not establish that reducing coil current releases the target, that the two sensor fields cancel, or that the controller has sufficient force range. The actual stack/polarity, sensor readings, coil temperature and force/current range must be characterized for the assembled plant. No old one-disk calibration should be carried over as measured evidence for this configuration.
