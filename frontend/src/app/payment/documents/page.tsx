'use client';

import React, { useState } from 'react';
import {
  useDocuments,
  useUploadDocument,
  useReprocessDocument,
  useSuppliers,
} from '@/hooks/usePayment';
import { FileUpload } from '@/components/workflow/FileUpload';
import { Button } from '@/components/Button';
import { DocType, ExtractionStatus, SourceDocument } from '@/lib/api/payment';
import { RefreshCw, FileText, ChevronDown, ChevronUp, Info } from 'lucide-react';

const STATUS_STYLES: Record<ExtractionStatus, string> = {
  PENDING: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400',
  PROCESSING: 'bg-blue-100 text-blue-700 dark:bg-blue-950/40 dark:text-blue-400',
  SUCCESS: 'bg-green-100 text-green-700 dark:bg-green-950/40 dark:text-green-400',
  FAILED: 'bg-red-100 text-red-700 dark:bg-red-950/40 dark:text-red-400',
  NEEDS_REVIEW: 'bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400',
};

export default function DocumentsPage() {
  const [docTypeFilter, setDocTypeFilter] = useState<DocType | ''>('');
  const [statusFilter, setStatusFilter] = useState<ExtractionStatus | ''>('');
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const { data: documents, isLoading, error } = useDocuments({
    doc_type: docTypeFilter || undefined,
    extraction_status: statusFilter || undefined,
  });
  const reprocessMutation = useReprocessDocument();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Documents</h1>
        <p className="text-sm text-gray-500 mt-1">
          Upload supplier quotations and invoices for AI-assisted extraction
        </p>
      </div>

      <UploadForm />

      <div className="flex flex-wrap gap-3">
        <select
          value={docTypeFilter}
          onChange={(e) => setDocTypeFilter(e.target.value as DocType | '')}
          className="h-10 rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-3 text-sm outline-none"
        >
          <option value="">All Types</option>
          <option value="QUOTATION">Quotation</option>
          <option value="INVOICE">Invoice</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as ExtractionStatus | '')}
          className="h-10 rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-3 text-sm outline-none"
        >
          <option value="">All Statuses</option>
          <option value="PENDING">Pending</option>
          <option value="PROCESSING">Processing</option>
          <option value="SUCCESS">Success</option>
          <option value="FAILED">Failed</option>
          <option value="NEEDS_REVIEW">Needs Review</option>
        </select>
      </div>

      {error && (
        <div className="p-8 text-center bg-red-50 dark:bg-red-900/10 rounded-xl border border-red-100 dark:border-red-900/20">
          <p className="text-red-600 dark:text-red-400">Error loading documents</p>
        </div>
      )}

      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500 uppercase font-semibold text-xs border-b border-gray-200 dark:border-gray-800">
              <tr>
                <th className="px-6 py-4">Type</th>
                <th className="px-6 py-4">File</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Uploaded</th>
                <th className="px-6 py-4"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                  </td>
                </tr>
              ) : documents?.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-gray-500 italic">
                    <FileText className="w-12 h-12 mx-auto mb-3 opacity-20" />
                    No documents uploaded yet.
                  </td>
                </tr>
              ) : (
                documents?.map((doc) => (
                  <DocumentRow
                    key={doc.id}
                    doc={doc}
                    isExpanded={expandedId === doc.id}
                    onToggle={() => setExpandedId(expandedId === doc.id ? null : doc.id)}
                    onReprocess={() => reprocessMutation.mutate(doc.id)}
                    isReprocessing={reprocessMutation.isPending}
                  />
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function DocumentRow({
  doc,
  isExpanded,
  onToggle,
  onReprocess,
  isReprocessing,
}: {
  doc: SourceDocument;
  isExpanded: boolean;
  onToggle: () => void;
  onReprocess: () => void;
  isReprocessing: boolean;
}) {
  return (
    <>
      <tr
        className="hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors cursor-pointer"
        onClick={onToggle}
      >
        <td className="px-6 py-4">{doc.doc_type === 'QUOTATION' ? 'Quotation' : 'Invoice'}</td>
        <td className="px-6 py-4">
          <a
            href={doc.file}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="text-primary hover:underline text-xs truncate max-w-[240px] inline-block"
          >
            {doc.file.split('/').pop()}
          </a>
        </td>
        <td className="px-6 py-4">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${STATUS_STYLES[doc.extraction_status]}`}>
            {doc.extraction_status.replace('_', ' ')}
          </span>
        </td>
        <td className="px-6 py-4 text-gray-500 text-xs">
          {new Date(doc.created_at).toLocaleDateString()}
        </td>
        <td className="px-6 py-4 text-right">
          <div className="flex items-center justify-end gap-2">
            {(doc.extraction_status === 'FAILED' || doc.extraction_status === 'NEEDS_REVIEW') && (
              <Button
                variant="outline"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  onReprocess();
                }}
                disabled={isReprocessing}
              >
                <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
                Reprocess
              </Button>
            )}
            {isExpanded ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
          </div>
        </td>
      </tr>
      {isExpanded && (
        <tr>
          <td colSpan={5} className="px-6 pb-4 bg-gray-50 dark:bg-gray-800/20">
            <ExtractedDataPreview doc={doc} />
          </td>
        </tr>
      )}
    </>
  );
}

function ExtractedDataPreview({ doc }: { doc: SourceDocument }) {
  if (doc.extraction_status === 'FAILED' && doc.ai_error_message) {
    return (
      <div className="text-sm text-red-600 dark:text-red-400 py-3">
        Extraction failed: {doc.ai_error_message}
      </div>
    );
  }

  if (!doc.extracted_data) {
    return <div className="text-sm text-gray-400 italic py-3">No extracted data available yet.</div>;
  }

  const data = doc.extracted_data;

  return (
    <div className="py-4 space-y-3">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <PreviewItem label="Supplier" value={data.supplier_name} />
        <PreviewItem label="Tax ID" value={data.tax_id} />
        <PreviewItem label="Invoice No." value={data.invoice_no} />
        <PreviewItem label="Invoice Date" value={data.invoice_date} />
        <PreviewItem label="Due Date" value={data.due_date} />
        <PreviewItem label="Subtotal" value={data.subtotal?.toString()} />
        <PreviewItem label="VAT" value={data.vat_amount?.toString()} />
        <PreviewItem label="WHT" value={data.wht_amount?.toString()} />
        <PreviewItem label="Net Total" value={data.net_total?.toString()} />
        <PreviewItem label="Confidence" value={data.confidence != null ? `${(data.confidence * 100).toFixed(0)}%` : undefined} />
      </div>

      {data.line_items && data.line_items.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-xs border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
            <thead className="bg-gray-100 dark:bg-gray-800 text-gray-500">
              <tr>
                <th className="px-3 py-2 text-left">Description</th>
                <th className="px-3 py-2 text-right">Amount</th>
                <th className="px-3 py-2 text-right">VAT %</th>
                <th className="px-3 py-2 text-right">WHT %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800 bg-white dark:bg-gray-900">
              {data.line_items.map((item, idx) => (
                <tr key={idx}>
                  <td className="px-3 py-2">{item.description}</td>
                  <td className="px-3 py-2 text-right">{item.amount}</td>
                  <td className="px-3 py-2 text-right">{item.vat_rate ?? '-'}</td>
                  <td className="px-3 py-2 text-right">{item.wht_rate ?? '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {data.notes && (
        <p className="text-xs text-gray-500 italic flex items-start gap-1.5">
          <Info className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" /> {data.notes}
        </p>
      )}
    </div>
  );
}

function PreviewItem({ label, value }: { label: string; value?: string | null }) {
  return (
    <div className="bg-white dark:bg-gray-900 p-2 rounded-lg border border-gray-100 dark:border-gray-800">
      <span className="text-gray-400 block mb-0.5">{label}</span>
      <span className="font-medium text-gray-800 dark:text-gray-200">{value || '-'}</span>
    </div>
  );
}

function UploadForm() {
  const uploadMutation = useUploadDocument();
  const { data: suppliers } = useSuppliers();
  const { data: allDocuments } = useDocuments({ doc_type: 'QUOTATION' });

  const [docType, setDocType] = useState<DocType>('INVOICE');
  const [files, setFiles] = useState<File[]>([]);
  const [supplierGuess, setSupplierGuess] = useState('');
  const [linkedQuotation, setLinkedQuotation] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (files.length === 0) return;

    const formData = new FormData();
    formData.append('doc_type', docType);
    formData.append('file', files[0]);
    if (supplierGuess) formData.append('supplier_guess', supplierGuess);
    if (docType === 'INVOICE' && linkedQuotation) formData.append('linked_quotation', linkedQuotation);

    uploadMutation.mutate(formData, {
      onSuccess: () => {
        setFiles([]);
        setSupplierGuess('');
        setLinkedQuotation('');
      },
      onError: () => alert('Failed to upload document. Please try again.'),
    });
  };

  return (
    <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 shadow-sm">
      <h2 className="text-lg font-bold mb-4">Upload Document</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex gap-2">
          {(['INVOICE', 'QUOTATION'] as DocType[]).map((type) => (
            <button
              key={type}
              type="button"
              onClick={() => setDocType(type)}
              className={`flex-1 py-2 rounded-xl border text-sm font-medium transition-all ${
                docType === type
                  ? 'bg-primary/10 text-primary border-primary'
                  : 'border-gray-200 dark:border-white/10 text-gray-500 hover:bg-gray-50 dark:hover:bg-white/5'
              }`}
            >
              {type === 'INVOICE' ? 'Invoice' : 'Quotation'}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-1">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Supplier Guess (optional)
            </label>
            <select
              value={supplierGuess}
              onChange={(e) => setSupplierGuess(e.target.value)}
              className="flex h-11 w-full rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            >
              <option value="">-- None --</option>
              {suppliers?.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          {docType === 'INVOICE' && (
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Linked Quotation (optional)
              </label>
              <select
                value={linkedQuotation}
                onChange={(e) => setLinkedQuotation(e.target.value)}
                className="flex h-11 w-full rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 outline-none transition-all"
              >
                <option value="">-- None --</option>
                {allDocuments?.map((d) => (
                  <option key={d.id} value={d.id}>
                    Quotation #{d.id} ({d.file.split('/').pop()})
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">File</label>
          <FileUpload files={files} onChange={setFiles} maxFiles={1} />
        </div>

        <Button type="submit" disabled={uploadMutation.isPending || files.length === 0}>
          {uploadMutation.isPending ? 'Uploading...' : 'Upload & Extract'}
        </Button>
      </form>
    </div>
  );
}
