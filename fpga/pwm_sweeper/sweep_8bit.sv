module sweep_8bit(
  input  logic clk,
  input  logic n_reset,
  output logic [7:0] out 
);
  typedef enum logic {
    INCR, DECR
} state_t;
state_t state, next_state;
logic [18:0] prescale_count;
logic [7:0] out_count;
logic prescaled_clk;
logic is_at_max_out;
counter #(524288, 19) prescale_counter(clk, n_reset, 1'b1, prescale_count);
assign prescaled_clk=prescale_count==524288-1;
counter #(256,  8) duty_counter(clk, n_reset,prescaled_clk, out_count);
assign is_at_max_out=out_count==255;
assign out = (state==INCR)?out_count: (255-out_count);

always_comb begin
    unique case (state)
        INCR: next_state = is_at_max_out ? DECR : INCR;
        DECR: next_state = is_at_max_out ? INCR:DECR;
        endcase
end

 always_ff @(posedge clk or negedge n_reset) begin
        if (!n_reset)
            state <= INCR;
        else if(prescaled_clk)
            state <= next_state;
    end




endmodule
