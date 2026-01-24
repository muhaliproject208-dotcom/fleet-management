// Inspection Module TypeScript Types
// Based on backend models in backend/inspections/models/

export enum InspectionStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  APPROVED = 'approved',
  REJECTED = 'rejected',
}

export enum HealthCheckStatus {
  PASS = 'pass',
  FAIL = 'fail',
}

export enum CheckStatus {
  PASS = 'pass',
  FAIL = 'fail',
}

export enum DocumentStatus {
  VALID = 'valid',
  EXPIRED = 'expired',
  MISSING = 'missing',
}

// Core Inspection Types

export interface CompletionInfo {
  completed_steps: number[];
  next_step: number | null;
  completion_percentage: number;
  total_steps: number;
}

export interface PreTripInspection {
  id: string;
  inspection_id: string;
  
  // Core relationships
  driver: {
    id: string;
    driver_id: string;
    full_name: string;
  };
  vehicle: {
    id: string;
    vehicle_id: string;
    registration_number: string;
  };
  supervisor: {
    id: string;
    full_name: string;
  };
  mechanic?: {
    id: string;
    mechanic_id: string;
    full_name: string;
  };
  
  // Inspection details
  inspection_date: string;
  route: string;
  approved_driving_hours: string;
  approved_rest_stops: number;
  
  // Workflow
  status: InspectionStatus;
  approval_status_updated_at?: string;
  approved_by?: {
    id: string;
    full_name: string;
    email: string;
  };
  rejection_reason?: string;
  
  // Completion tracking for drafts
  completion_info?: CompletionInfo | null;
  
  // Timestamps
  created_at: string;
  updated_at: string;
}

// Vehicle Check Types
export interface VehicleCheck {
  id: string;
  inspection: string;
  check_item: string;
  status: CheckStatus;
  remarks?: string;
  created_at: string;
  updated_at: string;
}

export interface PreTripInspectionFull extends PreTripInspection {
  // OneToOne relationships
  health_fitness?: HealthFitnessCheck | null;
  documentation?: DocumentationCompliance | null;
  
  // Vehicle checks (ForeignKey many)
  exterior_checks?: VehicleCheck[];
  engine_fluid_checks?: VehicleCheck[];
  interior_cabin_checks?: VehicleCheck[];
  functional_checks?: VehicleCheck[];
  safety_equipment_checks?: VehicleCheck[];
  
  // Computed fields
  completion_percentage?: number;
  total_violation_points?: number;
  has_critical_failures?: boolean;
}

export interface CreateInspectionData {
  driver: string;
  vehicle: string;
  mechanic?: string;
  inspection_date: string;
  route: string;
  approved_driving_hours: string;
  approved_rest_stops: number;
}

export type UpdateInspectionData = Partial<CreateInspectionData>;

// Health & Fitness Check

export type HealthFitnessCheck = BaseModel & {
  inspection: string;

  // Checks
  alcohol_test_status: HealthCheckStatus;
  alcohol_test_remarks?: string;
  temperature_check_status: HealthCheckStatus;
  temperature_value?: number;

  // Fitness flags
  fit_for_duty: boolean;
  medication_status: boolean;
  medication_remarks?: string;
  no_health_impairment: boolean;

  // Fatigue
  fatigue_checklist_completed: boolean;
  fatigue_remarks?: string;

  created_at: string;
  updated_at: string;
};

export interface CreateHealthFitnessData {
  inspection: string;
  alcohol_test_status: HealthCheckStatus;
  alcohol_test_remarks?: string;
  temperature_check_status: HealthCheckStatus;
  temperature_value?: number;
  fit_for_duty: boolean;
  medication_status: boolean;
  medication_remarks?: string;
  no_health_impairment: boolean;
  fatigue_checklist_completed: boolean;
  fatigue_remarks?: string;
}

// Documentation Compliance

export interface DocumentationCompliance {
  id: string;
  inspection: string;
  
  // Documentation checks
  certificate_of_fitness: 'valid' | 'invalid';
  road_tax_valid: boolean;
  insurance_valid: boolean;
  trip_authorization_signed: boolean;
  logbook_present: boolean;
  driver_handbook_present: boolean;
  permits_valid: boolean;
  ppe_available: boolean;
  route_familiarity: boolean;
  emergency_procedures_known: boolean;
  gps_activated: boolean;
  safety_briefing_provided: boolean;
  rtsa_clearance: boolean;
  emergency_contact: string;
  
  created_at: string;
  updated_at: string;
}

export interface CreateDocumentationData {
  inspection: string;
  certificate_of_fitness: 'valid' | 'invalid';
  road_tax_valid: boolean;
  insurance_valid: boolean;
  trip_authorization_signed: boolean;
  logbook_present: boolean;
  driver_handbook_present: boolean;
  permits_valid: boolean;
  ppe_available: boolean;
  route_familiarity: boolean;
  emergency_procedures_known: boolean;
  gps_activated: boolean;
  safety_briefing_provided: boolean;
  rtsa_clearance: boolean;
  emergency_contact: string;
}

// API Response Types

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface APIResponse<T> {
  data?: T;
  error?: string;
}
