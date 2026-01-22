"""
API v1 URL Configuration

This module configures URL routing for API version 1.
All endpoints are prefixed with /api/v1/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from drivers.views import DriverViewSet
from mechanics.views import MechanicViewSet

app_name = 'api_v1'

# Create a single router for all viewsets
router = DefaultRouter()
router.register(r'drivers', DriverViewSet, basename='driver')
router.register(r'mechanics', MechanicViewSet, basename='mechanic')

urlpatterns = [
    # Authentication endpoints
    path('auth/', include('authentication.urls', namespace='auth')),
    
    # API viewsets (drivers, mechanics, etc.)
    path('', include(router.urls)),
    
    # Future endpoints can be added here
    # path('vehicles/', include('vehicles.urls', namespace='vehicles')),
    # path('trips/', include('trips.urls', namespace='trips')),
]
