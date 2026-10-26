/* Minimal GNU/Clang startup, with unused interrupt vectors routed to shutdown. */
#include <stdint.h>
#include "board.h"
extern uint32_t _estack,_sidata,_sdata,_edata,_sbss,_ebss;
extern int main(void);
extern void SysTick_Handler(void);
extern void TIM6_DAC_IRQHandler(void);
extern void DMA1_Channel2_IRQHandler(void);
void SystemInit(void) {} /* clocks are configured by board_init */
uint32_t SystemCoreClock=4000000;
void Default_Handler(void) {
    __asm__ volatile("cpsid i" ::: "memory");
    board_permit(false); /* stop timer/DMA work too; FPGA watchdog remains independent */
    for (;;) {}
}
void Reset_Handler(void) {
    uint32_t *s=&_sidata;
    for(uint32_t *d=&_sdata;d<&_edata;) *d++=*s++;
    for(uint32_t *d=&_sbss;d<&_ebss;) *d++=0;
    (void)main(); Default_Handler();
}
typedef void (*handler_t)(void);
__attribute__((section(".isr_vector"),used))
handler_t const vectors[112] = {
    [0]=(handler_t)&_estack,[1]=Reset_Handler,
    [2 ... 14]=Default_Handler,[15]=SysTick_Handler,
    [16 ... 27]=Default_Handler,[28]=DMA1_Channel2_IRQHandler,
    [29 ... 69]=Default_Handler,[70]=TIM6_DAC_IRQHandler,[71 ... 111]=Default_Handler
};
