// Kód je založen na :
// AS5600 magnetic position encoder; autor: Curious Scientist; dostupné z: https://curiousscientist.tech/blog/as5600-magnetic-position-encoder
// ADXL345 accelerometer; autor: Dejan; dostupné z: https://howtomechatronics.com/tutorials/arduino/how-to-track-orientation-with-arduino-and-adxl345-accelerometer/
#include <Arduino.h>
#include <Wire.h>

// AS5600
#define AS5600 0x36
int magnetStatus = 0;
int lowbyte;
word highbyte;
int rawAngle;
float degAngle;

int quadrantNumber, previousquadrantNumber;
float numberofTurns = 0;
float Angle_corrected = 0;
float startAngle = 0;
float totalAngle = 0;

// GY-291
#define ADXL345 (0x53)
float X_val, Y_val, Z_val;

void setup()
{
  Serial.begin(9600);
  Wire.begin();
  Wire.setClock(800000L);

  Wire.beginTransmission(ADXL345);
  Wire.write(0x2D);
  Wire.write(8);
  Wire.endTransmission();
  delay(10);

  checkMagnet();
  ReadRawAngle();
  startAngle = degAngle;
}

void loop()
{
  Accelerometer();
  ReadRawAngle();
  correctAngle();
  Angle_total();
}

void Accelerometer()
{
  Wire.beginTransmission(ADXL345);
  Wire.write(0x32);
  Wire.endTransmission(false);
  Wire.requestFrom(ADXL345, 6, true);
  X_val = (Wire.read() | Wire.read() << 8);
  X_val = X_val / 256;
  Y_val = (Wire.read() | Wire.read() << 8);
  Y_val = Y_val / 256;
  Z_val = (Wire.read() | Wire.read() << 8);
  Z_val = Z_val / 256;

  Serial.print("X: ");
  Serial.print(X_val);
  Serial.print(" Y: ");
  Serial.print(Y_val);
  Serial.print(" Z: ");
  Serial.println(Z_val);
}

void ReadRawAngle()
{
  Wire.beginTransmission(AS5600);
  Wire.write(0x0D);
  Wire.endTransmission();
  Wire.requestFrom(AS5600, 1);

  while (Wire.available() == 0)
    ;
  lowbyte = Wire.read();

  Wire.beginTransmission(AS5600);
  Wire.write(0x0C);
  Wire.endTransmission();
  Wire.requestFrom(AS5600, 1);

  while (Wire.available() == 0)
    ;
  highbyte = Wire.read();

  highbyte = highbyte << 8;
  rawAngle = highbyte | lowbyte;

  degAngle = rawAngle * 0.087890625;
}

void correctAngle()
{
  Angle_corrected = degAngle - startAngle;
  if (Angle_corrected < 0)
  {
    Angle_corrected = 360 + Angle_corrected;
  }
}

void Angle_total()
{
  if (Angle_corrected >= 0 && Angle_corrected <= 90)
  {
    quadrantNumber = 1;
  }

  if (Angle_corrected > 90 && Angle_corrected <= 180)
  {
    quadrantNumber = 2;
  }

  if (Angle_corrected > 180 && Angle_corrected <= 270)
  {
    quadrantNumber = 3;
  }

  if (Angle_corrected > 270 && Angle_corrected < 360)
  {
    quadrantNumber = 4;
  }

  if (quadrantNumber != previousquadrantNumber)
  {
    if (quadrantNumber == 1 && previousquadrantNumber == 4)
    {
      numberofTurns++;
    }

    if (quadrantNumber == 4 && previousquadrantNumber == 1)
    {
      numberofTurns--;
    }

    previousquadrantNumber = quadrantNumber;
  }

  totalAngle = 360 * numberofTurns + Angle_corrected;
//Serial.print("Total angle: ");//
//Serial.println(totalAngle, 2);
}
void checkMagnet()
{
  while ((magnetStatus & 32) != 32)
  {
    magnetStatus = 0;

    Wire.beginTransmission(AS5600);
    Wire.write(0x0B);
    Wire.endTransmission();
    Wire.requestFrom(AS5600, 1);

    while (Wire.available() == 0)
      ;
    magnetStatus = Wire.read();

    Serial.print("Magnet status: ");
    Serial.println(magnetStatus, BIN);
  }

  Serial.println("Magnet detected");
  delay(1000);
}