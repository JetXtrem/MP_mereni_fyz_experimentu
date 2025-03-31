// Kód je založen na :
// AS5600 magnetic position encoder; autor: Curious Scientist; dostupné z: https://curiousscientist.tech/blog/as5600-magnetic-position-encoder
// ADXL345 accelerometer; autor: Dejan; dostupné z: https://howtomechatronics.com/tutorials/arduino/how-to-track-orientation-with-arduino-and-adxl345-accelerometer/

// Knihovny
#include <Wire.h>
#include <SPI.h>
#include <SD.h>

// SD
File dataFile;             // Vytvoření objektu pro zápis do souboru
const int chipSelect = 10; // Pin pro zahájení komunikace s SD čtěčkou
const char *fileName = "data.csv";

// AS5600 (magnetický enkodér)
const int AS5600 = 0x36; // I2C adresa AS5600
const float degConst = 0.087890625;
/* 12-bitový výstup AS5600 => 4096 hodnot (2^12) na úplný kruh (360°)
=> 360°/4096 = 0.087890625° */
int magnetStatus = 0;
int lowByte;   // 8-bitový integer pro uložení výstupu z AS5600
word highByte; // 16-bitový unsigned integer (word) pro uložení výstupu z AS5600
int rawAngle;
float degAngle;
float numberOfTurns = 0;
float angleCorrected = 0;
float startAngle = 0;
float totalAngle = 0;
float previousDegAngle = 0;

// ADXL345 (akcelerometr)
const int ADXL345 = 0x53; // I2C adresa ADXL345
float X_val, Y_val, Z_val;

const int switchPin = 5; // Pin vypínače

void setup()
{
  /* Serial.begin(115200); */
  pinMode(switchPin, INPUT); // Deklarace pinu vypínače pro zahájení měření

  // Inicializace SD karty
  if (!SD.begin(chipSelect))
  {
    while (true)
    {
      Serial.println("CHYBA: Inicializace SD selhala!");
      delay(1000);
    }
  }
  Serial.println("SD inicializace úspěšná");

  SD.remove(fileName); // Odstranění starého souboru, pokud existuje

  // Vytvoření nového souboru pro zápis dat
  dataFile = SD.open(fileName, FILE_WRITE);
  if (dataFile)
  {
    Serial.println("Soubor data.csv vytvořen");
    dataFile.println("currentTime,totalAngle,Y_val,Z_val");
    dataFile.close();
  }
  else
  {
    Serial.println("Chyba: Nelze vytvořit data.csv!");
  }
  delay(50);

  // Zahájení I2C komunikace
  Wire.begin();
  Wire.setClock(800000L); // Nastavení rychlosti I2C na 800kHz

  // Inicializace ADXL345
  Wire.beginTransmission(ADXL345);
  Wire.write(0x2D); // Zápis do registru POWER_CTL
  Wire.write(8);    // Aktivace měření (nastaví bit D3 = 1)
  Wire.endTransmission();
  delay(10);

  // Kalibrace osy Z akcelerometru
  Wire.beginTransmission(ADXL345);
  Wire.write(0x20); // Zápis do registru OFSZ
  Wire.write(1);    // Zápis kalibrační hodnoty
  Wire.endTransmission();
  delay(10);

  // Inicializace AS5600
  checkMagnet();
  ReadRawAngle();
  startAngle = degAngle;
}

void loop()
{
  dataFile = SD.open(fileName, FILE_WRITE); // Otevření souboru pro zápis dat

  // Smyčka měření
  while (digitalRead(5) == HIGH)
  {
    // Získání dat z AS5600 a ADXL345
    ReadRawAngle();
    correctAngle();
    Angle_total();
    Accelerometer();

    unsigned long currentTime = millis(); // Získání času od spuštění programu v milisekundách

    // Debugging:
    /* Serial.print(currentTime);
    Serial.print(",");
    Serial.print(totalAngle);
    Serial.print(",");
    Serial.print(Y_val);
    Serial.print(",");
    Serial.println(Z_val);
    delay(5); */

    // Zápis dat do souboru
    if (dataFile)
    {
      dataFile.print(currentTime);
      dataFile.print(",");
      dataFile.print(totalAngle);
      dataFile.print(",");
      dataFile.print(Y_val);
      dataFile.print(",");
      dataFile.println(Z_val);
      dataFile.flush();
    }
    else
    {
      Serial.println("Chyba: Nelze otevřít data.csv!");
    }
  }
  dataFile.close(); // Zavření souboru po ukončení měření
}

void Accelerometer()
{
  // Získání dat z akcelerometru
  Wire.beginTransmission(ADXL345);
  Wire.write(0x32); // Zápis do registru DATAX0 pro čtení
  Wire.endTransmission(false);
  Wire.requestFrom(ADXL345, 6, true);     // Požadavek na 6 registrů (2 pro každou osu)
  X_val = Wire.read() | Wire.read() << 8; // Čtení dat osy X, která není dál potřeba (operace OR a posun o 8 bitů pro sloučení dvou bajtů)
  Y_val = Wire.read() | Wire.read() << 8; // Obdobně pro osu Y (děleno 256 (2^8) pro převod na G jednotky)
  Y_val = Y_val / 256;
  Z_val = Wire.read() | Wire.read() << 8; // Stejně i pro osu Z
  Z_val = Z_val / 256;
}

void ReadRawAngle()
{
  Wire.beginTransmission(AS5600); // Zahájení komunikace s AS5600
  Wire.write(0x0D);               // Zápis příkazu pro čtení úhlu (nižší bajt)
  Wire.endTransmission();         // Ukončení komunikace
  Wire.requestFrom(AS5600, 1);    // Požadavek na 1 bajt dat

  while (Wire.available() == 0); // Čekání na dostupnost I2C
  lowByte = Wire.read();         // Zápis nižšího bajtu

  Wire.beginTransmission(AS5600);
  Wire.write(0x0C); // Zápis příkazu pro čtení (vyšší bajt)
  Wire.endTransmission();
  Wire.requestFrom(AS5600, 1);

  while (Wire.available() == 0);
  highByte = Wire.read(); // Zápis vyššího bajtu

  highByte = highByte << 8;      // Posun vyššího bajtu o 8 bitů doleva
  rawAngle = highByte | lowByte; // Sloučení obou bajtů do jednoho 16-bitového čísla (operace OR)

  degAngle = rawAngle * degConst; // Převod na úhel ve stupních
}

void correctAngle()
{
  angleCorrected = degAngle - startAngle; // Vynulování úhlu podle počátečního úhlu
  if (angleCorrected < 0)                 // Pokud je úhel záporný, přičteme 360, aby byl v rozsahu 0°-360°
  {
    angleCorrected = angleCorrected + 360;
  }
}

void Angle_total()
{
  // Získání počtu otáček
  float RotationChange = angleCorrected - previousDegAngle; // Rozdíl mezi aktuálním a předchozím úhlem
  if (RotationChange > 180)                                 // Rozdíl větší než 180 => -1 otáčka
  {
    numberOfTurns--;
  }
  else if (RotationChange < -180) // Rozdíl menší než 180 => +1 otáčka
  {
    numberOfTurns++;
  }

  totalAngle = (360 * numberOfTurns) + angleCorrected; // Celkový úhel = počet otáček * 360 + aktuální úhel
  previousDegAngle = angleCorrected;                   // Uložení aktuálního úhlu jako předchozího pro další výpočet
}
void checkMagnet()
{
  // Kontrola magnetu
  while ((magnetStatus & 32) != 32) // Běží, dokud není detekován magnet
  {
    magnetStatus = 0;

    Wire.beginTransmission(AS5600);
    Wire.write(0x0B); // Zápis příkazu pro čtení stavu magnetu
    Wire.endTransmission();
    Wire.requestFrom(AS5600, 1);

    while (Wire.available() == 0) // Čekání na dostupnost I2C
    {
      Serial.println("Chyba: Senzor AS5600 neodpovídá! Čekám na odpověď senzoru...");
      delay(1000);
    }
    magnetStatus = Wire.read(); // Zápis stavu magnetu do proměnné

    /* Výpis stavu magnetu pro ladění
    Magnet je moc blízko: 100111, moc daleko: 10111, ve správné vzdálenosti: 110111  */
    Serial.print("Stav magnetu: ");
    Serial.println(magnetStatus, BIN);
  }

  Serial.println("Magnet detekován!");
  delay(1000);
}