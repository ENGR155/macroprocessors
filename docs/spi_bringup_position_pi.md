# MCU-FPGA SPI wiring, communication, and debugging

**Project:** ENGR 155 magnetic levitation, Stephen Kanti Mahanty and Ben Lertwachara  
**Updated:** November 6, 2026  
**Proposal authority:** [MicroPEs_Proposal.pdf](<C:/Users/steph/Downloads/MicroPEs_Proposal.pdf>), especially sections 1, 2, and 5.

Use the **STM32L432KC as the SPI master**, with the **UPduino FPGA and MCP3204 ADC as two separately selected slaves**. The MCU acquires sensor data and estimates gap. The FPGA runs **position PI and produces PWM duty directly**. There is **no current controller and no requested-current command**.

This guide replaces the earlier current-controller SPI explanation. It combines the updated PDF with the selected Heyiarbeit JF-XP2520-12V electromagnet and DRV5056 A3/A4 through-hole sensors. It does not modify the proposal, firmware, or FPGA logic.

> **Implementation status:** The physical pin assignments below match the existing project driver and FPGA constraint file. The packet contract in section 5 is a **proposed replacement to implement on both devices**. The existing `protocol.c`, `runtime.c`, and `lev_core.sv` still describe the older current-controller architecture. Do not assume the new packets already work with those files.

## 1. What each device does

| Component | Responsibility in the updated proposal |
|---|---|
| DRV5056 Hall sensors above and below the electromagnet | Produce analog magnetic-field measurements |
| Current shunt and amplifier | Produce an analog current measurement for compensation, telemetry, and protection |
| MCP3204 ADC | Convert current and the two Hall outputs into separate 12-bit readings |
| STM32L432KC MCU | Read the ADC using SPI/DMA at 5 kHz; estimate gap at 1 kHz; handle the ESP8266/web interface and parameter transfers |
| UPduino FPGA | Run position PI at 1 kHz; apply duty limits and anti-windup; generate 20 kHz PWM; supervise command freshness and faults |
| Gate driver, MOSFET, and flyback circuit | Switch the 12 V electromagnet |
| Physical E-stop and overcurrent comparator | Disable gate drive independently of software communication |

The MCU sends **estimated gap, requested gap, measured current, validity/status, and PI configuration**. The FPGA returns **acknowledgments, applied configuration information, duty, and faults**. The webpage already has the MCU's estimated and requested gaps available locally; it does not need the FPGA to send the Hall readings back.

Current measurement does not create a current feedback controller. It is used in the MCU's magnetic-field compensation, displayed on the webpage, and checked for overcurrent. The FPGA's controlled variable is position, and its output is duty.

## 2. Connect the digital hardware

Use this proposed jumper map, which preserves the existing pin assignments:

| Signal | STM32 pin | Nucleo label | FPGA endpoint | MCP3204 endpoint |
|---|---|---|---|---|
| SCK, clock from MCU | **PA5** | **A4** | **GPIO_23** | CLK, pin **11** |
| MOSI, data from MCU | **PA7** | **A6** | **GPIO_26** | DIN, pin **9** |
| MISO, data to MCU | **PA6** | **A5** | **GPIO_27** | DOUT, pin **10** |
| FPGA chip select, active low | **PA4** | **A3** | **GPIO_25** | -- |
| ADC chip select, active low | **PA1** | **A1** | -- | CS, pin **8** |
| MCU drive permit, active high | **PA0** | **A0** | **GPIO_34**, also routed to hardware enable logic | -- |
| Ground | **GND** | **GND** | **GND** | AGND, pin **12**; DGND, pin **7** |

**GPIO_23 is the UPduino signal/pad label, not header contact number 23.** Verify the actual board labels and continuity against the [E155 development-board schematic](https://hmc-e155.github.io/assets/doc/E155%20Development%20Board%20Schematic.pdf). The FPGA constraint file uses SG48 package pad numbers.

Also, the Nucleo label **A4** is unrelated to the Hall sensor sensitivity option **A4**.

For this explicit jumper arrangement:

- Leave the **MCU-FPGA bridge DIP switches open**. Otherwise, an additional board connection can put an unexpected output on a signal.
- Use **3.3 V logic**, including the FPGA I/O bank configuration.
- Add a **10 kohm pull-up to 3.3 V on each CS line** so both slaves stay deselected while the MCU resets.
- Add a **10 kohm pull-down on drive permit**, so a reset or disconnected MCU does not request drive.
- Keep wires short, with nearby ground returns. Route SPI and sensor wiring away from the electromagnet's switching node and current loop.
- All signals need a common ground reference. Keep electromagnet current out of sensor/ADC ground wiring.
- Use the board's intended power arrangement. Do not automatically join two independently powered 3.3 V regulator outputs just because the boards share ground.
- Keep the **12 V electromagnet supply off all MCU, FPGA, Hall, and ADC signal pins**. The electromagnet connects through its power driver.

### Nucleo solder bridges

The Nucleo's **SB16 and SB18** can connect PA6/PA5 to PB6/PB7 for Arduino-compatible I2C routing. For the PA5/PA6 SPI map above, use the configuration that separates those pins: **SB16 and SB18 open**, verified against your board revision and a continuity check. Leave PB6/PB7 unused for this interface.

See [ST UM1956, section 7.10 and Table 16](https://www.st.com/resource/en/user_manual/um1956-stm32-nucleo32-boards-mb1180-stmicroelectronics.pdf). These solder bridges are different from the course carrier board's bridge DIP switches.

The retained local pin references are [hardware.md](hardware.md) and [upduino.pcf](../fpga/constraints/upduino.pcf). Their older control-loop descriptions are not the authority for this guide.

## 3. Configure the SPI link

| Setting | Value |
|---|---|
| MCU peripheral | SPI1, master, full duplex |
| FPGA role | SPI slave implemented in FPGA logic |
| Mode | **0: CPOL = 0, CPHA = 0** |
| Bit order | **MSB first** |
| MCU word size | **8 bits** |
| Final operating SCK | **1 MHz** |
| Chip selects | Separate GPIO outputs, active low |
| FPGA frame | **8 bytes / 64 clock pulses under one continuous CS assertion** |
| ADC read | **3 bytes / 24 clock pulses under its own CS assertion** |

Mode 0 means SCK rests low, receivers sample on rising edges, and transmitters advance data on falling edges. The transmitter must present the first bit before the first rising edge.

Configure **PA5, PA6, and PA7 as AF5** for SPI1. Configure PA4 and PA1 as ordinary GPIO outputs for software-controlled CS. PA4 is not being used as hardware NSS in this arrangement. With the existing driver's 16 MHz SPI peripheral clock, division by 16 gives 1 MHz; division by 128 gives 125 kHz for initial bench tests. Recalculate the divider if you change the peripheral clock.

The pin functions are in [ST's STM32L432KC datasheet, Table 15](https://www.st.com/resource/en/datasheet/stm32l432kc.pdf). The existing [board driver](../firmware/src/board_stm32l432.c) contains the retained mapping and initialization.

### Chip-select discipline

```text
ADC_CS  = HIGH
FPGA_CS = LOW
wait at least 2 us

exchange all 8 bytes, receiving while transmitting

wait for the final receive byte and SPI BSY to clear
wait at least 2 us
FPGA_CS = HIGH
```

Keep FPGA_CS low across all eight bytes. Raising it after each byte produces eight short frames. After each ADC conversion, leave ADC_CS high for at least 1 us before its next conversion. The existing driver also uses an ADC setup delay; account for all such delays in the timing measurement.

**Only one CS may be low at a time.** SCK and MOSI are shared inputs to both slaves, but only the selected slave may drive MISO. An unselected device must release MISO into high impedance. A disabled output driven to zero is not high impedance and would interfere with the other slave.

The existing [spi_frame.sv](../fpga/rtl/spi_frame.sv) provides useful mode-0 framing and MISO release behavior. Retain those features when changing the application protocol. Its 24 MHz oversampling implementation specifies SCK no faster than 1 MHz and at least 2 us CS setup/hold guards. Do not increase SCK without revisiting that implementation and timing.

## 4. Connect the ADC and the DRV5056 sensors

Power MCP3204 **VDD, pin 14**, and **VREF, pin 13**, from the quiet 3.3 V rail. Connect AGND and DGND as listed in section 2. Place local bypass capacitors near VDD and VREF, following the reference/layout guidance in the [MCP3204 datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/21298e.pdf).

| ADC channel | Input |
|---|---|
| CH0, pin 1 | Current-amplifier output |
| CH1, pin 2 | Hall A output, above the electromagnet |
| CH2, pin 3 | Hall B output, below the electromagnet |
| CH3, pin 4 | Ground if unused |

MCP3204 pins 5 and 6 are NC. Use the 14-pin MCP3204 drawing, not the MCP3208 pinout. Keep all analog inputs within the ADC's permitted input range.

### Hall sensor wiring and expected readings

For the selected **DRV5056A3QLPG / DRV5056A4QLPG through-hole TO-92 packages**:

| Sensor pin | Connection |
|---|---|
| 1, VCC | 3.3 V |
| 2, GND | Sensor/ADC ground |
| 3, OUT | Its single-ended ADC channel |

Use the package-view drawing to establish physical orientation before inserting the part. Place at least **100 nF between VCC and GND** at each sensor. See [TI's DRV5056 datasheet, pin functions and electrical characteristics](https://www.ti.com/lit/ds/symlink/drv5056.pdf).

These are **DRV5056**, not DRV5055. Their zero-field output is approximately **0.6 V**, rather than half the supply. At 3.3 V, nominal sensitivity is **30 mV/mT for A3** and **15 mV/mT for A4**. The 50/25 mV/mT figures apply at 5 V. Use the 3.3 V specifications for this circuit.

The DRV5056 is **unipolar**. Verify the sensing direction of each mounted sensor with a magnet; opposite physical locations do not guarantee both see a useful positive field. Record orientation and check for clipping over the actual current/gap range. The fixed helper magnet contributes field even with no suspended payload, so removing the payload does not create a zero-field calibration condition.

Read both outputs separately, then compensate/combine them in software. If you install an A3 and an A4 together, their different sensitivities must appear in calibration; raw subtraction of their ADC codes is not a matched-sensitivity field difference. Read two installed sensors; purchasing two of each option does not require installing all four.

### ADC transactions

The MCP3204 uses single-ended commands:

```text
CH0: transmit 06 00 00
CH1: transmit 06 40 00
CH2: transmit 06 80 00

result = ((rx[1] & 0x0F) << 8) | rx[2]
```

Here `rx[0]` is the first received byte. Each conversion uses 24 clocks. Ignore the irrelevant early receive bits and extract the final 12-bit result as above. Keep FPGA_CS high throughout the ADC transaction. See the [MCP3204 datasheet, section 6.1](https://ww1.microchip.com/downloads/en/DeviceDoc/21298e.pdf).

With VREF = 3.3 V, one ADC count is approximately **0.806 mV**. A known 1.65 V input should read near **2048**, and a true zero-field 0.6 V Hall output would read near **745**. Device offsets, reference error, and magnetic fields affect the latter; it is a diagnostic estimate, not a required exact code.

## 5. Recommended replacement packet contract

**This section is a design recommendation, not a claim about implemented code or a packet specification supplied by the PDF.** Agree on one shared MCU/FPGA definition before programming either device. Use a new command family so the old current-controller decoder rejects these packets.

Keep fixed **8-byte frames**, and use separate packet types for position, measurement/status, and configuration. That preserves the proposal's short bus transactions without trying to fit gap, target, current, two gains, flags, sequence, and CRC into one frame.

### Common command envelope

| Byte | Meaning |
|---:|---|
| 0 | Packet type, including enable meaning where applicable |
| 1 | 8-bit sequence number for that packet type |
| 2-5 | Four-byte payload defined by the packet type |
| 6-7 | CRC high byte, then low byte |

Use **big-endian** multibyte fields. Pack fields explicitly rather than transmitting a C structure, whose padding and byte order may differ.

One concrete command assignment is:

| Type | Name | Bytes 2-5 |
|---|---|---|
| `B0` | POSITION_DISABLED | Estimated gap `uint16`, requested gap `uint16` |
| `B1` | POSITION_ENABLED | Same layout; requests enabling when all other conditions permit |
| `B2` | CURRENT_STATUS | Current ADC code `uint16`, scan ID low byte, validity flags byte |
| `B3` | BEGIN_CONFIG | Configuration revision `uint32` |
| `B4` | STAGE_KP | Signed 32-bit fixed-point Kp |
| `B5` | STAGE_KI | Signed 32-bit fixed-point Ki |
| `B6` | COMMIT_CONFIG | Configuration revision `uint32` |
| `B7` | CLEAR_FAULTS | Four zero bytes; only eligible while disabled and physically healthy |
| `B8` | PING | Arbitrary four-byte test cookie, echoed in a later reply |
| `B9` | READ_CONFIG | Four zero bytes; requests the active configuration revision |

The `B*` values above are hexadecimal. They are deliberately different from the old `A0/A1` current command family. Reserved payload bits must be zero. All packets require a valid CRC and legal payload before acceptance.

For CURRENT_STATUS, define validity bit 0 as current valid and bit 1 as gap estimate valid; reserve bits 2-7 as zero. Invalid sensing must prevent arming and cause an operating system to stop. These flags report MCU checks, not independent proof that an analog sensor is electrically healthy.

### Units and position PI

For the position payload, a practical encoding is **0.01 mm per unsigned count**: 10.00 mm is 1000 counts and 20.00 mm is 2000 counts. Encoding granularity is not sensor resolution or accuracy. Define the downward surface gap exactly as the proposal does.

The MCU estimates gap and requests gap; it does not calculate a current request. The FPGA converts the gap values into its agreed arithmetic units and computes position error. With downward gap positive and increasing duty producing upward attraction, use:

```text
error_mm = measured_gap_mm - requested_gap_mm
duty = clamp(bias_duty + Kp * error_mm + integral_contribution,
             0, duty_limit)
```

The integral update uses **dt = 0.001 s** at the 1 kHz control rate, with anti-windup. Positive error means the target is too low and should ordinarily request more attraction. Verify that sign with the actual sensor calibration and actuator orientation before powered operation. No Kd or current PI is introduced here.

For transporting gains, signed **Q16.16** is a possible common format: `encoded = round(value * 65536)`. In this guide's millimeter arithmetic, Kp has units duty/mm and Ki has units duty/(mm*s); Ki is a continuous-time gain and does **not** already contain dt. If calculations use meters, divide the numeric gains in duty/m and duty/(m*s) by 1000 before encoding in these millimeter units. Specify wide intermediate arithmetic, rounding, saturation, and accumulator bounds on the FPGA. This wire encoding does not select stable gains.

### Atomic gain updates

Treat gain changes as one transaction spanning multiple SPI frames:

1. BEGIN_CONFIG establishes a new revision and clears the staging-complete mask.
2. STAGE_KP and STAGE_KI write only temporary registers and set their respective mask bits.
3. COMMIT_CONFIG must match the pending revision and requires both staged values to be present and within configured bounds.
4. Apply the pair together at the next 1 kHz control boundary. Until then, the old pair remains active.
5. READ_CONFIG reports the **active** revision. A commit acknowledgment alone means the request was accepted; the active revision confirms application.

Allow only one staging transaction at a time. A new BEGIN replaces an incomplete staging transaction; missing values or a mismatched commit must never mix old and new gains. PING and configuration traffic must not enable the output or refresh the position-command watchdog.

For changes while running, define the integrator policy too. One bumpless-transfer approach adjusts the stored integral contribution to preserve the previous duty under the new Kp, subject to its limits; the new Ki then governs subsequent integration. Validate this behavior rather than assuming atomic register writes alone prevent an output step. While disabled, reset/hold the integrator according to the startup policy.

### CRC

Use **CRC-16/CCITT-FALSE** for commands and replies:

```text
Polynomial:    0x1021
Initial value: 0xFFFF
Reflection:    none
Final XOR:     none
Coverage:      bytes 0-5
Storage:       byte 6 high, byte 7 low
Check vector:  ASCII "123456789" -> 0x29B1
```

The existing [CRC implementation](../firmware/src/protocol.c) is a useful reference. Its old field packing and application semantics must be replaced.

### Replies and acknowledgments

For a normal status reply, use:

| Byte | Proposed status layout |
|---:|---|
| 0 | `0x60` plus bit 0 position-data ready and bit 1 drive enabled; bits 2-3 reserved zero |
| 1 | Sequence number of the last accepted command |
| 2-3 | Active PWM duty in timer ticks |
| 4 | Latched fault bits |
| 5 | Type of the last accepted command, or zero if none |
| 6-7 | CRC |

Proposed fault bits are 0 external interlock, 1 measured overcurrent, 2 stale/missing position command, 3 invalid/stale sensing, and 4 invalid configuration; bits 5-7 are reserved. CRC/frame rejection should increment diagnostic counters without automatically overwriting the last accepted command. Adopt explicit fault-clear conditions on both devices.

For a PING response, use byte 0 = `0x80`, byte 1 = accepted PING sequence, bytes 2-5 = echoed cookie, and bytes 6-7 = CRC. For READ_CONFIG, use byte 0 = `0x70`, byte 1 = accepted READ_CONFIG sequence, bytes 2-5 = active revision, and CRC in bytes 6-7. Return normal status when no special response is pending. The MCU must recognize each response type before interpreting its payload; an echo cookie must never be decoded as PWM duty.

SPI is full duplex: the FPGA cannot acknowledge a complete packet before that packet has arrived. Freeze one coherent reply at CS assertion. After processing a command, make its response available for the **next** transaction. Allow processing time before the next CS assertion: at least 10 us in slow bench tests, with the final scheduled spacing also verified on hardware.

```text
Transaction 1: send PING sequence 1 -> receive initial status
Transaction 2: send PING sequence 2 -> receive cookie/sequence from PING 1
Transaction 3: send PING sequence 3 -> receive cookie/sequence from PING 2
```

Track `(type, sequence)` together because the recommendation uses per-type sequence counters. Reject immediately repeated packets of the same type, and handle the 255-to-0 wrap. A rejected packet leaves the acknowledgment pointing at the last accepted command. Match replies against a small transaction history rather than assuming every received reply acknowledges the packet currently being transmitted.

Use a new position sequence only for a new gap estimate; never relabel an old sample as fresh. The two POSITION types should share one sequence/freshness history so toggling enable cannot make a stale measurement fresh. Apply a separate MCU sensing-age check. A changing sequence number by itself cannot establish ADC health.

## 6. Schedule acquisition and communication

The proposal specifies **5 kHz ADC scans** and **1 kHz gap estimation/FPGA position PI**. These are separate rates. Receiving five SPI frames per millisecond must not cause five PI integration steps per millisecond.

After each 200 us timer event:

```text
Read current: 3-byte ADC transaction
Read Hall A:  3-byte ADC transaction
Read Hall B:  3-byte ADC transaction
Keep the completed scan together with its timestamp/sample ID

Every fifth scan:
    estimate gap using both Hall readings and measured current
    prepare one fresh position packet

Exchange at most one 8-byte FPGA frame in this scan slot
Validate the received CRC, response type, and acknowledgment
```

A useful repeating five-slot assignment is:

| Slot in each millisecond | FPGA transaction after ADC acquisition |
|---:|---|
| 0 | Fresh estimated/requested position packet |
| 1 | Current/status packet |
| 2 | One queued configuration packet, otherwise PING |
| 3 | One queued configuration packet, otherwise PING |
| 4 | One queued configuration packet or active-revision read, otherwise PING |

Gain staging may span milliseconds. It does not need to displace position commands. Prioritize STOP, sensing faults, and position delivery over configuration traffic. For STOP, lower the independent MCU permit immediately and send a disabled position command at the earliest available transaction; do not wait for a browser plot update.

For the initial FPGA implementation, use acceptance of each **fresh POSITION packet as the control-update trigger**. The MCU produces those packets at nominally 1 kHz, so the FPGA executes one PI step per new estimate. Apply any committed gain pair at that same boundary before the step. The FPGA's internal clock runs the arithmetic; unrelated packet types do not trigger it. This avoids requiring two independent board clocks to maintain exactly aligned millisecond ticks. Use nominal dt = 1 ms only after checking actual position-packet intervals, and include estimation, SPI, arithmetic, and PWM-boundary delays in the measured loop latency.

If you instead implement a free-running FPGA 1 kHz tick, define pending-sample handling and clock-drift behavior explicitly; do not silently integrate an old sample again when no new one arrived. Define an appropriate sensing/position deadline policy in addition to the proposal's 50 ms command watchdog. Never let PING/configuration traffic conceal missing position updates.

The CURRENT_STATUS packet in this example is 1 kHz. If protection requires fresher digital current checks, allocate additional non-position slots to it and reduce background traffic. The analog comparator remains independent. Three channels in a scan are sequential readings, not simultaneous measurements; record their timing for field compensation.

### Timing budget

At 1 MHz, the minimum clocking time in a slot containing all three ADC reads and one FPGA frame is:

```text
ADC:    3 channels * 24 clocks = 72 us
FPGA:   8 bytes * 8 clocks    = 64 us
Total wire time              = 136 us
Available scan period        = 200 us
```

The PDF budgets approximately **143 us including its nominal gaps**, leaving **57 us** for other work. The existing driver also inserts ADC setup delays, and real execution adds DMA setup, interrupts, CRC, gap estimation, and chip-select handling. Treat 57 us as a proposal allowance, not a measured margin. Confirm worst-case completion before 200 us, especially on estimation slots and while serving the webpage.

Do not append a second 8-byte FPGA transaction to the same busy scan slot: **72 + 2*64 = 200 us of clocking alone**, before any guards or software. Likewise, simply enlarging the frame changes the budget. The typed-frame schedule is intended to preserve the short frame size.

## 7. Add DMA after the polling link works

The retained driver maps **SPI1 RX to DMA1 channel 2/request 1** and **SPI1 TX to DMA1 channel 3/request 1**. Review the mapping whenever changing peripheral or MCU configuration.

DMA moves bytes between memory and the SPI data register. Software still owns chip selects, transaction ordering, buffer ownership, CRC, acknowledgments, sample freshness, and error recovery.

For each DMA transaction:

1. Confirm the bus is idle and the other slave is deselected.
2. Prepare TX bytes and reserve an RX buffer of the same length.
3. Configure byte-sized memory/peripheral transfers and the correct transfer count: 3 for an ADC read, 8 for an FPGA frame.
4. Assert the selected CS and meet its setup guard.
5. Arm receive DMA before starting transmit DMA/clocks.
6. On completion, check DMA/SPI error flags, receive completion, and the final SPI busy state.
7. Meet the hold guard, raise CS, and only then reuse the completed buffers or advance the state machine.

TX DMA completion alone does not prove the last bit has left the SPI peripheral. Releasing CS prematurely loses the end of the frame. Buffers must remain alive and unchanged until completion; use static/double-buffered storage rather than a temporary stack buffer that expires while DMA is running.

During acquisition, do not let a foreground web handler start another SPI transfer on the same peripheral. Queue web requests for the scheduled communication path. A DMA error, SPI stall, invalid sensing, or scan overrun should remove permit and leave the system stopped until deliberately recovered.

## 8. Bring-up procedure

Keep electromagnet power disconnected through the digital-link and sensing checks. Use the project's disabled/default output gate until the physical driver and interlocks have been checked.

### Step 1: establish MCU loopback

Disconnect the FPGA and ADC MISO outputs. Temporarily connect **MCU MOSI to MCU MISO**. Using polling at approximately **125 kHz**, transmit:

```text
00 FF AA 55 81 7E
```

The received bytes should match exactly. This checks the MCU SPI setup and data path, not the FPGA or its CS handling. Remove the loopback jumper afterward.

### Step 2: establish the FPGA packet link

Connect only the FPGA SPI link, keep ADC_CS high, and hold permit low. Implement the proposed PING parser/reply path first, without enabling position control. After FPGA startup, exchange PING packets at approximately 10 transactions/s using different cookies and sequence values. Verify the CRC and the delayed echo of the previous cookie/sequence.

The proposed golden frames are listed in section 9. They intentionally differ from the old `A0` current-controller examples. The new PING will be rejected by the unchanged old decoder; that is expected until the replacement parser is programmed.

Require repeatable echoes and no unexplained errors over at least 1000 slow transactions. The first reply can be startup status; it is not expected to echo a command the FPGA has not received yet. An external-interlock fault can coexist with a valid packet link if the interlock is not assembled.

### Step 3: connect the ADC

Confirm both devices release MISO when unselected. Apply known safe voltages to each ADC channel: ground, approximately half reference, and another voltage measured with a meter. Check channel order, command bytes, and result extraction. A plausible constant ADC code is insufficient proof of correct acquisition.

Connect and inspect Hall/current outputs only after known-voltage tests pass. Move a magnet by hand with drive off and verify the Hall responses, sensing direction, and absence of clipping.

### Step 4: validate application messages with output inhibited

Send disabled position packets with known gap/target values. Inspect the FPGA's decoded values, sequence, and pending registers. Check that a current packet cannot be mistaken for position and that changing a gain stage does not immediately change the active gain.

Test the position PI arithmetic in simulation using synthetic gap values. Verify that it integrates only at 1 kHz, handles the configured error sign, saturates correctly, and unwinds correctly. The inhibited hardware output may remain at zero even when communication is working; inspect decoded/pending values rather than treating zero PWM as a failed link.

### Step 5: increase to 1 MHz, then enable DMA and the timer schedule

Repeat the same checks at 1 MHz using polling first, then DMA, then timer-driven scans. Do not combine all three changes into the first test. The 125 kHz setting is only for isolated bring-up and cannot meet the final 5 kHz scan schedule.

Capture the maximum complete scan duration. Exercise the every-fifth-scan gap calculation, configuration commits, webpage requests, and graph traffic during the timing test.

### Step 6: exercise failures before powered levitation

- Corrupt a CRC; verify no command/gain update occurs.
- Send 63 or 65 clocks instead of 64; verify rejection.
- Repeat a position sequence; verify it does not refresh position freshness.
- Stop position traffic while continuing PING/configuration; verify the position timeout still acts.
- Interrupt a gain transfer; verify the active pair stays unchanged.
- Commit the wrong revision or an incomplete pair; verify rejection.
- Lower permit or trigger the physical interlock; verify the actual gate-drive path is inhibited independently of SPI.
- Reset/program either board; verify there is no unintended gate pulse.

Once the powered position loop is running, pausing the MCU debugger should cause stale-data handling and, at the latest, the FPGA's 50 ms command watchdog to act. Use recorded traces and buffered logs for that stage. Gate-off delay and coil-current decay are different measurements because current continues through the flyback path.

## 9. Concrete protocol test vectors

These vectors apply **only to the proposed replacement protocol in section 5**, not the old current-controller implementation.

| Frame | Complete bytes, including CRC |
|---|---|
| PING sequence 1, cookie `12345678` | `B8 01 12 34 56 78 E6 83` |
| PING sequence 2, cookie `A5A55A5A` | `B8 02 A5 A5 5A 5A A6 E9` |
| Echo of PING 1 | `80 01 12 34 56 78 C4 4D` |
| Echo of PING 2 | `80 02 A5 A5 5A 5A 84 27` |
| Disabled position sequence 1, estimated = requested = 15.00 mm | `B0 01 05 DC 05 DC 06 59` |

Recalculate and compare these in both C and HDL tests. An intentionally corrupted version must fail. The disabled-position vector is a communication test value, not a control-tuning instruction.

## 10. Instruments and debug information

Connect a logic analyzer to:

| Analyzer signal | Connection |
|---|---|
| SCK | PA5 |
| MOSI | PA7 |
| MISO | PA6 |
| FPGA_CS | PA4 |
| ADC_CS | PA1 |
| FPGA accepted-frame debug | GPIO_38, after defining its meaning in the revised RTL |
| Optional permit | PA0 |
| Ground | Logic ground |

Decode mode 0, MSB first, eight-bit words, using a separate CS-aware decoder for each slave if available. At 1 MHz SCK, use at least **10 MS/s**, preferably higher. Trigger on FPGA_CS falling to inspect packets, or on a debug/fault transition to capture failures.

The current GPIO_38 pulse means acceptance of an old current packet. In revised RTL, explicitly choose whether it means **any accepted frame** or **a position PI update**. Those events have different rates. For the most useful timing check, expose the PI update at 1 kHz and use another temporary debug signal or HDL counters for accepted frames. Do not interpret a 5 kHz accepted-frame pulse as proof that the PI update rate is correct.

Useful MCU watch variables and buffered counters are:

- Last TX/RX frames, response type, expected acknowledgment type/sequence, and last valid reply time.
- Raw CH0/CH1/CH2 values, scan ID, scan timestamp, gap estimate, and sensing-validity state.
- CRC failures, invalid response types, acknowledgment failures, DMA/SPI errors, and scan overruns.
- Maximum scan duration and maximum age of the position estimate at transmission.
- Pending and active configuration revisions; requested and acknowledged Kp/Ki values.
- Requested gap, returned duty, fault bits, and permit state.

Useful FPGA simulation/debug values are accepted/rejected frame counts, last position sequence, position age/watchdog, pending and active gains, active configuration revision, PI tick count, error, integral contribution, requested/active duty, and latched faults.

Log summaries at a modest rate, such as 10-20 Hz. Do not print formatted logs from each 5 kHz interrupt. Decimate graph telemetry separately from control, and preserve sample timestamps so graph timing does not imply simultaneous ADC readings or zero transport delay.

| Symptom | First checks |
|---|---|
| No clock | SPI enable, peripheral clock, AF5 mapping, code reached transfer |
| Always `FF` | Floating MISO, wrong CS, unconfigured FPGA, missing ground |
| Always `00` | MISO held low, reset, wrong endpoint, missing FPGA clock |
| Shifted bytes | CPHA/CPOL, first-bit setup, bit count, CS timing |
| Works with FPGA alone but fails with ADC | Both CS low, wrong CS, unselected slave driving MISO |
| Good CRC but no acknowledgment advance | Old decoder, wrong type, duplicate sequence, invalid bounds/configuration |
| Echo is correct but PWM stays zero | Expected while disabled; check permit, interlock, commissioned gate, valid position/configuration |
| Failures begin with DMA | Request/channel mapping, byte widths/counts, buffer lifetime, premature CS release |
| Failures recur every fifth scan | Gap-estimation work or scheduling exceeds available time |
| Failures start during webpage/graph requests | Blocking work, excessive interrupt masking, shared buffer/bus ownership |
| Failures start with electromagnet switching | Ground return, supply disturbance, wire routing, ringing; inspect with a scope |
| PING works but gains do not change | Staging completeness, matching revision, commit boundary, active-revision readback |

## 11. What must change in the existing implementation

The retained pin map and byte-transport code are starting points. The updated proposal requires application changes on both devices:

| Existing area | Required change |
|---|---|
| [protocol.c / protocol.h](../firmware/src/protocol.c) | Define typed position/current/configuration packets and response parsing; remove requested-current fields |
| [runtime.c](../firmware/src/runtime.c) and MCU control path | Keep ADC acquisition and gap estimation; stop running the position controller on the MCU; transmit gap/target and queued configuration |
| [lev_core.sv](../fpga/rtl/lev_core.sv) | Replace current PI application behavior with 1 kHz position PI and direct duty output; implement typed parsing, sample freshness, and atomic gain application |
| [spi_frame.sv](../fpga/rtl/spi_frame.sv) | Retain/revalidate 64-bit framing, mode-0 timing, MISO release, and coherent reply snapshots |
| MCU/FPGA tests | Replace old current-request assertions; verify new packet types, gain transactions, rate separation, faults, and watchdog semantics |
| Web interface | Queue target/gain commands; show the acknowledged active configuration and current faults; keep stop independent of graph refresh |

Host simulation and successful compilation do not establish physical wiring, SPI timing, ADC accuracy, or a working feedback loop. The prior software verification record applies to its older architecture, not automatically to this replacement.

## 12. Proposal inconsistencies to keep separate from implementation

- The updated PDF's text and Figure 1 caption specify **FPGA position PI**, but the image still labels the FPGA **Current PI control**, labels the MCU **Height control**, and describes requested-current traffic. It also routes ADC SPI toward the FPGA. Follow the updated section 2 text: the MCU owns ADC acquisition and estimates gap; the FPGA owns position PI.
- The PDF BOM still says **DRV5055**. The user's selected purchase is **DRV5056 A3/A4 through-hole**; use its actual pinout, unipolar response, offset, and supply-specific sensitivity.
- The selected actuator is the **Heyiarbeit JF-XP2520-12V electromagnet**, not the example air-core coil in the sizing calculations. Its current limit and field compensation must use actual characterization. This does not change the SPI electrical interface.
- The PDF's position-resolution example uses a 5 V ADC span and preliminary sensitivities. This guide's proposed bus/sensor circuit uses **3.3 V**; keep those assumptions separate when interpreting ADC codes.

## References

1. [Updated project proposal](<C:/Users/steph/Downloads/MicroPEs_Proposal.pdf>), sections 1-2, 5, and 8: architecture, rates, telemetry, and gain updates.
2. [HMC E155 development-board schematic](https://hmc-e155.github.io/assets/doc/E155%20Development%20Board%20Schematic.pdf): carrier routing, MCU/UPduino labels, and bridge connections.
3. [ST UM1956, Nucleo-32 user manual](https://www.st.com/resource/en/user_manual/um1956-stm32-nucleo32-boards-mb1180-stmicroelectronics.pdf), section 7.10 and Table 16: solder bridges and NUCLEO-L432KC connector mapping.
4. [STM32L432KB/KC datasheet](https://www.st.com/resource/en/datasheet/stm32l432kc.pdf), Table 15: SPI1 alternate functions.
5. [Microchip MCP3204/3208 datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/21298e.pdf), pinout and section 6.1: ADC electrical interface, mode-0 transactions, and data alignment.
6. [TI DRV5056 datasheet](https://www.ti.com/lit/ds/symlink/drv5056.pdf), pin functions and electrical/magnetic characteristics: TO-92 wiring, decoupling, offset, polarity, and sensitivity at 3.3 V/5 V.
7. Local [FPGA constraints](../fpga/constraints/upduino.pcf), [STM32 driver](../firmware/src/board_stm32l432.c), and [SPI framing module](../fpga/rtl/spi_frame.sv): retained implementation references, with the architecture limitations identified above.
