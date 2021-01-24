/*
GNU GPL v3.0+ 
Copyright 2021 Forrest Sheng Bao 

For details of how the code works, or the wiring, 
please watch this YouTube video

https://www.youtube.com/watch?v=sTbF03DOTrQ

*/

int digiPin = 2;   int ADCPin = 1;   // same pin, but different numbering 

// The ADC pin I used is A0. It is muxed as a digital pin as well. 
// So I set the pin as digital output and pulled it to charge the RC circuit. 
// Then set it as ADC input to measure the discharging on the C. 

int discharge_time = 50; // read ADC after a  discharge period 

void setup() {
  Serial.begin(9600); 
}

void charge(){
  // charge to digital pin
  pinMode(digiPin, OUTPUT); 
  digitalWrite(digiPin, HIGH);
  delay(100); // almost instant
  }

int discharge(){
  // measure discharge at an ADC pin that was previous charged 

  digitalWrite(digiPin, LOW); // DO I need this? 
  pinMode(digiPin, INPUT); // DO I NEED This? 

  delay(discharge_time); // give it a longer time to discharge 
  
  return analogRead(ADCPin);
  }

void loop() {
  charge();
  int local_reading = discharge();
  Serial.println(local_reading); 
}
