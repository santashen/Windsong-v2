package config

import (
	"os"

	"github.com/joho/godotenv"
)

// Config holds all configuration for the application
type Config struct {
	DatabaseURL  string
	Port         string
	Env          string
	AdminAPIKey  string // API Key for admin operations
	PostsRepoURL string // Git repository URL for markdown posts
	PostsDir     string // Local directory to clone/store posts
	AIServiceURL string // AI service URL for gold analysis
}

// Load loads configuration from environment variables
func Load() *Config {
	// Load .env file if exists
	_ = godotenv.Load()

	return &Config{
		DatabaseURL:  getEnv("DATABASE_URL", "host=localhost user=windsong password=windsong123 dbname=windsong port=5432 sslmode=disable"),
		Port:         getEnv("PORT", "8080"),
		Env:          getEnv("ENV", "development"),
		AdminAPIKey:  getEnv("ADMIN_API_KEY", ""), // Set this in production!
		PostsRepoURL: getEnv("POSTS_REPO_URL", ""),
		PostsDir:     getEnv("POSTS_DIR", "./data/posts"),
		AIServiceURL: getEnv("AI_SERVICE_URL", "http://localhost:8000"),
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
