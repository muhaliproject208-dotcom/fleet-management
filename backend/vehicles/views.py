from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Vehicle
from .serializers import VehicleListSerializer, VehicleDetailSerializer
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


class VehicleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing vehicles.
    
    Provides CRUD operations for Vehicle model with:
    - List: All authenticated users
    - Retrieve: All authenticated users
    - Create/Update/Delete: Transport Supervisor, Fleet Manager, or Admin
    
    Features:
    - Pagination: 25 items per page
    - Search: by registration_number or vehicle_type
    - Ordering: by created_at (newest first)
    - Filters: is_active, vehicle_type
    - Driver assignment: One-to-one relationship management
    
    Query Parameters:
    - is_active: 'true', 'false', or 'all' (default: 'true')
    - vehicle_type: filter by vehicle type
    - search: search term for registration_number or vehicle_type
    - ordering: field to order by (default: '-created_at')
    """
    
    permission_classes = [IsFleetManagerOrSupervisor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'vehicle_type']
    search_fields = ['registration_number', 'vehicle_type']
    ordering_fields = ['created_at', 'registration_number', 'vehicle_id']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Get queryset with optimizations and filtering.
        
        By default, returns only active vehicles.
        Use ?is_active=all to show all vehicles.
        """
        queryset = Vehicle.objects.select_related('created_by', 'driver')
        
        # Handle is_active filtering
        is_active_param = self.request.query_params.get('is_active', 'true')
        
        if is_active_param.lower() == 'all':
            # Return all vehicles
            pass
        elif is_active_param.lower() == 'false':
            queryset = queryset.filter(is_active=False)
        else:
            # Default: only active vehicles
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def get_serializer_class(self):
        """
        Use different serializers for list and detail views.
        """
        if self.action == 'list':
            return VehicleListSerializer
        return VehicleDetailSerializer
    
    def perform_create(self, serializer):
        """
        Set the created_by field to the current user when creating a vehicle.
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
            {'detail': 'Vehicle deactivated successfully.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsFleetManagerOrSupervisor])
    def activate(self, request, pk=None):
        """
        Custom action to reactivate a deactivated vehicle.
        
        POST /api/v1/vehicles/{id}/activate/
        """
        vehicle = self.get_object()
        
        if vehicle.is_active:
            return Response(
                {'detail': 'Vehicle is already active.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        vehicle.is_active = True
        vehicle.save()
        
        serializer = self.get_serializer(vehicle)
        return Response(
            {
                'detail': 'Vehicle activated successfully.',
                'vehicle': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsFleetManagerOrSupervisor])
    def deactivate(self, request, pk=None):
        """
        Custom action to deactivate a vehicle.
        
        POST /api/v1/vehicles/{id}/deactivate/
        """
        vehicle = self.get_object()
        
        if not vehicle.is_active:
            return Response(
                {'detail': 'Vehicle is already inactive.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if vehicle is referenced in any active inspection
        # This will be implemented when inspection module is added
        
        vehicle.is_active = False
        vehicle.save()
        
        serializer = self.get_serializer(vehicle)
        return Response(
            {
                'detail': 'Vehicle deactivated successfully.',
                'vehicle': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsFleetManagerOrSupervisor])
    def assign_driver(self, request, pk=None):
        """
        Assign a driver to a vehicle.
        
        POST /api/v1/vehicles/{id}/assign_driver/
        Body: {"driver_id": <driver_id>}
        """
        vehicle = self.get_object()
        driver_id = request.data.get('driver_id')
        
        if not driver_id:
            return Response(
                {'detail': 'driver_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from drivers.models import Driver
        
        try:
            driver = Driver.objects.get(id=driver_id, is_active=True)
        except Driver.DoesNotExist:
            return Response(
                {'detail': 'Driver not found or inactive.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if driver is already assigned to another vehicle
        if hasattr(driver, 'assigned_vehicle') and driver.assigned_vehicle and driver.assigned_vehicle != vehicle:
            return Response(
                {'detail': f'Driver is already assigned to vehicle {driver.assigned_vehicle.registration_number}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        vehicle.driver = driver
        vehicle.save()
        
        serializer = self.get_serializer(vehicle)
        return Response(
            {
                'detail': 'Driver assigned successfully.',
                'vehicle': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsFleetManagerOrSupervisor])
    def unassign_driver(self, request, pk=None):
        """
        Unassign driver from a vehicle.
        
        POST /api/v1/vehicles/{id}/unassign_driver/
        """
        vehicle = self.get_object()
        
        if not vehicle.driver:
            return Response(
                {'detail': 'No driver assigned to this vehicle.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        vehicle.driver = None
        vehicle.save()
        
        serializer = self.get_serializer(vehicle)
        return Response(
            {
                'detail': 'Driver unassigned successfully.',
                'vehicle': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def inspection_history(self, request, pk=None):
        """
        Get inspection history for a vehicle.
        
        GET /api/v1/vehicles/{id}/inspection_history/
        
        This will be implemented when inspection module is added.
        """
        vehicle = self.get_object()
        
        return Response(
            {
                'detail': 'Inspection history feature will be available when inspection module is implemented.',
                'vehicle_id': vehicle.vehicle_id,
                'registration_number': vehicle.registration_number,
                'inspections': []
            },
            status=status.HTTP_200_OK
        )
