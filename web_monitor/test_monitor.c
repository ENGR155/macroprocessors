/* Portable protocol tests: cc -std=c11 -Wall -Wextra -Werror
 * web_monitor/test_monitor.c -o test_monitor */
#define MAGLEV_MONITOR_TEST
#include "../mcu/src/main.c"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static maglev_monitor_t m;
static char output[16384];
static unsigned assertions, calls;
static uint32_t now_ms = 1000;
static bool accept = true;
static maglev_gains_t actual;
/* A named successful endpoint lets emSim distinguish success from a fault. */
void maglev_tests_pass(void) {}
#define CHECK(x) do { assertions++; if (!(x)) { printf("FAIL line %d: %s\n", __LINE__, #x); exit(1); } } while (0)
static bool apply(void *context, const maglev_gains_t *next) {
    calls++; if (!accept) return false;
    *(maglev_gains_t *)context = *next; return true;
}
static const char *drain(void) {
    size_t n = 0;
    while (maglev_monitor_tx_pending(&m)) {
        CHECK(n + 1 < sizeof(output));
        output[n++] = m.reply[m.tx_pos++];
    }
    output[n] = 0;
    if (n) {
        CHECK(!strncmp(output, "@M1 ", 4));
        CHECK(n >= 3 && !strcmp(output + n - 2, "}\n"));
    }
    return output;
}
static const char *request(const char *line) {
    while (*line) maglev_monitor_feed(&m, *line++, now_ms);
    return drain();
}
int main(void) {
    maglev_monitor_init(&m, false);
    CHECK(strstr(request("@M1 41 GET\n"), "@M1 41 {\"result\":\"ok\""));
    CHECK(strstr(output, "\"valid\":false"));
    record_fpga_reading(&m, 400, 975);
    CHECK(strstr(request("@M1 42 GET\n"), "\"age_ms\":25"));
    char expected[48];
    snprintf(expected, sizeof(expected), "\"position_um\":%ld",
             (long)(400 * MAGLEV_POSITION_UM_PER_WORD + MAGLEV_POSITION_OFFSET_UM));
    CHECK(strstr(output, expected));
    CHECK(strstr(output, "\"raw\":400"));
    CHECK(fpga_word == 400 && fpga_average == 1600 && read_count == 1);
    const char *pending = "@M1 57 GET\n";
    while (*pending) maglev_monitor_feed(&m, *pending++, 1000);
    record_fpga_reading(&m, 420, 1001);
    CHECK(strstr(drain(), "\"raw\":400"));   /* Snapshot stays coherent during TX. */
    CHECK(fpga_word == 420 && fpga_average == 1640 && read_count == 2);
    record_fpga_reading(&m, 900, 1002);
    now_ms = 1003;
    CHECK(strstr(request("@M1 58 GET\n"), "\"raw\":900"));
    CHECK(fpga_average == 1640 && rejected_count == 1);
    CHECK(strstr(request("@M1 43 PID 1 2 3 0\n"), "pid_unavailable"));
    CHECK(calls == 0);
    actual = (maglev_gains_t){1000, 2000, 0};
    maglev_monitor_pid(&m, &actual, apply, &actual);
    CHECK(m.pid_revision == 1);
    CHECK(strstr(request("@M1 44 PID 1.234 0 0.001 1\n"), "applied"));
    CHECK(actual.kp_milli == 1234 && actual.ki_milli == 0 && actual.kd_milli == 1);
    CHECK(calls == 1 && m.pid_revision == 2);
    CHECK(strstr(request("@M1 45 PID 9 9 9 1\n"), "conflict"));
    CHECK(calls == 1 && actual.kp_milli == 1234);
    const char *bad[] = {
        "@M1 46 PID -1 2 3 2\n", "@M1 46 PID 1e2 2 3 2\n",
        "@M1 46 PID 1.0001 2 3 2\n", "@M1 46 PID 1000.001 2 3 2\n",
        "@M1 46 PID 1001 2 3 2\n", "@M1 46 PID 1 2 3 4294967296\n",
        "@M1 46 PID 1 2 3 2junk\n", "@M1 46 PID 1 2 3 2 \n",
        "@M1 46 PID .1 2 3 2\n", "@M1 46 PID 1. 2 3 2\n",
        "@M1 46 PID 1 2 2\n", "@M1 46 PID %31 2 3 2\n"
    };
    for (unsigned i = 0; i < sizeof(bad)/sizeof(bad[0]); i++) {
        CHECK(strstr(request(bad[i]), "invalid_gains")); CHECK(calls == 1);
    }
    accept = false;
    CHECK(strstr(request("@M1 47 PID 2 2 2 2\n"), "controller_rejected"));
    CHECK(actual.kp_milli == 1234 && m.pid_revision == 2);
    accept = true;
    CHECK(strstr(request("@M1 48 PID 1000 1000.000 0 2\n"), "applied"));
    CHECK(actual.kp_milli == 1000000 && actual.ki_milli == 1000000);
    unsigned before = calls;
    CHECK(!*request("junk/REQ:pid/1/2/3/3\n"));
    CHECK(!*request("@M1 4294967296 PID 1 2 3 3\n"));
    CHECK(strstr(request("@M1 49 PID 1 2 3 3?x\n"), "invalid_gains"));
    CHECK(!*request("@M1 50 PID 1 2 3 3"));
    CHECK(strstr(request("@M1 51 GET\n"), "@M1 51 "));  /* restart without a newline */
    CHECK(calls == before);
    CHECK(!*request("@M1 52 PID 1 "));
    maglev_monitor_feed(&m, '\0', now_ms);
    CHECK(!*request("2 3 3\n"));
    CHECK(calls == before);
    for (unsigned i = 0; i < 200; i++) maglev_monitor_feed(&m, 'a', now_ms);
    CHECK(!*request("\n"));
    CHECK(strstr(request("@M1 53 GET\n"), "\"result\":\"ok\""));
    const char *line = "@M1 54 GET\n";
    while (*line) maglev_monitor_feed(&m, *line++, now_ms);
    line = "@M1 55 PID 1 2 3 3\n";
    while (*line) maglev_monitor_feed(&m, *line++, now_ms);
    CHECK(calls == before); drain(); /* request while TX busy cannot mutate PID */
    actual.kp_milli = 5000; maglev_monitor_pid(&m, &actual, NULL, NULL);
    CHECK(m.pid_revision == 4);
    CHECK(strstr(request("@M1 56 GET\n"), "\"pid_writable\":false"));
    m.sequence = UINT32_MAX; m.sample_ms = 999; m.position_um = INT32_MIN;
    m.failures = m.uart_errors = m.rejected_requests = UINT32_MAX;
    CHECK(strstr(request("@M1 4294967295 GET\n"), "@M1 4294967295 "));
    CHECK(strstr(output, "\"seq\":4294967295"));
    CHECK(strstr(output, "-2147483648"));
    printf("PASS monitor protocol: %u assertions\n", assertions);
    maglev_tests_pass();
    return 0;
}
