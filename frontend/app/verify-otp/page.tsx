'use client';

import { useState, FormEvent, useRef, KeyboardEvent, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { verifyOTP, resendOTP } from '@/lib/api/auth';
import { getFieldErrorMessage } from '@/lib/utils/errorMessages';

export default function VerifyOTPPage() {
  const router = useRouter();
  const [otp, setOtp] = useState(['', '', '', '', '', '', '', '']);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const [email] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('verification_email') || '';
    }
    return '';
  });

  useEffect(() => {
    if (!email) {
      router.push('/register');
    }
  }, [router, email]);

  if (!email) {
    return null;
  }

  const handleChange = (index: number, value: string) => {
    if (value.length > 1) return;
    if (!/^\d*$/.test(value)) return;

    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Auto-focus next input
    if (value && index < 7) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    const otpCode = otp.join('');

    if (otpCode.length !== 8) {
      setError(getFieldErrorMessage('otp', 'incomplete'));
      setLoading(false);
      return;
    }

    const response = await verifyOTP(email, otpCode);

    if (response.error) {
      setError(response.error);
      setLoading(false);
    } else {
      setSuccess('Email verified successfully! Redirecting to login...');
      localStorage.removeItem('verification_email');
      setTimeout(() => {
        router.push('/login');
      }, 1500);
    }
  };

  const handleResend = async () => {
    setError('');
    setSuccess('');
    setResending(true);

    const response = await resendOTP(email, 'signup');

    if (response.error) {
      setError(response.error);
    } else {
      setSuccess('A new verification code has been sent to your email.');
      // Clear the OTP inputs
      setOtp(['', '', '', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
    }
    setResending(false);
  };

  return (
    <div className="container">
      <div className="card">
        <h1>Verify Email</h1>
        <p>
          We&apos;ve sent an 8-digit code to <strong>{email}</strong>
        </p>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <form onSubmit={handleSubmit}>
          <div className="otp-input-group">
            {otp.map((digit, index) => (
              <input
                key={index}
                ref={(el) => {
                  inputRefs.current[index] = el;
                }}
                type="text"
                maxLength={1}
                className="otp-input"
                value={digit}
                onChange={(e) => handleChange(index, e.target.value)}
                onKeyDown={(e) => handleKeyDown(index, e)}
                autoFocus={index === 0}
              />
            ))}
          </div>

          <button type="submit" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner"></span>
                Verifying...
              </>
            ) : (
              'Verify Email'
            )}
          </button>
        </form>

        <p className="text-center mt-20">
          Didn&apos;t receive the code?{' '}
          <button
            type="button"
            className="link"
            onClick={handleResend}
            disabled={resending}
            style={{ 
              background: 'none', 
              border: 'none', 
              padding: 0,
              width: 'auto',
              display: 'inline'
            }}
          >
            {resending ? 'Sending...' : 'Resend Code'}
          </button>
        </p>
      </div>
    </div>
  );
}
