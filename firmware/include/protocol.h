#ifndef LEV_PROTOCOL_H
#define LEV_PROTOCOL_H
#include <stdbool.h>
#include <stdint.h>
#define LEV_FRAME_BYTES 8
#define LEV_SAMPLE_HZ 5000u
#define LEV_POSITION_DECIMATION 5u
#define LEV_SAMPLE_US (1000000u / LEV_SAMPLE_HZ)
typedef struct {
    uint16_t sample_id, hall1, hall2, current, duty;
    uint8_t faults, flags, accepted_sequence;
} lev_telemetry_t;
uint16_t lev_crc16(const uint8_t *p, unsigned n);
void lev_pack(uint8_t p[LEV_FRAME_BYTES], uint8_t seq, bool enable, bool clear,
              uint16_t measured, uint16_t target);
/* Updates FPGA status only; local ADC readings and sample ID are preserved. */
bool lev_unpack(const uint8_t p[LEV_FRAME_BYTES], lev_telemetry_t *t);
#endif
