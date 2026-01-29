package services

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"gorm.io/gorm"

	"windsong/models"
)

type GoldAnalysisService struct {
	db           *gorm.DB
	aiServiceURL string
}

func NewGoldAnalysisService(db *gorm.DB, aiServiceURL string) *GoldAnalysisService {
	return &GoldAnalysisService{
		db:           db,
		aiServiceURL: aiServiceURL,
	}
}

// AIServiceResponse represents the response from Python AI service
type AIServiceResponse struct {
	Content    string `json:"content"`
	ModelUsed  string `json:"modelUsed"`
	PromptHash string `json:"promptHash"`
}

// GetTodayAnalysis returns today's analysis, fetching from AI service if needed
func (s *GoldAnalysisService) GetTodayAnalysis() (*models.GoldAnalysis, error) {
	// Get today's date at midnight (local time)
	now := time.Now()
	today := time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, now.Location())

	// Check database cache
	var analysis models.GoldAnalysis
	err := s.db.Where("DATE(analysis_date) = DATE(?)", today).First(&analysis).Error

	if err == nil {
		// Cache hit
		return &analysis, nil
	}

	if err != gorm.ErrRecordNotFound {
		return nil, fmt.Errorf("database error: %w", err)
	}

	// Cache miss, call AI service
	result, err := s.fetchFromAIService()
	if err != nil {
		return nil, fmt.Errorf("AI service error: %w", err)
	}

	// Save to database
	analysis = models.GoldAnalysis{
		AnalysisDate: today,
		Content:      result.Content,
		ModelUsed:    result.ModelUsed,
		PromptHash:   result.PromptHash,
	}

	if err := s.db.Create(&analysis).Error; err != nil {
		return nil, fmt.Errorf("failed to save analysis: %w", err)
	}

	return &analysis, nil
}

// fetchFromAIService calls the Python AI service
func (s *GoldAnalysisService) fetchFromAIService() (*AIServiceResponse, error) {
	url := fmt.Sprintf("%s/api/gold/analyze", s.aiServiceURL)

	client := &http.Client{Timeout: 180 * time.Second} // Long timeout for LLM

	resp, err := client.Get(url)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("AI service returned status %d", resp.StatusCode)
	}

	var result AIServiceResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode response failed: %w", err)
	}

	return &result, nil
}
