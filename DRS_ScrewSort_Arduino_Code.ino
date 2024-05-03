#include <Servo.h>
Servo motor;
int data = 90;

void setup() {
  Serial.begin(9600);
  motor.attach(9);
  
}

void loop() {
  if (Serial.available() > 0) {
    data = Serial.read();
  }
  motor.write(data);
}
