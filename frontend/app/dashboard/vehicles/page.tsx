'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/api/auth';
import { getVehicles, createVehicle, updateVehicle, Vehicle, CreateVehicleData } from '@/lib/api/vehicles';
import { getDrivers, Driver } from '@/lib/api/drivers';
import { getFriendlyErrorMessage } from '@/lib/utils/errorMessages';

export default function VehiclesPage() {
  const router = useRouter();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null);
  const [formData, setFormData] = useState<CreateVehicleData>({
    registration_number: '',
    vehicle_type: '',
    driver_id: '',
  });
  const [submitting, setSubmitting] = useState(false);

  const fetchDrivers = useCallback(async () => {
    const response = await getDrivers({ is_active: true });
    if (response.data) {
      setDrivers(response.data.results || []);
    }
  }, []);

  const fetchVehicles = useCallback(async () => {
    const response = await getVehicles({ is_active: 'all' });

    if (response.error) {
      setError(getFriendlyErrorMessage(response.error));
    } else if (response.data) {
      setVehicles(response.data.results || []);
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
    }, 0);

    return () => clearTimeout(timer);
  }, [router, fetchVehicles, fetchDrivers]);

  const openModal = (vehicle?: Vehicle) => {
    if (vehicle) {
      setEditingVehicle(vehicle);
      setFormData({
        registration_number: vehicle.registration_number,
        vehicle_type: vehicle.vehicle_type,
        driver_id: '',
      });
    } else {
      setEditingVehicle(null);
      setFormData({
        registration_number: '',
        vehicle_type: '',
        driver_id: '',
      });
    }
    setModalOpen(true);
    setError('');
    setSuccessMessage('');
  };

  const closeModal = () => {
    setModalOpen(false);
    setEditingVehicle(null);
    setFormData({
      registration_number: '',
      vehicle_type: '',
      driver_id: '',
    });
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    setSuccessMessage('');

    const response = editingVehicle
      ? await updateVehicle(editingVehicle.id, formData)
      : await createVehicle(formData);

    if (response.error) {
      setError(getFriendlyErrorMessage(response.error));
      setSubmitting(false);
    } else if (response.data) {
      setSuccessMessage(editingVehicle ? 'Vehicle updated successfully' : 'Vehicle created successfully');
      closeModal();
      void fetchVehicles();
      void fetchDrivers();
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="text-center">
          <div className="spinner" style={{ margin: '0 auto' }}></div>
          <p style={{ marginTop: '20px' }}>Loading vehicles...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1>Vehicles</h1>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={() => openModal()} className="button-primary" style={{ width: 'auto' }}>
            Add Vehicle
          </button>
          <button onClick={() => router.push('/dashboard')} className="button-secondary" style={{ width: 'auto' }}>
            Back to Dashboard
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {successMessage && <div className="alert alert-success">{successMessage}</div>}

      {vehicles.length === 0 ? (
        <div className="profile-card" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <span className="material-icons" style={{ fontSize: '64px', color: '#ccc', marginBottom: '20px' }}>
            directions_car_off
          </span>
          <h2>No Vehicles Found</h2>
          <p style={{ color: '#000', marginBottom: '20px' }}>Get started by adding your first vehicle</p>
          <button onClick={() => openModal()} className="button-primary" style={{ width: 'auto' }}>
            Add Vehicle
          </button>
        </div>
      ) : (
        <div style={{ marginTop: '30px', overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #000' }}>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>ID</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Registration</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Type</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Driver</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Status</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {vehicles.map((vehicle) => (
                <tr key={vehicle.id} style={{ borderBottom: '1px solid #ddd' }}>
                  <td style={{ padding: '12px', color: '#000' }}>{vehicle.vehicle_id}</td>
                  <td style={{ padding: '12px', color: '#000' }}>{vehicle.registration_number}</td>
                  <td style={{ padding: '12px', color: '#000' }}>{vehicle.vehicle_type}</td>
                  <td style={{ padding: '12px', color: '#000' }}>{vehicle.driver_name || '—'}</td>
                  <td style={{ padding: '12px' }}>
                    <span className={vehicle.is_active ? 'badge badge-verified' : 'badge badge-unverified'}>
                      {vehicle.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <button
                      onClick={() => openModal(vehicle)}
                      className="button-secondary"
                      style={{ width: 'auto', padding: '6px 12px', fontSize: '14px' }}
                    >
                      Edit
                    </button>
                  </td>
                </tr>
              ))}
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
            <h2 style={{ marginTop: 0 }}>{editingVehicle ? 'Edit Vehicle' : 'Add Vehicle'}</h2>
            
            {error && <div className="alert alert-error">{error}</div>}
            
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '15px' }}>
                <label className="label">Registration Number *</label>
                <input
                  type="text"
                  className="input"
                  required
                  placeholder="ALB 9345"
                  value={formData.registration_number}
                  onChange={(e) => setFormData({ ...formData, registration_number: e.target.value })}
                />
              </div>
              <div style={{ marginBottom: '15px' }}>
                <label className="label">Vehicle Type *</label>
                <select
                  className="input"
                  required
                  value={formData.vehicle_type}
                  onChange={(e) => setFormData({ ...formData, vehicle_type: e.target.value })}
                >
                  <option value="">-- Select Vehicle Type --</option>
                  <option value="Truck">Truck</option>
                  <option value="Small Truck">Small Truck</option>
                  <option value="Big Bus">Big Bus</option>
                  <option value="Mini Bus">Mini Bus</option>
                  <option value="Car">Car</option>
                </select>
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label className="label">Assign Driver</label>
                <select
                  className="input"
                  value={formData.driver_id || ''}
                  onChange={(e) => setFormData({ ...formData, driver_id: e.target.value || undefined })}
                >
                  <option value="">-- No Driver --</option>
                  {drivers.map((driver) => (
                    <option key={driver.id} value={driver.id}>
                      {driver.full_name}
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
                  {submitting ? (editingVehicle ? 'Updating...' : 'Creating...') : (editingVehicle ? 'Update Vehicle' : 'Create Vehicle')}
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
