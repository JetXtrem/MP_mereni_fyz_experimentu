// Kód je založen na :
// AS5600 magnetic position encoder; autor: Curious Scientist; dostupné z: https://curiousscientist.tech/blog/as5600-magnetic-position-encoder
// ADXL345 accelerometer; autor: Dejan; dostupné z: https://howtomechatronics.com/tutorials/arduino/how-to-track-orientation-with-arduino-and-adxl345-accelerometer/

// Knihovny
#include <Wire.h>
#include <SPI.h>
#include <SD.h>

// SD
File dataFile;
const int chipSelect = 10;

// AS5600
const int AS5600 = 0x36;
int magnetStatus = 0;
int lowbyte;
word highbyte;
int rawAngle;
float degAngle;
const float degConst = 0.087890625;
float numberOfTurns = 0;
float AngleCorrected = 0;
float startAngle = 0;
float totalAngle = 0;
float previousDegAngle = 0;

// ADXL345
const int ADXL345 = 0x53;
float X_val, Y_val, Z_val;

void setup()
{
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  pinMode(5, INPUT);

  if (!SD.begin(chipSelect))
  {
  Serial.println("CHYBA: Inicializace SD selhala!");
  while (true);
  }
  Serial.println("SD inicializace úspěšná!");
  SD.remove("data.csv");

  dataFile = SD.open("data.csv", FILE_WRITE);
  if (dataFile) {
  Serial.println("Soubor data.csv vytvořen.");
  dataFile.println("currentTime,totalAngle,Y_val,Z_val");
  dataFile.close();
  } else {
  Serial.println("Chyba: Nelze vytvořit data.csv");
  }
  delay(50);

  Wire.begin();
  Wire.setClock(800000L);
  Wire.beginTransmission(ADXL345);
  Wire.write(0x2D);
  Wire.write(8);
  Wire.endTransmission();
  delay(10);

  Wire.beginTransmission(ADXL345);
  Wire.write(0x20);
  Wire.write(1);
  Wire.endTransmission();
  delay(10);

  checkMagnet();
  ReadRawAngle();
  startAngle = degAngle;
}

void loop()
{
  while (digitalRead(5) == HIGH) {
    ReadRawAngle();
    correctAngle();
    Angle_total();
    Accelerometer();
    unsigned long currentTime = millis();

    Serial.print(currentTime);
    Serial.print(",");
    Serial.print(totalAngle);
    Serial.print(",");
    Serial.print(Y_val);
    Serial.print(",");
    Serial.println(Z_val);
    delay(5);
    dataFile = SD.open("data.csv", FILE_WRITE);
    if (dataFile)
    {
      dataFile.print(currentTime);
      dataFile.print(",");
      dataFile.print(totalAngle);
      dataFile.print(",");
      dataFile.print(Y_val);
      dataFile.print(",");
      dataFile.println(Z_val);
      dataFile.close();
    }
    else {
    Serial.println("Chyba: Nelze otevřít data.csv");
    }
  }
}

void Accelerometer()
{
  Wire.beginTransmission(ADXL345);
  Wire.write(0x32);
  Wire.endTransmission(false);
  Wire.requestFrom(ADXL345, 6, true);
  X_val = (Wire.read() | Wire.read() << 8);
  Y_val = (Wire.read() | Wire.read() << 8);
  Y_val = Y_val / 256;
  Z_val = (Wire.read() | Wire.read() << 8);
  Z_val = Z_val / 256;
}

void ReadRawAngle()
{
  Wire.beginTransmission(AS5600);
  Wire.write(0x0D);
  Wire.endTransmission();
  Wire.requestFrom(AS5600, 1);

  while (Wire.available() == 0);
  lowbyte = Wire.read();

  Wire.beginTransmission(AS5600);
  Wire.write(0x0C);
  Wire.endTransmission();
  Wire.requestFrom(AS5600, 1);

  while (Wire.available() == 0);
  highbyte = Wire.read();

  highbyte = highbyte << 8;
  rawAngle = highbyte | lowbyte;

  degAngle = rawAngle * degConst;
}

void correctAngle()
{
  AngleCorrected = degAngle - startAngle;
  if (AngleCorrected < 0)
  {
    AngleCorrected = AngleCorrected + 360;
  }
}

void Angle_total()
{
  float RotationChange = AngleCorrected - previousDegAngle;
  if (RotationChange > 180)
  {
    numberOfTurns--;
  }
  else if (RotationChange < -180)
  {
    numberOfTurns++;
  }

  totalAngle = (360 * numberOfTurns) + AngleCorrected;
  previousDegAngle = AngleCorrected;
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

    while (Wire.available() == 0);
    magnetStatus = Wire.read();

    Serial.print("Magnet status: ");
    Serial.println(magnetStatus, BIN);
  }

  Serial.println("Magnet detected");
  delay(1000);
}