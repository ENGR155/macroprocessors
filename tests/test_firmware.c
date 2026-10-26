#include "web.h"
#include "runtime.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static lev_config_t cfg(void) {
    lev_config_t c=lev_config;
    c.power_stage_ready=true; c.calibration_ready=true;
    c.counts_per_amp=1000; c.max_current_a=1;
    c.gap_min_mm=8; c.gap_max_mm=10; c.gap_start_mm=9;
    c.hall_c[0]=0; c.hall_c[1]=0.005f;
    c.kp=0.1f; c.ki=0; c.kd=0; c.hover_a=0.4f;
    return c;
}
static void request(const char *r,lev_control_t *s,lev_config_t *c,lev_telemetry_t *t,bool *clear) {
    char b[64]; snprintf(b,sizeof b,"/REQ:%s\n",r);
    assert(lev_web_request(b,s,c,t,clear));
}
static void status(uint8_t p[8],uint8_t seq,uint8_t flags,uint8_t faults) {
    uint8_t body[8]={0x50,seq,0,100,faults,0,0,0};
    memcpy(p,body,8); p[0]|=flags;
    uint16_t crc=lev_crc16(p,6); p[6]=(uint8_t)(crc>>8); p[7]=(uint8_t)crc;
}
static void sample(lev_runtime_t *r,uint32_t us,uint8_t flags) {
    lev_adc_t adc={400,1900,2100}; uint8_t tx[8],rx[8];
    uint8_t previous=r->sequence;
    lev_runtime_sample(r,&adc,us,tx);
    assert(tx[2]==1 && tx[3]==144); /* current belongs to this local scan */
    status(rx,previous,flags,0); lev_runtime_feedback(r,rx,true);
}
static void runtime_tests(void) {
    lev_config_t c=cfg(); lev_runtime_t r; lev_runtime_init(&r,&c);
    assert(LEV_FRAME_BYTES==8 && LEV_SAMPLE_HZ==5000 && LEV_POSITION_DECIMATION==5);
    for (unsigned i=1;i<=4;i++) sample(&r,i*200,1);
    assert(r.control.gap_mm==0); /* no outer control until fifth reading */
    sample(&r,1000,1); assert(fabsf(r.control.gap_mm-9.5f)<0.0001f);
    assert(lev_arm(&r.control,&c,&r.telemetry));
    for (unsigned i=6;i<=9;i++) { sample(&r,i*200,3); assert(r.control.output_a==0); }
    sample(&r,2000,3); assert(fabsf(r.control.output_a-0.45f)<0.0001f);
    for (unsigned i=11;i<270;i++) sample(&r,i*200,3); /* sequence wraps at 256 */
    assert(r.control.active && r.sequence==(uint8_t)269);
    uint8_t rx[8]; status(rx,(uint8_t)(r.sequence-1),3,0);
    lev_runtime_feedback(&r,rx,true); assert(r.control.tripped && !r.control.active);
    lev_runtime_init(&r,&c); sample(&r,200,1); sample(&r,600,1);
    assert(r.control.tripped); /* dropped 5 kHz deadline */
    lev_runtime_init(&r,&c); sample(&r,200,1); sample(&r,400,1);
    assert(lev_arm(&r.control,&c,&r.telemetry));
    lev_runtime_feedback(&r,rx,false); assert(r.control.tripped && !r.control.active);
    r.control.tripped=false; assert(!lev_arm(&r.control,&c,&r.telemetry));
    lev_runtime_init(&r,&c); sample(&r,200,1); sample(&r,400,1);
    assert(lev_arm(&r.control,&c,&r.telemetry));
    r.last_sample_us=5000000; sample(&r,5000200,3); assert(r.control.tripped); /* browser lease */
    lev_runtime_init(&r,&c); sample(&r,UINT32_MAX-199,1); sample(&r,0,1);
    assert(!r.control.tripped); /* free-running microsecond counter wrap */
    r.control.tripped=false; status(rx,r.sequence,1,2);
    lev_runtime_feedback(&r,rx,true); assert(!r.control.tripped); /* old fault reply during clear */
    lev_adc_t high={1241,1900,2100}; uint8_t tx[8];
    lev_runtime_sample(&r,&high,200,tx); assert(r.control.tripped && !(tx[0]&1));
}
int main(void) {
    assert(lev_crc16((const uint8_t *)"123456789",9)==0x29b1);
    uint8_t p[8]; lev_pack(p,0x34,true,false,500,800);
    assert(p[0]==0xa1 && p[1]==0x34 && p[2]==1 && p[3]==244 && p[4]==3 && p[5]==32);
    assert(lev_crc16(p,8)==0);
    lev_telemetry_t t={.sample_id=7,.hall1=1900,.hall2=2100,.current=400,.flags=1};
    status(p,0x34,3,0); lev_telemetry_t decoded=t; assert(lev_unpack(p,&decoded));
    assert(decoded.hall1==1900 && decoded.current==400 && decoded.sample_id==7);
    assert(decoded.accepted_sequence==0x34 && decoded.duty==100 && decoded.flags==3);
    p[2]^=1; assert(!lev_unpack(p,&decoded));
    lev_config_t c=cfg(); lev_control_t s; lev_control_init(&s,&c);
    assert(lev_config.gap_max_mm==10);
    assert(!lev_arm(&s,&lev_config,&t));
    assert(lev_arm(&s,&c,&t)); assert(lev_control_step(&s,&c,&t,0.001f));
    assert(fabsf(s.output_a-0.45f)<0.0001f);
    t.hall1=1700; c.max_velocity_mm_s=1000; assert(lev_control_step(&s,&c,&t,0.001f));
    assert(fabsf(s.output_a-0.35f)<0.0001f);
    c.ki=100; t.hall1=2000;
    for(int i=0;i<1000;i++) assert(lev_control_step(&s,&c,&t,0.001f));
    assert(s.output_a<=1 && fabsf(s.integral)<0.6f);
    t.hall1=4095; assert(!lev_control_step(&s,&c,&t,0.001f));
    assert(!s.active && s.tripped && s.output_a==0);
    assert(!lev_arm(&s,&c,&t));
    bool clear=false; request("clear",&s,&c,&t,&clear); assert(clear && !s.tripped);
    request("modeamp",&s,&c,&t,&clear); assert(s.current_mode);
    for(int i=0;i<100;i++) request("up",&s,&c,&t,&clear);
    assert(s.manual_a==1);
    assert(lev_arm(&s,&c,&t)); assert(lev_control_step(&s,&c,&t,0.001f));
    assert(s.output_a<=0.000101f);
    request("modegap",&s,&c,&t,&clear); assert(s.current_mode);
    assert(!lev_control_step(&s,&c,&t,0.004f) && s.tripped);
    c=cfg(); lev_control_init(&s,&c); t.hall1=1900;
    c.kd=0.01f; assert(lev_arm(&s,&c,&t));
    assert(lev_control_step(&s,&c,&t,0.001f)); assert(s.velocity==0);
    t.hall1=1902; assert(lev_control_step(&s,&c,&t,0.001f)); assert(s.velocity>0);
    t.hall1=2000; assert(!lev_control_step(&s,&c,&t,0.001f)); /* velocity ceiling */
    c=cfg(); c.hall_sensors=1; t.hall1=1900; t.hall2=0;
    lev_control_init(&s,&c); assert(lev_arm(&s,&c,&t));
    assert(lev_control_step(&s,&c,&t,0.001f)); /* absent second sensor is allowed */
    lev_stop(&s,false); c.hall_c[2]=0.001f; assert(!lev_arm(&s,&c,&t));
    c.hall_c[2]=0; c.hall_sensors=2; assert(lev_arm(&s,&c,&t));
    assert(!lev_control_step(&s,&c,&t,0.001f)); /* installed second sensor at rail */
    t.faults=2; assert(!lev_arm(&s,&c,&t));
    request("stop",&s,&c,&t,&clear); request("modegap",&s,&c,&t,&clear);
    for(int i=0;i<100;i++) request("up",&s,&c,&t,&clear);
    assert(s.goal_mm==10);
    char bad[]="/REQ:armjunk"; assert(!lev_web_request(bad,&s,&c,&t,&clear));
    char page[3072]; size_t n=lev_web_render(page,sizeof page,&s,&t,&c);
    assert(n>0 && !strncmp(page,"<!DOCTYPE html>",15) && strstr(page,"</html>"));
    assert(strstr(page,"1;url=/")); assert(lev_web_render(page,10,&s,&t,&c)==0);
    runtime_tests();
    puts("Firmware PASS: 8-byte protocol, paired current, 5:1 control timing, ACK/wrap, deadlines, limits, sensor modes, faults, web");
}
