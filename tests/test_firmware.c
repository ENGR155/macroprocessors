#include "web.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static lev_config_t cfg(void) {
    lev_config_t c=lev_config;
    c.power_stage_ready=true; c.calibration_ready=true;
    c.counts_per_amp=1000; c.max_current_a=1;
    c.hall_c[0]=0; c.hall_c[1]=0.005f;
    c.kp=0.1f; c.ki=0; c.kd=0; c.hover_a=0.4f;
    return c;
}
static void request(const char *r,lev_control_t *s,lev_config_t *c,lev_telemetry_t *t,bool *clear) {
    char b[64]; snprintf(b,sizeof b,"/REQ:%s\n",r);
    assert(lev_web_request(b,s,c,t,clear));
}
int main(void) {
    assert(lev_crc16((const uint8_t *)"123456789",9)==0x29b1);
    uint8_t p[16]; lev_pack(p,0x1234,true,false,800,256,32,1241);
    assert(p[0]==0xa5 && p[2]==0x12 && p[3]==0x34 && p[6]==3 && p[7]==32);
    assert(lev_crc16(p,16)==0); /* big-endian appended CRC */
    lev_telemetry_t t={.hall1=2200,.hall2=2100,.current=400,.flags=1};
    uint8_t status[16]={0x5a,1,0,1,8,152,8,52,1,144,0,100,0,1,0,0};
    uint16_t crc=lev_crc16(status,14); status[14]=(uint8_t)(crc>>8);status[15]=(uint8_t)crc;
    lev_telemetry_t decoded; assert(lev_unpack(status,&decoded));
    assert(decoded.hall1==2200 && decoded.current==400);
    status[8]^=1; assert(!lev_unpack(status,&decoded));
    lev_config_t c=cfg(); lev_control_t s; lev_control_init(&s,&c);
    assert(!lev_arm(&s,&lev_config,&t)); /* shipped configuration cannot drive coil */
    assert(lev_arm(&s,&c,&t)); assert(lev_control_step(&s,&c,&t,0.001f));
    assert(fabsf(s.output_a-0.5f)<0.0001f); /* ball low -> more lift */
    t.hall1=1800; assert(lev_control_step(&s,&c,&t,0.001f));
    assert(fabsf(s.output_a-0.3f)<0.0001f);
    c.ki=100; t.hall1=2700;
    for(int i=0;i<1000;i++) assert(lev_control_step(&s,&c,&t,0.001f));
    assert(s.output_a<=1 && fabsf(s.integral)<0.3f); /* anti-windup */
    t.hall1=4095; assert(!lev_control_step(&s,&c,&t,0.001f));
    assert(!s.active && s.tripped && s.output_a==0);
    assert(!lev_arm(&s,&c,&t));
    bool clear=false; request("clear",&s,&c,&t,&clear); assert(clear && !s.tripped);
    request("modeamp",&s,&c,&t,&clear); assert(s.current_mode);
    for(int i=0;i<100;i++) request("up",&s,&c,&t,&clear);
    assert(s.manual_a==1);
    assert(lev_arm(&s,&c,&t)); assert(lev_control_step(&s,&c,&t,0.001f));
    assert(s.output_a<=0.000101f); /* current slew limit */
    request("modegap",&s,&c,&t,&clear); assert(s.current_mode);
    assert(!lev_control_step(&s,&c,&t,0.004f) && s.tripped); /* missed deadline */
    c=cfg(); lev_control_init(&s,&c); t.hall1=2200;
    c.kd=0.01f; assert(lev_arm(&s,&c,&t));
    assert(lev_control_step(&s,&c,&t,0.001f)); assert(s.velocity==0); /* no derivative kick */
    t.hall1=2220; assert(lev_control_step(&s,&c,&t,0.001f)); assert(s.velocity>0);
    t.faults=2; assert(!lev_control_step(&s,&c,&t,0.001f));
    char bad[]="/REQ:armjunk"; assert(!lev_web_request(bad,&s,&c,&t,&clear));
    char page[3072]; size_t n=lev_web_render(page,sizeof page,&s,&t,&c);
    assert(n>0 && !strncmp(page,"<!DOCTYPE html>",15) && strstr(page,"</html>"));
    assert(strstr(page,"1;url=/")); assert(lev_web_render(page,10,&s,&t,&c)==0);
    puts("Firmware: CRC, framing, control sign, saturation, anti-windup, slew, faults, routes, HTML PASS");
}
