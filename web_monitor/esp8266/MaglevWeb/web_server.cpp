#include <Arduino.h>
#include <ESP8266WebServer.h>
#include <ESP8266WiFi.h>
#include "dashboard.h"

namespace {
constexpr uint32_t baud = 125000;
constexpr uint32_t replyTimeoutMs = 180;
constexpr char ssid[] = "MicroPEs-Maglev";
constexpr char password[] = "MicroPEs155";
constexpr char commandHeader[] = "X-Maglev-Command";

ESP8266WebServer server(80);
uint32_t nextRequestId;
char uartLine[768];

void sendJson(int status, const char *body) {
    server.sendHeader("Cache-Control", "no-store");
    server.send(status, "application/json", String(body));
}

// Each request gets its own ID so a late UART response cannot acknowledge
// another request. A start marker and newline let either board resynchronize.
void exchange(const char *command) {
    char prefix[20];
    const size_t prefixLength = snprintf(prefix, sizeof(prefix), "@M1 %lu ",
                                         static_cast<unsigned long>(++nextRequestId));
    Serial.print(prefix);
    Serial.print(command);
    Serial.write('\n');

    const uint32_t started = millis();
    size_t length = 0;
    while (static_cast<uint32_t>(millis() - started) < replyTimeoutMs) {
        while (Serial.available() && static_cast<uint32_t>(millis() - started) < replyTimeoutMs) {
            const char byte = static_cast<char>(Serial.read());
            if (byte == '@') {
                length = 0;
            } else if (length == 0) {
                continue;
            }
            if (byte == '\n') {
                uartLine[length] = '\0';
                if (length > prefixLength + 1 &&
                    memcmp(uartLine, prefix, prefixLength) == 0 &&
                    uartLine[prefixLength] == '{' && uartLine[length - 1] == '}') {
                    sendJson(200, uartLine + prefixLength);
                    return;
                }
                length = 0;
            } else if (length < sizeof(uartLine) - 1 && byte >= 32 && byte <= 126) {
                uartLine[length++] = byte;
            } else {
                length = 0;
            }
        }
        delay(1);
    }
    sendJson(504, R"({"error":"STM32 UART response timed out"})");
}

bool isWireNumber(const String &value, size_t limit, bool decimal) {
    if (value.length() == 0 || value.length() > limit) return false;
    for (unsigned i = 0; i < value.length(); ++i) {
        char byte = value[i];
        if ((byte < '0' || byte > '9') && !(decimal && byte == '.')) return false;
    }
    return true;
}

void handlePid() {
    // This header is set by the dashboard's same-origin fetch. Ordinary
    // navigation, image requests and HTML form submissions cannot set it.
    if (server.header(commandHeader) != "1") {
        sendJson(403, R"({"error":"Missing dashboard command header"})");
        return;
    }
    const String kp = server.arg("kp");
    const String ki = server.arg("ki");
    const String kd = server.arg("kd");
    const String revision = server.arg("revision");
    if (!isWireNumber(kp, 8, true) ||
        !isWireNumber(ki, 8, true) || !isWireNumber(kd, 8, true) ||
        !isWireNumber(revision, 10, false)) {
        sendJson(400, R"({"error":"Expected kp, ki, kd and revision"})");
        return;
    }

    // The STM32 validates the full numeric grammar and controller limits.
    char command[44];
    snprintf(command, sizeof(command), "PID %s %s %s %s",
             kp.c_str(), ki.c_str(), kd.c_str(), revision.c_str());
    exchange(command);
}
}  // namespace

void setup() {
    Serial.setRxBufferSize(sizeof(uartLine));
    Serial.begin(baud, SERIAL_8N1);
    Serial.setDebugOutput(false);
    nextRequestId = micros();

    WiFi.persistent(false);
    WiFi.mode(WIFI_AP);
    WiFi.softAP(ssid, password);

    server.collectHeaders(commandHeader);
    server.on("/", HTTP_GET, [] {
        server.sendHeader("Cache-Control", "no-store");
        server.send_P(200, PSTR("text/html; charset=utf-8"), maglev_dashboard,
                      sizeof(maglev_dashboard) - 1);
    });
    server.on("/api/status", HTTP_GET, [] { exchange("GET"); });
    server.on("/api/pid", HTTP_POST, handlePid);
    server.onNotFound([] { sendJson(404, R"({"error":"Unknown route"})"); });
    server.begin();
}

void loop() {
    server.handleClient();
}
