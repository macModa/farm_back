#!/usr/bin/env python3
"""
Simulateur de données IoT pour tester le dashboard
Génère des données réalistes avec humidité du sol autour de 40%
"""

import os
import sys
import time
import random
import requests
from datetime import datetime, timedelta
import argparse

# Add Django project to path
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esp32_iot.settings')

import django
django.setup()

from sensor_data.models import SensorData

class IoTDataSimulator:
    def __init__(self):
        self.api_key = "b64f4b22af3619354b9f398481a70644"
        self.city = "Bizerte"
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        # Paramètres de simulation
        self.soil_humidity_base = 40.0  # Humidité du sol de base (40%)
        self.soil_humidity_variation = 15.0  # Variation possible (+/- 15%)
        
        print("🤖 Simulateur de données IoT ESP32")
        print("=" * 40)
        print(f"📍 Localisation : {self.city}")
        print(f"🌱 Humidité sol de base : {self.soil_humidity_base}%")
        print(f"📊 Variation possible : ±{self.soil_humidity_variation}%")
        print()

    def get_weather_data(self):
        """Récupère les données météo réelles depuis OpenWeather API"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': self.city,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            weather_data = {
                'temperature': data['main']['temp'],
                'humidity_air': data['main']['humidity'],
                'rain_forecast': data.get('rain', {}).get('1h', 0.0)
            }
            
            return weather_data
            
        except Exception as e:
            print(f"⚠️  Erreur API météo: {e}")
            # Données météo par défaut pour Bizerte
            return {
                'temperature': random.uniform(18.0, 28.0),
                'humidity_air': random.uniform(60.0, 85.0),
                'rain_forecast': random.choice([0.0, 0.0, 0.0, 0.2, 0.5, 1.0, 2.0])  # Pluie occasionnelle
            }

    def generate_soil_humidity(self, weather_data, hour_of_day, season='spring'):
        """
        Génère une humidité du sol réaliste basée sur plusieurs facteurs
        """
        base_humidity = self.soil_humidity_base
        
        # Facteur météorologique (pluie augmente l'humidité)
        if weather_data['rain_forecast'] > 0:
            rain_bonus = min(weather_data['rain_forecast'] * 5, 20)  # Max +20%
        else:
            rain_bonus = 0
        
        # Facteur temporel (évaporation pendant la journée)
        if 10 <= hour_of_day <= 16:  # Milieu de journée
            time_factor = -5  # Évaporation
        elif 22 <= hour_of_day or hour_of_day <= 6:  # Nuit
            time_factor = +3  # Moins d'évaporation
        else:
            time_factor = 0
        
        # Facteur saisonnier
        season_factors = {
            'spring': 0,
            'summer': -8,  # Plus sec en été
            'autumn': +5,  # Plus humide en automne
            'winter': +3   # Humidité hivernale
        }
        seasonal_factor = season_factors.get(season, 0)
        
        # Facteur de variation aléatoire
        random_variation = random.uniform(-self.soil_humidity_variation/2, self.soil_humidity_variation/2)
        
        # Calcul final
        final_humidity = base_humidity + rain_bonus + time_factor + seasonal_factor + random_variation
        
        # Limiter entre 5% et 95%
        final_humidity = max(5.0, min(95.0, final_humidity))
        
        return round(final_humidity, 1)

    def create_sample_reading(self, timestamp=None, use_real_weather=True):
        """Crée une lecture de capteur simulée"""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # Récupérer les données météo
        if use_real_weather:
            weather_data = self.get_weather_data()
        else:
            weather_data = {
                'temperature': random.uniform(15.0, 30.0),
                'humidity_air': random.uniform(50.0, 80.0),
                'rain_forecast': random.choice([0.0, 0.0, 0.0, 0.5, 1.2])
            }
        
        # Déterminer la saison
        month = timestamp.month
        if month in [12, 1, 2]:
            season = 'winter'
        elif month in [3, 4, 5]:
            season = 'spring'
        elif month in [6, 7, 8]:
            season = 'summer'
        else:
            season = 'autumn'
        
        # Générer l'humidité du sol
        soil_humidity = self.generate_soil_humidity(
            weather_data, 
            timestamp.hour, 
            season
        )
        
        # Créer l'enregistrement
        sensor_data = {
            'timestamp': timestamp,
            'temperature': round(weather_data['temperature'], 1),
            'humidity_air': round(weather_data['humidity_air'], 1),
            'rain_forecast': round(weather_data['rain_forecast'], 1),
            'humidity_soil': soil_humidity
        }
        
        return sensor_data

    def save_reading_to_db(self, reading_data):
        """Sauvegarde une lecture dans MongoDB"""
        try:
            sensor_reading = SensorData(**reading_data)
            sensor_reading.save()
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return False

    def generate_historical_data(self, days_back=7, readings_per_day=48):
        """Génère des données historiques"""
        print(f"📈 Génération de {days_back} jours de données historiques...")
        print(f"📊 {readings_per_day} lectures par jour (toutes les {24*60//readings_per_day} minutes)")
        print()
        
        total_readings = days_back * readings_per_day
        successful_saves = 0
        
        for day in range(days_back, 0, -1):
            day_start = datetime.utcnow() - timedelta(days=day)
            
            for reading_num in range(readings_per_day):
                # Calcul du timestamp pour cette lecture
                minutes_offset = reading_num * (24 * 60 // readings_per_day)
                timestamp = day_start + timedelta(minutes=minutes_offset)
                
                # Générer et sauvegarder la lecture
                reading = self.create_sample_reading(timestamp, use_real_weather=False)
                
                if self.save_reading_to_db(reading):
                    successful_saves += 1
                
                # Affichage du progrès
                progress = ((days_back - day) * readings_per_day + reading_num + 1) / total_readings * 100
                if reading_num % 10 == 0 or reading_num == readings_per_day - 1:
                    print(f"📊 Progrès: {progress:.1f}% - Jour {days_back - day + 1}/{days_back}")
        
        print()
        print(f"✅ Données historiques générées avec succès!")
        print(f"📊 {successful_saves}/{total_readings} lectures sauvegardées")
        return successful_saves

    def run_continuous_simulation(self, interval_seconds=30):
        """Lance la simulation en continu"""
        print(f"🔄 Simulation en continu (intervalle: {interval_seconds}s)")
        print("Appuyez sur Ctrl+C pour arrêter")
        print()
        
        reading_count = 0
        
        try:
            while True:
                reading = self.create_sample_reading(use_real_weather=True)
                
                if self.save_reading_to_db(reading):
                    reading_count += 1
                    print(f"📊 Lecture #{reading_count} - "
                          f"T: {reading['temperature']}°C | "
                          f"HA: {reading['humidity_air']}% | "
                          f"HS: {reading['humidity_soil']}% | "
                          f"P: {reading['rain_forecast']}mm")
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Simulation arrêtée par l'utilisateur")
            print(f"📊 Total de lectures générées: {reading_count}")

    def show_statistics(self):
        """Affiche les statistiques de la base de données"""
        try:
            total_readings = SensorData.objects.count()
            latest_reading = SensorData.objects.order_by('-timestamp').first()
            
            if total_readings == 0:
                print("📊 Aucune donnée dans la base")
                return
            
            # Données des dernières 24h
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=1)
            recent_readings = list(SensorData.get_readings_by_date_range(start_date, end_date))
            
            print("📊 Statistiques de la base de données")
            print("=" * 40)
            print(f"Total d'enregistrements: {total_readings}")
            print(f"Lectures dernières 24h: {len(recent_readings)}")
            
            if latest_reading:
                print(f"Dernière lecture: {latest_reading.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  - Température: {latest_reading.temperature}°C")
                print(f"  - Humidité air: {latest_reading.humidity_air}%")
                print(f"  - Humidité sol: {latest_reading.humidity_soil}%")
                print(f"  - Pluie prévue: {latest_reading.rain_forecast}mm")
            
            if recent_readings:
                soil_humidities = [float(r.humidity_soil) for r in recent_readings]
                avg_soil = sum(soil_humidities) / len(soil_humidities)
                min_soil = min(soil_humidities)
                max_soil = max(soil_humidities)
                
                print(f"\nHumidité du sol (24h):")
                print(f"  - Moyenne: {avg_soil:.1f}%")
                print(f"  - Min: {min_soil:.1f}%")
                print(f"  - Max: {max_soil:.1f}%")
                
        except Exception as e:
            print(f"❌ Erreur lors de l'affichage des statistiques: {e}")

def main():
    parser = argparse.ArgumentParser(description='Simulateur de données IoT ESP32')
    parser.add_argument('--mode', choices=['historical', 'continuous', 'single', 'stats'], 
                        default='historical', help='Mode de simulation')
    parser.add_argument('--days', type=int, default=7, help='Nombre de jours pour les données historiques')
    parser.add_argument('--readings-per-day', type=int, default=48, help='Lectures par jour')
    parser.add_argument('--interval', type=int, default=30, help='Intervalle en secondes pour le mode continu')
    
    args = parser.parse_args()
    
    simulator = IoTDataSimulator()
    
    if args.mode == 'historical':
        simulator.generate_historical_data(args.days, args.readings_per_day)
    elif args.mode == 'continuous':
        simulator.run_continuous_simulation(args.interval)
    elif args.mode == 'single':
        reading = simulator.create_sample_reading()
        if simulator.save_reading_to_db(reading):
            print("✅ Lecture unique créée:")
            print(f"   Température: {reading['temperature']}°C")
            print(f"   Humidité air: {reading['humidity_air']}%")
            print(f"   Humidité sol: {reading['humidity_soil']}%")
            print(f"   Pluie: {reading['rain_forecast']}mm")
    elif args.mode == 'stats':
        simulator.show_statistics()

if __name__ == '__main__':
    main()