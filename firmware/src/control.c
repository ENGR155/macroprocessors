#include "control.h"
#include <math.h>
#include <string.h>
static float clampf(float x,float a,float b) { return x<a?a:(x>b?b:x); }
static float slew(float x,float goal,float rate,float dt) {
    return x+clampf(goal-x,-rate*dt,rate*dt);
}
void lev_control_init(lev_control_t *s,const lev_config_t *c) {
    memset(s,0,sizeof(*s)); s->goal_mm=c->gap_start_mm; s->ramp_mm=s->goal_mm;
}
void lev_stop(lev_control_t *s,bool trip) {
    s->active=false; s->output_a=0; s->ramp_a=0; s->integral=0;
    s->have_position=false; s->velocity=0; s->tripped|=trip;
}
bool lev_arm(lev_control_t *s,const lev_config_t *c,const lev_telemetry_t *t) {
    if (s->tripped || !c->power_stage_ready || (!s->current_mode && !c->calibration_ready)
        || !(c->counts_per_amp>0) || !isfinite(c->counts_per_amp)
        || !(c->max_current_a>0) || t->faults || !(t->flags&1)) return false;
    s->active=true; s->integral=0; s->velocity=0; s->have_position=false;
    s->ramp_mm=s->goal_mm; s->ramp_a=0;
    return true;
}
bool lev_control_step(lev_control_t *s,const lev_config_t *c,
                      const lev_telemetry_t *t,float dt) {
    s->current_a=((float)t->current-c->current_zero)/c->counts_per_amp;
    s->gap_mm=c->hall_c[0]+c->hall_c[1]*t->hall1+c->hall_c[2]*t->hall2
              +c->hall_c[3]*s->current_a;
    if (!s->active) { s->output_a=0; return true; }
    bool bad=t->faults || !(t->flags&1) || !isfinite(s->current_a)
             || s->current_a>c->max_current_a+0.05f || s->current_a < -0.05f
             || !(dt>=0.0005f && dt<=0.0015f);
    if (!s->current_mode)
        bad|=!isfinite(s->gap_mm) || t->hall1<16 || t->hall1>4079
              || t->hall2<16 || t->hall2>4079
              || s->gap_mm<c->gap_min_mm || s->gap_mm>c->gap_max_mm;
    if (bad) { lev_stop(s,true); return false; }
    if (s->current_mode) {
        s->ramp_a=slew(s->ramp_a,clampf(s->manual_a,0,c->max_current_a),c->current_slew_a_s,dt);
        s->output_a=s->ramp_a; return true;
    }
    s->goal_mm=clampf(s->goal_mm,c->gap_min_mm,c->gap_max_mm);
    s->ramp_mm=slew(s->ramp_mm,s->goal_mm,c->gap_slew_mm_s,dt);
    /* Gap increases downward. Positive error or falling velocity demands lift. */
    float v=s->have_position?(s->gap_mm-s->previous_mm)/dt:0;
    s->velocity+=c->derivative_alpha*(v-s->velocity);
    s->previous_mm=s->gap_mm; s->have_position=true;
    float e=s->gap_mm-s->ramp_mm;
    float trial=s->integral+c->ki*e*dt;
    float u=c->hover_a+c->kp*e+c->kd*s->velocity+trial;
    if ((u>=0 && u<=c->max_current_a) || (u>c->max_current_a && e<0) || (u<0 && e>0))
        s->integral=clampf(trial,-c->max_current_a,c->max_current_a);
    u=c->hover_a+c->kp*e+c->kd*s->velocity+s->integral;
    if (!isfinite(u)) { lev_stop(s,true); return false; }
    s->output_a=clampf(u,0,c->max_current_a); return true;
}
