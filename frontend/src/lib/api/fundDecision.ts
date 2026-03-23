import { authApi } from '@/lib/auth';

export interface FundHolding {
  id?: number;
  name?: string;
  weight?: number;
  [key: string]: unknown;
}

export interface FundAnalysis {
  id?: number;
  standard_deviation: number | null;
  treynor_ratio: number | null;
  sortino_ratio: number | null;
  information_ratio: number | null;
  capture_ratio_up: number | null;
  capture_ratio_down: number | null;
  sentiment_score: number | null;
  sentiment_summary: string | null;
  sentiment_impact_level: 'LOW' | 'MED' | 'HIGH' | null;
  last_calculated: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface AiInsight {
  id?: number;
  content?: string;
  created_at?: string;
  [key: string]: unknown;
}

export interface FundMetrics {
  id?: number;
  [key: string]: unknown;
}

export interface NewsArticle {
  id: number;
  source: string;
  title: string;
  content: string;
  url: string;
  published_at: string;
  ai_sentiment_score: number | null;
  ai_summary: string;
  ai_impact_level: 'LOW' | 'MED' | 'HIGH' | null;
}

export interface FundDetail {
  id: number;
  fundCode: string;
  name_th: string;
  name_en: string;
  fund_category: string;
  risk_level: number;
  is_dividend: boolean;
  fact_sheet_pdf: string | null;
  fact_sheet_url: string | null;
  last_updated_ffs: string | null;
  management_fee: number | null;
  total_expense_ratio: number | null;
  sharpe_ratio: number | null;
  alpha: number | null;
  beta: number | null;
  max_drawdown: number | null;
  created_at: string;
  updated_at: string;
  amc: number;
  holdings: FundHolding[];
  fund_analysis: FundAnalysis[];
  ai_insights: AiInsight[];
  latest_insight: AiInsight | null;
  metrics: FundMetrics | null;
  approved_news: NewsArticle[];
}

export const getFundDetail = async (fundCode: string): Promise<FundDetail> => {
  const response = await authApi.get(`/api/v1/fundDecision/funds/${fundCode}/`);
  return response.data;
};
