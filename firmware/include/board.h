#ifndef LEV_BOARD_H
#define LEV_BOARD_H
#include <stdbool.h>
#include <stdint.h>
void board_init(void);
uint32_t board_ms(void);
uint32_t board_us(void);
void board_permit(bool on);
bool board_exchange(const uint8_t tx[16],uint8_t rx[16]);
bool board_rx(char *c);
bool board_tx(char c);
#endif
