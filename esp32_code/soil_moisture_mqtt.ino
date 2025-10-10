/*
 * ESP32 Soil Moisture Sensor (Simulated on Wokwi)
 * Sends simulated soil humidity data to EMQX Cloud via MQTT (TLS)
 */

 #include <WiFi.h>
 #include <WiFiClientSecure.h>
 #include <PubSubClient.h>
 #include <ArduinoJson.h>
 
 // WiFi Configuration (Use Wokwi’s simulated Wi-Fi)
 const char* ssid = "Wokwi-GUEST";
 const char* password = "";
 
 // MQTT Configuration (EMQX Cloud)
 const char* mqtt_server = "u2cc2628.ala.dedicated.aws.emqxcloud.com";
 const int mqtt_port = 8883;
 const char* mqtt_user = "esp32_user";
 const char* mqtt_password = "esp32_pass";
 const char* client_id = "ESP32_SoilSensor_Wokwi";
 
 // MQTT Topics
 const char* soil_topic = "esp32/humidity_soil";
 const char* status_topic = "esp32/status";
 
 // Timing
 const unsigned long READING_INTERVAL = 10000; // every 10 seconds
 
 // Root CA Certificate for EMQX Cloud
 const char* root_ca = R"EOF(
 -----BEGIN CERTIFICATE-----
 MIIFazCCA1OgAwIBAgIRAIIQz7DSQONZRGPgu2OCiwAwDQYJKoZIhvcNAQELBQAw
 TzELMAkGA1UEBhMCVVMxKTAnBgNVBAoTIEludGVybmV0IFNlY3VyaXR5IFJlc2Vh
 cmNoIEdyb3VwMRUwEwYDVQQDEwxJU1JHIFJvb3QgWDEwHhcNMTUwNjA0MTEwNDM4
 WhcNMzUwNjA0MTEwNDM4WjBPMQswCQYDVQQGEwJVUzEpMCcGA1UEChMgSW50ZXJu
 ZXQgU2VjdXJpdHkgUmVzZWFyY2ggR3JvdXAxFTATBgNVBAMTDElTUkcgUm9vdCBY
 MTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAK3oJHP0FDfzm54rVygc
 h77ct984kIxuPOZXoHj3dcKi/vVqbvYATyjb3miGbESTtrFj/RQSa78f0uoxmyF+
 0TM8ukj13Xnfs7j/EvEhmkvBioZxaUpmZmyPfjxwv60pIgbz5MDmgK7iS4+3mX6U
 A5/TR5d8mUgjU+g4rk8Kb4Mu0UlXjIB0ttov0DiNewNwIRt18jA8+o+u3dpjq+sW
 T8KOEUt+zwvo/7V3LvSye0rgTBIlDHCNAymg4VMk7BPZ7hm/ELNKjD+Jo2FR3qyH
 B5T0Y3HsLuJvW5iB4YlcNHlsdu87kGJ55tukmi8mxdAQ4Q7e2RCOFvu396j3x+UC
 B5iPNgiV5+I3lg02dZ77DnKxHZu8A/lJBdiB3QW0KtZB6awBdpUKD9jf1b0SHzUv
 KBds0pjBqAlkd25HN7rOrFleaJ1/ctaJxQZBKT5ZPt0m9STJEadao0xAH0ahmbWn
 OlFuhjuefXKnEgV4We0+UXgVCwOPjdAvBbI+e0ocS3MFEvzG6uBQE3xDk3SzynTn
 jh8BCNAw1FtxNrQHusEwMFxIt4I7mKZ9YIqioymCzLq9gwQbooMDQaHWBfEbwrbw
 qHyGO0aoSCqI3Haadr8faqU9GY/rOPNk3sgrDQoo//fb4hVC1CLQJ13hef4Y53CI
 rU7m2Ys6xt0nUW7/vGT1M0NPAgMBAAGjQjBAMA4GA1UdDwEB/wQEAwIBBjAPBgNV
 HRMBAf8EBTADAQH/MB0GA1UdDgQWBBR5tFnme7bl5AFzgAiIyBpY9umbbjANBgkq
 hkiG9w0BAQsFAAOCAgEAVR9YqbyyqFDQDLHYGmkgJykIrGF1XIpu+ILlaS/V9lZL
 ubhzEFnTIZd+50xx+7LSYK05qAvqFyFWhfFQDlnrzuBZ6brJFe+GnY+EgPbk6ZGQ
 3BebYhtF8GaV0nxvwuo77x/Py9auJ/GpsMiu/X1+mvoiBOv/2X/qkSsisRcOj/KK
 NFtY2PwByVS5uCbMiogziUwthDyC3+6WVwW6LLv3xLfHTjuCvjHIInNzktHCgKQ5
 ORAzI4JMPJ+GslWYHb4phowim57iaztXOoJwTdwJx4nLCgdNbOhdjsnvzqvHu7Ur
 TkXWStAmzOVyyghqpZXjFaH3pO3JLF+l+/+sKAIuvtd7u+Nxe5AW0wdeRlN8NwdC
 jNPElpzVmbUq4JUagEiuTDkHzsxHpFKVK7q4+63SM1N95R1NbdWhscdCb+ZAJzVc
 oyi3B43njTOQ5yOf+1CceWxG1bQVs5ZufpsMljq4Ui0/1lvh+wjChP4kqKOJ2qxq
 4RgqsahDYVvTH9w7jXbyLeiNdd8XM2w9U/t7y0Ff/9yi0GE44Za4rF2LN9d11TPA
 mRGunUHBcnWEvgJBQl9nJEiU0Zsnvgc/ubhPgXRR4Xq37Z0j4r7g1SgEEzwxA57d
 emyPxgcYxn/eR44/KJ4EBs+lVDR3veyJm+kXQ99b21/+jh5Xos1AnX5iItreGCc=
 -----END CERTIFICATE-----
 )EOF";
 
 // Global objects
 WiFiClientSecure espClient;
 PubSubClient client(espClient);
 
 unsigned long lastReading = 0;
 
 void setup() {
   Serial.begin(115200);
   Serial.println("\nESP32 Wokwi MQTT Soil Sensor");
 
   // Connect WiFi
   WiFi.begin(ssid, password);
   while (WiFi.status() != WL_CONNECTED) {
     delay(500);
     Serial.print(".");
   }
   Serial.println("\n✅ WiFi connected");
   Serial.print("IP: ");
   Serial.println(WiFi.localIP());
 
   // Configure TLS
   espClient.setCACert(root_ca);
 
   // Configure MQTT
   client.setServer(mqtt_server, mqtt_port);
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
   Serial.print("Connecting to MQTT broker... ");
   while (!client.connected()) {
     if (client.connect(client_id, mqtt_user, mqtt_password)) {
       Serial.println("✅ Connected to EMQX Cloud!");
       client.publish(status_topic, "ESP32 Wokwi connected");
     } else {
       Serial.print("❌ Failed, rc=");
       Serial.println(client.state());
       delay(3000);
     }
   }
 }
 
 void sendSoilData() {
   // Simulate soil moisture between 30% and 70%
   float humidity_soil = random(300, 700) / 10.0;
 
   DynamicJsonDocument doc(200);
   doc["humidity_soil"] = humidity_soil;
   doc["wifi_rssi"] = WiFi.RSSI();
   doc["uptime"] = millis();
 
   String payload;
   serializeJson(doc, payload);
 
   client.publish(soil_topic, payload.c_str());
   Serial.print("📡 Published: ");
   Serial.println(payload);
 }
 