package middleware

import (
	"net/http"

	"github.com/gin-gonic/gin"

	"windsong/handlers"
)

// AdminAuth creates a middleware that validates the admin API key
func AdminAuth(apiKey string) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Skip auth if no API key is configured (development mode)
		if apiKey == "" {
			c.Next()
			return
		}

		// Get API key from header
		providedKey := c.GetHeader("X-API-Key")
		if providedKey == "" {
			// Also check Authorization header with Bearer token
			providedKey = c.GetHeader("Authorization")
			if len(providedKey) > 7 && providedKey[:7] == "Bearer " {
				providedKey = providedKey[7:]
			}
		}

		if providedKey != apiKey {
			c.JSON(http.StatusUnauthorized, handlers.Response{
				Code:    handlers.CodeUnauthorized,
				Message: "Invalid or missing API key",
			})
			c.Abort()
			return
		}

		c.Next()
	}
}
