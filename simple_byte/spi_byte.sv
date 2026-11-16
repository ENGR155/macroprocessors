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
