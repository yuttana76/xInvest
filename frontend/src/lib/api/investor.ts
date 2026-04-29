import { authApi } from '@/lib/auth';

export interface Profile {
  custCode: string;
  fullNameEn: string;
  fullNameTh: string;
  mobile?: string;
  email: string;
  status: string;
}

export interface Balance {
  accountID: string;
  fundCode: string;
  amount: number;
  averageCost: number;
  NAV: number;
  unitBalance: number;
  NAVdate: string;
  fund_analysis?: {
    sentiment_score: number | null;
    sentiment_summary: string | null;
    sentiment_impact_level: 'LOW' | 'MED' | 'HIGH' | null;
    updated_at: string | null;
  } | null;
}

export interface Account {
  accountID: string;
  compCode: string;
  status: string;
  marketing?: number;
  marketing_name?: string;
  agent_name?: string;
  openDate?: string;
  balances?: Balance[];
}

export interface BondAccount {
  compCode: string;
  bondCode?: string;
  amount: number;
  fromDate?: string;
  toDate?: string;
  issuer?: string;
  bondSymbol?: string;
  paymentDate?: string;
  paymentAmount?: number;
  paymentType?: string;
  paymentStatus?: string;
  channel?: string;
  maturityDate?: string;
  maturityAmount?: number;
  maturityType?: string;
  maturityStatus?: string;
  status: string;
  marketing_name?: string;
  agent_name?: string;
}

export interface PrivateFundAccount {
  accountID: string;
  compCode: string;
  fundType?: string;
  status: string;
  marketing_name?: string;
  agent_name?: string;
  openDate?: string;
  privateFundBalances?: Balance[];
}

export interface PerformanceSummary {
  start_value: number;
  current_value: number;
  change_amount: number;
  change_percent: number;
}

export interface PerformanceChartData {
  date: string;
  total_market_value: number;
  total_gain: number;
}

export interface PerformanceData {
  account_id: string;
  period_days: number;
  summary: PerformanceSummary;
  chart_data: PerformanceChartData[];
}

export interface InvestorData {
  profile: Profile;
  mfAccounts: Account[];
  privateFundAccounts: PrivateFundAccount[];
  bondAccounts: BondAccount[];
}

export interface MarketingInvestor {
  id: number;
  custCode: string;
  fullNameEn: string;
  fullNameTh: string;
  status: string;
  mf_amount: number;
  bond_amount: number;
  pf_amount: number;
  total_amount: number;
  total_profit: number;
  mf_profit: number;
  pf_profit: number;
  suitDate?: string;
  cardExpireDate?: string;
  nextKycDate?: string;
  created_at: string;
  updated_at: string;
}

export interface OperatorDashboardStats {
  stats: {
    totalCustomers: number;
    newToday: number;
    modifiedToday: number;
    suitExpiredMonth: number;
    cardExpiredMonth: number;
    kycExpiredMonth: number;
  };
  newCustomers: Profile[];
  modifiedCustomers: Profile[];
}

export interface MarketingDashboardStats {
  profile: {
    fullName: string;
    code: string;
  };
  stats: {
    totalInvestors: number;
    totalAUM: number;
    aumThisMonth: number;
    mfAUM: number;
    bondAUM: number;
    pfAUM: number;
    subThisMonth: number;
    mfSubThisMonth: number;
    bondSubThisMonth: number;
    pfSubThisMonth: number;
  };
  alerts: {
    suitability: number;
    card: number;
    kyc: number;
  };
  statusDistribution: Record<string, number>;
}

export interface AgentDashboardStats {
  profile: {
    fullName: string;
    agentCode: string;
  };
  stats: {
    totalInvestors: number;
    totalAUM: number;
    aumThisMonth: number;
    mfAUM: number;
    bondAUM: number;
    pfAUM: number;
    subThisMonth: number;
    mfSubThisMonth: number;
    bondSubThisMonth: number;
    pfSubThisMonth: number;
  };
  alerts: {
    suitability: number;
    card: number;
    kyc: number;
  };
  statusDistribution: Record<string, number>;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const getInvestorDashboardData = async (): Promise<InvestorData> => {
  const response = await authApi.get('/api/v1/invest/me/');
  return response.data;
};

export const getMFPerformanceData = async (accountId: string, days: number): Promise<PerformanceData> => {
  const response = await authApi.post('/api/v1/invest/mf/portfolio-performance/', {
    account_id: accountId,
    days: days
  });
  return response.data;
};

export const getPFPerformanceData = async (accountId: string, days: number): Promise<PerformanceData> => {
  const response = await authApi.post('/api/v1/invest/pf/portfolio-performance/', {
    account_id: accountId,
    days: days
  });
  return response.data;
};

export const getOperatorInvestorList = async (page: number = 1, status?: string, search?: string): Promise<PaginatedResponse<MarketingInvestor>> => {
  const response = await authApi.get('/api/v1/invest/operator/investors/', {
    params: { page, status, search }
  });
  return response.data;
};

export const getOperatorDashboardStats = async (): Promise<OperatorDashboardStats> => {
  const response = await authApi.get('/api/v1/invest/operator/dashboard/');
  return response.data;
};

export const exportOperatorInvestors = async (): Promise<void> => {
  const response = await authApi.get('/api/v1/invest/operator/investors/export/', {
    responseType: 'blob'
  });
  
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'investors.xlsx');
  document.body.appendChild(link);
  link.click();
  link.remove();
};

export const getMarketingInvestorList = async (status?: string, search?: string): Promise<MarketingInvestor[]> => {
  const response = await authApi.get('/api/v1/invest/marketing/investors/', {
    params: { status, search }
  });
  return response.data.results || response.data;
};

export const getAgentInvestorList = async (status?: string, search?: string): Promise<MarketingInvestor[]> => {
  const response = await authApi.get('/api/v1/invest/agent/investors/', {
    params: { status, search }
  });
  return response.data.results || response.data;
};

export const getMarketingDashboardStats = async (): Promise<MarketingDashboardStats> => {
  const response = await authApi.get('/api/v1/invest/marketing/dashboard/');
  return response.data;
};

export const getAgentDashboardStats = async (): Promise<AgentDashboardStats> => {
  const response = await authApi.get('/api/v1/invest/agent/dashboard/');
  return response.data;
};
