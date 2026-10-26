# Communication contract v2

## Shared MCU SPI bus

The STM32 owns SPI1 at 1 MHz, mode 0, MSB first. PA1 selects the MCP3204; PA4 selects the FPGA. PA5/PA7/PA6 are shared SCK/MOSI/MISO. Only one chip select may be low. The FPGA releases MISO when PA4 is high, including during ADC transactions.

TIM6 releases one scan every 200 us (5 kHz). DMA1 channel 2/request 1 receives SPI1 data and channel 3/request 1 transmits it. Each ADC channel gets a separate 24-clock transaction: CH0 current, CH1 primary Hall, and optionally CH2 reference Hall. ADC CS is high for at least 1 us between conversions. These sequential readings belong to the same scan; they are not simultaneous. Then the MCU exchanges one 8-byte FPGA packet, with at least 2 us CS lead/trail guards. DMA completion interrupts advance the transactions. A DMA error, stalled SPI, or scan overrun removes permit and halts acquisition until reset.

The FPGA consumes one new measured/requested-current pair per valid packet, nominally 5 kHz. The MCU estimates height and runs its position/motion controller every fifth completed ADC scan (1 kHz). The requested current computed on that scan is sent in the following FPGA transaction. HTML generation and UART traffic run in the foreground while acquisition/control runs in interrupts.

## Eight-byte frames

Fields are explicitly packed big-endian. CRC-16/CCITT-FALSE uses polynomial `0x1021`, initial `0xffff`, no reflection/final XOR, over bytes 0-5, stored high byte first in bytes 6-7. Check vector: `123456789 -> 0x29b1`. This wire format is incompatible with the old 16-byte design; rebuild both devices.

| Byte | MCU MOSI | FPGA MISO |
|---:|---|---|
| 0 | `0xa0` plus bit 0 enable, bit 1 clear | `0x50` plus bit 0 measurement ready, bit 1 enabled |
| 1 | 8-bit command sequence, increments every scan, wraps at 256 | last accepted command sequence |
| 2-3 | measured current ADC code, 0-4095 | active PWM duty, 0-1080 ticks |
| 4 | requested current code high byte | latched faults |
| 5 | requested current code low byte | reserved, zero |
| 6-7 | CRC | CRC |

Measurement and target are absolute ADC codes, including current zero offset. The compiled FPGA ceiling is in `project_config.svh`; the firmware's `hard_limit_counts` must agree. Current PI gains also live in that FPGA configuration, with Kp Q8.8 in 0-4096 and Ki Q8.8 in 0-1024; Ki includes the 200 us sample period. They no longer occupy packet fields. Example gains remain zero until measured and tuned.

The reply is a coherent snapshot frozen at CS assertion, acknowledging the previous transaction. MCU feedback verifies that previous sequence after the first exchange; it does not interpret the reply as acknowledgment of the packet still on the wire. Local ADC data is retained separately and never overwritten by FPGA telemetry. A missing acknowledgment, CRC/bounds failure, or missed 200 us acquisition deadline trips MCU control.

The FPGA rejects short/overlong packets, reserved flags, bad CRCs, out-of-range values, and immediately repeated sequence numbers. Rejected packets cannot update PI or refresh the watchdog. Every accepted packet updates the current PI once. Fifty milliseconds without a fresh command while enabled latches a timeout fault. This is an MCU-command watchdog, not independent proof of ADC electrical health. Frozen but plausible analog readings need physical diagnosis and the independent comparator/interlock.

Fault bits: 0 external interlock, 1 measured overcurrent, 2 command timeout; bits 3-7 reserved. Clearing requires a fresh disabled packet, healthy external interlock, and measured current below the compiled limit. Clear and arm are separate actions. Permit and external fault directly remove gate permission without waiting for another serial packet.

## ESP8266 to MCU

The unchanged course bridge uses USART1, 125000 baud, 8N1, and `/REQ:<route>\n` (CRLF also accepted). Exact routes are empty/root, `arm`, `stop`, `clear`, `modegap`, `modeamp`, `up`, and `down`. The response is one complete HTML document. Refresh points at root once per second so commands are not repeated by refresh. A recognized request renews a 5-second browser lease; expiry is checked in the interrupt control path. Web STOP removes MCU permit immediately after parsing. Physical E-stop remains independent of communications.
