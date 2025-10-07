from django.urls import path
from . import views
from . import dashboard_views

urlpatterns = [
    # API REST endpoints
    path('readings/latest/', views.get_latest_readings, name='latest_readings'),
    path('readings/by-date/', views.get_readings_by_date, name='readings_by_date'),
    path('statistics/', views.get_statistics, name='statistics'),
    
    # Dashboard web pages
    path('', dashboard_views.dashboard_home, name='dashboard_home'),
    path('charts/', dashboard_views.dashboard_charts, name='dashboard_charts'),
    path('data-table/', dashboard_views.dashboard_data_table, name='dashboard_data_table'),
    path('analytics/', dashboard_views.dashboard_analytics, name='dashboard_analytics'),
    
    # Dashboard API endpoints
    path('api/chart-data/', dashboard_views.api_chart_data, name='api_chart_data'),
    path('api/realtime/', dashboard_views.api_realtime_data, name='api_realtime_data'),
    path('api/statistics/', dashboard_views.api_statistics_summary, name='api_statistics_summary'),
]
