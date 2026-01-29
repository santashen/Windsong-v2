package routes

import (
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"

	"windsong/config"
	"windsong/database"
	"windsong/handlers"
	"windsong/middleware"
	"windsong/services"
)

// Setup sets up all routes
func Setup(r *gin.Engine, cfg *config.Config) {
	// Configure CORS (only for development)
	if !cfg.IsProduction() {
		r.Use(cors.New(cors.Config{
			AllowOrigins:     []string{"http://localhost:5173", "http://localhost:3000"},
			AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
			AllowHeaders:     []string{"Origin", "Content-Type", "Authorization", "X-API-Key"},
			AllowCredentials: true,
		}))
	}

	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status":  "ok",
			"message": "Windsong Blog API is running",
		})
	})

	// Initialize services
	photoService := services.NewPhotoService(database.GetDB())
	postService := services.NewPostService(database.GetDB(), cfg.PostsRepoURL, cfg.PostsDir)
	goldAnalysisService := services.NewGoldAnalysisService(database.GetDB(), cfg.AIServiceURL)

	// Initialize handlers
	photoHandler := handlers.NewPhotoHandler(photoService)
	postHandler := handlers.NewPostHandler(postService)
	goldAnalysisHandler := handlers.NewGoldAnalysisHandler(goldAnalysisService)

	// Initialize auth handler
	authHandler := handlers.NewAuthHandler(cfg.AdminAPIKey)

	// API routes
	api := r.Group("/api")
	{
		// Existing hello endpoint
		api.GET("/hello", func(c *gin.Context) {
			c.JSON(200, gin.H{
				"message": "Hello from Windsong Blog API!",
			})
		})

		// Auth routes (public)
		auth := api.Group("/auth")
		{
			auth.POST("/verify", authHandler.Verify)
		}

		// Photo routes - Public (read-only)
		api.GET("/photos", photoHandler.GetPhotos)
		api.GET("/photos/filters", photoHandler.GetFilterOptions)
		api.GET("/photos/:id", photoHandler.GetPhoto)

		// Photo routes - Protected (require API key)
		adminPhotos := api.Group("/photos")
		adminPhotos.Use(middleware.AdminAuth(cfg.AdminAPIKey))
		{
			adminPhotos.POST("", photoHandler.CreatePhoto)
			adminPhotos.PUT("/:id", photoHandler.UpdatePhoto)
			adminPhotos.DELETE("/:id", photoHandler.DeletePhoto)
		}

		// Post routes - Public (read-only)
		api.GET("/posts", postHandler.GetPosts)
		api.GET("/posts/:slug", postHandler.GetPost)

		// Webhook routes - Protected (require API key)
		webhooks := api.Group("/webhooks")
		webhooks.Use(middleware.AdminAuth(cfg.AdminAPIKey))
		{
			webhooks.POST("/sync", postHandler.SyncPosts)
		}

		// Gold Analysis routes - Public
		api.GET("/gold/today", goldAnalysisHandler.GetTodayAnalysis)
	}
}
