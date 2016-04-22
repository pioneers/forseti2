#include <Servo.h>
Servo s;
void setup() {
  Serial.begin(9600);
  s.attach(9);
}

void loop() {
  if (Serial.available()) {
    int x = Serial.read();
    Serial.write(x);
    s.write(x);
  }
  delay(10);
}
