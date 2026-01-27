package database

import (
	"log"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"windsong/config"
	"windsong/models"
)

var DB *gorm.DB

// Init initializes the database connection and runs migrations
func Init(cfg *config.Config) {
	var err error
	DB, err = gorm.Open(postgres.Open(cfg.DatabaseURL), &gorm.Config{})
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}
	log.Println("Database connected successfully")

	// Run migrations
	migrate()
}

// migrate runs database migrations
func migrate() {
	err := DB.AutoMigrate(&models.Photo{})
	if err != nil {
		log.Fatal("Failed to migrate database:", err)
	}
	log.Println("Database migration completed")
}

// GetDB returns the database instance
func GetDB() *gorm.DB {
	return DB
}
