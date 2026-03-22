package services

import (
	"windsong/models"

	"gorm.io/gorm"
)

// PortfolioService handles portfolio snapshot persistence and retrieval.
type PortfolioService struct {
	db *gorm.DB
}

// NewPortfolioService creates a new PortfolioService.
func NewPortfolioService(db *gorm.DB) *PortfolioService {
	return &PortfolioService{db: db}
}

// CreateSnapshot inserts a new historical snapshot.
func (s *PortfolioService) CreateSnapshot(snapshot *models.PortfolioSnapshot) error {
	return s.db.Create(snapshot).Error
}

// GetLatestSnapshot returns the most recent snapshot by record date, then creation time.
func (s *PortfolioService) GetLatestSnapshot() (*models.PortfolioSnapshot, error) {
	var snapshot models.PortfolioSnapshot
	err := s.db.
		Order("record_date DESC").
		Order("created_at DESC").
		First(&snapshot).Error
	if err != nil {
		return nil, err
	}
	return &snapshot, nil
}
