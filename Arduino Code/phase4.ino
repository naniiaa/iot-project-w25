#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <PubSubClient.h>

// WiFi and MQTT setup
const char* ssid = "MIKO";
const char* password = "DarCenMiko2025!";
const char* mqtt_server = "10.0.0.230"; // Make sure this matches your RPi IP  // USE IF CONFIG

WiFiClient espClient;
PubSubClient client(espClient);

// RFID setup 
#define SS_PIN 5    // connected to GPIO5
#define RST_PIN 4   // connected to GPIO4
MFRC522 rfid(SS_PIN, RST_PIN);
String lastUID = "";

// Light sensor setup
#define LIGHT_SENSOR_PIN 36  // GPIO36
#define LED_PIN 12           // LED output pin
#define ANALOG_THRESHOLD 2000

// Control variables
bool stopExecution = false;
unsigned long lastLightCheck = 0;
unsigned long lastRFIDCheck = 0;
unsigned long lastMqttReconnectAttempt = 0;
const long lightInterval = 1000;     
const long rfidInterval = 1000;       
const long mqttReconnectInterval = 5000;

void setup() {
  Serial.begin(115200);
  
  // Setup Light Sensor and LED
  pinMode(LIGHT_SENSOR_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW); // Initialize LED to OFF
  Serial.println("Light sensor and LED initialized");
  
  // Setup SPI and RFID
  SPI.begin();        // Default SPI pins: SCK=18, MISO=19, MOSI=23, SS=5
  rfid.PCD_Init();    // Initialize MFRC522
  
  // Setup WiFi
  setup_wifi();
  
  // Setup MQTT
  client.setServer(mqtt_server, 1883);
  
  Serial.println("ESP32 RFID & Light Sensor System ready");
}

void setup_wifi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  // Wait up to 20 seconds
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
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

boolean reconnect() {
  // Exit if already connected
  if (client.connected()) {
    return true;
  }
  
  Serial.print("Attempting MQTT connection...");
  
  // Create a random client ID
  String clientId = "ESP32Client-";
  clientId += String(random(0xffff), HEX);
  
  // Attempt to connect with a clean session
  if (client.connect(clientId.c_str())) {
    Serial.println("connected");
    return true;
  } else {
    Serial.print("failed, rc=");
    Serial.print(client.state());
    Serial.println(" will try again later");
    return false;
  }
}

void checkRFID() {
  // Skip if RFID checking is not due yet
  unsigned long currentMillis = millis();
  if (currentMillis - lastRFIDCheck < rfidInterval) {
    return;
  }
  lastRFIDCheck = currentMillis;

  if (!rfid.PICC_IsNewCardPresent()) {
    return;
  }

  if (!rfid.PICC_ReadCardSerial()) {
    return;
  }

  String currentUID = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) {
      currentUID += "0"; 
    }
    currentUID += String(rfid.uid.uidByte[i], HEX);
  }
  currentUID.toLowerCase(); 

  Serial.print("RFID Card detected! UID: ");
  Serial.println(currentUID);

  if (currentUID != lastUID) {
    if (client.connected()) {
      // Publish to MQTT
      boolean published = client.publish("rfid/ID", currentUID.c_str());
      Serial.print("Published to MQTT topic 'rfid/ID': ");
      Serial.println(published ? "SUCCESS" : "FAILED");
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
  
  // Control LED based on threshold
  bool ledState = (lightIntensity < ANALOG_THRESHOLD);
  digitalWrite(LED_PIN, ledState ? HIGH : LOW);
  
  if (client.connected()) {
    // Publish light intensity
    boolean publishedIntensity = client.publish("sensor/light", String(lightIntensity).c_str());
    
    // Publish LED status
    boolean publishedLed = client.publish("sensor/led", ledState ? "ON" : "OFF");
    
    // Print the values 
    Serial.print("Light Intensity: ");
    Serial.print(lightIntensity);
    Serial.print(", LED: ");
    Serial.print(ledState ? "ON" : "OFF");
    Serial.print(", Published: ");
    Serial.print(publishedIntensity && publishedLed ? "SUCCESS" : "FAILED");
    Serial.println();
  } else {
    Serial.print("Light Intensity: ");
    Serial.print(lightIntensity);
    Serial.print(", LED: ");
    Serial.print(ledState ? "ON" : "OFF");
    Serial.println(" (MQTT disconnected)");
  }
}

void checkMqttConnection() {
  unsigned long currentMillis = millis();
  
  // Only try reconnecting if we're connected to WiFi but not to MQTT
  if (WiFi.status() == WL_CONNECTED && !client.connected() && 
      (currentMillis - lastMqttReconnectAttempt > mqttReconnectInterval)) {
    
    lastMqttReconnectAttempt = currentMillis;
    
    // Attempt to reconnect to MQTT
    if (reconnect()) {
      // Reset last attempt time if reconnection successful
      lastMqttReconnectAttempt = 0;
    }
  }
  
  // If WiFi is disconnected, try to reconnect
  if (WiFi.status() != WL_CONNECTED && 
      (currentMillis - lastMqttReconnectAttempt > mqttReconnectInterval)) {
    
    lastMqttReconnectAttempt = currentMillis;
    Serial.println("WiFi disconnected. Attempting to reconnect...");
    setup_wifi();
  }
}

void loop() {
  // Check serial for commands
  if (Serial.available()) {
    char cmd = Serial.read();
    if (cmd == 'x') {
      stopExecution = true;
      Serial.println("Execution STOPPED. Type 'r' to resume");
    } else if (cmd == 'r') {
      stopExecution = false;
      Serial.println("Execution RESUMED");
    }
    // Clear any remaining characters
    while (Serial.available()) Serial.read();
  }
  
  // If execution is stopped, just wait
  if (stopExecution) {
    delay(1000);
    return;
  }
  
  // Check WiFi and MQTT connections
  checkMqttConnection();
  
  // Process incoming MQTT messages
  if (client.connected()) {
    client.loop();
  }
  
  // Check sensors
  checkRFID();
  checkLightSensor();
  
  // Delay
   delay(2000);
}