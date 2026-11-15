module top(
	output 	logic pwm
);
	logic int_osc;
	logic[7:0] duty;
	HSOSC hf_osc (.CLKHFPU(1'b1), .CLKHFEN(1'b1), .CLKHF(int_osc));
	sweep_8bit sweep(int_osc,1'b1, duty );
  pwm pwm_gen(int_osc, 1'b1, duty, pwm);

endmodule
