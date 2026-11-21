module dsp_mac #(parameter ACCUMULATE_ENABLE = 1'b1, parameter SIGNED_ENABLE = 1'b1)(
  input  logic clk,
  input  logic n_reset,
  input logic enable,
  input logic [15:0] in_a,
  input logic [15:0] in_b,
  output logic [31:0] out
);
logic [31:0] full_result;

assign out = full_result;
 SB_MAC16 #(
        .NEG_TRIGGER(1'b0),

        // No input or multiplier pipeline registers
        .A_REG(1'b1),
        .B_REG(1'b1),
        .C_REG(1'b0),
        .D_REG(1'b0),
        .TOP_8x8_MULT_REG(1'b0),
        .BOT_8x8_MULT_REG(1'b0),
        .PIPELINE_16x16_MULT_REG1(1'b1),
        .PIPELINE_16x16_MULT_REG2(1'b1),

        // MAC: registered adder output; multiply: direct product
        .TOPOUTPUT_SELECT(ACCUMULATE_ENABLE ? 2'b01 : 2'b11),
        .BOTOUTPUT_SELECT(ACCUMULATE_ENABLE ? 2'b01 : 2'b11),

        // Feed the 32-bit product into the adders
        .TOPADDSUB_LOWERINPUT(2'b10),
        .BOTADDSUB_LOWERINPUT(2'b10),

        // Feed accumulator registers back into the adders
        .TOPADDSUB_UPPERINPUT(1'b0),
        .BOTADDSUB_UPPERINPUT(1'b0),

        // Connect lower accumulator carry to upper accumulator
        .TOPADDSUB_CARRYSELECT(2'b10),
        .BOTADDSUB_CARRYSELECT(2'b00),

        .MODE_8x8(1'b0),
        .A_SIGNED(SIGNED_ENABLE),
        .B_SIGNED(SIGNED_ENABLE)
    ) dsp (
        .CLK(clk),
        .CE(1'b1),

        .A(in_a),
        .B(in_b),
        .C(16'b0),
        .D(16'b0),

        .AHOLD(1'b0),
        .BHOLD(1'b0),
        .CHOLD(1'b0),
        .DHOLD(1'b0),

        .IRSTTOP(1'b0),
        .IRSTBOT(1'b0),
        .ORSTTOP(~n_reset),
        .ORSTBOT(~n_reset),

        .OLOADTOP(1'b0),
        .OLOADBOT(1'b0),
        .OHOLDTOP(~enable),
        .OHOLDBOT(~enable),

        .ADDSUBTOP(1'b0),
        .ADDSUBBOT(1'b0),

        .CI(1'b0),
        .ACCUMCI(1'b0),
        .SIGNEXTIN(1'b0),

        .O(full_result),
        .CO(),
        .ACCUMCO(),
        .SIGNEXTOUT()
    );

endmodule
