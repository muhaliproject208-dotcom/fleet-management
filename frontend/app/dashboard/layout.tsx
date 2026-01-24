'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { isAuthenticated } from '@/lib/api/auth';
import Navbar from '../components/Navbar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Check authentication on mount and route changes
    if (!isAuthenticated()) {
      router.push('/login');
    }
  }, [router, pathname]);

  // Don't show navbar if not authenticated
  if (!isAuthenticated()) {
    return null;
  }

  return (
    <>
      <Navbar />
      <main>{children}</main>
    </>
  );
}
