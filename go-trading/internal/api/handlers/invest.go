package handlers

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"time"

	"xinvest/go-trading/internal/models"
	"xinvest/go-trading/internal/repository"

	"github.com/gin-gonic/gin"
)

func GetInvestmentInfo(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User ID not found in context"})
		return
	}

	var userIDStr string
	switch v := userID.(type) {
	case string:
		userIDStr = v
	case float64:
		userIDStr = fmt.Sprintf("%.0f", v)
	default:
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Invalid user ID type"})
		return
	}

	// 1. Try to get from Redis
	portfolio, err := repository.GetPortfolioFromCache(c.Request.Context(), userIDStr)
	if err == nil && portfolio != nil {
		c.JSON(http.StatusOK, portfolio)
		return
	}

	// 2. Fallback to Postgres
	portfolio, err = fetchPortfolioFromDB(c.Request.Context(), userIDStr)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		return
	}

	// 3. Update Cache asynchronously
	go func() {
		_ = repository.SetPortfolioToCache(context.Background(), userIDStr, portfolio)
	}()

	c.JSON(http.StatusOK, portfolio)
}

// fetchPortfolioFromDB fetches full portfolio data from Postgres
func fetchPortfolioFromDB(ctx context.Context, userID string) (*models.Portfolio, error) {
	db := repository.DB
	if db == nil {
		return nil, fmt.Errorf("database connection not initialized")
	}

	// 1. Fetch Investor Profile
	var p models.Investor
	err := db.QueryRowContext(ctx,
		`SELECT id, "custCode", "compCode", "fullNameEn", "fullNameTh", mobile, email, projects, status, "suitDate", "cardExpireDate", "nextKycDate", created_at, updated_at 
		 FROM invest_investor WHERE user_id = $1`, userID).Scan(
		&p.ID, &p.CustCode, &p.CompCode, &p.FullNameEn, &p.FullNameTh, &p.Mobile, &p.Email, &p.Projects, &p.Status,
		&p.SuitDate, &p.CardExpireDate, &p.NextKycDate, &p.CreatedAt, &p.UpdatedAt)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("no investor profile associated with this user")
		}
		return nil, err
	}

	portfolio := &models.Portfolio{
		Profile:   p,
		UpdatedAt: time.Now(),
	}

	// 2. Fetch MF Accounts
	rows, err := db.QueryContext(ctx,
		`SELECT ia.id, ia."compCode", ia."custCode_id", ia."accountID", ia."openDate", ia.status, m."fullName", ea."fullName"
		 FROM invest_investoraccount ia
		 LEFT JOIN invest_marketing m ON ia.marketing_id = m.id
		 LEFT JOIN invest_externalagent ea ON ia.referred_by_agent_id = ea.id
		 WHERE ia."custCode_id" = $1`, p.ID)
	if err == nil {
		defer rows.Close()
		for rows.Next() {
			var acc models.InvestorAccount
			if err := rows.Scan(&acc.ID, &acc.CompCode, &acc.CustCode, &acc.AccountID, &acc.OpenDate, &acc.Status, &acc.MarketingName, &acc.AgentName); err != nil {
				continue
			}

			// Fetch Balances for this account with latest ACTIVE FundAnalysis
			bRows, err := db.QueryContext(ctx,
				`SELECT b.id, b."compCode", b.fundCode, b."unitBalance", b.amount, b."averageCost", b."NAV", b."NAVdate",
						fa.id, fa.standard_deviation, fa.treynor_ratio, fa.sortino_ratio, fa.information_ratio,
						fa.capture_ratio_up, fa.capture_ratio_down, fa.sentiment_score, fa.sentiment_summary,
						fa.sentiment_impact_level, fa.last_calculated, fa.created_at, fa.updated_at,
						fa."createBy", fa."updateBy"
				 FROM invest_accountbalance b
				 LEFT JOIN LATERAL (
					SELECT id, standard_deviation, treynor_ratio, sortino_ratio, information_ratio,
					       capture_ratio_up, capture_ratio_down, sentiment_score, sentiment_summary,
					       sentiment_impact_level, last_calculated, created_at, updated_at,
					       "createBy", "updateBy"
					FROM "fundDecision_fundanalysis" 
					WHERE fund_id = (SELECT id FROM "fundDecision_fundinfo" WHERE "fundCode" = b."fundCode")
					AND status = 'ACTIVE'
					ORDER BY created_at DESC LIMIT 1
				 ) fa ON true
				 WHERE b."accountID_id" = $1`, acc.ID)

			if err == nil {
				func() {
					defer bRows.Close()
					acc.Balances = []models.AccountBalance{} // Initialize to empty slice
					for bRows.Next() {
						var bal models.AccountBalance
						var fa models.FundAnalysis
						var faID sql.NullInt64 // To check if fa exists

						err := bRows.Scan(
							&bal.ID, &bal.CompCode, &bal.FundCode, &bal.UnitBalance, &bal.Amount, &bal.AverageCost, &bal.NAV, &bal.NAVdate,
							&faID, &fa.StandardDeviation, &fa.TreynorRatio, &fa.SortinoRatio, &fa.InformationRatio,
							&fa.CaptureRatioUp, &fa.CaptureRatioDown, &fa.SentimentScore, &fa.SentimentSummary,
							&fa.SentimentImpactLevel, &fa.LastCalculated, &fa.CreatedAt, &fa.UpdatedAt,
							&fa.CreateBy, &fa.UpdateBy,
						)
						if err != nil {
							log.Printf("Error scanning MF balance row: %v", err)
							continue
						}
						bal.AccountID = acc.AccountID // Map the string accountID
						if faID.Valid {
							fa.ID = int(faID.Int64)
							bal.FundAnalysis = &fa
						}
						acc.Balances = append(acc.Balances, bal)
					}
				}()
			}
			portfolio.MFAccounts = append(portfolio.MFAccounts, acc)
		}
	}

	// 3. Fetch Bond Accounts
	rows, err = db.QueryContext(ctx,
		`SELECT ba.id, ba."compCode", ba."custCode_id", ba."bondCode", ba.amount, ba."fromDate", ba."toDate", ba.issuer, ba."bondSymbol", ba.status, m."fullName", ea."fullName"
		 FROM invest_bondaccount ba
		 LEFT JOIN invest_marketing m ON ba.marketing_id = m.id
		 LEFT JOIN invest_externalagent ea ON ba.referred_by_agent_id = ea.id
		 WHERE ba."custCode_id" = $1`, p.ID)
	if err == nil {
		defer rows.Close()
		for rows.Next() {
			var bond models.BondAccount
			if err := rows.Scan(&bond.ID, &bond.CompCode, &bond.CustCode, &bond.BondCode, &bond.Amount, &bond.FromDate, &bond.ToDate, &bond.Issuer, &bond.BondSymbol, &bond.Status, &bond.MarketingName, &bond.AgentName); err == nil {
				portfolio.BondAccounts = append(portfolio.BondAccounts, bond)
			}
		}
	}
	if portfolio.BondAccounts == nil {
		portfolio.BondAccounts = []models.BondAccount{}
	}

	// 4. Fetch Private Fund Accounts
	rows, err = db.QueryContext(ctx,
		`SELECT pa.id, pa."compCode", pa."custCode_id", pa."accountID", pa."fundType", pa."openDate", pa.status, m."fullName", ea."fullName"
		 FROM invest_privatefundaccount pa
		 LEFT JOIN invest_marketing m ON pa.marketing_id = m.id
		 LEFT JOIN invest_externalagent ea ON pa.referred_by_agent_id = ea.id
		 WHERE pa."custCode_id" = $1`, p.ID)
	if err == nil {
		defer rows.Close()
		for rows.Next() {
			var acc models.PrivateFundAccount
			if err := rows.Scan(&acc.ID, &acc.CompCode, &acc.CustCode, &acc.AccountID, &acc.FundType, &acc.OpenDate, &acc.Status, &acc.MarketingName, &acc.AgentName); err != nil {
				continue
			}

			// Fetch PF Balances with latest ACTIVE FundAnalysis
			bRows, err := db.QueryContext(ctx,
				`SELECT b.id, b."compCode", b.fundCode, b."unitBalance", b.amount, b."averageCost", b."NAV", b."NAVdate",
						fa.id, fa.standard_deviation, fa.treynor_ratio, fa.sortino_ratio, fa.information_ratio,
						fa.capture_ratio_up, fa.capture_ratio_down, fa.sentiment_score, fa.sentiment_summary,
						fa.sentiment_impact_level, fa.last_calculated, fa.created_at, fa.updated_at,
						fa."createBy", fa."updateBy"
				 FROM invest_privatefundbalance b
				 LEFT JOIN LATERAL (
					SELECT id, standard_deviation, treynor_ratio, sortino_ratio, information_ratio,
					       capture_ratio_up, capture_ratio_down, sentiment_score, sentiment_summary,
					       sentiment_impact_level, last_calculated, created_at, updated_at,
					       "createBy", "updateBy"
					FROM "fundDecision_fundanalysis" 
					WHERE fund_id = (SELECT id FROM "fundDecision_fundinfo" WHERE "fundCode" = b."fundCode")
					AND status = 'ACTIVE'
					ORDER BY created_at DESC LIMIT 1
				 ) fa ON true
				 WHERE b."accountID_id" = $1`, acc.ID)

			if err == nil {
				func() {
					defer bRows.Close()
					acc.PrivateFundBalances = []models.PrivateFundBalance{} // Initialize to empty slice
					for bRows.Next() {
						var bal models.PrivateFundBalance
						var fa models.FundAnalysis
						var faID sql.NullInt64

						err := bRows.Scan(
							&bal.ID, &bal.CompCode, &bal.FundCode, &bal.UnitBalance, &bal.Amount, &bal.AverageCost, &bal.NAV, &bal.NAVdate,
							&faID, &fa.StandardDeviation, &fa.TreynorRatio, &fa.SortinoRatio, &fa.InformationRatio,
							&fa.CaptureRatioUp, &fa.CaptureRatioDown, &fa.SentimentScore, &fa.SentimentSummary,
							&fa.SentimentImpactLevel, &fa.LastCalculated, &fa.CreatedAt, &fa.UpdatedAt,
							&fa.CreateBy, &fa.UpdateBy,
						)
						if err != nil {
							log.Printf("Error scanning PF balance row: %v", err)
							continue
						}
						bal.AccountID = acc.AccountID // Map the string accountID
						if faID.Valid {
							fa.ID = int(faID.Int64)
							bal.FundAnalysis = &fa
						}
						acc.PrivateFundBalances = append(acc.PrivateFundBalances, bal)
					}
				}()
			}
			portfolio.PrivateFundAccounts = append(portfolio.PrivateFundAccounts, acc)
		}
	}

	if portfolio.MFAccounts == nil {
		portfolio.MFAccounts = []models.InvestorAccount{}
	}
	if portfolio.PrivateFundAccounts == nil {
		portfolio.PrivateFundAccounts = []models.PrivateFundAccount{}
	}

	return portfolio, nil
}
