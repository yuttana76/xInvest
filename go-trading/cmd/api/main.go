package main

import (
	"log"
	"net/http"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"xinvest/go-trading/internal/api/handlers"
	"xinvest/go-trading/internal/config"
	"xinvest/go-trading/internal/middleware"
	"xinvest/go-trading/internal/repository"
)

func main() {
	// Load Configuration
	config.LoadConfig()

	// Initialize Repositories
	repository.InitRedis()
	repository.InitDB()

	// Initialize Gin
	r := gin.Default()

	// Global Middleware
	r.Use(middleware.ErrorHandler())

	// CORS Configuration
	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:3000"}, // Update with your frontend URL
		AllowMethods:     []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
	}))

	// Public Routes
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "up",
		})
	})

	// Protected Routes
	api := r.Group("/api/v1")
	api.Use(middleware.AuthMiddleware())
	{
		api.GET("/invesInfo", handlers.GetInvestmentInfo)
	}

	// Start Server
	log.Printf("Server starting on port %s", config.AppConfig.Port)
	if err := r.Run(":" + config.AppConfig.Port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
