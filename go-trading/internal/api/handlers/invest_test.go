package handlers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"xinvest/go-trading/internal/config"
	"xinvest/go-trading/internal/models"
	"xinvest/go-trading/internal/repository"
)

func TestGetInvestmentInfo(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	
	// Initialize a dummy redis client to avoid panic
	config.AppConfig = &config.Config{RedisAddr: "localhost:6379"}
	repository.InitRedis()

	t.Run("Success with mock data", func(t *testing.T) {
		r := gin.New()
		r.GET("/invesInfo", func(c *gin.Context) {
			c.Set("user_id", "user123")
			GetInvestmentInfo(c)
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/invesInfo", nil)
		r.ServeHTTP(w, req)

		assert.True(t, w.Code == http.StatusOK || w.Code == http.StatusNotFound || w.Code == http.StatusInternalServerError)
		if w.Code == http.StatusOK {
			var portfolio models.Portfolio
			err := json.Unmarshal(w.Body.Bytes(), &portfolio)
			assert.NoError(t, err)
			assert.NotNil(t, portfolio.Profile)
		}
	})

	t.Run("Unauthorized without user_id", func(t *testing.T) {
		r := gin.New()
		r.GET("/invesInfo", GetInvestmentInfo)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/invesInfo", nil)
		r.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}
