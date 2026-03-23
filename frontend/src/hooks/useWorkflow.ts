import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { workflowApi } from '@/lib/api/workflow';

export const useWorkflowConfigs = () => {
  return useQuery({
    queryKey: ['workflow', 'configs'],
    queryFn: workflowApi.getConfigs,
  });
};

export const useMyRequests = () => {
  return useQuery({
    queryKey: ['workflow', 'my-requests'],
    queryFn: workflowApi.getMyRequests,
  });
};

export const useWaitingApproval = () => {
  return useQuery({
    queryKey: ['workflow', 'waiting-approval'],
    queryFn: workflowApi.getWaitingApproval,
  });
};

export const useRequestDetail = (id: number) => {
  return useQuery({
    queryKey: ['workflow', 'request', id],
    queryFn: () => workflowApi.getRequestDetail(id),
    enabled: !!id,
  });
};

export const useWorkflowMutation = () => {
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: workflowApi.createRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflow', 'my-requests'] });
    },
  });

  const approveMutation = useMutation({
    mutationFn: ({ id, comment }: { id: number; comment: string }) => workflowApi.approveRequest(id, comment),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['workflow', 'waiting-approval'] });
      queryClient.invalidateQueries({ queryKey: ['workflow', 'request', id] });
    },
  });

  const returnMutation = useMutation({
    mutationFn: ({ id, comment }: { id: number; comment: string }) => workflowApi.returnToCreator(id, comment),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['workflow', 'waiting-approval'] });
      queryClient.invalidateQueries({ queryKey: ['workflow', 'request', id] });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: ({ id, comment }: { id: number; comment: string }) => workflowApi.rejectRequest(id, comment),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['workflow', 'waiting-approval'] });
      queryClient.invalidateQueries({ queryKey: ['workflow', 'request', id] });
    },
  });

  const resubmitMutation = useMutation({
    mutationFn: ({ id, formData }: { id: number; formData: FormData }) => workflowApi.resubmitRequest(id, formData),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['workflow', 'my-requests'] });
      queryClient.invalidateQueries({ queryKey: ['workflow', 'request', id] });
    },
  });

  const completeMutation = useMutation({
    mutationFn: ({ id, comment, rating, rating_comment }: { id: number; comment: string; rating?: number; rating_comment?: string }) => 
      workflowApi.completeRequest(id, comment, rating, rating_comment),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['workflow', 'my-requests'] });
      queryClient.invalidateQueries({ queryKey: ['workflow', 'request', id] });
    },
  });

  const rateMutation = useMutation({
    mutationFn: ({ id, rating, comment }: { id: number; rating: number; comment: string }) => 
      workflowApi.rateRequest(id, rating, comment),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['workflow', 'my-requests'] });
      queryClient.invalidateQueries({ queryKey: ['workflow', 'request', id] });
    },
  });

  return {
    createMutation,
    approveMutation,
    returnMutation,
    rejectMutation,
    resubmitMutation,
    completeMutation,
    rateMutation,
  };
};
