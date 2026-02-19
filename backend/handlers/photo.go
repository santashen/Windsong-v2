package handlers

import (
	"encoding/json"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"

	"windsong/middleware"
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

// GetPhotos godoc
// @Summary      List photos
// @Description  Returns paginated photos with optional filters
// @Tags         photos
// @Produce      json
// @Param        page      query  int     false  "Page number"      default(1)
// @Param        pageSize  query  int     false  "Items per page"   default(20)
// @Param        year      query  int     false  "Filter by year"
// @Param        location  query  string  false  "Filter by location"
// @Param        tags      query  string  false  "Filter by tags (comma-separated)"
// @Success      200  {object}  Response{data=models.PhotoResponse}
// @Failure      400  {object}  Response
// @Failure      500  {object}  Response
// @Router       /photos [get]
func (h *PhotoHandler) GetPhotos(c *gin.Context) {
	var query PhotoListQuery
	if err := c.ShouldBindQuery(&query); err != nil {
		ValidationError(c, err)
		return
	}

	// Apply defaults
	if query.Page == 0 {
		query.Page = 1
	}
	if query.PageSize == 0 {
		query.PageSize = 20
	}

	// Parse tags
	var tags []string
	if query.Tags != "" {
		tags = services.ParseTags(query.Tags)
	}

	// Build service query
	serviceQuery := services.PhotoQuery{
		Page:     query.Page,
		PageSize: query.PageSize,
		Year:     query.Year,
		Location: query.Location,
		Tags:     tags,
	}

	// Get photos
	response, err := h.photoService.GetPhotos(serviceQuery)
	if err != nil {
		middleware.GetLogger(c).Error().Err(err).Msg("failed to fetch photos")
		Error(c, http.StatusInternalServerError, CodeInternalError, "Failed to fetch photos")
		return
	}

	Success(c, response)
}

// GetFilterOptions godoc
// @Summary      Get photo filter options
// @Description  Returns available filter options (years, locations, tags)
// @Tags         photos
// @Produce      json
// @Success      200  {object}  Response{data=models.FilterOptions}
// @Failure      500  {object}  Response
// @Router       /photos/filters [get]
func (h *PhotoHandler) GetFilterOptions(c *gin.Context) {
	options, err := h.photoService.GetFilterOptions()
	if err != nil {
		middleware.GetLogger(c).Error().Err(err).Msg("failed to fetch filter options")
		Error(c, http.StatusInternalServerError, CodeInternalError, "Failed to fetch filter options")
		return
	}

	Success(c, options)
}

// PhotoInput is the input structure for creating/updating photos
type PhotoInput struct {
	URL         string   `json:"url" binding:"required,url"`
	Thumbnail   string   `json:"thumbnail" binding:"omitempty,url"`
	Title       string   `json:"title" binding:"required,min=1,max=200"`
	Description string   `json:"description" binding:"max=2000"`
	Date        string   `json:"date" binding:"required,datetime=2006-01-02"`
	Location    string   `json:"location" binding:"max=200"`
	City        string   `json:"city" binding:"max=100"`
	Country     string   `json:"country" binding:"max=100"`
	Tags        []string `json:"tags" binding:"max=20,dive,min=1,max=50"`
	AspectRatio string   `json:"aspectRatio" binding:"omitempty,max=20"`
}

// PhotoListQuery is the query parameter structure for listing photos
type PhotoListQuery struct {
	Page     int    `form:"page" binding:"omitempty,min=1"`
	PageSize int    `form:"pageSize" binding:"omitempty,min=1,max=100"`
	Year     int    `form:"year" binding:"omitempty,min=1900,max=2100"`
	Location string `form:"location" binding:"omitempty,max=200"`
	Tags     string `form:"tags" binding:"omitempty,max=500"`
}

// GetPhoto godoc
// @Summary      Get a photo
// @Description  Returns a single photo by ID
// @Tags         photos
// @Produce      json
// @Param        id  path  int  true  "Photo ID"
// @Success      200  {object}  Response{data=models.Photo}
// @Failure      400  {object}  Response
// @Failure      404  {object}  Response
// @Router       /photos/{id} [get]
func (h *PhotoHandler) GetPhoto(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		Error(c, http.StatusBadRequest, CodeBadRequest, "Invalid photo ID")
		return
	}

	photo, err := h.photoService.GetPhotoByID(uint(id))
	if err != nil {
		middleware.GetLogger(c).Warn().Err(err).Uint64("photo_id", id).Msg("photo not found")
		Error(c, http.StatusNotFound, CodeNotFound, "Photo not found")
		return
	}

	Success(c, photo)
}

// CreatePhoto godoc
// @Summary      Create a photo
// @Description  Creates a new photo entry
// @Tags         photos
// @Accept       json
// @Produce      json
// @Security     ApiKeyAuth
// @Param        body  body      PhotoInput  true  "Photo data"
// @Success      201   {object}  Response{data=models.Photo}
// @Failure      400   {object}  Response
// @Failure      401   {object}  Response
// @Failure      500   {object}  Response
// @Router       /photos [post]
func (h *PhotoHandler) CreatePhoto(c *gin.Context) {
	var input PhotoInput
	if err := c.ShouldBindJSON(&input); err != nil {
		ValidationError(c, err)
		return
	}

	// Parse date (format already validated by binding tag)
	date, _ := time.Parse("2006-01-02", input.Date)

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
		middleware.GetLogger(c).Error().Err(err).Msg("failed to create photo")
		Error(c, http.StatusInternalServerError, CodeInternalError, "Failed to create photo")
		return
	}

	SuccessCreated(c, photo)
}

// UpdatePhoto godoc
// @Summary      Update a photo
// @Description  Updates an existing photo by ID
// @Tags         photos
// @Accept       json
// @Produce      json
// @Security     ApiKeyAuth
// @Param        id    path      int         true  "Photo ID"
// @Param        body  body      PhotoInput  true  "Photo data"
// @Success      200   {object}  Response{data=models.Photo}
// @Failure      400   {object}  Response
// @Failure      401   {object}  Response
// @Failure      404   {object}  Response
// @Router       /photos/{id} [put]
func (h *PhotoHandler) UpdatePhoto(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		Error(c, http.StatusBadRequest, CodeBadRequest, "Invalid photo ID")
		return
	}

	var input PhotoInput
	if err := c.ShouldBindJSON(&input); err != nil {
		ValidationError(c, err)
		return
	}

	// Parse date (format already validated by binding tag)
	date, _ := time.Parse("2006-01-02", input.Date)

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
		middleware.GetLogger(c).Warn().Err(err).Uint64("photo_id", id).Msg("photo not found for update")
		Error(c, http.StatusNotFound, CodeNotFound, "Photo not found")
		return
	}

	// Get updated photo
	updated, _ := h.photoService.GetPhotoByID(uint(id))
	Success(c, updated)
}

// DeletePhoto godoc
// @Summary      Delete a photo
// @Description  Deletes a photo by ID
// @Tags         photos
// @Produce      json
// @Security     ApiKeyAuth
// @Param        id  path  int  true  "Photo ID"
// @Success      200  {object}  Response
// @Failure      400  {object}  Response
// @Failure      401  {object}  Response
// @Failure      404  {object}  Response
// @Router       /photos/{id} [delete]
func (h *PhotoHandler) DeletePhoto(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		Error(c, http.StatusBadRequest, CodeBadRequest, "Invalid photo ID")
		return
	}

	if err := h.photoService.DeletePhoto(uint(id)); err != nil {
		middleware.GetLogger(c).Warn().Err(err).Uint64("photo_id", id).Msg("photo not found for delete")
		Error(c, http.StatusNotFound, CodeNotFound, "Photo not found")
		return
	}

	Success(c, nil)
}
