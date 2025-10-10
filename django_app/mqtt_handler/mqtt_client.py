import paho.mqtt.client as mqtt
import json
import logging
import time
import requests
from datetime import datetime
import os
import sys

# Add Django project to path
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esp32_iot.settings')

import django
django.setup()

from sensor_data.models import SensorData
from django.conf import settings

logger = logging.getLogger('mqtt_handler')

class WeatherAPIClient:
    """Client for fetching weather data from OpenWeatherMap API"""
    
    def __init__(self):
        self.api_key = settings.OPENWEATHER_SETTINGS['API_KEY']
        self.city = settings.OPENWEATHER_SETTINGS['CITY']
        self.base_url = settings.OPENWEATHER_SETTINGS['BASE_URL']
    
    def get_current_weather(self):
        """Fetch current weather data"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': self.city,
                'appid': self.api_key,
                'units': 'metric'  # Celsius
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract required data
            weather_data = {
                'temperature': data['main']['temp'],
                'humidity_air': data['main']['humidity'],
                'rain_forecast': 0.0  # Default value
            }
            
            # Check if there's rain in the forecast
            if 'rain' in data:
                weather_data['rain_forecast'] = data['rain'].get('1h', 0.0)
            
            logger.info(f"Weather data fetched: {weather_data}")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API request error: {e}")
            raise
        except KeyError as e:
            logger.error(f"Weather API response parsing error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching weather: {e}")
            raise

class MQTTHandler:
    """MQTT client handler for ESP32 sensor data"""
    
    def __init__(self):
        self.client = mqtt.Client()
        self.weather_client = WeatherAPIClient()
        self.broker_host = settings.MQTT_SETTINGS['BROKER_HOST']
        self.broker_port = settings.MQTT_SETTINGS['BROKER_PORT']
        self.username = settings.MQTT_SETTINGS['USERNAME']
        self.password = settings.MQTT_SETTINGS['PASSWORD']
        self.topic = settings.MQTT_SETTINGS['TOPIC']
        
        # Set up MQTT callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Set credentials if provided
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        logger.info(f"MQTT Handler initialized - Broker: {self.broker_host}:{self.broker_port}")
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback for when the client receives a CONNACK response"""
        if rc == 0:
            logger.info(f"Connected to MQTT broker successfully")
            # Subscribe to ESP32 soil humidity topic
            client.subscribe(self.topic)
            logger.info(f"Subscribed to topic: {self.topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects"""
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnection: {rc}")
        else:
            logger.info("MQTT client disconnected")
    
    def on_message(self, client, userdata, msg):
        """Callback for when a PUBLISH message is received"""
        try:
            logger.info(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
            
            # Parse ESP32 soil humidity data
            try:
                payload = msg.payload.decode('utf-8')
                
                # Try to parse as JSON first
                try:
                    esp32_data = json.loads(payload)
                    humidity_soil = float(esp32_data.get('humidity_soil', esp32_data.get('humidity', payload)))
                except json.JSONDecodeError:
                    # If not JSON, assume it's just the humidity value
                    humidity_soil = float(payload)
                
                logger.info(f"Parsed soil humidity: {humidity_soil}%")
                
            except (ValueError, KeyError) as e:
                logger.error(f"Error parsing ESP32 data: {e}")
                return
            
            # Fetch weather data from OpenWeather API
            try:
                weather_data = self.weather_client.get_current_weather()
                logger.info(f"Weather data fetched: {weather_data}")
            except Exception as e:
                logger.error(f"Failed to fetch weather data: {e}")
                return
            
            # Combine ESP32 and weather data
            combined_data = {
                'timestamp': datetime.utcnow(),
                'temperature': weather_data['temperature'],
                'humidity_air': weather_data['humidity_air'],
                'rain_forecast': weather_data['rain_forecast'],
                'humidity_soil': humidity_soil
            }
            
            # Save to MongoDB
            try:
                sensor_reading = SensorData(**combined_data)
                sensor_reading.save()
                logger.info(f"Sensor data saved to MongoDB: {sensor_reading}")
                
            except Exception as e:
                logger.error(f"Error saving to MongoDB: {e}")
                return
                
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def start(self):
        """Start the MQTT client"""
        try:
            logger.info(f"Connecting to MQTT broker: {self.broker_host}:{self.broker_port}")
            self.client.connect(self.broker_host, self.broker_port, 60)
            
            # Start the network loop in a separate thread
            self.client.loop_forever()
            
        except Exception as e:
            logger.error(f"Error starting MQTT client: {e}")
            # Retry connection after 30 seconds
            time.sleep(30)
            self.start()
    
    def stop(self):
        """Stop the MQTT client"""
        logger.info("Stopping MQTT client")
        self.client.disconnect()
        self.client.loop_stop()

if __name__ == "__main__":
    # For testing purposes
    mqtt_handler = MQTTHandler()
    try:
        mqtt_handler.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, stopping...")
        mqtt_handler.stop()