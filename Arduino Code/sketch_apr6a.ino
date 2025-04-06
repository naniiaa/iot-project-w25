#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <PubSubClient.h>

// const char* ssid = "Bridjette";
// const char* password = "11223344";
// const char* mqtt_server = "172.20.10.4";

// WiFi and MQTT setup
const char* ssid = "MEGA-2.4G-005327";        // Replace with your actual WiFi name
const char* password = "53a16f64";    // Replace with your actual WiFi password
const char* mqtt_server = "192.168.1.29";   // Replace with your Raspberry Pi IP address
WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;

// RFID setup
#define SS_PIN 5    // SDA Pin on RC522
#define RST_PIN 4   // RST Pin on RC522
MFRC522 rfid(SS_PIN, RST_PIN); // Create MFRC522 instance
String data = "";         // String to store the UID data
String lastUID = "";      // String to store the last UID for comparison

// Light sensor setup
#define LIGHT_SENSOR_PIN  A0  // ESP32 pin GPIO35 connected to light sensor
#define LED_PIN 12            // LED output pin 
#define ANALOG_THRESHOLD  2000

void setup() {
  Serial.begin(115200);
  
  // Setup Light Sensor and LED
  analogSetAttenuation(ADC_11db);
  pinMode(LED_PIN, OUTPUT);
  
  // Setup WiFi
  setup_wifi();
  
  // Setup MQTT
  client.setServer(mqtt_server, 1883);
  
  // Setup RFID
  SPI.begin();
  rfid.PCD_Init();
  Serial.println("Place your RFID card near the reader...");
}

void setup_wifi() {
  delay(10);
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client")) {
      Serial.println("connected to MQTT");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop(); // Keep the MQTT connection alive
  
  // Read the light sensor value
  int lightIntensity = analogRead(LIGHT_SENSOR_PIN);  
  Serial.print("Light Intensity: ");
  Serial.println(lightIntensity);
  
  // Publish light intensity to sensor/light topic to match LightManager.py
  client.publish("sensor/light", String(lightIntensity).c_str());

  // Control LED based on light intensity
  if (lightIntensity < ANALOG_THRESHOLD) {
    digitalWrite(LED_PIN, HIGH);
    client.publish("sensor/led", "ON");
  } else {
    digitalWrite(LED_PIN, LOW);
    client.publish("sensor/led", "OFF");
  }
  
  // RFID card detection
  if (!rfid.PICC_IsNewCardPresent()) {
    delay(100); // Small delay to avoid CPU hogging
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
    
    // Publish the new UID to MQTT topic IoTProject/ID to match RFIDManager.py
    Serial.print("New Card UID: ");
    Serial.println(data);
    client.publish("rfid/ID", data.c_str()); // Publish UID to MQTT
  }
  
  // Update the 'lastUID' with the current UID
  lastUID = currentUID;
  
  // Halt PICC (Card)
  rfid.PICC_HaltA();
  
  // Small delay to avoid flooding the serial and MQTT server
  delay(500);
}