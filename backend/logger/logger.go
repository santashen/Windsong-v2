package logger

import (
	"os"
	"time"

	"github.com/rs/zerolog"
)

// Log is the global logger instance.
var Log zerolog.Logger

// Init initializes the global logger.
// Production: JSON to stdout, level Info.
// Development: colored console output, level Debug.
func Init(isProduction bool) {
	if isProduction {
		Log = zerolog.New(os.Stdout).
			Level(zerolog.InfoLevel).
			With().
			Timestamp().
			Logger()
	} else {
		Log = zerolog.New(zerolog.ConsoleWriter{
			Out:        os.Stdout,
			TimeFormat: time.DateTime,
		}).
			Level(zerolog.DebugLevel).
			With().
			Timestamp().
			Logger()
	}
}
