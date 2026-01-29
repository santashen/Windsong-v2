package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"

	"windsong/services"
)

type GoldAnalysisHandler struct {
	service *services.GoldAnalysisService
}

func NewGoldAnalysisHandler(service *services.GoldAnalysisService) *GoldAnalysisHandler {
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
