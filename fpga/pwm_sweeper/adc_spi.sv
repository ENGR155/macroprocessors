module adc_spi(
  input  logic clk,
  input  logic n_reset, input logic miso,
output logic mosi, output logic n_cs, output logic n_spi_clk,  output logic [11:0] v_diff, output logic frame_start_tick
);
  typedef enum logic {
    TRANSACTION, SAMPLING
} state_t;
state_t state, next_state;
logic channel, next_channel;
logic [4:0] prescale_count;
logic [6:0] sample_time_count;
logic spi_tick;
logic [1:0] [11:0] channel_v;
// logic [3:0] control_bits = 4'b0000
counter #(128, 7) sample_time_counter(clk, n_reset, state==SAMPLING, sample_time_count);
counter #(24, 5) prescale_counter(clk, n_reset, state==TRANSACTION, prescale_count);

assign n_spi_clk = (state == TRANSACTION)? (prescale_count > 5'd11): (sample_time_count > 7'd63);
assign spi_tick = state==TRANSACTION?prescale_count==0: sample_time_count==0;
logic [4:0] bit_count;
counter #(20, 5) bit_counter(clk, n_reset, spi_tick, bit_count);
assign n_cs = bit_count==5'd19;
assign frame_start_tick = bit_count==0&& prescale_count==0;
assign next_state = (bit_count==4)?SAMPLING:TRANSACTION;
always_comb begin
  next_channel = !channel;
        case (bit_count)
        5'd0: mosi=1;
        5'd1: mosi=1;
        5'd4: mosi=channel;
        default: mosi =0;
        endcase
end

 always_ff @(posedge clk or negedge n_reset) begin
        if (!n_reset)
        begin
            v_diff <= 12'b0;
            channel <= 1'b1;
            state <=TRANSACTION;
            channel_v <= '0;
        end
        else
        begin
          if(n_spi_clk)
          begin
              state<=next_state;
              channel_v[channel][18-bit_count] <= miso;
          end
          if(frame_start_tick)
          begin
              channel<=next_channel;
              v_diff<= 4096-(channel_v[0]-channel_v[1]);
              // v_diff<=channel_v[0];
          end
        end
    end

endmodule
