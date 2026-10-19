// Multi-cycle PI: ki includes the 100 us sample interval.
// Seven short registered stages complete in <0.3 us at 24 MHz.
module current_pi #(parameter integer MAX_DUTY=1080) (
    input logic clk,rst,enable,sample,
    input logic [11:0] measured,target,
    input logic [15:0] kp_q8,ki_q8,
    output logic [11:0] duty
);
    logic [2:0] stage;
    logic signed [12:0] error;
    logic signed [13:0] kp;
    logic signed [11:0] ki;
    logic signed [26:0] p_term;
    logic signed [23:0] i_delta;
    logic signed [24:0] trial_i;
    logic signed [27:0] trial_sum,final_sum;
    logic signed [20:0] integral,chosen_i;
    wire accept_i=(trial_sum>=0 && trial_sum<=MAX_DUTY*256) ||
                  (trial_sum>MAX_DUTY*256 && error<0) || (trial_sum<0 && error>0);
    always_ff @(posedge clk) begin
        if(rst || !enable) begin
            stage<=0; integral<=0; chosen_i<=0; duty<=0;
            error<=0; kp<=0; ki<=0; p_term<=0; i_delta<=0;
            trial_i<=0; trial_sum<=0; final_sum<=0;
        end else case(stage)
            0: if(sample) begin
                error<=$signed({1'b0,target})-$signed({1'b0,measured});
                kp<=$signed({1'b0,kp_q8[12:0]}); ki<=$signed({1'b0,ki_q8[10:0]});
                stage<=1;
            end
            1: begin p_term<=error*kp; i_delta<=error*ki; stage<=2; end
            2: begin trial_i<=integral+i_delta; stage<=3; end
            3: begin trial_sum<=p_term+trial_i; stage<=4; end
            4: begin
                if(accept_i) begin
                    if(trial_i>MAX_DUTY*256) chosen_i<=MAX_DUTY*256;
                    else if(trial_i< -MAX_DUTY*256) chosen_i<= -MAX_DUTY*256;
                    else chosen_i<=trial_i[20:0];
                end else chosen_i<=integral;
                stage<=5;
            end
            5: begin integral<=chosen_i; final_sum<=p_term+chosen_i; stage<=6; end
            6: begin
                if(final_sum<0) duty<=0;
                else if(final_sum>MAX_DUTY*256) duty<=MAX_DUTY;
                else duty<=final_sum[19:8];
                stage<=0;
            end
            default: stage<=0;
        endcase
    end
endmodule
