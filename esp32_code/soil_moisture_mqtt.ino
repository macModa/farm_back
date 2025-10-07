/*
 * ESP32 Soil Moisture Sensor with MQTT
 * Sends soil humidity data to EMQX Cloud broker
 * 
 * Required libraries:
 * - WiFi (ESP32 core)
 * - PubSubClient
 * 
 * Hardware:
 * - ESP32 Dev Board
 * - Soil moisture sensor connected to pin A0
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// WiFi Configuration
const char* ssid = "VOTRE_WIFI_SSID";
const char* password = "VOTRE_WIFI_PASSWORD";

// MQTT Configuration (EMQX Cloud)
const char* mqtt_server = "u2cc2628.ala.dedicated.aws.emqxcloud.com";
const int mqtt_port = 1883;
const char* mqtt_user = ""; // Leave empty if no authentication
const char* mqtt_password = ""; // Leave empty if no authentication
const char* client_id = "ESP32_SoilSensor_001";

// MQTT Topics
const char* soil_topic = "esp32/humidity_soil";
const char* status_topic = "esp32/status";

// Hardware Configuration
const int SOIL_SENSOR_PIN = A0;
const int LED_PIN = 2; // Built-in LED

// Timing Configuration
const unsigned long READING_INTERVAL = 30000; // 30 seconds
const unsigned long WIFI_TIMEOUT = 10000; // 10 seconds
const unsigned long MQTT_RETRY_INTERVAL = 5000; // 5 seconds

// Global Variables
WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastReading = 0;
unsigned long lastMqttAttempt = 0;
int readingCount = 0;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(SOIL_SENSOR_PIN, INPUT);
  
  Serial.println("ESP32 Soil Moisture MQTT Sensor");
  Serial.println("================================");
  
  // Initialize WiFi
  setupWiFi();
  
  // Initialize MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(onMqttMessage);
  
  // Connect to MQTT
  connectMQTT();
  
  // Send startup message
  sendStatusMessage("ESP32 Soil Sensor Started");
  
  Serial.println("Setup complete. Starting main loop...");
}

void loop() {
  // Maintain MQTT connection
  if (!client.connected()) {
    if (millis() - lastMqttAttempt > MQTT_RETRY_INTERVAL) {
      connectMQTT();
      lastMqttAttempt = millis();
    }
  } else {
    client.loop();
  }
  
  // Read and send sensor data
  if (millis() - lastReading > READING_INTERVAL) {
    readAndSendSensorData();
    lastReading = millis();
  }
  
  delay(100); // Small delay to prevent watchdog reset
}

void setupWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  unsigned long startAttemptTime = millis();
  
  while (WiFi.status() != WL_CONNECTED && 
         millis() - startAttemptTime < WIFI_TIMEOUT) {
    delay(500);
    Serial.print(".");
    digitalWrite(LED_PIN, !digitalRead(LED_PIN)); // Blink LED
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    digitalWrite(LED_PIN, HIGH); // Turn on LED when connected
    Serial.println("");
    Serial.println("WiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal strength (RSSI): ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("");
    Serial.println("WiFi connection failed!");
    digitalWrite(LED_PIN, LOW);
  }
}

void connectMQTT() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected. Cannot connect to MQTT.");
    return;
  }
  
  Serial.print("Connecting to MQTT broker: ");
  Serial.println(mqtt_server);
  
  // Generate unique client ID if needed
  String clientId = String(client_id) + "_" + String(random(0xffff), HEX);
  
  bool connected = false;
  if (strlen(mqtt_user) > 0 && strlen(mqtt_password) > 0) {
    connected = client.connect(clientId.c_str(), mqtt_user, mqtt_password);
  } else {
    connected = client.connect(clientId.c_str());
  }
  
  if (connected) {
    Serial.println("MQTT connected!");
    
    // Subscribe to command topics (optional)
    client.subscribe("esp32/commands");
    
    // Blink LED to indicate MQTT connection
    for (int i = 0; i < 3; i++) {
      digitalWrite(LED_PIN, LOW);
      delay(100);
      digitalWrite(LED_PIN, HIGH);
      delay(100);
    }
    
  } else {
    Serial.print("MQTT connection failed, rc=");
    Serial.print(client.state());
    Serial.println(" Retrying...");
  }
}

void readAndSendSensorData() {
  if (!client.connected()) {
    Serial.println("MQTT not connected. Skipping sensor reading.");
    return;
  }
  
  // Read soil moisture sensor
  int sensorValue = analogRead(SOIL_SENSOR_PIN);
  
  // Convert to humidity percentage
  // Note: Calibrate these values based on your specific sensor
  float humidity_soil = map(sensorValue, 4095, 0, 0, 100); // Invert if needed
  
  // Ensure value is within valid range
  humidity_soil = constrain(humidity_soil, 0, 100);
  
  readingCount++;
  
  Serial.println("--- Sensor Reading #" + String(readingCount) + " ---");
  Serial.print("Raw sensor value: ");
  Serial.println(sensorValue);
  Serial.print("Soil humidity: ");
  Serial.print(humidity_soil);
  Serial.println("%");
  Serial.print("WiFi RSSI: ");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm");
  
  // Create JSON payload
  DynamicJsonDocument doc(200);
  doc["humidity_soil"] = humidity_soil;
  doc["sensor_raw"] = sensorValue;
  doc["wifi_rssi"] = WiFi.RSSI();
  doc["reading_count"] = readingCount;
  doc["uptime"] = millis();
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Send to MQTT broker
  bool success = client.publish(soil_topic, jsonString.c_str());
  
  if (success) {
    Serial.println("✓ Data sent successfully to MQTT");
    Serial.println("Published: " + jsonString);
    
    // Brief LED blink to indicate successful transmission
    digitalWrite(LED_PIN, LOW);
    delay(50);
    digitalWrite(LED_PIN, HIGH);
    
  } else {
    Serial.println("✗ Failed to send data to MQTT");
  }
  
  Serial.println();
}

void sendStatusMessage(String message) {
  if (client.connected()) {
    DynamicJsonDocument doc(200);
    doc["status"] = message;
    doc["timestamp"] = millis();
    doc["wifi_rssi"] = WiFi.RSSI();
    doc["free_heap"] = ESP.getFreeHeap();
    
    String jsonString;
    serializeJson(doc, jsonString);
    
    client.publish(status_topic, jsonString.c_str());
    Serial.println("Status sent: " + message);
  }
}

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  // Handle incoming MQTT messages (optional)
  Serial.print("Message received on topic: ");
  Serial.println(topic);
  
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println("Message: " + message);
  
  // Add custom command handling here if needed
  if (String(topic) == "esp32/commands") {
    if (message == "status") {
      sendStatusMessage("ESP32 running normally");
    } else if (message == "restart") {
      sendStatusMessage("Restarting ESP32...");
      delay(1000);
      ESP.restart();
    }
  }
}