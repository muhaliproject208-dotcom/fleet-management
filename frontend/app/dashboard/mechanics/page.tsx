'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/api/auth';
import { getMechanics, createMechanic, updateMechanic, Mechanic, CreateMechanicData } from '@/lib/api/mechanics';

export default function MechanicsPage() {
  const router = useRouter();
  const [mechanics, setMechanics] = useState<Mechanic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingMechanic, setEditingMechanic] = useState<Mechanic | null>(null);
  const [formData, setFormData] = useState<CreateMechanicData>({
    full_name: '',
    specialization: '',
    phone_number: '',
  });
  const [submitting, setSubmitting] = useState(false);

  const fetchMechanics = useCallback(async () => {
    const response = await getMechanics({ is_active: 'all' });

    if (response.error) {
      setError(response.error);
    } else if (response.data) {
      setMechanics(response.data.results || []);
    }

    setLoading(false);
  }, []);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    const timer = setTimeout(() => {
      void fetchMechanics();
    }, 0);

    return () => clearTimeout(timer);
  }, [router, fetchMechanics]);

  const openModal = (mechanic?: Mechanic) => {
    if (mechanic) {
      setEditingMechanic(mechanic);
      setFormData({
        full_name: mechanic.full_name,
        specialization: mechanic.specialization,
        phone_number: mechanic.phone_number,
      });
    } else {
      setEditingMechanic(null);
      setFormData({
        full_name: '',
        specialization: '',
        phone_number: '',
      });
    }
    setModalOpen(true);
    setError('');
    setSuccessMessage('');
  };

  const closeModal = () => {
    setModalOpen(false);
    setEditingMechanic(null);
    setFormData({
      full_name: '',
      specialization: '',
      phone_number: '',
    });
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    setSuccessMessage('');

    const response = editingMechanic
      ? await updateMechanic(editingMechanic.id, formData)
      : await createMechanic(formData);

    if (response.error) {
      setError(response.error);
      setSubmitting(false);
    } else if (response.data) {
      setSuccessMessage(editingMechanic ? 'Mechanic updated successfully' : 'Mechanic created successfully');
      closeModal();
      void fetchMechanics();
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="text-center">
          <div className="spinner" style={{ margin: '0 auto' }}></div>
          <p style={{ marginTop: '20px' }}>Loading mechanics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1>Mechanics</h1>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={() => openModal()} className="button-primary" style={{ width: 'auto' }}>
            Add Mechanic
          </button>
          <button onClick={() => router.push('/dashboard')} className="button-secondary" style={{ width: 'auto' }}>
            Back to Dashboard
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {successMessage && <div className="alert alert-success">{successMessage}</div>}

      {mechanics.length === 0 ? (
        <div className="profile-card" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <span className="material-icons" style={{ fontSize: '64px', color: '#ccc', marginBottom: '20px' }}>
            build_circle
          </span>
          <h2>No Mechanics Found</h2>
          <p style={{ color: '#000', marginBottom: '20px' }}>Get started by adding your first mechanic</p>
          <button onClick={() => openModal()} className="button-primary" style={{ width: 'auto' }}>
            Add Mechanic
          </button>
        </div>
      ) : (
        <div style={{ marginTop: '30px', overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #000' }}>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>ID</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Name</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Specialization</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Phone</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Status</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {mechanics.map((mechanic) => (
                <tr key={mechanic.id} style={{ borderBottom: '1px solid #ddd' }}>
                  <td style={{ padding: '12px', color: '#000' }}>{mechanic.mechanic_id}</td>
                  <td style={{ padding: '12px', color: '#000' }}>{mechanic.full_name}</td>
                  <td style={{ padding: '12px', color: '#000' }}>{mechanic.specialization}</td>
                  <td style={{ padding: '12px', color: '#000' }}>{mechanic.phone_number}</td>
                  <td style={{ padding: '12px' }}>
                    <span className={mechanic.is_active ? 'badge badge-verified' : 'badge badge-unverified'}>
                      {mechanic.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <button
                      onClick={() => openModal(mechanic)}
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
            <h2 style={{ marginTop: 0 }}>{editingMechanic ? 'Edit Mechanic' : 'Add Mechanic'}</h2>
            
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
                <label className="label">Specialization *</label>
                <input
                  type="text"
                  className="input"
                  required
                  placeholder="General Mechanic"
                  value={formData.specialization}
                  onChange={(e) => setFormData({ ...formData, specialization: e.target.value })}
                />
              </div>
              <div style={{ marginBottom: '15px' }}>
                <label className="label">Phone Number *</label>
                <input
                  type="tel"
                  className="input"
                  required
                  placeholder="+260977654321"
                  value={formData.phone_number}
                  onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                />
              </div>

              <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                <button
                  type="submit"
                  disabled={submitting}
                  className="button-primary"
                  style={{ flex: 1 }}
                >
                  {submitting ? (editingMechanic ? 'Updating...' : 'Creating...') : (editingMechanic ? 'Update Mechanic' : 'Create Mechanic')}
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
