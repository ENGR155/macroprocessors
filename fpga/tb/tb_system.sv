`timescale 1ns/1ps
module tb_system;
    logic clk=0,rst=1,sck=0,cs=1,adc_cs=1,mosi=0,permit=1,fault_n=1;
    tri miso;
    wire pwm,en,sample;
    wire [7:0] faults;
    always #20.833333 clk=~clk;
    lev_core #(.COMMISSIONED(1),.CURRENT_KP_Q8(256),.CURRENT_KI_Q8(16))
        dut(clk,rst,sck,cs,mosi,permit,fault_n,miso,pwm,en,faults,sample);
    wire disabled_pwm,disabled_enable;
    lev_core disabled_build(.clk(clk),.rst(rst),.mcu_sck(sck),.mcu_cs_n(cs),
        .mcu_mosi(mosi),.permit(permit),.fault_n(fault_n),
        .pwm(disabled_pwm),.gate_enable(disabled_enable));
    always @(posedge clk) if(!rst && (disabled_pwm!==0 || disabled_enable!==0))
        $fatal(1,"Uncommissioned build produced drive");
    function automatic [15:0] crc(input [47:0] p);
        reg [15:0] c;
        begin
            c=16'hffff;
            for(integer i=47;i>=0;i=i-1) c=(c[15]^p[i])?(c<<1)^16'h1021:c<<1;
            return c;
        end
    endfunction
    // ADC and FPGA share SCK/MOSI/MISO with independent chip selects.
    integer adc_bits=0,channel=0,scans=0,accepted=0;
    reg [23:0] adc_command=0;
    reg [11:0] adc_value=0,current_value=500;
    reg adc_miso=0;
    assign miso=adc_cs?1'bz:adc_miso;
    always @(negedge adc_cs) begin adc_bits=0; adc_command=0; adc_miso=0; end
    always @(posedge sck) if(!adc_cs) begin
        adc_command={adc_command[22:0],mosi}; adc_bits=adc_bits+1;
        if(adc_bits==12) begin
            channel=adc_command[3:2];
            case(channel) 0:adc_value=current_value;1:adc_value=1900;2:adc_value=2100;
                default:$fatal(1,"Unexpected ADC channel"); endcase
        end
    end
    always @(negedge sck) if(!adc_cs) begin
        if(adc_bits>=12 && adc_bits<24) adc_miso=adc_value[23-adc_bits]; else adc_miso=0;
    end
    always @(posedge adc_cs) if(!rst && adc_bits) begin
        if(adc_bits!=24 || adc_command!==(24'h060000|(channel<<14)))
            $fatal(1,"Bad MCU ADC command %h",adc_command);
        scans=scans+1;
    end
    always @(posedge clk) if(!rst && sample) accepted=accepted+1;
    always @(negedge adc_cs) if(!cs) $fatal(1,"Two chip selects active together");
    always @(posedge adc_cs) begin
        #100; if(cs && miso!==1'bz) $fatal(1,"Unselected SPI devices did not release MISO");
    end
    task automatic read_adc(input integer ch,output reg [11:0] value);
        reg [23:0] tx,rx;
        tx=24'h060000|(ch<<14); rx=0; adc_cs=0; #1000;
        for(integer b=23;b>=0;b=b-1) begin
            mosi=tx[b]; #500; sck=1; #100; rx={rx[22:0],miso}; #400; sck=0;
        end
        #1000; adc_cs=1; #1000; value=rx[11:0];
    endtask
    task automatic transfer(input [63:0] tx,output [63:0] rx,input integer nbits=64);
        rx=0; sck=0; cs=0; #2000;
        for(integer b=0;b<nbits;b=b+1) begin
            mosi=tx[63-(b%64)]; #500; sck=1; #100; rx={rx[62:0],miso}; #400; sck=0;
        end
        #2000; cs=1; #6000;
    endtask
    integer seq=0;
    reg [63:0] sent,received,replayed;
    reg [11:0] measured,hall1,hall2;
    time next_scan=0;
    integer cycles=0,last_command_cycle=0;
    always @(posedge clk) begin
        cycles=cycles+1;
        if(dut.fresh_command) last_command_cycle=cycles;
        if(!rst && dut.active_duty>1080) $fatal(1,"PWM duty exceeded 90 percent");
    end
    always @(posedge faults[2])
        if(cycles-last_command_cycle<1199999 || cycles-last_command_cycle>1200008)
            $fatal(1,"Watchdog interval was not 50 ms: %0d clocks",cycles-last_command_cycle);
    task automatic command(input bit enable,input bit clear,input bit corrupt=0,input integer halls=2);
        reg [47:0] body;
        if($time<next_scan) #(next_scan-$time);
        next_scan=$time+200000;
        read_adc(0,measured); read_adc(1,hall1);
        if(halls==2) read_adc(2,hall2);
        if(measured!==current_value || hall1!==1900 || (halls==2 && hall2!==2100))
            $fatal(1,"MCU ADC read/data alignment");
        seq=seq+1;
        body={6'b101000,clear,enable,8'(seq),4'b0,measured,16'd800};
        sent={body,crc(body)}; if(corrupt) sent[0]=~sent[0];
        transfer(sent,received);
        if(received[63:58]!==6'b010100 || received[15:0]!==crc(received[63:16]))
            $fatal(1,"Invalid telemetry CRC/header %h",received);
    endtask
    task automatic rejected(input [47:0] body,input integer bits=64);
        integer before_count;
        before_count=accepted; transfer({body,crc(body)},received,bits);
        if(accepted!=before_count) $fatal(1,"Malformed packet accepted");
    endtask
    integer before_count;
    initial begin
        #1000; rst=0; #10000;
        command(0,1); command(0,0);
        if(received[55:48]!==8'd1) $fatal(1,"Status did not ACK previous command");
        command(1,0); replayed=sent; #50000;
        if(!en || dut.active_duty==0 || dut.active_duty>1080) $fatal(1,"No regulated output");
        if(dut.current_raw!==500 || dut.target!==800) $fatal(1,"Paired current decode");
        // Valid disabled commands stop drive, even with permission still asserted.
        command(0,0); if(en || pwm) $fatal(1,"STOP command did not disable drive");
        command(1,0,0,1); // supported one-Hall scan: two ADC transactions
        if(!en) $fatal(1,"One-sensor acquisition did not enable");
        permit=0; #1; if(pwm || en) $fatal(1,"Permit removal not immediate");
        #1000; permit=1; #1000; command(1,0);
        before_count=accepted; command(0,0,1); if(accepted!=before_count || !en) $fatal(1,"Bad CRC executed");
        rejected(48'ha00001f40320,32); // short frame
        rejected(48'ha00001f40320,65); // overlong frame
        rejected(48'ha40001f40320);    // reserved flag
        rejected(48'ha00010000320);    // measurement beyond 12 bits
        rejected(48'ha00001f41000);    // target beyond compiled hard limit
        if(!en) $fatal(1,"Malformed traffic changed enable");
        // Exercise the 8-bit wrap using actual 200 us scan periods.
        repeat(260) command(1,0);
        replayed=sent;
        // Replays must neither integrate PI again nor refresh the 50 ms watchdog.
        before_count=accepted;
        repeat(660) transfer(replayed,received);
        if(!en || faults[2]) $fatal(1,"Watchdog expired before 50 ms");
        repeat(30) transfer(replayed,received);
        if(en || !faults[2] || accepted!=before_count) $fatal(1,"Replay refreshed watchdog/PI");
        command(0,1); command(1,0); #50000;
        fault_n=0; #1; if(pwm || en) $fatal(1,"External fault gating was not immediate");
        #1000; fault_n=1; #1000;
        if(!faults[0]) $fatal(1,"External fault was not latched");
        command(1,1); if(en || !faults[0]) $fatal(1,"Enabled packet cleared a fault");
        command(0,1); command(1,0); current_value=1300;
        command(1,0); if(en || !faults[1]) $fatal(1,"Measured overcurrent did not latch");
        command(0,1); if(!faults[1]) $fatal(1,"Unsafe current allowed clear");
        current_value=500; command(0,1); command(1,0);
        #50000; if(!en || faults) $fatal(1,"Safe clear/re-arm failed");
        #51000000; if(en || !faults[2]) $fatal(1,"Missing-command watchdog failed");
        if(scans<500) $fatal(1,"Too few shared-bus ADC reads");
        $display("FPGA PASS: shared SPI ADC acquisition, 8-byte CRC/ACK, paired PI/PWM, one/two Hall, STOP, malformed/replay/wrap, 50 ms watchdog, interlock, overcurrent, clear, default lockout");
        $finish;
    end
    initial begin #200000000; $fatal(1,"Global test timeout"); end
endmodule
