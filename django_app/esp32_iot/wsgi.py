import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esp32_iot.settings')

# Import Django after setting up the environment
import django
django.setup()

# Now import the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Import and start MQTT handler after Django is fully loaded
try:
    from mqtt_handler import MQTTClient
    from esp32_iot import settings as app_settings
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('wsgi')
    
    # Initialize MQTT client
    logger.info("Initializing MQTT client...")
    mqtt_client = MQTTClient()
    mqtt_client.start()
    logger.info("MQTT Handler started successfully!")
except ImportError as e:
    logger.error(f"Error importing MQTT handler: {e}", exc_info=True)
except Exception as e:
    logger.error(f"Error starting MQTT client: {e}", exc_info=True)