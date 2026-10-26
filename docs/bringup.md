# Staged bring-up and acceptance gates

Record hardware revision, configuration commit/hash, supply limit, instruments, and plots for each gate. A completed software test is not evidence of lift, stability, temperature, or real shutdown timing.

## 1. Establish sensing feasibility before a parts commitment

Mount the candidate coil and actual object at known gaps using nonmagnetic spacers. Measure both Hall voltages with no object, with the object, and at multiple coil currents. Choose sensor orientation/sensitivity so signals remain in their linear range and neither clips. Measure whether object position remains distinguishable after coil-current effects and noise are included. Sweep the gap in both directions to expose hysteresis, rotation, and ambiguous responses. For a plain steel sphere, explicitly check the current-dependent magnetization model rather than adopting the permanent-magnet assumptions.

Acceptance: at least one contiguous operating interval has repeatable position estimates with independent holdout RMSE ≤0.25 mm and worst error ≤0.5 mm. These are proposed design thresholds; revise the committed specification with the team/instructor before proposal submission if feasibility measurements require it. Stop expanding the system if observability fails; change geometry/sensor arrangement/object first.

## 2. Characterize coil and driver

Measure coil DC resistance cold and hot, inductance or current step response, lift force versus current and gap, current needed to support the measured object mass, and temperature rise. Select supply, switch, clamp, wiring, fuse, current cap, and mechanical clearance from those measurements. Establish a continuous-duty current rating or add a thermal cutoff in the physical interlock. The supplied code does not measure coil temperature.

Acceptance: lift exceeds weight with operating margin throughout the chosen interval; thermal and electrical ratings support the intended demo duration. Document `tau=L/R`, maximum current rise/decay rates, `Pcoil=I²R`, switch/shunt dissipation, and clamp voltage. Do not power the coil through the development board or a solderless breadboard power rail.

## 3. Verify digital paths with coil power disconnected

Check bridge switches open and every jumper by continuity. Program default-disabled devices. Confirm the UART baud and complete HTML. Capture the shared MCU SPI bus and both chip selects: mode 0, clock rates, CS guards, 64-bit host frames, CRC byte ordering, 24 ADC clocks, channel order, and CS high interval. Apply known analog voltages to the ADC channels. Compare raw telemetry against a meter. A plausible constant ADC code is not sufficient proof that an ADC is connected.

Acceptance: decoded measurements match applied voltages and the C/SV packet tests. Scope MCU ADC CS, `sample_debug`, and PWM to verify 5 kHz scans/accepted packets, 20 kHz PWM, and interchannel timing; output remains low during reset, programming, power loss, and disconnected permit/interlock.

## 4. Calibrate and prove the physical cutoff

Support the object; initially replace the coil with a resistive load if suitable for the driver. Calibrate current zero and gain against a meter, including low-current output headroom. Compute the firmware absolute code limit and FPGA compiled ceiling from actual calibration; account for tolerances. Check the inline shunt measures flyback current. Set and measure the comparator threshold/hysteresis independently. Operate the E-stop and break each interlock wire while monitoring the actual MOSFET gate.

Acceptance: no unintended pulse at startup; physical fault removes gate drive promptly even if the MCU and FPGA are halted. Record the measured gate-off delay and coil-current decay separately. Only then set `power_stage_ready=true` and `LEV_COMMISSIONED=1` with low supply/current limits, still supported mechanically. Keep `calibration_ready=false`.

## 5. Tune the inner current loop

Select current-test mode while stopped. Start at zero target. Begin with Ki zero and small Kp; increase until current follows small supported-load steps without sustained ringing. Add a modest Ki to remove steady error. Convert gains into the documented Q8.8 per-sample units. Examine response across PWM duty and supply voltage. Avoid integral gains below one representable step unless a different fixed-point scale is implemented.

Acceptance: no sustained oscillation, no saturation under nominal commands, bounded overshoot, and measured response sufficiently faster than the intended position loop. Sweep current through the allowed range and verify the cap. Test MCU cable removal, identical frozen packets, checksum errors, missed updates, ADC disconnect, comparator trip, permit loss, and E-stop. An ADC disconnect can yield a plausible stuck value; the physical cutoff remains necessary. Retain scope captures, not just a pass checkbox.

## 6. Fit Hall calibration and tune the position loop

Follow docs/calibration.md with current control already characterized. Fit only a validated local operating region. Verify sensor sign by moving the supported object downward at fixed current: reported gap must increase. Measure false position change after a current step with the object clamped. Set measured operating range, coefficients, hover current, and candidate PD gains in `config.c`. Validate by recompiling and running host checks before setting `calibration_ready=true`.

At the nominal gap, use a catch tray, a current-limited supply, and a supported release. Tune PD for damping before adding integral. Expand the commanded range gradually. Record recovery from small disturbances and current saturation. Test the full path while refreshing web pages repeatedly to check the MCU deadline budget.

## 7. Demonstrate and preserve evidence

The revised proposal targets sustainable continuous suspension and visible commanded motion with a maximum gap of 10 mm. Measure an extended run through thermal equilibrium and command motion over the validated interval, retaining the exact duration and trajectory; a finite run cannot prove indefinite operation. Check page stop, the 50 ms command watchdog, overcurrent, and physical interlock operation. Record target/estimated gap versus an independent ruler/camera reference, current, PWM, actual speed, settling time, RMS noise, and coil temperature. The former draft's 30-second/three-target numbers are not the revised proposal specifications.

Complete the checkoff matrix, final KiCad schematics, photos, team information, and demo video. Upload/publish only when the team has reviewed the actual evidence and the instructor's current submission requirements.
