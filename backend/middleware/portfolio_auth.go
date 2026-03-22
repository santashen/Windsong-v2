package middleware

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// PortfolioAuth validates the family portfolio access password from request headers.
func PortfolioAuth(password string) gin.HandlerFunc {
	return func(c *gin.Context) {
		if password == "" {
			c.Next()
			return
		}

		providedPassword := c.GetHeader("X-Portfolio-Password")
		if providedPassword == "" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"code":    40100,
				"message": "Invalid or missing portfolio access password",
			})
			c.Abort()
			return
		}

		if providedPassword != password {
			GetLogger(c).Warn().
				Str("ip", c.ClientIP()).
				Msg("portfolio auth failed: invalid password")
			c.JSON(http.StatusUnauthorized, gin.H{
				"code":    40100,
				"message": "Invalid or missing portfolio access password",
			})
			c.Abort()
			return
		}

		c.Next()
	}
}
