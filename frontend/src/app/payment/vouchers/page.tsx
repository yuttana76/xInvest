'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useVouchers } from '@/hooks/usePayment';
import { Button } from '@/components/Button';
import { VoucherStatus } from '@/lib/api/payment';
import { Plus, Receipt, ArrowRight, AlertTriangle } from 'lucide-react';

const STATUS_TABS: { value: VoucherStatus | ''; label: string }[] = [
  { value: '', label: 'All' },
  { value: 'DRAFT', label: 'Draft' },
  { value: 'PENDING_APPROVAL', label: 'Pending Approval' },
  { value: 'APPROVED', label: 'Approved' },
  { value: 'REJECTED', label: 'Rejected' },
  { value: 'RETURNED', label: 'Returned' },
  { value: 'PAID', label: 'Paid' },
];

const STATUS_STYLES: Record<VoucherStatus, string> = {
  DRAFT: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400',
  PENDING_APPROVAL: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
  APPROVED: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  REJECTED: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  RETURNED: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
  PAID: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
};

export default function VouchersPage() {
  const [statusFilter, setStatusFilter] = useState<VoucherStatus | ''>('');
  const { data: vouchers, isLoading, error } = useVouchers(
    statusFilter ? { status: statusFilter } : undefined
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Payment Vouchers</h1>
          <p className="text-sm text-gray-500 mt-1">Track vouchers from creation through approval to payment</p>
        </div>
        <Link href="/payment/vouchers/create">
          <Button className="w-full sm:w-auto">
            <Plus className="w-4 h-4 mr-2" />
            Create Voucher
          </Button>
        </Link>
      </div>

      <div className="flex flex-wrap gap-2">
        {STATUS_TABS.map((tab) => (
          <button
            key={tab.value}
            onClick={() => setStatusFilter(tab.value)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
              statusFilter === tab.value
                ? 'bg-primary/10 text-primary'
                : 'text-gray-500 hover:bg-gray-100 dark:hover:bg-white/5'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {error && (
        <div className="p-8 text-center bg-red-50 dark:bg-red-900/10 rounded-xl border border-red-100 dark:border-red-900/20">
          <p className="text-red-600 dark:text-red-400">Error loading vouchers</p>
        </div>
      )}

      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500 uppercase font-semibold text-xs border-b border-gray-200 dark:border-gray-800">
              <tr>
                <th className="px-6 py-4">PV Code</th>
                <th className="px-6 py-4">Supplier</th>
                <th className="px-6 py-4">Invoice Ref</th>
                <th className="px-6 py-4">Net Amount</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Flags</th>
                <th className="px-6 py-4">Created</th>
                <th className="px-6 py-4"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                  </td>
                </tr>
              ) : vouchers?.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-gray-500 italic">
                    <Receipt className="w-12 h-12 mx-auto mb-3 opacity-20" />
                    No vouchers found.
                  </td>
                </tr>
              ) : (
                vouchers?.map((v) => (
                  <tr key={v.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors">
                    <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">
                      {v.pv_code || `#${v.id}`}
                    </td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">{v.supplier_name}</td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">{v.invoice_no_ref || '-'}</td>
                    <td className="px-6 py-4 font-medium">{v.net_amount}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${STATUS_STYLES[v.status]}`}>
                        {v.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {v.validation_flags && v.validation_flags.length > 0 && (
                        <span className="inline-flex items-center gap-1 text-amber-600 dark:text-amber-400 text-xs font-semibold">
                          <AlertTriangle className="w-3.5 h-3.5" />
                          {v.validation_flags.length}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-gray-500 text-xs">
                      {new Date(v.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link href={`/payment/vouchers/${v.id}`}>
                        <Button variant="ghost" size="sm" className="text-primary hover:text-primary-dark">
                          Details
                          <ArrowRight className="w-3 h-3 ml-1.5" />
                        </Button>
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
