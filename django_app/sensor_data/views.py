from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import json

from .models import SensorData

@require_http_methods(["GET"])
def get_latest_readings(request):
    """API endpoint to get latest sensor readings"""
    try:
        limit = int(request.GET.get('limit', 10))
        readings = SensorData.get_latest_readings(limit)
        
        data = {
            'status': 'success',
            'count': len(readings),
            'data': [reading.to_dict() for reading in readings]
        }
        
        return JsonResponse(data)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_readings_by_date(request):
    """API endpoint to get readings by date range"""
    try:
        # Get date parameters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        
        if not start_date_str or not end_date_str:
            # Default to last 24 hours if no dates provided
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=1)
        else:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        
        readings = SensorData.get_readings_by_date_range(start_date, end_date)
        
        data = {
            'status': 'success',
            'count': len(readings),
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'data': [reading.to_dict() for reading in readings]
        }
        
        return JsonResponse(data)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_statistics(request):
    """API endpoint to get basic statistics"""
    try:
        # Get readings from last 24 hours
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=1)
        readings = list(SensorData.get_readings_by_date_range(start_date, end_date))
        
        if not readings:
            return JsonResponse({
                'status': 'success',
                'message': 'No data available',
                'data': {}
            })
        
        # Calculate statistics
        temperatures = [r.temperature for r in readings]
        humidity_air = [r.humidity_air for r in readings]
        humidity_soil = [r.humidity_soil for r in readings]
        rain_forecasts = [r.rain_forecast for r in readings]
        
        stats = {
            'total_readings': len(readings),
            'latest_reading': readings[0].to_dict(),
            'temperature': {
                'avg': sum(temperatures) / len(temperatures),
                'min': min(temperatures),
                'max': max(temperatures)
            },
            'humidity_air': {
                'avg': sum(humidity_air) / len(humidity_air),
                'min': min(humidity_air),
                'max': max(humidity_air)
            },
            'humidity_soil': {
                'avg': sum(humidity_soil) / len(humidity_soil),
                'min': min(humidity_soil),
                'max': max(humidity_soil)
            },
            'rain_forecast': {
                'avg': sum(rain_forecasts) / len(rain_forecasts),
                'min': min(rain_forecasts),
                'max': max(rain_forecasts)
            }
        }
        
        data = {
            'status': 'success',
            'period': '24 hours',
            'data': stats
        }
        
        return JsonResponse(data)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)