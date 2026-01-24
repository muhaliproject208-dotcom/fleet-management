from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError as DjangoValidationError

from ..models import SupervisorRemarks, EvaluationSummary, PreTripInspection
from ..serializers import SupervisorRemarksSerializer, EvaluationSummarySerializer


class SupervisorRemarksViewSet(viewsets.ModelViewSet):
    """ViewSet for Supervisor Remarks"""
    
    serializer_class = SupervisorRemarksSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'put', 'head', 'options']  # Disable DELETE
    
    def get_queryset(self):
        """Get supervisor remarks for the current user's accessible inspections"""
        user = self.request.user
        
        # Get the inspection ID from the URL if nested routing is used
        inspection_id = self.kwargs.get('inspection_pk')
        
        if inspection_id:
            queryset = SupervisorRemarks.objects.filter(
                inspection__id=inspection_id
            ).select_related('inspection')
        else:
            queryset = SupervisorRemarks.objects.select_related('inspection')
        
        # Apply role-based filtering
        if user.is_superuser_role or user.is_fleet_manager_role:
            pass
        elif user.is_transport_supervisor_role:
            queryset = queryset.filter(inspection__supervisor=user)
        else:
            queryset = queryset.none()
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create or update supervisor remarks (upsert behavior)"""
        inspection_id = self.kwargs.get('inspection_pk')
        
        if not inspection_id:
            return Response(
                {'error': 'Inspection ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            inspection = PreTripInspection.objects.get(id=inspection_id)
        except PreTripInspection.DoesNotExist:
            return Response(
                {'error': 'Inspection not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate user has permission
        user = request.user
        if not (user.is_superuser_role or user.is_fleet_manager_role):
            if user.is_transport_supervisor_role and inspection.supervisor != user:
                return Response(
                    {'error': 'You can only create remarks for your own inspections'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Auto-populate supervisor_name from logged-in user
        supervisor_name = user.get_full_name() or user.email
        
        # Check if remarks already exist - update instead of create
        try:
            existing_remarks = SupervisorRemarks.objects.get(inspection=inspection)
            serializer = self.get_serializer(existing_remarks, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(supervisor_name=supervisor_name)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SupervisorRemarks.DoesNotExist:
            # Create new remarks
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(inspection=inspection, supervisor_name=supervisor_name)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_update(self, serializer):
        """Update supervisor remarks"""
        serializer.save()


class EvaluationSummaryViewSet(viewsets.ModelViewSet):
    """ViewSet for Evaluation Summaries"""
    
    serializer_class = EvaluationSummarySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'put', 'head', 'options']  # Disable DELETE
    
    def get_queryset(self):
        """Get evaluation summaries for the current user's accessible inspections"""
        user = self.request.user
        
        # Get the inspection ID from the URL if nested routing is used
        inspection_id = self.kwargs.get('inspection_pk')
        
        if inspection_id:
            queryset = EvaluationSummary.objects.filter(
                inspection__id=inspection_id
            ).select_related('inspection')
        else:
            queryset = EvaluationSummary.objects.select_related('inspection')
        
        # Apply role-based filtering
        if user.is_superuser_role or user.is_fleet_manager_role:
            pass
        elif user.is_transport_supervisor_role:
            queryset = queryset.filter(inspection__supervisor=user)
        else:
            queryset = queryset.none()
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create or update evaluation summary (upsert behavior)"""
        inspection_id = self.kwargs.get('inspection_pk')
        
        if not inspection_id:
            return Response(
                {'error': 'Inspection ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            inspection = PreTripInspection.objects.get(id=inspection_id)
        except PreTripInspection.DoesNotExist:
            return Response(
                {'error': 'Inspection not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate user has permission (typically supervisor or fleet manager)
        user = request.user
        if not (user.is_superuser_role or user.is_fleet_manager_role):
            if user.is_transport_supervisor_role and inspection.supervisor != user:
                return Response(
                    {'error': 'You can only create evaluations for your own inspections'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Check if evaluation already exists - update instead of create
        try:
            existing_evaluation = EvaluationSummary.objects.get(inspection=inspection)
            serializer = self.get_serializer(existing_evaluation, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            # Check and update post-trip completion status
            inspection.check_and_update_post_trip_status()
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except EvaluationSummary.DoesNotExist:
            # Create new evaluation
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(inspection=inspection)
            
            # Check and update post-trip completion status
            inspection.check_and_update_post_trip_status()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_update(self, serializer):
        """Update evaluation summary (will auto-recalculate overall performance)"""
        serializer.save()
