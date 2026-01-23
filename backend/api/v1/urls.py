"""
API v1 URL Configuration

This module configures URL routing for API version 1.
All endpoints are prefixed with /api/v1/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from drivers.views import DriverViewSet
from mechanics.views import MechanicViewSet
from vehicles.views import VehicleViewSet
from inspections.views import (
    PreTripInspectionViewSet,
    HealthFitnessCheckViewSet,
    DocumentationComplianceViewSet,
    VehicleExteriorCheckViewSet,
    EngineFluidCheckViewSet,
    InteriorCabinCheckViewSet,
    FunctionalCheckViewSet,
    SafetyEquipmentCheckViewSet,
    TripBehaviorMonitoringViewSet,
    DrivingBehaviorCheckViewSet,
    PostTripReportViewSet,
    RiskScoreSummaryViewSet,
    CorrectiveMeasureViewSet,
    EnforcementActionViewSet,
    SupervisorRemarksViewSet,
    EvaluationSummaryViewSet,
    InspectionSignOffViewSet,
)

app_name = 'api_v1'

# Create a single router for all viewsets
router = DefaultRouter()
router.register(r'drivers', DriverViewSet, basename='driver')
router.register(r'mechanics', MechanicViewSet, basename='mechanic')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'inspections', PreTripInspectionViewSet, basename='inspection')

# Nested router for inspection sub-modules
inspections_router = routers.NestedDefaultRouter(router, r'inspections', lookup='inspection')
inspections_router.register(r'health-fitness', HealthFitnessCheckViewSet, basename='inspection-health-fitness')
inspections_router.register(r'documentation', DocumentationComplianceViewSet, basename='inspection-documentation')
inspections_router.register(r'exterior-checks', VehicleExteriorCheckViewSet, basename='inspection-exterior')
inspections_router.register(r'engine-checks', EngineFluidCheckViewSet, basename='inspection-engine')
inspections_router.register(r'interior-checks', InteriorCabinCheckViewSet, basename='inspection-interior')
inspections_router.register(r'functional-checks', FunctionalCheckViewSet, basename='inspection-functional')
inspections_router.register(r'safety-checks', SafetyEquipmentCheckViewSet, basename='inspection-safety')
inspections_router.register(r'trip-behaviors', TripBehaviorMonitoringViewSet, basename='inspection-trip-behavior')
inspections_router.register(r'driving-behaviors', DrivingBehaviorCheckViewSet, basename='inspection-driving-behavior')
inspections_router.register(r'post-trip', PostTripReportViewSet, basename='inspection-post-trip')
inspections_router.register(r'risk-score', RiskScoreSummaryViewSet, basename='inspection-risk-score')
inspections_router.register(r'corrective-measures', CorrectiveMeasureViewSet, basename='inspection-corrective')
inspections_router.register(r'enforcement-actions', EnforcementActionViewSet, basename='inspection-enforcement')
inspections_router.register(r'supervisor-remarks', SupervisorRemarksViewSet, basename='inspection-remarks')
inspections_router.register(r'evaluation', EvaluationSummaryViewSet, basename='inspection-evaluation')
inspections_router.register(r'sign-offs', InspectionSignOffViewSet, basename='inspection-signoff')

urlpatterns = [
    # Authentication endpoints
    path('auth/', include('authentication.urls', namespace='auth')),
    
    # API viewsets (drivers, mechanics, vehicles, inspections, etc.)
    path('', include(router.urls)),
    
    # Nested routes for inspection sub-modules
    path('', include(inspections_router.urls)),
    
    # Future endpoints can be added here
    # path('trips/', include('trips.urls', namespace='trips')),
]
