import os
from pathlib import Path
import mongoengine

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-esp32-iot-project-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = ['*']

# Application definition
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

# MongoDB Configuration
MONGODB_SETTINGS = {
    'host': os.getenv(
        'MONGODB_URI',
        'mongodb+srv://jesssser93_db_user:FydCbJAO4CqguvLu@cluster0.5y36wng.mongodb.net/farmdb?retryWrites=true&w=majority&tls=true'
    ),
    'db': os.getenv('MONGODB_DB_NAME', 'esp32_iot_data'),
}


# Connect to MongoDB
try:
    mongoengine.connect(**MONGODB_SETTINGS)
    print("MongoDB connected successfully!")
except Exception as e:
    print(f"MongoDB connection error: {e}")

# MQTT Configuration
MQTT_SETTINGS = {
    'BROKER_HOST': os.getenv('MQTT_BROKER_HOST', 'u2cc2628.ala.dedicated.aws.emqxcloud.com'),
    'BROKER_PORT': int(os.getenv('MQTT_BROKER_PORT', '1883')),
    'USERNAME': os.getenv('MQTT_USERNAME', 'esp32_user'),
    'PASSWORD': os.getenv('MQTT_PASSWORD', 'esp32_pass'),
    'TOPIC': 'esp32/humidity_soil',
}

# OpenWeather API Configuration
OPENWEATHER_SETTINGS = {
    'API_KEY': os.getenv('OPENWEATHER_API_KEY', '0b5d680180d9c99eecfebfd9982873fd'),
    'CITY': os.getenv('OPENWEATHER_CITY', 'Tunis'),
    'BASE_URL': 'https://api.openweathermap.org/data/2.5'
}

# Database (SQLite for Django admin, but we use MongoDB for data storage)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging configuration
import os

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
        'mqtt': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
    },
}
import os
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

