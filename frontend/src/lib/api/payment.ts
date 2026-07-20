import { authApi } from '@/lib/auth';

// ── Types ────────────────────────────────────────────────────────────────────

export type BranchType = 'HQ' | 'BRANCH';

export interface SupplierBankAccount {
  id: number;
  supplier: number;
  bank_name: string;
  branch: string;
  account_no: string;
  account_name: string;
  is_current: boolean;
  verified_by: number | null;
  verified_at: string | null;
  created_at: string;
}

export interface Supplier {
  id: number;
  name: string;
  tax_id: string;
  branch_type: BranchType;
  branch_no: string;
  address: string;
  phone: string;
  email: string;
  default_wht_rate: number | string;
  is_active: boolean;
  bank_accounts: SupplierBankAccount[];
  created_at: string;
  updated_at: string;
}

export type DocType = 'QUOTATION' | 'INVOICE';
export type ExtractionStatus = 'PENDING' | 'PROCESSING' | 'SUCCESS' | 'FAILED' | 'NEEDS_REVIEW';

export interface InvoiceLineItem {
  description: string;
  amount: number;
  vat_rate?: number;
  wht_rate?: number;
}

export interface InvoiceExtractionResult {
  supplier_name?: string;
  tax_id?: string;
  invoice_no?: string;
  invoice_date?: string;
  due_date?: string;
  line_items?: InvoiceLineItem[];
  subtotal?: number;
  vat_amount?: number;
  wht_amount?: number;
  net_total?: number;
  confidence?: number;
  notes?: string;
}

export interface SourceDocument {
  id: number;
  doc_type: DocType;
  file: string;
  uploaded_by: number;
  supplier_guess: number | null;
  extraction_status: ExtractionStatus;
  extracted_data: InvoiceExtractionResult | null;
  ai_error_message: string;
  linked_quotation: number | null;
  created_at: string;
  updated_at: string;
}

export type VoucherStatus = 'DRAFT' | 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'RETURNED' | 'PAID';

export interface ValidationFlag {
  code: string;
  message: string;
  severity: string;
}

export interface PaymentVoucherLine {
  id: number;
  description: string;
  department: string;
  amount: number | string;
  vat_rate: number | string;
  vat_amount: number | string;
  wht_rate: number | string;
  wht_amount: number | string;
  net_amount: number | string;
}

export interface PaymentVoucher {
  id: number;
  request: number;
  request_status: string;
  pv_code: string | null;
  supplier: number;
  supplier_name: string;
  source_document: number | null;
  payee_bank_account: number;
  invoice_no_ref: string;
  invoice_date: string | null;
  due_date: string | null;
  subtotal: number | string;
  vat_amount: number | string;
  wht_amount: number | string;
  net_amount: number | string;
  is_fixed_asset: boolean;
  status: VoucherStatus;
  pay_bank: string;
  cheque_no: string;
  cheque_date: string | null;
  paid_at: string | null;
  validation_flags: ValidationFlag[];
  batch: number | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  lines: PaymentVoucherLine[];
}

export interface CreateVoucherLineInput {
  description: string;
  department?: string;
  amount: number;
  vat_rate?: number;
  wht_rate?: number;
}

export interface CreateVoucherInput {
  supplier: number;
  payee_bank_account: number;
  source_document?: number;
  is_fixed_asset?: boolean;
  invoice_no_ref?: string;
  invoice_date?: string;
  due_date?: string;
  lines: CreateVoucherLineInput[];
}

export interface PaymentApprovalTier {
  id: number;
  name: string;
  min_amount: number | string;
  max_amount: number | string;
  workflow_config: number;
  is_active: boolean;
  order: number;
}

export type AssetCategory = 'VEHICLE' | 'COMPUTER' | 'FURNITURE' | 'OFFICE_DECOR' | 'SOFTWARE' | 'OTHER';

export interface FixedAsset {
  id: number;
  asset_code: string;
  name: string;
  category: AssetCategory;
  purchase_voucher: number | null;
  legacy_pv_ref: string;
  tax_invoice_no: string;
  purchase_price: number | string;
  purchase_date: string;
  depreciation_rate_percent: number | string;
  useful_life_days: number;
  disposed_at: string | null;
}

export interface DepreciationEntry {
  id: number;
  asset: number;
  period: string;
  amount: number | string;
  accumulated_amount: number | string;
  is_disallowed_expense: boolean;
}

interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

function unwrapList<T>(data: T[] | Paginated<T>): T[] {
  if (Array.isArray(data)) return data;
  return data.results;
}

// ── API ──────────────────────────────────────────────────────────────────────

export const paymentApi = {
  // Suppliers
  getSuppliers: async (params?: { q?: string; tax_id?: string }): Promise<Supplier[]> => {
    const response = await authApi.get('/api/v1/payment/suppliers/', { params });
    return unwrapList<Supplier>(response.data);
  },

  getSupplier: async (id: number): Promise<Supplier> => {
    const response = await authApi.get(`/api/v1/payment/suppliers/${id}/`);
    return response.data;
  },

  createSupplier: async (data: Partial<Supplier>): Promise<Supplier> => {
    const response = await authApi.post('/api/v1/payment/suppliers/', data);
    return response.data;
  },

  updateSupplier: async (id: number, data: Partial<Supplier>): Promise<Supplier> => {
    const response = await authApi.patch(`/api/v1/payment/suppliers/${id}/`, data);
    return response.data;
  },

  getBankAccounts: async (supplierId: number): Promise<SupplierBankAccount[]> => {
    const response = await authApi.get(`/api/v1/payment/suppliers/${supplierId}/bank-accounts/`);
    return response.data;
  },

  addBankAccount: async (
    supplierId: number,
    data: { bank_name: string; branch: string; account_no: string; account_name: string; is_current?: boolean }
  ): Promise<SupplierBankAccount> => {
    const response = await authApi.post(`/api/v1/payment/suppliers/${supplierId}/bank-accounts/`, data);
    return response.data;
  },

  setCurrentBankAccount: async (supplierId: number, bankId: number): Promise<SupplierBankAccount> => {
    const response = await authApi.post(
      `/api/v1/payment/suppliers/${supplierId}/bank-accounts/${bankId}/set-current/`
    );
    return response.data;
  },

  // Documents
  getDocuments: async (params?: { doc_type?: DocType; extraction_status?: ExtractionStatus }): Promise<SourceDocument[]> => {
    const response = await authApi.get('/api/v1/payment/documents/', { params });
    return unwrapList<SourceDocument>(response.data);
  },

  getDocument: async (id: number): Promise<SourceDocument> => {
    const response = await authApi.get(`/api/v1/payment/documents/${id}/`);
    return response.data;
  },

  uploadDocument: async (formData: FormData): Promise<SourceDocument> => {
    const response = await authApi.post('/api/v1/payment/documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  reprocessDocument: async (id: number): Promise<SourceDocument> => {
    const response = await authApi.post(`/api/v1/payment/documents/${id}/reprocess/`);
    return response.data;
  },

  // Vouchers
  getVouchers: async (params?: { status?: VoucherStatus; supplier?: number }): Promise<PaymentVoucher[]> => {
    const response = await authApi.get('/api/v1/payment/vouchers/', { params });
    return unwrapList<PaymentVoucher>(response.data);
  },

  getVoucher: async (id: number): Promise<PaymentVoucher> => {
    const response = await authApi.get(`/api/v1/payment/vouchers/${id}/`);
    return response.data;
  },

  createVoucher: async (data: CreateVoucherInput): Promise<PaymentVoucher> => {
    const response = await authApi.post('/api/v1/payment/vouchers/', data);
    return response.data;
  },

  markPaid: async (
    id: number,
    data: { pay_bank: string; cheque_no: string; cheque_date: string }
  ): Promise<PaymentVoucher> => {
    const response = await authApi.post(`/api/v1/payment/vouchers/${id}/mark-paid/`, data);
    return response.data;
  },

  downloadVoucherPdf: async (id: number, pvCode?: string | null): Promise<void> => {
    const response = await authApi.get(`/api/v1/payment/vouchers/${id}/pdf/`, {
      responseType: 'blob',
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${pvCode || id}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  // Approval tiers
  getApprovalTiers: async (): Promise<PaymentApprovalTier[]> => {
    const response = await authApi.get('/api/v1/payment/approval-tiers/');
    return unwrapList<PaymentApprovalTier>(response.data);
  },

  createApprovalTier: async (data: Partial<PaymentApprovalTier>): Promise<PaymentApprovalTier> => {
    const response = await authApi.post('/api/v1/payment/approval-tiers/', data);
    return response.data;
  },

  // Assets
  getAssets: async (): Promise<FixedAsset[]> => {
    const response = await authApi.get('/api/v1/payment/assets/');
    return unwrapList<FixedAsset>(response.data);
  },

  createAsset: async (data: Partial<FixedAsset>): Promise<FixedAsset> => {
    const response = await authApi.post('/api/v1/payment/assets/', data);
    return response.data;
  },

  getAssetDepreciationEntries: async (id: number): Promise<DepreciationEntry[]> => {
    const response = await authApi.get(`/api/v1/payment/assets/${id}/depreciation-entries/`);
    return response.data;
  },
};
