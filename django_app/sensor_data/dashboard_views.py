from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from .models import SensorData
import json

def dashboard_home(request):
    """Page d'accueil du tableau de bord"""
    try:
        # Statistiques générales
        total_readings = SensorData.objects.count()
        latest_reading = SensorData.objects.order_by('-timestamp').first()
        
        # Données des dernières 24h
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=1)
        recent_readings = list(SensorData.get_readings_by_date_range(start_date, end_date))
        
        context = {
            'total_readings': total_readings,
            'latest_reading': latest_reading,
            'recent_count': len(recent_readings),
            'page_title': 'Dashboard IoT - ESP32 Station Météo'
        }
        
        return render(request, 'dashboard/home.html', context)
    
    except Exception as e:
        context = {
            'error': str(e),
            'page_title': 'Dashboard IoT - Erreur'
        }
        return render(request, 'dashboard/home.html', context)

def dashboard_charts(request):
    """Page des graphiques avancés"""
    return render(request, 'dashboard/charts.html', {
        'page_title': 'Graphiques Avancés - IoT Dashboard'
    })

def dashboard_data_table(request):
    """Page du tableau de données"""
    return render(request, 'dashboard/data_table.html', {
        'page_title': 'Données Détaillées - IoT Dashboard'
    })

def dashboard_analytics(request):
    """Page d'analyse et statistiques"""
    return render(request, 'dashboard/analytics.html', {
        'page_title': 'Analytics - IoT Dashboard'
    })

# API Endpoints pour les graphiques
@require_http_methods(["GET"])
def api_chart_data(request):
    """API pour récupérer les données des graphiques"""
    try:
        # Paramètres
        hours = int(request.GET.get('hours', 24))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=hours)
        
        readings = SensorData.get_readings_by_date_range(start_date, end_date)
        
        # Format pour Chart.js
        chart_data = {
            'labels': [],
            'datasets': {
                'temperature': [],
                'humidity_air': [],
                'humidity_soil': [],
                'rain_forecast': []
            }
        }
        
        for reading in readings:
            chart_data['labels'].append(reading.timestamp.strftime('%H:%M'))
            chart_data['datasets']['temperature'].append(float(reading.temperature))
            chart_data['datasets']['humidity_air'].append(float(reading.humidity_air))
            chart_data['datasets']['humidity_soil'].append(float(reading.humidity_soil))
            chart_data['datasets']['rain_forecast'].append(float(reading.rain_forecast))
        
        return JsonResponse({
            'status': 'success',
            'data': chart_data,
            'count': len(readings),
            'period_hours': hours
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_http_methods(["GET"])
def api_realtime_data(request):
    """API pour données en temps réel (dernière lecture)"""
    try:
        latest_reading = SensorData.objects.order_by('-timestamp').first()
        
        if not latest_reading:
            return JsonResponse({
                'status': 'success',
                'data': None,
                'message': 'Aucune donnée disponible'
            })
        
        data = {
            'timestamp': latest_reading.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'temperature': float(latest_reading.temperature),
            'humidity_air': float(latest_reading.humidity_air),
            'humidity_soil': float(latest_reading.humidity_soil),
            'rain_forecast': float(latest_reading.rain_forecast),
            'time_ago': get_time_ago(latest_reading.timestamp)
        }
        
        return JsonResponse({
            'status': 'success',
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_http_methods(["GET"])
def api_statistics_summary(request):
    """API pour résumé statistique"""
    try:
        # Données des dernières 24h
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=1)
        readings = list(SensorData.get_readings_by_date_range(start_date, end_date))
        
        if not readings:
            return JsonResponse({
                'status': 'success',
                'data': None,
                'message': 'Aucune donnée disponible'
            })
        
        # Calculs statistiques
        temperatures = [float(r.temperature) for r in readings]
        humidity_air = [float(r.humidity_air) for r in readings]
        humidity_soil = [float(r.humidity_soil) for r in readings]
        rain_forecasts = [float(r.rain_forecast) for r in readings]
        
        stats = {
            'total_readings': len(readings),
            'last_update': readings[0].timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'temperature': {
                'current': temperatures[0],
                'avg': round(sum(temperatures) / len(temperatures), 1),
                'min': min(temperatures),
                'max': max(temperatures)
            },
            'humidity_air': {
                'current': humidity_air[0],
                'avg': round(sum(humidity_air) / len(humidity_air), 1),
                'min': min(humidity_air),
                'max': max(humidity_air)
            },
            'humidity_soil': {
                'current': humidity_soil[0],
                'avg': round(sum(humidity_soil) / len(humidity_soil), 1),
                'min': min(humidity_soil),
                'max': max(humidity_soil)
            },
            'rain_forecast': {
                'current': rain_forecasts[0],
                'avg': round(sum(rain_forecasts) / len(rain_forecasts), 1),
                'total_predicted': sum(rain_forecasts)
            }
        }
        
        return JsonResponse({
            'status': 'success',
            'data': stats
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def get_time_ago(timestamp):
    """Calcule le temps écoulé depuis un timestamp"""
    now = datetime.utcnow()
    diff = now - timestamp
    
    if diff.seconds < 60:
        return f"{diff.seconds}s"
    elif diff.seconds < 3600:
        return f"{diff.seconds // 60}min"
    elif diff.days < 1:
        return f"{diff.seconds // 3600}h"
    else:
        return f"{diff.days}j"