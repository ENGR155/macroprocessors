`timescale 1ns/1ps
module tb_spi_byte;
    reg sck=0, cs_n=1;
    reg [7:0] byte_in=0;
    wire miso;
    spi_byte_tx dut(sck,cs_n,byte_in,miso);
    task automatic read_bits(input integer bits, output reg [7:0] rx);
        rx=0;
        for(integer k=0;k<bits;k=k+1) begin
            #4000; sck=1; #100; rx={rx[6:0],miso};
            #3900; sck=0;
        end
    endtask
    reg [7:0] rx;
    initial begin
        #100;
        if(miso!==1'bz) $fatal(1,"MISO must release when deselected");
        for(integer n=0;n<256;n=n+1) begin
            byte_in=n; cs_n=0; #2000;
            read_bits(8,rx);
            if(rx!==byte_in) $fatal(1,"n=%d rx=%h",n,rx);
            #2000; cs_n=1; #2000;
            if(miso!==1'bz) $fatal(1,"MISO release");
        end
        byte_in=8'hA5; cs_n=0; #2000; read_bits(3,rx);
        #2000; cs_n=1; #2000; cs_n=0; #2000; read_bits(8,rx);
        if(rx!==8'hA5) $fatal(1,"CS did not reset partial byte");
        $display("PASS: all 256 byte values, MISO release, aborted-byte recovery at 125 kHz");
        $finish;
    end
endmodule
