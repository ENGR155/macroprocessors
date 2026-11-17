module adc_spi(
  input  logic clk,
  input  logic n_reset, input logic miso,
output logic mosi, output logic n_cs, output logic n_spi_clk,  output logic [11:0] v_diff
);
logic channel, next_channel;
logic [6:0] prescale_count;
logic spi_tick;
logic [1:0] [11:0] channel_v;
// logic [3:0] control_bits = 4'b0000
logic frame_start;
counter #(128, 7) prescale_counter(clk, n_reset, 1'b1, prescale_count);
assign n_spi_clk = prescale_count>11;
assign spi_tick = prescale_count==0;
logic [4:0] bit_count;
counter #(20, 5) bit_counter(clk, n_reset, spi_tick, bit_count);
assign n_cs = bit_count==12;
assign frame_start = bit_count==13&& prescale_count==0;
always_comb begin
  next_channel = !channel;
        case (bit_count)
        5'd13: mosi=1;
        5'd14: mosi=1;
        5'd17: mosi=channel;
        default: mosi =0;
        endcase
end

 always_ff @(posedge clk or negedge n_reset) begin
        if (!n_reset)
        begin
            v_diff <= 12'b0;
            channel <= 1'b1;
        end
        else
        begin
          if(n_spi_clk)
          begin

              channel_v[channel][11-bit_count] <= miso;
          end
          if(frame_start)
          begin
              channel<=next_channel;
              v_diff= channel_v[0]-channel_v[1];
              // v_diff<=channel_v[0];
          end
        end
    end

endmodule
