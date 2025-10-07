# 📊 Guide du Dashboard IoT Professionnel

## 🎯 Vue d'ensemble

Le dashboard ESP32 IoT est une interface web professionnelle pour visualiser et analyser les données de votre station météo connectée. Il combine des données de capteurs ESP32 (humidité du sol) avec des données météorologiques en temps réel.

### ✨ Fonctionnalités Principales

- **📊 Visualisation temps réel** : Cartes statistiques animées avec données actuelles
- **📈 Graphiques interactifs** : Chart.js avec données historiques sur 6h, 24h ou 7 jours
- **🎨 Interface moderne** : Design Bootstrap 5 avec animations CSS et gradients
- **📱 Responsive** : Compatible mobile, tablette et desktop
- **🔄 Auto-refresh** : Mise à jour automatique toutes les 30 secondes
- **⚡ Performance** : API REST rapides avec MongoDB optimisé

## 🚀 Démarrage Rapide

### Option 1: Test sans Docker (Recommandé pour le développement)

```bash
# Se placer dans le projet
cd esp32_iot_project

# Lancer le script de test (installe automatiquement les dépendances)
python3 test_dashboard.py

# Le script va :
# 1. Installer les dépendances Python
# 2. Générer des données de test avec humidité sol ~40%
# 3. Lancer le serveur Django sur http://localhost:8000
```

### Option 2: Avec Docker (Production)

```bash
# Avec Docker Compose
docker-compose up --build

# Dashboard accessible sur http://localhost:8000
```

## 📊 Interface Dashboard

### 🏠 Page d'Accueil (`/dashboard/`)

**Cartes Statistiques** :
- **🌡️ Température** : Données météo actuelles avec tendance (Froid/Modéré/Chaud)
- **☁️ Humidité Air** : Pourcentage d'humidité atmosphérique
- **🌱 Humidité Sol** : Donnée ESP32 avec classification (Sec/Normal/Humide)
- **🌧️ Pluie Prévue** : Prévisions de précipitations en mm

**Graphique Principal** :
- Évolution temporelle de toutes les métriques
- Boutons de période : 6h, 24h, 7 jours
- Double axe Y pour optimiser l'affichage
- Tooltips interactifs sur survol

**Panneau Statut** :
- État de connexion ESP32, API météo, base de données
- Total des lectures enregistrées
- Activité récente avec horodatage

### 📈 Pages Spécialisées

**Graphiques (`/dashboard/charts/`)** :
- Graphiques avancés et analyses détaillées
- Comparaisons multi-périodes
- Graphiques spécialisés par métrique

**Données (`/dashboard/data-table/)** :
- Tableau paginé avec toutes les lectures
- Filtres par date et valeurs
- Export CSV intégré

**Analytics (`/dashboard/analytics/`)** :
- Statistiques avancées et tendances
- Analyses prédictives
- Rapports personnalisés

## 🔧 Configuration des Données de Test

Le simulateur génère des données réalistes avec humidité du sol centrée sur 40% :

### Facteurs de Variation de l'Humidité du Sol

1. **Base** : 40% (configurable)
2. **Météo** : +5 à +20% si pluie prévue
3. **Heure** : -5% en journée (évaporation), +3% la nuit
4. **Saison** : 
   - Été: -8% (plus sec)
   - Automne: +5% (plus humide)  
   - Hiver: +3%
   - Printemps: neutre
5. **Variation aléatoire** : ±7.5%

### Commandes du Simulateur

```bash
# Générer 7 jours de données historiques
python3 scripts/data_simulator.py --mode historical --days 7

# Générer en continu (simulation ESP32)
python3 scripts/data_simulator.py --mode continuous --interval 30

# Lecture unique de test
python3 scripts/data_simulator.py --mode single

# Voir les statistiques
python3 scripts/data_simulator.py --mode stats
```

## 🎨 Personnalisation Visuelle

### Couleurs du Thème

```css
:root {
    --primary-color: #2c3e50;      /* Bleu foncé principal */
    --secondary-color: #3498db;    /* Bleu clair */
    --success-color: #27ae60;      /* Vert succès */
    --warning-color: #f39c12;      /* Orange alerte */
    --danger-color: #e74c3c;       /* Rouge erreur */
}
```

### Gradients des Cartes

- **Température** : Rose → Violet (`#ff9a9e` → `#fecfef`)
- **Humidité** : Cyan → Rose (`#a8edea` → `#fed6e3`)
- **Pluie** : Bleu clair → Bleu foncé (`#74b9ff` → `#0984e3`)
- **Sol** : Bleu → Bleu foncé (`#55a3ff` → `#003d82`)

### Animations

- **Entrée** : `animate__fadeInUp` avec délais échelonnés
- **Hover** : Élévation des cartes (`translateY(-5px)`)
- **Statut** : Animation `pulse` pour l'indicateur en ligne
- **Transitions** : `0.3s ease` pour toutes les interactions

## 🔌 API REST

### Endpoints Disponibles

```bash
# Données temps réel
GET /api/readings/latest/?limit=10

# Données par période
GET /api/readings/by-date/?start_date=2024-01-01&end_date=2024-01-07

# Statistiques générales
GET /api/statistics/

# API Dashboard (utilisées par l'interface)
GET /dashboard/api/realtime/
GET /dashboard/api/chart-data/?hours=24
GET /dashboard/api/statistics/
```

### Format des Données

```json
{
  "status": "success",
  "data": {
    "timestamp": "2024-01-07T14:30:00Z",
    "temperature": 22.5,
    "humidity_air": 65.3,
    "rain_forecast": 0.0,
    "humidity_soil": 42.1
  }
}
```

## 📈 Export des Données

### Pour l'Entraînement IA

```bash
# Export simple
python3 scripts/export_to_csv.py -o sensor_data.csv

# Export avec features calculées pour ML
python3 scripts/export_to_csv.py -o training_data.csv --features

# Features générées automatiquement :
# - hour_of_day, day_of_week, month, season
# - temperature_humidity_air_ratio
# - soil_air_humidity_diff  
# - is_rain_predicted (0/1)
```

## 🛠️ Développement et Debug

### Structure des Templates

```
sensor_data/templates/dashboard/
├── base.html           # Template de base avec Bootstrap 5
├── home.html          # Page d'accueil du dashboard
├── charts.html        # Graphiques avancés
├── data_table.html    # Tableau de données
└── analytics.html     # Page analytics
```

### JavaScript Principal

- **Chart.js 4.4.0** : Graphiques interactifs
- **Bootstrap 5.3.0** : Framework CSS
- **Font Awesome 6.4.0** : Icônes
- **Animate.css 4.1.1** : Animations

### Debug Mode

```bash
# Variables d'environnement de debug
export DEBUG=True
export MONGODB_URI="votre_uri_mongodb"
export OPENWEATHER_API_KEY="votre_cle_api"

# Lancer en mode debug
python3 django_app/manage.py runserver --settings=esp32_iot.settings
```

## 📊 Métriques et Performance

### Base de Données

- **MongoDB Atlas** : Base cloud avec réplication
- **Indexation** : Index sur `timestamp` pour requêtes rapides
- **Sharding** : Optimisé pour les séries temporelles

### Caching

- Données temps réel mises en cache 30s
- Graphiques mis en cache par période
- API REST avec cache headers appropriés

### Responsive Breakpoints

- **Mobile** : < 768px (cartes empilées)
- **Tablette** : 768px - 1024px (layout adaptatif)
- **Desktop** : > 1024px (layout complet)

## 🔒 Sécurité et Production

### Recommandations

1. **HTTPS** : Activez SSL/TLS en production
2. **Secrets** : Utilisez des variables d'environnement
3. **CORS** : Configurez les origines autorisées
4. **Rate Limiting** : Limitez les requêtes API
5. **Monitoring** : Ajoutez des logs et métriques

### Variables d'Environnement

```bash
# Production
DEBUG=False
SECRET_KEY="votre-cle-secrete-longue-et-complexe"
ALLOWED_HOSTS="votre-domaine.com,www.votre-domaine.com"
MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/db"
OPENWEATHER_API_KEY="votre_cle_api"
```

## 🎯 Cas d'Usage

### Agriculture de Précision

- Surveillance de l'humidité du sol en temps réel
- Alertes d'irrigation basées sur les seuils
- Corrélation avec données météorologiques
- Historique pour optimiser les cycles de culture

### Smart Garden

- Monitoring automatique du jardin connecté
- Notifications push sur smartphone
- Prédictions d'arrosage intelligentes
- Analytics de croissance des plantes

### Station Météo

- Collecte multi-capteurs centralisée
- Dashboard public de données météo locales
- API ouverte pour applications tierces
- Archive historique complète

---

## 📞 Support

Le dashboard est entièrement configuré et prêt à l'emploi. Pour toute question :

1. Vérifiez les logs Django : `python3 manage.py runserver`
2. Consultez les APIs : http://localhost:8000/api/
3. Testez les données : `python3 scripts/data_simulator.py --mode stats`

**Dashboard professionnel ESP32 IoT - Prêt pour la production ! 🚀**