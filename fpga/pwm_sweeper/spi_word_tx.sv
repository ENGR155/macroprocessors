// SPI mode 0, MSB first. Keep byte_in stable while cs_n is low.
// One CS-low interval = exactly one byte. No FPGA oscillator is needed.
module spi_word_tx (
    input  wire        sck,
    input  wire        cs_n,
    input  wire [15:0] word_in,
    output wire        miso
);
    logic [15:0] sampled_word;
    logic [3:0] bit_index = 4'd0;

    always_ff @(negedge cs_n)
        sampled_word <= word_in;

    always_ff @(negedge sck or posedge cs_n) begin
        if (cs_n)
            bit_index <= 4'd0;
        else
            bit_index <= bit_index + 4'd1;
    end

    assign miso = cs_n ? 1'bz : sampled_word[4'd15 - bit_index];
endmodule
