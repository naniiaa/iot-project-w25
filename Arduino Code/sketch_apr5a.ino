#include <WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h>

// const char* ssid = "Bridjette";
// const char* password = "11223344";
// const char* mqtt_server = "172.20.10.4";

const char* ssid = "MEGA-2.4G-005327";
const char* password = "53a16f64";
const char* mqtt_server = "192.168.1.29";  // MQTT broker IP
bool stopExec = false;

WiFiClient espClient;
PubSubClient client(espClient);

long lastMsg = 0;
char msg[50];
int value = 0;

#define SS_PIN 5  // SDA Pin on RC522
#define RST_PIN 4 // RST Pin on RC522
MFRC522 rfid(SS_PIN, RST_PIN); // Create MFRC522 instance

String data = "";  // String to store the UID data
String lastUID = ""; // String to store the last UID for comparison

const int ldrPin = A0;//36;//A0;  // Photoresistor connected to A0
const int ledPin = 12;  // LED connected to GPIO

void setup() {
  pinMode(ldrPin, INPUT);
  pinMode(ledPin, OUTPUT);
  
  Serial.begin(115200);
  
  SPI.begin();
  rfid.PCD_Init();
  Serial.println("Place your RFID card near the reader...");


  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi Connected");

  client.setServer(mqtt_server, 1883);
  while (!client.connected()) {
    if (client.connect("ESP8266Client")) {
      Serial.println("Connected to MQTT");
    } else {
      delay(5000);
    }
  }
}

void loop() {
  if (Serial.available()) {
    char command = Serial.read();
    if(command == 'x') {
      stopExec = true;
      Serial.println("Exec stopped by user.");
    }
  }

  if (stopExec) return;
  
  int lightIntensity = analogRead(ldrPin);  
  Serial.print("Light Intensity: ");
  Serial.println(lightIntensity);
  
  client.publish("sensor/light", String(lightIntensity).c_str());

  if (lightIntensity < 400) {
    digitalWrite(ledPin, HIGH);
    client.publish("sensor/led", "ON");
  } else {
    digitalWrite(ledPin, LOW);
    client.publish("sensor/led", "OFF");
  }
  delay(500);


// RFID TYPE SHIT
  if (!rfid.PICC_IsNewCardPresent()) {
    return;
  }
  
  if (!rfid.PICC_ReadCardSerial()) {
    return;
  }

  // Initialize the current UID as a string
  String currentUID = "";

  // Store the current UID into the currentUID string
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) {
      currentUID += "0"; // Add leading zero if necessary
    }
    currentUID += String(rfid.uid.uidByte[i], HEX); // Append byte as hex
  }

  // Check if the current UID is different from the last one
  if (currentUID != lastUID) {
    // UID is different, reset 'data' string
    data = "";  // Clear the data string
    Serial.println("New card detected, resetting data.");
    data = currentUID; // Store new UID in data string

    // Publish the new UID to MQTT topic IoTProject/ID
    Serial.print("New Card UID: ");
    Serial.println(data);
    client.publish("rfid/ID", data.c_str()); // Publish UID to MQTT
  }

  // Update the 'lastUID' with the current UID
  lastUID = currentUID;


  // Halt PICC (Card)
  rfid.PICC_HaltA();
  client.loop();
  delay(2000);
}
