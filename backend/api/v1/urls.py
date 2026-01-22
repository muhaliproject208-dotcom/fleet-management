"""
API v1 URL Configuration

This module configures URL routing for API version 1.
All endpoints are prefixed with /api/v1/
"""

from django.urls import path, include

app_name = 'api_v1'

urlpatterns = [
    # Authentication endpoints
    path('auth/', include('authentication.urls', namespace='auth')),
    
    # Future endpoints can be added here
    # path('vehicles/', include('vehicles.urls', namespace='vehicles')),
    # path('drivers/', include('drivers.urls', namespace='drivers')),
    # path('trips/', include('trips.urls', namespace='trips')),
]
