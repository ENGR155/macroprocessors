module top(input logic adc_miso,
	output 	logic pwm, output logic adc_clk, output logic adc_mosi, output logic adc_cs
);
	logic int_osc;
	logic[7:0] duty;
	logic[11:0] v_diff;
	HSOSC hf_osc (.CLKHFPU(1'b1), .CLKHFEN(1'b1), .CLKHF(int_osc));
	sweep_8bit sweep(int_osc,1'b1, duty );
  pwm pwm_gen(int_osc, 1'b1, duty, pwm);
	adc_spi adc(int_osc, 1'b1, adc_miso, adc_mosi, adc_cs, adc_clk, v_diff);

endmodule
