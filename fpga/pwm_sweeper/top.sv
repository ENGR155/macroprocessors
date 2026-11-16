module top(input logic adc_miso,
	output 	logic pwm, output logic adc_clk, output logic adc_mosi, output logic adc_cs, input logic mcu_clk, input logic mcu_cs, output logic mcu_miso
);

	logic int_osc;
	logic[7:0] duty;
	logic[11:0] v_diff;
	// logic[7:0] trunc_v_diff;
	// assign trunc_v_diff = v_diff[11:4];
	HSOSC hf_osc (.CLKHFPU(1'b1), .CLKHFEN(1'b1), .CLKHF(int_osc));
	sweep_8bit sweep(int_osc,1'b1, duty );
  pwm pwm_gen(int_osc, 1'b1, duty, pwm);
	adc_spi adc(int_osc, 1'b1, adc_miso, adc_mosi, adc_cs, adc_clk, v_diff);
	spi_word_tx send_word(mcu_clk, mcu_cs,v_diff, mcu_miso);

endmodule
