// Standalone STM32L432KC main for the E155 carrier's SW7 SPI connections.
// 16-bit SPI, Mode 0, MSB first, 125 kHz.
// FPGA must send bits 15 through 0 during each CS-low transaction.
// Keep the normal CMSIS headers, startup, linker and system files.

#include <stdint.h>
#include "stm32l432xx.h"

#ifndef PRINT_TO_SEGGER
#define PRINT_TO_SEGGER 1 // Set to 0 for Watch-only operation.
#endif

#if PRINT_TO_SEGGER
#include <stdio.h>
#endif

volatile uint16_t fpga_word = 0;
volatile uint32_t read_count = 0;
#define AVERAGE_WINDOW 10u
#define MAX_SAMPLE_DELTA 1000u  // Maximum change between accepted readings.
//#define MAX_VALID_READING 3900u

volatile uint16_t fpga_average = 0;
volatile uint32_t rejected_count = 0;

static uint16_t samples[AVERAGE_WINDOW];
static uint32_t sample_sum = 0;
static unsigned sample_count = 0;
static unsigned next_sample = 0;
static uint16_t previous_sample = 0;

static void update_average(uint16_t reading) {
    //if (reading > MAX_VALID_READING) {
    //    ++rejected_count;
    //    return;
    //}

    if (sample_count > 0u) {
        uint32_t delta = (reading >= previous_sample)
            ? (uint32_t)reading - previous_sample
            : (uint32_t)previous_sample - reading;

        if (delta > MAX_SAMPLE_DELTA) {
            ++rejected_count;
            return;
        }
    }

    if (sample_count == AVERAGE_WINDOW) {
        sample_sum -= samples[next_sample];
    } else {
        ++sample_count;
    }

    samples[next_sample] = reading;
    sample_sum += reading;
    next_sample = (next_sample + 1u) % AVERAGE_WINDOW;
    previous_sample = reading;

    // Round to the nearest integer ADC count.
    fpga_average = (float)((sample_sum + sample_count / 2u) / sample_count);
}

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

    // PA11 = manual CS, initially high.
    GPIOA->BSRR = 1u << 11;
    GPIOA->OTYPER &= ~(1u << 11);
    GPIOA->MODER = (GPIOA->MODER & ~(3u << 22)) | (1u << 22);
    GPIOA->PUPDR = (GPIOA->PUPDR & ~(3u << 22)) | (1u << 22);

    // PB3 = SCK, PB4 = MISO, PB5 = MOSI; SPI1 AF5.
    for (unsigned p = 3; p <= 5; ++p) {
        GPIOB->MODER =
            (GPIOB->MODER & ~(3u << (2*p))) | (2u << (2*p));

        GPIOB->AFR[0] =
            (GPIOB->AFR[0] & ~(15u << (4*p))) | (5u << (4*p));

        GPIOB->OTYPER &= ~(1u << p);
        GPIOB->OSPEEDR |= 3u << (2*p);
        GPIOB->PUPDR &= ~(3u << (2*p));
    }

    GPIOB->PUPDR |= 1u << 8; // Weak pull-up on PB4/MISO.

    RCC->APB2ENR |= RCC_APB2ENR_SPI1EN;
    (void)RCC->APB2ENR;

    RCC->APB2RSTR |= RCC_APB2RSTR_SPI1RST;
    RCC->APB2RSTR &= ~RCC_APB2RSTR_SPI1RST;

    // Master, software CS, Mode 0, MSB first.
    // SPI clock = 16 MHz / 128 = 125 kHz.
    SPI1->CR1 = SPI_CR1_MSTR | SPI_CR1_SSM | SPI_CR1_SSI |
                (6u << SPI_CR1_BR_Pos);

    // DS = 15: 16-bit frames.
    // FRXTH = 0: 16-bit receive FIFO threshold.
    SPI1->CR2 = (15u << SPI_CR2_DS_Pos);

    // To use LSB first instead, uncomment this before enabling SPI:
    // SPI1->CR1 |= SPI_CR1_LSBFIRST;

    SPI1->CR1 |= SPI_CR1_SPE;

    // Polled 1 ms timer; no SysTick interrupt.
    SysTick->LOAD = 16000u - 1u;
    SysTick->VAL = 0;
    SysTick->CTRL =
        SysTick_CTRL_CLKSOURCE_Msk | SysTick_CTRL_ENABLE_Msk;
}

static uint16_t read_fpga_word(void) {
    GPIOA->BSRR = 1u << (11 + 16); // CS low.

    for (volatile unsigned n = 0; n < 100; ++n) {
        __NOP();
    }

    while (!(SPI1->SR & SPI_SR_TXE)) {}

    // Dummy TX generates 16 clocks while receiving the FPGA word.
    *(volatile uint16_t *)&SPI1->DR = 0x0000u;

    while (!(SPI1->SR & SPI_SR_RXNE)) {}
    uint16_t received = *(volatile uint16_t *)&SPI1->DR;

    while (SPI1->SR & SPI_SR_BSY) {}

    for (volatile unsigned n = 0; n < 100; ++n) {
        __NOP();
    }

    GPIOA->BSRR = 1u << 11; // CS high; resets FPGA bit index.

    return received;
}

int main(void) {
    init_spi();

    for (;;) {
       int16_t reading = read_fpga_word();
        fpga_word = reading;
        uint16_t pos = (reading*100)/25;
        uint16_t pos_cm = pos/1000U;
        uint16_t pos_mm = pos%1000U;
        ++read_count;
        update_average(pos);

#if PRINT_TO_SEGGER
        printf("Raw = %d, Pos = %u.%ucm, average = %u\n",
               reading,
               (unsigned)pos_cm,
               (unsigned)pos_mm,
               (unsigned)fpga_average
              );
        fflush(stdout);
#endif

        delay_ms(25);
    }
}
