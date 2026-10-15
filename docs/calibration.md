# Hall/current calibration and controller tuning

## Measurements

Use a fixed jig and known gap reference. Log `gap_mm,hall1,hall2,current_a` rows in CSV; `data/calibration-format.csv` gives the header. Measure actual current, not just commanded current. Sample a grid of gaps and currents spanning the proposed operating interval, with repeated measurements after reversing each sweep. Include coil-only baseline, object orientation, supply, temperature, sensor mount dimensions, and ADC filter components in the experiment notes.

Use a second independently collected sweep for holdout validation. Randomly splitting adjacent samples from one stationary measurement understates error. Repeat across relevant coil temperatures and several current trajectories. Hold the object fixed during current steps to quantify how much coil-field change leaks into estimated position. A static fit may pass while sequential-channel transient error makes feedback unusable.

The local affine model is a practical first model, not a physical cancellation guarantee. Nonmonotonic or degenerate sensor responses require a change of placement, object, sensitivity, or estimator. A table/nonlinear estimator is a future design change if the local fit fails; it is not silently implemented by the calibration script. Restrict the committed gap/current interval to where this model has been validated.

## Fit and validate

```powershell
python -m pip install -r tools/requirements.txt
python tools/calibrate.py data/raw/training.csv data/raw/holdout.csv
```

The script normalizes inputs, checks matrix rank and conditioning, fits least squares, prints training/holdout errors, and emits candidate `hall_c` coefficients only when numerical acceptance passes. It rejects near-rail Hall samples and a holdout current/gap range outside the training range. It does not change firmware or enable outputs. Save reviewed coefficients and measured validity ranges in `config.c`; preserve data deliberately under `data/results` when suitable for the public repository. Files under `data/raw` are ignored by default.

Current conversion is `I=(ADC-current_zero)/counts_per_amp`. Fit zero/gain against an independent meter over the intended range. Convert an absolute trip current into `round(current_zero + counts_per_amp * Itrip)` and choose a conservative threshold accounting for uncertainty. Keep the FPGA ceiling, command limit, comparator, and firmware cap consistent. The runtime cap should remain below the physical trip threshold.

## Gains and practical limits

The height loop uses mm, A, and seconds: Kp has A/mm; Kd has A·s/mm; Ki has A/(mm·s). Begin with Ki zero. Verify lift direction on a supported object before release. The current loop uses ADC counts and PWM ticks, with Ki already multiplied by 0.0001 s. Quantizing a small Ki to zero changes loop behavior; verify the quantized loop rather than only the floating-point design.

Tune around one measured equilibrium. The force model may change significantly with gap. `hover_a` is a constant bias in this implementation; there is no unvalidated gain scheduling or feedforward lookup. The feasible height interval may therefore be smaller than the candidate 8–14 mm values. Browser targets and fault limits must be updated to match the tested interval. Sampling rate, delay, sensor filtering, coil decay, object mass, and lateral/orientation motion all affect stability.
