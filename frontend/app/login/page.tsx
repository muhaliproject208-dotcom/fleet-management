'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { login } from '@/lib/api/auth';
import { getFieldErrorMessage } from '@/lib/utils/errorMessages';

export default function LoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    
    if (!formData.email.trim()) {
      errors.email = getFieldErrorMessage('email', 'required');
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = getFieldErrorMessage('email', 'format');
    }
    
    if (!formData.password) {
      errors.password = getFieldErrorMessage('password', 'required');
    }
    
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setFieldErrors({});
    setLoading(true);

    if (!validateForm()) {
      setLoading(false);
      return;
    }

    const response = await login(formData);

    if (response.error) {
      // Check for field-specific errors from API
      if (response.fieldErrors) {
        setFieldErrors(response.fieldErrors);
      }
      setError(response.error);
      setLoading(false);
    } else {
      router.push('/dashboard');
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h1>Welcome Back</h1>
        <p>Sign in to your fleet management account</p>

        {error && !Object.keys(fieldErrors).length && (
          <div className="alert alert-error">{error}</div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              placeholder="you@company.com"
              value={formData.email}
              onChange={(e) => {
                setFormData({ ...formData, email: e.target.value });
                if (fieldErrors.email) {
                  setFieldErrors({ ...fieldErrors, email: '' });
                }
              }}
              className={fieldErrors.email ? 'input-error' : ''}
              required
            />
            {fieldErrors.email && (
              <span className="field-error">{fieldErrors.email}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type={showPassword ? 'text' : 'password'}
              id="password"
              placeholder="Enter your password"
              value={formData.password}
              onChange={(e) => {
                setFormData({ ...formData, password: e.target.value });
                if (fieldErrors.password) {
                  setFieldErrors({ ...fieldErrors, password: '' });
                }
              }}
              className={fieldErrors.password ? 'input-error' : ''}
              required
            />
            {fieldErrors.password && (
              <span className="field-error">{fieldErrors.password}</span>
            )}
            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword(!showPassword)}
              style={{
                background: 'none',
                border: 'none',
                padding: '4px 0',
                color: '#000',
                fontSize: '14px',
                marginTop: '4px',
              }}
            >
              {showPassword ? 'Hide Password' : 'Show Password'}
            </button>
          </div>

          <div className="text-right mb-20">
            <Link href="/password-reset" className="link">
              Forgot Password?
            </Link>
          </div>

          <button type="submit" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner"></span>
                Signing In...
              </>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <p className="text-center mt-20">
          Don&apos;t have an account?{' '}
          <Link href="/register" className="link">
            Create Account
          </Link>
        </p>
      </div>
    </div>
  );
}
