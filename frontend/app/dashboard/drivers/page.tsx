'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/api/auth';
import { getDrivers, createDriver, updateDriver, Driver, CreateDriverData } from '@/lib/api/drivers';
import { getVehicles, Vehicle } from '@/lib/api/vehicles';

export default function DriversPage() {
  const router = useRouter();
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingDriver, setEditingDriver] = useState<Driver | null>(null);
  const [formData, setFormData] = useState<CreateDriverData & { vehicle_id?: string }>({
    full_name: '',
    license_number: '',
    phone_number: '',
    email: '',
  });
  const [submitting, setSubmitting] = useState(false);

  const fetchVehicles = useCallback(async () => {
    const response = await getVehicles({ is_active: 'all' });

    if (response.error) {
      console.error('Failed to fetch vehicles:', response.error);
    } else if (response.data) {
      setVehicles(response.data.results || []);
    }
  }, []);

  const fetchDrivers = useCallback(async () => {
    const response = await getDrivers({ is_active: 'all' });

    if (response.error) {
      setError(response.error);
    } else if (response.data) {
      setDrivers(response.data.results || []);
    }

    setLoading(false);
  }, []);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    const timer = setTimeout(() => {
      void fetchDrivers();
      void fetchVehicles();
    }, 100);

    return () => clearTimeout(timer);
  }, [router, fetchDrivers, fetchVehicles]);

  const openModal = (driver?: Driver) => {
    if (driver) {
      setEditingDriver(driver);
      // Find the vehicle assigned to this driver
      const assignedVehicle = vehicles.find(v => v.driver_name === driver.full_name);
      setFormData({
        full_name: driver.full_name,
        license_number: driver.license_number,
        phone_number: driver.phone_number,
        email: driver.email || '',
        vehicle_id: assignedVehicle ? assignedVehicle.id : undefined,
      });
    } else {
      setEditingDriver(null);
      setFormData({
        full_name: '',
        license_number: '',
        phone_number: '',
        email: '',
      });
    }
    setModalOpen(true);
    setError('');
    setSuccessMessage('');
  };

  const closeModal = () => {
    setModalOpen(false);
    setEditingDriver(null);
    setFormData({
      full_name: '',
      license_number: '',
      phone_number: '',
      email: '',
    });
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    setSuccessMessage('');

    const response = editingDriver
      ? await updateDriver(editingDriver.id, formData)
      : await createDriver(formData);

    if (response.error) {
      setError(response.error);
      setSubmitting(false);
    } else if (response.data) {
      // Handle vehicle assignment if specified
      if (formData.vehicle_id) {
        const { updateVehicle } = await import('@/lib/api/vehicles');
        const vehicleResponse = await updateVehicle(formData.vehicle_id, {
          driver_id: response.data.id,
        });
        
        if (vehicleResponse.error) {
          setError(`Driver saved but vehicle assignment failed: ${vehicleResponse.error}`);
          setSubmitting(false);
          void fetchDrivers();
          void fetchVehicles();
          return;
        }
      } else if (editingDriver) {
        // If vehicle_id is cleared, unassign any previously assigned vehicle
        const previousVehicle = vehicles.find(v => v.driver_name === editingDriver.full_name);
        if (previousVehicle) {
          const { updateVehicle } = await import('@/lib/api/vehicles');
          await updateVehicle(previousVehicle.id, { driver_id: undefined });
        }
      }
      
      setSuccessMessage(editingDriver ? 'Driver updated successfully' : 'Driver created successfully');
      closeModal();
      void fetchDrivers();
      void fetchVehicles();
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="text-center">
          <div className="spinner" style={{ margin: '0 auto' }}></div>
          <p style={{ marginTop: '20px' }}>Loading drivers...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1>Drivers</h1>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={() => openModal()} className="button-primary" style={{ width: 'auto' }}>
            Add Driver
          </button>
          <button onClick={() => router.push('/dashboard')} className="button-secondary" style={{ width: 'auto' }}>
            Back to Dashboard
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {successMessage && <div className="alert alert-success">{successMessage}</div>}

      {drivers.length === 0 ? (
        <div className="profile-card" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <span className="material-icons" style={{ fontSize: '64px', color: '#ccc', marginBottom: '20px' }}>
            person_off
          </span>
          <h2>No Drivers Found</h2>
          <p style={{ color: '#000', marginBottom: '20px' }}>Get started by adding your first driver</p>
          <button onClick={() => openModal()} className="button-primary" style={{ width: 'auto' }}>
            Add Driver
          </button>
        </div>
      ) : (
        <div style={{ marginTop: '30px', overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #000' }}>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>ID</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Name</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>License Number</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Phone</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Email</th>
                <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Avg Risk Score</th>
                <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Risk Level</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Status</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {drivers.map((driver) => {
                const getRiskLevelColor = (level: string) => {
                  switch (level) {
                    case 'Low': return '#4CAF50';
                    case 'Medium': return '#FF9800';
                    case 'High': return '#f44336';
                    default: return '#999';
                  }
                };

                return (
                  <tr key={driver.id} style={{ borderBottom: '1px solid #ddd' }}>
                    <td style={{ padding: '12px', color: '#000' }}>{driver.driver_id}</td>
                    <td style={{ padding: '12px', color: '#000' }}>{driver.full_name}</td>
                    <td style={{ padding: '12px', color: '#000' }}>{driver.license_number}</td>
                    <td style={{ padding: '12px', color: '#000' }}>{driver.phone_number}</td>
                    <td style={{ padding: '12px', color: '#000' }}>{driver.email || '—'}</td>
                    <td style={{ padding: '12px', textAlign: 'center', color: '#000', fontWeight: '600' }}>
                      {driver.average_risk_score !== null && driver.average_risk_score !== undefined 
                        ? driver.average_risk_score.toFixed(2) 
                        : '—'}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <span style={{
                        padding: '4px 12px',
                        borderRadius: '12px',
                        fontSize: '13px',
                        fontWeight: '600',
                        color: '#fff',
                        backgroundColor: getRiskLevelColor(driver.risk_level || 'N/A'),
                      }}>
                        {driver.risk_level || 'N/A'}
                      </span>
                    </td>
                    <td style={{ padding: '12px' }}>
                      <span className={driver.is_active ? 'badge badge-verified' : 'badge badge-unverified'}>
                        {driver.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td style={{ padding: '12px' }}>
                      <button
                        onClick={() => openModal(driver)}
                        className="button-secondary"
                        style={{ width: 'auto', padding: '6px 12px', fontSize: '14px' }}
                      >
                        Edit
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal */}
      {modalOpen && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 2000,
          }}
          onClick={closeModal}
        >
          <div 
            style={{
              backgroundColor: 'white',
              borderRadius: '8px',
              padding: '30px',
              maxWidth: '500px',
              width: '90%',
              maxHeight: '80vh',
              overflowY: 'auto',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2 style={{ marginTop: 0 }}>{editingDriver ? 'Edit Driver' : 'Add Driver'}</h2>
            
            {error && <div className="alert alert-error">{error}</div>}
            
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '15px' }}>
                <label className="label">Full Name *</label>
                <input
                  type="text"
                  className="input"
                  required
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                />
              </div>
              <div style={{ marginBottom: '15px' }}>
                <label className="label">License Number *</label>
                <input
                  type="text"
                  className="input"
                  required
                  value={formData.license_number}
                  onChange={(e) => setFormData({ ...formData, license_number: e.target.value })}
                />
              </div>
              <div style={{ marginBottom: '15px' }}>
                <label className="label">Phone Number *</label>
                <input
                  type="tel"
                  className="input"
                  required
                  placeholder="+260971234567"
                  value={formData.phone_number}
                  onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                />
              </div>
              <div style={{ marginBottom: '15px' }}>
                <label className="label">Email</label>
                <input
                  type="email"
                  className="input"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label className="label">Assign Vehicle</label>
                <select
                  className="input"
                  value={formData.vehicle_id || ''}
                  onChange={(e) => setFormData({ ...formData, vehicle_id: e.target.value || undefined })}
                >
                  <option value="">-- No Vehicle --</option>
                  {vehicles.map((vehicle) => (
                    <option key={vehicle.id} value={vehicle.id}>
                      {vehicle.registration_number} ({vehicle.vehicle_type})
                    </option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                <button
                  type="submit"
                  disabled={submitting}
                  className="button-primary"
                  style={{ flex: 1 }}
                >
                  {submitting ? (editingDriver ? 'Updating...' : 'Creating...') : (editingDriver ? 'Update Driver' : 'Create Driver')}
                </button>
                <button
                  type="button"
                  onClick={closeModal}
                  disabled={submitting}
                  className="button-secondary"
                  style={{ flex: 1 }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
