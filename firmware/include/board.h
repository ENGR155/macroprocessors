#ifndef LEV_BOARD_H
#define LEV_BOARD_H
#include <stdbool.h>
#include <stdint.h>
#include "runtime.h"
void board_init(void);
uint32_t board_ms(void);
uint32_t board_us(void);
void board_permit(bool on);
typedef void (*board_adc_callback_t)(const lev_adc_t *,uint32_t,uint8_t [LEV_FRAME_BYTES]);
typedef void (*board_reply_callback_t)(const uint8_t [LEV_FRAME_BYTES],bool);
void board_start_sampling(unsigned hall_sensors,board_adc_callback_t adc,board_reply_callback_t reply);
uint32_t board_lock(void);
void board_unlock(uint32_t previous);
bool board_rx(char *c);
bool board_tx(char c);
#endif
