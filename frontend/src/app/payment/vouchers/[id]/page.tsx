'use client';

import React, { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useVoucher, useMarkPaid, useDownloadVoucherPdf } from '@/hooks/usePayment';
import { useRequestDetail, useWaitingApproval } from '@/hooks/useWorkflow';
import { useAuth } from '@/hooks/useAuth';
import { ActionPanel } from '@/components/workflow/ActionPanel';
import { WorkflowProgress } from '@/components/workflow/WorkflowProgress';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { VoucherStatus } from '@/lib/api/payment';
import { ChevronLeft, AlertTriangle, Download, Banknote } from 'lucide-react';

const STATUS_STYLES: Record<VoucherStatus, string> = {
  DRAFT: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400',
  PENDING_APPROVAL: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
  APPROVED: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  REJECTED: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  RETURNED: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
  PAID: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
};

const FLAG_SEVERITY_STYLES: Record<string, string> = {
  ERROR: 'bg-red-50 border-red-200 text-red-700 dark:bg-red-950/20 dark:border-red-900 dark:text-red-400',
  WARNING: 'bg-amber-50 border-amber-200 text-amber-700 dark:bg-amber-950/20 dark:border-amber-900 dark:text-amber-400',
  INFO: 'bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-950/20 dark:border-blue-900 dark:text-blue-400',
};

export default function VoucherDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const voucherId = parseInt(id as string);
  const { user } = useAuth();

  const { data: voucher, isLoading, error } = useVoucher(voucherId);
  const { data: request } = useRequestDetail(voucher?.request ?? 0);
  const { data: waitingList } = useWaitingApproval();
  const markPaidMutation = useMarkPaid();
  const downloadMutation = useDownloadVoucherPdf();

  const [payBank, setPayBank] = useState('');
  const [chequeNo, setChequeNo] = useState('');
  const [chequeDate, setChequeDate] = useState('');

  const isApprover = request ? waitingList?.some((r) => r.id === request.id) : false;
  const isCreator = request?.creator_username?.toLowerCase().trim() === user?.username?.toLowerCase().trim();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  if (error || !voucher) {
    return (
      <div className="p-8 text-center bg-red-50 dark:bg-red-900/10 rounded-xl">
        <p className="text-red-600">Voucher not found or an error occurred</p>
        <Button variant="outline" className="mt-4" onClick={() => router.back()}>
          Go back
        </Button>
      </div>
    );
  }

  const canMarkPaid = voucher.status === 'APPROVED' && voucher.request_status === 'APPROVED';

  const handleMarkPaid = (e: React.FormEvent) => {
    e.preventDefault();
    markPaidMutation.mutate(
      { id: voucherId, data: { pay_bank: payBank, cheque_no: chequeNo, cheque_date: chequeDate } },
      {
        onError: (err) => {
          console.error(err);
          alert('Failed to mark as paid. Please verify the voucher and request are both Approved.');
        },
      }
    );
  };

  const handleDownloadPdf = () => {
    downloadMutation.mutate({ id: voucherId, pvCode: voucher.pv_code });
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ChevronLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-2xl font-bold">
            {voucher.pv_code || `Voucher #${voucher.id}`}
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-semibold ${STATUS_STYLES[voucher.status]}`}>
            {voucher.status.replace('_', ' ')}
          </span>
          <Button variant="outline" size="sm" onClick={handleDownloadPdf} disabled={downloadMutation.isPending}>
            <Download className="w-3.5 h-3.5 mr-1.5" />
            {downloadMutation.isPending ? 'Downloading...' : 'Download PDF'}
          </Button>
        </div>
      </div>

      {voucher.validation_flags && voucher.validation_flags.length > 0 && (
        <div className="space-y-2">
          {voucher.validation_flags.map((flag, idx) => (
            <div
              key={idx}
              className={`flex items-start gap-2 p-3 rounded-xl border text-sm ${
                FLAG_SEVERITY_STYLES[flag.severity] || FLAG_SEVERITY_STYLES.WARNING
              }`}
            >
              <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold">{flag.code}: </span>
                {flag.message}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 shadow-sm">
            <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-4">
              Voucher Details
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <InfoItem label="Supplier" value={voucher.supplier_name} />
              <InfoItem label="Invoice Ref" value={voucher.invoice_no_ref || '-'} />
              <InfoItem label="Invoice Date" value={voucher.invoice_date || '-'} />
              <InfoItem label="Due Date" value={voucher.due_date || '-'} />
              <InfoItem label="Fixed Asset" value={voucher.is_fixed_asset ? 'Yes' : 'No'} />
              <InfoItem label="Request Status" value={voucher.request_status} />
            </div>

            <div className="mt-6 overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500 uppercase font-semibold text-xs border-b border-gray-200 dark:border-gray-800">
                  <tr>
                    <th className="px-4 py-3 text-left">Description</th>
                    <th className="px-4 py-3 text-left">Department</th>
                    <th className="px-4 py-3 text-right">Amount</th>
                    <th className="px-4 py-3 text-right">VAT</th>
                    <th className="px-4 py-3 text-right">WHT</th>
                    <th className="px-4 py-3 text-right">Net</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {voucher.lines.map((line) => (
                    <tr key={line.id}>
                      <td className="px-4 py-3">{line.description}</td>
                      <td className="px-4 py-3 text-gray-500">{line.department || '-'}</td>
                      <td className="px-4 py-3 text-right">{line.amount}</td>
                      <td className="px-4 py-3 text-right">{line.vat_amount}</td>
                      <td className="px-4 py-3 text-right">{line.wht_amount}</td>
                      <td className="px-4 py-3 text-right font-medium">{line.net_amount}</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="border-t-2 border-gray-200 dark:border-gray-800 font-bold">
                    <td className="px-4 py-3" colSpan={2}>Total</td>
                    <td className="px-4 py-3 text-right">{voucher.subtotal}</td>
                    <td className="px-4 py-3 text-right">{voucher.vat_amount}</td>
                    <td className="px-4 py-3 text-right">{voucher.wht_amount}</td>
                    <td className="px-4 py-3 text-right">{voucher.net_amount}</td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          {/* Approval Actions — delegated to the workflow engine via the underlying request */}
          {request && ((isApprover && request.status === 'PENDING') || (isCreator && request.status === 'APPROVED')) && (
            <ActionPanel requestId={request.id} status={request.status} />
          )}

          {/* Mark Paid */}
          {canMarkPaid && (
            <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 shadow-sm">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <Banknote className="w-5 h-5 text-emerald-600" />
                Mark as Paid
              </h3>
              <form onSubmit={handleMarkPaid} className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Pay Bank</label>
                  <Input value={payBank} onChange={(e) => setPayBank(e.target.value)} required />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Cheque No.</label>
                  <Input value={chequeNo} onChange={(e) => setChequeNo(e.target.value)} required />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Cheque Date</label>
                  <input
                    type="date"
                    value={chequeDate}
                    onChange={(e) => setChequeDate(e.target.value)}
                    required
                    className="flex h-11 w-full rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                  />
                </div>
                <Button type="submit" className="sm:col-span-3" disabled={markPaidMutation.isPending}>
                  {markPaidMutation.isPending ? 'Saving...' : 'Confirm Payment'}
                </Button>
              </form>
            </div>
          )}

          {voucher.status === 'PAID' && (
            <div className="bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900 rounded-2xl p-6 text-sm text-emerald-700 dark:text-emerald-400">
              Paid on {voucher.paid_at ? new Date(voucher.paid_at).toLocaleString() : '-'} via {voucher.pay_bank}
              {voucher.cheque_no && ` (Cheque ${voucher.cheque_no})`}
            </div>
          )}
        </div>

        <div className="space-y-6">
          {request && (
            <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 shadow-sm">
              <h2 className="text-sm font-bold uppercase tracking-wider text-gray-500 mb-8 font-mono pb-4 border-b border-gray-100 dark:border-gray-800">
                Approval Progress
              </h2>
              <WorkflowProgress request={request} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-50 dark:bg-gray-800/50 p-3 rounded-xl border border-gray-100 dark:border-gray-800">
      <span className="text-xs text-gray-500 block mb-1">{label}</span>
      <span className="text-sm font-medium">{value}</span>
    </div>
  );
}
