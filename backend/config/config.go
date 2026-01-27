package config

import (
	"os"

	"github.com/joho/godotenv"
)

// Config holds all configuration for the application
type Config struct {
	DatabaseURL string
	Port        string
	Env         string
	AdminAPIKey string // API Key for admin operations
}

// Load loads configuration from environment variables
func Load() *Config {
	// Load .env file if exists
	_ = godotenv.Load()

	return &Config{
		DatabaseURL: getEnv("DATABASE_URL", "host=localhost user=windsong password=windsong123 dbname=windsong port=5432 sslmode=disable"),
		Port:        getEnv("PORT", "8080"),
		Env:         getEnv("ENV", "development"),
		AdminAPIKey: getEnv("ADMIN_API_KEY", ""), // Set this in production!
	}
}

// IsProduction returns true if running in production mode
func (c *Config) IsProduction() bool {
	return c.Env == "production"
}

// getEnv gets an environment variable or returns a default value
func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
