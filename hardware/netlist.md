# Proposed circuit netlist — implementation reference, not final CAD

| Node / connection | Endpoints / constraints |
|---|---|
| LOGIC_3V3 | MCP3204 VDD/VREF, Hall VCC, current amplifier VS, 3.3 V interlock logic; local bypass capacitors |
| AGND | ADC AGND/DGND, Hall GND, current amplifier GND/REF1/REF2; single low-impedance reference to logic/power ground |
| VCOIL | fused supply after E-stop → shunt positive; flyback cathode |
| COIL_TOP | shunt negative → coil positive |
| SWITCH | coil negative → MOSFET drain → flyback anode |
| PGND | MOSFET source → supply negative; driver GND; current returns kept off AGND wiring |
| CURRENT_SENSE | INA240 IN+ Kelvin to shunt positive; IN− Kelvin to shunt negative; OUT to CH0 and comparator |
| HALL_PRIMARY | linear Hall OUT → ADC CH1; verify signal stays within calibrated interval |
| HALL_REFERENCE | linear Hall OUT → ADC CH2 |
| DRIVER_SUPPLY | regulated gate-driver supply with local ceramic + bulk bypassing |
| GATE | driver output through selected gate resistor → MOSFET gate; gate-source pulldown |
| DRIVE_LOGIC | PWM AND FPGA_ENABLE AND MCU_PERMIT AND HEALTHY → driver IN+; IN− to ground |
| HEALTHY | normally-safe E-stop auxiliary + overcurrent comparator; false on open/disconnected logic; FPGA fault_n input |

Package-specific pin numbers for Hall, amplifier, MOSFET, driver, comparator, and logic await exact ordering codes. The ADC and board pin map is specified in docs/hardware.md. Complete the KiCad sheet, component ratings, comparator polarity/hysteresis, fuse, connectors, and power layout after coil characterization. Do not present this table as a finished fabrication schematic.
