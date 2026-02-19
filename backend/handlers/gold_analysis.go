package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type GoldAnalysisHandler struct {
	service GoldAnalysisServiceInterface
}

func NewGoldAnalysisHandler(service GoldAnalysisServiceInterface) *GoldAnalysisHandler {
	return &GoldAnalysisHandler{service: service}
}

// GetTodayAnalysis handles GET /api/gold/today
func (h *GoldAnalysisHandler) GetTodayAnalysis(c *gin.Context) {
	analysis, err := h.service.GetTodayAnalysis()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get today's analysis",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, analysis)
}
