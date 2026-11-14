# Selecting and recording Hall positions

The adjustment is vertical. Each fixed indexed rail and moving carriage selects a height for one fitted DRV5056 package. The sensor's broad marked face remains horizontal; it can face up or down to select the useful magnetic polarity. The body does not rotate with height adjustment.

Select an indexed position for coarse placement, slide within that position for fine adjustment, then tighten the clamp. Move the printed holder rather than pulling on sensor leads. Provide a flexible service loop between the moving wire strain relief and the fixed frame. Record the index and fine offset independently for the upper and lower sensors so the setting can be reproduced.

The holes and travel provide positioning options. They do not guarantee that every position gives a usable signal. Select final positions using actual sensor readings with the installed helper-stack location, polarity, intended payload gaps and coil-current range. Both sensors should remain within the manufacturer's specified linear output range throughout that operating envelope.

Your A3 and A4 have different sensitivities. Equal raw output voltages do not establish equal magnetic fields. Interpret each reading using its own calibration; do not move one sensor solely to make the two voltages match. Neither mechanical symmetry nor matching readings establishes cancellation of the electromagnet's field.

After choosing and locking the positions, calibrate the complete assembly at those settings. Moving either sensor or changing the helper-stack configuration changes the measurement geometry and requires updated calibration. Follow the package pin view when flipping a sensor; the outer pins exchange their physical positions.

Primary sensor reference: [TI DRV5056 datasheet](https://www.ti.com/lit/ds/symlink/drv5056.pdf). The README and independent check report document the actual mechanical travel, hardware, print jobs and remaining operating limits.
