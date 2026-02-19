package handlers

import (
	"errors"
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/go-playground/validator/v10"
)

// Response is the unified API response envelope.
type Response struct {
	Code    int         `json:"code"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
}

// Business error codes (HTTP status prefix + sub-code).
const (
	CodeSuccess         = 0
	CodeBadRequest      = 40000
	CodeValidationError = 40001
	CodeUnauthorized    = 40100
	CodeNotFound        = 40400
	CodeInternalError   = 50000
	CodeExternalService = 50200
)

// Success sends a 200 response with data.
func Success(c *gin.Context, data interface{}) {
	c.JSON(http.StatusOK, Response{
		Code:    CodeSuccess,
		Message: "success",
		Data:    data,
	})
}

// SuccessCreated sends a 201 response with data.
func SuccessCreated(c *gin.Context, data interface{}) {
	c.JSON(http.StatusCreated, Response{
		Code:    CodeSuccess,
		Message: "success",
		Data:    data,
	})
}

// Error sends an error response with the given HTTP status and business code.
func Error(c *gin.Context, httpStatus int, code int, message string) {
	c.JSON(httpStatus, Response{
		Code:    code,
		Message: message,
	})
}

// ValidationError sends a 400 response with structured validation error details.
func ValidationError(c *gin.Context, err error) {
	var ve validator.ValidationErrors
	if errors.As(err, &ve) {
		details := make([]string, len(ve))
		for i, fe := range ve {
			details[i] = fmt.Sprintf("field '%s' failed on '%s' validation", fe.Field(), fe.Tag())
		}
		c.JSON(http.StatusBadRequest, Response{
			Code:    CodeValidationError,
			Message: "Validation failed",
			Data:    details,
		})
		return
	}
	Error(c, http.StatusBadRequest, CodeBadRequest, err.Error())
}
