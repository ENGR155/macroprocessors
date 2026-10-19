#include "config.h"
const lev_config_t lev_config = {
    .power_stage_ready = false, .calibration_ready = false,
    /* INA240A1 (20 V/V), 0.100 ohm inline shunt, 3.3 V ADC reference. */
    .current_zero = 0, .counts_per_amp = 4096.0f * 2.0f / 3.3f,
    .max_current_a = 0.40f,
    .gap_min_mm = 8, .gap_max_mm = 14, .gap_start_mm = 10,
    .gap_slew_mm_s = 1, .current_slew_a_s = 0.1f,
    /* No unmeasured control gains are enabled by default. */
    .kp = 0, .ki = 0, .kd = 0, .hover_a = 0,
    .derivative_alpha = 0.2f, .hall_c = {0, 0, 0, 0},
    .current_kp_q8 = 0, .current_ki_q8 = 0,
    .hard_limit_counts = 1241 /* about 0.50 A, independent of web limit */
};
