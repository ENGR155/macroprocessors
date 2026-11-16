// CRC-16/CCITT-FALSE over six bytes, one bit per clock (2 us at 24 MHz).
module crc48(input logic clk,rst,start, input logic [47:0] payload,
    output logic [15:0] value, output logic done);
    logic [47:0] shift;
    logic [15:0] accumulator;
    logic [5:0] remaining;
    logic busy;
    wire [15:0] next_crc=(accumulator[15]^shift[47])?
                         (accumulator<<1)^16'h1021:accumulator<<1;
    always_ff @(posedge clk) begin
        done<=0;
        if(rst) begin
            shift<=0; accumulator<=16'hffff; remaining<=0; value<=0; busy<=0;
        end else if(start && !busy) begin
            shift<=payload; accumulator<=16'hffff; remaining<=48; busy<=1;
        end else if(busy) begin
            accumulator<=next_crc; shift<={shift[46:0],1'b0}; remaining<=remaining-1'b1;
            if(remaining==1) begin value<=next_crc; done<=1; busy<=0; end
        end
    end
endmodule
