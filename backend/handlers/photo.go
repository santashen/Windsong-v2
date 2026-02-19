package handlers

import (
	"encoding/json"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"

	"windsong/models"
	"windsong/services"
)

// PhotoHandler handles photo-related HTTP requests
type PhotoHandler struct {
	photoService PhotoServiceInterface
}

// NewPhotoHandler creates a new PhotoHandler
func NewPhotoHandler(photoService PhotoServiceInterface) *PhotoHandler {
	return &PhotoHandler{photoService: photoService}
}

// GetPhotos handles GET /api/photos
func (h *PhotoHandler) GetPhotos(c *gin.Context) {
	// Parse query parameters
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("pageSize", "20"))
	year, _ := strconv.Atoi(c.Query("year"))
	location := c.Query("location")
	tagsStr := c.Query("tags")

	// Parse tags
	var tags []string
	if tagsStr != "" {
		tags = services.ParseTags(tagsStr)
	}

	// Build query
	query := services.PhotoQuery{
		Page:     page,
		PageSize: pageSize,
		Year:     year,
		Location: location,
		Tags:     tags,
	}

	// Get photos
	response, err := h.photoService.GetPhotos(query)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to fetch photos",
		})
		return
	}

	c.JSON(http.StatusOK, response)
}

// GetFilterOptions handles GET /api/photos/filters
func (h *PhotoHandler) GetFilterOptions(c *gin.Context) {
	options, err := h.photoService.GetFilterOptions()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to fetch filter options",
		})
		return
	}

	c.JSON(http.StatusOK, options)
}

// PhotoInput is the input structure for creating/updating photos
type PhotoInput struct {
	URL         string   `json:"url" binding:"required"`
	Thumbnail   string   `json:"thumbnail"`
	Title       string   `json:"title" binding:"required"`
	Description string   `json:"description"`
	Date        string   `json:"date" binding:"required"` // Format: YYYY-MM-DD
	Location    string   `json:"location"`
	City        string   `json:"city"`
	Country     string   `json:"country"`
	Tags        []string `json:"tags"`
	AspectRatio string   `json:"aspectRatio"`
}

// GetPhoto handles GET /api/photos/:id
func (h *PhotoHandler) GetPhoto(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid photo ID"})
		return
	}

	photo, err := h.photoService.GetPhotoByID(uint(id))
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Photo not found"})
		return
	}

	c.JSON(http.StatusOK, photo)
}

// CreatePhoto handles POST /api/photos
func (h *PhotoHandler) CreatePhoto(c *gin.Context) {
	var input PhotoInput
	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Parse date
	date, err := time.Parse("2006-01-02", input.Date)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid date format, use YYYY-MM-DD"})
		return
	}

	// Convert tags to JSON string
	tagsJSON, _ := json.Marshal(input.Tags)

	photo := &models.Photo{
		URL:         input.URL,
		Thumbnail:   input.Thumbnail,
		Title:       input.Title,
		Description: input.Description,
		Date:        date,
		Location:    input.Location,
		City:        input.City,
		Country:     input.Country,
		Tags:        string(tagsJSON),
		AspectRatio: input.AspectRatio,
	}

	if err := h.photoService.CreatePhoto(photo); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create photo"})
		return
	}

	c.JSON(http.StatusCreated, photo)
}

// UpdatePhoto handles PUT /api/photos/:id
func (h *PhotoHandler) UpdatePhoto(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid photo ID"})
		return
	}

	var input PhotoInput
	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Parse date
	date, err := time.Parse("2006-01-02", input.Date)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid date format, use YYYY-MM-DD"})
		return
	}

	// Convert tags to JSON string
	tagsJSON, _ := json.Marshal(input.Tags)

	photo := &models.Photo{
		URL:         input.URL,
		Thumbnail:   input.Thumbnail,
		Title:       input.Title,
		Description: input.Description,
		Date:        date,
		Location:    input.Location,
		City:        input.City,
		Country:     input.Country,
		Tags:        string(tagsJSON),
		AspectRatio: input.AspectRatio,
	}

	if err := h.photoService.UpdatePhoto(uint(id), photo); err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Photo not found"})
		return
	}

	// Get updated photo
	updated, _ := h.photoService.GetPhotoByID(uint(id))
	c.JSON(http.StatusOK, updated)
}

// DeletePhoto handles DELETE /api/photos/:id
func (h *PhotoHandler) DeletePhoto(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid photo ID"})
		return
	}

	if err := h.photoService.DeletePhoto(uint(id)); err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Photo not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Photo deleted successfully"})
}
