module pwm(
  input  logic clk,
  input  logic n_reset,
  input logic [7:0] duty,
  output logic pwm
);

logic [3:0] prescale_count;
logic [7:0] duty_count;
logic prescaled_clk;

counter #(9, 4) prescale_counter(clk, n_reset, 1'b1, prescale_count);
assign prescaled_clk=prescale_count==8;
counter #(256,  8) duty_counter(clk, n_reset,prescaled_clk, duty_count);

assign pwm = duty_count<duty;



endmodule
