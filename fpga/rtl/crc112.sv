// CRC-16/CCITT-FALSE over 112 bits, one bit per 24 MHz clock (~4.67 us).
module crc112(input logic clk,rst,start, input logic [111:0] payload,
    output logic [15:0] value, output logic done);
    logic [111:0] shift;
    logic [15:0] accumulator;
    logic [6:0] remaining;
    logic busy,last_bit;
    wire [15:0] next_crc=(accumulator[15]^shift[111])?
                         (accumulator<<1)^16'h1021:accumulator<<1;
    always_ff @(posedge clk) begin
        done<=0;
        if(rst) begin
            shift<=0; accumulator<=16'hffff; remaining<=0; value<=0; busy<=0; last_bit<=0;
        end else if(start && !busy) begin
            shift<=payload; accumulator<=16'hffff; remaining<=112; busy<=1; last_bit<=0;
        end else if(busy) begin
            accumulator<=next_crc; shift<={shift[110:0],1'b0}; remaining<=remaining-1'b1;
            last_bit<=remaining==2;
            if(last_bit) begin value<=next_crc; done<=1; busy<=0; end
        end
    end
endmodule
