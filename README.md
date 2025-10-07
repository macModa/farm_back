# ESP32 IoT Project - Django MQTT Weather Station

Un projet IoT complet utilisant ESP32, MQTT, Django et MongoDB pour collecter et analyser les données de capteurs météorologiques et d'humidité du sol.

## 🏗️ Architecture

- **ESP32** : Envoie l'humidité du sol via MQTT
- **EMQX Cloud** : Broker MQTT hébergé dans le cloud  
- **Django** : Backend API REST
- **MongoDB Atlas** : Base de données cloud pour le stockage
- **OpenWeather API** : Données météorologiques en temps réel
- **Docker** : Containerisation complète

## 📊 Structure des données

Chaque enregistrement contient :
```json
{
  "timestamp": "2024-01-07T14:30:00Z",
  "temperature": 22.5,
  "humidity_air": 65.3,
  "rain_forecast": 0.0,
  "humidity_soil": 45.8
}
```

## 🚀 Démarrage rapide

### Prérequis
- Docker et Docker Compose installés
- Clé API OpenWeatherMap

### Configuration

1. **Cloner le projet** :
   ```bash
   git clone <repo-url>
   cd esp32_iot_project
   ```

2. **Configurer la clé API OpenWeather** :
   Éditer `docker-compose.yml` et remplacer :
   ```yaml
   OPENWEATHER_API_KEY: "VOTRE_CLE_API_ICI"
   ```

3. **Lancer le projet** :
   ```bash
   docker-compose up --build
   ```

### Services disponibles

- **Django API** : http://localhost:8000
- **EMQX Dashboard** : http://localhost:18083 (admin/public)
- **MongoDB** : localhost:27017

## 📡 Configuration ESP32

Code ESP32 pour envoyer l'humidité du sol :

```cpp
#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "VOTRE_WIFI";
const char* password = "VOTRE_MOT_DE_PASSE";
const char* mqtt_server = "u2cc2628.ala.dedicated.aws.emqxcloud.com";
const int mqtt_port = 1883;
const char* topic = "esp32/humidity_soil";

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  // Lire le capteur d'humidité du sol
  float humidity_soil = analogRead(A0) * 100.0 / 4095.0; // Exemple
  
  // Publier les données
  String payload = String(humidity_soil);
  client.publish(topic, payload.c_str());
  
  delay(30000); // Envoyer toutes les 30 secondes
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("ESP32Client")) {
      Serial.println("Connected to MQTT");
    } else {
      delay(5000);
    }
  }
}
```

## 🔌 API Endpoints

### Données en temps réel
- `GET /api/readings/latest/` - Dernières lectures
- `GET /api/readings/by-date/` - Lectures par période
- `GET /api/statistics/` - Statistiques des dernières 24h

### Exemples d'utilisation

```bash
# Obtenir les 10 dernières lectures
curl http://localhost:8000/api/readings/latest/?limit=10

# Obtenir les données des 7 derniers jours
curl "http://localhost:8000/api/readings/by-date/?start_date=2024-01-01&end_date=2024-01-07"

# Obtenir les statistiques
curl http://localhost:8000/api/statistics/
```

## 📈 Export des données pour IA

### Script d'export CSV

```bash
# Export simple
python scripts/export_to_csv.py -o sensor_data.csv

# Export avec features pour ML
python scripts/export_to_csv.py -o training_data.csv --features

# Export des 30 derniers jours
python scripts/export_to_csv.py -o monthly_data.csv --last-days 30

# Export avec limite
python scripts/export_to_csv.py -o sample_data.csv --limit 1000
```

### Features calculées pour ML

Le script génère automatiquement :
- `hour_of_day` - Heure de la journée (0-23)
- `day_of_week` - Jour de la semaine (0-6)
- `month` - Mois (1-12)
- `season` - Saison (spring, summer, autumn, winter)
- `temperature_humidity_air_ratio` - Ratio température/humidité air
- `soil_air_humidity_diff` - Différence humidité sol/air
- `is_rain_predicted` - Prédiction de pluie (0/1)

## 🐳 Services Docker

### Construction et démarrage
```bash
docker-compose up --build -d
```

### Logs en temps réel
```bash
docker-compose logs -f django_app
docker-compose logs -f emqx
docker-compose logs -f mongodb
```

### Redémarrage d'un service
```bash
docker-compose restart django_app
```

## 🔧 Configuration avancée

### Variables d'environnement importantes

```yaml
# MongoDB
MONGODB_URI: "mongodb+srv://user:pass@cluster.mongodb.net/db"
MONGODB_DB_NAME: "esp32_iot_data"

# MQTT
MQTT_BROKER_HOST: "u2cc2628.ala.dedicated.aws.emqxcloud.com"
MQTT_BROKER_PORT: "1883"
MQTT_USERNAME: ""
MQTT_PASSWORD: ""

# OpenWeather
OPENWEATHER_API_KEY: "votre_cle_api"
OPENWEATHER_CITY: "Tunis"
```

## 🧪 Test du système

### Simuler des données ESP32
```bash
# Test avec mosquitto_pub
mosquitto_pub -h u2cc2628.ala.dedicated.aws.emqxcloud.com -t esp32/humidity_soil -m "42.5"

# Test avec JSON
mosquitto_pub -h u2cc2628.ala.dedicated.aws.emqxcloud.com -t esp32/humidity_soil -m '{"humidity_soil": 42.5}'
```

## 📁 Structure du projet

```
esp32_iot_project/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── django_app/
│   ├── esp32_iot/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── sensor_data/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   └── manage.py
├── mqtt_handler/
│   ├── mqtt_client.py
│   └── __init__.py
└── scripts/
    └── export_to_csv.py
```

## 🛠️ Dépannage

### Erreurs communes

1. **Connexion MQTT échoue** :
   - Vérifier les identifiants EMQX
   - Vérifier la connectivité réseau

2. **API OpenWeather échoue** :
   - Vérifier la clé API dans docker-compose.yml
   - Vérifier le nom de la ville

3. **MongoDB non accessible** :
   - Vérifier l'URI de connexion MongoDB Atlas
   - Vérifier les autorisations IP

### Logs utiles
```bash
# Logs MQTT
docker-compose logs django_app | grep mqtt

# Logs MongoDB
docker-compose logs mongodb

# Logs complets
docker-compose logs --tail=50 -f
```

## 🎯 Utilisation pour l'IA

### Cas d'usage ML possibles

1. **Prédiction d'irrigation** : Prédire quand arroser selon la météo
2. **Classification climatique** : Classifier les conditions météo
3. **Détection d'anomalies** : Identifier des lectures anormales
4. **Optimisation énergétique** : Optimiser la consommation des capteurs

### Pipeline ML recommandé

1. Export des données avec features
2. Preprocessing (normalisation, gestion des valeurs manquantes)
3. Division train/test
4. Entraînement du modèle
5. Évaluation et déploiement

## 🔒 Sécurité

- Changez les mots de passe par défaut
- Utilisez HTTPS en production
- Configurez les certificats SSL/TLS pour MQTT
- Limitez l'accès réseau MongoDB

## 📞 Support

Pour des questions ou problèmes :
- Vérifiez les logs Docker
- Consultez la documentation des APIs utilisées
- Vérifiez la configuration réseau

---

**Note** : Ce projet est configuré pour fonctionner avec vos identifiants cloud EMQX et MongoDB Atlas. Assurez-vous que ces services sont accessibles et configurés correctement.# farm_back
# farm_back
