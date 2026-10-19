#include "web.h"
#include <stdio.h>
#include <string.h>
#include <math.h>
bool lev_web_request(char *line,lev_control_t *s,const lev_config_t *c,
                     const lev_telemetry_t *t,bool *clear) {
    size_t n=strlen(line);
    while (n && (line[n-1]=='\n'||line[n-1]=='\r')) line[--n]=0;
    if (strncmp(line,"/REQ:",5)) return false;
    const char *r=line+5;
    if (!strcmp(r,"")) return true;
    if (!strcmp(r,"stop")) { lev_stop(s,false); return true; }
    if (!strcmp(r,"clear")) {
        if (!s->active) { s->tripped=false; *clear=true; } return true;
    }
    if (!strcmp(r,"arm")) { (void)lev_arm(s,c,t); return true; }
    if (!strcmp(r,"modegap") || !strcmp(r,"modeamp")) {
        if (!s->active) { s->current_mode=!strcmp(r,"modeamp"); s->manual_a=0; }
        return true;
    }
    if (!strcmp(r,"up") || !strcmp(r,"down")) {
        float d=!strcmp(r,"up")?1.0f:-1.0f;
        if (s->current_mode) {
            s->manual_a+=d*0.025f;
            if (s->manual_a<0) s->manual_a=0;
            if (s->manual_a>c->max_current_a) s->manual_a=c->max_current_a;
        } else {
            s->goal_mm+=d*0.5f;
            if (s->goal_mm<c->gap_min_mm) s->goal_mm=c->gap_min_mm;
            if (s->goal_mm>c->gap_max_mm) s->goal_mm=c->gap_max_mm;
        }
        return true;
    }
    return false;
}
size_t lev_web_render(char *out,size_t cap,const lev_control_t *s,
                      const lev_telemetry_t *t,const lev_config_t *c) {
    /* Integers avoid a firmware dependency on printf float formatting.
     * Target is a downward gap: increasing it lowers the ball. */
    int n=snprintf(out,cap,
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<meta http-equiv=\"refresh\" content=\"1;url=/\">"
        "<title>E155 Magnetic Levitation</title><style>"
        "body{font:18px system-ui;max-width:42rem;margin:2rem auto;padding:1rem;background:#eef3f6;color:#182a3a}"
        "a{display:inline-block;padding:.8rem;margin:.3rem;background:white;border:1px solid #678;border-radius:.5rem;color:#124}"
        ".stop{background:#9e1930;color:white}</style></head><body>"
        "<h1>Magnetic Levitation</h1><p>Status: <b>%s</b>. FPGA enabled: %s. FPGA faults: 0x%02x.</p>"
        "<p>Power stage verified: %s. Position calibration verified: %s.</p>"
        "<p>Mode: %s. Target gap: %d micrometres. Estimated gap: %d micrometres.</p>"
        "<p>Current target: %d mA. Measured: %d mA. PWM: %u / 1200.</p>"
        "<p>ADC current / Hall 1 / Hall 2: %u / %u / %u. Sample: %u.</p>"
        "<p><a class=\"stop\" href=\"/stop\">STOP</a><a href=\"/arm\">Arm</a>"
        "<a href=\"/clear\">Clear fault</a></p>"
        "<p><a href=\"/modegap\">Height mode</a><a href=\"/modeamp\">Current test mode</a></p>"
        "<p><a href=\"/down\">Decrease target</a><a href=\"/up\">Increase target</a></p>"
        "<p>Gap is measured down from the coil: a larger gap lowers the object. "
        "Steps: 0.5 mm or 25 mA. Mode changes require stopping. "
        "The controller stops after 5 seconds without page activity. Use the physical emergency stop for immediate shutdown.</p>"
        "</body></html>",
        s->tripped?"FAULT":(s->active?"ACTIVE":"STOPPED"),(t->flags&2)?"yes":"no",t->faults,
        c->power_stage_ready?"yes":"no",c->calibration_ready?"yes":"no",
        s->current_mode?"current test":"height",(int)(s->goal_mm*1000),
        isfinite(s->gap_mm)?(int)(s->gap_mm*1000):0,
        (int)((s->current_mode?s->manual_a:s->output_a)*1000),
        isfinite(s->current_a)?(int)(s->current_a*1000):0,
        t->duty,t->current,t->hall1,t->hall2,t->sample_id);
    if (n<0 || (size_t)n>=cap) { if(cap) out[0]=0; return 0; }
    return (size_t)n;
}
