"""
Main API URL Configuration

This module routes requests to the appropriate API version.
"""

from django.urls import path, include

urlpatterns = [
    # API v1 endpoints
    path('v1/', include('api.v1.urls', namespace='v1')),
    
    # Future API versions can be added here
    # path('v2/', include('api.v2.urls', namespace='v2')),
]
