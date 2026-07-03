'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function MarketingPage() {
  const router = useRouter();
  useEffect(() => {
    // router.push('/marketing/dashboard');
    router.push('/workflow/my-requests');
  }, [router]);
  return null;
}
