// @title           Windsong Blog API
// @version         1.0
// @description     Personal blog system API with posts, photos, and gold analysis.

// @host            localhost:8080
// @BasePath        /api/v1

// @securityDefinitions.apikey ApiKeyAuth
// @in header
// @name X-API-Key

package main

import (
	"flag"
	"log"
	"os"

	"github.com/gin-gonic/gin"

	"windsong/config"
	"windsong/database"
	"windsong/routes"
	"windsong/services"
)

func main() {
	// Parse command line flags
	importData := flag.Bool("import", false, "Import photos from data/photos.json")
	flag.Parse()

	// Load configuration
	cfg := config.Load()

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

	// Create Gin router
	r := gin.Default()

	// Setup routes
	routes.Setup(r, cfg)

	// Start server
	log.Printf("Server starting on port %s...", cfg.Port)
	if err := r.Run(":" + cfg.Port); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}

// importPhotos imports photos from JSON file
func importPhotos() {
	log.Println("Importing photos from data/photos.json...")

	// Read JSON file
	data, err := os.ReadFile("data/photos.json")
	if err != nil {
		log.Fatal("Failed to read photos.json:", err)
	}

	// Import using service
	photoService := services.NewPhotoService(database.GetDB())
	if err := photoService.ImportFromJSON(data); err != nil {
		log.Fatal("Failed to import photos:", err)
	}

	log.Println("Photos imported successfully!")
}
