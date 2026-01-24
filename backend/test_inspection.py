import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inspections.models import PreTripInspection

try:
    inspection = PreTripInspection.objects.get(id=2)
    print(f"Inspection ID: {inspection.inspection_id}")
    print(f"Status: {inspection.status}")
    print(f"Driver: {inspection.driver}")
    print(f"Vehicle: {inspection.vehicle}")
    
    # Check OneToOne relations
    try:
        health = inspection.health_fitness
        print(f"Has health_fitness: Yes")
    except Exception as e:
        print(f"Has health_fitness: No - {e}")
    
    try:
        doc = inspection.documentation
        print(f"Has documentation: Yes")
    except Exception as e:
        print(f"Has documentation: No - {e}")
    
    try:
        post = inspection.post_trip
        print(f"Has post_trip: Yes")
    except Exception as e:
        print(f"Has post_trip: No - {e}")
    
    try:
        risk = inspection.risk_score
        print(f"Has risk_score: Yes")
    except Exception as e:
        print(f"Has risk_score: No - {e}")
    
    try:
        remarks = inspection.supervisor_remarks
        print(f"Has supervisor_remarks: Yes")
    except Exception as e:
        print(f"Has supervisor_remarks: No - {e}")
    
    try:
        evaluation = inspection.evaluation
        print(f"Has evaluation: Yes")
    except Exception as e:
        print(f"Has evaluation: No - {e}")
    
    # Check ForeignKey relations
    print(f"Exterior checks: {inspection.exterior_checks.count()}")
    print(f"Engine checks: {inspection.engine_fluid_checks.count()}")
    print(f"Interior checks: {inspection.interior_cabin_checks.count()}")
    print(f"Functional checks: {inspection.functional_checks.count()}")
    print(f"Safety checks: {inspection.safety_equipment_checks.count()}")
    print(f"Trip behaviors: {inspection.trip_behaviors.count()}")
    print(f"Driving behaviors: {inspection.driving_behaviors.count()}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
