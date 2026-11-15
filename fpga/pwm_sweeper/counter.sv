module counter #(
parameter MAX_COUNT = 200_000,
parameter COUNTER_WIDTH = 25
) (input logic clk, n_reset, enable,
output logic[COUNTER_WIDTH-1:0] counter);
	
	// Simple clock divider
	always_ff @(posedge clk)
	begin
		if(n_reset == 0) 
			counter <=0;
    else if(enable ==1)
    begin
      if(counter == MAX_COUNT-1) 
        counter <= 0;
      else
        counter <= counter+1'b1;
    end
	end

endmodule
