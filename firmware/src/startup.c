/* Minimal GNU/Clang startup, with unused interrupt vectors routed to shutdown. */
#include <stdint.h>
extern uint32_t _estack,_sidata,_sdata,_edata,_sbss,_ebss;
extern int main(void);
extern void SysTick_Handler(void);
void SystemInit(void) {} /* clocks are configured by board_init */
uint32_t SystemCoreClock=4000000;
void Default_Handler(void) { for (;;) {} } /* FPGA watchdog removes drive within 20 ms */
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
    [2 ... 14]=Default_Handler,[15]=SysTick_Handler,[16 ... 111]=Default_Handler
};
