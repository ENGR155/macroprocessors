module field_to_position(
  input		logic [11:0] v_diff,
	output 	logic [15:0] pos_mm);
            
assign pos_mm =  583 + (19'd511630 / (v_diff + 433));

endmodule
