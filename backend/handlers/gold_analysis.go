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

// GetTodayAnalysis godoc
// @Summary      Get today's gold analysis
// @Description  Returns the AI-generated gold market analysis for today
// @Tags         gold
// @Produce      json
// @Success      200  {object}  Response{data=models.GoldAnalysis}
// @Failure      500  {object}  Response
// @Router       /gold/today [get]
func (h *GoldAnalysisHandler) GetTodayAnalysis(c *gin.Context) {
	analysis, err := h.service.GetTodayAnalysis()
	if err != nil {
		Error(c, http.StatusInternalServerError, CodeExternalService, "Failed to get today's analysis: "+err.Error())
		return
	}

	Success(c, analysis)
}
