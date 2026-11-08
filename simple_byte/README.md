# One byte from the FPGA to SEGGER

The FPGA supplies **0xA5**. The MCU reads one byte about twice a second and prints:

```text
FPGA byte = 0xA5 (165)
FPGA byte = 0xA5 (165)
```

The received value also lives in the global variable **fpga_byte**, which you can inspect in SEGGER Embedded Studio's Watch window.

This is the complete standalone test: one FPGA sender and one MCU main. It replaces the earlier multi-byte test while you run this experiment. No ADC, Hall sensor, DMA, interrupt handler, UART, FPGA oscillator, or levitation code is needed. Keep the electromagnet disconnected.

**SPI still needs a master:** the FPGA cannot send a byte spontaneously. The MCU pulls CS low and transmits a dummy byte to generate eight clock pulses; the FPGA simultaneously presents its byte on MISO. The dummy byte is discarded. This checks MCU-to-FPGA CS/clock and FPGA-to-MCU data. It does not test MOSI reception by the FPGA.

## 1. Carrier switches and pins

For the [E155 development-board schematic, Rev v4](https://hmc-e155.github.io/assets/doc/E155%20Development%20Board%20Schematic.pdf), set **SW7 positions 5, 7, and 8 ON; all other SW7 positions OFF**. SW7-6/MOSI may also remain ON if already set, but this FPGA test does not use it. Leave SW6 OFF. Remove previous SPI jumper wires. The carrier supplies these connections:

| Signal | MCU pin | SW7 position | FPGA package site |
|---|---|---:|---:|
| CS, active low | PA11 / D10 | 5 | 20 |
| MISO: FPGA to MCU | PB4 / D12 | 7 | 12 |
| SCK: MCU to FPGA | PB3 / D13 | 8 | 21 |

These are switch positions and FPGA package sites, not header contact numbers. No extra SPI jumper wires are needed. Both modules share ground through the carrier. With each module USB-powered separately, leave carrier power jumpers **J3 and J4 open** and leave external VIN unpowered, as in the previous guide. Match your physical board revision and orientation to the schematic.

## 2. FPGA: paste this entire file

Create a SystemVerilog source named **spi_byte.sv**, paste the following, and select **spi_byte_top** as the top-level module. Target the course UPduino's **iCE40UP5K, SG48**. Do not include the old SPI test or application top in this build.

```systemverilog
// SPI mode 0, MSB first. Keep byte_in stable while cs_n is low.
// One CS-low interval = exactly one byte. No FPGA oscillator is needed.
module spi_byte_tx (
    input  wire       sck,
    input  wire       cs_n,
    input  wire [7:0] byte_in,
    output wire       miso
);
    reg [2:0] bit_index = 3'd0; // Supported power-up initialization on UP5K.

    // Master samples on rising SCK; advance data on falling SCK.
    always @(negedge sck or posedge cs_n) begin
        if (cs_n) bit_index <= 3'd0;
        else      bit_index <= bit_index + 3'd1;
    end

    assign miso = cs_n ? 1'bz : byte_in[3'd7 - bit_index];
endmodule

module spi_byte_top (
    input  wire sck,
    input  wire cs_n,
    output wire miso
);
    spi_byte_tx sender (
        .sck(sck), .cs_n(cs_n), .byte_in(8'hA5), .miso(miso)
    );
endmodule
```

In Radiant's pin editor, assign **sck = site 21**, **cs_n = site 20**, and **miso = site 12**, with **LVCMOS33**. No oscillator primitive or RADIANT define is needed. Constrain the input SCK to **125 kHz**, an **8000 ns period**, for this test; this is an externally supplied clock. Build and program the FPGA using your usual course procedure.

For the open-source flow, the supplied **spi_byte.pcf** contains:

```text
set_io sck 21
set_io cs_n 20
set_io miso 12
```

The reusable module's eight-bit input is **byte_in**. The top connects it to the test constant with **.byte_in(8'hA5)**. Later, replace that constant with your FPGA signal, keeping all eight bits stable from before CS falls until after CS rises. This tiny sender does not synchronize or snapshot a changing multi-bit value; add a coherent handoff before connecting a live measurement from another clock domain.

The master samples MISO on rising SCK edges. The sender advances to the next bit on falling SCK edges. CS high resets the bit index and releases MISO. Use exactly **one byte per CS-low interval**.

## 3. MCU: paste this as your only main

Use a separate STM32L432KC project or a copy of your working SEGGER lab project. Keep the normal STM32/CMSIS headers, startup/vector file, system file, linker settings, and debug connection. Add **main.c** below as the only application file containing main(). Do not call the old initSPI(), clock initializer, or SysTick initializer in addition to this code.

The required device header is **stm32l432xx.h**, with CMSIS core headers on the include path. The code uses the actual **SPI1 hardware peripheral**, mode 0, eight bits, MSB first, at **125 kHz**. PB3/PB4/PB5 use AF5, as listed in the [STM32L432KC datasheet](https://hmc-e155.github.io/assets/doc/ds11451-stm32l432kc.pdf). PB5 is configured as SPI MOSI but does not need to be connected for this receive-only experiment.

```c
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
```

## 4. See the printed byte in SEGGER

For a project using the **SEGGER Runtime Library**:

1. Open **Project > Edit Options** and select the configuration you are building. Under **Library > Library I/O**, choose **SEMIHOST** for this simple debug-connected test. Use the SEGGER runtime's standard I/O rather than a previous UART printf retarget. The exact option layout can vary by version.
2. Build in **Debug** with debug symbols and no/low optimization. Program the FPGA first, then download and start debugging the MCU using your existing working connection.
3. Open **View > Debug Terminal** and run/resume the MCU.
4. Expect **FPGA byte = 0xA5 (165)** about twice a second. Read count starts increasing before the print call.

[SEGGER's Library I/O documentation](https://kb.segger.com/Embedded_Studio_Library_IO) describes the SEMIHOST setting and the alternative RTT backend. Semihosting briefly halts the MCU to print through the debugger, which is acceptable for this isolated test. Run this printing configuration with the debugger attached; it is not a final control-loop logging design. If your working project already uses RTT with a compatible J-Link connection, you can keep that backend instead and use the same printf calls. Do not select **SWO**: it would compete for **PB3**, which this test uses as SCK.

No UART baud rate or serial COM terminal is involved in this setup. The MCU receives the byte through SPI and then separately prints it through the debug connection. See the course's [tutorials page](https://hmc-e155.github.io/tutorials/) for its MCU printf debugging tutorial.

## 5. See the variable directly, even without printf

1. Open **View > Watch > Watch 1**.
2. Add **fpga_byte** and **read_count**.
3. Set a breakpoint on **delay_ms(500);** in main, after the assignment, count increment, and print. Run to it. Set fpga_byte's display format to **hexadecimal**; expect **0xA5** (or decimal **165**).
4. Resume to reach the breakpoint again. The byte remains A5 and read_count increases by one. An ordinary Watch window refreshes on pause/step; do not assume it refreshes continuously while running. See [SEGGER's Watch instructions](https://studio.segger.com/ide_watch_window.htm).

If printf does not work, set **PRINT_TO_SEGGER to 0**, rebuild, and use the same breakpoint/Watch steps. This removes printf and fflush completely. The byte assignment and SPI transfer still run; you can then resolve terminal configuration separately.

## 6. Prove that the displayed value comes from the FPGA

Change **.byte_in(8'hA5)** to **.byte_in(8'h3B)** in spi_byte_top. Rebuild and reprogram **only the FPGA**, then reset/run the MCU. The output must become:

```text
FPGA byte = 0x3B (59)
```

This second pattern also helps expose reversed bit order. If A5 stays on screen, make sure you resumed the MCU, programmed the new FPGA build, and are looking at new output rather than old terminal lines.

| Observation | First thing to check |
|---|---|
| A5/165, then 3B/59 after changing the FPGA | Expected result; this verifies this simple SPI read path. |
| FF/255 every read | Unconfigured/unpowered FPGA, open SW7-7, wrong MISO pin, or CS not reaching FPGA. MCU's weak MISO pull-up makes an undriven input tend toward FF. |
| 00 every read | Wrong FPGA bitstream, MISO held low, wrong pin mapping, or an actual zero byte at the module input. |
| Wrong or shifting bits | Mode 0, MSB first, site assignments, stable byte_in, and one CS pulse per byte. |
| Correct Watch value, no terminal text | SPI reception works; inspect Library I/O, printf retargets, debugger connection, and Debug Terminal. |
| read_count becomes 1 and stops at printf | Debug output is blocking or its backend is not serviced. Try PRINT_TO_SEGGER=0. |
| read_count never increases | Pause the MCU and see whether startup, initialization, or a SPI status wait is where it stopped. |

## Verification performed

The sender passed HDL simulation for **all 256 byte values**, MISO release when deselected, and restarting after an aborted partial byte, at 125 kHz. The FPGA top synthesized and placed/routed for UP5K-SG48 using these pins (8 logic cells). The MCU source compiled for Cortex-M4 with warnings treated as errors in **Watch-only mode**. The SEGGER printf backend and full MCU project link were not exercised here. **Physical board operation still needs your bench test.**

Supporting files: [MCU main](main.c), [FPGA source](spi_byte.sv), [open-source pin constraints](spi_byte.pcf), and [simulation testbench](tb_spi_byte.sv). No existing application source or proposal was changed.
