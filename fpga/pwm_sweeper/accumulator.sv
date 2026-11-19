module accumulator (
  input  logic clk,
  input logic tick,
  input  logic n_reset,
  input logic signed[15:0] addend,
  output logic[15:0] out
);

logic [31:0] sum;
logic[31:0] next_sum;
dsp_addsub big_add(addend, sum, next_sum);
assign out = sum[31:16];

always_ff @(posedge clk)
	begin
		if(n_reset == 0) 
			sum <=0;
    else if(tick ==1)
    begin
      sum <= next_sum;
    end
	end

endmodule
