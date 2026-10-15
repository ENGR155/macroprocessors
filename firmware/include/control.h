#ifndef LEV_CONTROL_H
#define LEV_CONTROL_H
#include "config.h"
#include "protocol.h"
typedef struct {
    float goal_mm, ramp_mm, manual_a, ramp_a, gap_mm, current_a;
    float previous_mm, velocity, integral, output_a;
    bool active, current_mode, tripped, have_position;
} lev_control_t;
void lev_control_init(lev_control_t *s, const lev_config_t *c);
void lev_stop(lev_control_t *s, bool trip);
bool lev_arm(lev_control_t *s, const lev_config_t *c, const lev_telemetry_t *t);
bool lev_control_step(lev_control_t *s, const lev_config_t *c,
                      const lev_telemetry_t *t, float dt);
#endif
