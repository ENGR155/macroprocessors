#include "board.h"
#include "web.h"
static lev_runtime_t app;
static char page[3072],line[64];
static void on_adc(const lev_adc_t *adc,uint32_t now,uint8_t tx[LEV_FRAME_BYTES]) {
    lev_runtime_sample(&app,adc,now,tx);
    board_permit(app.control.active && app.link_ok);
}
static void on_reply(const uint8_t rx[LEV_FRAME_BYTES],bool ok) {
    lev_runtime_feedback(&app,rx,ok);
    board_permit(app.control.active && app.link_ok);
}
int main(void) {
    board_init(); lev_runtime_init(&app,&lev_config);
    board_start_sampling(lev_config.hall_sensors,on_adc,on_reply);
    unsigned used=0; bool overflow=false;
    size_t page_size=0,page_pos=0;
    for (;;) {
        char ch;
        if (board_rx(&ch)) {
            if (ch=='\n') {
                line[used]=0;
                uint32_t lock=board_lock();
                if (!overflow && lev_web_request(line,&app.control,&lev_config,&app.telemetry,&app.clear))
                    app.last_request_us=board_us();
                if (!app.control.active) board_permit(false);
                lev_control_t control=app.control; lev_telemetry_t telemetry=app.telemetry;
                board_unlock(lock);
                used=0; overflow=false;
                /* DMA/interrupt control continues while HTML is formatted/transmitted. */
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
