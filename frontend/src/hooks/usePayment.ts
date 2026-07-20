import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  paymentApi,
  Supplier,
  DocType,
  ExtractionStatus,
  VoucherStatus,
  CreateVoucherInput,
  PaymentApprovalTier,
} from '@/lib/api/payment';

// ── Suppliers ────────────────────────────────────────────────────────────────

export const useSuppliers = (params?: { q?: string; tax_id?: string }) => {
  return useQuery({
    queryKey: ['payment', 'suppliers', params ?? {}],
    queryFn: () => paymentApi.getSuppliers(params),
  });
};

export const useSupplier = (id: number) => {
  return useQuery({
    queryKey: ['payment', 'supplier', id],
    queryFn: () => paymentApi.getSupplier(id),
    enabled: !!id,
  });
};

export const useCreateSupplier = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Supplier>) => paymentApi.createSupplier(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payment', 'suppliers'] });
    },
  });
};

export const useAddBankAccount = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      supplierId,
      data,
    }: {
      supplierId: number;
      data: { bank_name: string; branch: string; account_no: string; account_name: string; is_current?: boolean };
    }) => paymentApi.addBankAccount(supplierId, data),
    onSuccess: (_, { supplierId }) => {
      queryClient.invalidateQueries({ queryKey: ['payment', 'supplier', supplierId] });
    },
  });
};

export const useSetCurrentBankAccount = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ supplierId, bankId }: { supplierId: number; bankId: number }) =>
      paymentApi.setCurrentBankAccount(supplierId, bankId),
    onSuccess: (_, { supplierId }) => {
      queryClient.invalidateQueries({ queryKey: ['payment', 'supplier', supplierId] });
    },
  });
};

// ── Documents ────────────────────────────────────────────────────────────────

export const useDocuments = (params?: { doc_type?: DocType; extraction_status?: ExtractionStatus }) => {
  return useQuery({
    queryKey: ['payment', 'documents', params ?? {}],
    queryFn: () => paymentApi.getDocuments(params),
  });
};

export const useDocument = (id: number) => {
  return useQuery({
    queryKey: ['payment', 'document', id],
    queryFn: () => paymentApi.getDocument(id),
    enabled: !!id,
  });
};

export const useUploadDocument = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (formData: FormData) => paymentApi.uploadDocument(formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payment', 'documents'] });
    },
  });
};

export const useReprocessDocument = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => paymentApi.reprocessDocument(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['payment', 'documents'] });
      queryClient.invalidateQueries({ queryKey: ['payment', 'document', id] });
    },
  });
};

// ── Vouchers ─────────────────────────────────────────────────────────────────

export const useVouchers = (params?: { status?: VoucherStatus; supplier?: number }) => {
  return useQuery({
    queryKey: ['payment', 'vouchers', params ?? {}],
    queryFn: () => paymentApi.getVouchers(params),
  });
};

export const useVoucher = (id: number) => {
  return useQuery({
    queryKey: ['payment', 'voucher', id],
    queryFn: () => paymentApi.getVoucher(id),
    enabled: !!id,
  });
};

export const useCreateVoucher = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateVoucherInput) => paymentApi.createVoucher(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payment', 'vouchers'] });
    },
  });
};

export const useMarkPaid = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: { pay_bank: string; cheque_no: string; cheque_date: string };
    }) => paymentApi.markPaid(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['payment', 'vouchers'] });
      queryClient.invalidateQueries({ queryKey: ['payment', 'voucher', id] });
    },
  });
};

export const useDownloadVoucherPdf = () => {
  return useMutation({
    mutationFn: ({ id, pvCode }: { id: number; pvCode?: string | null }) =>
      paymentApi.downloadVoucherPdf(id, pvCode),
  });
};

// ── Approval Tiers ───────────────────────────────────────────────────────────

export const useApprovalTiers = () => {
  return useQuery({
    queryKey: ['payment', 'approval-tiers'],
    queryFn: () => paymentApi.getApprovalTiers(),
  });
};

export const useCreateApprovalTier = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<PaymentApprovalTier>) => paymentApi.createApprovalTier(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payment', 'approval-tiers'] });
    },
  });
};

// ── Assets ───────────────────────────────────────────────────────────────────

export const useAssets = () => {
  return useQuery({
    queryKey: ['payment', 'assets'],
    queryFn: () => paymentApi.getAssets(),
  });
};

export const useAssetDepreciationEntries = (id: number) => {
  return useQuery({
    queryKey: ['payment', 'asset', id, 'depreciation-entries'],
    queryFn: () => paymentApi.getAssetDepreciationEntries(id),
    enabled: !!id,
  });
};
