`timescale 1ns/1ps
// ModelSim/Questa:
//   vlog -sv pwm_20khz_top.sv tb_pwm_20khz.sv
//   vsim -c tb_pwm_20khz -do "run -all; quit -f"
// Icarus (from this folder):
//   iverilog -g2012 -s tb_pwm_20khz -o build/tb_pwm pwm_20khz_top.sv tb_pwm_20khz.sv
//   vvp build/tb_pwm
module tb_pwm_20khz;
    reg clk = 0;
    always #20.833 clk = !clk; // ~24 MHz, rounded to simulation resolution
    reg rst = 1;
    wire [4:0] pwm;
    pwm_20khz_core #(.HIGH_TICKS(0))    d0   (clk, rst, pwm[0]);
    pwm_20khz_core #(.HIGH_TICKS(300))  d25  (clk, rst, pwm[1]);
    pwm_20khz_core #(.HIGH_TICKS(600))  d50  (clk, rst, pwm[2]);
    pwm_20khz_core #(.HIGH_TICKS(900))  d75  (clk, rst, pwm[3]);
    pwm_20khz_core #(.HIGH_TICKS(1200)) d100 (clk, rst, pwm[4]);

    integer cycle, frame, high_count;
    reg [4:0] expected;
    task check_frames;
        begin
            for (frame = 0; frame < 4; frame = frame + 1) begin
                high_count = 0;
                for (cycle = 0; cycle < 1200; cycle = cycle + 1) begin
                    @(posedge clk); #1;
                    expected = {1'b1, (cycle < 900), (cycle < 600), (cycle < 300), 1'b0};
                    if (pwm !== expected)
                        $fatal(1, "Duty/period mismatch: frame=%0d cycle=%0d got=%b expected=%b", frame, cycle, pwm, expected);
                    if (pwm[2]) high_count = high_count + 1;
                end
                if (high_count != 600) $fatal(1, "Incorrect 50%% pulse width");
            end
        end
    endtask

    initial begin
        repeat (3) @(posedge clk);
        #1;
        if (pwm !== 5'b00000) $fatal(1, "Reset must hold every output low");
        @(negedge clk); rst = 0;
        check_frames();
        // Reset midway through a pulse; then verify phase restarts correctly.
        repeat (100) @(posedge clk);
        @(negedge clk); rst = 1;
        @(posedge clk); #1;
        if (pwm !== 5'b00000) $fatal(1, "Mid-pulse reset failed");
        @(negedge clk); rst = 0;
        check_frames();
        $display("PASS: 1200-clock periods, 0/25/50/75/100%% duty, startup reset and mid-pulse reset");
        $finish;
    end
    initial begin
        #1000000;
        $fatal(1, "Simulation timeout");
    end
endmodule
