`timescale 1ns/1ps
module tb_system;
    logic clk=0,rst=1,sck=0,cs=1,mosi=0,amiso=0,permit=1,fault_n=1;
    wire miso,acs,asck,amosi,pwm,en,sample;
    wire [7:0] faults;
    always #20.833333 clk=~clk;
    lev_core #(.COMMISSIONED(1),.WATCHDOG_CYCLES(480000))
        dut(clk,rst,sck,cs,mosi,amiso,permit,fault_n,miso,acs,asck,amosi,pwm,en,faults,sample);
    wire disabled_pwm,disabled_enable;
    lev_core disabled_build(.clk(clk),.rst(rst),.mcu_sck(sck),.mcu_cs_n(cs),
        .mcu_mosi(mosi),.adc_miso(amiso),.permit(permit),.fault_n(fault_n),
        .pwm(disabled_pwm),.gate_enable(disabled_enable));
    always @(posedge clk) if(!rst && (disabled_pwm!==0 || disabled_enable!==0))
        $fatal(1,"Uncommissioned build produced drive");
    function automatic [15:0] crc(input [111:0] p);
        reg [15:0] c;
        begin
            c=16'hffff;
            for(integer i=111;i>=0;i=i-1) c=(c[15]^p[i])?(c<<1)^16'h1021:c<<1;
            return c;
        end
    endfunction
    // Behavioral ADC checks command/channel selection and returns known codes.
    integer adc_bits=0,channel=0,scans=0;
    reg [23:0] adc_command=0;
    reg [11:0] adc_value=0;
    reg [11:0] current_value=500;
    always @(negedge acs) begin
        adc_bits=0; adc_command=0;
        case(channel) 0:adc_value=current_value;1:adc_value=2000;2:adc_value=2100;endcase
        amiso=0;
    end
    always @(posedge asck) if(!acs) begin
        adc_command={adc_command[22:0],amosi}; adc_bits=adc_bits+1;
        if(adc_bits==24 && adc_command!==(24'h060000|(channel<<14)))
            $fatal(1,"ADC channel command %h, channel %d",adc_command,channel);
    end
    always @(negedge asck) if(!acs) begin
        if(adc_bits>=12 && adc_bits<24) amiso=adc_value[23-adc_bits]; else amiso=0;
    end
    always @(posedge acs) if(!rst && adc_bits==24) begin
        channel=(channel+1)%3; if(channel==0) scans=scans+1;
    end
    task automatic transfer(input [127:0] tx,output [127:0] rx,input integer nbits=128);
        rx=0; sck=0; cs=0; #2000;
        for(integer b=127;b>=128-nbits;b=b-1) begin
            mosi=tx[b]; #500; sck=1; #100; rx={rx[126:0],miso}; #400; sck=0;
        end
        #2000; cs=1; #2000;
    endtask
    integer seq=0;
    reg [127:0] sent,received,replayed;
    task automatic command(input bit enable,input bit clear,input bit corrupt=0);
        reg [111:0] body;
        seq=seq+1;
        body={8'ha5,8'h01,16'(seq),8'(enable),8'(clear),16'd800,16'd256,16'd16,16'd1241};
        sent={body,crc(body)}; if(corrupt) sent[0]=~sent[0];
        transfer(sent,received);
        if(received[127:120]!==8'h5a || received[15:0]!==crc(received[127:16]))
            $fatal(1,"Invalid telemetry CRC/header %h",received);
    endtask
    initial begin
        #1000; rst=0; #100000;
        command(0,1); command(0,0);
        if(received[95:80]!==2000 || received[79:64]!==2100 || received[63:48]!==500)
            $fatal(1,"ADC data ordering %h",received);
        command(1,0); replayed=sent; #200000;
        if(!en || dut.active_duty==0 || dut.active_duty>1080) $fatal(1,"No regulated output");
        // Invalid CRC and short frames cannot stop or pet the watchdog.
        command(0,0,1); if(!en) $fatal(1,"Bad CRC executed");
        transfer(128'd0,received,64); if(!en) $fatal(1,"Short frame executed");
        // Repeated sequence numbers cannot keep an abandoned controller armed.
        repeat(160) transfer(replayed,received);
        if(en || !faults[2]) $fatal(1,"Watchdog did not latch");
        command(0,1); command(1,0); #150000;
        fault_n=0; #1; if(pwm || en) $fatal(1,"External fault gating was not immediate");
        #1000; fault_n=1; #1000;
        if(!faults[0]) $fatal(1,"External fault was not latched");
        command(0,1); command(1,0); current_value=1300; #200000;
        if(en || !faults[1]) $fatal(1,"Overcurrent did not latch");
        current_value=500; #200000; command(0,1); command(1,0);
        force dut.scan_done=0; #300000;
        if(en || !faults[3]) $fatal(1,"ADC timeout did not latch");
        release dut.scan_done;
        if(scans<10) $fatal(1,"Too few scans");
        $display("FPGA PASS: ADC commands/data, SPI/CRC, PI/PWM, abort, replay watchdog, interlock, current trip, ADC timeout");
        $finish;
    end
    initial begin #40000000; $fatal(1,"Global test timeout"); end
endmodule
