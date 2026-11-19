module dsp_addsub #(
    parameter bit SUBTRACT = 1'b0
) (
    input  logic [31:0] in_a,
    input  logic [31:0] in_b,
    output wire  [31:0] out
);

    SB_MAC16 #(
        .A_REG(1'b0),
        .B_REG(1'b0),
        .C_REG(1'b0),
        .D_REG(1'b0),

        .TOPOUTPUT_SELECT(2'b00),
        .BOTOUTPUT_SELECT(2'b00),

        .TOPADDSUB_UPPERINPUT(1'b1),  // C
        .BOTADDSUB_UPPERINPUT(1'b1),  // D
        .TOPADDSUB_LOWERINPUT(2'b00), // A
        .BOTADDSUB_LOWERINPUT(2'b00), // B

        .TOPADDSUB_CARRYSELECT(2'b11), // Carry/borrow from lower half
        .BOTADDSUB_CARRYSELECT(2'b00)
    ) dsp (
        .CLK(1'b0),
        .CE(1'b1),

        .A(in_b[31:16]),
        .B(in_b[15:0]),
        .C(in_a[31:16]),
        .D(in_a[15:0]),

        .AHOLD(1'b0),
        .BHOLD(1'b0),
        .CHOLD(1'b0),
        .DHOLD(1'b0),

        .IRSTTOP(1'b0),
        .IRSTBOT(1'b0),
        .ORSTTOP(1'b0),
        .ORSTBOT(1'b0),

        .OLOADTOP(1'b0),
        .OLOADBOT(1'b0),
        .OHOLDTOP(1'b0),
        .OHOLDBOT(1'b0),

        .ADDSUBTOP(SUBTRACT),
        .ADDSUBBOT(SUBTRACT),

        .CI(1'b0),
        .ACCUMCI(1'b0),
        .SIGNEXTIN(1'b0),

        .O(out),
        .CO(),
        .ACCUMCO(),
        .SIGNEXTOUT()
    );

endmodule