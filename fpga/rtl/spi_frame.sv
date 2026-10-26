// Mode-0 SPI slave with a 24 MHz oversampling clock. SCK <= 1 MHz.
// CS must lead/trail SCK by >= 2 us. One CS interval is exactly 64 clocks.
module spi_frame (
    input logic clk, rst, sck, cs_n, mosi,
    input logic [63:0] status,
    output wire miso,
    output logic [63:0] command,
    output logic command_valid
);
    (* ASYNC_REG="TRUE" *) logic [2:0] ss=3'b111, sk=0, mi=0;
    logic [63:0] rx, tx;
    logic [7:0] count;
    wire cs_fall=ss[2] && !ss[1], cs_rise=!ss[2] && ss[1];
    wire rise=!sk[2] && sk[1], fall=sk[2] && !sk[1];
    // MISO releases the shared bus even while reset/configuration is settling.
    assign miso=cs_n?1'bz:tx[63];
    always_ff @(posedge clk) begin
        ss<={ss[1:0],cs_n}; sk<={sk[1:0],sck}; mi<={mi[1:0],mosi};
        command_valid<=0;
        if (rst) begin rx<=0; tx<=0; count<=0; command<=0; end
        else if (cs_fall) begin tx<=status; rx<=0; count<=0; end
        else if (cs_rise) begin
            if(count==64) begin command<=rx; command_valid<=1; end
        end else if (!ss[1]) begin
            if (rise) begin
                rx<={rx[62:0],mi[1]};
                if (count<65) count<=count+1'b1;
            end
            if (fall) tx<={tx[62:0],1'b0};
        end
    end
endmodule
