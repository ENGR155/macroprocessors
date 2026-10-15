/* STM32L432KC, CMSIS register driver. No lab libraries are modified.
 * Explicit jumper wiring is in docs/hardware.md. Leave all MCU/FPGA bridge
 * switches OPEN; these pins intentionally avoid PB3's onboard LED. */
#include "board.h"
#include "stm32l432xx.h"
static volatile uint32_t milliseconds;
static void mode(unsigned p,unsigned m) {
    GPIOA->MODER=(GPIOA->MODER&~(3u<<(2*p)))|(m<<(2*p));
}
static void af(unsigned p,unsigned a) {
    mode(p,2); unsigned i=p/8,shift=4*(p%8);
    GPIOA->AFR[i]=(GPIOA->AFR[i]&~(15u<<shift))|(a<<shift);
    GPIOA->OSPEEDR|=3u<<(2*p);
}
void SysTick_Handler(void) { milliseconds++; }
uint32_t board_ms(void) { return milliseconds; }
uint32_t board_us(void) { return TIM2->CNT; }
void board_permit(bool on) { GPIOA->BSRR=on?1u:1u<<16; }
void board_init(void) {
    RCC->AHB2ENR|=RCC_AHB2ENR_GPIOAEN; (void)RCC->AHB2ENR;
    GPIOA->BSRR=(1u<<16)|(1u<<4); /* PA0 low, CS high before output mode */
    mode(0,1); mode(4,1);
    GPIOA->PUPDR=(GPIOA->PUPDR&~3u)|2u; /* PA0 pulldown, plus external 10k */
    RCC->CR|=RCC_CR_HSION;
    while (!(RCC->CR&RCC_CR_HSIRDY)) {}
    RCC->CFGR=(RCC->CFGR&~RCC_CFGR_SW)|RCC_CFGR_SW_HSI;
    while ((RCC->CFGR&RCC_CFGR_SWS)!=RCC_CFGR_SWS_HSI) {}
    RCC->CFGR&=~(RCC_CFGR_HPRE|RCC_CFGR_PPRE1|RCC_CFGR_PPRE2);
    SystemCoreClock=16000000;
    /* Enable hardware float before any control arithmetic. */
    SCB->CPACR|=(0xfu<<20); __DSB(); __ISB();
    RCC->APB1ENR1|=RCC_APB1ENR1_TIM2EN; (void)RCC->APB1ENR1;
    TIM2->PSC=15; TIM2->ARR=0xffffffff; TIM2->EGR=TIM_EGR_UG; TIM2->CR1=TIM_CR1_CEN;
    af(5,5); af(6,5); af(7,5); /* SPI1 SCK/MISO/MOSI */
    RCC->APB2ENR|=RCC_APB2ENR_SPI1EN|RCC_APB2ENR_USART1EN; (void)RCC->APB2ENR;
    /* 16 MHz / 16 = 1 MHz, mode 0, MSB first, software CS, 8-bit FIFO. */
    SPI1->CR1=SPI_CR1_MSTR|SPI_CR1_SSM|SPI_CR1_SSI|(3u<<SPI_CR1_BR_Pos);
    SPI1->CR2=(7u<<SPI_CR2_DS_Pos)|SPI_CR2_FRXTH;
    SPI1->CR1|=SPI_CR1_SPE;
    af(9,7); af(10,7); /* USART1 to the course ESP8266 */
    RCC->CCIPR=(RCC->CCIPR&~RCC_CCIPR_USART1SEL)|(2u<<RCC_CCIPR_USART1SEL_Pos);
    USART1->CR1=0; USART1->CR2=0; USART1->CR3=0; USART1->BRR=128;
    USART1->CR1=USART_CR1_UE|USART_CR1_TE|USART_CR1_RE; /* 125000 baud 8N1 */
    SysTick_Config(16000);
}
static bool wait_spi(uint32_t mask,uint32_t start) {
    while (!(SPI1->SR&mask)) if ((uint32_t)(board_us()-start)>300) return false;
    return true;
}
bool board_exchange(const uint8_t tx[16],uint8_t rx[16]) {
    uint32_t start=board_us();
    GPIOA->BSRR=1u<<(4+16);
    while ((uint32_t)(board_us()-start)<2) {}
    bool ok=true;
    for (unsigned i=0;i<16;i++) {
        if (!wait_spi(SPI_SR_TXE,start)) { ok=false; break; }
        *(volatile uint8_t *)&SPI1->DR=tx[i];
        if (!wait_spi(SPI_SR_RXNE,start)) { ok=false; break; }
        rx[i]=*(volatile uint8_t *)&SPI1->DR;
    }
    while (SPI1->SR&SPI_SR_BSY) {
        if ((uint32_t)(board_us()-start)>300) { ok=false; break; }
    }
    uint32_t end=board_us();
    while ((uint32_t)(board_us()-end)<2) {}
    GPIOA->BSRR=1u<<4;
    if (!ok) board_permit(false);
    return ok;
}
bool board_rx(char *c) {
    if (USART1->ISR&(USART_ISR_ORE|USART_ISR_FE|USART_ISR_NE)) {
        USART1->ICR=USART_ICR_ORECF|USART_ICR_FECF|USART_ICR_NCF;
        /* Corrupt the current line so it cannot execute a command. */
        *c='!'; if (USART1->ISR&USART_ISR_RXNE) (void)USART1->RDR; return true;
    }
    if (!(USART1->ISR&USART_ISR_RXNE)) return false;
    *c=(char)USART1->RDR; return true;
}
bool board_tx(char c) {
    if (!(USART1->ISR&USART_ISR_TXE)) return false;
    USART1->TDR=(uint8_t)c; return true;
}
