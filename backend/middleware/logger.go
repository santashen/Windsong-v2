package middleware

import (
	"time"

	"github.com/gin-gonic/gin"
	"github.com/rs/zerolog"

	"windsong/logger"
)

const loggerKey = "logger"

// Logger returns a Gin middleware that creates a per-request sub-logger
// (with request_id, method, path bound) and logs the completed request.
func Logger() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()

		requestID, _ := c.Get(RequestIDKey)

		sub := logger.Log.With().
			Str("request_id", requestID.(string)).
			Str("method", c.Request.Method).
			Str("path", c.Request.URL.Path).
			Logger()

		c.Set(loggerKey, &sub)

		c.Next()

		status := c.Writer.Status()
		latency := time.Since(start)

		var event *zerolog.Event
		switch {
		case status >= 500:
			event = sub.Error()
		case status >= 400:
			event = sub.Warn()
		default:
			event = sub.Info()
		}

		event.
			Int("status", status).
			Dur("latency", latency).
			Str("ip", c.ClientIP()).
			Msg("request completed")
	}
}

// GetLogger retrieves the per-request zerolog.Logger from the Gin context.
// Falls back to the global logger if none is found.
func GetLogger(c *gin.Context) *zerolog.Logger {
	if l, ok := c.Get(loggerKey); ok {
		return l.(*zerolog.Logger)
	}
	return &logger.Log
}
