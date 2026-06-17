import { authApi } from '@/lib/auth';

export type RequestStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'RETURNED' | 'IN_PROGRESS' | 'COMPLETED';

export interface WorkflowConfig {
  id: number;
  name: string;
  description: string;
  steps: WorkflowStep[];
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
  step_number: number;
}

export interface WorkflowFile {
  id: number;
  file: string;
  file_name?: string;
  filename?: string;
  uploaded_at: string;
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
}

export const workflowApi = {
  getConfigs: async (): Promise<WorkflowConfig[]> => {
    const response = await authApi.get('/api/v1/workflow/configs/');
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
};
