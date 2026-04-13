// @title           Windsong Blog API
// @version         1.0
// @description     Personal blog system API with posts and photos.

// @host            localhost:8080
// @BasePath        /api/v1

// @securityDefinitions.apikey ApiKeyAuth
// @in header
// @name X-API-Key

package main

import (
	"flag"
	"os"

	"github.com/gin-gonic/gin"

	"windsong/config"
	"windsong/database"
	"windsong/logger"
	"windsong/middleware"
	"windsong/routes"
	"windsong/services"
)

func main() {
	// Parse command line flags
	importData := flag.Bool("import", false, "Import photos from data/photos.json")
	flag.Parse()

	// Load configuration
	cfg := config.Load()

	// Initialize structured logger
	logger.Init(cfg.IsProduction())

	// Set Gin mode based on production flag
	if cfg.IsProduction() {
		gin.SetMode(gin.ReleaseMode)
	}

	// Initialize database
	database.Init(cfg)

	// Import data if flag is set
	if *importData {
		importPhotos()
		return
	}

	// Create Gin router with custom middleware
	r := gin.New()
	r.Use(middleware.RequestID())
	r.Use(middleware.Logger())
	r.Use(middleware.Recovery())

	// Setup routes
	routes.Setup(r, cfg)

	// Start server
	logger.Log.Info().Str("port", cfg.Port).Msg("server starting")
	if err := r.Run(":" + cfg.Port); err != nil {
		logger.Log.Fatal().Err(err).Msg("failed to start server")
	}
}

// importPhotos imports photos from JSON file
func importPhotos() {
	logger.Log.Info().Msg("importing photos from data/photos.json")

	// Read JSON file
	data, err := os.ReadFile("data/photos.json")
	if err != nil {
		logger.Log.Fatal().Err(err).Msg("failed to read photos.json")
	}

	// Import using service
	photoService := services.NewPhotoService(database.GetDB())
	if err := photoService.ImportFromJSON(data); err != nil {
		logger.Log.Fatal().Err(err).Msg("failed to import photos")
	}

	logger.Log.Info().Msg("photos imported successfully")
}
