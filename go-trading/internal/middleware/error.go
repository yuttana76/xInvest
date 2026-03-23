package middleware

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type APIError struct {
	Status  int    `json:"status"`
	Message string `json:"message"`
}

func ErrorHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Next()

		if len(c.Errors) > 0 {
			err := c.Errors.Last()
			c.JSON(http.StatusInternalServerError, APIError{
				Status:  http.StatusInternalServerError,
				Message: err.Error(),
			})
		}
	}
}
