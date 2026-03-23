package repository

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/lib/pq"
	"xinvest/go-trading/internal/config"
)

var DB *sql.DB

func InitDB() {
	var err error
	connStr := config.AppConfig.DBURL
	if connStr == "" {
		connStr = fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
			config.AppConfig.DBHost, config.AppConfig.DBPort, config.AppConfig.DBUser, config.AppConfig.DBPass, config.AppConfig.DBName)
	}

	DB, err = sql.Open("postgres", connStr)
	if err != nil {
		log.Fatalf("Error opening database: %v", err)
	}

	if err = DB.Ping(); err != nil {
		log.Printf("Warning: Could not connect to database: %v", err)
	}
}
