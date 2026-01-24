# Fleet Management - Inspection Module Frontend Implementation Guide

## 📋 Table of Contents
1. [Overview](#overview)
2. [Backend API Analysis](#backend-api-analysis)
3. [Data Models & TypeScript Interfaces](#data-models--typescript-interfaces)
4. [API Layer Implementation](#api-layer-implementation)
5. [UI/UX Design & Component Structure](#uiux-design--component-structure)
6. [Step-by-Step Implementation Plan](#step-by-step-implementation-plan)
7. [Advanced Features](#advanced-features)
8. [Testing Strategy](#testing-strategy)

---

## 🎯 Overview

The Inspection Module is a **comprehensive pre-trip and post-trip inspection system** for fleet management. It consists of:

- **1 Main Inspection Entity** (`PreTripInspection`)
- **12 Related Sub-modules** (Health checks, vehicle checks, behaviors, etc.)
- **Role-Based Workflow** (Transport Supervisor → Fleet Manager approval)
- **PDF Generation** for reports
- **Audit Logging** for compliance

### Key Features
- ✅ Multi-step inspection workflow (Draft → Submitted → Approved/Rejected)
- ✅ Comprehensive vehicle and driver health checks
- ✅ Real-time behavior monitoring during trips
- ✅ Post-trip reporting and risk assessment
- ✅ Corrective measures and enforcement actions
- ✅ Digital sign-offs with role verification
- ✅ Complete audit trail

---

## 🔌 Backend API Analysis

### Main Endpoints

```
Base URL: http://localhost:8000/api/v1/
```

#### 1. **Main Inspections** (`/inspections/`)
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/inspections/` | List all inspections (filtered by role) | Authenticated |
| POST | `/inspections/` | Create new inspection | Transport Supervisor+ |
| GET | `/inspections/{id}/` | Get detailed inspection (full nested data) | Authenticated |
| PATCH | `/inspections/{id}/` | Update inspection (draft/rejected only) | Transport Supervisor |
| POST | `/inspections/{id}/submit/` | Submit for approval | Transport Supervisor |
| POST | `/inspections/{id}/approve/` | Approve inspection | Fleet Manager |
| POST | `/inspections/{id}/reject/` | Reject inspection (requires reason) | Fleet Manager |
| GET | `/inspections/{id}/pdf/` | Generate PDF report | Authenticated |

#### 2. **Sub-Module Endpoints** (all under `/inspections/`)

```
/inspections/health-fitness/          - Health & Fitness Checks
/inspections/documentation/           - Documentation Compliance
/inspections/exterior-checks/         - Vehicle Exterior Checks
/inspections/engine-checks/           - Engine & Fluid Checks
/inspections/interior-checks/         - Interior Cabin Checks
/inspections/functional-checks/       - Functional System Checks
/inspections/safety-checks/           - Safety Equipment Checks
/inspections/trip-behaviors/          - Trip Behavior Monitoring
/inspections/driving-behaviors/       - Driving Behavior Checks
/inspections/post-trip/               - Post-Trip Reports
/inspections/risk-score/              - Risk Score Summary
/inspections/corrective-measures/     - Corrective Measures
/inspections/enforcement-actions/     - Enforcement Actions
/inspections/supervisor-remarks/      - Supervisor Remarks
/inspections/evaluation/              - Evaluation Summary
/inspections/sign-offs/               - Inspection Sign-Offs
```

Each sub-module supports:
- `GET` - List/filter checks for an inspection
- `POST` - Create new check item
- `GET /{id}/` - Retrieve specific check
- `PATCH /{id}/` - Update check item
- `DELETE /{id}/` - Delete check item

### Query Parameters & Filtering

```typescript
// Main inspections filtering
?status=draft|submitted|approved|rejected
?inspection_date_from=2026-01-01
?inspection_date_to=2026-01-31
?driver={driver_id}
?vehicle={vehicle_id}
?search={keyword}  // Searches: inspection_id, driver name, vehicle registration, route
?page=1
?page_size=25
```

---

## 📦 Data Models & TypeScript Interfaces

### Core Models

#### 1. PreTripInspection (Main Entity)

```typescript
// lib/api/inspections/types.ts

export enum InspectionStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  APPROVED = 'approved',
  REJECTED = 'rejected',
}

export interface PreTripInspection {
  id: string;
  inspection_id: string; // Format: "INSP-0001"
  
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
    vehicle_type: string;
  };
  supervisor: {
    id: string;
    full_name: string;
    email: string;
  };
  mechanic?: {
    id: string;
    mechanic_id: string;
    full_name: string;
  };
  
  // Inspection details
  inspection_date: string; // ISO date
  route: string; // e.g., "Lusaka - Ndola"
  approved_driving_hours: string; // e.g., "6 hrs 50 mins"
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
  
  // Timestamps
  created_at: string;
  updated_at: string;
}

export interface PreTripInspectionFull extends PreTripInspection {
  // OneToOne relationships
  health_fitness?: HealthFitnessCheck;
  documentation?: DocumentationCompliance;
  post_trip?: PostTripReport;
  risk_score?: RiskScoreSummary;
  supervisor_remarks?: SupervisorRemarks;
  evaluation?: EvaluationSummary;
  
  // Many-to-one relationships (arrays)
  exterior_checks: VehicleExteriorCheck[];
  engine_fluid_checks: EngineFluidCheck[];
  interior_cabin_checks: InteriorCabinCheck[];
  functional_checks: FunctionalCheck[];
  safety_equipment_checks: SafetyEquipmentCheck[];
  trip_behaviors: TripBehaviorMonitoring[];
  driving_behaviors: DrivingBehaviorCheck[];
  corrective_measures: CorrectiveMeasure[];
  enforcement_actions: EnforcementAction[];
  sign_offs: InspectionSignOff[];
  
  // Computed fields
  completion_percentage: number; // 0-100
  total_violation_points: number;
  has_critical_failures: boolean;
}

export interface CreateInspectionData {
  driver: string; // driver ID
  vehicle: string; // vehicle ID
  mechanic?: string; // mechanic ID (optional)
  inspection_date: string; // ISO date
  route: string;
  approved_driving_hours: string;
  approved_rest_stops: number;
}

export interface UpdateInspectionData extends Partial<CreateInspectionData> {}
```

#### 2. Health & Fitness Check

```typescript
export enum HealthCheckStatus {
  PASS = 'pass',
  FAIL = 'fail',
}

export interface HealthFitnessCheck {
  id: string;
  inspection: string; // inspection ID
  
  // Checks
  alcohol_test_status: HealthCheckStatus;
  alcohol_test_remarks?: string;
  temperature_check_status: HealthCheckStatus;
  temperature_value?: number; // Celsius (e.g., 36.7)
  
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
}

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
```

#### 3. Documentation Compliance

```typescript
export enum DocumentStatus {
  VALID = 'valid',
  EXPIRED = 'expired',
  MISSING = 'missing',
}

export interface DocumentationCompliance {
  id: string;
  inspection: string;
  
  // Driver documents
  driver_license_status: DocumentStatus;
  driver_license_expiry?: string; // ISO date
  medical_certificate_status: DocumentStatus;
  medical_certificate_expiry?: string;
  
  // Vehicle documents
  vehicle_registration_status: DocumentStatus;
  vehicle_registration_expiry?: string;
  insurance_status: DocumentStatus;
  insurance_expiry?: string;
  fitness_certificate_status: DocumentStatus;
  fitness_certificate_expiry?: string;
  road_tax_status: DocumentStatus;
  road_tax_expiry?: string;
  
  remarks?: string;
  created_at: string;
  updated_at: string;
}
```

#### 4. Vehicle Check (Base Pattern)

```typescript
export enum CheckStatus {
  PASS = 'pass',
  FAIL = 'fail',
}

// Base interface for all vehicle checks
export interface BaseVehicleCheck {
  id: string;
  inspection: string;
  check_item: string;
  status: CheckStatus;
  remarks?: string;
  created_at: string;
  updated_at: string;
}

// Exterior checks
export enum ExteriorItems {
  TIRES = 'tires',
  LIGHTS = 'lights',
  MIRRORS = 'mirrors',
  WINDSHIELD = 'windshield',
  BODY_CONDITION = 'body_condition',
  LOOSE_PARTS = 'loose_parts',
  LEAKS = 'leaks',
}

export interface VehicleExteriorCheck extends BaseVehicleCheck {
  check_item: ExteriorItems;
}

// Engine/Fluid checks
export enum FluidItems {
  ENGINE_OIL = 'engine_oil',
  COOLANT = 'coolant',
  BRAKE_FLUID = 'brake_fluid',
  TRANSMISSION_FLUID = 'transmission_fluid',
  POWER_STEERING_FLUID = 'power_steering_fluid',
  BATTERY = 'battery',
}

export interface EngineFluidCheck extends BaseVehicleCheck {
  check_item: FluidItems;
}

// Similar patterns for:
// - InteriorCabinCheck (seats, seatbelts, HVAC, dashboard, etc.)
// - FunctionalCheck (brakes, steering, horn, wipers, etc.)
// - SafetyEquipmentCheck (fire extinguisher, first aid, reflective triangles, etc.)
```

#### 5. Behavior Monitoring

```typescript
export enum BehaviorStatus {
  COMPLIANT = 'compliant',
  NON_COMPLIANT = 'non_compliant',
}

export interface TripBehaviorMonitoring {
  id: string;
  inspection: string;
  behavior_type: string; // e.g., "speed_limit_adherence", "rest_stop_compliance"
  status: BehaviorStatus;
  violation_points?: number;
  remarks?: string;
  created_at: string;
  updated_at: string;
}

export interface DrivingBehaviorCheck {
  id: string;
  inspection: string;
  behavior_item: string; // e.g., "harsh_braking", "sudden_acceleration"
  frequency: number; // number of occurrences
  severity: 'low' | 'medium' | 'high';
  remarks?: string;
  created_at: string;
  updated_at: string;
}
```

#### 6. Post-Trip & Risk Assessment

```typescript
export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export interface PostTripReport {
  id: string;
  inspection: string;
  
  // Trip details
  actual_departure_time?: string;
  actual_arrival_time?: string;
  total_distance_km?: number;
  fuel_consumed_liters?: number;
  
  // Incidents
  incidents_reported: boolean;
  incident_details?: string;
  vehicle_damage_reported: boolean;
  damage_details?: string;
  
  // Driver feedback
  driver_comments?: string;
  
  created_at: string;
  updated_at: string;
}

export interface RiskScoreSummary {
  id: string;
  inspection: string;
  
  total_risk_score: number; // 0-100
  risk_level: RiskLevel;
  
  // Score breakdown
  vehicle_condition_score: number;
  driver_health_score: number;
  documentation_score: number;
  behavior_score: number;
  
  recommendations?: string;
  created_at: string;
  updated_at: string;
}
```

#### 7. Enforcement & Evaluation

```typescript
export enum MeasureType {
  WARNING = 'warning',
  TRAINING = 'training',
  SUSPENSION = 'suspension',
  VEHICLE_REPAIR = 'vehicle_repair',
}

export enum ActionType {
  FINE = 'fine',
  LICENSE_SUSPENSION = 'license_suspension',
  VEHICLE_GROUNDING = 'vehicle_grounding',
  DRIVER_RETRAINING = 'driver_retraining',
}

export interface CorrectiveMeasure {
  id: string;
  inspection: string;
  measure_type: MeasureType;
  description: string;
  assigned_to?: string; // mechanic or driver ID
  deadline?: string; // ISO date
  is_completed: boolean;
  completion_date?: string;
  created_at: string;
  updated_at: string;
}

export interface EnforcementAction {
  id: string;
  inspection: string;
  action_type: ActionType;
  reason: string;
  penalty_amount?: number; // for fines
  effective_date?: string;
  expiry_date?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export enum PerformanceLevel {
  EXCELLENT = 'excellent',
  GOOD = 'good',
  SATISFACTORY = 'satisfactory',
  NEEDS_IMPROVEMENT = 'needs_improvement',
  UNSATISFACTORY = 'unsatisfactory',
}

export interface SupervisorRemarks {
  id: string;
  inspection: string;
  remarks: string;
  created_by: {
    id: string;
    full_name: string;
  };
  created_at: string;
  updated_at: string;
}

export interface EvaluationSummary {
  id: string;
  inspection: string;
  
  overall_performance: PerformanceLevel;
  driver_performance_rating: number; // 1-5
  vehicle_condition_rating: number; // 1-5
  
  strengths?: string;
  areas_for_improvement?: string;
  recommendations?: string;
  
  created_at: string;
  updated_at: string;
}
```

#### 8. Sign-Offs & Audit

```typescript
export enum SignOffRole {
  DRIVER = 'driver',
  SUPERVISOR = 'supervisor',
  MECHANIC = 'mechanic',
  FLEET_MANAGER = 'fleet_manager',
}

export interface InspectionSignOff {
  id: string;
  inspection: string;
  role: SignOffRole;
  signed_by: {
    id: string;
    full_name: string;
  };
  signature_timestamp: string;
  remarks?: string;
  created_at: string;
}

export enum AuditAction {
  CREATED = 'created',
  UPDATED = 'updated',
  SUBMITTED = 'submitted',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  DELETED = 'deleted',
}

export interface AuditLog {
  id: string;
  inspection: string;
  action: AuditAction;
  user: {
    id: string;
    full_name: string;
  };
  timestamp: string;
  changes?: Record<string, any>; // JSON field with old/new values
}
```

---

## 🔧 API Layer Implementation

### File Structure

```
frontend/lib/api/inspections/
├── index.ts                      # Main inspections API
├── types.ts                      # All TypeScript interfaces
├── healthFitness.ts              # Health & Fitness API
├── documentation.ts              # Documentation API
├── vehicleChecks.ts              # All vehicle checks (exterior, engine, interior, etc.)
├── behavior.ts                   # Behavior monitoring API
├── postTrip.ts                   # Post-trip & risk score API
├── enforcement.ts                # Corrective measures & enforcement API
├── evaluation.ts                 # Remarks & evaluation API
├── signoff.ts                    # Sign-off API
└── utils.ts                      # Helper functions
```

### Example: Main Inspections API

```typescript
// lib/api/inspections/index.ts

import { API_URL } from '../index';
import type {
  PreTripInspection,
  PreTripInspectionFull,
  CreateInspectionData,
  UpdateInspectionData,
  InspectionStatus,
} from './types';

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const getInspections = async (params?: {
  status?: InspectionStatus;
  inspection_date_from?: string;
  inspection_date_to?: string;
  driver?: string;
  vehicle?: string;
  search?: string;
  page?: number;
  page_size?: number;
}) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }

    const response = await fetch(
      `${API_URL}/inspections/?${queryParams.toString()}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || 'Failed to fetch inspections' };
    }

    const data: PaginatedResponse<PreTripInspection> = await response.json();
    return { data };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to fetch inspections',
    };
  }
};

export const getInspection = async (id: string) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/inspections/${id}/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail || 'Failed to fetch inspection' };
    }

    const data: PreTripInspectionFull = await response.json();
    return { data };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to fetch inspection',
    };
  }
};

export const createInspection = async (inspectionData: CreateInspectionData) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/inspections/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(inspectionData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return {
        error: errorData.detail || errorData.message || 'Failed to create inspection',
      };
    }

    const data: PreTripInspection = await response.json();
    return { data };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to create inspection',
    };
  }
};

export const updateInspection = async (
  id: string,
  inspectionData: UpdateInspectionData
) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/inspections/${id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(inspectionData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return {
        error: errorData.detail || errorData.message || 'Failed to update inspection',
      };
    }

    const data: PreTripInspection = await response.json();
    return { data };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to update inspection',
    };
  }
};

export const submitInspection = async (id: string) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/inspections/${id}/submit/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.error || 'Failed to submit inspection' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to submit inspection',
    };
  }
};

export const approveInspection = async (id: string) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/inspections/${id}/approve/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.error || 'Failed to approve inspection' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to approve inspection',
    };
  }
};

export const rejectInspection = async (id: string, reason: string) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/inspections/${id}/reject/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ rejection_reason: reason }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.error || 'Failed to reject inspection' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to reject inspection',
    };
  }
};

export const downloadInspectionPDF = async (id: string) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return { error: 'No authentication token found' };
    }

    const response = await fetch(`${API_URL}/inspections/${id}/pdf/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      return { error: 'Failed to generate PDF' };
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `inspection-${id}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    return { success: true };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to download PDF',
    };
  }
};
```

### Example: Vehicle Checks API

```typescript
// lib/api/inspections/vehicleChecks.ts

import { API_URL } from '../index';
import type {
  VehicleExteriorCheck,
  EngineFluidCheck,
  InteriorCabinCheck,
  FunctionalCheck,
  SafetyEquipmentCheck,
  CheckStatus,
} from './types';

// Generic function for all vehicle checks
const createCheckAPI = <T>(endpoint: string) => {
  return {
    getAll: async (inspectionId: string) => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          return { error: 'No authentication token found' };
        }

        const response = await fetch(
          `${API_URL}/inspections/${endpoint}/?inspection=${inspectionId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          const errorData = await response.json();
          return { error: errorData.detail || 'Failed to fetch checks' };
        }

        const data: { results: T[] } = await response.json();
        return { data: data.results };
      } catch (error) {
        return {
          error: error instanceof Error ? error.message : 'Failed to fetch checks',
        };
      }
    },

    create: async (checkData: Partial<T>) => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          return { error: 'No authentication token found' };
        }

        const response = await fetch(`${API_URL}/inspections/${endpoint}/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(checkData),
        });

        if (!response.ok) {
          const errorData = await response.json();
          return { error: errorData.detail || 'Failed to create check' };
        }

        const data: T = await response.json();
        return { data };
      } catch (error) {
        return {
          error: error instanceof Error ? error.message : 'Failed to create check',
        };
      }
    },

    update: async (id: string, checkData: Partial<T>) => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          return { error: 'No authentication token found' };
        }

        const response = await fetch(`${API_URL}/inspections/${endpoint}/${id}/`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(checkData),
        });

        if (!response.ok) {
          const errorData = await response.json();
          return { error: errorData.detail || 'Failed to update check' };
        }

        const data: T = await response.json();
        return { data };
      } catch (error) {
        return {
          error: error instanceof Error ? error.message : 'Failed to update check',
        };
      }
    },

    delete: async (id: string) => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          return { error: 'No authentication token found' };
        }

        const response = await fetch(`${API_URL}/inspections/${endpoint}/${id}/`, {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          return { error: 'Failed to delete check' };
        }

        return { success: true };
      } catch (error) {
        return {
          error: error instanceof Error ? error.message : 'Failed to delete check',
        };
      }
    },
  };
};

// Export specific APIs
export const exteriorChecksAPI = createCheckAPI<VehicleExteriorCheck>('exterior-checks');
export const engineChecksAPI = createCheckAPI<EngineFluidCheck>('engine-checks');
export const interiorChecksAPI = createCheckAPI<InteriorCabinCheck>('interior-checks');
export const functionalChecksAPI = createCheckAPI<FunctionalCheck>('functional-checks');
export const safetyChecksAPI = createCheckAPI<SafetyEquipmentCheck>('safety-checks');
```

---

## 🎨 UI/UX Design & Component Structure

### Page Structure

```
frontend/app/dashboard/inspections/
├── page.tsx                              # Main inspections list
├── new/
│   └── page.tsx                          # Create new inspection wizard
├── [id]/
│   ├── page.tsx                          # View/edit inspection (full details)
│   └── pdf/
│       └── page.tsx                      # PDF preview (optional)
└── components/
    ├── InspectionList.tsx                # Table/grid of inspections
    ├── InspectionFilters.tsx             # Filter sidebar
    ├── InspectionStatusBadge.tsx         # Status indicator
    ├── InspectionWizard/
    │   ├── StepIndicator.tsx             # Progress indicator
    │   ├── BasicInfoStep.tsx             # Step 1: Basic info
    │   ├── HealthFitnessStep.tsx         # Step 2: Health check
    │   ├── DocumentationStep.tsx         # Step 3: Documents
    │   ├── VehicleChecksStep.tsx         # Step 4: Vehicle checks (tabs)
    │   ├── ReviewStep.tsx                # Step 5: Review & submit
    │   └── index.tsx                     # Wizard container
    ├── InspectionDetail/
    │   ├── InspectionHeader.tsx          # Header with actions
    │   ├── InspectionSummary.tsx         # Overview cards
    │   ├── HealthFitnessSection.tsx      # Health check display
    │   ├── DocumentationSection.tsx      # Document status display
    │   ├── VehicleChecksSection.tsx      # All vehicle checks (tabs)
    │   ├── BehaviorSection.tsx           # Behavior monitoring
    │   ├── PostTripSection.tsx           # Post-trip report
    │   ├── EnforcementSection.tsx        # Corrective measures/actions
    │   ├── EvaluationSection.tsx         # Evaluation & remarks
    │   ├── SignOffSection.tsx            # Digital signatures
    │   ├── AuditLogSection.tsx           # Audit trail
    │   └── index.tsx                     # Detail container
    ├── ApprovalActions.tsx               # Approve/reject buttons
    └── RejectModal.tsx                   # Rejection reason modal
```

### UI Flow

#### 1. **Inspections List Page** (`/dashboard/inspections`)

**Layout:**
```
┌────────────────────────────────────────────────────────────┐
│ Inspections                                    [+ New]      │
├────────────────────────────────────────────────────────────┤
│ Filters:                                                    │
│ [Status ▼] [Date Range] [Driver ▼] [Vehicle ▼] [Search]   │
├────────────────────────────────────────────────────────────┤
│  ID        | Driver    | Vehicle   | Route    | Status     │
│  INSP-0001 | John Doe  | ALB 9345  | LSK-NDL  | 🟢 Approved│
│  INSP-0002 | Jane Doe  | ALB 1234  | LSK-KIT  | 🟡 Submitted│
│  INSP-0003 | Bob Smith | ALB 5678  | NDL-LSK  | ⚪ Draft   │
├────────────────────────────────────────────────────────────┤
│ Showing 1-25 of 150      [1] [2] [3] ... [6]  [Next >]    │
└────────────────────────────────────────────────────────────┘
```

**Features:**
- **Status badges** with colors (Draft=gray, Submitted=yellow, Approved=green, Rejected=red)
- **Quick actions** on hover (View, Edit if draft, Delete)
- **Role-based filtering** (Supervisors see only their inspections)
- **Bulk actions** (optional: export selected to CSV)

#### 2. **Create Inspection Wizard** (`/dashboard/inspections/new`)

**Multi-Step Form:**

```
Step 1: Basic Information
─────────────────────────
• Driver selection (dropdown)
• Vehicle selection (dropdown)
• Mechanic assignment (optional)
• Inspection date
• Route
• Approved driving hours
• Approved rest stops

Step 2: Health & Fitness Check
───────────────────────────────
• Alcohol test: [Pass/Fail] + remarks
• Temperature: [Pass/Fail] + value (°C)
• Fit for duty: [Yes/No]
• Medication status: [Yes/No] + details
• Health impairment: [Yes/No]
• Fatigue checklist: [Completed/Not] + remarks

Step 3: Documentation Compliance
─────────────────────────────────
Driver Documents:
• License: [Valid/Expired/Missing] + expiry date
• Medical cert: [Valid/Expired/Missing] + expiry date

Vehicle Documents:
• Registration: [Valid/Expired/Missing] + expiry
• Insurance: [Valid/Expired/Missing] + expiry
• Fitness cert: [Valid/Expired/Missing] + expiry
• Road tax: [Valid/Expired/Missing] + expiry

Step 4: Vehicle Checks (Tabbed Interface)
──────────────────────────────────────────
Tabs: [Exterior] [Engine/Fluids] [Interior] [Functional] [Safety]

Each tab contains checkboxes:
Exterior Checks:
☐ Tires [Pass/Fail] Remarks: _______
☐ Lights [Pass/Fail] Remarks: _______
☐ Mirrors [Pass/Fail] Remarks: _______
...

Step 5: Review & Submit
───────────────────────
Summary of all entered data
Validation warnings if any
[Save as Draft] [Submit for Approval]
```

**UX Considerations:**
- **Progress indicator** at top (e.g., 1/5 → 2/5 → ...)
- **Save draft** button available at all steps
- **Validation** on each step before proceeding
- **Previous/Next** navigation
- **Auto-save** every 30 seconds to localStorage (recover if browser crashes)

#### 3. **Inspection Detail/Edit Page** (`/dashboard/inspections/[id]`)

**Layout (Tabbed Sections):**

```
┌────────────────────────────────────────────────────────────┐
│ INSP-0001 | John Doe | ALB 9345        [🟡 Submitted]     │
│ Route: Lusaka → Ndola | Date: 2026-01-23                  │
│ [Approve] [Reject] [Download PDF] [Edit] [Submit]         │
├────────────────────────────────────────────────────────────┤
│ Tabs:                                                       │
│ [Overview] [Health] [Docs] [Vehicle] [Behavior] [Post-Trip]│
│ [Enforcement] [Evaluation] [Sign-Offs] [Audit Log]         │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  (Tab content here based on selection)                     │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

**Tab: Overview**
- Summary cards: Completion %, Risk Score, Critical Failures
- Quick status of all sections (✅ Complete, ⚠️ Incomplete, ❌ Failed)

**Tab: Health**
- Health & Fitness check results (read-only or editable if draft)
- Visual indicators (✅/❌) for each check

**Tab: Docs**
- Document status table with expiry dates
- Color-coded status (green=valid, yellow=expiring soon, red=expired/missing)

**Tab: Vehicle**
- Sub-tabs: Exterior | Engine/Fluids | Interior | Functional | Safety
- Table view of all checks with Pass/Fail status
- Remarks displayed

**Tab: Behavior**
- Trip behavior violations with points
- Driving behavior incidents with severity
- Timeline view (optional)

**Tab: Post-Trip**
- Post-trip report details
- Risk score summary with breakdown chart

**Tab: Enforcement**
- Corrective measures with status
- Enforcement actions with effective dates

**Tab: Evaluation**
- Supervisor remarks
- Performance ratings (visual stars/bars)
- Recommendations

**Tab: Sign-Offs**
- List of signatures with timestamps
- Role badges (Driver, Supervisor, Mechanic, Fleet Manager)

**Tab: Audit Log**
- Chronological list of all changes
- User, action, timestamp
- Diff view for changes (optional)

---

## 📝 Step-by-Step Implementation Plan

### Phase 1: Foundation (Week 1)

#### Step 1.1: API Layer Setup
**Time: 2-3 days**

1. Create TypeScript interfaces (`lib/api/inspections/types.ts`)
   - All models from backend
   - Enums for status, check types, etc.
   - Request/response types

2. Implement main inspections API (`lib/api/inspections/index.ts`)
   - CRUD operations
   - Workflow actions (submit, approve, reject)
   - PDF download

3. Create sub-module APIs
   - Health fitness API
   - Documentation API
   - Vehicle checks API (reusable pattern)
   - Behavior API
   - Post-trip API
   - Enforcement API
   - Evaluation API
   - Sign-off API

4. Add error handling and type safety
   - Consistent error format
   - TypeScript strict mode
   - API response validation

**Testing:**
- Test all API endpoints with Postman
- Verify authentication headers
- Check error responses

#### Step 1.2: Basic Components
**Time: 1-2 days**

1. Create reusable components:
   - `InspectionStatusBadge.tsx` - Status indicator with colors
   - `CheckItemRow.tsx` - Row for vehicle checks
   - `DocumentStatusCard.tsx` - Document status display
   - `ProgressIndicator.tsx` - Multi-step wizard progress
   - `ValidationAlert.tsx` - Form validation messages

2. Create utility functions:
   - Date formatting helpers
   - Status color mapping
   - Validation helpers
   - Form data transformers

### Phase 2: Inspections List (Week 1)

#### Step 2.1: List Page
**Time: 2-3 days**

1. Create main page (`app/dashboard/inspections/page.tsx`)
   - Fetch and display inspections
   - Implement pagination
   - Add loading states
   - Error handling

2. Implement filtering (`components/InspectionFilters.tsx`)
   - Status filter dropdown
   - Date range picker
   - Driver/Vehicle selectors
   - Search input
   - Clear filters button

3. Create table view (`components/InspectionList.tsx`)
   - Sortable columns
   - Row actions (View, Edit, Delete)
   - Empty state
   - Skeleton loaders

4. Add role-based features
   - Transport Supervisor: only their inspections
   - Fleet Manager: all inspections + approval actions
   - Conditional rendering of actions

**Testing:**
- Test with different user roles
- Verify filtering works correctly
- Check pagination
- Test search functionality

### Phase 3: Create Inspection Wizard (Week 2)

#### Step 3.1: Wizard Container
**Time: 1 day**

1. Create wizard component (`components/InspectionWizard/index.tsx`)
   - Step management state
   - Navigation (Previous/Next)
   - Save draft functionality
   - Form context provider

2. Implement progress indicator (`components/InspectionWizard/StepIndicator.tsx`)
   - Visual step indicator (1 → 2 → 3 → ...)
   - Click to navigate to completed steps
   - Validation status per step

#### Step 3.2: Form Steps
**Time: 3-4 days**

1. **Basic Info Step** (`BasicInfoStep.tsx`)
   - Driver dropdown (fetch active drivers)
   - Vehicle dropdown (fetch active vehicles)
   - Mechanic dropdown (optional)
   - Date picker
   - Route input
   - Driving hours/rest stops
   - Validation

2. **Health & Fitness Step** (`HealthFitnessStep.tsx`)
   - Alcohol test radio buttons + remarks
   - Temperature radio + value input
   - Checkboxes for fitness flags
   - Fatigue checklist toggle + remarks
   - Real-time validation

3. **Documentation Step** (`DocumentationStep.tsx`)
   - Driver document status selectors
   - Vehicle document status selectors
   - Date pickers for expiry dates
   - Visual status indicators
   - Expiry warnings

4. **Vehicle Checks Step** (`VehicleChecksStep.tsx`)
   - Tabbed interface (5 tabs)
   - Dynamic check items per tab
   - Pass/Fail toggles
   - Remarks inputs
   - Critical failure warnings

5. **Review Step** (`ReviewStep.tsx`)
   - Summary of all entered data
   - Validation summary
   - Edit buttons per section
   - Submit/Save draft buttons

#### Step 3.3: Form Submission
**Time: 1 day**

1. Implement save draft
   - Save to API with status='draft'
   - Show success message
   - Redirect to detail page

2. Implement submit for approval
   - Validate all required fields
   - Save inspection
   - Call submit endpoint
   - Show success/error message
   - Redirect to detail page

**Testing:**
- Test each step independently
- Test navigation (forward/back)
- Test validation
- Test save draft at each step
- Test submit workflow
- Test with missing required fields

### Phase 4: Detail/Edit Page (Week 3)

#### Step 4.1: Detail Page Layout
**Time: 2 days**

1. Create detail page (`app/dashboard/inspections/[id]/page.tsx`)
   - Fetch full inspection data
   - Loading states
   - Error handling (404, permission denied)

2. Implement header (`components/InspectionDetail/InspectionHeader.tsx`)
   - Inspection ID, driver, vehicle
   - Status badge
   - Action buttons (Edit, Submit, Approve, Reject, PDF)
   - Role-based button visibility

3. Create tab navigation
   - Tab state management
   - Responsive tabs (collapse to dropdown on mobile)
   - Active tab indicator

#### Step 4.2: Detail Tab Components
**Time: 3-4 days**

1. **Overview Tab** (`InspectionSummary.tsx`)
   - Summary cards (completion %, risk score, critical failures)
   - Quick status indicators per section
   - Workflow timeline

2. **Health Tab** (`HealthFitnessSection.tsx`)
   - Display health check data
   - Visual pass/fail indicators
   - Edit mode if draft/rejected

3. **Documentation Tab** (`DocumentationSection.tsx`)
   - Document status table
   - Expiry date warnings
   - Edit mode if draft/rejected

4. **Vehicle Checks Tab** (`VehicleChecksSection.tsx`)
   - Sub-tabs for each check type
   - Table view of checks
   - Add/edit/delete checks
   - Critical failure highlights

5. **Behavior Tab** (`BehaviorSection.tsx`)
   - Trip behaviors table
   - Driving behaviors table
   - Violation points summary
   - Add/edit/delete behaviors

6. **Post-Trip Tab** (`PostTripSection.tsx`)
   - Post-trip report form/display
   - Risk score summary
   - Score breakdown chart (optional)
   - Add/edit post-trip data

7. **Enforcement Tab** (`EnforcementSection.tsx`)
   - Corrective measures list
   - Enforcement actions list
   - Add/edit/delete items
   - Status tracking

8. **Evaluation Tab** (`EvaluationSection.tsx`)
   - Supervisor remarks
   - Evaluation summary
   - Performance ratings
   - Add/edit evaluations

9. **Sign-Offs Tab** (`SignOffSection.tsx`)
   - Signature list
   - Add signature button (if user's role hasn't signed)
   - Signature confirmation modal

10. **Audit Log Tab** (`AuditLogSection.tsx`)
    - Chronological log
    - User, action, timestamp
    - Filter by action type

#### Step 4.3: Approval Workflow
**Time: 1 day**

1. Implement approve action (`ApprovalActions.tsx`)
   - Approve button (Fleet Manager only)
   - Confirmation modal
   - Success/error handling
   - Refresh data after approval

2. Implement reject action (`RejectModal.tsx`)
   - Reject button (Fleet Manager only)
   - Modal with rejection reason input
   - Submit rejection
   - Refresh data

3. Implement submit action
   - Submit button (Transport Supervisor, draft/rejected only)
   - Confirmation modal
   - Submit to API
   - Update status

**Testing:**
- Test detail view for all statuses
- Test editing in draft mode
- Test submit workflow
- Test approve/reject (with Fleet Manager role)
- Test PDF download
- Test role-based visibility
- Test all tabs load correctly

### Phase 5: Advanced Features (Week 4)

#### Step 5.1: Real-Time Validation
**Time: 1 day**

1. Add validation rules
   - Required fields
   - Date validations (not in future, expiry dates)
   - Numeric validations (temperature, scores)
   - Critical failure checks

2. Implement inline validation
   - Show errors below fields
   - Disable submit if invalid
   - Highlight invalid sections

#### Step 5.2: Auto-Save & Recovery
**Time: 1 day**

1. Implement auto-save
   - Save draft every 30 seconds
   - Show "Saving..." indicator
   - Handle conflicts (if edited elsewhere)

2. Implement recovery
   - Store form state in localStorage
   - Detect unfinished forms on page load
   - Prompt user to recover or discard

#### Step 5.3: PDF Integration
**Time: 1 day**

1. Implement PDF download
   - Call PDF endpoint
   - Handle blob response
   - Download file with proper name
   - Show download progress (optional)

2. Add PDF preview (optional)
   - Display PDF in iframe or viewer
   - Print functionality

#### Step 5.4: Notifications & Alerts
**Time: 1 day**

1. Add toast notifications
   - Success messages (saved, submitted, approved)
   - Error messages
   - Warning messages (expiring documents)

2. Implement dashboard alerts
   - Pending approvals count (for Fleet Manager)
   - Rejected inspections (for Supervisor)
   - Expiring documents

#### Step 5.5: Search & Analytics (Optional)
**Time: 2 days**

1. Implement advanced search
   - Full-text search across all fields
   - Filter by date ranges
   - Filter by risk level
   - Filter by completion status

2. Add analytics dashboard (optional)
   - Inspection stats (total, approved, rejected)
   - Driver performance metrics
   - Vehicle condition trends
   - Risk score trends
   - Charts/graphs

### Phase 6: Testing & Refinement (Week 5)

#### Step 6.1: Integration Testing
**Time: 2-3 days**

1. End-to-end testing
   - Complete workflow (create → submit → approve)
   - Test with different roles
   - Test error scenarios
   - Test edge cases

2. Cross-browser testing
   - Chrome, Firefox, Safari, Edge
   - Mobile browsers

3. Responsive design testing
   - Desktop (1920x1080, 1366x768)
   - Tablet (iPad, Android tablets)
   - Mobile (iPhone, Android phones)

#### Step 6.2: Performance Optimization
**Time: 1-2 days**

1. Code splitting
   - Lazy load tabs
   - Lazy load sub-modules

2. Data optimization
   - Implement caching (React Query or SWR)
   - Paginate large lists
   - Optimize re-renders

3. Bundle size optimization
   - Remove unused dependencies
   - Tree-shaking
   - Minification

#### Step 6.3: Bug Fixes & Polish
**Time: 1-2 days**

1. Fix bugs found in testing
2. Improve error messages
3. Add loading skeletons
4. Improve accessibility (ARIA labels, keyboard navigation)
5. Code cleanup and documentation

---

## 🚀 Advanced Features (Optional)

### 1. Real-Time Collaboration
- **WebSocket integration** for live updates
- Show when another user is editing same inspection
- Lock editing to prevent conflicts

### 2. Mobile App Features
- **Offline mode** - save inspections offline, sync later
- **Camera integration** - attach photos to checks
- **GPS tracking** - auto-fill location data
- **Voice input** - dictate remarks

### 3. Analytics & Reporting
- **Dashboard widgets** - key metrics at a glance
- **Trend analysis** - risk scores over time
- **Driver leaderboard** - top performers
- **Vehicle health report** - maintenance predictions

### 4. AI/ML Features
- **Predictive risk scoring** - ML model predicts risk
- **Smart validation** - AI flags suspicious data
- **Automated remarks** - AI suggests remarks based on checks

### 5. Integration Features
- **Email notifications** - notify on status changes
- **Calendar integration** - schedule inspections
- **Third-party integrations** - telematics, GPS, fuel cards

---

## 🧪 Testing Strategy

### Unit Tests
- Test API functions
- Test utility functions
- Test form validations

### Component Tests
- Test individual components
- Test form inputs
- Test button actions

### Integration Tests
- Test complete workflows
- Test API interactions
- Test state management

### E2E Tests (Cypress/Playwright)
```typescript
// Example E2E test
describe('Inspection Workflow', () => {
  it('should create, submit, and approve inspection', () => {
    // Login as Transport Supervisor
    cy.login('supervisor@example.com', 'password');
    
    // Navigate to create inspection
    cy.visit('/dashboard/inspections/new');
    
    // Fill basic info
    cy.selectDriver('John Doe');
    cy.selectVehicle('ALB 9345');
    cy.fillRoute('Lusaka - Ndola');
    
    // Complete health check
    cy.get('[name="alcohol_test_status"]').check('pass');
    cy.get('[name="temperature_check_status"]').check('pass');
    
    // ... complete all steps
    
    // Submit
    cy.clickButton('Submit for Approval');
    cy.contains('Inspection submitted successfully');
    
    // Logout and login as Fleet Manager
    cy.logout();
    cy.login('manager@example.com', 'password');
    
    // Approve inspection
    cy.visit('/dashboard/inspections');
    cy.contains('INSP-').click();
    cy.clickButton('Approve');
    cy.contains('Inspection approved successfully');
  });
});
```

### Accessibility Tests
- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader compatibility

### Performance Tests
- Lighthouse scores (>90)
- Bundle size (<500KB)
- Load time (<2s)

---

## 📚 Additional Resources

### Design Patterns
- **Form State Management**: React Hook Form or Formik
- **Data Fetching**: React Query or SWR (for caching, refetching)
- **State Management**: Context API or Zustand (lightweight)
- **Styling**: Tailwind CSS or CSS Modules

### Libraries to Consider
- `react-hook-form` - Form management
- `yup` or `zod` - Schema validation
- `react-query` - Data fetching & caching
- `date-fns` - Date manipulation
- `recharts` - Charts for analytics
- `react-pdf` - PDF viewer
- `react-table` - Advanced tables

### Backend Reference Files
- Models: `backend/inspections/models/*.py`
- Serializers: `backend/inspections/serializers/*.py`
- Views: `backend/inspections/views/*.py`
- Filters: `backend/inspections/filters.py`

---

## 📋 Checklist for Implementation

### Pre-Development
- [ ] Review backend API endpoints
- [ ] Understand data models and relationships
- [ ] Design mockups/wireframes
- [ ] Setup project structure

### Development
- [ ] Create TypeScript interfaces (all models)
- [ ] Implement API layer (all endpoints)
- [ ] Build reusable components
- [ ] Create inspections list page
- [ ] Build create inspection wizard
- [ ] Implement detail/edit page
- [ ] Add approval workflow
- [ ] Implement all sub-modules

### Testing
- [ ] Unit tests for API functions
- [ ] Component tests
- [ ] Integration tests
- [ ] E2E tests for critical workflows
- [ ] Cross-browser testing
- [ ] Mobile responsive testing

### Polish
- [ ] Error handling everywhere
- [ ] Loading states
- [ ] Empty states
- [ ] Success/error messages
- [ ] Accessibility audit
- [ ] Performance optimization
- [ ] Code documentation

### Deployment
- [ ] Environment variables configured
- [ ] Build production bundle
- [ ] Test in staging environment
- [ ] Deploy to production
- [ ] Monitor for errors

---

## 🎓 Summary

The Inspection Module is **the most complex module** in the fleet management system due to:
- 12+ related sub-modules
- Multi-step workflow with approvals
- Extensive form handling
- Role-based permissions
- Real-time validation requirements

**Estimated Timeline: 4-5 weeks** for complete implementation with testing.

**Recommended Approach:**
1. Start with list view (simple)
2. Build create wizard (complex but isolated)
3. Implement detail view (most complex, many tabs)
4. Add approval workflow (critical path)
5. Polish and test thoroughly

**Key Success Factors:**
- ✅ Strong TypeScript typing from the start
- ✅ Reusable components for repetitive patterns
- ✅ Consistent error handling
- ✅ Role-based testing with multiple accounts
- ✅ Regular backend sync (verify API matches expectations)

Good luck with the implementation! 🚀
