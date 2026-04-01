#include <Arduino.h>
#define PPG_PIN 4
#define SAMPLE_RATE 100

int maxVal = 0;
int minVal = 4095;
int threshold = 2048;
int lastVal = 0;
int beatCount = 0;
unsigned long lastCalculatedTime = 0;
float bpm = 0;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  Serial.println("PPG Sensor Ready");
}

void loop() {
  int rawValue = analogRead(PPG_PIN);

  Serial.println(rawValue);
}
