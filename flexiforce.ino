const int ff_pin = A0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  int flexiForceReading = analogRead(ff_pin);
  Serial.println(flexiForceReading);

//  if(Serial.available()){ // only send data back if data has been sent
//    char inByte = Serial.read(); // read the incoming data
//  }
  
  delay(100);

}

