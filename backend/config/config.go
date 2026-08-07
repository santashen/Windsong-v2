package config

import (
	"os"
	"strconv"

	"github.com/joho/godotenv"
)

// Config holds all configuration for the application
type Config struct {
	DatabaseURL    string
	Port           string
	Env            string
	AdminAPIKey    string // API Key for admin operations
	PostsRepoURL   string // Git repository URL for markdown posts
	PostsDir       string // Local directory to clone/store posts
	SiteURL        string
	RSSTitle       string
	RSSDescription string
	RSSAuthor      string
	RSSMaxItems    int
}

// Load loads configuration from environment variables
func Load() *Config {
	// Load .env file if exists
	_ = godotenv.Load()

	return &Config{
		DatabaseURL:    getEnv("DATABASE_URL", "host=localhost user=windsong password=windsong123 dbname=windsong port=5432 sslmode=disable"),
		Port:           getEnv("PORT", "8080"),
		Env:            getEnv("ENV", "development"),
		AdminAPIKey:    getEnv("ADMIN_API_KEY", ""), // Set this in production!
		PostsRepoURL:   getEnv("POSTS_REPO_URL", ""),
		PostsDir:       getEnv("POSTS_DIR", "./data/posts"),
		SiteURL:        getEnv("SITE_URL", "https://v2.windsong.top"),
		RSSTitle:       getEnv("RSS_TITLE", "Windsong Blog"),
		RSSDescription: getEnv("RSS_DESCRIPTION", "Windsong Blog RSS Feed"),
		RSSAuthor:      getEnv("RSS_AUTHOR", ""),
		RSSMaxItems:    getEnvInt("RSS_MAX_ITEMS", 20),
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

func getEnvInt(key string, defaultValue int) int {
	value, err := strconv.Atoi(os.Getenv(key))
	if err != nil || value < 1 {
		return defaultValue
	}
	return value
}
