`timescale 1ns/1ps
module tb_current_pi;
    logic clk=0,rst=1,enable=0,sample=0;
    logic [11:0] measured=500,target=800;
    logic [15:0] kp=256,ki=16;
    wire [11:0] duty;
    always #20.833333 clk=~clk;
    current_pi dut(clk,rst,enable,sample,measured,target,kp,ki,duty);
    task automatic update;
        @(negedge clk); sample=1; @(negedge clk); sample=0;
        repeat(9) @(negedge clk);
    endtask
    initial begin
        repeat(3) @(negedge clk); rst=0; enable=1;
        update(); if(duty!=318) $fatal(1,"Incorrect Q8.8 first update: %0d",duty);
        update(); if(duty!=337) $fatal(1,"Incorrect accumulated integral: %0d",duty);
        enable=0; repeat(2) @(negedge clk);
        if(duty || dut.integral) $fatal(1,"Disable did not reset history");
        enable=1; kp=4096; ki=1024; measured=0; target=1200;
        repeat(20) update();
        if(duty!=1080 || dut.integral!=0) $fatal(1,"Saturation/anti-windup failed");
        measured=1200; target=0; update();
        if(duty) $fatal(1,"Negative error did not clamp to zero");
        kp=0; ki=256; measured=500; target=800;
        repeat(10) update();
        if(duty!=900) $fatal(1,"Integral continued winding up: %0d",duty);
        measured=900; update(); if(duty!=800) $fatal(1,"Integral failed to unwind");
        enable=0; update(); if(duty || dut.integral) $fatal(1,"Final disable failed");
        $display("Current PI PASS: fixed-point arithmetic, positive/negative error, clamps, anti-windup, reset");
        $finish;
    end
    initial begin #1000000; $fatal(1,"PI test timeout"); end
endmodule
