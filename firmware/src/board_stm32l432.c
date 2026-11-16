/* STM32L432KC, CMSIS register driver. No lab libraries are modified.
 * Explicit jumper wiring is in docs/hardware.md. Leave all MCU/FPGA bridge
 * switches OPEN; these pins intentionally avoid PB3's onboard LED. */
#include "board.h"
#include "stm32l432xx.h"
static volatile uint32_t milliseconds;
static board_adc_callback_t adc_callback;
static board_reply_callback_t reply_callback;
static unsigned adc_channels;
static volatile unsigned phase;
static bool sampling_failed;
static uint32_t scan_started;
static lev_adc_t scan;
static uint8_t dma_tx[LEV_FRAME_BYTES];
static volatile uint8_t dma_rx[LEV_FRAME_BYTES];
uint32_t board_lock(void) { uint32_t p=__get_PRIMASK(); __disable_irq(); return p; }
void board_unlock(uint32_t p) { __set_PRIMASK(p); }
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
    GPIOA->BSRR=(1u<<16)|(1u<<4)|(1u<<1); /* permit low, both CS high */
    mode(0,1); mode(4,1); mode(1,1); /* PA1: ADC CS; PA4: FPGA CS */
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
static void delay_us(uint32_t us) {
    uint32_t start=board_us(); while ((uint32_t)(board_us()-start)<us) {}
}
static void dma_stop(void) {
    SPI1->CR2&=~(SPI_CR2_RXDMAEN|SPI_CR2_TXDMAEN);
    DMA1_Channel2->CCR=0; DMA1_Channel3->CCR=0;
    DMA1->IFCR=DMA_IFCR_CGIF2|DMA_IFCR_CGIF3;
}
static void sampling_fault(void) {
    sampling_failed=true; board_permit(false); dma_stop();
    GPIOA->BSRR=(1u<<1)|(1u<<4); phase=0;
    const uint8_t invalid_reply[LEV_FRAME_BYTES]={0};
    reply_callback(invalid_reply,false);
}
static void dma_start(unsigned n,unsigned cs_pin,unsigned lead_us) {
    GPIOA->BSRR=1u<<(cs_pin+16); delay_us(lead_us);
    DMA1_Channel2->CPAR=(uint32_t)&SPI1->DR;
    DMA1_Channel3->CPAR=(uint32_t)&SPI1->DR;
    DMA1_Channel2->CMAR=(uint32_t)dma_rx; DMA1_Channel3->CMAR=(uint32_t)dma_tx;
    DMA1_Channel2->CNDTR=n; DMA1_Channel3->CNDTR=n;
    __DMB(); /* publish the TX bytes before DMA can fetch them */
    /* SPI1 RX: DMA1 channel 2/request 1; TX: channel 3/request 1. */
    DMA1_Channel2->CCR=DMA_CCR_MINC|DMA_CCR_TCIE|DMA_CCR_TEIE|DMA_CCR_PL_1|DMA_CCR_EN;
    DMA1_Channel3->CCR=DMA_CCR_MINC|DMA_CCR_DIR|DMA_CCR_PL_1|DMA_CCR_EN;
    SPI1->CR2|=SPI_CR2_RXDMAEN|SPI_CR2_TXDMAEN;
}
static void adc_start(unsigned channel) {
    dma_tx[0]=(uint8_t)(0x06u|(channel>>2));
    dma_tx[1]=(uint8_t)(channel<<6); dma_tx[2]=0;
    dma_start(3,1,1);
}
void TIM6_DAC_IRQHandler(void) {
    TIM6->SR=0;
    if (sampling_failed) return;
    if (phase) { sampling_fault(); return; } /* previous scan exceeded 200 us */
    if (TIM6->CNT>20) { sampling_fault(); return; } /* delayed timer service */
    scan_started=board_us(); phase=1; adc_start(0);
}
void DMA1_Channel2_IRQHandler(void) {
    uint32_t flags=DMA1->ISR;
    if (flags&(DMA_ISR_TEIF2|DMA_ISR_TEIF3)) { sampling_fault(); return; }
    if (!(flags&DMA_ISR_TCIF2) || !phase) return;
    __DMB(); /* RX bytes were written by DMA, not the C abstract machine */
    uint32_t start=board_us();
    while (SPI1->SR&SPI_SR_BSY) {
        if ((uint32_t)(board_us()-start)>5) { sampling_fault(); return; }
    }
    dma_stop();
    if (phase<=adc_channels) {
        GPIOA->BSRR=1u<<1; delay_us(1);
        uint16_t value=(uint16_t)(((dma_rx[1]&15u)<<8)|dma_rx[2]);
        if (phase==1) scan.current=value;
        else if (phase==2) scan.hall1=value;
        else scan.hall2=value;
        if (phase<adc_channels) { adc_start(phase++); return; }
        adc_callback(&scan,scan_started,dma_tx); phase=adc_channels+1;
        dma_start(LEV_FRAME_BYTES,4,2);
    } else {
        if ((uint32_t)(board_us()-scan_started)>=LEV_SAMPLE_US-2) { sampling_fault(); return; }
        delay_us(2); GPIOA->BSRR=1u<<4;
        uint8_t reply[LEV_FRAME_BYTES];
        for (unsigned i=0;i<LEV_FRAME_BYTES;i++) reply[i]=dma_rx[i];
        reply_callback(reply,true);
        if ((uint32_t)(board_us()-scan_started)>=LEV_SAMPLE_US) { sampling_fault(); return; }
        phase=0;
    }
}
void board_start_sampling(unsigned hall_sensors,board_adc_callback_t adc,board_reply_callback_t reply) {
    adc_callback=adc; reply_callback=reply;
    if (hall_sensors!=1 && hall_sensors!=2) { board_permit(false); return; }
    adc_channels=hall_sensors+1;
    RCC->AHB1ENR|=RCC_AHB1ENR_DMA1EN;
    RCC->APB1ENR1|=RCC_APB1ENR1_TIM6EN; (void)RCC->APB1ENR1;
    DMA1_CSELR->CSELR=(DMA1_CSELR->CSELR&~(DMA_CSELR_C2S|DMA_CSELR_C3S))|
                      (1u<<DMA_CSELR_C2S_Pos)|(1u<<DMA_CSELR_C3S_Pos);
    NVIC_SetPriority(DMA1_Channel2_IRQn,0); NVIC_EnableIRQ(DMA1_Channel2_IRQn);
    NVIC_SetPriority(TIM6_DAC_IRQn,1); NVIC_EnableIRQ(TIM6_DAC_IRQn);
    TIM6->PSC=15; TIM6->ARR=LEV_SAMPLE_US-1; TIM6->EGR=TIM_EGR_UG;
    TIM6->SR=0; TIM6->DIER=TIM_DIER_UIE; TIM6->CR1=TIM_CR1_CEN;
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
