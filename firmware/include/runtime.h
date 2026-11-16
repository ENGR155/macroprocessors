#ifndef LEV_RUNTIME_H
#define LEV_RUNTIME_H
#include "control.h"
typedef struct { uint16_t current, hall1, hall2; } lev_adc_t;
typedef struct {
    lev_control_t control;
    lev_telemetry_t telemetry;
    const lev_config_t *config;
    uint32_t last_sample_us, last_request_us;
    uint8_t sequence, previous_sequence;
    unsigned position_phase, arm_samples;
    bool have_sample, have_reply, clear, link_ok;
} lev_runtime_t;
void lev_runtime_init(lev_runtime_t *s,const lev_config_t *c);
/* Called by the DMA scan at 5 kHz, before transmitting its paired current. */
void lev_runtime_sample(lev_runtime_t *s,const lev_adc_t *adc,uint32_t now_us,
                        uint8_t tx[LEV_FRAME_BYTES]);
/* The reply acknowledges the PREVIOUS packet, since SPI is full duplex. */
void lev_runtime_feedback(lev_runtime_t *s,const uint8_t rx[LEV_FRAME_BYTES],bool ok);
#endif
