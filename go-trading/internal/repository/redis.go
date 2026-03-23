package repository

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/redis/go-redis/v9"
	"xinvest/go-trading/internal/config"
	"xinvest/go-trading/internal/models"
)

var RedisClient *redis.Client

func InitRedis() {
	RedisClient = redis.NewClient(&redis.Options{
		Addr: config.AppConfig.RedisAddr,
	})
}

func GetPortfolioFromCache(ctx context.Context, userID string) (*models.Portfolio, error) {
	key := fmt.Sprintf("portfolio:%s", userID)
	data, err := RedisClient.Get(ctx, key).Result()
	if err != nil {
		return nil, err
	}

	var portfolio models.Portfolio
	if err := json.Unmarshal([]byte(data), &portfolio); err != nil {
		return nil, err
	}

	return &portfolio, nil
}

func SetPortfolioToCache(ctx context.Context, userID string, portfolio *models.Portfolio) error {
	key := fmt.Sprintf("portfolio:%s", userID)
	data, err := json.Marshal(portfolio)
	if err != nil {
		return err
	}

	// Cache for 1 hour
	return RedisClient.Set(ctx, key, data, 1*time.Hour).Err()
}
