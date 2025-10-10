# MQTT Handler module for ESP32 IoT project
from .mqtt_client import MQTTHandler

# Alias for backward compatibility
MQTTClient = MQTTHandler

__all__ = ['MQTTHandler', 'MQTTClient']