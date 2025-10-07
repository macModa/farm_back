#!/usr/bin/env python3
"""
Script de test pour vérifier l'API OpenWeather avec ta clé API
Teste la récupération des données météo pour Bizerte
"""

import requests
import json
from datetime import datetime

# Configuration
API_KEY = "b64f4b22af3619354b9f398481a70644"
CITY = "Bizerte"
BASE_URL = "http://api.openweathermap.org/data/2.5"

def test_openweather_api():
    """Test de l'API OpenWeather"""
    print("🌤️  Test de l'API OpenWeather")
    print("=" * 50)
    print(f"Ville : {CITY}")
    print(f"Clé API : {API_KEY[:8]}..." + "*" * (len(API_KEY) - 8))
    print()
    
    try:
        # URL complète
        url = f"{BASE_URL}/weather"
        params = {
            'q': CITY,
            'appid': API_KEY,
            'units': 'metric',  # Celsius
            'lang': 'fr'  # Français
        }
        
        print(f"🔗 URL de test : {url}")
        print(f"📦 Paramètres : {params}")
        print()
        
        # Requête
        print("📡 Envoi de la requête...")
        response = requests.get(url, params=params, timeout=10)
        
        print(f"📊 Code de réponse : {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Succès ! Données reçues :")
            print("-" * 30)
            
            # Informations principales
            print(f"📍 Ville : {data['name']}, {data['sys']['country']}")
            print(f"🌡️  Température : {data['main']['temp']}°C")
            print(f"💨 Humidité : {data['main']['humidity']}%")
            print(f"☁️  Description : {data['weather'][0]['description']}")
            print(f"💧 Pression : {data['main']['pressure']} hPa")
            
            # Vérifier s'il y a des précipitations
            rain_forecast = 0.0
            if 'rain' in data:
                rain_forecast = data['rain'].get('1h', 0.0)
                print(f"🌧️  Pluie (1h) : {rain_forecast} mm")
            else:
                print("🌧️  Pluie (1h) : 0.0 mm")
            
            print()
            print("🤖 Données formatées pour le projet ESP32 :")
            print("-" * 40)
            
            # Format pour le projet
            weather_data = {
                'temperature': data['main']['temp'],
                'humidity_air': data['main']['humidity'],
                'rain_forecast': rain_forecast,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
            print(json.dumps(weather_data, indent=2))
            
            return True
            
        elif response.status_code == 401:
            print("❌ Erreur d'authentification !")
            print("🔑 Vérifiez votre clé API OpenWeather")
            return False
            
        elif response.status_code == 404:
            print("❌ Ville non trouvée !")
            print(f"🏙️  '{CITY}' n'est pas reconnu par OpenWeather")
            print("💡 Essayez 'Bizerte,TN' ou vérifiez l'orthographe")
            return False
            
        else:
            print(f"❌ Erreur HTTP : {response.status_code}")
            print(f"📄 Réponse : {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de réseau : {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON : {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        return False

if __name__ == "__main__":
    success = test_openweather_api()
    
    if success:
        print("\n🎉 Test réussi ! Votre configuration est correcte.")
        print("👉 Le projet ESP32 IoT peut maintenant utiliser cette API.")
    else:
        print("\n💥 Test échoué ! Vérifiez votre configuration.")
        
    print("\n" + "=" * 50)
    print("Pour lancer le projet complet :")
    print("docker-compose up --build")