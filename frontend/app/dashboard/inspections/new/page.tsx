'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { isAuthenticated } from '@/lib/api/auth';
import { getDrivers, Driver } from '@/lib/api/drivers';
import { getVehicles, Vehicle } from '@/lib/api/vehicles';
import { getMechanics, Mechanic } from '@/lib/api/mechanics';
import { createInspection, getInspection } from '@/lib/api/inspections';
import { API_URL } from '@/lib/api';
import type { VehicleCheck } from '@/lib/api/inspections/types';
import ProgressTracker from '../components/ProgressTracker';
import { RadioOption, CheckItem } from '../components/FormComponents';

// Mapping from display labels to backend-valid enum keys
const EXTERIOR_CHECK_MAP: Record<string, string> = {
  'Tires (inflation, tread depth, damage)': 'tires',
  'Lights (headlights, taillights, brake lights, signals, hazard)': 'lights',
  'Mirrors (clean, adjusted, damage-free)': 'mirrors',
  'Windshield (cracks, chips, wipers, washer fluid)': 'windshield',
  'Body Condition (visible damage)': 'body_condition',
  'Loose Parts': 'loose_parts',
  'Leaks': 'leaks',
};

const ENGINE_CHECK_MAP: Record<string, string> = {
  'Engine Oil (level, quality)': 'engine_oil',
  'Coolant (level, leaks)': 'coolant',
  'Brake Fluid (level)': 'brake_fluid',
  'Transmission Fluid (level, condition)': 'transmission_fluid',
  'Power Steering Fluid (level)': 'power_steering_fluid',
  'Battery (terminals, secure)': 'battery',
};

const INTERIOR_CHECK_MAP: Record<string, string> = {
  'Dashboard Indicators (warning lights functioning)': 'dashboard_indicators',
  'Seatbelts (operational, no wear/damage)': 'seatbelts',
  'Horn (working)': 'horn',
  'Fire Extinguisher (present, condition)': 'fire_extinguisher',
  'First Aid Kit (present, condition)': 'first_aid_kit',
  'Safety Triangles (present, condition)': 'safety_triangles',
};

const FUNCTIONAL_CHECK_MAP: Record<string, string> = {
  'Brakes (responsiveness, effectiveness)': 'brakes',
  'Steering (smooth operation)': 'steering',
  'Suspension (unusual noises, handling)': 'suspension',
  'Heating & Air Conditioning (both systems operational)': 'hvac',
};

const SAFETY_CHECK_MAP: Record<string, string> = {
  'Fire Extinguisher (charged, tagged)': 'fire_extinguisher',
  'First Aid Kit (stock verified)': 'first_aid_kit',
  'Reflective Triangles (2 present)': 'reflective_triangles',
  'Wheel Chocks': 'wheel_chocks',
  'Spare Tyre and Jack': 'spare_tyre',
  'Torch/Flashlight': 'torch',
  'Emergency Contact List': 'emergency_contacts',
  'GPS Tracker Operational': 'gps_tracker',
};

interface InspectionFormData {
  driver: string;
  vehicle: string;
  mechanic: string;
  inspection_date: string;
  route: string;
  approved_driving_hours: string;
  approved_rest_stops: number;
  
  adequate_rest: boolean | null;
  alcohol_test_status: 'pass' | 'fail' | '';
  alcohol_test_remarks: string;
  temperature_check_status: 'pass' | 'fail' | '';
  temperature_value: string;
  fit_for_duty: boolean | null;
  medication_status: boolean | null;
  medication_remarks: string;
  no_health_impairment: boolean | null;
  fatigue_checklist_completed: boolean | null;
  fatigue_remarks: string;
  
  certificate_of_fitness: 'valid' | 'invalid' | '';
  road_tax_valid: boolean | null;
  insurance_valid: boolean | null;
  trip_authorization_signed: boolean | null;
  logbook_present: boolean | null;
  driver_handbook_present: boolean | null;
  permits_valid: boolean | null;
  ppe_available: boolean | null;
  route_familiarity: boolean | null;
  emergency_procedures_known: boolean | null;
  gps_activated: boolean | null;
  safety_briefing_provided: boolean | null;
  rtsa_clearance: boolean | null;
  emergency_contact: string;
  
  exterior_checks: Array<{ item: string; status: 'pass' | 'fail' | null; remarks: string }>;
  engine_checks: Array<{ item: string; status: 'pass' | 'fail' | null; remarks: string }>;
  interior_checks: Array<{ item: string; status: 'pass' | 'fail' | null; remarks: string }>;
  functional_checks: Array<{ item: string; status: 'pass' | 'fail' | null; remarks: string }>;
  safety_checks: Array<{ item: string; status: 'pass' | 'fail' | null; remarks: string }>;
  
  all_defects_rectified: boolean | null;
  defects_remarks: string;
  driver_briefed: boolean | null;
  briefing_remarks: string;
  vehicle_ready: boolean | null;
  ready_remarks: string;
}

const TOTAL_STEPS = 9;

export default function NewInspectionWizard() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [inspectionId, setInspectionId] = useState<string | null>(null);
  
  // Track which sections have been saved and their IDs (for OneToOne relationships)
  const [savedSections, setSavedSections] = useState({
    health: false,
    documentation: false,
    exterior: false,
    engine: false,
    interior: false,
    functional: false,
    safety: false,
  });
  
  // Track IDs for OneToOne relationships (needed for updates)
  const [sectionIds, setSectionIds] = useState<{
    healthId: string | null;
    documentationId: string | null;
    supervisorRemarksId: string | null;
  }>({
    healthId: null,
    documentationId: null,
    supervisorRemarksId: null,
  });
  
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [mechanics, setMechanics] = useState<Mechanic[]>([]);
  
  const [formData, setFormData] = useState<InspectionFormData>({
    driver: '',
    vehicle: '',
    mechanic: '',
    inspection_date: new Date().toISOString().split('T')[0],
    route: '',
    approved_driving_hours: '',
    approved_rest_stops: 0,
    
    adequate_rest: null,
    alcohol_test_status: '',
    alcohol_test_remarks: '',
    temperature_check_status: '',
    temperature_value: '',
    fit_for_duty: null,
    medication_status: null,
    medication_remarks: '',
    no_health_impairment: null,
    fatigue_checklist_completed: null,
    fatigue_remarks: '',
    
    certificate_of_fitness: '',
    road_tax_valid: null,
    insurance_valid: null,
    trip_authorization_signed: null,
    logbook_present: null,
    driver_handbook_present: null,
    permits_valid: null,
    ppe_available: null,
    route_familiarity: null,
    emergency_procedures_known: null,
    gps_activated: null,
    safety_briefing_provided: null,
    rtsa_clearance: null,
    emergency_contact: '',
    
    exterior_checks: [
      { item: 'Tires (inflation, tread depth, damage)', status: null, remarks: '' },
      { item: 'Lights (headlights, taillights, brake lights, signals, hazard)', status: null, remarks: '' },
      { item: 'Mirrors (clean, adjusted, damage-free)', status: null, remarks: '' },
      { item: 'Windshield (cracks, chips, wipers, washer fluid)', status: null, remarks: '' },
      { item: 'Body Condition (visible damage)', status: null, remarks: '' },
      { item: 'Loose Parts', status: null, remarks: '' },
      { item: 'Leaks', status: null, remarks: '' },
    ],
    
    engine_checks: [
      { item: 'Engine Oil (level, quality)', status: null, remarks: '' },
      { item: 'Coolant (level, leaks)', status: null, remarks: '' },
      { item: 'Brake Fluid (level)', status: null, remarks: '' },
      { item: 'Transmission Fluid (level, condition)', status: null, remarks: '' },
      { item: 'Power Steering Fluid (level)', status: null, remarks: '' },
      { item: 'Battery (terminals, secure)', status: null, remarks: '' },
    ],
    
    interior_checks: [
      { item: 'Dashboard Indicators (warning lights functioning)', status: null, remarks: '' },
      { item: 'Seatbelts (operational, no wear/damage)', status: null, remarks: '' },
      { item: 'Horn (working)', status: null, remarks: '' },
      { item: 'Fire Extinguisher (present, condition)', status: null, remarks: '' },
      { item: 'First Aid Kit (present, condition)', status: null, remarks: '' },
      { item: 'Safety Triangles (present, condition)', status: null, remarks: '' },
    ],
    
    functional_checks: [
      { item: 'Brakes (responsiveness, effectiveness)', status: null, remarks: '' },
      { item: 'Steering (smooth operation)', status: null, remarks: '' },
      { item: 'Suspension (unusual noises, handling)', status: null, remarks: '' },
      { item: 'Heating & Air Conditioning (both systems operational)', status: null, remarks: '' },
    ],
    
    safety_checks: [
      { item: 'Fire Extinguisher (charged, tagged)', status: null, remarks: '' },
      { item: 'First Aid Kit (stock verified)', status: null, remarks: '' },
      { item: 'Reflective Triangles (2 present)', status: null, remarks: '' },
      { item: 'Wheel Chocks', status: null, remarks: '' },
      { item: 'Spare Tyre and Jack', status: null, remarks: '' },
      { item: 'Torch/Flashlight', status: null, remarks: '' },
      { item: 'Emergency Contact List', status: null, remarks: '' },
      { item: 'GPS Tracker Operational', status: null, remarks: '' },
    ],
    
    all_defects_rectified: null,
    defects_remarks: '',
    driver_briefed: null,
    briefing_remarks: '',
    vehicle_ready: null,
    ready_remarks: '',
  });

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    const fetchData = async () => {
      setInitialLoading(true);
      
      const [driversRes, vehiclesRes, mechanicsRes] = await Promise.all([
        getDrivers({ is_active: true }),
        getVehicles({ is_active: true }),
        getMechanics({ is_active: true }),
      ]);

      if (driversRes.data) setDrivers(driversRes.data.results || []);
      if (vehiclesRes.data) setVehicles(vehiclesRes.data.results || []);
      if (mechanicsRes.data) setMechanics(mechanicsRes.data.results || []);
      
      // Check if we're editing an existing inspection (from URL params)
      const editId = searchParams.get('id');
      const stepParam = searchParams.get('step');
      
      if (editId) {
        setInspectionId(editId);
        const response = await getInspection(editId);
        
        if (response.error) {
          console.error('Failed to load inspection:', response.error);
          setError(`Failed to load inspection: ${response.error}`);
          setInitialLoading(false);
          return;
        }
        
        if (response.data) {
          const inspection = response.data;
          
          // Load basic inspection data
          setFormData(prev => ({
            ...prev,
            driver: inspection.driver.id.toString(),
            vehicle: inspection.vehicle.id.toString(),
            mechanic: inspection.mechanic?.id.toString() || '',
            inspection_date: inspection.inspection_date,
            route: inspection.route,
            approved_driving_hours: inspection.approved_driving_hours,
            approved_rest_stops: inspection.approved_rest_stops,
            
            // Load health check data if it exists
            ...(inspection.health_fitness ? {
              adequate_rest: inspection.health_fitness.adequate_rest,
              alcohol_test_status: inspection.health_fitness.alcohol_test_status,
              alcohol_test_remarks: inspection.health_fitness.alcohol_test_remarks || '',
              temperature_check_status: inspection.health_fitness.temperature_check_status,
              temperature_value: inspection.health_fitness.temperature_value?.toString() || '',
              fit_for_duty: inspection.health_fitness.fit_for_duty,
              medication_status: inspection.health_fitness.medication_status,
              medication_remarks: inspection.health_fitness.medication_remarks || '',
              no_health_impairment: inspection.health_fitness.no_health_impairment,
              fatigue_checklist_completed: inspection.health_fitness.fatigue_checklist_completed,
              fatigue_remarks: inspection.health_fitness.fatigue_remarks || '',
            } : {}),
            
            // Load documentation data if it exists
            ...(inspection.documentation ? {
              certificate_of_fitness: inspection.documentation.certificate_of_fitness,
              road_tax_valid: inspection.documentation.road_tax_valid,
              insurance_valid: inspection.documentation.insurance_valid,
              trip_authorization_signed: inspection.documentation.trip_authorization_signed,
              logbook_present: inspection.documentation.logbook_present,
              driver_handbook_present: inspection.documentation.driver_handbook_present,
              permits_valid: inspection.documentation.permits_valid,
              ppe_available: inspection.documentation.ppe_available,
              route_familiarity: inspection.documentation.route_familiarity,
              emergency_procedures_known: inspection.documentation.emergency_procedures_known,
              gps_activated: inspection.documentation.gps_activated,
              safety_briefing_provided: inspection.documentation.safety_briefing_provided,
              rtsa_clearance: inspection.documentation.rtsa_clearance,
              emergency_contact: inspection.documentation.emergency_contact || '',
            } : {}),
            
            // Load vehicle check data if it exists
            ...(inspection.exterior_checks && inspection.exterior_checks.length > 0 ? {
              exterior_checks: inspection.exterior_checks.map(check => ({
                item: check.check_item,
                status: check.status,
                remarks: check.remarks || ''
              }))
            } : {}),
            ...(inspection.engine_fluid_checks && inspection.engine_fluid_checks.length > 0 ? {
              engine_checks: inspection.engine_fluid_checks.map(check => ({
                item: check.check_item,
                status: check.status,
                remarks: check.remarks || ''
              }))
            } : {}),
            ...(inspection.interior_cabin_checks && inspection.interior_cabin_checks.length > 0 ? {
              interior_checks: inspection.interior_cabin_checks.map(check => ({
                item: check.check_item,
                status: check.status,
                remarks: check.remarks || ''
              }))
            } : {}),
            ...(inspection.functional_checks && inspection.functional_checks.length > 0 ? {
              functional_checks: inspection.functional_checks.map(check => ({
                item: check.check_item,
                status: check.status,
                remarks: check.remarks || ''
              }))
            } : {}),
            ...(inspection.safety_equipment_checks && inspection.safety_equipment_checks.length > 0 ? {
              safety_checks: inspection.safety_equipment_checks.map(check => ({
                item: check.check_item,
                status: check.status,
                remarks: check.remarks || ''
              }))
            } : {})
          }));
          
          // Mark sections as saved if they exist
          setSavedSections({
            health: !!inspection.health_fitness,
            documentation: !!inspection.documentation,
            exterior: !!(inspection.exterior_checks && inspection.exterior_checks.length > 0),
            engine: !!(inspection.engine_fluid_checks && inspection.engine_fluid_checks.length > 0),
            interior: !!(inspection.interior_cabin_checks && inspection.interior_cabin_checks.length > 0),
            functional: !!(inspection.functional_checks && inspection.functional_checks.length > 0),
            safety: !!(inspection.safety_equipment_checks && inspection.safety_equipment_checks.length > 0),
          });
          
          // Store IDs for OneToOne relationships (needed for updates)
          setSectionIds({
            healthId: inspection.health_fitness?.id?.toString() || null,
            documentationId: inspection.documentation?.id?.toString() || null,
            supervisorRemarksId: inspection.supervisor_remarks?.id?.toString() || null,
          });
          
          // Set the step from URL param if provided (after data is loaded)
          if (stepParam) {
            const step = parseInt(stepParam, 10);
            if (step >= 1 && step <= TOTAL_STEPS) {
              setCurrentStep(step);
            }
          }
        }
      } else {
        // If not editing, just set the step if provided
        if (stepParam) {
          const step = parseInt(stepParam, 10);
          if (step >= 1 && step <= TOTAL_STEPS) {
            setCurrentStep(step);
          }
        }
      }
      
      setInitialLoading(false);
    };

    void fetchData();
  }, [router, searchParams]);

  const validateStep = (step: number): boolean => {
    setError('');
    
    switch (step) {
      case 1:
        if (!formData.driver || !formData.vehicle || !formData.inspection_date || 
            !formData.route || !formData.approved_driving_hours) {
          setError('Please fill in all required fields');
          return false;
        }
        break;
      case 2:
        // First check the critical rest question
        if (formData.adequate_rest === null) {
          setError('Please answer the rest/fatigue clearance question');
          return false;
        }
        if (formData.adequate_rest === false) {
          setError('⚠️ TRAVEL NOT PERMITTED: Driver has not rested for 8 hours or more. The driver should not travel.');
          return false;
        }
        if (!formData.alcohol_test_status || !formData.temperature_check_status || 
            formData.fit_for_duty === null || formData.medication_status === null || 
            formData.no_health_impairment === null || formData.fatigue_checklist_completed === null) {
          setError('Please complete all health checks');
          return false;
        }
        if (formData.alcohol_test_status === 'fail' && !formData.alcohol_test_remarks.trim()) {
          setError('Remarks required when alcohol test fails');
          return false;
        }
        if (formData.medication_status && !formData.medication_remarks.trim()) {
          setError('Medication remarks required');
          return false;
        }
        break;
      case 3:
        if (!formData.certificate_of_fitness || formData.road_tax_valid === null || 
            formData.insurance_valid === null || formData.trip_authorization_signed === null ||
            formData.logbook_present === null || formData.driver_handbook_present === null ||
            formData.permits_valid === null || formData.ppe_available === null ||
            formData.route_familiarity === null || formData.emergency_procedures_known === null ||
            formData.gps_activated === null || formData.safety_briefing_provided === null ||
            formData.rtsa_clearance === null || !formData.emergency_contact.trim()) {
          setError('Please complete all documentation checks');
          return false;
        }
        break;
      case 4:
        if (!formData.exterior_checks.every(c => c.status !== null)) {
          setError('Please complete all exterior checks');
          return false;
        }
        break;
      case 5:
        if (!formData.engine_checks.every(c => c.status !== null)) {
          setError('Please complete all engine checks');
          return false;
        }
        break;
      case 6:
        if (!formData.interior_checks.every(c => c.status !== null)) {
          setError('Please complete all interior checks');
          return false;
        }
        break;
      case 7:
        if (!formData.functional_checks.every(c => c.status !== null)) {
          setError('Please complete all functional checks');
          return false;
        }
        break;
      case 8:
        if (!formData.safety_checks.every(c => c.status !== null)) {
          setError('Please complete all safety equipment checks');
          return false;
        }
        break;
      case 9:
        if (formData.all_defects_rectified === null || formData.driver_briefed === null || 
            formData.vehicle_ready === null) {
          setError('Please complete all final verification questions');
          return false;
        }
        break;
    }
    
    return true;
  };

  const handleNext = async () => {
    if (!validateStep(currentStep)) return;
    
    setLoading(true);
    setError('');
    
    try {
      // Save current step data before proceeding
      await saveCurrentStepData();
      
      setCurrentStep(prev => Math.min(prev + 1, TOTAL_STEPS));
      window.scrollTo(0, 0);
    } catch (err) {
      setError(`Failed to save data: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const handlePrevious = async () => {
    setError('');
    
    // If we have an inspection ID, refetch the data to ensure we have the latest
    if (inspectionId) {
      setLoading(true);
      const response = await getInspection(inspectionId);
      
      if (response.data) {
        const inspection = response.data;
        
        // Reload all form data
        setFormData(prev => ({
          ...prev,
          driver: inspection.driver.id.toString(),
          vehicle: inspection.vehicle.id.toString(),
          mechanic: inspection.mechanic?.id.toString() || '',
          inspection_date: inspection.inspection_date,
          route: inspection.route,
          approved_driving_hours: inspection.approved_driving_hours,
          approved_rest_stops: inspection.approved_rest_stops,
          
          // Load health check data if it exists
          ...(inspection.health_fitness ? {
            adequate_rest: inspection.health_fitness.adequate_rest,
            alcohol_test_status: inspection.health_fitness.alcohol_test_status,
            alcohol_test_remarks: inspection.health_fitness.alcohol_test_remarks || '',
            temperature_check_status: inspection.health_fitness.temperature_check_status,
            temperature_value: inspection.health_fitness.temperature_value?.toString() || '',
            fit_for_duty: inspection.health_fitness.fit_for_duty,
            medication_status: inspection.health_fitness.medication_status,
            medication_remarks: inspection.health_fitness.medication_remarks || '',
            no_health_impairment: inspection.health_fitness.no_health_impairment,
            fatigue_checklist_completed: inspection.health_fitness.fatigue_checklist_completed,
            fatigue_remarks: inspection.health_fitness.fatigue_remarks || '',
          } : {}),
          
          // Load documentation data if it exists
          ...(inspection.documentation ? {
            certificate_of_fitness: inspection.documentation.certificate_of_fitness,
            road_tax_valid: inspection.documentation.road_tax_valid,
            insurance_valid: inspection.documentation.insurance_valid,
            trip_authorization_signed: inspection.documentation.trip_authorization_signed,
            logbook_present: inspection.documentation.logbook_present,
            driver_handbook_present: inspection.documentation.driver_handbook_present,
            permits_valid: inspection.documentation.permits_valid,
            ppe_available: inspection.documentation.ppe_available,
            route_familiarity: inspection.documentation.route_familiarity,
            emergency_procedures_known: inspection.documentation.emergency_procedures_known,
            gps_activated: inspection.documentation.gps_activated,
            safety_briefing_provided: inspection.documentation.safety_briefing_provided,
            rtsa_clearance: inspection.documentation.rtsa_clearance,
            emergency_contact: inspection.documentation.emergency_contact || '',
          } : {}),
          
          // Load vehicle check data if it exists
          ...(inspection.exterior_checks && inspection.exterior_checks.length > 0 ? {
            exterior_checks: inspection.exterior_checks.map((check: VehicleCheck) => ({
              item: check.check_item,
              status: check.status,
              remarks: check.remarks || ''
            }))
          } : {}),
          ...(inspection.engine_fluid_checks && inspection.engine_fluid_checks.length > 0 ? {
            engine_checks: inspection.engine_fluid_checks.map((check: VehicleCheck) => ({
              item: check.check_item,
              status: check.status,
              remarks: check.remarks || ''
            }))
          } : {}),
          ...(inspection.interior_cabin_checks && inspection.interior_cabin_checks.length > 0 ? {
            interior_checks: inspection.interior_cabin_checks.map((check: VehicleCheck) => ({
              item: check.check_item,
              status: check.status,
              remarks: check.remarks || ''
            }))
          } : {}),
          ...(inspection.functional_checks && inspection.functional_checks.length > 0 ? {
            functional_checks: inspection.functional_checks.map((check: VehicleCheck) => ({
              item: check.check_item,
              status: check.status,
              remarks: check.remarks || ''
            }))
          } : {}),
          ...(inspection.safety_equipment_checks && inspection.safety_equipment_checks.length > 0 ? {
            safety_checks: inspection.safety_equipment_checks.map((check: VehicleCheck) => ({
              item: check.check_item,
              status: check.status,
              remarks: check.remarks || ''
            }))
          } : {}),
        }));
        
        // Also update section IDs for OneToOne relationships
        setSectionIds({
          healthId: inspection.health_fitness?.id?.toString() || null,
          documentationId: inspection.documentation?.id?.toString() || null,
          supervisorRemarksId: inspection.supervisor_remarks?.id?.toString() || null,
        });
      }
      setLoading(false);
    }
    
    setCurrentStep(prev => Math.max(prev - 1, 1));
    window.scrollTo(0, 0);
  };

  const saveCurrentStepData = async () => {
    const token = localStorage.getItem('access_token');
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };

    switch (currentStep) {
      case 1: {
        // Create the inspection with basic info
        const inspectionData = {
          driver: formData.driver,
          vehicle: formData.vehicle,
          mechanic: formData.mechanic || undefined,
          inspection_date: formData.inspection_date,
          route: formData.route,
          approved_driving_hours: formData.approved_driving_hours,
          approved_rest_stops: formData.approved_rest_stops,
        };

        const inspectionResponse = await createInspection(inspectionData);
        if (inspectionResponse.error) {
          throw new Error(inspectionResponse.error);
        }
        
        setInspectionId(inspectionResponse.data!.id.toString());
        setSuccess('Basic information saved!');
        break;
      }

      case 2: {
        // Save or update health & fitness check
        if (!inspectionId) throw new Error('Inspection not created yet');
        
        const healthData = {
          inspection: inspectionId,
          adequate_rest: formData.adequate_rest,
          alcohol_test_status: formData.alcohol_test_status,
          alcohol_test_remarks: formData.alcohol_test_remarks,
          temperature_check_status: formData.temperature_check_status,
          temperature_value: parseFloat(formData.temperature_value) || null,
          fit_for_duty: formData.fit_for_duty,
          medication_status: formData.medication_status,
          medication_remarks: formData.medication_remarks,
          no_health_impairment: formData.no_health_impairment,
          fatigue_checklist_completed: formData.fatigue_checklist_completed,
          fatigue_remarks: formData.fatigue_remarks,
        };

        // Use PATCH with ID for updates, POST for create
        const isUpdate = savedSections.health && sectionIds.healthId;
        const healthMethod = isUpdate ? 'PATCH' : 'POST';
        const healthUrl = isUpdate 
          ? `${API_URL}/inspections/${inspectionId}/health-fitness/${sectionIds.healthId}/`
          : `${API_URL}/inspections/${inspectionId}/health-fitness/`;
        
        const healthResponse = await fetch(healthUrl, { 
          method: healthMethod, 
          headers, 
          body: JSON.stringify(healthData) 
        });

        if (!healthResponse.ok) {
          const errorData = await healthResponse.json();
          throw new Error(`Failed to save health check: ${JSON.stringify(errorData)}`);
        }
        
        // Store the ID from response if it was a create
        if (!isUpdate) {
          const healthResult = await healthResponse.json();
          setSectionIds(prev => ({ ...prev, healthId: healthResult.id?.toString() || null }));
        }
        
        setSavedSections(prev => ({ ...prev, health: true }));
        setSuccess('Health & fitness check saved!');
        break;
      }

      case 3: {
        // Save or update documentation compliance
        if (!inspectionId) throw new Error('Inspection not created yet');
        
        const docData = {
          inspection: inspectionId,
          certificate_of_fitness: formData.certificate_of_fitness,
          road_tax_valid: formData.road_tax_valid,
          insurance_valid: formData.insurance_valid,
          trip_authorization_signed: formData.trip_authorization_signed,
          logbook_present: formData.logbook_present,
          driver_handbook_present: formData.driver_handbook_present,
          permits_valid: formData.permits_valid,
          ppe_available: formData.ppe_available,
          route_familiarity: formData.route_familiarity,
          emergency_procedures_known: formData.emergency_procedures_known,
          gps_activated: formData.gps_activated,
          safety_briefing_provided: formData.safety_briefing_provided,
          rtsa_clearance: formData.rtsa_clearance,
          emergency_contact: formData.emergency_contact,
        };

        // Use PATCH with ID for updates, POST for create
        const isDocUpdate = savedSections.documentation && sectionIds.documentationId;
        const docMethod = isDocUpdate ? 'PATCH' : 'POST';
        const docUrl = isDocUpdate
          ? `${API_URL}/inspections/${inspectionId}/documentation/${sectionIds.documentationId}/`
          : `${API_URL}/inspections/${inspectionId}/documentation/`;
        
        const docResponse = await fetch(docUrl, { 
          method: docMethod, 
          headers, 
          body: JSON.stringify(docData) 
        });

        if (!docResponse.ok) {
          const errorData = await docResponse.json();
          throw new Error(`Failed to save documentation: ${JSON.stringify(errorData)}`);
        }
        
        // Store the ID from response if it was a create
        if (!isDocUpdate) {
          const docResult = await docResponse.json();
          setSectionIds(prev => ({ ...prev, documentationId: docResult.id?.toString() || null }));
        }
        
        setSavedSections(prev => ({ ...prev, documentation: true }));
        setSuccess('Documentation saved!');
        break;
      }

      case 4: {
        // Save or delete/recreate exterior checks
        if (!inspectionId) throw new Error('Inspection not created yet');
        
        // If already saved, delete all existing checks first
        if (savedSections.exterior) {
          const existingChecks = await fetch(
            `${API_URL}/inspections/${inspectionId}/exterior-checks/`,
            { headers }
          );
          if (existingChecks.ok) {
            const checks = await existingChecks.json();
            for (const check of checks) {
              await fetch(
                `${API_URL}/inspections/${inspectionId}/exterior-checks/${check.id}/`,
                { method: 'DELETE', headers }
              );
            }
          }
        }
        
        // Create new checks
        for (const check of formData.exterior_checks) {
          if (check.status) {
            const checkKey = EXTERIOR_CHECK_MAP[check.item];
            if (!checkKey) {
              console.error('Unknown exterior check item:', check.item);
              continue;
            }
            await fetch(`${API_URL}/inspections/${inspectionId}/exterior-checks/`, {
              method: 'POST',
              headers,
              body: JSON.stringify({
                inspection: inspectionId,
                check_item: checkKey,
                status: check.status,
                remarks: check.remarks,
              }),
            });
          }
        }
        
        setSavedSections(prev => ({ ...prev, exterior: true }));
        setSuccess('Exterior checks saved!');
        break;
      }

      case 5: {
        // Save or delete/recreate engine checks
        if (!inspectionId) throw new Error('Inspection not created yet');
        
        // If already saved, delete all existing checks first
        if (savedSections.engine) {
          const existingChecks = await fetch(
            `${API_URL}/inspections/${inspectionId}/engine-checks/`,
            { headers }
          );
          if (existingChecks.ok) {
            const checks = await existingChecks.json();
            for (const check of checks) {
              await fetch(
                `${API_URL}/inspections/${inspectionId}/engine-checks/${check.id}/`,
                { method: 'DELETE', headers }
              );
            }
          }
        }
        
        // Create new checks
        for (const check of formData.engine_checks) {
          if (check.status) {
            const checkKey = ENGINE_CHECK_MAP[check.item];
            if (!checkKey) {
              console.error('Unknown engine check item:', check.item);
              continue;
            }
            await fetch(`${API_URL}/inspections/${inspectionId}/engine-checks/`, {
              method: 'POST',
              headers,
              body: JSON.stringify({
                inspection: inspectionId,
                check_item: checkKey,
                status: check.status,
                remarks: check.remarks,
              }),
            });
          }
        }
        
        setSavedSections(prev => ({ ...prev, engine: true }));
        setSuccess('Engine checks saved!');
        break;
      }

      case 6: {
        // Save or delete/recreate interior checks
        if (!inspectionId) throw new Error('Inspection not created yet');
        
        // If already saved, delete all existing checks first
        if (savedSections.interior) {
          const existingChecks = await fetch(
            `${API_URL}/inspections/${inspectionId}/interior-checks/`,
            { headers }
          );
          if (existingChecks.ok) {
            const checks = await existingChecks.json();
            for (const check of checks) {
              await fetch(
                `${API_URL}/inspections/${inspectionId}/interior-checks/${check.id}/`,
                { method: 'DELETE', headers }
              );
            }
          }
        }
        
        // Create new checks
        for (const check of formData.interior_checks) {
          if (check.status) {
            const checkKey = INTERIOR_CHECK_MAP[check.item];
            if (!checkKey) {
              console.error('Unknown interior check item:', check.item);
              continue;
            }
            await fetch(`${API_URL}/inspections/${inspectionId}/interior-checks/`, {
              method: 'POST',
              headers,
              body: JSON.stringify({
                inspection: inspectionId,
                check_item: checkKey,
                status: check.status,
                remarks: check.remarks,
              }),
            });
          }
        }
        
        setSavedSections(prev => ({ ...prev, interior: true }));
        setSuccess('Interior checks saved!');
        break;
      }

      case 7: {
        // Save or delete/recreate functional checks
        if (!inspectionId) throw new Error('Inspection not created yet');
        
        // If already saved, delete all existing checks first
        if (savedSections.functional) {
          const existingChecks = await fetch(
            `${API_URL}/inspections/${inspectionId}/functional-checks/`,
            { headers }
          );
          if (existingChecks.ok) {
            const checks = await existingChecks.json();
            for (const check of checks) {
              await fetch(
                `${API_URL}/inspections/${inspectionId}/functional-checks/${check.id}/`,
                { method: 'DELETE', headers }
              );
            }
          }
        }
        
        // Create new checks
        for (const check of formData.functional_checks) {
          if (check.status) {
            const checkKey = FUNCTIONAL_CHECK_MAP[check.item];
            if (!checkKey) {
              console.error('Unknown functional check item:', check.item);
              continue;
            }
            await fetch(`${API_URL}/inspections/${inspectionId}/functional-checks/`, {
              method: 'POST',
              headers,
              body: JSON.stringify({
                inspection: inspectionId,
                check_item: checkKey,
                status: check.status,
                remarks: check.remarks,
              }),
            });
          }
        }
        
        setSavedSections(prev => ({ ...prev, functional: true }));
        setSuccess('Functional checks saved!');
        break;
      }

      case 8: {
        // Save or delete/recreate safety equipment checks
        if (!inspectionId) throw new Error('Inspection not created yet');
        
        // If already saved, delete all existing checks first
        if (savedSections.safety) {
          const existingChecks = await fetch(
            `${API_URL}/inspections/${inspectionId}/safety-checks/`,
            { headers }
          );
          if (existingChecks.ok) {
            const checks = await existingChecks.json();
            for (const check of checks) {
              await fetch(
                `${API_URL}/inspections/${inspectionId}/safety-checks/${check.id}/`,
                { method: 'DELETE', headers }
              );
            }
          }
        }
        
        // Create new checks
        for (const check of formData.safety_checks) {
          if (check.status) {
            const checkKey = SAFETY_CHECK_MAP[check.item];
            if (!checkKey) {
              console.error('Unknown safety check item:', check.item);
              continue;
            }
            await fetch(`${API_URL}/inspections/${inspectionId}/safety-checks/`, {
              method: 'POST',
              headers,
              body: JSON.stringify({
                inspection: inspectionId,
                check_item: checkKey,
                status: check.status,
                remarks: check.remarks,
              }),
            });
          }
        }
        
        setSavedSections(prev => ({ ...prev, safety: true }));
        setSuccess('Safety equipment checks saved!');
        break;
      }

      default:
        break;
    }

    // Clear success message after 2 seconds
    setTimeout(() => setSuccess(''), 2000);
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return;
    
    if (!inspectionId) {
      setError('No inspection created. Please start from step 1.');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('Saving final verification...');

    try {
      const token = localStorage.getItem('access_token');
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      };

      // Save final verification as supervisor remarks
      // Use PATCH if remarks already exist, POST otherwise
      const isRemarksUpdate = !!sectionIds.supervisorRemarksId;
      const remarksMethod = isRemarksUpdate ? 'PATCH' : 'POST';
      const remarksUrl = isRemarksUpdate 
        ? `${API_URL}/inspections/${inspectionId}/supervisor-remarks/${sectionIds.supervisorRemarksId}/`
        : `${API_URL}/inspections/${inspectionId}/supervisor-remarks/`;
      
      const remarksResponse = await fetch(remarksUrl, {
        method: remarksMethod,
        headers,
        body: JSON.stringify({
          inspection: inspectionId,
          supervisor_name: 'Current User', // Will be replaced by backend
          remarks: `Defects Rectified: ${formData.all_defects_rectified ? 'Yes' : 'No'}. ${formData.defects_remarks}\n` +
                   `Driver Briefed: ${formData.driver_briefed ? 'Yes' : 'No'}. ${formData.briefing_remarks}\n` +
                   `Vehicle Ready: ${formData.vehicle_ready ? 'Yes' : 'No'}. ${formData.ready_remarks}`,
          recommendation: formData.vehicle_ready ? 'Vehicle cleared for departure' : 'Vehicle requires attention before departure',
        }),
      });

      if (!remarksResponse.ok) {
        const errorData = await remarksResponse.json();
        throw new Error(`Failed to save supervisor remarks: ${JSON.stringify(errorData)}`);
      }
      
      // Store the ID if it was a create
      if (!isRemarksUpdate) {
        const remarksResult = await remarksResponse.json();
        setSectionIds(prev => ({ ...prev, supervisorRemarksId: remarksResult.id?.toString() || null }));
      }

      // Submit the inspection for approval (changes status from 'draft' to 'submitted')
      setSuccess('Submitting inspection for approval...');
      const submitResponse = await fetch(`${API_URL}/inspections/${inspectionId}/submit/`, {
        method: 'POST',
        headers,
      });

      if (!submitResponse.ok) {
        const errorData = await submitResponse.json();
        throw new Error(`Failed to submit inspection: ${errorData.error || JSON.stringify(errorData)}`);
      }

      setSuccess('Pre-trip inspection submitted for approval! Redirecting...');
      setTimeout(() => {
        router.push('/dashboard/inspections');
      }, 2000);
    } catch (err) {
      setError(`Failed to complete submission: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const getFormTitle = () => {
    const titles = [
      'Basic Information',
      'Health & Fitness Check',
      'Documentation & Compliance',
      'Vehicle Exterior Checks',
      'Engine & Fluids Check',
      'Interior & Cabin Check',
      'Functional Checks',
      'Safety Equipment Check',
      'Final Verification'
    ];
    return titles[currentStep - 1];
  };

  const renderForm = () => {
    switch (currentStep) {
      case 1:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            <div style={{ marginBottom: '20px' }}>
              <label className="label">Driver *</label>
              <select
                className="input"
                value={formData.driver}
                onChange={(e) => setFormData({ ...formData, driver: e.target.value })}
              >
                <option value="">Select Driver</option>
                {drivers.map(d => (
                  <option key={d.id} value={d.id}>{d.full_name}</option>
                ))}
              </select>
            </div>
            
            <div style={{ marginBottom: '20px' }}>
              <label className="label">Vehicle *</label>
              <select
                className="input"
                value={formData.vehicle}
                onChange={(e) => setFormData({ ...formData, vehicle: e.target.value })}
              >
                <option value="">Select Vehicle</option>
                {vehicles.map(v => (
                  <option key={v.id} value={v.id}>{v.registration_number} - {v.vehicle_type}</option>
                ))}
              </select>
            </div>
            
            <div style={{ marginBottom: '20px' }}>
              <label className="label">Mechanic (Optional)</label>
              <select
                className="input"
                value={formData.mechanic}
                onChange={(e) => setFormData({ ...formData, mechanic: e.target.value })}
              >
                <option value="">Select Mechanic (Optional)</option>
                {mechanics.map(m => (
                  <option key={m.id} value={m.id}>{m.full_name}</option>
                ))}
              </select>
            </div>
            
            <div style={{ marginBottom: '20px' }}>
              <label className="label">Inspection Date *</label>
              <input
                type="date"
                className="input"
                value={formData.inspection_date}
                onChange={(e) => setFormData({ ...formData, inspection_date: e.target.value })}
              />
            </div>
            
            <div style={{ marginBottom: '20px' }}>
              <label className="label">Route *</label>
              <input
                type="text"
                className="input"
                placeholder="e.g., Lusaka - Ndola"
                value={formData.route}
                onChange={(e) => setFormData({ ...formData, route: e.target.value })}
              />
            </div>
            
            <div style={{ marginBottom: '20px' }}>
              <label className="label">Approved Driving Hours *</label>
              <input
                type="text"
                className="input"
                placeholder="e.g., 6 hrs 50 mins"
                value={formData.approved_driving_hours}
                onChange={(e) => setFormData({ ...formData, approved_driving_hours: e.target.value })}
              />
            </div>
            
            <div style={{ marginBottom: '20px' }}>
              <label className="label">Approved Rest Stops *</label>
              <input
                type="number"
                className="input"
                min="0"
                value={formData.approved_rest_stops}
                onChange={(e) => setFormData({ ...formData, approved_rest_stops: parseInt(e.target.value) || 0 })}
              />
            </div>
          </div>
        );
        
      case 2:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            
            {/* CRITICAL: Rest/Fatigue Clearance - Must be first and prominent */}
            <div style={{ 
              marginBottom: '30px', 
              padding: '20px', 
              backgroundColor: formData.adequate_rest === false ? '#fee2e2' : (formData.adequate_rest === true ? '#dcfce7' : '#fef3c7'),
              borderRadius: '8px',
              border: formData.adequate_rest === false ? '2px solid #ef4444' : (formData.adequate_rest === true ? '2px solid #22c55e' : '2px solid #f59e0b')
            }}>
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '10px', 
                marginBottom: '15px' 
              }}>
                <span style={{ fontSize: '24px' }}>⚠️</span>
                <label style={{ 
                  display: 'block', 
                  fontWeight: '700', 
                  color: '#000', 
                  fontSize: '16px' 
                }}>
                  FATIGUE CLEARANCE - CRITICAL *
                </label>
              </div>
              <p style={{ 
                color: '#374151', 
                marginBottom: '15px', 
                fontSize: '15px',
                fontWeight: '500'
              }}>
                Has the driver rested for 8 hours or more?
              </p>
              <div style={{ display: 'flex', gap: '20px', marginBottom: '10px' }}>
                <RadioOption
                  label="Yes - Driver has rested 8+ hours"
                  value="yes"
                  selected={formData.adequate_rest === true}
                  onChange={() => setFormData({ ...formData, adequate_rest: true })}
                />
                <RadioOption
                  label="No - Driver has NOT rested 8+ hours"
                  value="no"
                  selected={formData.adequate_rest === false}
                  onChange={() => setFormData({ ...formData, adequate_rest: false })}
                />
              </div>
              
              {/* Warning message when No is selected */}
              {formData.adequate_rest === false && (
                <div style={{
                  marginTop: '15px',
                  padding: '15px',
                  backgroundColor: '#fecaca',
                  borderRadius: '6px',
                  border: '1px solid #ef4444'
                }}>
                  <p style={{ 
                    color: '#991b1b', 
                    fontWeight: '700', 
                    margin: 0,
                    fontSize: '14px'
                  }}>
                    ⛔ TRAVEL NOT PERMITTED
                  </p>
                  <p style={{ 
                    color: '#991b1b', 
                    margin: '8px 0 0 0',
                    fontSize: '13px'
                  }}>
                    The driver has not had adequate rest (8 hours or more) and should NOT travel. 
                    Please ensure the driver rests sufficiently before attempting the trip.
                  </p>
                </div>
              )}
              
              {/* Cleared message when Yes is selected */}
              {formData.adequate_rest === true && (
                <div style={{
                  marginTop: '15px',
                  padding: '12px',
                  backgroundColor: '#bbf7d0',
                  borderRadius: '6px',
                  border: '1px solid #22c55e'
                }}>
                  <p style={{ 
                    color: '#166534', 
                    fontWeight: '600', 
                    margin: 0,
                    fontSize: '13px'
                  }}>
                    ✓ Driver has confirmed adequate rest - Fatigue clearance granted
                  </p>
                </div>
              )}
            </div>
            
            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                Alcohol/Drug Test *
              </label>
              <div style={{ display: 'flex', gap: '15px', marginBottom: '10px' }}>
                <RadioOption
                  label="Pass"
                  value="pass"
                  selected={formData.alcohol_test_status === 'pass'}
                  onChange={() => setFormData({ ...formData, alcohol_test_status: 'pass' })}
                />
                <RadioOption
                  label="Fail"
                  value="fail"
                  selected={formData.alcohol_test_status === 'fail'}
                  onChange={() => setFormData({ ...formData, alcohol_test_status: 'fail' })}
                />
              </div>
              <textarea
                className="input"
                rows={2}
                placeholder="Remarks..."
                value={formData.alcohol_test_remarks}
                onChange={(e) => setFormData({ ...formData, alcohol_test_remarks: e.target.value })}
                style={{ marginTop: '10px' }}
              />
            </div>

            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                Temperature Check *
              </label>
              <div style={{ display: 'flex', gap: '15px', marginBottom: '10px' }}>
                <RadioOption
                  label="Pass"
                  value="pass"
                  selected={formData.temperature_check_status === 'pass'}
                  onChange={() => setFormData({ ...formData, temperature_check_status: 'pass' })}
                />
                <RadioOption
                  label="Fail"
                  value="fail"
                  selected={formData.temperature_check_status === 'fail'}
                  onChange={() => setFormData({ ...formData, temperature_check_status: 'fail' })}
                />
              </div>
              <input
                type="number"
                step="0.1"
                className="input"
                placeholder="Temperature Value (°C)"
                value={formData.temperature_value}
                onChange={(e) => setFormData({ ...formData, temperature_value: e.target.value })}
                style={{ marginTop: '10px' }}
              />
            </div>

            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                Driver Fit for Duty *
              </label>
              <div style={{ display: 'flex', gap: '15px' }}>
                <RadioOption
                  label="Yes"
                  value="yes"
                  selected={formData.fit_for_duty === true}
                  onChange={() => setFormData({ ...formData, fit_for_duty: true })}
                />
                <RadioOption
                  label="No"
                  value="no"
                  selected={formData.fit_for_duty === false}
                  onChange={() => setFormData({ ...formData, fit_for_duty: false })}
                />
              </div>
            </div>

            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                On Medication *
              </label>
              <div style={{ display: 'flex', gap: '15px', marginBottom: '10px' }}>
                <RadioOption
                  label="Yes"
                  value="yes"
                  selected={formData.medication_status === true}
                  onChange={() => setFormData({ ...formData, medication_status: true })}
                />
                <RadioOption
                  label="No"
                  value="no"
                  selected={formData.medication_status === false}
                  onChange={() => setFormData({ ...formData, medication_status: false })}
                />
              </div>
              <input
                type="text"
                className="input"
                placeholder="Medication Remarks (if applicable)"
                value={formData.medication_remarks}
                onChange={(e) => setFormData({ ...formData, medication_remarks: e.target.value })}
                style={{ marginTop: '10px' }}
              />
            </div>

            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                No Health Impairments *
              </label>
              <div style={{ display: 'flex', gap: '15px' }}>
                <RadioOption
                  label="Yes"
                  value="yes"
                  selected={formData.no_health_impairment === true}
                  onChange={() => setFormData({ ...formData, no_health_impairment: true })}
                />
                <RadioOption
                  label="No"
                  value="no"
                  selected={formData.no_health_impairment === false}
                  onChange={() => setFormData({ ...formData, no_health_impairment: false })}
                />
              </div>
            </div>

            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                Fatigue Checklist Completed *
              </label>
              <div style={{ display: 'flex', gap: '15px', marginBottom: '10px' }}>
                <RadioOption
                  label="Yes"
                  value="yes"
                  selected={formData.fatigue_checklist_completed === true}
                  onChange={() => setFormData({ ...formData, fatigue_checklist_completed: true })}
                />
                <RadioOption
                  label="No"
                  value="no"
                  selected={formData.fatigue_checklist_completed === false}
                  onChange={() => setFormData({ ...formData, fatigue_checklist_completed: false })}
                />
              </div>
              <textarea
                className="input"
                rows={2}
                placeholder="Fatigue Remarks..."
                value={formData.fatigue_remarks}
                onChange={(e) => setFormData({ ...formData, fatigue_remarks: e.target.value })}
                style={{ marginTop: '10px' }}
              />
            </div>
          </div>
        );

      case 3:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            
            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                Certificate of Fitness *
              </label>
              <div style={{ display: 'flex', gap: '15px' }}>
                <RadioOption
                  label="Valid"
                  value="valid"
                  selected={formData.certificate_of_fitness === 'valid'}
                  onChange={() => setFormData({ ...formData, certificate_of_fitness: 'valid' })}
                />
                <RadioOption
                  label="Invalid"
                  value="invalid"
                  selected={formData.certificate_of_fitness === 'invalid'}
                  onChange={() => setFormData({ ...formData, certificate_of_fitness: 'invalid' })}
                />
              </div>
            </div>

            {[
              { key: 'road_tax_valid', label: 'Road Tax Valid' },
              { key: 'insurance_valid', label: 'Insurance Valid' },
              { key: 'trip_authorization_signed', label: 'Trip Authorization Signed' },
              { key: 'logbook_present', label: 'Logbook Present' },
              { key: 'driver_handbook_present', label: 'Driver Handbook Present' },
              { key: 'permits_valid', label: 'Permits Valid' },
              { key: 'ppe_available', label: 'PPE Available' },
              { key: 'route_familiarity', label: 'Route Familiarity' },
              { key: 'emergency_procedures_known', label: 'Emergency Procedures Known' },
              { key: 'gps_activated', label: 'GPS Activated' },
              { key: 'safety_briefing_provided', label: 'Safety Briefing Provided' },
              { key: 'rtsa_clearance', label: 'RTSA Clearance' },
            ].map(({ key, label }) => (
              <div key={key} style={{ marginBottom: '25px' }}>
                <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                  {label} *
                </label>
                <div style={{ display: 'flex', gap: '15px' }}>
                  <RadioOption
                    label="Yes"
                    value="yes"
                    selected={formData[key as keyof InspectionFormData] === true}
                    onChange={() => setFormData({ ...formData, [key]: true })}
                  />
                  <RadioOption
                    label="No"
                    value="no"
                    selected={formData[key as keyof InspectionFormData] === false}
                    onChange={() => setFormData({ ...formData, [key]: false })}
                  />
                </div>
              </div>
            ))}

            <div style={{ marginBottom: '20px' }}>
              <label className="label">Emergency Contact *</label>
              <input
                type="text"
                className="input"
                placeholder="Enter emergency contact number"
                value={formData.emergency_contact}
                onChange={(e) => setFormData({ ...formData, emergency_contact: e.target.value })}
              />
            </div>
          </div>
        );

      case 4:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            {formData.exterior_checks.map((check, index) => (
              <CheckItem
                key={index}
                label={check.item}
                status={check.status}
                remarks={check.remarks}
                onStatusChange={(status) => {
                  const updated = [...formData.exterior_checks];
                  updated[index].status = status;
                  setFormData({ ...formData, exterior_checks: updated });
                }}
                onRemarksChange={(remarks) => {
                  const updated = [...formData.exterior_checks];
                  updated[index].remarks = remarks;
                  setFormData({ ...formData, exterior_checks: updated });
                }}
              />
            ))}
          </div>
        );

      case 5:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            {formData.engine_checks.map((check, index) => (
              <CheckItem
                key={index}
                label={check.item}
                status={check.status}
                remarks={check.remarks}
                onStatusChange={(status) => {
                  const updated = [...formData.engine_checks];
                  updated[index].status = status;
                  setFormData({ ...formData, engine_checks: updated });
                }}
                onRemarksChange={(remarks) => {
                  const updated = [...formData.engine_checks];
                  updated[index].remarks = remarks;
                  setFormData({ ...formData, engine_checks: updated });
                }}
              />
            ))}
          </div>
        );

      case 6:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            {formData.interior_checks.map((check, index) => (
              <CheckItem
                key={index}
                label={check.item}
                status={check.status}
                remarks={check.remarks}
                onStatusChange={(status) => {
                  const updated = [...formData.interior_checks];
                  updated[index].status = status;
                  setFormData({ ...formData, interior_checks: updated });
                }}
                onRemarksChange={(remarks) => {
                  const updated = [...formData.interior_checks];
                  updated[index].remarks = remarks;
                  setFormData({ ...formData, interior_checks: updated });
                }}
              />
            ))}
          </div>
        );

      case 7:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            {formData.functional_checks.map((check, index) => (
              <CheckItem
                key={index}
                label={check.item}
                status={check.status}
                remarks={check.remarks}
                onStatusChange={(status) => {
                  const updated = [...formData.functional_checks];
                  updated[index].status = status;
                  setFormData({ ...formData, functional_checks: updated });
                }}
                onRemarksChange={(remarks) => {
                  const updated = [...formData.functional_checks];
                  updated[index].remarks = remarks;
                  setFormData({ ...formData, functional_checks: updated });
                }}
              />
            ))}
          </div>
        );

      case 8:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            {formData.safety_checks.map((check, index) => (
              <CheckItem
                key={index}
                label={check.item}
                status={check.status}
                remarks={check.remarks}
                onStatusChange={(status) => {
                  const updated = [...formData.safety_checks];
                  updated[index].status = status;
                  setFormData({ ...formData, safety_checks: updated });
                }}
                onRemarksChange={(remarks) => {
                  const updated = [...formData.safety_checks];
                  updated[index].remarks = remarks;
                  setFormData({ ...formData, safety_checks: updated });
                }}
              />
            ))}
          </div>
        );

      case 9:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            
            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                All Critical Defects Rectified Before Departure? *
              </label>
              <div style={{ display: 'flex', gap: '15px', marginBottom: '10px' }}>
                <RadioOption
                  label="Yes"
                  value="yes"
                  selected={formData.all_defects_rectified === true}
                  onChange={() => setFormData({ ...formData, all_defects_rectified: true })}
                />
                <RadioOption
                  label="No"
                  value="no"
                  selected={formData.all_defects_rectified === false}
                  onChange={() => setFormData({ ...formData, all_defects_rectified: false })}
                />
              </div>
              <textarea
                className="input"
                rows={3}
                placeholder="Remarks..."
                value={formData.defects_remarks}
                onChange={(e) => setFormData({ ...formData, defects_remarks: e.target.value })}
                style={{ marginTop: '10px' }}
              />
            </div>

            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                Driver Briefed on Trip Hazards and Route Plan? *
              </label>
              <div style={{ display: 'flex', gap: '15px', marginBottom: '10px' }}>
                <RadioOption
                  label="Yes"
                  value="yes"
                  selected={formData.driver_briefed === true}
                  onChange={() => setFormData({ ...formData, driver_briefed: true })}
                />
                <RadioOption
                  label="No"
                  value="no"
                  selected={formData.driver_briefed === false}
                  onChange={() => setFormData({ ...formData, driver_briefed: false })}
                />
              </div>
              <textarea
                className="input"
                rows={3}
                placeholder="Remarks..."
                value={formData.briefing_remarks}
                onChange={(e) => setFormData({ ...formData, briefing_remarks: e.target.value })}
                style={{ marginTop: '10px' }}
              />
            </div>

            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                Vehicle Safe and Ready for Dispatch? *
              </label>
              <div style={{ display: 'flex', gap: '15px', marginBottom: '10px' }}>
                <RadioOption
                  label="Yes"
                  value="yes"
                  selected={formData.vehicle_ready === true}
                  onChange={() => setFormData({ ...formData, vehicle_ready: true })}
                />
                <RadioOption
                  label="No"
                  value="no"
                  selected={formData.vehicle_ready === false}
                  onChange={() => setFormData({ ...formData, vehicle_ready: false })}
                />
              </div>
              <textarea
                className="input"
                rows={3}
                placeholder="Remarks..."
                value={formData.ready_remarks}
                onChange={(e) => setFormData({ ...formData, ready_remarks: e.target.value })}
                style={{ marginTop: '10px' }}
              />
            </div>

            <div style={{ 
              marginTop: '30px', 
              padding: '20px', 
              backgroundColor: '#e8f5e9', 
              borderRadius: '8px',
              border: '1px solid #4CAF50'
            }}>
              <h3 style={{ color: '#2e7d32', marginBottom: '10px' }}>Ready to Submit</h3>
              <p style={{ color: '#000', marginBottom: '0' }}>
                You&apos;ve completed all sections of the pre-trip inspection. Click &quot;Create Inspection&quot; to submit.
              </p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="dashboard-container">
      {initialLoading ? (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '400px',
          gap: '20px'
        }}>
          <div style={{
            width: '50px',
            height: '50px',
            border: '4px solid #f3f3f3',
            borderTop: '4px solid #007bff',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
          <p style={{ color: '#666', fontSize: '16px' }}>Loading inspection data...</p>
          <style jsx>{`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}</style>
        </div>
      ) : (
        <>
      <div className="dashboard-header">
        <div>
          <h1>New Pre-Trip Inspection</h1>
          <p style={{ color: '#666', marginTop: '5px' }}>
            Complete all sections of the pre-trip checklist
          </p>
        </div>
        <button 
          onClick={() => router.push('/dashboard/inspections')} 
          className="button-secondary"
          style={{ width: 'auto' }}
        >
          Cancel
        </button>
      </div>

      <div className="profile-card">
        <ProgressTracker 
          currentStep={currentStep} 
          totalSteps={TOTAL_STEPS}
        />

        {error && <div className="alert alert-error" style={{ marginBottom: '20px' }}>{error}</div>}
        {success && <div className="alert alert-success" style={{ marginBottom: '20px' }}>{success}</div>}

        {renderForm()}

        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          marginTop: '30px',
          paddingTop: '20px',
          borderTop: '1px solid #e0e0e0'
        }}>
          <button
            onClick={handlePrevious}
            disabled={currentStep === 1 || loading}
            className="button-secondary"
            style={{ 
              width: 'auto',
              opacity: currentStep === 1 ? 0.5 : 1,
              cursor: currentStep === 1 ? 'not-allowed' : 'pointer',
            }}
          >
            Previous
          </button>

          {currentStep < TOTAL_STEPS ? (
            <button
              onClick={handleNext}
              disabled={loading}
              className="button-primary"
              style={{ width: 'auto' }}
            >
              Next
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="button-primary"
              style={{ width: 'auto' }}
            >
              {loading ? 'Creating...' : 'Create Inspection'}
            </button>
          )}
        </div>
      </div>
      </>
      )}
    </div>
  );
}
