#include <ESP8266WiFi.h>
#include <PubSubClient.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* mqtt_server = "BROKER_IP_ADDRESS";  // MQTT broker IP

WiFiClient espClient;
PubSubClient client(espClient);

const int ldrPin = A0;  // Photoresistor connected to A0
const int ledPin = D5;  // Optional LED connected to GPIO5 (D5)

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
