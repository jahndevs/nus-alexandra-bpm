#include <WiFi.h>
#include <HTTPClient.h>

#define PPG_PIN 4
#define STR_HELPER(x) #x
#define STR(x) STR_HELPER(x)

const char *ssid = WIFI_SSID;
const char *password = WIFI_PASSWORD;
const char *backendURL = "http://" BACKEND_IP ":" STR(BACKEND_PORT) "/api/ppg";

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);

  delay(10);

  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  int raw = analogRead(PPG_PIN);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(backendURL);
    http.addHeader("Content-Type", "application/json");

    String payload = "{\"raw\":" + String(raw) + "}";
    int responseCode = http.POST(payload);

    if (responseCode > 0) {
      Serial.print("POST OK: ");
      Serial.println(responseCode);
    } else {
      Serial.print("POST failed: ");
      Serial.println(http.errorToString(responseCode));
    }

    http.end();
  }

  delay(50);
}
