import os
from pathlib import Path
import mongoengine

# ------------------------------
# BASE DJANGO CONFIG
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-esp32-iot-project-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sensor_data',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'esp32_iot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'esp32_iot.wsgi.application'

# ------------------------------
# MONGODB ATLAS CONFIG
# ------------------------------
MONGODB_SETTINGS = {
    "db": "farmdb",
    "host": "mongodb+srv://jmihoussem552_db_user:pLhziopH28UmvNbo@cluster0.i2ke9ev.mongodb.net/farmdb?retryWrites=true&w=majority",
    "tls": True,
    "tlsAllowInvalidCertificates": True,  # pour éviter SSL sur Windows
}

try:
    # éviter erreur “alias default already registered”
    mongoengine.disconnect(alias='default')
    mongoengine.connect(**MONGODB_SETTINGS)
    print("✅ MongoDB connected successfully to:", MONGODB_SETTINGS["host"])
except Exception as e:
    print(f"❌ MongoDB connection error: {e}")

# ------------------------------
# MQTT CONFIG
# ------------------------------
MQTT_SETTINGS = {
    'BROKER_HOST': os.getenv('MQTT_BROKER_HOST', 'j2a24bbb.ala.dedicated.aws.emqxcloud.com'),
    'BROKER_PORT': int(os.getenv('MQTT_BROKER_PORT', '1883')),
    'USERNAME': os.getenv('MQTT_USERNAME', 'esp32_user'),
    'PASSWORD': os.getenv('MQTT_PASSWORD', 'esp32_pass'),
    'TOPIC': 'esp32/humidity_soil',
}

# ------------------------------
# OPENWEATHER CONFIG
# ------------------------------
OPENWEATHER_SETTINGS = {
    'API_KEY': os.getenv('OPENWEATHER_API_KEY', '0b5d680180d9c99eecfebfd9982873fd'),
    'CITY': os.getenv('OPENWEATHER_CITY', 'Tunis'),
    'BASE_URL': 'https://api.openweathermap.org/data/2.5'
}

# ------------------------------
# SQLITE (pour Django Admin)
# ------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ------------------------------
# AUTRES PARAMÈTRES DJANGO
# ------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ------------------------------
# LOGGING CONFIG
# ------------------------------
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'mqtt.log'),
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'mqtt_handler': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
