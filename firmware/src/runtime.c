#include "runtime.h"
#include <math.h>
#include <string.h>
void lev_runtime_init(lev_runtime_t *s,const lev_config_t *c) {
    memset(s,0,sizeof(*s)); s->config=c; lev_control_init(&s->control,c);
}
void lev_runtime_sample(lev_runtime_t *s,const lev_adc_t *adc,uint32_t now_us,
                        uint8_t tx[LEV_FRAME_BYTES]) {
    const lev_config_t *c=s->config;
    uint32_t elapsed=now_us-s->last_sample_us;
    if ((s->have_sample && (elapsed<150 || elapsed>250))
        || (s->control.active && now_us-s->last_request_us>5000000u)
        || adc->current>4095 || adc->hall1>4095 || adc->hall2>4095
        || adc->current>=c->hard_limit_counts) lev_stop(&s->control,true);
    s->last_sample_us=now_us; s->have_sample=true;
    s->telemetry.current=adc->current; s->telemetry.hall1=adc->hall1;
    s->telemetry.hall2=c->hall_sensors==2?adc->hall2:0;
    s->telemetry.sample_id++;
    if (++s->position_phase==LEV_POSITION_DECIMATION) {
        s->position_phase=0;
        (void)lev_control_step(&s->control,c,&s->telemetry,0.001f);
    }
    float target=s->control.output_a*c->counts_per_amp+c->current_zero;
    if (!isfinite(target) || target<0) target=0;
    if (target>c->hard_limit_counts) target=c->hard_limit_counts;
    lev_pack(tx,++s->sequence,s->control.active && s->link_ok,s->clear,
             adc->current,(uint16_t)target);
    s->clear=false;
}
void lev_runtime_feedback(lev_runtime_t *s,const uint8_t rx[LEV_FRAME_BYTES],bool ok) {
    ok=ok && lev_unpack(rx,&s->telemetry);
    if (s->have_reply)
        ok=ok && (s->telemetry.flags&1) &&
           s->telemetry.accepted_sequence==s->previous_sequence;
    s->previous_sequence=s->sequence; s->have_reply=true; s->link_ok=ok;
    if (!ok) s->telemetry.flags=0; /* stale data cannot be used to re-arm */
    if (!ok || (s->telemetry.faults && s->control.active)) lev_stop(&s->control,true);
    if (s->control.active) {
        if (++s->arm_samples>10 && !(s->telemetry.flags&2)) lev_stop(&s->control,true);
    } else s->arm_samples=0;
}
