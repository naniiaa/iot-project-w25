#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <PubSubClient.h>

// WiFi and MQTT setup
const char* ssid = "MEGA-2.4G-005327";
const char* password = "53a16f64";
const char* mqtt_server = "192.168.1.29";
WiFiClient espClient;
PubSubClient client(espClient);

// RFID setup - Using default ESP32 SPI pins
#define SS_PIN 5    // SDA (SS) connected to GPIO5
#define RST_PIN 4   // RST connected to GPIO4
MFRC522 rfid(SS_PIN, RST_PIN);
String lastUID = "";

// Light sensor setup
#define LIGHT_SENSOR_PIN 36  // ESP32 ADC1_CH0 (GPIO36)
#define LED_PIN 12           // LED output pin
#define ANALOG_THRESHOLD 2000

// Control variables
bool stopExecution = false;
unsigned long lastLightCheck = 0;
unsigned long lastRFIDCheck = 0;
const long lightInterval = 2000; // Check light every 5 seconds
const long rfidInterval = 1000;  // Check RFID every second

void setup() {
  Serial.begin(115200);
  delay(2000); // Short delay for serial to initialize
  
  Serial.println("\n\n----- ESP32 RFID & Light Sensor System -----");
  
  // Setup Light Sensor and LED
  pinMode(LIGHT_SENSOR_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW); // Initialize LED to OFF
  Serial.println("Light sensor and LED initialized");
  
  // Setup SPI and RFID
  SPI.begin();        // Default SPI pins: SCK=18, MISO=19, MOSI=23, SS=5
  delay(2000);
  rfid.PCD_Init();    // Initialize MFRC522
  delay(2000);
  
  // Check if RFID reader is responding
  byte v = rfid.PCD_ReadRegister(rfid.VersionReg);
  if (v == 0x00 || v == 0xFF) {
    Serial.println("WARNING: RFID reader not found or not responding!");
    Serial.println("Check wiring and connections");
  } else {
    Serial.print("RFID reader version: 0x");
    Serial.println(v, HEX);
    Serial.println("RFID reader initialized successfully");
  }

  // Print expected SPI connections for reference
  Serial.println("ESP32 SPI connections (verify these match your wiring):");
  Serial.println(" - SCK:  GPIO18");
  Serial.println(" - MISO: GPIO19");
  Serial.println(" - MOSI: GPIO23");
  Serial.println(" - SS:   GPIO5");
  Serial.println(" - RST:  GPIO4");
  
  // Setup WiFi
  setup_wifi();
  
  // Setup MQTT
  client.setServer(mqtt_server, 1883);
  
  Serial.println("Place your RFID card near the reader...");
  Serial.println("Type 'x' to stop execution, 'r' to resume");
  Serial.println("----- Setup Complete -----\n");
}

void setup_wifi() {
  delay(10);
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi connection failed. Will retry in the loop");
  }
}

void reconnect() {
  // Only try to reconnect if WiFi is connected
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  
  // Exit if already connected
  if (client.connected()) {
    return;
  }
  
  Serial.print("Attempting MQTT connection...");
  
  // Create a random client ID
  String clientId = "ESP32Client-";
  clientId += String(random(0xffff), HEX);
  
  // Attempt to connect
  if (client.connect(clientId.c_str())) {
    Serial.println("connected");
  } else {
    Serial.print("failed, rc=");
    Serial.print(client.state());
    Serial.println(" will try again next cycle");
  }
}

void checkForSerialCommands() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    
    if (cmd == 'x') {
      stopExecution = true;
      Serial.println("Execution STOPPED. Type 'r' to resume");
    } else if (cmd == 'r') {
      stopExecution = false;
      Serial.println("Execution RESUMED");
    }
    
    // Clear any remaining characters
    while (Serial.available()) {
      Serial.read();
    }
  }
}

void checkRFID() {
  // Skip if RFID checking is not due yet
  unsigned long currentMillis = millis();
  if (currentMillis - lastRFIDCheck < rfidInterval) {
    return;
  }
  lastRFIDCheck = currentMillis;
  
  // Reset will improve detection reliability
  rfid.PCD_Init();
  
  // Check if a new card is present
  if (!rfid.PICC_IsNewCardPresent()) {
    return;
  }
  
  // Try to read the card serial
  if (!rfid.PICC_ReadCardSerial()) {
    return;
  }
  
  // Build UID string
  String currentUID = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) {
      currentUID += "0"; // Add leading zero for single-digit hex
    }
    currentUID += String(rfid.uid.uidByte[i], HEX);
  }
  currentUID.toLowerCase(); // Ensure lowercase for matching
  
  // Print card info
  Serial.print("RFID Card detected! UID: ");
  Serial.println(currentUID);
  
  // Only publish if it's a new card
  if (currentUID != lastUID) {
    if (client.connected()) {
      // Publish to MQTT
      client.publish("rfid/ID", currentUID.c_str());
      Serial.println("Published to MQTT topic 'rfid/ID'");
    } else {
      Serial.println("MQTT not connected, can't publish UID");
    }
    lastUID = currentUID;
  }
  
  // Halt PICC and stop encryption
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}

void checkLightSensor() {
  // Skip if light checking is not due yet
  unsigned long currentMillis = millis();
  if (currentMillis - lastLightCheck < lightInterval) {
    return;
  }
  lastLightCheck = currentMillis;
  
  // Read the light sensor
  int lightIntensity = analogRead(LIGHT_SENSOR_PIN);
  Serial.print("Light Intensity: ");
  Serial.println(lightIntensity);
  
  if (client.connected()) {
    // Publish light intensity
    client.publish("sensor/light", String(lightIntensity).c_str());
    
    // Control LED based on threshold
    if (lightIntensity < ANALOG_THRESHOLD) {
      digitalWrite(LED_PIN, HIGH);
      client.publish("sensor/led", "ON");
      Serial.println("LED status: ON");
    } else {
      digitalWrite(LED_PIN, LOW);
      client.publish("sensor/led", "OFF");
      Serial.println("LED status: OFF");
    }
  }
}

void loop() {
  // Check for serial commands
  checkForSerialCommands();
  
  // If execution is stopped, just wait
  if (stopExecution) {
    delay(2000);
    return;
  }
  
  // Try to connect to MQTT if needed
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  // Check sensors
  checkRFID();
  checkLightSensor();
  
  // Main loop delay to reduce resource usage
  delay(2000);
}