import { authApi } from '@/lib/auth';
import { NewsArticle } from './fundDecision';

export const getNewsByProduct = async (productType?: string, ticker?: string): Promise<NewsArticle[]> => {
  const params: Record<string, string> = {};
  if (productType) params.relate_product = productType;
  if (ticker) params.ticker = ticker;

  const response = await authApi.get('/api/v1/fundDecision/news/', { params });
  return response.data.results || response.data;
};
