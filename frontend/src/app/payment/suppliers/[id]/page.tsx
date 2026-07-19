'use client';

import React, { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useSupplier, useAddBankAccount, useSetCurrentBankAccount } from '@/hooks/usePayment';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { ChevronLeft, Landmark, CheckCircle2, Plus, X } from 'lucide-react';

export default function SupplierDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const supplierId = parseInt(id as string);
  const [showAddBank, setShowAddBank] = useState(false);

  const { data: supplier, isLoading, error } = useSupplier(supplierId);
  const setCurrentMutation = useSetCurrentBankAccount();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  if (error || !supplier) {
    return (
      <div className="p-8 text-center bg-red-50 dark:bg-red-900/10 rounded-xl">
        <p className="text-red-600">Supplier not found or an error occurred</p>
        <Button variant="outline" className="mt-4" onClick={() => router.back()}>
          Go back
        </Button>
      </div>
    );
  }

  const handleSetCurrent = (bankId: number) => {
    setCurrentMutation.mutate({ supplierId, bankId });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center space-x-2">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ChevronLeft className="w-5 h-5" />
        </Button>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{supplier.name}</h1>
      </div>

      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 shadow-sm">
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-4">
          Supplier Details
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <InfoItem label="Tax ID" value={supplier.tax_id} />
          <InfoItem label="Branch" value={supplier.branch_type === 'HQ' ? 'HQ' : `Branch ${supplier.branch_no}`} />
          <InfoItem
            label="Status"
            value={supplier.is_active ? 'Active' : 'Inactive'}
          />
          <InfoItem label="Phone" value={supplier.phone || '-'} />
          <InfoItem label="Email" value={supplier.email || '-'} />
          <InfoItem label="Default WHT Rate" value={`${supplier.default_wht_rate}%`} />
          <div className="sm:col-span-3">
            <InfoItem label="Address" value={supplier.address || '-'} />
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 flex items-center gap-1.5">
            <Landmark className="w-4 h-4" /> Bank Accounts
          </h3>
          <Button size="sm" onClick={() => setShowAddBank(true)}>
            <Plus className="w-3.5 h-3.5 mr-1.5" />
            Add Bank Account
          </Button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500 uppercase font-semibold text-xs border-b border-gray-200 dark:border-gray-800">
              <tr>
                <th className="px-4 py-3">Bank</th>
                <th className="px-4 py-3">Branch</th>
                <th className="px-4 py-3">Account No.</th>
                <th className="px-4 py-3">Account Name</th>
                <th className="px-4 py-3">Current</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {supplier.bank_accounts?.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-500 italic">
                    No bank accounts registered.
                  </td>
                </tr>
              ) : (
                supplier.bank_accounts?.map((acc) => (
                  <tr key={acc.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/30">
                    <td className="px-4 py-3">{acc.bank_name}</td>
                    <td className="px-4 py-3 text-gray-500">{acc.branch}</td>
                    <td className="px-4 py-3 font-mono text-xs">{acc.account_no}</td>
                    <td className="px-4 py-3">{acc.account_name}</td>
                    <td className="px-4 py-3">
                      {acc.is_current ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                          <CheckCircle2 className="w-3 h-3" /> Current
                        </span>
                      ) : (
                        <span className="text-xs text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      {!acc.is_current && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleSetCurrent(acc.id)}
                          disabled={setCurrentMutation.isPending}
                        >
                          Set Current
                        </Button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showAddBank && (
        <AddBankAccountModal supplierId={supplierId} onClose={() => setShowAddBank(false)} />
      )}
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

function AddBankAccountModal({ supplierId, onClose }: { supplierId: number; onClose: () => void }) {
  const addMutation = useAddBankAccount();
  const [bankName, setBankName] = useState('');
  const [branch, setBranch] = useState('');
  const [accountNo, setAccountNo] = useState('');
  const [accountName, setAccountName] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    addMutation.mutate(
      {
        supplierId,
        data: { bank_name: bankName, branch, account_no: accountNo, account_name: accountName },
      },
      {
        onSuccess: () => onClose(),
        onError: () => alert('Failed to add bank account. Please try again.'),
      }
    );
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 w-full max-w-md shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold">Add Bank Account</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Bank Name <span className="text-red-500">*</span>
            </label>
            <Input value={bankName} onChange={(e) => setBankName(e.target.value)} required />
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Branch</label>
            <Input value={branch} onChange={(e) => setBranch(e.target.value)} />
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Account No. <span className="text-red-500">*</span>
            </label>
            <Input value={accountNo} onChange={(e) => setAccountNo(e.target.value)} required />
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Account Name <span className="text-red-500">*</span>
            </label>
            <Input value={accountName} onChange={(e) => setAccountName(e.target.value)} required />
          </div>
          <div className="pt-2 flex gap-3">
            <Button type="submit" className="flex-1" disabled={addMutation.isPending}>
              {addMutation.isPending ? 'Saving...' : 'Save'}
            </Button>
            <Button type="button" variant="outline" className="flex-1" onClick={onClose}>
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
