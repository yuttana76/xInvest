import { authApi } from '@/lib/auth';

export type RequestStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'RETURNED' | 'IN_PROGRESS' | 'COMPLETED';

export type PriorityLevel = 1 | 2 | 3; // 1=High, 2=Medium, 3=Low

export interface WorkflowConfig {
  id: number;
  name: string;
  description: string;
  steps: WorkflowStep[];
  subjects: RequestSubject[];  // active subjects for this workflow
}

export interface WorkflowStep {
  id: number;
  step_number: number;
  step_name: string;
  required_group: number;
  required_group_name?: string;
}

export interface ApprovalLog {
  id: number;
  action: string;
  comment: string;
  created_at: string;
  user_display: string;
  approver_name: string;
  approver_username?: string;
  step_number: number;
}

export interface WorkflowFile {
  id: number;
  file: string;
  file_name?: string;
  filename?: string;
  uploaded_at: string;
}

export interface RequestSubject {
  id: number;
  name: string;
  code: string;
}

export interface WorkflowRequest {
  id: number;
  req_code: string | null;
  title: string;
  description: string;
  create_department?: string | null;
  status: RequestStatus;
  current_step_number: number;
  workflow: number;
  workflow_name: string;
  workflow_category: string;
  creator: number;
  creator_name: string;
  creator_username: string;
  created_at: string;
  updated_at: string;
  workflow_steps: WorkflowStep[];
  current_step_info?: WorkflowStep;
  logs: ApprovalLog[];
  files: WorkflowFile[];
  rating: number | null;
  rating_comment: string | null;
  // IT request fields
  reqSubject: number[];                  // writable: list of subject IDs
  reqSubject_details: RequestSubject[];  // readable: full subject objects
  priorify: PriorityLevel;
  expectDate: string | null;             // ISO date string (YYYY-MM-DD)
  auditFlag: boolean;
}

export const workflowApi = {
  getConfigs: async (): Promise<WorkflowConfig[]> => {
    const response = await authApi.get('/api/v1/workflow/configs/');
    return response.data;
  },

  getSubjects: async (workflowId?: number): Promise<RequestSubject[]> => {
    const url = workflowId
      ? `/api/v1/workflow/subjects/?workflow=${workflowId}`
      : '/api/v1/workflow/subjects/';
    const response = await authApi.get(url);
    return response.data;
  },

  getRequests: async (): Promise<WorkflowRequest[]> => {
    const response = await authApi.get('/api/v1/workflow/requests/');
    return response.data;
  },

  getMyRequests: async (): Promise<WorkflowRequest[]> => {
    const response = await authApi.get('/api/v1/workflow/requests/my_requests/');
    return response.data;
  },

  getWaitingApproval: async (): Promise<WorkflowRequest[]> => {
    const response = await authApi.get('/api/v1/workflow/requests/waiting_approval/');
    return response.data;
  },

  getRequestDetail: async (id: number): Promise<WorkflowRequest> => {
    const response = await authApi.get(`/api/v1/workflow/requests/${id}/`);
    return response.data;
  },

  createRequest: async (formData: FormData): Promise<WorkflowRequest> => {
    const response = await authApi.post('/api/v1/workflow/requests/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  approveRequest: async (id: number, comment: string, files?: File[]): Promise<{ status: string; message: string }> => {
    if (files && files.length > 0) {
      const formData = new FormData();
      formData.append('comment', comment);
      files.forEach((file) => formData.append('uploaded_files', file));
      const response = await authApi.post(`/api/v1/workflow/requests/${id}/approve/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    } else {
      const response = await authApi.post(`/api/v1/workflow/requests/${id}/approve/`, { comment });
      return response.data;
    }
  },

  returnToCreator: async (id: number, comment: string): Promise<{ status: string; message: string }> => {
    const response = await authApi.post(`/api/v1/workflow/requests/${id}/return_to_creator/`, { comment });
    return response.data;
  },

  rejectRequest: async (id: number, comment: string): Promise<{ status: string; message: string }> => {
    const response = await authApi.post(`/api/v1/workflow/requests/${id}/reject/`, { comment });
    return response.data;
  },

  completeRequest: async (id: number, comment: string, rating?: number, rating_comment?: string): Promise<{ status: string; message: string }> => {
    const response = await authApi.post(`/api/v1/workflow/requests/${id}/complete/`, {
      comment,
      rating,
      rating_comment
    });
    return response.data;
  },

  resubmitRequest: async (id: number, formData: FormData): Promise<WorkflowRequest> => {
    const response = await authApi.post(`/api/v1/workflow/requests/${id}/resubmit/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  rateRequest: async (id: number, rating: number, comment: string): Promise<WorkflowRequest> => {
    const response = await authApi.post(`/api/v1/workflow/requests/${id}/rate/`, { rating, rating_comment: comment });
    return response.data;
  },

  exportPdf: async (id: number): Promise<Blob> => {
    const response = await authApi.get(`/api/v1/workflow/requests/${id}/export-pdf/`, {
      responseType: 'blob',
    });
    return response.data;
  },
};
