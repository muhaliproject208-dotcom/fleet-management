from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Mechanic
from .serializers import MechanicListSerializer, MechanicDetailSerializer
from authentication.permissions import IsTransportSupervisor


class IsFleetManagerOrSupervisor(IsTransportSupervisor):
    """
    Permission class that allows transport supervisors, fleet managers, and admins to create/update/delete.
    All authenticated users can view.
    """
    def has_permission(self, request, view):
        # Allow read-only access to all authenticated users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user and request.user.is_authenticated
        
        # For write operations, require Transport Supervisor, Fleet Manager, or Admin role
        return super().has_permission(request, view)


class MechanicViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing mechanics.
    
    Provides CRUD operations for Mechanic model with:
    - List: All authenticated users
    - Retrieve: All authenticated users
    - Create/Update/Delete: Transport Supervisor, Fleet Manager, or Admin
    
    Features:
    - Pagination: 25 items per page
    - Search: by full_name or specialization
    - Ordering: by created_at (newest first)
    - Filters: is_active, specialization
    
    Query Parameters:
    - is_active: 'true', 'false', or 'all' (default: 'true')
    - specialization: filter by specialization
    - search: search term for full_name or specialization
    - ordering: field to order by (default: '-created_at')
    """
    
    permission_classes = [IsFleetManagerOrSupervisor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'specialization']
    search_fields = ['full_name', 'specialization']
    ordering_fields = ['created_at', 'full_name', 'mechanic_id']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Get queryset with optimizations and filtering.
        
        By default, returns only active mechanics.
        Use ?is_active=all to show all mechanics.
        """
        queryset = Mechanic.objects.select_related('created_by')
        
        # Handle is_active filtering
        is_active_param = self.request.query_params.get('is_active', 'true')
        
        if is_active_param.lower() == 'all':
            # Return all mechanics
            pass
        elif is_active_param.lower() == 'false':
            queryset = queryset.filter(is_active=False)
        else:
            # Default: only active mechanics
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def get_serializer_class(self):
        """
        Use different serializers for list and detail views.
        """
        if self.action == 'list':
            return MechanicListSerializer
        return MechanicDetailSerializer
    
    def perform_create(self, serializer):
        """
        Set the created_by field to the current user when creating a mechanic.
        """
        serializer.save(created_by=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete: Set is_active to False instead of deleting the record.
        """
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        
        return Response(
            {'detail': 'Mechanic deactivated successfully.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsFleetManagerOrSupervisor])
    def activate(self, request, pk=None):
        """
        Custom action to reactivate a deactivated mechanic.
        
        POST /api/v1/mechanics/{id}/activate/
        """
        mechanic = self.get_object()
        
        if mechanic.is_active:
            return Response(
                {'detail': 'Mechanic is already active.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        mechanic.is_active = True
        mechanic.save()
        
        serializer = self.get_serializer(mechanic)
        return Response(
            {
                'detail': 'Mechanic activated successfully.',
                'mechanic': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsFleetManagerOrSupervisor])
    def deactivate(self, request, pk=None):
        """
        Custom action to deactivate a mechanic.
        
        POST /api/v1/mechanics/{id}/deactivate/
        """
        mechanic = self.get_object()
        
        if not mechanic.is_active:
            return Response(
                {'detail': 'Mechanic is already inactive.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        mechanic.is_active = False
        mechanic.save()
        
        serializer = self.get_serializer(mechanic)
        return Response(
            {
                'detail': 'Mechanic deactivated successfully.',
                'mechanic': serializer.data
            },
            status=status.HTTP_200_OK
        )
