#include "protocol.h"
static void put16(uint8_t *p, uint16_t v) { p[0]=(uint8_t)(v>>8); p[1]=(uint8_t)v; }
static uint16_t get16(const uint8_t *p) { return (uint16_t)((p[0]<<8)|p[1]); }
uint16_t lev_crc16(const uint8_t *p, unsigned n) {
    uint16_t c=0xffff;
    while (n--) {
        c^=(uint16_t)*p++<<8;
        for (unsigned j=0;j<8;j++) c=(uint16_t)((c&0x8000)?(c<<1)^0x1021:c<<1);
    }
    return c;
}
void lev_pack(uint8_t p[16], uint16_t seq, bool en, bool clear,
              uint16_t target, uint16_t kp, uint16_t ki, uint16_t limit) {
    p[0]=0xa5; p[1]=1; put16(p+2,seq); p[4]=en; p[5]=clear;
    put16(p+6,target); put16(p+8,kp); put16(p+10,ki); put16(p+12,limit);
    put16(p+14,lev_crc16(p,14));
}
bool lev_unpack(const uint8_t p[16], lev_telemetry_t *t) {
    if (p[0]!=0x5a || p[1]!=1 || get16(p+14)!=lev_crc16(p,14)) return false;
    t->sample_id=get16(p+2); t->hall1=get16(p+4); t->hall2=get16(p+6);
    t->current=get16(p+8); t->duty=get16(p+10); t->faults=p[12]; t->flags=p[13];
    return t->hall1<=4095 && t->hall2<=4095 && t->current<=4095 && t->duty<=1080;
}
