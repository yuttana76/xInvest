'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useSuppliers, useCreateSupplier } from '@/hooks/usePayment';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { BranchType } from '@/lib/api/payment';
import { Plus, Search, ArrowRight, Building2, X } from 'lucide-react';

export default function SuppliersPage() {
  const [q, setQ] = useState('');
  const [showModal, setShowModal] = useState(false);
  const { data: suppliers, isLoading, error } = useSuppliers(q ? { q } : undefined);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Suppliers</h1>
          <p className="text-sm text-gray-500 mt-1">Manage supplier master data and bank accounts</p>
        </div>
        <Button className="w-full sm:w-auto" onClick={() => setShowModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Supplier
        </Button>
      </div>

      <div className="relative max-w-sm">
        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <Input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search by name..."
          className="pl-9"
        />
      </div>

      {error && (
        <div className="p-8 text-center bg-red-50 dark:bg-red-900/10 rounded-xl border border-red-100 dark:border-red-900/20">
          <p className="text-red-600 dark:text-red-400">Error loading suppliers</p>
        </div>
      )}

      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500 uppercase font-semibold text-xs border-b border-gray-200 dark:border-gray-800">
              <tr>
                <th className="px-6 py-4">Name</th>
                <th className="px-6 py-4">Tax ID</th>
                <th className="px-6 py-4">Branch</th>
                <th className="px-6 py-4">Phone</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                  </td>
                </tr>
              ) : suppliers?.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500 italic">
                    <Building2 className="w-12 h-12 mx-auto mb-3 opacity-20" />
                    No suppliers found.
                  </td>
                </tr>
              ) : (
                suppliers?.map((s) => (
                  <tr key={s.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors">
                    <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">{s.name}</td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">{s.tax_id}</td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                      {s.branch_type === 'HQ' ? 'HQ' : `Branch ${s.branch_no}`}
                    </td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">{s.phone}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                          s.is_active
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                            : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
                        }`}
                      >
                        {s.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link href={`/payment/suppliers/${s.id}`}>
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

      {showModal && <AddSupplierModal onClose={() => setShowModal(false)} />}
    </div>
  );
}

function AddSupplierModal({ onClose }: { onClose: () => void }) {
  const createMutation = useCreateSupplier();
  const [name, setName] = useState('');
  const [taxId, setTaxId] = useState('');
  const [branchType, setBranchType] = useState<BranchType>('HQ');
  const [branchNo, setBranchNo] = useState('');
  const [address, setAddress] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [defaultWhtRate, setDefaultWhtRate] = useState('0');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(
      {
        name,
        tax_id: taxId,
        branch_type: branchType,
        branch_no: branchNo,
        address,
        phone,
        email,
        default_wht_rate: parseFloat(defaultWhtRate) || 0,
        is_active: true,
      },
      {
        onSuccess: () => onClose(),
        onError: () => alert('Failed to create supplier. Please check the fields and try again.'),
      }
    );
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 w-full max-w-lg shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold">Add Supplier</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Name <span className="text-red-500">*</span>
              </label>
              <Input value={name} onChange={(e) => setName(e.target.value)} required />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Tax ID <span className="text-red-500">*</span>
              </label>
              <Input value={taxId} onChange={(e) => setTaxId(e.target.value)} required />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Branch Type</label>
              <select
                value={branchType}
                onChange={(e) => setBranchType(e.target.value as BranchType)}
                className="flex h-11 w-full rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 outline-none transition-all"
              >
                <option value="HQ">HQ</option>
                <option value="BRANCH">Branch</option>
              </select>
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Branch No.</label>
              <Input value={branchNo} onChange={(e) => setBranchNo(e.target.value)} disabled={branchType === 'HQ'} />
            </div>
            <div className="space-y-1 sm:col-span-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Address</label>
              <Input value={address} onChange={(e) => setAddress(e.target.value)} />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Phone</label>
              <Input value={phone} onChange={(e) => setPhone(e.target.value)} />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
              <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Default WHT Rate (%)</label>
              <Input type="number" step="0.01" value={defaultWhtRate} onChange={(e) => setDefaultWhtRate(e.target.value)} />
            </div>
          </div>
          <div className="pt-2 flex gap-3">
            <Button type="submit" className="flex-1" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Saving...' : 'Save Supplier'}
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
