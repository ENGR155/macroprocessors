module pid_controller#(parameter logic signed [15:0]KP = 240, parameter signed [15:0]KI =4, parameter logic signed [15:0]KD =600) (
  input  logic clk,
  input  logic n_reset,
  input logic [15:0]desired_state,
  input logic [15:0] current_state,
  input logic controller_tick,
  output logic[7:0] out,
  output logic [15:0] debug_out
);
logic signed[15:0] error;
logic signed[15:0] p_term, next_p_term, i_addend, next_i_addend, d_term, next_d_term, i_term, pi, pid;

logic signed[15:0] previous_error;
logic signed[15:0] delta_error;

// assign i_addend = error<<<KI;
logic [2:0] stage_counter;
counter #(3, 2) slow_int(clk, n_reset, 1'b1, stage_counter);

dsp_addsub #(1'b1)error_calc (current_state, desired_state, error);
	dsp_mac  #(1'b0, 1'b1) proportional (clk,1'b1,1'b1, KP, error, next_p_term); 
  dsp_mac #(1'b0, 1'b1) addend (clk, 1'b1, 1'b1, KI, error, next_i_addend);
  accumulator integral (clk,  controller_tick,n_reset, i_addend, i_term);
  // dsp_addsub #(1'b1)delta_error_calc (error, previous_error, delta_error);
  	dsp_mac  #(1'b0, 1'b1) derivative (clk,1'b1,1'b1, KD, delta_error, next_d_term); 
  // dsp_mac  #(1'b1, 1'b1) integral (clk,1'b1, controller_tick,1, i_addend, i_term); 
  dsp_addsub PI_sum (p_term, i_term, pi);
  dsp_addsub PID_sum (pi, d_term, pid);
  // logic [15:0] pi_unsigned;
  // assign pi_unsigned= pi ^ 16'h8000;
  // logic [15:0] pid_unsigned;
  // assign pid_unsigned= pid ^ 16'h8000;
  // assign out=pid_unsigned[15:8];
always_comb begin
    // debug_out = d_term;
    if (pid[15])         // Negative
        out = 8'd0;
    else if (pid[14])    // Positive value >= 16384
        out = 8'd255;
    else
        out = pid[13:6];
    // out = delta_error;
end
  // assign out = d_term;

always_ff @(posedge clk)
	begin
		if(n_reset == 0) 
    begin
			// previous_error <=0;
      d_term <=0;
      i_addend<=0;
      p_term<=0;
    end
    else if(controller_tick ==1)
    begin
      d_term<=next_d_term;
      i_addend<=next_i_addend;
      p_term<=next_p_term;
      // previous_error <= error;
    end
	end
  logic sample_ready;

always_ff @(posedge clk) begin
    if (!n_reset) begin
        sample_ready   <= 1'b0;
        previous_error <= '0;
        delta_error    <= '0;
    end else begin
        sample_ready <= controller_tick;

        if (sample_ready) begin
            delta_error    <= error - previous_error;
            previous_error <= error;
        end
    end
end

endmodule
