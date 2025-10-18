import os
import sys
import json
import time
import logging
import requests
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt

# Setup Django environment
sys.path.append('C:/Users/dell/Desktop/New folder/farm_boy/farm_back/django_app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esp32_iot.settings')

import django
django.setup()

from django.conf import settings
from sensor_data.models import SensorData

logger = logging.getLogger('mqtt_handler')

class WeatherAPIClient:
    """Client for fetching weather data from OpenWeatherMap API"""
    def __init__(self):
        self.api_key = settings.OPENWEATHER_SETTINGS['API_KEY']
        self.city = settings.OPENWEATHER_SETTINGS['CITY']
        self.base_url = settings.OPENWEATHER_SETTINGS['BASE_URL']

    def get_current_weather(self):
        try:
            url = f"{self.base_url}/weather"
            params = {'q': self.city, 'appid': self.api_key, 'units': 'metric'}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            weather_data = {
                'temperature': data['main']['temp'],
                'humidity_air': data['main']['humidity'],
                'rain_forecast': data.get('rain', {}).get('1h', 0.0)
            }
            logger.info(f"Weather data fetched: {weather_data}")
            return weather_data
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return None


class MQTTHandler:
    """MQTT client handler for ESP32 sensor data with hourly saves"""
    
    def __init__(self):
        self.client = mqtt.Client()
        self.weather_client = WeatherAPIClient()
        self.broker_host = settings.MQTT_SETTINGS['BROKER_HOST']
        self.broker_port = settings.MQTT_SETTINGS['BROKER_PORT']
        self.username = settings.MQTT_SETTINGS['USERNAME']
        self.password = settings.MQTT_SETTINGS['PASSWORD']
        self.topic = settings.MQTT_SETTINGS['TOPIC']

        # Mémo de la dernière sauvegarde
        self.last_saved_time = None

        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        logger.info(f"MQTT Handler initialized - Broker: {self.broker_host}:{self.broker_port}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("[OK] Connected to MQTT broker")
            client.subscribe(self.topic)
            logger.info(f"Subscribed to topic: {self.topic}")
        else:
            logger.error(f"[FAIL] Failed to connect, rc={rc}")

    def on_disconnect(self, client, userdata, rc):
        logger.warning(f"[WARN] Disconnected from MQTT broker (rc={rc})")

    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            logger.info(f"📩 Received message: {payload}")

            # Lecture JSON ou valeur brute
            try:
                data = json.loads(payload)
                humidity_soil = float(data.get('humidity_soil', data.get('humidity', 0)))
            except json.JSONDecodeError:
                humidity_soil = float(payload)

            # Vérifie si 1 heure s'est écoulée depuis la dernière sauvegarde
            now = datetime.utcnow()
            if self.last_saved_time and now - self.last_saved_time < timedelta(hours=1):
                logger.info("[SKIP] Ignoring message (less than 1 hour since last save)")
                return

            # Récupère les données météo
            weather = self.weather_client.get_current_weather()
            if not weather:
                logger.warning("[WARN] No weather data fetched, skipping save")
                return

            combined_data = {
                'timestamp': now,
                'temperature': weather['temperature'],
                'humidity_air': weather['humidity_air'],
                'rain_forecast': weather['rain_forecast'],
                'humidity_soil': humidity_soil
            }

            # Sauvegarde MongoDB
            sensor = SensorData(**combined_data)
            sensor.save()
            self.last_saved_time = now  # update
            logger.info(f"[SAVE] Data saved to MongoDB (hourly): {combined_data}")
            print(f"[SAVE] Data saved (hourly): {combined_data}")

        except Exception as e:
            logger.error(f"[ERROR] Error processing message: {e}")

    def start(self):
        while True:
            try:
                logger.info(f"Connecting to MQTT broker: {self.broker_host}:{self.broker_port}")
                self.client.connect(self.broker_host, self.broker_port, 60)
                self.client.loop_forever()
            except Exception as e:
                logger.error(f"MQTT connection error: {e}")
                time.sleep(10)


if __name__ == "__main__":
    handler = MQTTHandler()
    try:
        handler.start()
    except KeyboardInterrupt:
        logger.info("[STOP] Stopping MQTT client...")
        handler.client.disconnect()
