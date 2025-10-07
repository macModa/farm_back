#!/usr/bin/env python3
"""
Export script to extract sensor data from MongoDB and save to CSV format
Suitable for AI/ML model training
"""

import os
import sys
import csv
import argparse
from datetime import datetime, timedelta

# Add Django project to path
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esp32_iot.settings')

import django
django.setup()

from sensor_data.models import SensorData

def export_sensor_data_to_csv(output_file, start_date=None, end_date=None, limit=None):
    """
    Export sensor data to CSV format
    
    Args:
        output_file (str): Path to output CSV file
        start_date (datetime): Start date for filtering data
        end_date (datetime): End date for filtering data
        limit (int): Maximum number of records to export
    """
    try:
        # Build query based on parameters
        if start_date and end_date:
            queryset = SensorData.get_readings_by_date_range(start_date, end_date)
            print(f"Exporting data from {start_date} to {end_date}")
        else:
            queryset = SensorData.objects.order_by('-timestamp')
            print("Exporting all data")
        
        if limit:
            queryset = queryset[:limit]
            print(f"Limited to {limit} records")
        
        # Convert queryset to list for processing
        data_list = list(queryset)
        
        if not data_list:
            print("No data found to export")
            return False
        
        # Define CSV columns
        fieldnames = [
            'timestamp',
            'temperature',
            'humidity_air', 
            'rain_forecast',
            'humidity_soil'
        ]
        
        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write data rows
            for record in data_list:
                row = {
                    'timestamp': record.timestamp.isoformat(),
                    'temperature': float(record.temperature),
                    'humidity_air': float(record.humidity_air),
                    'rain_forecast': float(record.rain_forecast),
                    'humidity_soil': float(record.humidity_soil)
                }
                writer.writerow(row)
        
        print(f"Successfully exported {len(data_list)} records to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error exporting data: {e}")
        return False

def export_training_features(output_file, start_date=None, end_date=None, limit=None):
    """
    Export sensor data with additional calculated features for ML training
    
    Args:
        output_file (str): Path to output CSV file
        start_date (datetime): Start date for filtering data
        end_date (datetime): End date for filtering data 
        limit (int): Maximum number of records to export
    """
    try:
        # Build query
        if start_date and end_date:
            queryset = SensorData.get_readings_by_date_range(start_date, end_date)
        else:
            queryset = SensorData.objects.order_by('-timestamp')
        
        if limit:
            queryset = queryset[:limit]
        
        data_list = list(queryset)
        
        if not data_list:
            print("No data found to export")
            return False
        
        # Define enhanced CSV columns with calculated features
        fieldnames = [
            'timestamp',
            'temperature',
            'humidity_air',
            'rain_forecast',
            'humidity_soil',
            'hour_of_day',
            'day_of_week',
            'month',
            'temperature_humidity_air_ratio',
            'soil_air_humidity_diff',
            'is_rain_predicted',
            'season'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in data_list:
                # Calculate additional features
                timestamp = record.timestamp
                hour_of_day = timestamp.hour
                day_of_week = timestamp.weekday()
                month = timestamp.month
                
                # Determine season (Northern Hemisphere)
                if month in [12, 1, 2]:
                    season = 'winter'
                elif month in [3, 4, 5]:
                    season = 'spring'
                elif month in [6, 7, 8]:
                    season = 'summer'
                else:
                    season = 'autumn'
                
                # Calculate ratios and differences
                temp_humidity_ratio = float(record.temperature) / max(float(record.humidity_air), 1)
                soil_air_diff = float(record.humidity_soil) - float(record.humidity_air)
                is_rain = 1 if float(record.rain_forecast) > 0 else 0
                
                row = {
                    'timestamp': timestamp.isoformat(),
                    'temperature': float(record.temperature),
                    'humidity_air': float(record.humidity_air),
                    'rain_forecast': float(record.rain_forecast),
                    'humidity_soil': float(record.humidity_soil),
                    'hour_of_day': hour_of_day,
                    'day_of_week': day_of_week,
                    'month': month,
                    'temperature_humidity_air_ratio': round(temp_humidity_ratio, 2),
                    'soil_air_humidity_diff': round(soil_air_diff, 2),
                    'is_rain_predicted': is_rain,
                    'season': season
                }
                writer.writerow(row)
        
        print(f"Successfully exported {len(data_list)} records with features to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error exporting training features: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Export ESP32 IoT sensor data to CSV')
    parser.add_argument('--output', '-o', required=True, help='Output CSV file path')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    parser.add_argument('--limit', '-l', type=int, help='Maximum number of records to export')
    parser.add_argument('--features', '-f', action='store_true', 
                        help='Export with additional calculated features for ML training')
    parser.add_argument('--last-days', type=int, help='Export data from last N days')
    
    args = parser.parse_args()
    
    # Handle date parameters
    start_date = None
    end_date = None
    
    if args.last_days:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=args.last_days)
    elif args.start_date or args.end_date:
        if args.start_date:
            start_date = datetime.fromisoformat(args.start_date)
        if args.end_date:
            end_date = datetime.fromisoformat(args.end_date)
    
    # Perform export
    if args.features:
        success = export_training_features(args.output, start_date, end_date, args.limit)
    else:
        success = export_sensor_data_to_csv(args.output, start_date, end_date, args.limit)
    
    if success:
        print(f"Export completed successfully!")
        return 0
    else:
        print(f"Export failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())