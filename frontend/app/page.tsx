'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/api/auth';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated()) {
      router.push('/dashboard');
    } else {
      router.push('/login');
    }
  }, [router]);

  return (
    <div className="container">
      <div className="text-center">
        <div className="spinner" style={{ margin: '0 auto' }}></div>
        <p style={{ marginTop: '20px' }}>Loading...</p>
      </div>
    </div>
  );
}
