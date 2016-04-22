#include <Servo.h>
Servo s;
void setup() {
  Serial.begin(9600);
  s.attach(9);
  pinMode(11, OUTPUT);
  pinMode(12, OUTPUT);
  digitalWrite(11, HIGH);
  digitalWrite(12, HIGH);
}

void loop() {
//  while (!Serial.available()) {
//  }
//  int servo = Serial.read();
//  Serial.write(servo);
//  s.write(servo);
  
  while (!Serial.available()) {
  }
  int motors = Serial.read();
  if (motors > '0') {
    digitalWrite(11, LOW);
    digitalWrite(12, LOW);
    s.write(180);
  } else {
    digitalWrite(11, HIGH);
    digitalWrite(12, HIGH);
    s.write(0);
  }
  Serial.write(motors);
 
  delay(10);
}
