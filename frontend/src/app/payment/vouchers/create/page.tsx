'use client';

import React, { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  useDocuments,
  useSuppliers,
  useSupplier,
  useCreateVoucher,
} from '@/hooks/usePayment';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { CreateVoucherLineInput } from '@/lib/api/payment';
import { ChevronLeft, Sparkles, Plus, Trash2, CheckCircle2 } from 'lucide-react';

const emptyLine = (): CreateVoucherLineInput => ({
  description: '',
  department: '',
  amount: 0,
  vat_rate: 0,
  wht_rate: 0,
});

export default function CreateVoucherPage() {
  const router = useRouter();
  const createMutation = useCreateVoucher();

  const { data: documents } = useDocuments();
  const { data: suppliers } = useSuppliers();

  const [selectedDocId, setSelectedDocId] = useState('');
  const [supplierId, setSupplierId] = useState('');
  const [payeeBankAccountId, setPayeeBankAccountId] = useState('');
  const [invoiceNoRef, setInvoiceNoRef] = useState('');
  const [invoiceDate, setInvoiceDate] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [isFixedAsset, setIsFixedAsset] = useState(false);
  const [lines, setLines] = useState<CreateVoucherLineInput[]>([emptyLine()]);

  const { data: selectedSupplier } = useSupplier(supplierId ? parseInt(supplierId) : 0);

  const eligibleDocuments = useMemo(
    () => documents?.filter((d) => d.extraction_status === 'SUCCESS' || d.extraction_status === 'NEEDS_REVIEW'),
    [documents]
  );

  const selectedDoc = useMemo(
    () => documents?.find((d) => String(d.id) === selectedDocId),
    [documents, selectedDocId]
  );

  const handlePrefillFromDocument = () => {
    if (!selectedDoc || !selectedDoc.extracted_data) return;
    const data = selectedDoc.extracted_data;

    if (selectedDoc.supplier_guess) {
      setSupplierId(String(selectedDoc.supplier_guess));
    }
    if (data.invoice_no) setInvoiceNoRef(data.invoice_no);
    if (data.invoice_date) setInvoiceDate(data.invoice_date);
    if (data.due_date) setDueDate(data.due_date);

    if (data.line_items && data.line_items.length > 0) {
      setLines(
        data.line_items.map((item) => ({
          description: item.description,
          department: '',
          amount: item.amount,
          vat_rate: item.vat_rate ?? 0,
          wht_rate: item.wht_rate ?? 0,
        }))
      );
    }
  };

  const updateLine = (idx: number, field: keyof CreateVoucherLineInput, value: string) => {
    setLines((prev) =>
      prev.map((line, i) => {
        if (i !== idx) return line;
        if (field === 'description' || field === 'department') {
          return { ...line, [field]: value };
        }
        return { ...line, [field]: parseFloat(value) || 0 };
      })
    );
  };

  const addLine = () => setLines((prev) => [...prev, emptyLine()]);
  const removeLine = (idx: number) => setLines((prev) => prev.filter((_, i) => i !== idx));

  const totals = useMemo(() => {
    const subtotal = lines.reduce((sum, l) => sum + (Number(l.amount) || 0), 0);
    const vat = lines.reduce((sum, l) => sum + ((Number(l.amount) || 0) * (Number(l.vat_rate) || 0)) / 100, 0);
    const wht = lines.reduce((sum, l) => sum + ((Number(l.amount) || 0) * (Number(l.wht_rate) || 0)) / 100, 0);
    return { subtotal, vat, wht, net: subtotal + vat - wht };
  }, [lines]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!supplierId || !payeeBankAccountId || lines.length === 0) return;

    createMutation.mutate(
      {
        supplier: parseInt(supplierId),
        payee_bank_account: parseInt(payeeBankAccountId),
        source_document: selectedDocId ? parseInt(selectedDocId) : undefined,
        is_fixed_asset: isFixedAsset,
        invoice_no_ref: invoiceNoRef,
        invoice_date: invoiceDate || undefined,
        due_date: dueDate || undefined,
        lines,
      },
      {
        onSuccess: (voucher) => {
          router.push(`/payment/vouchers/${voucher.id}`);
        },
        onError: (err) => {
          console.error('Failed to create voucher:', err);
          alert('Error creating voucher. Please check the fields and try again.');
        },
      }
    );
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center space-x-2">
        <Link href="/payment/vouchers">
          <Button variant="ghost" size="icon" className="rounded-full">
            <ChevronLeft className="w-5 h-5" />
          </Button>
        </Link>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Create Payment Voucher</h1>
      </div>

      {/* AI Review Step */}
      <div className="bg-gradient-to-br from-primary/5 to-transparent rounded-2xl border-2 border-primary/20 p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-5 h-5 text-primary" />
          <h2 className="text-lg font-bold">Review AI Extraction</h2>
        </div>
        <p className="text-sm text-gray-500 mb-4">
          Pick a processed invoice/quotation document to prefill the fields below, then review and edit
          before submitting.
        </p>
        <div className="flex flex-col sm:flex-row gap-3">
          <select
            value={selectedDocId}
            onChange={(e) => setSelectedDocId(e.target.value)}
            className="flex-1 h-11 rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 outline-none transition-all"
          >
            <option value="">-- Select a processed document --</option>
            {eligibleDocuments?.map((d) => (
              <option key={d.id} value={d.id}>
                {d.doc_type} #{d.id} — {d.file.split('/').pop()} ({d.extraction_status})
              </option>
            ))}
          </select>
          <Button type="button" onClick={handlePrefillFromDocument} disabled={!selectedDoc}>
            <CheckCircle2 className="w-4 h-4 mr-2" />
            Apply to Form
          </Button>
        </div>

        {selectedDoc?.extracted_data?.confidence != null && (
          <p className="text-xs text-gray-500 mt-3">
            AI confidence: <strong>{(selectedDoc.extracted_data.confidence * 100).toFixed(0)}%</strong>
            {selectedDoc.extracted_data.notes && ` — ${selectedDoc.extracted_data.notes}`}
          </p>
        )}
      </div>

      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 md:p-8 shadow-sm">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Supplier <span className="text-red-500">*</span>
              </label>
              <select
                value={supplierId}
                onChange={(e) => {
                  setSupplierId(e.target.value);
                  setPayeeBankAccountId('');
                }}
                required
                className="flex h-11 w-full rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 outline-none transition-all"
              >
                <option value="">Select Supplier</option>
                {suppliers?.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Payee Bank Account <span className="text-red-500">*</span>
              </label>
              <select
                value={payeeBankAccountId}
                onChange={(e) => setPayeeBankAccountId(e.target.value)}
                required
                disabled={!supplierId}
                className="flex h-11 w-full rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 outline-none transition-all"
              >
                <option value="">Select Bank Account</option>
                {selectedSupplier?.bank_accounts?.map((acc) => (
                  <option key={acc.id} value={acc.id}>
                    {acc.bank_name} — {acc.account_no} {acc.is_current ? '(Current)' : ''}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Invoice No. Ref</label>
              <Input value={invoiceNoRef} onChange={(e) => setInvoiceNoRef(e.target.value)} />
            </div>

            <div />

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Invoice Date</label>
              <input
                type="date"
                value={invoiceDate}
                onChange={(e) => setInvoiceDate(e.target.value)}
                className="flex h-11 w-full rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 outline-none transition-all"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Due Date</label>
              <input
                type="date"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                className="flex h-11 w-full rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 outline-none transition-all"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="isFixedAsset"
              checked={isFixedAsset}
              onChange={(e) => setIsFixedAsset(e.target.checked)}
              className="h-4 w-4 rounded border-gray-300"
            />
            <label htmlFor="isFixedAsset" className="text-sm text-gray-700 dark:text-gray-300">
              This purchase is a fixed asset
            </label>
          </div>

          {/* Lines */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Lines <span className="text-red-500">*</span>
              </label>
              <Button type="button" variant="outline" size="sm" onClick={addLine}>
                <Plus className="w-3.5 h-3.5 mr-1.5" />
                Add Line
              </Button>
            </div>

            <div className="space-y-3">
              {lines.map((line, idx) => (
                <div
                  key={idx}
                  className="grid grid-cols-1 sm:grid-cols-12 gap-2 items-center p-3 rounded-xl border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/30"
                >
                  <div className="sm:col-span-4">
                    <Input
                      placeholder="Description"
                      value={line.description}
                      onChange={(e) => updateLine(idx, 'description', e.target.value)}
                      required
                    />
                  </div>
                  <div className="sm:col-span-2">
                    <Input
                      placeholder="Department"
                      value={line.department}
                      onChange={(e) => updateLine(idx, 'department', e.target.value)}
                    />
                  </div>
                  <div className="sm:col-span-2">
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="Amount"
                      value={line.amount}
                      onChange={(e) => updateLine(idx, 'amount', e.target.value)}
                      required
                    />
                  </div>
                  <div className="sm:col-span-1">
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="VAT %"
                      value={line.vat_rate}
                      onChange={(e) => updateLine(idx, 'vat_rate', e.target.value)}
                    />
                  </div>
                  <div className="sm:col-span-2">
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="WHT %"
                      value={line.wht_rate}
                      onChange={(e) => updateLine(idx, 'wht_rate', e.target.value)}
                    />
                  </div>
                  <div className="sm:col-span-1 flex justify-end">
                    <button
                      type="button"
                      onClick={() => removeLine(idx)}
                      disabled={lines.length === 1}
                      className="p-2 text-gray-400 hover:text-red-500 disabled:opacity-30 disabled:pointer-events-none"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-end">
              <div className="w-full sm:w-64 space-y-1 text-sm">
                <div className="flex justify-between text-gray-500">
                  <span>Subtotal</span>
                  <span>{totals.subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-gray-500">
                  <span>VAT</span>
                  <span>{totals.vat.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-gray-500">
                  <span>WHT</span>
                  <span>-{totals.wht.toFixed(2)}</span>
                </div>
                <div className="flex justify-between font-bold text-gray-900 dark:text-white pt-1 border-t border-gray-200 dark:border-gray-800">
                  <span>Net Total</span>
                  <span>{totals.net.toFixed(2)}</span>
                </div>
                <p className="text-xs text-gray-400 italic">Server recalculates exact totals on submit.</p>
              </div>
            </div>
          </div>

          <div className="pt-4 flex gap-3">
            <Button type="submit" className="flex-1" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Submitting...' : 'Create Voucher'}
            </Button>
            <Link href="/payment/vouchers" className="flex-1">
              <Button type="button" variant="outline" className="w-full">
                Cancel
              </Button>
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
