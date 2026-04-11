// use commands below to run in separate environment from 'src' for different firmward loading on ESP32
// pio run -e data_collect -t upload
// pio device monitor 
#include <Arduino.h>

#define PPG_PIN 4

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
}

void loop() {
  int raw = analogRead(PPG_PIN);
  Serial.println(raw);
  delay(10);  // ~100 Hz sampling rate
}