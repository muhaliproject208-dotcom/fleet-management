'use client';

import { useRouter, useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { isAuthenticated } from '@/lib/api/auth';
import { getInspection } from '@/lib/api/inspections';
import { PreTripInspectionFull } from '@/lib/api/inspections/types';
import InspectionStatusBadge from '../components/InspectionStatusBadge';

export default function InspectionDetailPage() {
  const router = useRouter();
  const params = useParams();
  const id = params?.id as string;

  const [inspection, setInspection] = useState<PreTripInspectionFull | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

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
  }, [router, id]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

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
      {/* Header */}
      <div className="dashboard-header">
        <div>
          <h1>{inspection.inspection_id}</h1>
          <p style={{ color: '#666', marginTop: '5px' }}>
            {formatDate(inspection.inspection_date)} • {inspection.route}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <InspectionStatusBadge status={inspection.status} size="md" />
          <button 
            onClick={() => router.push('/dashboard/inspections')} 
            className="button-secondary"
            style={{ width: 'auto' }}
          >
            Back to List
          </button>
        </div>
      </div>

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

      {/* Placeholder for additional sections */}
      <div className="profile-card" style={{ marginTop: '20px', textAlign: 'center', padding: '40px' }}>
        <span className="material-icons" style={{ fontSize: '48px', color: '#ccc', marginBottom: '15px' }}>
          construction
        </span>
        <h3 style={{ color: '#000', marginBottom: '10px' }}>Additional Sections Coming Soon</h3>
        <p style={{ color: '#666' }}>
          Health checks, documentation, vehicle checks, and more will be displayed here.
        </p>
      </div>
    </div>
  );
}
