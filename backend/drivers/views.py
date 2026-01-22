from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Driver
from .serializers import DriverListSerializer, DriverDetailSerializer
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


class DriverViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing drivers.
    
    Provides CRUD operations for Driver model with:
    - List: All authenticated users
    - Retrieve: All authenticated users
    - Create/Update/Delete: Transport Supervisor, Fleet Manager, or Admin
    
    Features:
    - Pagination: 25 items per page
    - Search: by full_name or license_number
    - Ordering: by created_at (newest first)
    - Filters: is_active
    
    Query Parameters:
    - is_active: 'true', 'false', or 'all' (default: 'true')
    - search: search term for full_name or license_number
    - ordering: field to order by (default: '-created_at')
    """
    
    permission_classes = [IsFleetManagerOrSupervisor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['full_name', 'license_number']
    ordering_fields = ['created_at', 'full_name', 'driver_id']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Get queryset with optimizations and filtering.
        
        By default, returns only active drivers.
        Use ?is_active=all to show all drivers.
        """
        queryset = Driver.objects.select_related('created_by')
        
        # Handle is_active filtering
        is_active_param = self.request.query_params.get('is_active', 'true')
        
        if is_active_param.lower() == 'all':
            # Return all drivers
            pass
        elif is_active_param.lower() == 'false':
            queryset = queryset.filter(is_active=False)
        else:
            # Default: only active drivers
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def get_serializer_class(self):
        """
        Use different serializers for list and detail views.
        """
        if self.action == 'list':
            return DriverListSerializer
        return DriverDetailSerializer
    
    def perform_create(self, serializer):
        """
        Set the created_by field to the current user when creating a driver.
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
            {'detail': 'Driver deactivated successfully.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsFleetManagerOrSupervisor])
    def activate(self, request, pk=None):
        """
        Custom action to reactivate a deactivated driver.
        
        POST /api/v1/drivers/{id}/activate/
        """
        driver = self.get_object()
        
        if driver.is_active:
            return Response(
                {'detail': 'Driver is already active.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        driver.is_active = True
        driver.save()
        
        serializer = self.get_serializer(driver)
        return Response(
            {
                'detail': 'Driver activated successfully.',
                'driver': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsFleetManagerOrSupervisor])
    def deactivate(self, request, pk=None):
        """
        Custom action to deactivate a driver.
        
        POST /api/v1/drivers/{id}/deactivate/
        """
        driver = self.get_object()
        
        if not driver.is_active:
            return Response(
                {'detail': 'Driver is already inactive.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if driver is referenced in any inspection
        # This will be implemented when inspection module is added
        # For now, we'll allow deactivation
        
        driver.is_active = False
        driver.save()
        
        serializer = self.get_serializer(driver)
        return Response(
            {
                'detail': 'Driver deactivated successfully.',
                'driver': serializer.data
            },
            status=status.HTTP_200_OK
        )
