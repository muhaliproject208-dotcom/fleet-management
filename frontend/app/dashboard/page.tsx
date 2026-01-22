'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getProfile, logout, getCurrentUser, isAuthenticated, User } from '@/lib/api/auth';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    // Load profile on mount
    const fetchProfile = async () => {
      // Try to get cached user first
      const cachedUser = getCurrentUser();
      if (cachedUser) {
        setUser(cachedUser);
      }

      // Fetch fresh profile data
      const response = await getProfile();

      if (response.error) {
        setError(response.error);
        // If token expired, redirect to login
        if (response.error.includes('token') || response.error.includes('auth')) {
          await logout();
          router.push('/login');
        }
      } else if (response.data) {
        setUser(response.data);
        // Update cached user
        localStorage.setItem('user', JSON.stringify(response.data));
      }

      setLoading(false);
    };

    void fetchProfile();
  }, [router]);

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  if (loading) {
    return (
      <div className="container">
        <div className="text-center">
          <div className="spinner" style={{ margin: '0 auto' }}></div>
          <p style={{ marginTop: '20px' }}>Loading dashboard...</p>
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
          <h1>Dashboard</h1>
          <p>Welcome back, {user.first_name}!</p>
        </div>
        <button onClick={handleLogout} className="button-secondary" style={{ width: 'auto' }}>
          Logout
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="profile-card">
        <h2>Profile Information</h2>

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
      </div>

      {user.role === 'fleet_manager' && (
        <div className="profile-card" style={{ marginTop: '30px' }}>
          <h2>Fleet Manager Dashboard</h2>
          <p style={{ color: '#666' }}>
            Welcome to your Fleet Manager dashboard. Vehicle and fleet management features will be available here soon.
          </p>
        </div>
      )}

      {user.role === 'transport_supervisor' && (
        <div className="profile-card" style={{ marginTop: '30px' }}>
          <h2>Transport Supervisor Dashboard</h2>
          <p style={{ color: '#666' }}>
            Welcome to your Transport Supervisor dashboard. Trip monitoring and scheduling features will be available here soon.
          </p>
        </div>
      )}
    </div>
  );
}
