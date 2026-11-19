# MicroPEs live position and PID monitor

The ESP8266 runs custom MicroPEs firmware and hosts the dashboard on its own Wi-Fi network. The STM32 reads the FPGA over SPI and answers UART requests for position and PID data. The browser plots 60 seconds of position history, shows the raw FPGA word and sample age, and can export the plotted points as CSV. The page loads from ESP flash even if the STM32 is disconnected.

## Flash the ESP8266

1. In Arduino IDE, add `https://arduino.esp8266.com/stable/package_esp8266com_index.json` under **Preferences → Additional Boards Manager URLs**. Install **esp8266 by ESP8266 Community**, version **3.1.2**, in Boards Manager.
2. Open [`MaglevWeb.ino`](esp8266/MaglevWeb/MaglevWeb.ino). For a MikroE WiFi ESP Click marked ESP-WROOM-02, select **Generic ESP8266 Module**, **2 MB flash**, **DIO** flash mode, and **115200** upload speed. For another ESP8266 dev board, select its matching board profile and follow its upload procedure. Use the serial port for the ESP or its adapter. Upload speed is separate from the runtime UART rate.
3. For the MikroE WiFi ESP Click, remove it from the carrier while programming so the STM32 and programmer do not drive the same input. Power it at 3.3 V and connect a **3.3 V USB-to-UART adapter** with adapter TX to ESP RX, adapter RX to ESP TX, and grounds joined. Short **HD1 pins 5 and 6** (GPIO0 and GND) and reset or power-cycle the ESP to enter download mode. Upload the sketch, remove the short, then reset or power-cycle again to run the sketch. Disconnect the adapter before reconnecting the Click to the STM32.

The dashboard header is included with the sketch. After editing `web_monitor/dashboard.html`, run `node web_monitor/build_dashboard.mjs` from the repository root to regenerate it.

## Wire the boards

Power down before moving wires. Use **125000 baud, 8 data bits, no parity, 1 stop bit**. Keep serial debug output off the ESP UART.

| STM32 / supply | ESP8266 endpoint | Purpose |
|---|---|---|
| **PA9 / D1, USART1 TX** | **RX / RXD / GPIO3** | Measurements and PID replies |
| **PA10 / D0, USART1 RX** | **TX / TXD / GPIO1** | Telemetry queries and PID commands |
| Regulated **3.3 V** | **3V3 / VCC** | Power |
| **GND** | **GND** | Common logic reference |

For the MikroE Click, plug it into the carrier's mikroBUS socket if the carrier provides the power and UART connections. With power off, check continuity from PA9 to ESP RX and from ESP TX to PA10. The table uses the UART signal directions of the ESP module itself. For a separate module supply, use a regulated 3.3 V supply rated for at least 500 mA and join the grounds. Keep 5 V and the 12 V coil rail away from ESP power and UART pins.

Keep the existing ADC and PWM wiring and the three SPI connections below. Leave unused MCU–FPGA bridges open, particularly bridges involving PA9 or PA10.

| SPI signal | STM32 | FPGA silicon pad |
|---|---|---|
| Clock | PB3 | P21 |
| Chip select | PA11 | P20 |
| FPGA data to MCU | PB4 | P12 |

## Run it

1. Start with coil power disconnected and the working FPGA sensing bitstream loaded. Build and download [`mcu/finalprojectsp.emProject`](../mcu/finalprojectsp.emProject) in SEGGER. The [`maglev_web.emProject`](../mcu/maglev_web.emProject) project also builds the same [`main.c`](../mcu/src/main.c).
2. Join **`MicroPEs-Maglev`** using **`MicroPEs155`**. The network name and password are in `esp8266/MaglevWeb/web_server.cpp`.
3. Open **http://192.168.4.1/**. Move the sensed magnet and compare the raw word on the page with `fpga_word` in the debugger. If the dashboard loads and reports a UART timeout, check that the updated STM32 application is running and verify TX, RX, and ground.

Opening **http://192.168.4.1/api/status** directly requests a fresh telemetry snapshot as JSON. For an offline preview, open the local `dashboard.html` with `?demo=1` appended to its URL. The page labels demo data as simulated.

## Position and PID

The STM32 reads the FPGA every **25 ms** and services UART between reads. Both are in `mcu/src/main.c`. The FPGA sets its own ADC timing. The browser polls 100 ms after each response and plots new sequence numbers. CSV includes the displayed history.

The default position conversion is **40 µm per FPGA word**, matching the bench calculation. The dashboard labels it as provisional. Compare readings against known gaps, then set the scale and offset in `main.c` and set `MAGLEV_POSITION_CALIBRATED` to 1 after validating the result. Watch `fpga_word`, `fpga_average`, `read_count`, and `rejected_count` in SEGGER or JS Scope. The dashboard uses the latest SPI reading. The 10-reading debugger average still uses 10 µm units. Set `PRINT_TO_SEGGER` to 1 in `main.c` for optional RTT output.

The current bench FPGA sweeps PWM and the STM32 has no active PID loop. The dashboard shows **PID not connected** until a controller publishes its actual gains. In the foreground, copy a coherent snapshot of those gains into the monitor:

```c
maglev_gains_t live = { kp_milli, ki_milli, kd_milli };
maglev_monitor_pid(&monitor, &live, apply_actual_pid, controller_context);
```

Gains are in thousandths of the actual controller units (1234 means 1.234). Pass a null callback for readback only. The callback has signature `bool apply_actual_pid(void *context, const maglev_gains_t *requested)`. Apply the entire tuple at a control update boundary and return true only upon commitment. Enforce the controller's measured limits before applying changes. An FPGA PID needs a gain-write command and acknowledgement over its own control link. The current SPI sender provides position readout. Change the ESP Wi-Fi password before enabling gain writes on an active controller.

## HTTP and UART

| Browser request | Example UART message | Response |
|---|---|---|
| `GET /` | — | Dashboard HTML from ESP flash |
| `GET /api/status` | `@M1 42 GET\n` | Latest telemetry and PID state as JSON |
| `POST /api/pid` | `@M1 43 PID 0.500 0.125 0.010 7\n` | Controller result and current values as JSON |

The PID POST carries form fields `kp`, `ki`, `kd`, and `revision` plus the `X-Maglev-Command: 1` header. The last UART field is the gain revision. The MCU replies with the same request ID followed by one JSON line, for example `@M1 42 {"result":"ok",…}\n`. The ESP waits up to 180 ms and ignores responses with a different ID. A stale gain revision returns a conflict. After a timeout on a gain write, check the live values before retrying.

## Verification

STM32 Debug and Release builds passed in SEGGER Embedded Studio 8.30a. The C protocol tests passed in the ARM simulator and the JavaScript dashboard tests passed under Node. A simulator check also connected the ESP request handlers to the STM32 protocol using simulated Arduino I/O. The ESP8266 board package could not be downloaded here. The Arduino target build and physical UART/Wi-Fi exchange still need verification.

```powershell
node web_monitor/build_dashboard.mjs --check
node web_monitor/test_dashboard.mjs
$ses = 'C:/Program Files/SEGGER/SEGGER Embedded Studio 8.30a/bin'
& "$ses/emBuild.exe" -config Debug mcu/finalprojectsp.emProject
& "$ses/emBuild.exe" -config Release mcu/finalprojectsp.emProject
& "$ses/emBuild.exe" -config Debug mcu/maglev_web_tests.emProject
& "$ses/emSim.exe" mcu/Output/Debug/Exe/maglev_web_tests.elf -end maglev_tests_pass -max 20000000
```

Hardware references include the [E155 Lab 6 board information](https://hmc-e155.github.io/lab/lab6/), [E155 v4 carrier schematic](https://hmc-e155.github.io/assets/doc/E155%20Development%20Board%20Schematic.pdf), [MikroE WiFi ESP Click schematic](https://download.mikroe.com/documents/add-on-boards/click/wifi-esp/wifi-esp-click-schematic-v100.pdf), and [ESP8266 Arduino board guide](https://arduino-esp8266.readthedocs.io/en/3.1.2/boards.html).
