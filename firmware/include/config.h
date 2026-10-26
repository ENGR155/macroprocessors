#ifndef LEV_CONFIG_H
#define LEV_CONFIG_H
#include <stdbool.h>
#include <stdint.h>

/* Engineering units are mm, seconds, amperes. Values below are EXAMPLES.
 * Set readiness flags only after completing docs/bringup.md. Rebuild both
 * devices when changing current scaling or the FPGA hard limit. */
typedef struct {
    bool power_stage_ready, calibration_ready;
    unsigned hall_sensors; /* 1: CH1/current compensation; 2: CH1/CH2/current fit */
    float current_zero, counts_per_amp, max_current_a;
    float gap_min_mm, gap_max_mm, gap_start_mm;
    float gap_slew_mm_s, current_slew_a_s, max_velocity_mm_s;
    float kp, ki, kd, hover_a, derivative_alpha;
    /* gap = c0 + c1*H1 + c2*H2 + c3*current_A. Local affine model only. */
    float hall_c[4];
    uint16_t hard_limit_counts; /* PI gains now live in FPGA project_config.svh. */
} lev_config_t;
extern const lev_config_t lev_config;
#endif
