// Standalone STM32L432KC main for the E155 carrier's SW7 SPI connections.
// Keep the normal CMSIS headers, startup, linker and system files.
#include <stdint.h>
#include "stm32l432xx.h"

#ifndef PRINT_TO_SEGGER
#define PRINT_TO_SEGGER 1 // Set to 0 for Watch-only operation.
#endif
#if PRINT_TO_SEGGER
#include <stdio.h>
#endif

volatile uint8_t fpga_byte = 0;
volatile uint32_t read_count = 0;

static void delay_ms(unsigned ms) {
    while (ms--) {
        SysTick->VAL = 0;
        while (!(SysTick->CTRL & SysTick_CTRL_COUNTFLAG_Msk)) {}
    }
}

static void init_spi(void) {
    // HSI16 -> system/APB clocks: 16 MHz.
    RCC->CR |= RCC_CR_HSION;
    while (!(RCC->CR & RCC_CR_HSIRDY)) {}
    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_HSI;
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_HSI) {}
    RCC->CFGR &= ~(RCC_CFGR_HPRE | RCC_CFGR_PPRE1 | RCC_CFGR_PPRE2);
    SystemCoreClock = 16000000u;

    RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN | RCC_AHB2ENR_GPIOBEN;
    (void)RCC->AHB2ENR;

    // PA11 = manual CS, initially high. PB3/4/5 = SPI1 AF5.
    GPIOA->BSRR = 1u << 11;
    GPIOA->OTYPER &= ~(1u << 11);
    GPIOA->MODER = (GPIOA->MODER & ~(3u << 22)) | (1u << 22);
    GPIOA->PUPDR = (GPIOA->PUPDR & ~(3u << 22)) | (1u << 22);
    for (unsigned p = 3; p <= 5; ++p) {
        GPIOB->MODER = (GPIOB->MODER & ~(3u << (2*p))) | (2u << (2*p));
        GPIOB->AFR[0] = (GPIOB->AFR[0] & ~(15u << (4*p))) | (5u << (4*p));
        GPIOB->OTYPER &= ~(1u << p);
        GPIOB->OSPEEDR |= 3u << (2*p);
        GPIOB->PUPDR &= ~(3u << (2*p));
    }
    GPIOB->PUPDR |= 1u << 8; // Weak pull-up on PB4/MISO.

    RCC->APB2ENR |= RCC_APB2ENR_SPI1EN;
    (void)RCC->APB2ENR;
    RCC->APB2RSTR |= RCC_APB2RSTR_SPI1RST;
    RCC->APB2RSTR &= ~RCC_APB2RSTR_SPI1RST;
    SPI1->CR1 = SPI_CR1_MSTR | SPI_CR1_SSM | SPI_CR1_SSI |
                (6u << SPI_CR1_BR_Pos); // Mode 0, MSB first, 125 kHz.
    SPI1->CR2 = (7u << SPI_CR2_DS_Pos) | SPI_CR2_FRXTH; // 8-bit frames.
    SPI1->CR1 |= SPI_CR1_SPE;

    // Polled 1 ms timer; no SysTick interrupt.
    SysTick->LOAD = 16000u - 1u;
    SysTick->VAL = 0;
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk | SysTick_CTRL_ENABLE_Msk;
}

static uint8_t read_fpga_byte(void) {
    GPIOA->BSRR = 1u << (11 + 16); // CS low.
    for (volatile unsigned n = 0; n < 100; ++n) { __NOP(); }
    while (!(SPI1->SR & SPI_SR_TXE)) {}
    *(volatile uint8_t *)&SPI1->DR = 0x00; // Dummy TX generates eight clocks.
    while (!(SPI1->SR & SPI_SR_RXNE)) {}
    uint8_t received = *(volatile uint8_t *)&SPI1->DR;
    while (SPI1->SR & SPI_SR_BSY) {}
    for (volatile unsigned n = 0; n < 100; ++n) { __NOP(); }
    GPIOA->BSRR = 1u << 11; // CS high; resets FPGA bit index.
    return received;
}

int main(void) {
    init_spi();
    for (;;) {
        fpga_byte = read_fpga_byte();
        ++read_count;
#if PRINT_TO_SEGGER
        printf("FPGA byte = 0x%02X (%u)\n", (unsigned)fpga_byte,
               (unsigned)fpga_byte);
        fflush(stdout);
#endif
        delay_ms(500); // Put a breakpoint here to inspect fpga_byte.
    }
}
