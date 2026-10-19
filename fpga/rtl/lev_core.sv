module lev_core #(
    parameter integer COMMISSIONED=0,
    parameter integer MAX_CURRENT_COUNTS=1241,
    parameter integer WATCHDOG_CYCLES=480000,
    parameter integer ADC_TIMEOUT_CYCLES=6000
) (
    input logic clk,rst,
    input logic mcu_sck,mcu_cs_n,mcu_mosi,adc_miso,
    input logic permit, fault_n,
    output wire mcu_miso,
    output logic adc_cs_n,adc_sck,adc_mosi,
    output wire pwm,gate_enable,
    output logic [7:0] faults,
    output logic sample_strobe
);
    (* ASYNC_REG="TRUE" *) logic [1:0] permit_s,fault_s;
    logic [12:0] frame_phase;
    logic [11:0] pwm_phase,requested_duty,active_duty;
    logic [11:0] current_raw,hall1_raw,hall2_raw;
    logic scan_done,scan_busy,adc_ready,enabled,command_valid;
    logic [15:0] sample_id,last_sequence,target,kp,ki,limit;
    logic sequence_seen;
    localparam integer WD_BITS=$clog2(WATCHDOG_CYCLES+1);
    localparam integer ADC_BITS=$clog2(ADC_TIMEOUT_CYCLES+1);
    logic [WD_BITS-1:0] watchdog;
    logic [ADC_BITS-1:0] adc_age;
    logic watchdog_expired,adc_expired;
    logic [127:0] command,pending_command,status;
    logic [111:0] status_body,status_payload;
    logic [15:0] command_crc,status_crc;
    logic command_crc_done,status_crc_done,status_crc_start;
    logic header_ok,bounds_ok,sequence_ok,crc_ok,crc_done_delayed,fresh_command,clear_allowed;
    logic over_limit,scan_done_delayed;
    logic [11:0] status_i,status_h1,status_h2;
    logic scan_start;
    // At 24 MHz, phase 60 is 2.5 us after every other PWM start.
    always_ff @(posedge clk) if(rst) scan_start<=0; else scan_start<=frame_phase==59;
    wire control_enable=COMMISSIONED!=0 && enabled && faults==0 && permit_s[1] && fault_s[1];
    assign sample_strobe=scan_done;
    assign gate_enable=COMMISSIONED!=0 && enabled && faults==0 && !rst && permit && fault_n;
    assign pwm=gate_enable && pwm_phase<active_duty;
    always_comb begin
        status_body={8'h5a,8'h01,sample_id,4'b0,status_h1,4'b0,status_h2,
                     4'b0,status_i,4'b0,active_duty,faults,6'b0,enabled,adc_ready};
    end
    spi_frame host(clk,rst,mcu_sck,mcu_cs_n,mcu_mosi,status,mcu_miso,command,command_valid);
    mcp3204_scan adc(clk,rst,scan_start,adc_miso,adc_cs_n,adc_sck,adc_mosi,
                    current_raw,hall1_raw,hall2_raw,scan_done,scan_busy);
    current_pi pi_loop(clk,rst,control_enable,scan_done,current_raw,target[11:0],kp,ki,requested_duty);
    crc112 command_checker(clk,rst,command_valid,command[127:16],command_crc,command_crc_done);
    crc112 status_checker(clk,rst,status_crc_start,status_payload,status_crc,status_crc_done);
    // Decode/bounds work runs in parallel with serial CRC. Register the final
    // decision too, so no long compare/CRC/fault-enable path crosses one clock.
    always_ff @(posedge clk) begin
        if(rst) begin
            header_ok<=0; bounds_ok<=0; sequence_ok<=0; crc_ok<=0;
            crc_done_delayed<=0; fresh_command<=0; clear_allowed<=0;
        end else begin
            header_ok<=pending_command[127:120]==8'ha5 && pending_command[119:112]==1 &&
                       pending_command[95:89]==0 && pending_command[87:81]==0;
            bounds_ok<=pending_command[79:64]<=pending_command[31:16] &&
                       pending_command[31:16]>0 && pending_command[31:16]<=MAX_CURRENT_COUNTS &&
                       pending_command[63:48]<=4096 && pending_command[47:32]<=1024;
            sequence_ok<=!sequence_seen || pending_command[111:96]!=last_sequence;
            crc_ok<=pending_command[15:0]==command_crc;
            crc_done_delayed<=command_crc_done;
            fresh_command<=crc_done_delayed && crc_ok && header_ok && bounds_ok && sequence_ok;
            clear_allowed<=fault_s[1] && adc_ready && adc_age<ADC_TIMEOUT_CYCLES &&
                           current_raw<pending_command[31:16];
        end
    end
    always_ff @(posedge clk) begin
        permit_s<={permit_s[0],permit}; fault_s<={fault_s[0],fault_n};
        if(rst) begin
            frame_phase<=0; pwm_phase<=0; active_duty<=0;
            adc_ready<=0; enabled<=0; faults<=0; sample_id<=0;
            status_i<=0; status_h1<=0; status_h2<=0;
            last_sequence<=0; sequence_seen<=0;
            watchdog<=0; adc_age<=0; target<=0; kp<=0; ki<=0; limit<=MAX_CURRENT_COUNTS;
            pending_command<=0; status<=0; status_payload<=0; status_crc_start<=0;
            over_limit<=0; scan_done_delayed<=0;
            watchdog_expired<=0; adc_expired<=0;
        end else begin
            watchdog_expired<=watchdog>=WATCHDOG_CYCLES;
            adc_expired<=adc_age>=ADC_TIMEOUT_CYCLES;
            over_limit<=current_raw>=limit;
            scan_done_delayed<=scan_done;
            status_crc_start<=0;
            if(command_valid) pending_command<=command;
            if(frame_phase==2250) begin status_payload<=status_body; status_crc_start<=1; end
            if(status_crc_done) status<={status_payload,status_crc};
            if(frame_phase==2399) frame_phase<=0; else frame_phase<=frame_phase+1'b1;
            if(pwm_phase==1199) begin
                pwm_phase<=0; active_duty<=control_enable?requested_duty:12'd0;
            end else pwm_phase<=pwm_phase+1'b1;
            if(!control_enable) active_duty<=0;
            if(watchdog<WATCHDOG_CYCLES) watchdog<=watchdog+1'b1;
            if(adc_age<ADC_TIMEOUT_CYCLES) adc_age<=adc_age+1'b1;
            if(scan_done) begin
                adc_ready<=1; adc_age<=0; sample_id<=sample_id+1'b1;
                status_i<=current_raw; status_h1<=hall1_raw; status_h2<=hall2_raw;
            end
            if(fresh_command) begin
                watchdog<=0; sequence_seen<=1; last_sequence<=pending_command[111:96];
                target<=pending_command[79:64]; kp<=pending_command[63:48]; ki<=pending_command[47:32];
                limit<=pending_command[31:16];
                if(pending_command[95:88]==0) enabled<=0;
                else if(COMMISSIONED!=0 && faults==0 && adc_ready && permit_s[1] && fault_s[1]) enabled<=1;
                // Clear requires a disabled packet, fresh ADC, safe current, and healthy external interlock.
                if(pending_command[80] && !pending_command[88] && clear_allowed) faults<=0;
            end
            // Fault conditions take precedence over a clear or enable in the same cycle.
            if(!fault_s[1]) begin faults[0]<=1; enabled<=0; end
            if(scan_done_delayed && over_limit) begin faults[1]<=1; enabled<=0; end
            if(enabled && watchdog_expired) begin faults[2]<=1; enabled<=0; end
            if(adc_expired) begin faults[3]<=1; enabled<=0; adc_ready<=0; end
            if(!permit_s[1]) enabled<=0;
        end
    end
endmodule
