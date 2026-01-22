"""
Role-based permissions for Fleet Management System

This module defines custom permission classes for role-based access control.
"""

from rest_framework import permissions


class IsSuperUser(permissions.BasePermission):
    """
    Permission class that allows only superusers.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_superuser_role
        )


class IsFleetManager(permissions.BasePermission):
    """
    Permission class that allows fleet managers and superusers.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_fleet_manager_role or request.user.is_superuser_role)
        )


class IsTransportSupervisor(permissions.BasePermission):
    """
    Permission class that allows transport supervisors, fleet managers, and superusers.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (
                request.user.is_transport_supervisor_role or
                request.user.is_fleet_manager_role or
                request.user.is_superuser_role
            )
        )


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Permission class that allows read operations for all authenticated users
    but write operations only for superusers.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for superusers
        return request.user.is_superuser_role


class IsFleetManagerOrReadOnly(permissions.BasePermission):
    """
    Permission class that allows read operations for all authenticated users
    but write operations only for fleet managers and superusers.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions for fleet managers and superusers
        return (
            request.user.is_fleet_manager_role or
            request.user.is_superuser_role
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has a 'user' attribute.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to the owner or superuser
        return (
            obj.user == request.user or
            request.user.is_superuser_role
        )


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to access it.
    Assumes the model instance has a 'user' attribute.
    """
    
    def has_object_permission(self, request, view, obj):
        return (
            obj.user == request.user or
            request.user.is_superuser_role
        )


# Example usage in views:
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from .permissions import IsFleetManager, IsSuperUser

class VehicleListView(APIView):
    permission_classes = [IsFleetManager]
    
    def get(self, request):
        # Only fleet managers and superusers can access
        return Response({...})

class VehicleDetailView(APIView):
    permission_classes = [IsFleetManagerOrReadOnly]
    
    def get(self, request, pk):
        # All authenticated users can read
        return Response({...})
    
    def put(self, request, pk):
        # Only fleet managers and superusers can update
        return Response({...})
"""
