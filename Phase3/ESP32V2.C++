#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "MEGA-2.4G-005327";
const char* password = "53a16f64";
const char* mqtt_server = "192.168.1.29";  // MQTT broker IP
bool stopExec = false;

WiFiClient espClient;
PubSubClient client(espClient);

const int ldrPin = A0;  // Photoresistor connected to A0
const int ledPin = 12;  // LED connected to GPIO

void setup() {
  pinMode(ldrPin, INPUT);
  pinMode(ledPin, OUTPUT);
  
  Serial.begin(115200);
  
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

  client.loop();
  delay(2000);
}
