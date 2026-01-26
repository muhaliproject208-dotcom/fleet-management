'use client';

import { useRouter, useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { isAuthenticated, getCurrentUser } from '@/lib/api/auth';
import { getInspection, approveInspection, rejectInspection, downloadPrechecklistPDF } from '@/lib/api/inspections';
import { PreTripInspectionFull, InspectionStatus } from '@/lib/api/inspections/types';
import InspectionStatusBadge from '../components/InspectionStatusBadge';

export default function InspectionDetailPage() {
  const router = useRouter();
  const params = useParams();
  const id = params?.id as string;

  const [inspection, setInspection] = useState<PreTripInspectionFull | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [showPostTripConfirmModal, setShowPostTripConfirmModal] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [userRole, setUserRole] = useState<string | null>(null);
  const [pdfLoading, setPdfLoading] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    // Get user role - defer setState to avoid cascading renders
    const frame = requestAnimationFrame(() => {
      const user = getCurrentUser();
      if (user) {
        setUserRole(user.role);
      }
    });

    const fetchInspectionData = async () => {
      const response = await getInspection(id);

      if (response.error) {
        setError(response.error);
      } else if (response.data) {
        setInspection(response.data);
      }

      setLoading(false);
    };

    void fetchInspectionData();

    return () => cancelAnimationFrame(frame);
  }, [router, id]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const handleApprove = async () => {
    if (!inspection) return;
    
    setActionLoading(true);
    setError('');
    
    const response = await approveInspection(inspection.id);
    
    if (response.error) {
      setError(response.error);
    } else {
      setSuccess('Inspection approved successfully!');
      // Refresh inspection data
      const refreshed = await getInspection(id);
      if (refreshed.data) {
        setInspection(refreshed.data);
      }
    }
    
    setActionLoading(false);
  };

  const handleReject = async () => {
    if (!inspection || !rejectReason.trim()) {
      setError('Please provide a rejection reason');
      return;
    }
    
    setActionLoading(true);
    setError('');
    
    const response = await rejectInspection(inspection.id, rejectReason);
    
    if (response.error) {
      setError(response.error);
    } else {
      setSuccess('Inspection rejected.');
      setShowRejectModal(false);
      setRejectReason('');
      // Refresh inspection data
      const refreshed = await getInspection(id);
      if (refreshed.data) {
        setInspection(refreshed.data);
      }
    }
    
    setActionLoading(false);
  };

  const handleDownloadPrechecklistPDF = async () => {
    if (!inspection) return;
    
    setPdfLoading(true);
    setError('');
    
    const response = await downloadPrechecklistPDF(inspection.id, inspection.inspection_id);
    
    if (response.error) {
      setError(response.error);
    } else {
      setSuccess('Pre-checklist PDF downloaded successfully!');
    }
    
    setPdfLoading(false);
  };

  const canApproveOrReject = userRole === 'fleet_manager' || userRole === 'superuser';

  if (loading) {
    return (
      <div className="container">
        <div className="text-center">
          <div className="spinner" style={{ margin: '0 auto' }}></div>
          <p style={{ marginTop: '20px' }}>Loading inspection...</p>
        </div>
      </div>
    );
  }

  if (error || !inspection) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1>Inspection Not Found</h1>
          <button 
            onClick={() => router.push('/dashboard/inspections')} 
            className="button-secondary"
            style={{ width: 'auto' }}
          >
            Back to Inspections
          </button>
        </div>
        <div className="alert alert-error">{error || 'Inspection not found'}</div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Success/Error Messages */}
      {success && (
        <div className="alert alert-success" style={{ marginBottom: '20px' }}>
          {success}
        </div>
      )}
      {error && (
        <div className="alert alert-error" style={{ marginBottom: '20px' }}>
          {error}
        </div>
      )}

      {/* Header */}
      <div className="dashboard-header">
        <div>
          <h1>{inspection.inspection_id}</h1>
          <p style={{ color: '#666', marginTop: '5px' }}>
            {formatDate(inspection.inspection_date)} • {inspection.route}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          <InspectionStatusBadge status={inspection.status} size="md" />
          
          {/* Approve/Reject buttons for Fleet Managers when status is submitted */}
          {canApproveOrReject && inspection.status === InspectionStatus.SUBMITTED && (
            <>
              <button 
                onClick={handleApprove}
                disabled={actionLoading}
                className="button-primary"
                style={{ 
                  width: 'auto', 
                  backgroundColor: '#000',
                  borderColor: '#000',
                }}
              >
                {actionLoading ? 'Processing...' : 'Approve'}
              </button>
              <button 
                onClick={handleDownloadPrechecklistPDF}
                disabled={pdfLoading}
                className="button-primary"
                style={{ 
                  width: 'auto', 
                  backgroundColor: '#2c5aa0',
                  borderColor: '#2c5aa0',
                }}
              >
                {pdfLoading ? 'Generating...' : 'Generate PDF'}
              </button>
              <button 
                onClick={() => setShowRejectModal(true)}
                disabled={actionLoading}
                className="button-secondary"
                style={{ 
                  width: 'auto', 
                  backgroundColor: '#666',
                  borderColor: '#666',
                  color: '#fff',
                }}
              >
                Reject
              </button>
            </>
          )}
          
          {/* Post-Trip button for approved inspections */}
          {inspection.status === InspectionStatus.APPROVED && (
            inspection.post_trip ? (
              <button 
                onClick={() => router.push(`/dashboard/inspections/${inspection.id}/report`)}
                className="button-primary"
                style={{ 
                  width: 'auto',
                  backgroundColor: '#000',
                  borderColor: '#000',
                }}
              >
                View Report
              </button>
            ) : (
              <button 
                onClick={() => setShowPostTripConfirmModal(true)}
                className="button-primary"
                style={{ 
                  width: 'auto',
                  backgroundColor: '#000',
                  borderColor: '#000',
                }}
              >
                Start Post-Trip
              </button>
            )
          )}
          
          <button 
            onClick={() => router.push('/dashboard/inspections')} 
            className="button-secondary"
            style={{ width: 'auto' }}
          >
            Back to List
          </button>
        </div>
      </div>

      {/* Reject Modal */}
      {showRejectModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div style={{
            backgroundColor: '#fff',
            padding: '30px',
            borderRadius: '12px',
            maxWidth: '500px',
            width: '90%',
          }}>
            <h3 style={{ color: '#000', marginBottom: '20px' }}>Reject Inspection</h3>
            <p style={{ color: '#666', marginBottom: '15px' }}>
              Please provide a reason for rejecting this inspection:
            </p>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Enter rejection reason..."
              style={{
                width: '100%',
                minHeight: '100px',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '8px',
                marginBottom: '20px',
                resize: 'vertical',
              }}
            />
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button 
                onClick={() => {
                  setShowRejectModal(false);
                  setRejectReason('');
                }}
                className="button-secondary"
                style={{ width: 'auto' }}
              >
                Cancel
              </button>
              <button 
                onClick={handleReject}
                disabled={actionLoading || !rejectReason.trim()}
                className="button-primary"
                style={{ 
                  width: 'auto',
                  backgroundColor: '#000',
                  borderColor: '#000',
                  opacity: !rejectReason.trim() ? 0.5 : 1,
                }}
              >
                {actionLoading ? 'Rejecting...' : 'Confirm Reject'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Content Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        {/* Driver Info */}
        <div className="profile-card">
          <h3 style={{ color: '#000', marginBottom: '15px', fontSize: '18px' }}>Driver Information</h3>
          <div style={{ marginBottom: '10px' }}>
            <span style={{ color: '#666', fontSize: '14px' }}>Name:</span>
            <p style={{ color: '#000', fontWeight: '500', marginTop: '5px' }}>
              {inspection.driver.full_name}
            </p>
          </div>
          <div style={{ marginBottom: '10px' }}>
            <span style={{ color: '#666', fontSize: '14px' }}>Driver ID:</span>
            <p style={{ color: '#000', fontWeight: '500', marginTop: '5px' }}>
              {inspection.driver.driver_id}
            </p>
          </div>
        </div>

        {/* Vehicle Info */}
        <div className="profile-card">
          <h3 style={{ color: '#000', marginBottom: '15px', fontSize: '18px' }}>Vehicle Information</h3>
          <div style={{ marginBottom: '10px' }}>
            <span style={{ color: '#666', fontSize: '14px' }}>Registration:</span>
            <p style={{ color: '#000', fontWeight: '500', marginTop: '5px' }}>
              {inspection.vehicle.registration_number}
            </p>
          </div>
          <div style={{ marginBottom: '10px' }}>
            <span style={{ color: '#666', fontSize: '14px' }}>Vehicle ID:</span>
            <p style={{ color: '#000', fontWeight: '500', marginTop: '5px' }}>
              {inspection.vehicle.vehicle_id}
            </p>
          </div>
        </div>

        {/* Trip Details */}
        <div className="profile-card">
          <h3 style={{ color: '#000', marginBottom: '15px', fontSize: '18px' }}>Trip Details</h3>
          <div style={{ marginBottom: '10px' }}>
            <span style={{ color: '#666', fontSize: '14px' }}>Route:</span>
            <p style={{ color: '#000', fontWeight: '500', marginTop: '5px' }}>
              {inspection.route}
            </p>
          </div>
          <div style={{ marginBottom: '10px' }}>
            <span style={{ color: '#666', fontSize: '14px' }}>Driving Hours:</span>
            <p style={{ color: '#000', fontWeight: '500', marginTop: '5px' }}>
              {inspection.approved_driving_hours}
            </p>
          </div>
          <div style={{ marginBottom: '10px' }}>
            <span style={{ color: '#666', fontSize: '14px' }}>Rest Stops:</span>
            <p style={{ color: '#000', fontWeight: '500', marginTop: '5px' }}>
              {inspection.approved_rest_stops}
            </p>
          </div>
        </div>
      </div>

      {/* Supervisor Info */}
      <div className="profile-card" style={{ marginTop: '20px' }}>
        <h3 style={{ color: '#000', marginBottom: '15px', fontSize: '18px' }}>Inspection Details</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
          <div>
            <span style={{ color: '#666', fontSize: '14px' }}>Created By:</span>
            <p style={{ color: '#000', fontWeight: '500', marginTop: '5px' }}>
              {inspection.supervisor.full_name}
            </p>
          </div>
          <div>
            <span style={{ color: '#666', fontSize: '14px' }}>Created At:</span>
            <p style={{ color: '#000', fontWeight: '500', marginTop: '5px' }}>
              {formatDate(inspection.created_at)}
            </p>
          </div>
          {inspection.mechanic && (
            <div>
              <span style={{ color: '#666', fontSize: '14px' }}>Assigned Mechanic:</span>
              <p style={{ color: '#000', fontWeight: '500', marginTop: '5px' }}>
                {inspection.mechanic.full_name}
              </p>
            </div>
          )}
          {inspection.approved_by && (
            <div>
              <span style={{ color: '#666', fontSize: '14px' }}>Approved By:</span>
              <p style={{ color: '#000', fontWeight: '500', marginTop: '5px' }}>
                {inspection.approved_by.full_name}
              </p>
            </div>
          )}
        </div>
        
        {inspection.rejection_reason && (
          <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#fee', borderRadius: '8px' }}>
            <span style={{ color: '#c00', fontSize: '14px', fontWeight: '600' }}>Rejection Reason:</span>
            <p style={{ color: '#000', marginTop: '5px' }}>
              {inspection.rejection_reason}
            </p>
          </div>
        )}
      </div>

      {/* Health & Fitness Check */}
      {inspection.health_fitness && (
        <div className="profile-card" style={{ marginTop: '20px' }}>
          <h3 style={{ color: '#000', marginBottom: '15px', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="material-icons" style={{ fontSize: '20px', color: '#000' }}>health_and_safety</span>
            Health & Fitness Check
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px' }}>
            <CheckItem 
              label="Alcohol Test" 
              status={inspection.health_fitness.alcohol_test_status} 
              remarks={inspection.health_fitness.alcohol_test_remarks}
            />
            <CheckItem 
              label="Temperature Check" 
              status={inspection.health_fitness.temperature_check_status}
              value={inspection.health_fitness.temperature_value ? `${inspection.health_fitness.temperature_value}°C` : undefined}
            />
            <BooleanItem label="Fit for Duty" value={inspection.health_fitness.fit_for_duty} />
            <BooleanItem 
              label="On Medication" 
              value={inspection.health_fitness.medication_status} 
              remarks={inspection.health_fitness.medication_remarks}
              invertColor
            />
            <BooleanItem label="No Health Impairment" value={inspection.health_fitness.no_health_impairment} />
            <BooleanItem 
              label="Fatigue Checklist Completed" 
              value={inspection.health_fitness.fatigue_checklist_completed}
              remarks={inspection.health_fitness.fatigue_remarks}
            />
          </div>
        </div>
      )}

      {/* Documentation & Compliance */}
      {inspection.documentation && (
        <div className="profile-card" style={{ marginTop: '20px' }}>
          <h3 style={{ color: '#000', marginBottom: '15px', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="material-icons" style={{ fontSize: '20px', color: '#000' }}>description</span>
            Documentation & Compliance
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px' }}>
            <CheckItem 
              label="Certificate of Fitness" 
              status={inspection.documentation.certificate_of_fitness}
            />
            <BooleanItem label="Road Tax Valid" value={inspection.documentation.road_tax_valid} />
            <BooleanItem label="Insurance Valid" value={inspection.documentation.insurance_valid} />
            <BooleanItem label="Trip Authorization Signed" value={inspection.documentation.trip_authorization_signed} />
            <BooleanItem label="Logbook Present" value={inspection.documentation.logbook_present} />
            <BooleanItem label="Driver Handbook Present" value={inspection.documentation.driver_handbook_present} />
            <BooleanItem label="Permits Valid" value={inspection.documentation.permits_valid} />
            <BooleanItem label="PPE Available" value={inspection.documentation.ppe_available} />
            <BooleanItem label="Route Familiarity" value={inspection.documentation.route_familiarity} />
            <BooleanItem label="Emergency Procedures Known" value={inspection.documentation.emergency_procedures_known} />
            <BooleanItem label="GPS Activated" value={inspection.documentation.gps_activated} />
            <BooleanItem label="Safety Briefing Provided" value={inspection.documentation.safety_briefing_provided} />
            <BooleanItem label="RTSA Clearance" value={inspection.documentation.rtsa_clearance} />
            <div>
              <span style={{ color: '#666', fontSize: '14px' }}>Emergency Contact:</span>
              <p style={{ color: '#000', fontWeight: '500', marginTop: '5px' }}>
                {inspection.documentation.emergency_contact || 'Not provided'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Vehicle Exterior Checks */}
      {inspection.exterior_checks && inspection.exterior_checks.length > 0 && (
        <div className="profile-card" style={{ marginTop: '20px' }}>
          <h3 style={{ color: '#000', marginBottom: '15px', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="material-icons" style={{ fontSize: '20px', color: '#000' }}>directions_car</span>
            Vehicle Exterior Checks
          </h3>
          <VehicleCheckTable checks={inspection.exterior_checks} />
        </div>
      )}

      {/* Engine & Fluid Checks */}
      {inspection.engine_fluid_checks && inspection.engine_fluid_checks.length > 0 && (
        <div className="profile-card" style={{ marginTop: '20px' }}>
          <h3 style={{ color: '#000', marginBottom: '15px', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="material-icons" style={{ fontSize: '20px', color: '#000' }}>build</span>
            Engine & Fluid Checks
          </h3>
          <VehicleCheckTable checks={inspection.engine_fluid_checks} />
        </div>
      )}

      {/* Interior & Cabin Checks */}
      {inspection.interior_cabin_checks && inspection.interior_cabin_checks.length > 0 && (
        <div className="profile-card" style={{ marginTop: '20px' }}>
          <h3 style={{ color: '#000', marginBottom: '15px', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="material-icons" style={{ fontSize: '20px', color: '#000' }}>airline_seat_recline_normal</span>
            Interior & Cabin Checks
          </h3>
          <VehicleCheckTable checks={inspection.interior_cabin_checks} />
        </div>
      )}

      {/* Functional Checks */}
      {inspection.functional_checks && inspection.functional_checks.length > 0 && (
        <div className="profile-card" style={{ marginTop: '20px' }}>
          <h3 style={{ color: '#000', marginBottom: '15px', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="material-icons" style={{ fontSize: '20px', color: '#000' }}>settings</span>
            Functional Checks
          </h3>
          <VehicleCheckTable checks={inspection.functional_checks} />
        </div>
      )}

      {/* Safety Equipment Checks */}
      {inspection.safety_equipment_checks && inspection.safety_equipment_checks.length > 0 && (
        <div className="profile-card" style={{ marginTop: '20px' }}>
          <h3 style={{ color: '#000', marginBottom: '15px', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="material-icons" style={{ fontSize: '20px', color: '#000' }}>security</span>
            Safety Equipment Checks
          </h3>
          <VehicleCheckTable checks={inspection.safety_equipment_checks} />
        </div>
      )}

      {/* Supervisor Remarks / Final Verification */}
      {inspection.supervisor_remarks && (
        <div className="profile-card" style={{ marginTop: '20px' }}>
          <h3 style={{ color: '#000', marginBottom: '15px', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="material-icons" style={{ fontSize: '20px', color: '#000' }}>verified</span>
            Final Verification & Supervisor Remarks
          </h3>
          <div style={{ marginBottom: '15px' }}>
            <span style={{ color: '#666', fontSize: '14px' }}>Supervisor:</span>
            <p style={{ color: '#000', fontWeight: '500', marginTop: '5px' }}>
              {inspection.supervisor_remarks.supervisor_name}
            </p>
          </div>
          <div style={{ marginBottom: '15px' }}>
            <span style={{ color: '#666', fontSize: '14px' }}>Remarks:</span>
            <p style={{ color: '#000', marginTop: '5px', whiteSpace: 'pre-line' }}>
              {inspection.supervisor_remarks.remarks}
            </p>
          </div>
          {inspection.supervisor_remarks.recommendation && (
            <div style={{ 
              padding: '15px', 
              backgroundColor: inspection.supervisor_remarks.recommendation.includes('cleared') ? '#e8f5e9' : '#fff3e0',
              borderRadius: '8px',
              marginTop: '15px'
            }}>
              <span style={{ color: '#666', fontSize: '14px', fontWeight: '600' }}>Recommendation:</span>
              <p style={{ color: '#000', marginTop: '5px', fontWeight: '500' }}>
                {inspection.supervisor_remarks.recommendation}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Post-Trip Confirmation Modal */}
      {showPostTripConfirmModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div style={{
            backgroundColor: '#fff',
            padding: '30px',
            borderRadius: '12px',
            maxWidth: '500px',
            width: '90%',
            boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '20px' }}>
              <span className="material-icons" style={{ fontSize: '40px', color: '#000' }}>
                assignment_turned_in
              </span>
              <h3 style={{ color: '#000', margin: 0, fontSize: '20px' }}>Start Post-Trip Checklist</h3>
            </div>
            <p style={{ color: '#666', marginBottom: '20px', lineHeight: '1.6' }}>
              You are about to begin the post-trip inspection checklist for inspection <strong>{inspection.inspection_id}</strong>.
            </p>
            <div style={{ 
              backgroundColor: '#f5f5f5', 
              padding: '15px', 
              borderRadius: '8px',
              marginBottom: '20px',
            }}>
              <p style={{ color: '#000', fontWeight: '600', marginBottom: '10px' }}>This process includes:</p>
              <ul style={{ color: '#666', margin: 0, paddingLeft: '20px' }}>
                <li>Trip behavior monitoring</li>
                <li>Driving behavior assessment</li>
                <li>Post-trip report completion</li>
                <li>Risk score calculation</li>
                <li>Supervisor evaluation & remarks</li>
                <li>Driver sign-off</li>
              </ul>
            </div>
            <p style={{ color: '#666', fontSize: '14px', marginBottom: '25px' }}>
              Ensure the trip has been completed before proceeding.
            </p>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button 
                onClick={() => setShowPostTripConfirmModal(false)}
                className="button-secondary"
                style={{ width: 'auto' }}
              >
                Cancel
              </button>
              <button 
                onClick={() => {
                  setShowPostTripConfirmModal(false);
                  router.push(`/dashboard/inspections/${inspection.id}/post-trip`);
                }}
                className="button-primary"
                style={{ 
                  width: 'auto',
                  backgroundColor: '#000',
                  borderColor: '#000',
                }}
              >
                Continue to Checklist
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper Components
function CheckItem({ label, status, remarks, value }: { 
  label: string; 
  status: string; 
  remarks?: string | null;
  value?: string;
}) {
  const isPass = status === 'pass' || status === 'valid';
  return (
    <div>
      <span style={{ color: '#666', fontSize: '14px' }}>{label}:</span>
      <p style={{ 
        color: isPass ? '#4caf50' : '#f44336', 
        fontWeight: '600', 
        marginTop: '5px',
        textTransform: 'capitalize'
      }}>
        {status} {value && `(${value})`}
      </p>
      {remarks && (
        <p style={{ color: '#666', fontSize: '13px', marginTop: '3px', fontStyle: 'italic' }}>
          {remarks}
        </p>
      )}
    </div>
  );
}

function BooleanItem({ label, value, remarks, invertColor }: { 
  label: string; 
  value: boolean; 
  remarks?: string | null;
  invertColor?: boolean;
}) {
  const isPositive = invertColor ? !value : value;
  return (
    <div>
      <span style={{ color: '#666', fontSize: '14px' }}>{label}:</span>
      <p style={{ 
        color: isPositive ? '#4caf50' : '#f44336', 
        fontWeight: '600', 
        marginTop: '5px' 
      }}>
        {value ? 'Yes' : 'No'}
      </p>
      {remarks && (
        <p style={{ color: '#666', fontSize: '13px', marginTop: '3px', fontStyle: 'italic' }}>
          {remarks}
        </p>
      )}
    </div>
  );
}

function VehicleCheckTable({ checks }: { checks: Array<{ check_item: string; status: string; remarks?: string | null }> }) {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ backgroundColor: '#f5f5f5' }}>
            <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd', color: '#000' }}>Item</th>
            <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #ddd', color: '#000', width: '100px' }}>Status</th>
            <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd', color: '#000' }}>Remarks</th>
          </tr>
        </thead>
        <tbody>
          {checks.map((check, index) => (
            <tr key={index} style={{ backgroundColor: index % 2 === 0 ? '#fff' : '#fafafa' }}>
              <td style={{ padding: '12px', borderBottom: '1px solid #eee', color: '#000' }}>
                {check.check_item}
              </td>
              <td style={{ padding: '12px', borderBottom: '1px solid #eee', textAlign: 'center' }}>
                <span style={{
                  display: 'inline-block',
                  padding: '4px 12px',
                  borderRadius: '20px',
                  fontSize: '13px',
                  fontWeight: '600',
                  backgroundColor: check.status === 'pass' ? '#e8f5e9' : '#ffebee',
                  color: check.status === 'pass' ? '#2e7d32' : '#c62828',
                  textTransform: 'capitalize'
                }}>
                  {check.status}
                </span>
              </td>
              <td style={{ padding: '12px', borderBottom: '1px solid #eee', color: '#666', fontStyle: check.remarks ? 'normal' : 'italic' }}>
                {check.remarks || '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
