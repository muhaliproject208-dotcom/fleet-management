'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useParams, useSearchParams } from 'next/navigation';
import { isAuthenticated } from '@/lib/api/auth';
import ProgressTracker from '../../components/ProgressTracker';
import { RadioOption } from '../../components/FormComponents';

interface PostTripFormData {
  // Form 10: Trip Behavior Monitoring
  behaviors: Array<{
    behavior: string;
    status: 'compliant' | 'violation' | 'none' | null;
    notes: string;
    points: number;
  }>;
  
  // Form 11: Driving Behavior Check
  driving_behaviors: Array<{
    behavior: string;
    status: boolean | null;
    remarks: string;
  }>;
  
  // Form 12: Post-Trip Report
  vehicle_fault_submitted: boolean | null;
  fault_notes: string;
  final_inspection_signed: boolean | null;
  compliance_with_policy: boolean | null;
  attitude_cooperation: boolean | null;
  incidents_recorded: boolean | null;
  incident_notes: string;
  total_trip_duration: string;
  
  // Form 13: Risk Score (auto-calculated)
  // Form 14: Corrective Measures
  corrective_measures: Array<{
    measure_type: string;
    required: boolean;
    due_date: string;
    completed: boolean;
    completed_date: string;
    notes: string;
  }>;
  
  // Form 15: Enforcement Actions
  enforcement_actions: Array<{
    action_type: string;
    is_applied: boolean;
    start_date: string;
    end_date: string;
    notes: string;
  }>;
  
  // Form 16: Supervisor Remarks
  supervisor_remarks: string;
  recommendation: string;
  
  // Form 17: Evaluation Summary
  pre_trip_inspection_score: number | null;
  driving_conduct_score: number | null;
  incident_management_score: number | null;
  post_trip_reporting_score: number | null;
  compliance_documentation_score: number | null;
  comments: string;
  
  // Form 18: Driver Sign-Off
  driver_signature: string;
}

const TOTAL_STEPS = 9;

// Map display labels to backend valid keys
const BEHAVIOR_KEY_MAP: Record<string, string> = {
  'Speed in School Zones (≤40 km/hr)': 'speed_school_zone',
  'Speed in Market Areas (≤40 km/hr)': 'speed_market_area',
  'Max Speed on Open Road': 'max_speed_open_road',
  'Railway Crossing Stop': 'railway_crossing',
  'Toll Gate Stop': 'toll_gate',
  'Hazardous Zone Speeding': 'hazardous_zone_speed',
  'Excessive Continuous Driving (>4 hrs)': 'excessive_driving',
  'Traffic Infractions (RTSA/Police)': 'traffic_infractions',
  'Incidents/Accidents': 'incidents',
  'Takes Scheduled Breaks (every 2 hours)': 'scheduled_breaks',
  'Reports Fatigue/Sleepiness Immediately': 'fatigue_reporting',
  'Uses Rest Stops and Designated Parking Areas': 'rest_stops_usage',
};

const DRIVING_BEHAVIOR_KEY_MAP: Record<string, string> = {
  'Obeys All Traffic Rules and Road Signs': 'obeys_traffic_rules',
  'Maintains Safe Speed and Following Distance': 'safe_speed_distance',
  'Avoids Harsh Acceleration, Braking, Cornering': 'avoids_harsh_maneuvers',
  'Avoids Phone Use/Distraction While Driving': 'no_phone_use',
  'Keeps Headlights On During Poor Visibility': 'headlights_visibility',
  'Checks Load Security at Rest Stops': 'load_security',
  'Reports Abnormal Sounds, Vibrations, Smoke': 'abnormal_sounds_reporting',
  'Avoids Overloading or Unauthorized Passengers': 'no_overloading',
  'Reports Breakdowns or Near Misses Promptly': 'breakdown_reporting',
  'Follows Emergency Procedures for Crashes/Hazards': 'emergency_procedures',
  'Contacts Control Centre for Route Diversion/Delays': 'contact_control_center',
};

const VIOLATION_POINTS: Record<string, number> = {
  'Speed in School Zones (≤40 km/hr)': 5,
  'Speed in Market Areas (≤40 km/hr)': 5,
  'Max Speed on Open Road': 3,
  'Railway Crossing Stop': 10,
  'Toll Gate Stop': 2,
  'Hazardous Zone Speeding': 10,
  'Excessive Continuous Driving (>4 hrs)': 8,
  'Traffic Infractions (RTSA/Police)': 10,
  'Incidents/Accidents': 15,
  'Takes Scheduled Breaks (every 2 hours)': 3,
  'Reports Fatigue/Sleepiness Immediately': 5,
  'Uses Rest Stops and Designated Parking Areas': 2,
};

function PostTripWizardContent() {
  const router = useRouter();
  const params = useParams();
  const searchParams = useSearchParams();
  const inspectionId = params.id as string;
  const stepFromUrl = searchParams.get('step');
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [navigating, setNavigating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [completionInfo, setCompletionInfo] = useState<{ 
    completed_steps: number[], 
    next_step: number | null,
    completion_percentage: number,
    total_steps: number,
    is_complete: boolean 
  } | null>(null);
  
  const [formData, setFormData] = useState<PostTripFormData>({
    behaviors: Object.keys(VIOLATION_POINTS).map(behavior => ({
      behavior,
      status: null,
      notes: '',
      points: VIOLATION_POINTS[behavior],
    })),
    
    driving_behaviors: [
      { behavior: 'Obeys All Traffic Rules and Road Signs', status: null, remarks: '' },
      { behavior: 'Maintains Safe Speed and Following Distance', status: null, remarks: '' },
      { behavior: 'Avoids Harsh Acceleration, Braking, Cornering', status: null, remarks: '' },
      { behavior: 'Avoids Phone Use/Distraction While Driving', status: null, remarks: '' },
      { behavior: 'Keeps Headlights On During Poor Visibility', status: null, remarks: '' },
      { behavior: 'Checks Load Security at Rest Stops', status: null, remarks: '' },
      { behavior: 'Reports Abnormal Sounds, Vibrations, Smoke', status: null, remarks: '' },
      { behavior: 'Avoids Overloading or Unauthorized Passengers', status: null, remarks: '' },
      { behavior: 'Reports Breakdowns or Near Misses Promptly', status: null, remarks: '' },
      { behavior: 'Follows Emergency Procedures for Crashes/Hazards', status: null, remarks: '' },
      { behavior: 'Contacts Control Centre for Route Diversion/Delays', status: null, remarks: '' },
    ],
    
    vehicle_fault_submitted: null,
    fault_notes: '',
    final_inspection_signed: null,
    compliance_with_policy: null,
    attitude_cooperation: null,
    incidents_recorded: null,
    incident_notes: '',
    total_trip_duration: '',
    
    corrective_measures: [],
    enforcement_actions: [],
    
    supervisor_remarks: '',
    recommendation: '',
    
    pre_trip_inspection_score: null,
    driving_conduct_score: null,
    incident_management_score: null,
    post_trip_reporting_score: null,
    compliance_documentation_score: null,
    comments: '',
    
    driver_signature: '',
  });

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }
    
    // Fetch inspection to get completion info and existing data
    const fetchInspectionData = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('access_token');
        const headers = { 'Authorization': `Bearer ${token}` };
        
        // Start post-trip (this also returns completion info)
        const startResponse = await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/start_post_trip/`, {
          method: 'POST',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
        
        let completionData = null;
        if (startResponse.ok) {
          const data = await startResponse.json();
          console.log('Post-trip started:', data);
          completionData = data.post_trip_completion_info;
        }
        
        // Set completion info
        if (completionData) {
          setCompletionInfo(completionData);
          
          // Determine which step to show
          if (stepFromUrl) {
            setCurrentStep(parseInt(stepFromUrl));
          } else {
            const completedSteps = completionData.completed_steps || [];
            if (completedSteps.length > 0) {
              const highestCompleted = Math.max(...completedSteps);
              const nextAfterHighest = highestCompleted + 1;
              setCurrentStep(nextAfterHighest <= 9 ? nextAfterHighest : 9);
            } else {
              setCurrentStep(1);
            }
          }
        } else if (stepFromUrl) {
          setCurrentStep(parseInt(stepFromUrl));
        }
        
        // Helper to extract array from API response (handles both array and paginated responses)
        const getArrayFromResponse = (data: unknown): unknown[] => {
          if (Array.isArray(data)) return data;
          if (data && typeof data === 'object' && 'results' in data) {
            return (data as { results: unknown[] }).results || [];
          }
          return [];
        };
        
        // Fetch existing post-trip data to pre-populate form
        // Fetch trip behaviors (Step 1)
        const tripBehaviorsRes = await fetch(
          `http://localhost:8000/api/v1/inspections/${inspectionId}/trip-behaviors/`,
          { headers }
        );
        if (tripBehaviorsRes.ok) {
          const tripBehaviorsData = await tripBehaviorsRes.json();
          const tripBehaviors = getArrayFromResponse(tripBehaviorsData);
          if (tripBehaviors.length > 0) {
            setFormData(prev => {
              const updatedBehaviors = prev.behaviors.map(b => {
                const backendKey = BEHAVIOR_KEY_MAP[b.behavior];
                const existing = tripBehaviors.find((tb) => (tb as { behavior_item: string }).behavior_item === backendKey) as { behavior_item: string; status: string; notes: string } | undefined;
                if (existing) {
                  return {
                    ...b,
                    status: existing.status as 'compliant' | 'violation' | 'none' | null,
                    notes: existing.notes || '',
                  };
                }
                return b;
              });
              return { ...prev, behaviors: updatedBehaviors };
            });
          }
        }
        
        // Fetch driving behaviors (Step 2)
        const drivingBehaviorsRes = await fetch(
          `http://localhost:8000/api/v1/inspections/${inspectionId}/driving-behaviors/`,
          { headers }
        );
        if (drivingBehaviorsRes.ok) {
          const drivingBehaviorsData = await drivingBehaviorsRes.json();
          const drivingBehaviors = getArrayFromResponse(drivingBehaviorsData);
          if (drivingBehaviors.length > 0) {
            setFormData(prev => {
              const updatedDrivingBehaviors = prev.driving_behaviors.map(db => {
                const backendKey = DRIVING_BEHAVIOR_KEY_MAP[db.behavior];
                const existing = drivingBehaviors.find((dbe) => (dbe as { behavior_item: string }).behavior_item === backendKey) as { behavior_item: string; status: boolean; remarks: string } | undefined;
                if (existing) {
                  return {
                    ...db,
                    status: existing.status,
                    remarks: existing.remarks || '',
                  };
                }
                return db;
              });
              return { ...prev, driving_behaviors: updatedDrivingBehaviors };
            });
          }
        }
        
        // Fetch post-trip report (Step 3)
        const postTripRes = await fetch(
          `http://localhost:8000/api/v1/inspections/${inspectionId}/post-trip/`,
          { headers }
        );
        if (postTripRes.ok) {
          const postTripRaw = await postTripRes.json();
          const postTripData = getArrayFromResponse(postTripRaw);
          if (postTripData.length > 0) {
            const report = postTripData[0] as {
              vehicle_fault_submitted: boolean;
              fault_notes: string;
              final_inspection_signed: boolean;
              compliance_with_policy: boolean;
              attitude_cooperation: boolean;
              incidents_recorded: boolean;
              incident_notes: string;
              total_trip_duration: string;
            };
            setFormData(prev => ({
              ...prev,
              vehicle_fault_submitted: report.vehicle_fault_submitted,
              fault_notes: report.fault_notes || '',
              final_inspection_signed: report.final_inspection_signed,
              compliance_with_policy: report.compliance_with_policy,
              attitude_cooperation: report.attitude_cooperation,
              incidents_recorded: report.incidents_recorded,
              incident_notes: report.incident_notes || '',
              total_trip_duration: report.total_trip_duration || '',
            }));
          }
        }
        
        // Fetch corrective measures (Step 5)
        const correctiveRes = await fetch(
          `http://localhost:8000/api/v1/inspections/${inspectionId}/corrective-measures/`,
          { headers }
        );
        if (correctiveRes.ok) {
          const correctiveRaw = await correctiveRes.json();
          const correctiveMeasures = getArrayFromResponse(correctiveRaw);
          if (correctiveMeasures.length > 0) {
            const mappedMeasures = correctiveMeasures.map((cm) => {
              const measure = cm as {
                measure_type: string;
                required: boolean;
                due_date: string;
                completed: boolean;
                completed_date: string | null;
                notes: string;
              };
              return {
                measure_type: measure.measure_type,
                required: measure.required,
                due_date: measure.due_date || '',
                completed: measure.completed,
                completed_date: measure.completed_date || '',
                notes: measure.notes || '',
              };
            });
            setFormData(prev => ({ ...prev, corrective_measures: mappedMeasures }));
          }
        }
        
        // Fetch enforcement actions (Step 6)
        const enforcementRes = await fetch(
          `http://localhost:8000/api/v1/inspections/${inspectionId}/enforcement-actions/`,
          { headers }
        );
        if (enforcementRes.ok) {
          const enforcementRaw = await enforcementRes.json();
          const enforcementActions = getArrayFromResponse(enforcementRaw);
          if (enforcementActions.length > 0) {
            const mappedActions = enforcementActions.map((ea) => {
              const action = ea as {
                action_type: string;
                is_applied: boolean;
                start_date: string;
                end_date: string | null;
                notes: string;
              };
              return {
                action_type: action.action_type,
                is_applied: action.is_applied,
                start_date: action.start_date || '',
                end_date: action.end_date || '',
                notes: action.notes || '',
              };
            });
            setFormData(prev => ({ ...prev, enforcement_actions: mappedActions }));
          }
        }
        
        // Fetch supervisor remarks (Step 7)
        const remarksRes = await fetch(
          `http://localhost:8000/api/v1/inspections/${inspectionId}/supervisor-remarks/`,
          { headers }
        );
        if (remarksRes.ok) {
          const remarksRaw = await remarksRes.json();
          const remarksData = getArrayFromResponse(remarksRaw);
          if (remarksData.length > 0) {
            const remarks = remarksData[0] as {
              remarks: string;
              recommendation: string;
            };
            setFormData(prev => ({
              ...prev,
              supervisor_remarks: remarks.remarks || '',
              recommendation: remarks.recommendation || '',
            }));
          }
        }
        
        // Fetch evaluation summary (Step 8)
        const evalRes = await fetch(
          `http://localhost:8000/api/v1/inspections/${inspectionId}/evaluation/`,
          { headers }
        );
        if (evalRes.ok) {
          const evalRaw = await evalRes.json();
          const evalData = getArrayFromResponse(evalRaw);
          if (evalData.length > 0) {
            const evaluation = evalData[0] as {
              pre_trip_inspection_score: number;
              driving_conduct_score: number;
              incident_management_score: number;
              post_trip_reporting_score: number;
              compliance_documentation_score: number;
              comments: string;
            };
            setFormData(prev => ({
              ...prev,
              pre_trip_inspection_score: evaluation.pre_trip_inspection_score,
              driving_conduct_score: evaluation.driving_conduct_score,
              incident_management_score: evaluation.incident_management_score,
              post_trip_reporting_score: evaluation.post_trip_reporting_score,
              compliance_documentation_score: evaluation.compliance_documentation_score,
              comments: evaluation.comments || '',
            }));
          }
        }
        
        // Fetch sign-offs (Step 9)
        const signOffsRes = await fetch(
          `http://localhost:8000/api/v1/inspections/${inspectionId}/sign-offs/`,
          { headers }
        );
        if (signOffsRes.ok) {
          const signOffsRaw = await signOffsRes.json();
          const signOffs = getArrayFromResponse(signOffsRaw);
          const driverSignOff = signOffs.find((so) => (so as { role: string }).role === 'driver') as { role: string; signer_name: string } | undefined;
          if (driverSignOff) {
            setFormData(prev => ({
              ...prev,
              driver_signature: driverSignOff.signer_name || '',
            }));
          }
        }
        
      } catch (err) {
        console.error('Failed to fetch inspection:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchInspectionData();
  }, [router, inspectionId, stepFromUrl]);

  const calculateRiskScore = () => {
    const totalPoints = formData.behaviors
      .filter(b => b.status === 'violation')
      .reduce((sum, b) => sum + b.points, 0);
    
    let riskLevel = 'Low';
    let color = '#666';
    
    if (totalPoints >= 10) {
      riskLevel = 'High';
      color = '#000';
    } else if (totalPoints >= 4) {
      riskLevel = 'Medium';
      color = '#333';
    }
    
    return { totalPoints, riskLevel, color };
  };

  const calculateOverallScore = () => {
    const scores = [
      formData.pre_trip_inspection_score,
      formData.driving_conduct_score,
      formData.incident_management_score,
      formData.post_trip_reporting_score,
      formData.compliance_documentation_score,
    ].filter(s => s !== null) as number[];
    
    if (scores.length === 0) return { average: 0, rating: 'N/A', color: '#999' };
    
    const average = scores.reduce((a, b) => a + b, 0) / scores.length;
    let rating = 'Non-Compliant';
    let color = '#000';
    
    if (average >= 4.5) {
      rating = 'Excellent';
      color = '#000';
    } else if (average >= 3.5) {
      rating = 'Satisfactory';
      color = '#333';
    } else if (average >= 2.0) {
      rating = 'Needs Improvement';
      color = '#666';
    }
    
    return { average: average.toFixed(2), rating, color };
  };

  const validateStep = (step: number): boolean => {
    setError('');
    
    switch (step) {
      case 1:
        if (!formData.behaviors.every(b => b.status !== null)) {
          setError('Please complete all behavior monitoring items');
          return false;
        }
        break;
      case 2:
        if (!formData.driving_behaviors.every(b => b.status !== null)) {
          setError('Please complete all driving behavior checks');
          return false;
        }
        break;
      case 3:
        if (formData.vehicle_fault_submitted === null || formData.final_inspection_signed === null ||
            formData.compliance_with_policy === null || formData.attitude_cooperation === null ||
            formData.incidents_recorded === null || !formData.total_trip_duration.trim()) {
          setError('Please complete all post-trip report fields');
          return false;
        }
        break;
      case 7:
        if (!formData.supervisor_remarks.trim()) {
          setError('Supervisor remarks are required');
          return false;
        }
        break;
      case 8:
        if (formData.pre_trip_inspection_score === null || formData.driving_conduct_score === null ||
            formData.incident_management_score === null || formData.post_trip_reporting_score === null ||
            formData.compliance_documentation_score === null) {
          setError('Please complete all evaluation scores');
          return false;
        }
        break;
      case 9:
        if (!formData.driver_signature.trim()) {
          setError('Driver signature is required');
          return false;
        }
        break;
    }
    
    return true;
  };

  // Save current step data to backend (uses upsert - creates or updates)
  const saveCurrentStep = async (): Promise<boolean> => {
    setSaving(true);
    setError('');
    
    try {
      const token = localStorage.getItem('access_token');
      const headers = { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      };

      switch (currentStep) {
        case 1:
          // Save trip behaviors (upsert)
          for (const behavior of formData.behaviors) {
            const backendKey = BEHAVIOR_KEY_MAP[behavior.behavior];
            if (!backendKey) {
              console.error('Unknown behavior:', behavior.behavior);
              continue;
            }
            const response = await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/trip-behaviors/`, {
              method: 'POST',
              headers,
              body: JSON.stringify({
                behavior_item: backendKey,
                status: behavior.status,
                notes: behavior.notes,
                violation_points: behavior.status === 'violation' ? behavior.points : 0,
              }),
            });
            if (!response.ok) {
              const errorData = await response.json();
              throw new Error(errorData.detail || `Failed to save trip behavior: ${behavior.behavior}`);
            }
          }
          break;

        case 2:
          // Save driving behaviors
          for (const behavior of formData.driving_behaviors) {
            const backendKey = DRIVING_BEHAVIOR_KEY_MAP[behavior.behavior];
            if (!backendKey) {
              console.error('Unknown driving behavior:', behavior.behavior);
              continue;
            }
            const response = await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/driving-behaviors/`, {
              method: 'POST',
              headers,
              body: JSON.stringify({
                behavior_item: backendKey,
                status: behavior.status,
                remarks: behavior.remarks,
              }),
            });
            if (!response.ok) {
              const errorData = await response.json();
              throw new Error(errorData.detail || `Failed to save driving behavior: ${behavior.behavior}`);
            }
          }
          break;

        case 3:
          // Save post-trip report
          const postTripResponse = await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/post-trip/`, {
            method: 'POST',
            headers,
            body: JSON.stringify({
              vehicle_fault_submitted: formData.vehicle_fault_submitted,
              fault_notes: formData.fault_notes,
              final_inspection_signed: formData.final_inspection_signed,
              compliance_with_policy: formData.compliance_with_policy,
              attitude_cooperation: formData.attitude_cooperation,
              incidents_recorded: formData.incidents_recorded,
              incident_notes: formData.incident_notes,
              total_trip_duration: formData.total_trip_duration,
            }),
          });
          if (!postTripResponse.ok) {
            const errorData = await postTripResponse.json();
            throw new Error(errorData.detail || 'Failed to save post-trip report');
          }
          break;

        case 4:
          // Save Risk Score Summary - the backend auto-calculates from trip behaviors
          const riskScoreResponse = await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/risk-score/`, {
            method: 'POST',
            headers,
            body: JSON.stringify({}),  // Empty body - backend auto-calculates
          });
          if (!riskScoreResponse.ok) {
            const errorData = await riskScoreResponse.json();
            throw new Error(errorData.detail || 'Failed to save risk score');
          }
          break;

        case 5:
          // Save corrective measures
          for (const measure of formData.corrective_measures) {
            const response = await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/corrective-measures/`, {
              method: 'POST',
              headers,
              body: JSON.stringify(measure),
            });
            if (!response.ok) {
              const errorData = await response.json();
              throw new Error(errorData.detail || 'Failed to save corrective measure');
            }
          }
          break;

        case 6:
          // Save enforcement actions
          for (const action of formData.enforcement_actions) {
            const response = await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/enforcement-actions/`, {
              method: 'POST',
              headers,
              body: JSON.stringify(action),
            });
            if (!response.ok) {
              const errorData = await response.json();
              throw new Error(errorData.detail || 'Failed to save enforcement action');
            }
          }
          break;

        case 7:
          // Save supervisor remarks
          const remarksResponse = await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/supervisor-remarks/`, {
            method: 'POST',
            headers,
            body: JSON.stringify({
              remarks: formData.supervisor_remarks,
              recommendation: formData.recommendation,
            }),
          });
          if (!remarksResponse.ok) {
            const errorData = await remarksResponse.json();
            throw new Error(errorData.detail || 'Failed to save supervisor remarks');
          }
          break;

        case 8:
          // Save evaluation
          const evalResponse = await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/evaluation/`, {
            method: 'POST',
            headers,
            body: JSON.stringify({
              pre_trip_inspection_score: formData.pre_trip_inspection_score,
              driving_conduct_score: formData.driving_conduct_score,
              incident_management_score: formData.incident_management_score,
              post_trip_reporting_score: formData.post_trip_reporting_score,
              compliance_documentation_score: formData.compliance_documentation_score,
              comments: formData.comments,
            }),
          });
          if (!evalResponse.ok) {
            const errorData = await evalResponse.json();
            throw new Error(errorData.detail || 'Failed to save evaluation');
          }
          break;

        case 9:
          // Save driver sign-off (final step)
          const signOffResponse = await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/sign-offs/`, {
            method: 'POST',
            headers,
            body: JSON.stringify({
              role: 'driver',
              signer_name: formData.driver_signature,
            }),
          });
          if (!signOffResponse.ok) {
            const errorData = await signOffResponse.json();
            throw new Error(errorData.detail || 'Failed to save driver sign-off');
          }
          break;
      }

      // Refresh completion info after successful save
      try {
        const token = localStorage.getItem('access_token');
        const completionRes = await fetch(
          `http://localhost:8000/api/v1/inspections/${inspectionId}/`,
          { headers: { 'Authorization': `Bearer ${token}` } }
        );
        if (completionRes.ok) {
          const inspectionData = await completionRes.json();
          console.log('Refreshed completion info:', inspectionData.post_trip_completion_info);
          if (inspectionData.post_trip_completion_info) {
            setCompletionInfo(inspectionData.post_trip_completion_info);
          }
        }
      } catch (refreshErr) {
        console.error('Error refreshing completion info:', refreshErr);
      }

      return true;
    } catch (err) {
      setError(`Failed to save: ${err instanceof Error ? err.message : 'Unknown error'}`);
      return false;
    } finally {
      setSaving(false);
    }
  };

  const handleNext = async () => {
    if (!validateStep(currentStep)) return;
    
    setNavigating(true);
    // Save current step data
    const saved = await saveCurrentStep();
    if (!saved) {
      setNavigating(false);
      return;
    }
    
    // Move to next step
    setCurrentStep(prev => Math.min(prev + 1, TOTAL_STEPS));
    setNavigating(false);
    window.scrollTo(0, 0);
  };

  const handlePrevious = async () => {
    setError('');
    setNavigating(true);
    
    // Save current step data before going back (so changes aren't lost)
    await saveCurrentStep();
    
    setCurrentStep(prev => Math.max(prev - 1, 1));
    setNavigating(false);
    window.scrollTo(0, 0);
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return;

    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const headers = { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      };

      // Save driver sign-off (final step)
      const signOffResponse = await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/sign-offs/`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          role: 'driver',
          signer_name: formData.driver_signature,
        }),
      });
      
      if (!signOffResponse.ok) {
        const errorData = await signOffResponse.json();
        throw new Error(errorData.detail || 'Failed to save driver sign-off');
      }

      // Update inspection status to completed
      await fetch(`http://localhost:8000/api/v1/inspections/${inspectionId}/`, {
        method: 'PATCH',
        headers,
        body: JSON.stringify({
          status: 'post_trip_completed',
        }),
      });

      setSuccess('Post-trip inspection completed successfully! Redirecting to report...');
      setTimeout(() => {
        router.push(`/dashboard/inspections/${inspectionId}/report`);
      }, 2000);
    } catch (err) {
      setError(`Failed to submit: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const getFormTitle = () => {
    const titles = [
      'Trip Behavior Monitoring',
      'Driving Behavior Check',
      'Post-Trip Report',
      'Risk Score Summary',
      'Corrective Measures',
      'Enforcement Actions',
      'Supervisor Remarks',
      'Evaluation Summary',
      'Driver Sign-Off'
    ];
    return titles[currentStep - 1];
  };

  const addCorrectiveMeasure = () => {
    setFormData({
      ...formData,
      corrective_measures: [
        ...formData.corrective_measures,
        {
          measure_type: 'safety_training',
          required: true,
          due_date: '',
          completed: false,
          completed_date: '',
          notes: '',
        },
      ],
    });
  };

  const addEnforcementAction = () => {
    setFormData({
      ...formData,
      enforcement_actions: [
        ...formData.enforcement_actions,
        {
          action_type: 'verbal_warning',
          is_applied: false,
          start_date: '',
          end_date: '',
          notes: '',
        },
      ],
    });
  };

  const renderForm = () => {
    switch (currentStep) {
      case 1:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            <p style={{ color: '#666', marginBottom: '30px' }}>
              Monitor driver behavior during the trip. Mark violations and add notes.
            </p>
            {formData.behaviors.map((behavior, index) => (
              <div key={index} style={{ marginBottom: '30px', paddingBottom: '20px', borderBottom: '1px solid #e0e0e0' }}>
                <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                  {behavior.behavior} <span style={{ color: '#999', fontSize: '14px' }}>({behavior.points} points)</span>
                </label>
                <div style={{ display: 'flex', gap: '15px', marginBottom: '10px' }}>
                  <RadioOption
                    label="Compliant"
                    value="compliant"
                    selected={behavior.status === 'compliant'}
                    onChange={() => {
                      const updated = [...formData.behaviors];
                      updated[index].status = 'compliant';
                      setFormData({ ...formData, behaviors: updated });
                    }}
                  />
                  <RadioOption
                    label="Violation"
                    value="violation"
                    selected={behavior.status === 'violation'}
                    onChange={() => {
                      const updated = [...formData.behaviors];
                      updated[index].status = 'violation';
                      setFormData({ ...formData, behaviors: updated });
                    }}
                  />
                  <RadioOption
                    label="None"
                    value="none"
                    selected={behavior.status === 'none'}
                    onChange={() => {
                      const updated = [...formData.behaviors];
                      updated[index].status = 'none';
                      setFormData({ ...formData, behaviors: updated });
                    }}
                  />
                </div>
                <textarea
                  className="input"
                  rows={2}
                  placeholder="Notes..."
                  value={behavior.notes}
                  onChange={(e) => {
                    const updated = [...formData.behaviors];
                    updated[index].notes = e.target.value;
                    setFormData({ ...formData, behaviors: updated });
                  }}
                  style={{ marginTop: '10px' }}
                />
              </div>
            ))}
          </div>
        );

      case 2:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            {formData.driving_behaviors.map((behavior, index) => (
              <div key={index} style={{ marginBottom: '30px' }}>
                <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                  {behavior.behavior}
                </label>
                <div style={{ display: 'flex', gap: '15px', marginBottom: '10px' }}>
                  <RadioOption
                    label="Yes"
                    value="yes"
                    selected={behavior.status === true}
                    onChange={() => {
                      const updated = [...formData.driving_behaviors];
                      updated[index].status = true;
                      setFormData({ ...formData, driving_behaviors: updated });
                    }}
                  />
                  <RadioOption
                    label="No"
                    value="no"
                    selected={behavior.status === false}
                    onChange={() => {
                      const updated = [...formData.driving_behaviors];
                      updated[index].status = false;
                      setFormData({ ...formData, driving_behaviors: updated });
                    }}
                  />
                </div>
                <textarea
                  className="input"
                  rows={2}
                  placeholder="Remarks..."
                  value={behavior.remarks}
                  onChange={(e) => {
                    const updated = [...formData.driving_behaviors];
                    updated[index].remarks = e.target.value;
                    setFormData({ ...formData, driving_behaviors: updated });
                  }}
                  style={{ marginTop: '10px' }}
                />
              </div>
            ))}
          </div>
        );

      case 3:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            
            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                Vehicle Fault Report Submitted *
              </label>
              <div style={{ display: 'flex', gap: '15px', marginBottom: '10px' }}>
                <RadioOption
                  label="Yes"
                  value="yes"
                  selected={formData.vehicle_fault_submitted === true}
                  onChange={() => setFormData({ ...formData, vehicle_fault_submitted: true })}
                />
                <RadioOption
                  label="No"
                  value="no"
                  selected={formData.vehicle_fault_submitted === false}
                  onChange={() => setFormData({ ...formData, vehicle_fault_submitted: false })}
                />
              </div>
              <textarea
                className="input"
                rows={3}
                placeholder="Fault Notes..."
                value={formData.fault_notes}
                onChange={(e) => setFormData({ ...formData, fault_notes: e.target.value })}
                style={{ marginTop: '10px' }}
              />
            </div>

            {[
              { key: 'final_inspection_signed', label: 'Final Inspection Signed Off' },
              { key: 'compliance_with_policy', label: 'Compliance with Company Safety Policy' },
              { key: 'attitude_cooperation', label: 'Attitude and Cooperation During Journey' },
              { key: 'incidents_recorded', label: 'Any Incidents/Near Misses or Accidents Recorded & Reported' },
            ].map(({ key, label }) => (
              <div key={key} style={{ marginBottom: '25px' }}>
                <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                  {label} *
                </label>
                <div style={{ display: 'flex', gap: '15px' }}>
                  <RadioOption
                    label="Yes"
                    value="yes"
                    selected={formData[key as keyof PostTripFormData] === true}
                    onChange={() => setFormData({ ...formData, [key]: true })}
                  />
                  <RadioOption
                    label="No"
                    value="no"
                    selected={formData[key as keyof PostTripFormData] === false}
                    onChange={() => setFormData({ ...formData, [key]: false })}
                  />
                </div>
              </div>
            ))}

            <div style={{ marginBottom: '20px' }}>
              <label className="label">Incident Notes</label>
              <textarea
                className="input"
                rows={3}
                placeholder="Describe any incidents..."
                value={formData.incident_notes}
                onChange={(e) => setFormData({ ...formData, incident_notes: e.target.value })}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label className="label">Total Trip Duration *</label>
              <input
                type="text"
                className="input"
                placeholder="e.g., 6 hours 30 minutes"
                value={formData.total_trip_duration}
                onChange={(e) => setFormData({ ...formData, total_trip_duration: e.target.value })}
              />
            </div>
          </div>
        );

      case 4:
        const riskScore = calculateRiskScore();
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            <p style={{ color: '#666', marginBottom: '30px' }}>
              Auto-calculated based on trip behavior monitoring
            </p>
            
            <div style={{ 
              padding: '30px', 
              backgroundColor: '#f5f5f5', 
              borderRadius: '8px',
              marginBottom: '30px'
            }}>
              <h3 style={{ color: '#000', marginBottom: '20px' }}>This Trip</h3>
              <div style={{ fontSize: '48px', fontWeight: 'bold', color: riskScore.color, marginBottom: '10px' }}>
                {riskScore.totalPoints} points
              </div>
              <div style={{ 
                fontSize: '24px', 
                fontWeight: '600', 
                color: riskScore.color,
                padding: '10px 20px',
                backgroundColor: '#fff',
                borderRadius: '8px',
                display: 'inline-block'
              }}>
                Risk Level: {riskScore.riskLevel}
              </div>
            </div>

            <div style={{ 
              padding: '20px', 
              backgroundColor: '#e3f2fd', 
              borderRadius: '8px',
              border: '1px solid #2196F3'
            }}>
              <h4 style={{ color: '#1976D2', marginBottom: '10px' }}>Risk Level Guide</h4>
              <ul style={{ margin: 0, paddingLeft: '20px', color: '#000' }}>
                <li><span style={{ color: '#4CAF50', fontWeight: 'bold' }}>Low (0-3 points)</span> - Excellent performance</li>
                <li><span style={{ color: '#FF9800', fontWeight: 'bold' }}>Medium (4-9 points)</span> - Requires monitoring</li>
                <li><span style={{ color: '#f44336', fontWeight: 'bold' }}>High (10+ points)</span> - Immediate action required</li>
              </ul>
            </div>
          </div>
        );

      case 5:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              Add corrective measures if risk level is Medium or High
            </p>
            
            {formData.corrective_measures.map((measure, index) => (
              <div key={index} style={{ 
                padding: '20px', 
                backgroundColor: '#f9f9f9', 
                borderRadius: '8px',
                marginBottom: '20px',
                border: '1px solid #e0e0e0'
              }}>
                <div style={{ marginBottom: '15px' }}>
                  <label className="label">Measure Type</label>
                  <select
                    className="input"
                    value={measure.measure_type}
                    onChange={(e) => {
                      const updated = [...formData.corrective_measures];
                      updated[index].measure_type = e.target.value;
                      setFormData({ ...formData, corrective_measures: updated });
                    }}
                  >
                    <option value="safety_training">Safety Training</option>
                    <option value="performance_review">Performance Review</option>
                    <option value="probationary_period">Probationary Period</option>
                    <option value="policy_acknowledgment">Policy Acknowledgment</option>
                  </select>
                </div>
                <div style={{ marginBottom: '15px' }}>
                  <label className="label">Due Date</label>
                  <input
                    type="date"
                    className="input"
                    value={measure.due_date}
                    onChange={(e) => {
                      const updated = [...formData.corrective_measures];
                      updated[index].due_date = e.target.value;
                      setFormData({ ...formData, corrective_measures: updated });
                    }}
                  />
                </div>
                <div style={{ marginBottom: '15px' }}>
                  <label className="label">Notes</label>
                  <textarea
                    className="input"
                    rows={2}
                    value={measure.notes}
                    onChange={(e) => {
                      const updated = [...formData.corrective_measures];
                      updated[index].notes = e.target.value;
                      setFormData({ ...formData, corrective_measures: updated });
                    }}
                  />
                </div>
                <button
                  onClick={() => {
                    const updated = formData.corrective_measures.filter((_, i) => i !== index);
                    setFormData({ ...formData, corrective_measures: updated });
                  }}
                  className="button-secondary"
                  style={{ width: 'auto', fontSize: '14px', padding: '6px 12px' }}
                >
                  Remove
                </button>
              </div>
            ))}
            
            <button
              onClick={addCorrectiveMeasure}
              className="button-primary"
              style={{ width: 'auto' }}
            >
              Add Corrective Measure
            </button>
            
            {formData.corrective_measures.length === 0 && (
              <p style={{ color: '#666', marginTop: '20px', fontStyle: 'italic' }}>
                Skip if no corrective measures required
              </p>
            )}
          </div>
        );

      case 6:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              Add enforcement actions if violations occurred
            </p>
            
            {formData.enforcement_actions.map((action, index) => (
              <div key={index} style={{ 
                padding: '20px', 
                backgroundColor: '#fff3e0', 
                borderRadius: '8px',
                marginBottom: '20px',
                border: '1px solid #FF9800'
              }}>
                <div style={{ marginBottom: '15px' }}>
                  <label className="label">Action Type</label>
                  <select
                    className="input"
                    value={action.action_type}
                    onChange={(e) => {
                      const updated = [...formData.enforcement_actions];
                      updated[index].action_type = e.target.value;
                      setFormData({ ...formData, enforcement_actions: updated });
                    }}
                  >
                    <option value="verbal_warning">Verbal Warning</option>
                    <option value="written_warning">Written Warning</option>
                    <option value="suspension">Suspension</option>
                    <option value="final_warning">Final Warning</option>
                    <option value="termination">Termination</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div style={{ marginBottom: '15px' }}>
                  <label className="label">Start Date</label>
                  <input
                    type="date"
                    className="input"
                    value={action.start_date}
                    onChange={(e) => {
                      const updated = [...formData.enforcement_actions];
                      updated[index].start_date = e.target.value;
                      setFormData({ ...formData, enforcement_actions: updated });
                    }}
                  />
                </div>
                {action.action_type === 'Suspension' && (
                  <div style={{ marginBottom: '15px' }}>
                    <label className="label">End Date</label>
                    <input
                      type="date"
                      className="input"
                      value={action.end_date}
                      onChange={(e) => {
                        const updated = [...formData.enforcement_actions];
                        updated[index].end_date = e.target.value;
                        setFormData({ ...formData, enforcement_actions: updated });
                      }}
                    />
                  </div>
                )}
                <div style={{ marginBottom: '15px' }}>
                  <label className="label">Notes</label>
                  <textarea
                    className="input"
                    rows={2}
                    value={action.notes}
                    onChange={(e) => {
                      const updated = [...formData.enforcement_actions];
                      updated[index].notes = e.target.value;
                      setFormData({ ...formData, enforcement_actions: updated });
                    }}
                  />
                </div>
                <button
                  onClick={() => {
                    const updated = formData.enforcement_actions.filter((_, i) => i !== index);
                    setFormData({ ...formData, enforcement_actions: updated });
                  }}
                  className="button-secondary"
                  style={{ width: 'auto', fontSize: '14px', padding: '6px 12px' }}
                >
                  Remove
                </button>
              </div>
            ))}
            
            <button
              onClick={addEnforcementAction}
              className="button-primary"
              style={{ width: 'auto' }}
            >
              Add Enforcement Action
            </button>
            
            {formData.enforcement_actions.length === 0 && (
              <p style={{ color: '#666', marginTop: '20px', fontStyle: 'italic' }}>
                Skip if no enforcement actions required
              </p>
            )}
          </div>
        );

      case 7:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            
            <div style={{ marginBottom: '20px' }}>
              <label className="label">Supervisor Remarks *</label>
              <textarea
                className="input"
                rows={5}
                placeholder="Enter detailed supervisor remarks..."
                value={formData.supervisor_remarks}
                onChange={(e) => setFormData({ ...formData, supervisor_remarks: e.target.value })}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label className="label">Recommendation</label>
              <textarea
                className="input"
                rows={3}
                placeholder="Enter recommendations for driver..."
                value={formData.recommendation}
                onChange={(e) => setFormData({ ...formData, recommendation: e.target.value })}
              />
            </div>
          </div>
        );

      case 8:
        const overallScore = calculateOverallScore();
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            <p style={{ color: '#666', marginBottom: '30px' }}>
              Rate each area on a scale of 1-5
            </p>
            
            {[
              { key: 'pre_trip_inspection_score', label: 'Pre-Trip Inspection Score' },
              { key: 'driving_conduct_score', label: 'Driving Conduct Score' },
              { key: 'incident_management_score', label: 'Incident Management Score' },
              { key: 'post_trip_reporting_score', label: 'Post-Trip Feedback & Reporting Score' },
              { key: 'compliance_documentation_score', label: 'Compliance & Documentation Score' },
            ].map(({ key, label }) => (
              <div key={key} style={{ marginBottom: '25px' }}>
                <label style={{ display: 'block', fontWeight: '600', color: '#000', marginBottom: '10px' }}>
                  {label} *
                </label>
                <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                  {[1, 2, 3, 4, 5].map(score => (
                    <button
                      key={score}
                      onClick={() => setFormData({ ...formData, [key]: score })}
                      style={{
                        width: '50px',
                        height: '50px',
                        borderRadius: '50%',
                        border: `2px solid ${formData[key as keyof PostTripFormData] === score ? '#2196F3' : '#ccc'}`,
                        backgroundColor: formData[key as keyof PostTripFormData] === score ? '#2196F3' : '#fff',
                        color: formData[key as keyof PostTripFormData] === score ? '#fff' : '#000',
                        fontSize: '20px',
                        fontWeight: 'bold',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        padding: 0,
                      }}
                    >
                      {score}
                    </button>
                  ))}
                </div>
              </div>
            ))}

            <div style={{ 
              padding: '30px', 
              backgroundColor: '#f5f5f5', 
              borderRadius: '8px',
              marginTop: '30px',
              marginBottom: '30px'
            }}>
              <h3 style={{ color: '#000', marginBottom: '15px' }}>Overall Safety Performance</h3>
              <div style={{ fontSize: '36px', fontWeight: 'bold', color: overallScore.color, marginBottom: '10px' }}>
                {overallScore.average}
              </div>
              <div style={{ 
                fontSize: '20px', 
                fontWeight: '600', 
                color: overallScore.color
              }}>
                {overallScore.rating}
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label className="label">Comments</label>
              <textarea
                className="input"
                rows={4}
                placeholder="Additional comments..."
                value={formData.comments}
                onChange={(e) => setFormData({ ...formData, comments: e.target.value })}
              />
            </div>
          </div>
        );

      case 9:
        return (
          <div>
            <h2 style={{ color: '#000', marginBottom: '20px' }}>{getFormTitle()}</h2>
            
            <div style={{ 
              padding: '20px', 
              backgroundColor: '#fff3cd', 
              borderRadius: '8px',
              marginBottom: '30px',
              border: '1px solid #ffc107'
            }}>
              <h3 style={{ color: '#856404', marginBottom: '10px' }}>Declaration</h3>
              <p style={{ color: '#856404', marginBottom: '0' }}>
                I acknowledge that the information provided in this post-trip report is accurate and complete. 
                I understand that any violations noted may result in corrective actions or enforcement measures.
              </p>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label className="label">Driver Name (Auto-filled)</label>
              <input
                type="text"
                className="input"
                value="Current Driver"
                disabled
                style={{ backgroundColor: '#f5f5f5' }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label className="label">Signature *</label>
              <input
                type="text"
                className="input"
                placeholder="Type your full name as signature"
                value={formData.driver_signature}
                onChange={(e) => setFormData({ ...formData, driver_signature: e.target.value })}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label className="label">Date/Time</label>
              <input
                type="text"
                className="input"
                value={new Date().toLocaleString()}
                disabled
                style={{ backgroundColor: '#f5f5f5' }}
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
                You&apos;ve completed all sections of the post-trip inspection. Click &quot;Submit Post-Trip&quot; to finalize.
              </p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  if (loading && !completionInfo) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-header">
          <div>
            <h1>Post-Trip Checklist</h1>
            <p style={{ color: '#666', marginTop: '5px' }}>Loading your progress...</p>
          </div>
        </div>
        <div className="profile-card">
          <div style={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center',
            padding: '60px 20px',
            gap: '20px'
          }}>
            <div style={{
              width: '48px',
              height: '48px',
              border: '4px solid #e0e0e0',
              borderTopColor: '#000',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
            }} />
            <p style={{ color: '#666', margin: 0 }}>Loading inspection data...</p>
            <style>{`
              @keyframes spin {
                to { transform: rotate(360deg); }
              }
            `}</style>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1>Post-Trip Checklist</h1>
          <p style={{ color: '#666', marginTop: '5px' }}>
            Complete all post-trip sections after journey completion
            {completionInfo && (
              <span style={{ marginLeft: '15px', fontWeight: '600', color: '#4CAF50' }}>
                • {completionInfo.completed_steps.length}/{completionInfo.total_steps} sections complete
              </span>
            )}
          </p>
        </div>
        <button 
          onClick={() => router.push('/dashboard/inspections')} 
          className="button-secondary"
          style={{ width: 'auto' }}
        >
          Back to Inspections
        </button>
      </div>

      <div className="profile-card">
        <ProgressTracker 
          currentStep={currentStep} 
          totalSteps={TOTAL_STEPS}
          completedSteps={completionInfo?.completed_steps}
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
            disabled={currentStep === 1 || navigating || saving}
            className="button-secondary"
            style={{ 
              width: 'auto',
              minWidth: '120px',
              opacity: currentStep === 1 ? 0.5 : 1,
              cursor: currentStep === 1 || navigating || saving ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
            }}
          >
            {navigating && currentStep > 1 ? (
              <>
                <span style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid #ccc',
                  borderTopColor: '#333',
                  borderRadius: '50%',
                  animation: 'spin 0.8s linear infinite',
                }} />
                Saving...
              </>
            ) : 'Previous'}
          </button>

          {currentStep < TOTAL_STEPS ? (
            <button
              onClick={handleNext}
              disabled={navigating || saving}
              className="button-primary"
              style={{ 
                width: 'auto',
                minWidth: '120px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
              }}
            >
              {(navigating || saving) && currentStep < TOTAL_STEPS ? (
                <>
                  <span style={{
                    width: '16px',
                    height: '16px',
                    border: '2px solid rgba(255,255,255,0.3)',
                    borderTopColor: '#fff',
                    borderRadius: '50%',
                    animation: 'spin 0.8s linear infinite',
                  }} />
                  Saving...
                </>
              ) : 'Next'}
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={saving || navigating}
              className="button-primary"
              style={{ 
                width: 'auto',
                minWidth: '150px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
              }}
            >
              {saving ? (
                <>
                  <span style={{
                    width: '16px',
                    height: '16px',
                    border: '2px solid rgba(255,255,255,0.3)',
                    borderTopColor: '#fff',
                    borderRadius: '50%',
                    animation: 'spin 0.8s linear infinite',
                  }} />
                  Submitting...
                </>
              ) : 'Submit Post-Trip'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default function PostTripWizard() {
  return (
    <Suspense fallback={
      <div className="dashboard-container">
        <div className="dashboard-header">
          <div>
            <h1>Post-Trip Checklist</h1>
            <p style={{ color: '#666', marginTop: '5px' }}>Loading your progress...</p>
          </div>
        </div>
        <div className="profile-card">
          <div style={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center',
            padding: '60px 20px',
            gap: '20px'
          }}>
            <div style={{
              width: '48px',
              height: '48px',
              border: '4px solid #e0e0e0',
              borderTopColor: '#000',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
            }} />
            <p style={{ color: '#666', margin: 0 }}>Loading...</p>
            <style>{`
              @keyframes spin {
                to { transform: rotate(360deg); }
              }
            `}</style>
          </div>
        </div>
      </div>
    }>
      <PostTripWizardContent />
    </Suspense>
  );
}
