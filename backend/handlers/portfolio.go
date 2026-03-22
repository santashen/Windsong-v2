package handlers

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"

	"windsong/middleware"
	"windsong/models"
)

// PortfolioHandler handles portfolio snapshot requests.
type PortfolioHandler struct {
	portfolioService PortfolioServiceInterface
}

// NewPortfolioHandler creates a new PortfolioHandler.
func NewPortfolioHandler(portfolioService PortfolioServiceInterface) *PortfolioHandler {
	return &PortfolioHandler{portfolioService: portfolioService}
}

// PortfolioAccessHandler validates the family portfolio access password.
type PortfolioAccessHandler struct {
	password string
}

// NewPortfolioAccessHandler creates a new PortfolioAccessHandler.
func NewPortfolioAccessHandler(password string) *PortfolioAccessHandler {
	return &PortfolioAccessHandler{password: password}
}

// VerifyPortfolioAccessRequest is the input structure for family access password validation.
type VerifyPortfolioAccessRequest struct {
	Password string `json:"password" binding:"required"`
}

// VerifyPortfolioAccessResponse is the response structure for family access validation.
type VerifyPortfolioAccessResponse struct {
	Valid   bool   `json:"valid"`
	Message string `json:"message,omitempty"`
}

// PortfolioSnapshotInput is the input for creating a new portfolio snapshot.
type PortfolioSnapshotInput struct {
	RecordDate                  string                 `json:"recordDate" binding:"required,datetime=2006-01-02"`
	TotalPrincipal              float64                `json:"totalPrincipal" binding:"required,gte=0"`
	TotalMarketValue            float64                `json:"totalMarketValue" binding:"required,gte=0"`
	ExpectedAnnualDividends     float64                `json:"expectedAnnualDividends" binding:"required,gte=0"`
	PortfolioDividendYieldPct   float64                `json:"portfolioDividendYieldPct" binding:"required,gte=0"`
	MarketValueDividendYieldPct float64                `json:"marketValueDividendYieldPct" binding:"required,gte=0"`
	ManagerComment              string                 `json:"managerComment" binding:"max=5000"`
	Holdings                    PortfolioHoldingsInput `json:"holdings" binding:"required"`
}

// PortfolioHoldingsInput is the JSON body structure for all holdings.
type PortfolioHoldingsInput struct {
	ETFs      []PortfolioETFHoldingInput     `json:"etfs" binding:"required"`
	Companies []PortfolioCompanyHoldingInput `json:"companies" binding:"required"`
}

// PortfolioETFHoldingInput is one ETF row submitted by admin.
type PortfolioETFHoldingInput struct {
	Name                   string  `json:"name" binding:"required,max=200"`
	WeightPct              float64 `json:"weightPct" binding:"required,gte=0,lte=100"`
	Shares                 int     `json:"shares" binding:"required,gte=0"`
	AverageCost            float64 `json:"averageCost" binding:"required,gte=0"`
	DividendPerShare       float64 `json:"dividendPerShare" binding:"required,gte=0"`
	ExpectedAnnualDividend float64 `json:"expectedAnnualDividend" binding:"required,gte=0"`
	YieldOnCost            float64 `json:"yieldOnCost" binding:"required,gte=0"`
	CurrentReferencePrice  float64 `json:"currentReferencePrice" binding:"required,gte=0"`
}

// PortfolioCompanyHoldingInput is one company row submitted by admin.
type PortfolioCompanyHoldingInput struct {
	Name                    string  `json:"name" binding:"required,max=200"`
	ValuationStatus         string  `json:"valuationStatus" binding:"required,oneof=undervalued fair overvalued"`
	Shares                  int     `json:"shares" binding:"required,gte=0"`
	EPS                     float64 `json:"eps" binding:"required,gte=0"`
	PayoutRatioPct          float64 `json:"payoutRatio" binding:"required,gte=0,lte=100"`
	DPS                     float64 `json:"dps" binding:"required,gte=0"`
	ExpectedAnnualDividend  float64 `json:"expectedAnnualDividend" binding:"required,gte=0"`
	AverageCost             float64 `json:"averageCost" binding:"required,gte=0"`
	CurrentPrice            float64 `json:"currentPrice" binding:"required,gte=0"`
	HoldingDividendYieldPct float64 `json:"holdingDividendYieldPct" binding:"required,gte=0"`
	CurrentDividendYieldPct float64 `json:"currentDividendYieldPct" binding:"required,gte=0"`
}

// CreateSnapshot creates a new historical portfolio snapshot.
func (h *PortfolioHandler) CreateSnapshot(c *gin.Context) {
	var input PortfolioSnapshotInput
	if err := c.ShouldBindJSON(&input); err != nil {
		ValidationError(c, err)
		return
	}

	recordDate, _ := time.Parse("2006-01-02", input.RecordDate)

	snapshot := &models.PortfolioSnapshot{
		RecordDate:                  recordDate,
		TotalPrincipal:              input.TotalPrincipal,
		TotalMarketValue:            input.TotalMarketValue,
		ExpectedAnnualDividends:     input.ExpectedAnnualDividends,
		PortfolioDividendYieldPct:   input.PortfolioDividendYieldPct,
		MarketValueDividendYieldPct: input.MarketValueDividendYieldPct,
		ManagerComment:              input.ManagerComment,
		Holdings: models.PortfolioHoldings{
			ETFs:      make([]models.PortfolioETFHolding, 0, len(input.Holdings.ETFs)),
			Companies: make([]models.PortfolioCompanyHolding, 0, len(input.Holdings.Companies)),
		},
	}

	for _, etf := range input.Holdings.ETFs {
		snapshot.Holdings.ETFs = append(snapshot.Holdings.ETFs, models.PortfolioETFHolding{
			Name:                   etf.Name,
			WeightPct:              etf.WeightPct,
			Shares:                 etf.Shares,
			AverageCost:            etf.AverageCost,
			DividendPerShare:       etf.DividendPerShare,
			ExpectedAnnualDividend: etf.ExpectedAnnualDividend,
			YieldOnCost:            etf.YieldOnCost,
			CurrentReferencePrice:  etf.CurrentReferencePrice,
		})
	}

	for _, company := range input.Holdings.Companies {
		snapshot.Holdings.Companies = append(snapshot.Holdings.Companies, models.PortfolioCompanyHolding{
			Name:                    company.Name,
			ValuationStatus:         models.ValuationStatus(company.ValuationStatus),
			Shares:                  company.Shares,
			EPS:                     company.EPS,
			PayoutRatioPct:          company.PayoutRatioPct,
			DPS:                     company.DPS,
			ExpectedAnnualDividend:  company.ExpectedAnnualDividend,
			AverageCost:             company.AverageCost,
			CurrentPrice:            company.CurrentPrice,
			HoldingDividendYieldPct: company.HoldingDividendYieldPct,
			CurrentDividendYieldPct: company.CurrentDividendYieldPct,
		})
	}

	if err := h.portfolioService.CreateSnapshot(snapshot); err != nil {
		middleware.GetLogger(c).Error().Err(err).Msg("failed to create portfolio snapshot")
		Error(c, http.StatusInternalServerError, CodeInternalError, "Failed to create portfolio snapshot")
		return
	}

	SuccessCreated(c, snapshot)
}

// GetLatestSnapshot returns the latest portfolio snapshot.
func (h *PortfolioHandler) GetLatestSnapshot(c *gin.Context) {
	snapshot, err := h.portfolioService.GetLatestSnapshot()
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			Error(c, http.StatusNotFound, CodeNotFound, "No portfolio snapshot found")
			return
		}
		middleware.GetLogger(c).Error().Err(err).Msg("failed to fetch latest portfolio snapshot")
		Error(c, http.StatusInternalServerError, CodeInternalError, "Failed to fetch portfolio snapshot")
		return
	}

	Success(c, snapshot)
}

// Verify validates the family portfolio access password.
func (h *PortfolioAccessHandler) Verify(c *gin.Context) {
	var input VerifyPortfolioAccessRequest
	if err := c.ShouldBindJSON(&input); err != nil {
		Error(c, http.StatusBadRequest, CodeValidationError, "Password is required")
		return
	}

	if h.password == "" {
		Success(c, VerifyPortfolioAccessResponse{
			Valid:   true,
			Message: "Development mode - password check bypassed",
		})
		return
	}

	if input.Password != h.password {
		middleware.GetLogger(c).Warn().
			Str("ip", c.ClientIP()).
			Msg("portfolio access verify failed: invalid password")
		Error(c, http.StatusUnauthorized, CodeUnauthorized, "Invalid password")
		return
	}

	Success(c, VerifyPortfolioAccessResponse{
		Valid:   true,
		Message: "Access granted",
	})
}
