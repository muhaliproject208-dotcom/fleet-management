"""
Filterset classes for advanced filtering of models.
"""

import django_filters
from django.db.models import Q
from .models import PreTripInspection, RiskScoreSummary, InspectionStatus


class PreTripInspectionFilter(django_filters.FilterSet):
    """Advanced filtering for pre-trip inspections"""
    
    # Status filter
    status = django_filters.ChoiceFilter(
        choices=InspectionStatus.choices
    )
    
    # Date range filters
    inspection_date_from = django_filters.DateFilter(
        field_name='inspection_date',
        lookup_expr='gte',
        label='Inspection date from'
    )
    inspection_date_to = django_filters.DateFilter(
        field_name='inspection_date',
        lookup_expr='lte',
        label='Inspection date to'
    )
    
    # Search filter (inspection_id, driver name, vehicle registration)
    search = django_filters.CharFilter(
        method='filter_search',
        label='Search'
    )
    
    # Foreign key filters
    driver = django_filters.NumberFilter(
        field_name='driver__id',
        label='Driver ID'
    )
    vehicle = django_filters.NumberFilter(
        field_name='vehicle__id',
        label='Vehicle ID'
    )
    supervisor = django_filters.NumberFilter(
        field_name='supervisor__id',
        label='Supervisor ID'
    )
    
    # Boolean filters
    has_critical_failures = django_filters.BooleanFilter(
        method='filter_critical_failures',
        label='Has critical failures'
    )
    
    class Meta:
        model = PreTripInspection
        fields = [
            'status',
            'driver',
            'vehicle',
            'supervisor',
            'inspection_date_from',
            'inspection_date_to',
            'search',
            'has_critical_failures',
        ]
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields"""
        return queryset.filter(
            Q(inspection_id__icontains=value) |
            Q(driver__full_name__icontains=value) |
            Q(driver__license_number__icontains=value) |
            Q(vehicle__registration_number__icontains=value) |
            Q(route__icontains=value)
        )
    
    def filter_critical_failures(self, queryset, name, value):
        """Filter inspections with critical failures"""
        if value:
            from .models import (
                VehicleExteriorCheck,
                EngineFluidCheck,
                InteriorCabinCheck,
                FunctionalCheck,
                SafetyEquipmentCheck
            )
            
            # Get inspections with critical failures
            inspection_ids = set()
            
            for model in [VehicleExteriorCheck, EngineFluidCheck, InteriorCabinCheck,
                          FunctionalCheck, SafetyEquipmentCheck]:
                ids = model.objects.filter(
                    status='fail',
                    is_critical_failure=True
                ).values_list('inspection_id', flat=True)
                inspection_ids.update(ids)
            
            return queryset.filter(id__in=inspection_ids)
        
        return queryset


class RiskScoreSummaryFilter(django_filters.FilterSet):
    """Advanced filtering for risk scores"""
    
    risk_level = django_filters.ChoiceFilter(
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
        ]
    )
    
    requires_review = django_filters.BooleanFilter(
        field_name='requires_supervisor_review'
    )
    
    # Points range filters
    current_points_min = django_filters.NumberFilter(
        field_name='current_trip_points',
        lookup_expr='gte'
    )
    current_points_max = django_filters.NumberFilter(
        field_name='current_trip_points',
        lookup_expr='lte'
    )
    
    total_points_min = django_filters.NumberFilter(
        field_name='total_30_day_points',
        lookup_expr='gte'
    )
    total_points_max = django_filters.NumberFilter(
        field_name='total_30_day_points',
        lookup_expr='lte'
    )
    
    class Meta:
        model = RiskScoreSummary
        fields = [
            'risk_level',
            'requires_review',
            'current_points_min',
            'current_points_max',
            'total_points_min',
            'total_points_max',
        ]
