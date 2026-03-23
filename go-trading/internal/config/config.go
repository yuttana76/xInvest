package config

import (
	"log"

	"github.com/spf13/viper"
)

type Config struct {
	Port      string `mapstructure:"PORT"`
	JWTSecret string `mapstructure:"JWT_SECRET_KEY"`
	DBURL     string `mapstructure:"DB_URL"`
	RedisAddr string `mapstructure:"REDIS_ADDR"`
	DBHost    string `mapstructure:"POSTGRES_HOST"`
	DBPort    string `mapstructure:"POSTGRES_PORT"`
	DBUser    string `mapstructure:"POSTGRES_USER"`
	DBPass    string `mapstructure:"POSTGRES_PASSWORD"`
	DBName    string `mapstructure:"POSTGRES_DB"`
}

var AppConfig *Config

func LoadConfig() {
	viper.AutomaticEnv()

	// Explicitly bind environment variables to keys
	viper.BindEnv("PORT", "PORT")
	viper.BindEnv("JWT_SECRET_KEY", "JWT_SECRET_KEY")
	viper.BindEnv("REDIS_ADDR", "REDIS_ADDR")
	viper.BindEnv("POSTGRES_HOST", "POSTGRES_HOST")
	viper.BindEnv("POSTGRES_PORT", "POSTGRES_PORT")
	viper.BindEnv("POSTGRES_USER", "POSTGRES_USER")
	viper.BindEnv("POSTGRES_PASSWORD", "POSTGRES_PASSWORD")
	viper.BindEnv("POSTGRES_DB", "POSTGRES_DB")

	// Fallback to reading .env file if it exists
	viper.AddConfigPath(".")
	viper.SetConfigName(".env")
	viper.SetConfigType("env")
	if err := viper.ReadInConfig(); err != nil {
		log.Printf("Note: .env file not found, using environment variables")
	}

	AppConfig = &Config{}
	
	// Manually map fields to ensure they are picked up from environment variables
	AppConfig.Port = viper.GetString("PORT")
	AppConfig.JWTSecret = viper.GetString("JWT_SECRET_KEY")
	AppConfig.RedisAddr = viper.GetString("REDIS_ADDR")
	AppConfig.DBHost = viper.GetString("POSTGRES_HOST")
	AppConfig.DBPort = viper.GetString("POSTGRES_PORT")
	AppConfig.DBUser = viper.GetString("POSTGRES_USER")
	AppConfig.DBPass = viper.GetString("POSTGRES_PASSWORD")
	AppConfig.DBName = viper.GetString("POSTGRES_DB")

	log.Printf("Configuration loaded. JWT Secret length: %d", len(AppConfig.JWTSecret))
	log.Printf("Redis Addr: %s, DB Host: %s", AppConfig.RedisAddr, AppConfig.DBHost)

	// Set defaults if not provided
	if AppConfig.Port == "" {
		AppConfig.Port = "8080"
	}
	if AppConfig.RedisAddr == "" {
		AppConfig.RedisAddr = "redis:6379"
	}
}
