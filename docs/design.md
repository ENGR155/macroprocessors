# Implementation and control design

## System boundary

One coil controls vertical motion. The initial object should contain a permanent magnet with a repeatable orientation, so its field can be distinguished from the coil field. A plain steel sphere is not a drop-in equivalent: its induced field varies with current and gap. Do not assume the supplied affine estimator can sense it. Validate the actual object and geometry before committing the proposal.

```{mermaid}
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf0e8","primaryTextColor":"#202824","primaryBorderColor":"#95a08d","lineColor":"#77846f","fontFamily":"Segoe UI","fontSize":"16px"}}}%%
flowchart TB
    B[Browser: gap/current target] <-->|HTTP over local Wi-Fi| E[Course ESP8266 server]
    E <-->|UART: 125000 baud, 8N1| M[STM32L432KC: 1 kHz position loop]
    M <-->|SPI mode 0: 1 MHz, 16 bytes full duplex| F[UP5K: acquisition, current PI, PWM, faults]
    H1[Primary linear Hall] -->|0–3.3 V CH1| A[MCP3204: 12 bits]
    H2[Reference linear Hall] -->|0–3.3 V CH2| A
    S[Inline shunt + amplifier] -->|0–3.3 V CH0| A
    A <-->|SPI mode 0: 0.857 MHz| F
    M -->|PA0 permit| G[Hardware output interlock]
    F -->|PWM + enable| G
    X[Current comparator + E-stop] -->|fault_n| G
    X -->|fault_n| F
    G --> D[Gate driver + MOSFET + flyback path]
    D --> C[Electromagnet and suspended object]
    C -. magnetic field .-> H1
    C -. magnetic field .-> H2
    C --> S
```

This is a useful hardware/software partition, not a claim that an STM32 cannot generate 20 kHz PWM. The FPGA's substantial work is autonomous ADC sequencing, fixed-point feedback, packet validation, independent watchdogs, and output gating. The MCU contributes sensor compensation, filtered velocity estimation, floating-point position control, trajectories, and communication.

## Coordinates and model

Let `x` be the gap in mm measured **downward** from the coil reference plane. Increasing the web target lowers the object. Locally,

`m*x_ddot = m*g - F(i,x)`, with a rough magnetic model `F ≈ k*i²/x²`.

The force law is an identification aid, not a validated model of a stock electromagnet. Equilibrium requires measured force at the actual air gap, not a zero-gap holding-force rating. Record mass, lift versus current/gap, resistance, inductance, and steady temperature. Current dynamics approximately satisfy `L*di/dt = Vdrive - R*i`; off-time decay depends on the clamp.

Hall outputs contain the object field, the coil field, offsets, and noise. The supplied local estimator is

`gap_mm = c0 + c1*H1_counts + c2*H2_counts + c3*measured_current_A`.

Coefficients come from a mechanically fixed object swept through known gaps and currents. Two Hall sensors do not automatically cancel the coil. The ADC is multiplexed, so changing current during the scan can also corrupt this compensation. Validate transient errors; narrow the operating range or change sensing/model if necessary.

The MCU uses `e = measured_gap - ramped_target` and

`Irequest = clamp(Ihover + Kp*e + Kd*filtered_velocity + integral, 0, Imax)`.

Positive error and positive downward velocity request more lift. Derivative acts on measurement to avoid setpoint kick. Target gap moves at a bounded rate. Integral updates only when the output is unsaturated or the error drives it out of saturation. Default gains and bias are zero; tune PD first. Height-mode arming initializes the ramp at the requested gap, so initially hold the object close to that target. Current-test mode ramps current separately and requires a supported object.

## FPGA pipeline

```{mermaid}
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#edf0e8","primaryTextColor":"#202824","primaryBorderColor":"#95a08d","lineColor":"#77846f","fontFamily":"Segoe UI","fontSize":"16px"}}}%%
flowchart TB
    T[24 MHz timebase] --> P[1200-cycle PWM phase]
    T --> Q[2400-cycle ADC frame]
    Q --> A[CH0 current → CH1 Hall → CH2 Hall]
    A --> R[Coherent scan snapshot + sample ID]
    A --> I[Signed Q8.8 current PI]
    I --> L[Clamp 0…1080 ticks]
    L --> P
    S[SPI frame + CRC + sequence check] --> I
    S --> W[20 ms command watchdog]
    A --> V[250 us scan watchdog + current limit]
    W --> G[Latched fault/output gate]
    V --> G
    P --> G
```

Current PI takes error in raw ADC counts. `kp_q8/256` is duty ticks per count. `ki_q8/256` is duty ticks per count **per 100 us update**, already including the sample interval. Signed intermediate widths are bounded explicitly (13-bit error, 27-bit proportional product, 24-bit integral increment, 28-bit sums, and 21-bit integrator); accepted gain bounds are 4096 and 1024, and the integrator is bounded to ±1080×256. PWM duty changes only at a period boundary. A fault or loss of permit can truncate a pulse immediately. Zero enable clears PI history. Seven registered arithmetic stages finish in less than 0.3 us. CRC engines process one payload bit per clock; command validation completes about 5 us after CS rises. Status is assembled once per 100 us frame and its checksum is completed before the next scan. Fault decisions have a few system clocks of register latency beyond the nominal intervals; physical output gating is independent of telemetry refresh.

Fault bits are 0 external interlock, 1 sampled overcurrent, 2 command timeout, and 3 ADC scan timeout. Faults latch. Clearing requires a disabled valid command, recent completed scan, healthy external input, and current below the requested hard limit. Clear and arm are separate actions. A bad checksum, malformed frame, or repeated sequence cannot refresh the command watchdog.

## Nominal timing and performance calculations

| Item | Calculation | Design result |
|---|---|---|
| PWM | 24 MHz / 1200 | 20 kHz, 50 us; 0.0833% duty step |
| Maximum duty | 1080 / 1200 | 90%; deliberate off-time |
| ADC SPI | 24 MHz / (2×14) | 0.857 MHz, with margin below 1 MHz |
| Scan occupancy | 3×(28 us conversion + 1 us CS high) | approximately 87 us / 100 us frame |
| Acquisition trigger | 60 cycles / 24 MHz | 2.5 us after every other PWM start |
| ADC reference | 3.3 V / 4096 | 0.806 mV/count, ideal |
| Example current scale | 0.1 ohm × gain 20 | 2 V/A; 0.403 mA/count, ideal |
| Example 0.5 A shunt loss | I²R | 25 mW; use a rated part with margin |
| MCU exchange | 128 clocks / 1 MHz + CS guards | at least 132 us, plus software gaps |
| MCU link utilization | one exchange per 1 ms | at least 13.2% |
| UART payload | 125000/10 | 12500 bytes/s; a 2 KiB page takes about 164 ms |

24 MHz is the nominal internal oscillator frequency; measure it. ADC aperture times differ between channels. Sampling begins at a fixed PWM phase but the variable falling edge can move across the acquisition window. No claim of universally quiet sampling is made. Use suitable analog filtering and verify captures while sweeping duty. MCP3204 analog source impedance must meet its acquisition requirements.

Telemetry is frozen at CS assertion and may be almost 1 ms old when fetched; the MCU sends the previous tick's current request and calculates the next after receiving. Budget roughly 2–3 ms worst-case outer measurement-to-actuation delay including scan, scheduling, packet, and PWM boundary effects, then measure it. Do not infer stability from sample rates alone. Tune the current loop to be several times faster than the position loop, and measure frequency/step response rather than assuming a 10:1 bandwidth ratio from the update rates.

## MCU routine responsibilities

`board_init` establishes a 16 MHz HSI clock, 1 MHz SPI1, 125000-baud USART1, 1 MHz TIM2 timestamp, and 1 ms SysTick. Main checks elapsed ticks, exchanges one packet, detects stalled sample IDs, estimates gap/current, and computes the next output. Missing a tick or seeing invalid/stale telemetry stops the coil. UART RX/TX are polled without waiting for characters; page transmission continues across control updates. Requests are bounded and matched exactly. A 5-second browser lease stops an abandoned session. Measure worst-case execution time including page formatting; an overrun is a fault, not skipped control work.
