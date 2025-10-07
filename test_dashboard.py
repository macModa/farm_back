#!/usr/bin/env python3
"""
Script de test pour lancer le dashboard Django sans Docker
Génère des données de test et lance le serveur de développement
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

# Configuration des chemins
PROJECT_DIR = Path(__file__).parent
DJANGO_DIR = PROJECT_DIR / 'django_app'
SCRIPTS_DIR = PROJECT_DIR / 'scripts'

def setup_django_environment():
    """Configure l'environnement Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esp32_iot.settings')
    
    # Variables d'environnement pour la configuration
    os.environ['MONGODB_URI'] = 'mongodb+srv://jesssser93_db_user:FydCbJAO4CqguvLu@cluster0.5y36wng.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
    os.environ['MONGODB_DB_NAME'] = 'esp32_iot_data'
    os.environ['OPENWEATHER_API_KEY'] = 'b64f4b22af3619354b9f398481a70644'
    os.environ['OPENWEATHER_CITY'] = 'Bizerte'
    os.environ['DEBUG'] = 'True'
    os.environ['SECRET_KEY'] = 'django-insecure-esp32-iot-project-test-key'

def install_requirements():
    """Installe les dépendances Python"""
    requirements_file = PROJECT_DIR / 'requirements.txt'
    
    if requirements_file.exists():
        print("📦 Installation des dépendances...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)], 
                         check=True, capture_output=True)
            print("✅ Dépendances installées")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Erreur d'installation des dépendances: {e}")
            print("Continuons avec les packages existants...")
    else:
        print("⚠️  Fichier requirements.txt non trouvé")

def generate_test_data():
    """Génère des données de test"""
    print("\n🎲 Génération de données de test...")
    
    sys.path.insert(0, str(DJANGO_DIR))
    sys.path.insert(0, str(SCRIPTS_DIR))
    
    try:
        # Import du simulateur
        from scripts.data_simulator import IoTDataSimulator
        
        # Créer le simulateur
        simulator = IoTDataSimulator()
        
        # Générer quelques données historiques (2 jours, 24 lectures par jour)
        print("📊 Génération de 2 jours de données historiques...")
        simulator.generate_historical_data(days_back=2, readings_per_day=24)
        
        # Afficher les statistiques
        simulator.show_statistics()
        
        print("✅ Données de test générées avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération des données: {e}")
        print("Le dashboard fonctionnera sans données de test.")

def run_django_server():
    """Lance le serveur Django"""
    print("\n🚀 Démarrage du serveur Django...")
    
    manage_py = DJANGO_DIR / 'manage.py'
    
    if not manage_py.exists():
        print(f"❌ manage.py non trouvé dans {DJANGO_DIR}")
        return
    
    try:
        # Changer vers le répertoire Django
        os.chdir(DJANGO_DIR)
        
        # Lancer le serveur
        print("🌐 Serveur accessible sur: http://localhost:8000/")
        print("📊 Dashboard disponible sur: http://localhost:8000/dashboard/")
        print("🔌 API REST disponible sur: http://localhost:8000/api/")
        print("\nAppuyez sur Ctrl+C pour arrêter le serveur")
        
        subprocess.run([sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'])
        
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage du serveur: {e}")

def test_api_endpoints():
    """Teste les endpoints de l'API"""
    print("\n🧪 Test des endpoints API...")
    
    try:
        import requests
        
        base_url = "http://localhost:8000/api"
        endpoints = [
            "/readings/latest/",
            "/statistics/",
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {endpoint}: OK")
                else:
                    print(f"⚠️  {endpoint}: Status {response.status_code}")
            except requests.exceptions.RequestException:
                print(f"❌ {endpoint}: Inaccessible")
                
    except ImportError:
        print("⚠️  Module 'requests' non disponible pour tester les API")

def main():
    print("🤖 ESP32 IoT Dashboard - Test sans Docker")
    print("=" * 50)
    
    # Configuration de l'environnement
    setup_django_environment()
    
    # Installation des dépendances
    install_requirements()
    
    # Génération des données de test
    generate_test_data()
    
    print("\n" + "=" * 50)
    print("🎉 Configuration terminée!")
    print("📋 Pour utiliser le dashboard:")
    print("   1. Le serveur va démarrer automatiquement")
    print("   2. Ouvrez votre navigateur sur http://localhost:8000")
    print("   3. Le dashboard sera accessible avec des données de test")
    print("=" * 50)
    
    input("\nAppuyez sur Entrée pour lancer le serveur Django...")
    
    # Lancement du serveur Django
    run_django_server()

def quick_test():
    """Test rapide de l'API"""
    setup_django_environment()
    
    print("🔍 Test rapide de l'API...")
    
    # Démarrer le serveur en arrière-plan
    server_thread = threading.Thread(target=run_django_server, daemon=True)
    server_thread.start()
    
    # Attendre que le serveur démarre
    time.sleep(3)
    
    # Tester les endpoints
    test_api_endpoints()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test du dashboard ESP32 IoT')
    parser.add_argument('--quick-test', action='store_true', 
                       help='Test rapide des API sans interface')
    
    args = parser.parse_args()
    
    if args.quick_test:
        quick_test()
    else:
        main()