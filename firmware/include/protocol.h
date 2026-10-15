#ifndef LEV_PROTOCOL_H
#define LEV_PROTOCOL_H
#include <stdbool.h>
#include <stdint.h>
#define LEV_FRAME_BYTES 16
typedef struct {
    uint16_t sample_id, hall1, hall2, current, duty;
    uint8_t faults, flags;
} lev_telemetry_t;
uint16_t lev_crc16(const uint8_t *p, unsigned n);
void lev_pack(uint8_t p[16], uint16_t seq, bool enable, bool clear,
              uint16_t target, uint16_t kp, uint16_t ki, uint16_t limit);
bool lev_unpack(const uint8_t p[16], lev_telemetry_t *t);
#endif
