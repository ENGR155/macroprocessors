#include "protocol.h"
static void put16(uint8_t *p, uint16_t v) { p[0]=(uint8_t)(v>>8); p[1]=(uint8_t)v; }
static uint16_t get16(const uint8_t *p) { return (uint16_t)((p[0]<<8)|p[1]); }
uint16_t lev_crc16(const uint8_t *p, unsigned n) {
    /* Nibble table keeps both 5 kHz DMA callbacks inside the SPI budget. */
    static const uint16_t table[16]={0x0000,0x1021,0x2042,0x3063,
        0x4084,0x50a5,0x60c6,0x70e7,0x8108,0x9129,0xa14a,0xb16b,
        0xc18c,0xd1ad,0xe1ce,0xf1ef};
    uint16_t c=0xffff;
    while (n--) {
        c^=(uint16_t)*p++<<8;
        c=(uint16_t)((c<<4)^table[c>>12]);
        c=(uint16_t)((c<<4)^table[c>>12]);
    }
    return c;
}
void lev_pack(uint8_t p[LEV_FRAME_BYTES], uint8_t seq, bool en, bool clear,
              uint16_t measured, uint16_t target) {
    p[0]=(uint8_t)(0xa0u | (en?1u:0u) | (clear?2u:0u)); p[1]=seq;
    put16(p+2,measured); put16(p+4,target);
    put16(p+6,lev_crc16(p,6));
}
bool lev_unpack(const uint8_t p[LEV_FRAME_BYTES], lev_telemetry_t *t) {
    if ((p[0]&0xfcu)!=0x50 || p[5]!=0 || get16(p+6)!=lev_crc16(p,6)
        || get16(p+2)>1080) return false;
    t->accepted_sequence=p[1]; t->duty=get16(p+2); t->faults=p[4]; t->flags=p[0]&3u;
    return true;
}
