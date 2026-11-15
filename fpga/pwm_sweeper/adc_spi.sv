module adc_spi(
  input  logic clk,
  input  logic n_reset, input logic miso,
output logic mosi, output logic n_cs, output logic n_spi_clk,  output logic [11:0] v_diff
);
logic [4:0] prescale_count;
logic spi_tick;
// logic [3:0] control_bits = 4'b0000

counter #(24, 5) prescale_counter(clk, n_reset, 1'b1, prescale_count);
assign n_spi_clk = prescale_count>11;
assign spi_tick = prescale_count==0;
logic [4:0] bit_count;
assign mosi =bit_count==13;
counter #(20, 5) bit_counter(clk, n_reset, spi_tick, bit_count);
assign n_cs = bit_count==12;
 always_ff @(posedge clk or negedge n_reset) begin
        if (!n_reset)
            v_diff <= 12'b0;
        else if(n_spi_clk)
            v_diff[11-bit_count] <= miso;
    end

endmodule
