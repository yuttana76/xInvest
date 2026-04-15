import { gql } from '@apollo/client';

export const GET_FUND_PROFILE_BY_CODE = gql`
  query fundProfileByCode($fundCode: String!) {
    fundProfileByCode(fundCode: $fundCode) {
      fundCode
      amcCode
      fundNameTh
      fundNameEn
      fundPolicy
      taxType
      fundRiskLevel
      dividendFlag
      registrationDate
      fstLowbuyVal
      nxtLowbuyVal
      fundAnalysis {
        treynorRatio
        sortinoRatio
        informationRatio
        standardDeviation
      }
      aiInsight {
        content
        createdAt
      }
      fundPerformance {
        navDate
        pYtdReturn
        p1mReturn
        p3mReturn
        p6mReturn
        p1yReturn
        p3yReturn
        p5yReturn
      }
      assetAllocation {
        investmentTypeCode
        investmentSize
        asEndOf
      }
      topHolding {
        securitiesName
        securitiesInvestSize
        asEndOf
      }
    }
  }
`;
