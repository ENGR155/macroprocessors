/* MicroPEs STM32L432KC application.
 * Reads the FPGA's 16-bit position over SPI1 and serves telemetry to the
 * ESP8266 over USART1. The ESP8266 hosts the HTTP server and dashboard.
 */
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#ifndef MAGLEV_MONITOR_TEST
#include "stm32l432xx.h"
#endif

/* How often the STM32 reads the FPGA. The ADC runs on the FPGA's own clock. */
#define MAGLEV_SAMPLE_PERIOD_MS 25u
/* Provisional display calibration from the bench calculation, 0.04 mm/word. */
#define MAGLEV_POSITION_UM_PER_WORD 40
#define MAGLEV_POSITION_OFFSET_UM 0
#define MAGLEV_POSITION_CALIBRATED 0
#ifndef PRINT_TO_SEGGER
#define PRINT_TO_SEGGER 0    /* Set to 1 for optional RTT debug output. */
#endif

#define AVERAGE_WINDOW 10u
#define MAX_SAMPLE_DELTA 1000u

/* Debugger/JS Scope variables. The average retains the bench code's 10 um units. */
volatile uint16_t fpga_word;
volatile uint32_t fpga_average, read_count, rejected_count, spi_failures;
static uint32_t samples[AVERAGE_WINDOW];
static uint32_t sample_sum, previous_sample;
static unsigned sample_count, next_sample;

static void update_average(uint16_t word) {
    uint32_t reading = (uint32_t)word * 4u;
    if (sample_count) {
        uint32_t delta = reading >= previous_sample ? reading - previous_sample
                                                     : previous_sample - reading;
        if (delta > MAX_SAMPLE_DELTA) {
            rejected_count++;
            return;
        }
    }

    if (sample_count == AVERAGE_WINDOW) {
        sample_sum -= samples[next_sample];
    } else {
        sample_count++;
    }
    samples[next_sample] = reading;
    sample_sum += reading;
    next_sample = (next_sample + 1u) % AVERAGE_WINDOW;
    previous_sample = reading;
    fpga_average = (sample_sum + sample_count / 2u) / sample_count;
}

/* ESP8266 UART telemetry and configuration protocol. */

/* Fixed point: 1234 means gain 1.234. Units must match the actual controller. */
typedef struct { uint32_t kp_milli, ki_milli, kd_milli; } maglev_gains_t;
/* Called in the foreground. Return true only after all three gains are applied
 * together at a controller boundary. False leaves the published values intact. */
typedef bool (*maglev_apply_pid_fn)(void *context, const maglev_gains_t *gains);
typedef struct {
    uint32_t now_ms, sample_ms, sequence, failures, uart_errors, rejected_requests;
    uint16_t word;
    int32_t position_um;
    bool have_sample, calibrated, pid_connected;
    maglev_gains_t gains;
    uint32_t pid_revision;
    maglev_apply_pid_fn apply_pid;
    void *pid_context;
    char line[128], reply[768];
    size_t used, tx_size, tx_pos;
    bool overflow;
} maglev_monitor_t;

static void maglev_monitor_init(maglev_monitor_t *m, bool calibrated) {
    memset(m, 0, sizeof(*m));
    m->calibrated = calibrated;
}
static void record_fpga_reading(maglev_monitor_t *m, uint16_t word, uint32_t now_ms) {
    fpga_word = word;
    read_count++;
    update_average(word);

    m->word = word;
    m->position_um = (int32_t)word * MAGLEV_POSITION_UM_PER_WORD + MAGLEV_POSITION_OFFSET_UM;
    m->sample_ms = now_ms;
    m->sequence++;
    m->have_sample = true;
}
/* Call in the foreground with a coherent snapshot of the actual PID gains. */
void maglev_monitor_pid(maglev_monitor_t *m, const maglev_gains_t *actual,
                        maglev_apply_pid_fn apply, void *context) {
    bool connected = actual != NULL;
    if (connected != m->pid_connected ||
        (actual && (actual->kp_milli != m->gains.kp_milli ||
                    actual->ki_milli != m->gains.ki_milli ||
                    actual->kd_milli != m->gains.kd_milli))) m->pid_revision++;
    if (actual) m->gains = *actual;
    m->pid_connected = connected; m->apply_pid = apply; m->pid_context = context;
}
static bool maglev_monitor_tx_pending(const maglev_monitor_t *m) {
    return m->tx_pos < m->tx_size;
}

/* Strict decimal grammar, up to three fractional digits, gain 0..1000.
 * No exponents, negative values, suffixes, URL escapes, or partial updates. */
static bool parse_gain(const char **cursor, uint32_t *value) {
    const char *p = *cursor;
    uint32_t whole = 0, fraction = 0, scale = 100;
    unsigned digits = 0;
    while (*p >= '0' && *p <= '9') {
        if (++digits > 4) return false;
        whole = whole * 10u + (unsigned)(*p++ - '0');
    }
    if (!digits || whole > 1000) return false;
    if (*p == '.') {
        p++; unsigned fractional_digits = 0;
        while (*p >= '0' && *p <= '9') {
            if (++fractional_digits > 3) return false;
            fraction += (unsigned)(*p++ - '0') * scale; scale /= 10;
        }
        if (!fractional_digits) return false;
    }
    if (*p++ != ' ' || (whole == 1000 && fraction)) return false;
    *value = whole * 1000u + fraction; *cursor = p; return true;
}
static bool parse_uint32(const char **cursor, char delimiter, uint32_t *value) {
    const char *p = *cursor;
    uint32_t result = 0; unsigned digits = 0;
    while (*p >= '0' && *p <= '9') {
        uint32_t digit = (unsigned)(*p++ - '0');
        if (++digits > 10 || result > (UINT32_MAX - digit) / 10u) return false;
        result = result * 10u + digit;
    }
    if (!digits || *p != delimiter) return false;
    *value = result;
    *cursor = delimiter ? p + 1 : p;
    return true;
}
static void format_status(maglev_monitor_t *m, uint32_t id, const char *result) {
    int n = snprintf(m->reply, sizeof(m->reply),
        "@M1 %lu "
        "{\"result\":\"%s\",\"ms\":%lu,\"sample_ms\":%lu,\"seq\":%lu,"
        "\"valid\":%s,\"age_ms\":%lu,\"raw\":%u,\"position_um\":%ld,"
        "\"calibrated\":%s,\"pid_connected\":%s,\"pid_writable\":%s,"
        "\"kp_milli\":%lu,\"ki_milli\":%lu,\"kd_milli\":%lu,\"revision\":%lu,"
        "\"spi_failures\":%lu,\"uart_errors\":%lu,\"bad_requests\":%lu}\n",
        (unsigned long)id, result, (unsigned long)m->now_ms,
        (unsigned long)m->sample_ms, (unsigned long)m->sequence,
        m->have_sample ? "true" : "false",
        (unsigned long)(m->now_ms - m->sample_ms), (unsigned)m->word,
        (long)m->position_um, m->calibrated ? "true" : "false",
        m->pid_connected ? "true" : "false",
        m->pid_connected && m->apply_pid ? "true" : "false",
        (unsigned long)m->gains.kp_milli, (unsigned long)m->gains.ki_milli,
        (unsigned long)m->gains.kd_milli, (unsigned long)m->pid_revision,
        (unsigned long)m->failures, (unsigned long)m->uart_errors,
        (unsigned long)m->rejected_requests);
    m->tx_size = n >= 0 && (size_t)n < sizeof(m->reply) ? (size_t)n : 0;
    m->tx_pos = 0;
}
static void handle_uart_request(maglev_monitor_t *m) {
    const char *command = m->line + 4;
    uint32_t id;
    if (m->overflow || strncmp(m->line, "@M1 ", 4) ||
        !parse_uint32(&command, ' ', &id)) {
        if (m->used || m->overflow) m->rejected_requests++;
        return;
    }
    if (!strcmp(command, "GET")) { format_status(m, id, "ok"); return; }
    if (!strncmp(command, "PID ", 4)) {
        const char *p = command + 4; maglev_gains_t next; uint32_t rev;
        if (!parse_gain(&p, &next.kp_milli) || !parse_gain(&p, &next.ki_milli) ||
            !parse_gain(&p, &next.kd_milli) || !parse_uint32(&p, '\0', &rev)) {
            m->rejected_requests++; format_status(m, id, "invalid_gains"); return;
        }
        if (!m->pid_connected || !m->apply_pid) { format_status(m, id, "pid_unavailable"); return; }
        if (rev != m->pid_revision) { format_status(m, id, "conflict"); return; }
        if (!m->apply_pid(m->pid_context, &next)) { format_status(m, id, "controller_rejected"); return; }
        m->gains = next; m->pid_revision++; format_status(m, id, "applied"); return;
    }
    m->rejected_requests++; format_status(m, id, "unknown_command");
}
static void maglev_monitor_feed(maglev_monitor_t *m, char byte, uint32_t now_ms) {
    m->now_ms = now_ms;
    if (byte == '@') {
        if (m->used || m->overflow) m->rejected_requests++;
        m->used = 0;
        m->overflow = false;
    }
    if (byte == '\n') {
        m->line[m->used] = 0;
        /* The ESP makes one request at a time. Never overwrite an in-flight
         * response if a second client/request arrives unexpectedly. */
        if (!maglev_monitor_tx_pending(m)) handle_uart_request(m);
        else m->rejected_requests++;
        m->used = 0; m->overflow = false;
    } else {
        if (byte < 32 || byte > 126) m->overflow = true;
        if (m->used + 1 < sizeof(m->line)) m->line[m->used++] = byte;
        else m->overflow = true;
    }
}

#ifndef MAGLEV_MONITOR_TEST

/* STM32 peripheral setup and foreground scheduling. */
static maglev_monitor_t monitor;
static volatile unsigned rx_head, rx_tail;
static volatile uint32_t rx_errors, rx_dropped;
static volatile char rx_ring[256];

/* Interrupt reception buffers UART bytes while the 128 us SPI transfer runs.
 * The foreground parses commands and formats responses. */
void USART1_IRQHandler(void) {
    uint32_t flags = USART1->ISR;
    const bool error = (flags & (USART_ISR_ORE | USART_ISR_FE | USART_ISR_NE)) != 0;
    if (error) {
        USART1->ICR = USART_ICR_ORECF | USART_ICR_FECF | USART_ICR_NCF;
        rx_errors++;
    }
    if ((flags & USART_ISR_RXNE) || error) {
        char byte = flags & USART_ISR_RXNE ? (char)USART1->RDR : '\0';
        unsigned next = (rx_head + 1u) & 255u;
        if (next == rx_tail) {
            rx_errors++;
            rx_dropped++;
        } else {
            rx_ring[rx_head] = error ? '\0' : byte;
            rx_head = next;
        }
    }
}

static bool uart_receive(char *byte) {
    static uint32_t seen_dropped;
    uint32_t saved_mask = __get_PRIMASK();
    __disable_irq();
    if (seen_dropped != rx_dropped) {
        seen_dropped = rx_dropped;
        rx_tail = rx_head;
        monitor.overflow = true;
    }
    bool available = rx_tail != rx_head;
    if (available) {
        *byte = rx_ring[rx_tail];
        rx_tail = (rx_tail + 1u) & 255u;
    }
    __set_PRIMASK(saved_mask);
    return available;
}
static void spi_reset(void) {
    RCC->APB2RSTR |= RCC_APB2RSTR_SPI1RST;
    RCC->APB2RSTR &= ~RCC_APB2RSTR_SPI1RST;
    SPI1->CR1 = SPI_CR1_MSTR | SPI_CR1_SSM | SPI_CR1_SSI |
                (6u << SPI_CR1_BR_Pos); /* 16 MHz / 128 = 125 kHz */
    SPI1->CR2 = 15u << SPI_CR2_DS_Pos; /* 16-bit frame / FIFO threshold */
    SPI1->CR1 |= SPI_CR1_SPE;
}
static void board_init(void) {
    RCC->CR |= RCC_CR_HSION;
    while (!(RCC->CR & RCC_CR_HSIRDY)) {}
    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_HSI;
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_HSI) {}
    RCC->CFGR &= ~(RCC_CFGR_HPRE | RCC_CFGR_PPRE1 | RCC_CFGR_PPRE2);
    SystemCoreClock = 16000000u;
    RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN | RCC_AHB2ENR_GPIOBEN;
    RCC->APB1ENR1 |= RCC_APB1ENR1_TIM2EN;
    RCC->APB2ENR |= RCC_APB2ENR_SPI1EN | RCC_APB2ENR_USART1EN;
    (void)RCC->APB2ENR;

    /* Free-running 32-bit millisecond counter, wraps after about 49 days. */
    TIM2->CR1 = 0; TIM2->PSC = 16000u - 1u; TIM2->ARR = UINT32_MAX;
    TIM2->EGR = TIM_EGR_UG; TIM2->CNT = 0; TIM2->CR1 = TIM_CR1_CEN;
    GPIOA->BSRR = 1u << 11;
    GPIOA->OTYPER &= ~(1u << 11);
    GPIOA->MODER = (GPIOA->MODER & ~(3u << 22)) | (1u << 22);
    GPIOA->PUPDR = (GPIOA->PUPDR & ~(3u << 22)) | (1u << 22);
    for (unsigned p = 3; p <= 5; p++) {
        GPIOB->MODER = (GPIOB->MODER & ~(3u << (2*p))) | (2u << (2*p));
        GPIOB->AFR[0] = (GPIOB->AFR[0] & ~(15u << (4*p))) | (5u << (4*p));
        GPIOB->OTYPER &= ~(1u << p); GPIOB->OSPEEDR |= 3u << (2*p);
        GPIOB->PUPDR &= ~(3u << (2*p));
    }
    GPIOB->PUPDR |= 1u << 8;
    spi_reset();
    for (unsigned p = 9; p <= 10; p++) {
        GPIOA->MODER = (GPIOA->MODER & ~(3u << (2*p))) | (2u << (2*p));
        GPIOA->AFR[1] = (GPIOA->AFR[1] & ~(15u << (4*(p-8)))) | (7u << (4*(p-8)));
        GPIOA->OTYPER &= ~(1u << p);
        GPIOA->OSPEEDR |= 2u << (2*p);
        GPIOA->PUPDR &= ~(3u << (2*p));
    }
    GPIOA->PUPDR |= 1u << 20; /* RX idles high if ESP is disconnected. */
    RCC->CCIPR = (RCC->CCIPR & ~RCC_CCIPR_USART1SEL) |
                 (2u << RCC_CCIPR_USART1SEL_Pos); /* HSI16 */
    USART1->CR1 = 0; USART1->CR2 = 0; USART1->CR3 = 0;
    USART1->BRR = 128; /* 125000 baud, oversampling 16, 8N1 */
    USART1->ICR = USART_ICR_ORECF | USART_ICR_FECF | USART_ICR_NCF;
    USART1->CR1 = USART_CR1_UE | USART_CR1_TE | USART_CR1_RE | USART_CR1_RXNEIE;
    NVIC_SetPriority(USART1_IRQn, 2); NVIC_EnableIRQ(USART1_IRQn);
    __enable_irq();
}
static bool read_fpga_word(uint16_t *word) {
    uint32_t start = TIM2->CNT;
    GPIOA->BSRR = 1u << (11 + 16);
    for (volatile unsigned n = 0; n < 100; n++) __NOP();
    while (!(SPI1->SR & SPI_SR_TXE)) if ((uint32_t)(TIM2->CNT - start) >= 2) goto failed;
    *(volatile uint16_t *)&SPI1->DR = 0;
    while (!(SPI1->SR & SPI_SR_RXNE)) if ((uint32_t)(TIM2->CNT - start) >= 2) goto failed;
    *word = *(volatile uint16_t *)&SPI1->DR;
    while (SPI1->SR & SPI_SR_BSY) if ((uint32_t)(TIM2->CNT - start) >= 2) goto failed;
    for (volatile unsigned n = 0; n < 100; n++) __NOP();
    GPIOA->BSRR = 1u << 11; return true;
failed:
    GPIOA->BSRR = 1u << 11; spi_reset(); return false;
}
int main(void) {
    maglev_monitor_init(&monitor, MAGLEV_POSITION_CALIBRATED != 0);
    board_init();
    uint32_t last_sample = TIM2->CNT - MAGLEV_SAMPLE_PERIOD_MS;
#if PRINT_TO_SEGGER
    uint32_t last_print = TIM2->CNT;
#endif
    for (;;) {
        /* No inter-sample delay: service USART1 on every pass through the loop. */
        uint32_t now = TIM2->CNT;
        if ((uint32_t)(now - last_sample) >= MAGLEV_SAMPLE_PERIOD_MS) {
            last_sample = now;
            uint16_t word;
            if (read_fpga_word(&word)) {
                record_fpga_reading(&monitor, word, TIM2->CNT);
            } else {
                spi_failures++;
                monitor.failures = spi_failures;
            }
        }
        /* Add maglev_monitor_pid() here once a real controller exists.
         * See README.md for readback and atomic-apply integration. */
        monitor.uart_errors = rx_errors;
        char byte;
        for (unsigned budget = 0; budget < 16 && uart_receive(&byte); budget++) {
            maglev_monitor_feed(&monitor, byte, TIM2->CNT);
        }
        if (maglev_monitor_tx_pending(&monitor) && (USART1->ISR & USART_ISR_TXE)) {
            USART1->TDR = (uint8_t)monitor.reply[monitor.tx_pos++];
        }
#if PRINT_TO_SEGGER
        if (!maglev_monitor_tx_pending(&monitor) && (uint32_t)(now - last_print) >= 250u) {
            last_print = now;
            printf("Raw = %u, Position = %ld um, average = %lu (10 um units)\n",
                   (unsigned)fpga_word, (long)monitor.position_um, (unsigned long)fpga_average);
        }
#endif
    }
}

#endif
