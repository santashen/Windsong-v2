package database

import (
	"log"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"windsong/config"
)

var DB *gorm.DB

// Init initializes the database connection
func Init(cfg *config.Config) {
	var err error
	DB, err = gorm.Open(postgres.Open(cfg.DatabaseURL), &gorm.Config{})
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}
	log.Println("Database connected successfully")
}

// GetDB returns the database instance
func GetDB() *gorm.DB {
	return DB
}
