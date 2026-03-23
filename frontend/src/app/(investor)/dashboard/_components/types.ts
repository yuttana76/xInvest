import { Balance, PerformanceChartData } from '@/lib/api/investor';

export interface ExtendedBalance extends Balance {
  group: string;
  status?: string;
  fromDate?: string;
  toDate?: string;
}

export interface BaseProductDetailsProps {
  itemColor: string;
  innerSelectedAccount: string;
  setInnerSelectedAccount: (accountId: string) => void;
  accountIds: string[];
  performanceData: PerformanceChartData[];
  perfLoading: boolean;
  period: number;
  setPeriod: (days: number) => void;
}

export interface MFDetailsProps extends BaseProductDetailsProps {
  balances: ExtendedBalance[];
  holdingKeyPrefix: string;
  expandedHoldings: Record<string, boolean>;
  toggleExpand: (holdingKey: string) => void;
  hoveredSentimentKey: string | null;
  setHoveredSentimentKey: (key: string | null) => void;
}

export interface PFDetailsProps extends BaseProductDetailsProps {
  balances: ExtendedBalance[];
  holdingKeyPrefix: string;
  expandedHoldings: Record<string, boolean>;
  toggleExpand: (holdingKey: string) => void;
}

export interface AssetAllocationItem {
  name: string;
  percent: number;
  value: number;
  profit: number;
  profitPercent: number;
  balances: ExtendedBalance[];
  color: string;
}

export interface BondDetailsProps {
  balances: ExtendedBalance[];
  itemColor: string;
  expandedHoldings: Record<string, boolean>;
  toggleExpand: (holdingKey: string) => void;
}
