package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// AuthHandler handles authentication-related HTTP requests
type AuthHandler struct {
	apiKey string
}

// NewAuthHandler creates a new AuthHandler
func NewAuthHandler(apiKey string) *AuthHandler {
	return &AuthHandler{apiKey: apiKey}
}

// VerifyRequest is the input structure for API key verification
type VerifyRequest struct {
	APIKey string `json:"apiKey" binding:"required"`
}

// VerifyResponse is the response structure for verification
type VerifyResponse struct {
	Valid   bool   `json:"valid"`
	Message string `json:"message,omitempty"`
}

// Verify godoc
// @Summary      Verify admin API key
// @Description  Validates the provided API key for admin access
// @Tags         auth
// @Accept       json
// @Produce      json
// @Param        body  body      VerifyRequest  true  "API key to verify"
// @Success      200   {object}  Response{data=VerifyResponse}
// @Failure      400   {object}  Response
// @Failure      401   {object}  Response
// @Router       /auth/verify [post]
func (h *AuthHandler) Verify(c *gin.Context) {
	var input VerifyRequest
	if err := c.ShouldBindJSON(&input); err != nil {
		Error(c, http.StatusBadRequest, CodeValidationError, "API key is required")
		return
	}

	// In development mode (no API key configured), accept any non-empty key
	if h.apiKey == "" {
		Success(c, VerifyResponse{
			Valid:   true,
			Message: "Development mode - any key accepted",
		})
		return
	}

	// Verify the API key
	if input.APIKey != h.apiKey {
		Error(c, http.StatusUnauthorized, CodeUnauthorized, "Invalid API key")
		return
	}

	Success(c, VerifyResponse{
		Valid:   true,
		Message: "Authentication successful",
	})
}
