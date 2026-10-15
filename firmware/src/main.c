#include "board.h"
#include "web.h"
#include <math.h>
static lev_control_t control;
static lev_telemetry_t telemetry;
static char page[3072],line[64];
int main(void) {
    board_init(); lev_control_init(&control,&lev_config);
    uint32_t tick=board_ms(),last_page=tick,last_sample=tick;
    uint16_t seq=0,previous_sample=0;
    unsigned used=0,arm_ticks=0; bool overflow=false,clear=false,link_ok=false;
    size_t page_size=0,page_pos=0;
    for (;;) {
        uint32_t now=board_ms();
        if (now!=tick) {
            uint32_t dt=now-tick; tick=now;
            if (dt!=1 || (control.active && now-last_page>5000)) lev_stop(&control,true);
            uint8_t tx[16],rx[16];
            /* Last tick's result is sent; the explicit one-tick delay is in the timing budget. */
            float target=control.output_a*lev_config.counts_per_amp+lev_config.current_zero;
            if (!isfinite(target) || target<0) target=0;
            if (target>lev_config.hard_limit_counts) target=lev_config.hard_limit_counts;
            board_permit(control.active && link_ok);
            lev_pack(tx,++seq,control.active && link_ok,clear,(uint16_t)target,
                     lev_config.current_kp_q8,lev_config.current_ki_q8,lev_config.hard_limit_counts);
            clear=false;
            bool ok=board_exchange(tx,rx) && lev_unpack(rx,&telemetry);
            if (ok && (telemetry.flags&1)) {
                if (telemetry.sample_id!=previous_sample) {
                    previous_sample=telemetry.sample_id; last_sample=now;
                }
                ok=now-last_sample<3;
            } else ok=false;
            link_ok=ok;
            if (!ok) lev_stop(&control,true);
            else (void)lev_control_step(&control,&lev_config,&telemetry,dt*0.001f);
            if (control.active) {
                if(arm_ticks<5) arm_ticks++;
                else if(!(telemetry.flags&2)) lev_stop(&control,true);
            } else arm_ticks=0;
            if (!control.active) board_permit(false);
        }
        char ch;
        if (board_rx(&ch)) {
            if (ch=='\n') {
                line[used]=0;
                if (!overflow && lev_web_request(line,&control,&lev_config,&telemetry,&clear))
                    last_page=board_ms();
                used=0; overflow=false;
                /* Drop a refresh arriving during a response; never overwrite in-flight HTML. */
                if (page_pos==page_size) {
                    page_size=lev_web_render(page,sizeof(page),&control,&telemetry,&lev_config);
                    page_pos=0;
                }
            } else if (ch!='\r') {
                if (used+1<sizeof(line)) line[used++]=ch; else overflow=true;
            }
        }
        if (page_pos<page_size && board_tx(page[page_pos])) page_pos++;
    }
}
