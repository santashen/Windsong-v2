package models

import (
	"time"
)

// GoldAnalysis represents a daily gold analysis report
type GoldAnalysis struct {
	ID           uint      `gorm:"primaryKey" json:"id"`
	AnalysisDate time.Time `gorm:"uniqueIndex;not null" json:"analysisDate"`
	Content      string    `gorm:"type:text;not null" json:"content"`
	ModelUsed    string    `gorm:"size:50" json:"modelUsed"`
	PromptHash   string    `gorm:"size:64" json:"promptHash"`
	CreatedAt    time.Time `json:"createdAt"`
	UpdatedAt    time.Time `json:"updatedAt"`
}
