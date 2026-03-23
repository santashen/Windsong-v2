package models

import (
	"database/sql/driver"
	"encoding/json"
	"fmt"
	"time"
)

// ValuationStatus represents a simplified valuation assessment for a company.
type ValuationStatus string

const (
	ValuationUndervalued ValuationStatus = "undervalued"
	ValuationFair        ValuationStatus = "fair"
	ValuationOvervalued  ValuationStatus = "overvalued"
)

// PortfolioSnapshot stores one historical portfolio reporting period.
type PortfolioSnapshot struct {
	ID                          uint              `gorm:"primaryKey" json:"id"`
	RecordDate                  time.Time         `gorm:"type:date;not null;index" json:"recordDate"`
	TotalPrincipal              float64           `gorm:"type:numeric(18,4);not null" json:"totalPrincipal"`
	TotalMarketValue            float64           `gorm:"type:numeric(18,4);not null" json:"totalMarketValue"`
	ExpectedAnnualDividends     float64           `gorm:"type:numeric(18,4);not null" json:"expectedAnnualDividends"`
	PortfolioDividendYieldPct   float64           `gorm:"type:numeric(8,4);not null" json:"portfolioDividendYieldPct"`
	MarketValueDividendYieldPct float64           `gorm:"type:numeric(8,4);not null" json:"marketValueDividendYieldPct"`
	ManagerComment              string            `json:"managerComment"`
	Holdings                    PortfolioHoldings `gorm:"type:jsonb;serializer:json" json:"holdings"`
	CreatedAt                   time.Time         `json:"createdAt"`
	UpdatedAt                   time.Time         `json:"updatedAt"`
}

// PortfolioHoldings stores all holdings for a snapshot in JSONB.
type PortfolioHoldings struct {
	ETFs      []PortfolioETFHolding     `json:"etfs"`
	Companies []PortfolioCompanyHolding `json:"companies"`
}

// Value serializes holdings to JSON for database storage.
func (h PortfolioHoldings) Value() (driver.Value, error) {
	return json.Marshal(h)
}

// Scan deserializes holdings from database JSONB.
func (h *PortfolioHoldings) Scan(value interface{}) error {
	if value == nil {
		*h = PortfolioHoldings{}
		return nil
	}

	switch v := value.(type) {
	case []byte:
		return json.Unmarshal(v, h)
	case string:
		return json.Unmarshal([]byte(v), h)
	default:
		return fmt.Errorf("unsupported holdings type: %T", value)
	}
}

// PortfolioETFHolding is one ETF or fund position in the public report.
type PortfolioETFHolding struct {
	Name                   string  `json:"name"`
	WeightPct              float64 `json:"weightPct"`
	Shares                 int     `json:"shares"`
	AverageCost            float64 `json:"averageCost"`
	DividendPerShare       float64 `json:"dividendPerShare"`
	ExpectedAnnualDividend float64 `json:"expectedAnnualDividend"`
	YieldOnCost            float64 `json:"yieldOnCost"`
	CurrentReferencePrice  float64 `json:"currentReferencePrice"`
}

// PortfolioCompanyHolding is one business ownership position in the public report.
type PortfolioCompanyHolding struct {
	Name                    string          `json:"name"`
	ValuationStatus         ValuationStatus `json:"valuationStatus"`
	Shares                  int             `json:"shares"`
	EPS                     float64         `json:"eps"`
	PayoutRatioPct          float64         `json:"payoutRatio"`
	DPS                     float64         `json:"dps"`
	ExpectedAnnualDividend  float64         `json:"expectedAnnualDividend"`
	AverageCost             float64         `json:"averageCost"`
	CurrentPrice            float64         `json:"currentPrice"`
	HoldingDividendYieldPct float64         `json:"holdingDividendYieldPct"`
	CurrentDividendYieldPct float64         `json:"currentDividendYieldPct"`
}
