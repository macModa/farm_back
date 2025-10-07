#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import threading
from django.core.management import execute_from_command_line

def start_mqtt_handler():
    """Start MQTT handler in a separate thread"""
    try:
        from mqtt_handler.mqtt_client import MQTTHandler
        mqtt_handler = MQTTHandler()
        mqtt_handler.start()
    except ImportError as e:
        print(f"MQTT Handler import error: {e}")
    except Exception as e:
        print(f"MQTT Handler start error: {e}")

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esp32_iot.settings')
    
    try:
        # Import Django here to check if it's installed
        from django.core.management import execute_from_command_line
        
        # Check if we're running the server
        if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
            # Start MQTT handler in background thread when server starts
            mqtt_thread = threading.Thread(target=start_mqtt_handler, daemon=True)
            mqtt_thread.start()
            print("MQTT Handler started in background thread")
            
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    execute_from_command_line(sys.argv)