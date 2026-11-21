module top(input logic adc_miso, input logic n_reset,
	output 	logic pwm, output logic adc_clk, output logic adc_mosi, output logic adc_cs, input logic mcu_clk, input logic mcu_cs, output logic mcu_miso
);
	logic sensor_read_tick;
	logic int_osc;
	logic[7:0] duty;
	logic[11:0] v_diff;
	logic [15:0] setpoint = 16'd2280;
	logic [15:0] debug_data;
	// logic[7:0] trunc_v_diff;
	// assign trunc_v_diff = v_diff[11:4];
	logic[15:0] pos_mm;
	// field_to_position f_to_p(v_diff, pos_mm);
	HSOSC hf_osc (.CLKHFPU(1'b1), .CLKHFEN(1'b1), .CLKHF(int_osc));
	// sweep_8bit sweep(int_osc,1'b1, duty );
  // pwm pwm_gen(int_osc, 1'b1, duty, pwm);
	pwm pwm_gen(int_osc, 1'b1, duty, pwm);
	// assign pwm=1;
	adc_spi adc(int_osc, 1'b1, adc_miso, adc_mosi, adc_cs, adc_clk, v_diff, sensor_read_tick);
	pid_controller pid(int_osc, n_reset, setpoint, v_diff, sensor_read_tick, duty);
	spi_word_tx send_word(mcu_clk, mcu_cs,duty, mcu_miso);

endmodule
