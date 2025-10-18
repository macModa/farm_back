/*
https://wokwi.com/projects/305569599398609473
 * ESP32 Soil Moisture Sensor (Simulated on Wokwi)
 * Sends simulated soil humidity data to EMQX Cloud via MQTT (TLS)
 */

 #include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// --- WiFi Configuration ---
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// --- MQTT Configuration (EMQX Cloud) ---
const char* mqtt_server = "j2a24bbb.ala.dedicated.aws.emqxcloud.com";
const int mqtt_port = 1883; // Non-TLS port
const char* mqtt_user = "esp32_user";
const char* mqtt_password = "esp32_pass";
const char* client_id = "ESP32_SoilSensor_Wokwi";

// --- Topics ---
const char* soil_topic = "esp32/humidity_soil";
const char* status_topic = "esp32/status";

// --- Intervalle d’envoi ---
const unsigned long READING_INTERVAL = 10000;

// --- Objects ---
WiFiClient espClient; // Non-TLS client
PubSubClient client(espClient);
unsigned long lastReading = 0;

// --- Prototypes ---
void connectMQTT();
void sendSoilData();

void setup() {
  Serial.begin(115200);
  Serial.println("\n🌱 ESP32 Wokwi MQTT Soil Sensor");

  // Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setKeepAlive(60); // Increase keep-alive
  client.setSocketTimeout(60); // Increase timeout to avoid rc=-2
  connectMQTT();
}

void loop() {
  if (!client.connected()) connectMQTT();
  client.loop();

  if (millis() - lastReading > READING_INTERVAL) {
    sendSoilData();
    lastReading = millis();
  }
}

void connectMQTT() {
  Serial.print("Connecting to MQTT...");
  while (!client.connected()) {
    Serial.print("Attempting connection to ");
    Serial.print(mqtt_server);
    Serial.print(":");
    Serial.println(mqtt_port);
    if (client.connect(client_id, mqtt_user, mqtt_password)) {
      Serial.println("✅ Connected to EMQX!");
      client.publish(status_topic, "ESP32 Wokwi connected");
    } else {
      Serial.print("❌ Failed, rc=");
      Serial.print(client.state());
      Serial.print(" MQTT State: ");
      switch (client.state()) {
        case -4: Serial.println("MQTT_CONNECTION_TIMEOUT"); break;
        case -3: Serial.println("MQTT_CONNECTION_LOST"); break;
        case -2: Serial.println("MQTT_CONNECT_FAILED"); break;
        case -1: Serial.println("MQTT_DISCONNECTED"); break;
        case 0: Serial.println("MQTT_CONNECTED"); break;
        case 1: Serial.println("MQTT_CONNECT_BAD_PROTOCOL"); break;
        case 2: Serial.println("MQTT_CONNECT_BAD_CLIENT_ID"); break;
        case 3: Serial.println("MQTT_CONNECT_UNAVAILABLE"); break;
        case 4: Serial.println("MQTT_CONNECT_BAD_CREDENTIALS"); break;
        case 5: Serial.println("MQTT_CONNECT_UNAUTHORIZED"); break;
        default: Serial.println("UNKNOWN"); break;
      }
      delay(3000);
    }
  }
}

void sendSoilData() {
  float humidity_soil = random(300, 700) / 10.0;

  DynamicJsonDocument doc(200);
  doc["humidity_soil"] = humidity_soil;
  doc["wifi_rssi"] = WiFi.RSSI();
  doc["uptime_ms"] = millis();

  String payload;
  serializeJson(doc, payload);

  client.publish(soil_topic, payload.c_str());
  Serial.print("📡 Published: ");
  Serial.println(payload);
}