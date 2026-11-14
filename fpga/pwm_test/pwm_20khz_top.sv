`timescale 1ns/1ps
// Standalone resistor-load bench test; automatically starts after configuration.
// Do not connect the electromagnet or the installed power stage for this test.
// Hardware build: add this file; top = pwm_20khz_top; iCE40UP5K-SG48.
// Use a _top name so tools do not mistake this wrapper for a testbench.
// Assign pwm to package pad 36, LVCMOS33 (board GPIO 36, NOT header position 36).
// For Yosys, define YOSYS to select its oscillator primitive.
module pwm_20khz_top #(
    parameter integer HIGH_TICKS = 600 // 300=25%, 600=50%, 900=75%
) (
    output wire pwm
);
    wire clk;
`ifdef YOSYS
    SB_HFOSC #(.CLKHF_DIV("0b01")) osc (
`else
    HSOSC #(.CLKHF_DIV(2'b01)) osc (
`endif
        .CLKHFPU(1'b1), .CLKHFEN(1'b1), .CLKHF(clk)
    );

    // iCE40 configuration initializes registers. Hold output low for 4096 clocks.
    reg [12:0] startup = 13'd0;
    always @(posedge clk)
        if (!startup[12]) startup <= startup + 1'b1;

    pwm_20khz_core #(.HIGH_TICKS(HIGH_TICKS)) generator (
        .clk(clk), .rst(!startup[12]), .pwm(pwm)
    );
endmodule

module pwm_20khz_core #(
    parameter integer HIGH_TICKS = 600 // valid range 0..1200 inclusive
) (
    input wire clk, // nominal 24 MHz
    input wire rst,
    output reg pwm = 1'b0
);
    // 24,000,000 / 1,200 = 20,000 Hz; oscillator tolerance affects actual Hz.
    reg [10:0] phase = 11'd0;
    always @(posedge clk) begin
        if (rst) begin
            phase <= 11'd0;
            pwm <= 1'b0;
        end else begin
            phase <= (phase == 11'd1199) ? 11'd0 : phase + 1'b1;
            pwm <= (phase < HIGH_TICKS); // registered output avoids decode glitches
        end
    end
endmodule
