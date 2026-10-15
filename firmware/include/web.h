#ifndef LEV_WEB_H
#define LEV_WEB_H
#include <stddef.h>
#include "control.h"
/* Entire line /REQ:<route>\n; exact routes, never substring matches. */
bool lev_web_request(char *line, lev_control_t *s, const lev_config_t *c,
                     const lev_telemetry_t *t, bool *clear);
size_t lev_web_render(char *out,size_t cap,const lev_control_t *s,
                      const lev_telemetry_t *t,const lev_config_t *c);
#endif
