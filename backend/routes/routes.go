package routes

import (
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"

	"windsong/config"
	"windsong/database"
	_ "windsong/docs"
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
		handlers.Success(c, gin.H{
			"status": "ok",
		})
	})

	// Swagger UI
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	// Initialize services
	photoService := services.NewPhotoService(database.GetDB())
	postService := services.NewPostService(database.GetDB(), cfg.PostsRepoURL, cfg.PostsDir)
	rssService := services.NewRSSService(database.GetDB(), services.RSSConfig{
		SiteURL:     cfg.SiteURL,
		Title:       cfg.RSSTitle,
		Description: cfg.RSSDescription,
		Author:      cfg.RSSAuthor,
		MaxItems:    cfg.RSSMaxItems,
	})

	// Initialize handlers
	photoHandler := handlers.NewPhotoHandler(photoService)
	postHandler := handlers.NewPostHandler(postService)
	rssHandler := handlers.NewRSSHandler(rssService)

	// Initialize auth handler
	authHandler := handlers.NewAuthHandler(cfg.AdminAPIKey)

	// RSS feed (public, standard XML response)
	r.GET("/rss.xml", rssHandler.GetFeed)

	// API v1 routes
	v1 := r.Group("/api/v1")
	{
		// RSS API alias (the canonical public URL is /rss.xml)
		v1.GET("/rss.xml", rssHandler.GetFeed)

		// Existing hello endpoint
		v1.GET("/hello", func(c *gin.Context) {
			handlers.Success(c, gin.H{
				"message": "Hello from Windsong Blog API!",
			})
		})

		// Auth routes (public)
		auth := v1.Group("/auth")
		{
			auth.POST("/verify", authHandler.Verify)
		}

		// Photo routes - Public (read-only)
		v1.GET("/photos", photoHandler.GetPhotos)
		v1.GET("/photos/filters", photoHandler.GetFilterOptions)
		v1.GET("/photos/:id", photoHandler.GetPhoto)

		// Photo routes - Protected (require API key)
		adminPhotos := v1.Group("/photos")
		adminPhotos.Use(middleware.AdminAuth(cfg.AdminAPIKey))
		{
			adminPhotos.POST("", photoHandler.CreatePhoto)
			adminPhotos.PUT("/:id", photoHandler.UpdatePhoto)
			adminPhotos.DELETE("/:id", photoHandler.DeletePhoto)
		}

		// Post routes - Public (read-only)
		v1.GET("/posts", postHandler.GetPosts)
		v1.GET("/posts/tags", postHandler.GetTags)
		v1.GET("/posts/:slug", postHandler.GetPost)

		// Webhook routes - Protected (require API key)
		webhooks := v1.Group("/webhooks")
		webhooks.Use(middleware.AdminAuth(cfg.AdminAPIKey))
		{
			webhooks.POST("/sync", postHandler.SyncPosts)
		}
	}
}
