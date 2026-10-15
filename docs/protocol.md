# Communication contract v1

## MCU ↔ FPGA SPI

Separate bus from the ADC. Mode 0 (CPOL=0, CPHA=0), MSB first, 1 MHz maximum. CS leads the first rising SCK and follows the last falling SCK by at least 2 us. Clock exactly 128 bits under one CS. No bytes are read from MCU struct memory directly: the C codec packs explicit big-endian fields.

CRC is CRC-16/CCITT-FALSE: polynomial `0x1021`, initial `0xffff`, no reflection, no final XOR, over bytes 0–13; stored high byte first at 14–15. Check vector `123456789 → 0x29b1`.

| Byte | MCU MOSI | FPGA MISO |
|---:|---|---|
| 0 | `0xa5` | `0x5a` |
| 1 | protocol `1` | protocol `1` |
| 2–3 | monotonically incrementing 16-bit command ID | completed-scan sample ID, wraps at 65536 |
| 4 | enable: 0 or 1 | Hall1 high byte |
| 5 | clear fault: 0 or 1 | Hall1 low byte |
| 6–7 | current target ADC counts, 0…hard limit | Hall2 counts |
| 8–9 | current Kp Q8.8, 0…4096 | current counts |
| 10–11 | current Ki Q8.8 per update, 0…1024 | active duty ticks, 0…1080 |
| 12 | current hard limit high byte | latched fault bits |
| 13 | current hard limit low byte | flags: bit 0 scan ready; bit 1 enabled |
| 14–15 | CRC | CRC |

Telemetry is the most recently prepared coherent scan/status snapshot, frozen at CS assertion; it is not the response to the command currently being transmitted. Status is rebuilt every 100 us. The command is accepted about 5 us after CS rises once its frame/CRC/bounds are valid. There is no command ACK field; confirm actual enable/fault state in subsequent telemetry. A rejected command cannot keep the output enabled indefinitely: the 20 ms watchdog still runs. MCU command IDs change every tick, including disabled packets; the FPGA rejects the immediately repeated ID. This detects frozen retransmission, not arbitrary network replay/security attacks.

The accepted hard limit must be positive and no greater than the compiled FPGA ceiling. Targets use the ADC's absolute code, including measured current zero offset. The hard limit also uses absolute counts; update both firmware and FPGA configuration together. Gain formats and fault bits are defined in docs/design.md. The MCU faults on invalid telemetry or on a sample ID unchanged for 3 ms. Flags indicate a completed scan, not electrical proof that an ADC is connected: a stuck but plausible MISO level cannot be fully diagnosed digitally.

## ESP8266 ↔ MCU

Use the [course IoT server](https://hmc-e155.github.io/lab/lab6/) at 125000 baud, 8 data bits, no parity, one stop bit. Its line format is `/REQ:<route>\n`. This implementation accepts CRLF too. Routes are short, exact strings: empty route reads the page; `arm`, `stop`, `clear`, `modegap`, `modeamp`, `up`, and `down` perform controls. Query parameters are unnecessary. Connect to the board's existing SSID, then open `http://192.168.4.1/`.

Each response is one HTML document from `<!DOCTYPE html>` through `</html>`. The course bridge forwards HTML rather than a general JSON API. The page refreshes the **root** once per second so a refresh does not repeat an arm or increment command. Every recognized request renews the 5-second browser lease. A backgrounded browser or lost Wi-Fi therefore stops the system. The UART page path never blocks while waiting for bytes. Web STOP depends on communications and is distinct from the physical interlock.
