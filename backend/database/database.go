package database

import (
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"windsong/config"
	"windsong/logger"
)

var DB *gorm.DB

// Init initializes the database connection
func Init(cfg *config.Config) {
	var err error
	DB, err = gorm.Open(postgres.Open(cfg.DatabaseURL), &gorm.Config{})
	if err != nil {
		logger.Log.Fatal().Err(err).Msg("failed to connect to database")
	}
	logger.Log.Info().Msg("database connected successfully")
}

// GetDB returns the database instance
func GetDB() *gorm.DB {
	return DB
}
