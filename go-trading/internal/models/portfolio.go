package models

import "time"

type Portfolio struct {
	Profile             Investor             `json:"profile"`
	MFAccounts          []InvestorAccount    `json:"mfAccounts"`
	PrivateFundAccounts []PrivateFundAccount `json:"privateFundAccounts"`
	BondAccounts        []BondAccount        `json:"bondAccounts"`
	UpdatedAt           time.Time            `json:"updated_at"`
}

type Investor struct {
	ID             int        `json:"id"`
	CustCode       string     `json:"custCode"`
	CompCode       string     `json:"compCode"`
	FullNameEn     string     `json:"fullNameEn"`
	FullNameTh     string     `json:"fullNameTh"`
	Mobile         *string    `json:"mobile"`
	Email          string     `json:"email"`
	Projects       string     `json:"projects"`
	Status         string     `json:"status"`
	SuitDate       *string    `json:"suitDate"`
	CardExpireDate *string    `json:"cardExpireDate"`
	NextKycDate    *string    `json:"nextKycDate"`
	CreatedAt      time.Time  `json:"created_at"`
	UpdatedAt      time.Time  `json:"updated_at"`
}

type FundAnalysis struct {
	ID                   int        `json:"id"`
	StandardDeviation    *float64   `json:"standard_deviation"`
	TreynorRatio        *float64   `json:"treynor_ratio"`
	SortinoRatio        *float64   `json:"sortino_ratio"`
	InformationRatio     *float64   `json:"information_ratio"`
	CaptureRatioUp      *float64   `json:"capture_ratio_up"`
	CaptureRatioDown    *float64   `json:"capture_ratio_down"`
	SentimentScore      *float64   `json:"sentiment_score"`
	SentimentSummary    *string    `json:"sentiment_summary"`
	SentimentImpactLevel *string    `json:"sentiment_impact_level"`
	LastCalculated      *time.Time  `json:"last_calculated"`
	CreatedAt           time.Time   `json:"created_at"`
	UpdatedAt           time.Time   `json:"updated_at"`
	CreateBy           *string     `json:"createBy"`
	UpdateBy           *string     `json:"updateBy"`
}

type AccountBalance struct {
	ID           int           `json:"id"`
	CompCode     string        `json:"compCode"`
	AccountID    string        `json:"accountID"` // String from related account
	FundCode     string        `json:"fundCode"`
	UnitBalance  float64       `json:"unitBalance"`
	Amount       float64       `json:"amount"`
	AverageCost  *float64      `json:"averageCost"`
	NAV          float64       `json:"NAV"`
	NAVdate      string        `json:"NAVdate"`
	FundAnalysis *FundAnalysis `json:"fund_analysis"`
}

type InvestorAccount struct {
	ID            int              `json:"id"`
	CompCode      string           `json:"compCode"`
	CustCode      int              `json:"custCode"`
	AccountID     string           `json:"accountID"`
	OpenDate      *string          `json:"openDate"`
	Status        string           `json:"status"`
	MarketingName *string          `json:"marketing_name"`
	AgentName     *string          `json:"agent_name"`
	Balances      []AccountBalance `json:"balances"`
}

type BondAccount struct {
	ID            int     `json:"id"`
	CompCode      string  `json:"compCode"`
	CustCode      int     `json:"custCode"`
	BondCode      *string `json:"bondCode"`
	Amount        float64 `json:"amount"`
	FromDate      *string `json:"fromDate"`
	ToDate        *string `json:"toDate"`
	Issuer        *string `json:"issuer"`
	BondSymbol    *string `json:"bondSymbol"`
	Status        string  `json:"status"`
	MarketingName *string `json:"marketing_name"`
	AgentName     *string `json:"agent_name"`
}

type PrivateFundBalance struct {
	ID           int           `json:"id"`
	CompCode     string        `json:"compCode"`
	AccountID    string        `json:"accountID"` // String from related account
	FundCode     string        `json:"fundCode"`
	UnitBalance  float64       `json:"unitBalance"`
	Amount       float64       `json:"amount"`
	AverageCost  *float64      `json:"averageCost"`
	NAV          float64       `json:"NAV"`
	NAVdate      string        `json:"NAVdate"`
	FundAnalysis *FundAnalysis `json:"fund_analysis"`
}

type PrivateFundAccount struct {
	ID                  int                  `json:"id"`
	CompCode            string               `json:"compCode"`
	CustCode            int                  `json:"custCode"`
	AccountID           string               `json:"accountID"`
	FundType            *string              `json:"fundType"`
	OpenDate            *string              `json:"openDate"`
	Status              string               `json:"status"`
	MarketingName       *string              `json:"marketing_name"`
	AgentName           *string              `json:"agent_name"`
	PrivateFundBalances []PrivateFundBalance `json:"privateFundBalances"`
}

type Balance struct {
	UserID    string    `json:"user_id"`
	Available float64   `json:"available_balance"`
	Reserved  float64   `json:"reserved_balance"`
	UpdatedAt time.Time `json:"updated_at"`
}
