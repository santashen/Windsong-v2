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

// Verify handles POST /api/auth/verify
func (h *AuthHandler) Verify(c *gin.Context) {
	var input VerifyRequest
	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, VerifyResponse{
			Valid:   false,
			Message: "API key is required",
		})
		return
	}

	// In development mode (no API key configured), accept any non-empty key
	if h.apiKey == "" {
		c.JSON(http.StatusOK, VerifyResponse{
			Valid:   true,
			Message: "Development mode - any key accepted",
		})
		return
	}

	// Verify the API key
	if input.APIKey != h.apiKey {
		c.JSON(http.StatusUnauthorized, VerifyResponse{
			Valid:   false,
			Message: "Invalid API key",
		})
		return
	}

	c.JSON(http.StatusOK, VerifyResponse{
		Valid:   true,
		Message: "Authentication successful",
	})
}
