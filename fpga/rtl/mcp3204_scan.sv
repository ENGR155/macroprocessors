// Three independent 24-clock, mode-0 MCP3204 conversions. CH0=current,
// CH1=Hall primary, CH2=Hall reference. 0.857 MHz SCK, >= 1 us CS high.
// Trigger is periodic and phase locked to PWM; channels are NOT simultaneous.
module mcp3204_scan (
    input logic clk, rst, start, miso,
    output logic cs_n, sck, mosi,
    output logic [11:0] current_raw, hall1_raw, hall2_raw,
    output logic done, busy
);
    (* ASYNC_REG="TRUE" *) logic [1:0] md;
    logic [23:0] tx;
    logic [11:0] rx;
    logic sample_tick;
    logic [5:0] divider, gap;
    logic [4:0] bit_index;
    logic [1:0] channel;
    typedef enum logic [1:0] {IDLE,TRANSFER,GAP} state_t;
    state_t state;
    // Only the last 12 bits matter. Avoid clearing the receive shift register
    // at every channel boundary, which otherwise puts the gap decoder on its enable path.
    always_ff @(posedge clk) begin
        if(rst) begin sample_tick<=0; rx<=0; end
        else begin
            sample_tick<=state==TRANSFER && divider==12 && !sck;
            if(sample_tick) rx<={rx[10:0],md[1]};
        end
    end
    always_ff @(posedge clk) begin
        md<={md[0],miso}; done<=0;
        if (rst) begin
            state<=IDLE; cs_n<=1; sck<=0; mosi<=0; busy<=0;
            divider<=0; gap<=0; bit_index<=0; channel<=0; tx<=0;
            current_raw<=0; hall1_raw<=0; hall2_raw<=0;
        end else case(state)
            IDLE: if(start) begin
                channel<=0; tx<=24'h060000; bit_index<=0;
                divider<=0; mosi<=0; sck<=0; cs_n<=0; busy<=1; state<=TRANSFER;
            end
            TRANSFER: begin
                if(divider==13) begin
                    divider<=0; sck<=~sck;
                    if(sck && bit_index==23) begin
                        cs_n<=1; gap<=0; state<=GAP;
                        case(channel)
                            0: current_raw<=rx[11:0];
                            1: hall1_raw<=rx[11:0];
                            2: hall2_raw<=rx[11:0];
                            default: ;
                        endcase
                    end else if(sck) begin
                        bit_index<=bit_index+1'b1;
                        tx<={tx[22:0],1'b0}; mosi<=tx[22];
                    end
                end else divider<=divider+1'b1;
            end
            GAP: if(gap==23) begin
                if(channel==2) begin done<=1; busy<=0; state<=IDLE; end
                else begin
                    channel<=channel+1'b1;
                    // 0x060000 | ((next channel) << 14)
                    tx<=24'h060000|(({22'b0,channel}+24'd1)<<14);
                    mosi<=0; bit_index<=0; divider<=0;
                    cs_n<=0; state<=TRANSFER;
                end
            end else gap<=gap+1'b1;
            default: state<=IDLE;
        endcase
    end
endmodule
