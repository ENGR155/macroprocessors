`timescale 1ns/1ps
module dsp_mac_tb();
  logic clk;

  // dut instance here
  logic n_reset;
	logic [15:0] a;
	logic [15:0] b;
	logic [31:0] out;
  dsp_mac #(1'b0, 1'b1)
 dut (
.clk(clk), .n_reset(n_reset), .in_a(a), .in_b(b), .out(out)
    );

  always begin
    clk = 1; #5;
    clk = 0; #5;
  end

  initial begin
    a = 555;
    b=445;
    @(posedge clk);
    #1
      assert(out==1000)
		$display("PASSED! Addition worked correctly: %0t.", $time);

    #100;
    $finish;
  end
endmodule
