package main

import (
	"log"
	"os"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var db *gorm.DB

func main() {
	// 加载环境变量
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using defaults")
	}

	// 初始化数据库
	initDB()

	// 创建 Gin 路由
	r := gin.Default()

	// 配置 CORS
	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:5173", "http://localhost:3000"},
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Authorization"},
		AllowCredentials: true,
	}))

	// 健康检查
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status": "ok",
			"message": "Windsong Blog API is running",
		})
	})

	// API 路由组
	api := r.Group("/api")
	{
		api.GET("/hello", func(c *gin.Context) {
			c.JSON(200, gin.H{
				"message": "Hello from Windsong Blog API!",
			})
		})
	}

	// 获取端口
	port := getEnv("PORT", "8080")
	log.Printf("Server starting on port %s...", port)

	if err := r.Run(":" + port); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}

// initDB 初始化数据库连接
func initDB() {
	dsn := getEnv("DATABASE_URL", "host=localhost user=windsong password=windsong123 dbname=windsong port=5432 sslmode=disable")
	var err error
	db, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}
	log.Println("Database connected successfully")
}

// getEnv 获取环境变量，如果不存在则返回默认值
func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
