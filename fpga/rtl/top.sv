`include "project_config.svh"
module top #(
    parameter integer COMMISSIONED=`LEV_COMMISSIONED,
    parameter integer CURRENT_KP_Q8=`LEV_CURRENT_KP_Q8,
    parameter integer CURRENT_KI_Q8=`LEV_CURRENT_KI_Q8
) (
    input wire mcu_sck,mcu_cs_n,mcu_mosi,permit,fault_n,
    output wire mcu_miso,pwm,gate_enable,sample_debug
);
    wire clk;
`ifdef RADIANT
    HSOSC #(.CLKHF_DIV("0b01")) osc(.CLKHFPU(1'b1),.CLKHFEN(1'b1),.CLKHF(clk));
`else
    SB_HFOSC #(.CLKHF_DIV("0b01")) osc(.CLKHFPU(1'b1),.CLKHFEN(1'b1),.CLKHF(clk));
`endif
    // iCE40 configuration initializes this counter; hold reset for ~171 us.
    reg [12:0] power_on=0;
    always @(posedge clk) if(!power_on[12]) power_on<=power_on+1'b1;
    wire rst=!power_on[12];
    wire [7:0] faults;
    lev_core #(.COMMISSIONED(COMMISSIONED),.MAX_CURRENT_COUNTS(`LEV_MAX_CURRENT_COUNTS),
               .CURRENT_KP_Q8(CURRENT_KP_Q8),.CURRENT_KI_Q8(CURRENT_KI_Q8))
      core(clk,rst,mcu_sck,mcu_cs_n,mcu_mosi,permit,fault_n,
           mcu_miso,pwm,gate_enable,faults,sample_debug);
endmodule
