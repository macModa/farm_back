from mongoengine import Document, FloatField, DateTimeField
from datetime import datetime

class SensorData(Document):
    """
    MongoDB document for storing ESP32 and weather sensor data
    """
    timestamp = DateTimeField(default=datetime.utcnow, required=True)
    temperature = FloatField(required=True, help_text="Temperature in Celsius from OpenWeather API")
    humidity_air = FloatField(required=True, help_text="Air humidity percentage from OpenWeather API")
    rain_forecast = FloatField(required=True, help_text="Rain forecast in mm from OpenWeather API")
    humidity_soil = FloatField(required=True, help_text="Soil humidity percentage from ESP32 sensor")
    
    meta = {
        'collection': 'sensor_readings',
        'indexes': ['timestamp'],
        'ordering': ['-timestamp']
    }
    
    def __str__(self):
        return f"SensorData({self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - Soil: {self.humidity_soil}%, Air: {self.humidity_air}%, Temp: {self.temperature}°C)"
    
    def to_dict(self):
        """Convert document to dictionary for JSON serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'temperature': float(self.temperature),
            'humidity_air': float(self.humidity_air),
            'rain_forecast': float(self.rain_forecast),
            'humidity_soil': float(self.humidity_soil)
        }
    
    @classmethod
    def get_latest_readings(cls, limit=10):
        """Get the latest sensor readings"""
        return cls.objects.order_by('-timestamp')[:limit]
    
    @classmethod
    def get_readings_by_date_range(cls, start_date, end_date):
        """Get readings within a date range"""
        return cls.objects.filter(timestamp__gte=start_date, timestamp__lte=end_date).order_by('-timestamp')