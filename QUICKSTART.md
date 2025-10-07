# 🚀 Guide de Démarrage Rapide

## Étapes pour démarrer le projet

### 1. ⚙️ Configuration minimale requise

**Avant de commencer, vous devez :**

1. **Obtenir une clé API OpenWeather** :
   - Aller sur https://openweathermap.org/api
   - Créer un compte gratuit
   - Copier votre clé API

2. **Configurer la clé API** :
   ```bash
   # Éditer docker-compose.yml
   nano docker-compose.yml
   
   # Remplacer cette ligne :
   OPENWEATHER_API_KEY: "YOUR_OPENWEATHER_API_KEY_HERE"
   # Par :
   OPENWEATHER_API_KEY: "votre_vraie_cle_api"
   ```

### 2. 🐳 Lancer le projet

```bash
# Se placer dans le répertoire du projet
cd esp32_iot_project

# Construire et lancer tous les services
docker-compose up --build

# Ou en arrière-plan
docker-compose up --build -d
```

### 3. ✅ Vérifier que tout fonctionne

**Services disponibles :**
- API Django : http://localhost:8000/api/readings/latest/
- Dashboard EMQX : http://localhost:18083 (admin/public)
- MongoDB : localhost:27017

**Test rapide de l'API :**
```bash
curl http://localhost:8000/api/readings/latest/
```

### 4. 📡 Simuler des données ESP32

**Option A - Avec mosquitto_pub (si installé) :**
```bash
mosquitto_pub -h u2cc2628.ala.dedicated.aws.emqxcloud.com -t esp32/humidity_soil -m "45.7"
```

**Option B - Depuis le container EMQX :**
```bash
# Entrer dans le container EMQX
docker-compose exec emqx sh

# Publier des données de test
mosquitto_pub -h u2cc2628.ala.dedicated.aws.emqxcloud.com -t esp32/humidity_soil -m "42.3"
```

**Option C - Via le dashboard EMQX :**
1. Aller sur http://localhost:18083
2. Login : admin / public  
3. Tools > WebSocket Client
4. Connect to: u2cc2628.ala.dedicated.aws.emqxcloud.com:8083
5. Publish to topic: `esp32/humidity_soil` with payload: `55.2`

### 5. 📊 Vérifier les données

```bash
# Voir les dernières données reçues
curl http://localhost:8000/api/readings/latest/?limit=5

# Voir les statistiques
curl http://localhost:8000/api/statistics/
```

### 6. 📈 Export pour IA

```bash
# Export simple
docker-compose exec django_app python scripts/export_to_csv.py -o /tmp/data.csv

# Export avec features ML  
docker-compose exec django_app python scripts/export_to_csv.py -o /tmp/training.csv --features

# Récupérer les fichiers depuis le container
docker cp esp32_django:/tmp/data.csv ./exported_data.csv
```

## 🔧 Configuration ESP32

**Code minimal à flasher sur votre ESP32 :**

```cpp
#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "VOTRE_WIFI";
const char* password = "VOTRE_PASSWORD";
const char* mqtt_server = "u2cc2628.ala.dedicated.aws.emqxcloud.com";

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) {
    client.connect("ESP32Client");
  }
  client.loop();
  
  // Lire capteur (exemple)
  float humidity = analogRead(A0) * 100.0 / 4095.0;
  
  // Publier
  client.publish("esp32/humidity_soil", String(humidity).c_str());
  
  delay(30000); // 30 secondes
}
```

## 🛠️ Commandes utiles

```bash
# Voir les logs en temps réel
docker-compose logs -f

# Redémarrer un service
docker-compose restart django_app

# Arrêter tous les services
docker-compose down

# Nettoyer complètement
docker-compose down -v
docker system prune -a
```

## 🚨 Dépannage rapide

**Problème : API OpenWeather échoue**
- Vérifiez votre clé API dans docker-compose.yml
- Testez la clé : `curl "http://api.openweathermap.org/data/2.5/weather?q=Tunis&appid=VOTRE_CLE"`

**Problème : MQTT ne se connecte pas**
- Vérifiez la connectivité : `ping u2cc2628.ala.dedicated.aws.emqxcloud.com`
- Vérifiez les logs : `docker-compose logs django_app | grep mqtt`

**Problème : MongoDB échoue**
- Vérifiez l'URI MongoDB dans docker-compose.yml
- Testez la connexion depuis votre IP sur MongoDB Atlas

**Problème : ESP32 ne se connecte pas**
- Vérifiez le WiFi et les identifiants
- Vérifiez le topic MQTT (`esp32/humidity_soil`)
- Utilisez le Serial Monitor pour débugger

## 🎯 Prêt pour l'IA !

Une fois que des données sont collectées, utilisez le script d'export pour générer vos datasets d'entraînement avec toutes les features calculées automatiquement.

Le système est maintenant opérationnel et prêt à collecter vos données IoT ! 🎉