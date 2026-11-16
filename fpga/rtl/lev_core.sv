// The MCU owns the shared ADC bus and sends paired measured/requested current.
module lev_core #(
    parameter integer COMMISSIONED=0,
    parameter integer MAX_CURRENT_COUNTS=1241,
    parameter integer CURRENT_KP_Q8=0,
    parameter integer CURRENT_KI_Q8=0,
    parameter integer WATCHDOG_CYCLES=1200000 // 50 ms at 24 MHz
) (
    input logic clk,rst,
    input logic mcu_sck,mcu_cs_n,mcu_mosi,
    input logic permit, fault_n,
    output wire mcu_miso,
    output wire pwm,gate_enable,
    output logic [7:0] faults,
    output logic sample_strobe
);
    (* ASYNC_REG="TRUE" *) logic [1:0] permit_s,fault_s;
    logic [11:0] pwm_phase,requested_duty,active_duty,current_raw,target;
    logic enabled,sample_ready,sequence_seen;
    logic [7:0] last_sequence;
    localparam integer WD_BITS=$clog2(WATCHDOG_CYCLES+1);
    logic [WD_BITS-1:0] watchdog;
    logic [63:0] command,pending_command,status;
    logic [47:0] status_body,status_payload;
    logic [15:0] command_crc,status_crc;
    logic command_valid,command_crc_done,status_crc_done,status_crc_start;
    logic header_ok,bounds_ok,sequence_ok,crc_ok,crc_done_delayed,fresh_command;
    logic [5:0] status_phase;
    wire control_enable=COMMISSIONED!=0 && enabled && faults==0 && permit_s[1] && fault_s[1];
    assign gate_enable=COMMISSIONED!=0 && enabled && faults==0 && !rst && permit && fault_n;
    assign pwm=gate_enable && pwm_phase<active_duty;
    always_comb status_body={6'b010100,enabled,sample_ready,last_sequence,
                            4'b0,active_duty,faults,8'b0};
    spi_frame host(clk,rst,mcu_sck,mcu_cs_n,mcu_mosi,status,mcu_miso,command,command_valid);
    current_pi pi_loop(clk,rst,control_enable,sample_strobe,current_raw,target,
                       16'(CURRENT_KP_Q8),16'(CURRENT_KI_Q8),requested_duty);
    crc48 command_checker(clk,rst,command_valid,command[63:16],command_crc,command_crc_done);
    crc48 status_checker(clk,rst,status_crc_start,status_payload,status_crc,status_crc_done);
    // Registered bounds/CRC decisions keep compare paths short on the UP5K.
    always_ff @(posedge clk) begin
        if(rst) begin
            header_ok<=0; bounds_ok<=0; sequence_ok<=0; crc_ok<=0;
            crc_done_delayed<=0; fresh_command<=0;
        end else begin
            header_ok<=pending_command[63:58]==6'b101000;
            bounds_ok<=pending_command[47:32]<=4095 && pending_command[31:16]<=MAX_CURRENT_COUNTS;
            sequence_ok<=!sequence_seen || pending_command[55:48]!=last_sequence;
            crc_ok<=pending_command[15:0]==command_crc;
            crc_done_delayed<=command_crc_done;
            fresh_command<=crc_done_delayed && crc_ok && header_ok && bounds_ok && sequence_ok;
        end
    end
    always_ff @(posedge clk) begin
        permit_s<={permit_s[0],permit}; fault_s<={fault_s[0],fault_n};
        if(rst) begin
            pwm_phase<=0; active_duty<=0; current_raw<=0; target<=0;
            enabled<=0; faults<=0; sample_ready<=0; sample_strobe<=0;
            last_sequence<=0; sequence_seen<=0; watchdog<=0;
            pending_command<=0; status<=0; status_payload<=0;
            status_crc_start<=0; status_phase<=0;
        end else begin
            sample_strobe<=0; status_crc_start<=0;
            if(command_valid) pending_command<=command;
            // Coherent telemetry every 64 clocks (<3 us), independent of SPI CS.
            status_phase<=status_phase+1'b1;
            if(status_phase==0) begin status_payload<=status_body; status_crc_start<=1; end
            if(status_crc_done) status<={status_payload,status_crc};
            if(pwm_phase==1199) begin
                pwm_phase<=0; active_duty<=control_enable?requested_duty:12'd0;
            end else pwm_phase<=pwm_phase+1'b1;
            if(!control_enable) active_duty<=0;
            if(watchdog<WATCHDOG_CYCLES) watchdog<=watchdog+1'b1;
            if(fresh_command) begin
                watchdog<=0; sequence_seen<=1; last_sequence<=pending_command[55:48];
                current_raw<=pending_command[43:32]; target<=pending_command[27:16];
                sample_ready<=1; sample_strobe<=1;
                if(!pending_command[56]) enabled<=0;
                else if(COMMISSIONED!=0 && faults==0 && permit_s[1] && fault_s[1]
                        && pending_command[47:32]<MAX_CURRENT_COUNTS) enabled<=1;
                // Clear only on a disabled packet with a new safe current measurement.
                if(pending_command[57] && !pending_command[56] && fault_s[1]
                   && pending_command[47:32]<MAX_CURRENT_COUNTS) faults<=0;
                if(pending_command[47:32]>=MAX_CURRENT_COUNTS) begin faults[1]<=1; enabled<=0; end
            end
            // External gating is asynchronous; these bits retain the cause.
            if(!fault_s[1]) begin faults[0]<=1; enabled<=0; end
            if(enabled && watchdog>=WATCHDOG_CYCLES-1 && !fresh_command) begin
                faults[2]<=1; enabled<=0; sample_ready<=0;
            end
            if(!permit_s[1]) enabled<=0;
        end
    end
endmodule
