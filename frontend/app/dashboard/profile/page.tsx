'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getProfile, getCurrentUser, isAuthenticated, User, logout } from '@/lib/api/auth';

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    const fetchProfile = async () => {
      const cachedUser = getCurrentUser();
      if (cachedUser) {
        setUser(cachedUser);
        setFirstName(cachedUser.first_name || '');
        setLastName(cachedUser.last_name || '');
        setPhoneNumber(cachedUser.phone_number || '');
      }

      const response = await getProfile();

      if (response.error) {
        setError(response.error);
        if (response.error.includes('token') || response.error.includes('auth')) {
          await logout();
          router.push('/login');
        }
      } else if (response.data) {
        setUser(response.data);
        setFirstName(response.data.first_name || '');
        setLastName(response.data.last_name || '');
        setPhoneNumber(response.data.phone_number || '');
        localStorage.setItem('user', JSON.stringify(response.data));
      }

      setLoading(false);
    };

    void fetchProfile();
  }, [router]);

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccessMessage('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/profile/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          phone_number: phoneNumber,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to update profile');
      }

      setUser(data);
      localStorage.setItem('user', JSON.stringify(data));
      setSuccessMessage('Profile updated successfully');
      setIsEditing(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    if (user) {
      setFirstName(user.first_name || '');
      setLastName(user.last_name || '');
      setPhoneNumber(user.phone_number || '');
    }
    setIsEditing(false);
    setError('');
  };

  if (loading) {
    return (
      <div className="container">
        <div className="text-center">
          <div className="spinner" style={{ margin: '0 auto' }}></div>
          <p style={{ marginTop: '20px' }}>Loading profile...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const getRoleName = (role: string) => {
    switch (role) {
      case 'fleet_manager':
        return 'Fleet Manager';
      case 'transport_supervisor':
        return 'Transport Supervisor';
      case 'superuser':
        return 'Super User';
      default:
        return role;
    }
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1>View Profile</h1>
        </div>
        <button onClick={() => router.push('/dashboard')} className="button-secondary" style={{ width: 'auto' }}>
          Back to Dashboard
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {successMessage && <div className="alert alert-success">{successMessage}</div>}

      <div className="profile-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>Profile Information</h2>
          {!isEditing && (
            <button
              onClick={() => setIsEditing(true)}
              className="button-secondary"
              style={{ width: 'auto', padding: '8px 16px' }}
            >
              Edit Profile
            </button>
          )}
        </div>

        {isEditing ? (
          <>
            <div className="profile-row">
              <span className="profile-label">First Name</span>
              <input
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="input"
                style={{ maxWidth: '300px' }}
              />
            </div>

            <div className="profile-row">
              <span className="profile-label">Last Name</span>
              <input
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="input"
                style={{ maxWidth: '300px' }}
              />
            </div>

            <div className="profile-row">
              <span className="profile-label">Phone Number</span>
              <input
                type="tel"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                className="input"
                style={{ maxWidth: '300px' }}
              />
            </div>

            <div className="profile-row">
              <span className="profile-label">Email</span>
              <span className="profile-value" style={{ color: '#666' }}>
                {user.email} (Cannot be changed here)
              </span>
            </div>

            <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
              <button
                onClick={handleSave}
                disabled={saving}
                className="button-primary"
                style={{ width: 'auto', padding: '10px 20px' }}
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
              <button
                onClick={handleCancel}
                disabled={saving}
                className="button-secondary"
                style={{ width: 'auto', padding: '10px 20px' }}
              >
                Cancel
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="profile-row">
              <span className="profile-label">Full Name</span>
              <span className="profile-value">{user.full_name}</span>
            </div>

            <div className="profile-row">
              <span className="profile-label">Email</span>
              <span className="profile-value">{user.email}</span>
            </div>

            <div className="profile-row">
              <span className="profile-label">Role</span>
              <span className="profile-value">{getRoleName(user.role)}</span>
            </div>

            {user.phone_number && (
              <div className="profile-row">
                <span className="profile-label">Phone</span>
                <span className="profile-value">{user.phone_number}</span>
              </div>
            )}

            <div className="profile-row">
              <span className="profile-label">Email Verified</span>
              <span className="profile-value">
                <span className={user.email_verified ? 'badge badge-verified' : 'badge badge-unverified'}>
                  {user.email_verified ? 'Verified' : 'Not Verified'}
                </span>
              </span>
            </div>

            <div className="profile-row">
              <span className="profile-label">Account Status</span>
              <span className="profile-value">
                <span className={user.is_active ? 'badge badge-verified' : 'badge badge-unverified'}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </span>
              </span>
            </div>

            <div className="profile-row">
              <span className="profile-label">User ID</span>
              <span className="profile-value" style={{ fontSize: '12px', color: '#666' }}>
                {user.id}
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
