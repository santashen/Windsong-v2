package services

import (
	"encoding/json"
	"math"
	"strings"
	"time"

	"gorm.io/gorm"

	"windsong/models"
)

// PhotoService handles photo business logic
type PhotoService struct {
	db *gorm.DB
}

// NewPhotoService creates a new PhotoService
func NewPhotoService(db *gorm.DB) *PhotoService {
	return &PhotoService{db: db}
}

// PhotoQuery holds query parameters for photo list
type PhotoQuery struct {
	Page     int
	PageSize int
	Year     int
	Location string
	Tags     []string
}

// GetPhotos returns paginated and filtered photos
func (s *PhotoService) GetPhotos(query PhotoQuery) (*models.PhotoResponse, error) {
	// Set defaults
	if query.Page < 1 {
		query.Page = 1
	}
	if query.PageSize < 1 || query.PageSize > 100 {
		query.PageSize = 20
	}

	var photos []models.Photo
	var total int64

	// Build query
	db := s.db.Model(&models.Photo{})

	// Apply year filter
	if query.Year > 0 {
		db = db.Where("EXTRACT(YEAR FROM date) = ?", query.Year)
	}

	// Apply location filter
	if query.Location != "" {
		db = db.Where("location = ?", query.Location)
	}

	// Apply tags filter (photo must contain ALL specified tags)
	if len(query.Tags) > 0 {
		for _, tag := range query.Tags {
			// Search for tag in JSON array string
			db = db.Where("tags LIKE ?", "%\""+tag+"\"%")
		}
	}

	// Get total count
	if err := db.Count(&total).Error; err != nil {
		return nil, err
	}

	// Get paginated results
	offset := (query.Page - 1) * query.PageSize
	if err := db.Order("date DESC").Offset(offset).Limit(query.PageSize).Find(&photos).Error; err != nil {
		return nil, err
	}

	// Calculate total pages
	totalPages := int(math.Ceil(float64(total) / float64(query.PageSize)))

	return &models.PhotoResponse{
		Photos: photos,
		Pagination: models.Pagination{
			Page:       query.Page,
			PageSize:   query.PageSize,
			Total:      total,
			TotalPages: totalPages,
		},
	}, nil
}

// GetFilterOptions returns available filter options
func (s *PhotoService) GetFilterOptions() (*models.FilterOptions, error) {
	var options models.FilterOptions

	// Get unique years
	var years []int
	if err := s.db.Model(&models.Photo{}).
		Select("DISTINCT EXTRACT(YEAR FROM date) as year").
		Order("year DESC").
		Pluck("year", &years).Error; err != nil {
		return nil, err
	}
	options.Years = years

	// Get unique locations
	var locations []string
	if err := s.db.Model(&models.Photo{}).
		Select("DISTINCT location").
		Where("location != ''").
		Order("location").
		Pluck("location", &locations).Error; err != nil {
		return nil, err
	}
	options.Locations = locations

	// Get unique tags
	var allTags []string
	var tagStrings []string
	if err := s.db.Model(&models.Photo{}).
		Select("tags").
		Where("tags != ''").
		Pluck("tags", &tagStrings).Error; err != nil {
		return nil, err
	}

	// Parse JSON arrays and collect unique tags
	tagSet := make(map[string]bool)
	for _, tagStr := range tagStrings {
		var tags []string
		if err := json.Unmarshal([]byte(tagStr), &tags); err == nil {
			for _, tag := range tags {
				tagSet[tag] = true
			}
		}
	}
	for tag := range tagSet {
		allTags = append(allTags, tag)
	}
	options.Tags = allTags

	return &options, nil
}

// ImportFromJSON imports photos from JSON data
func (s *PhotoService) ImportFromJSON(jsonData []byte) error {
	var data struct {
		Photos []struct {
			URL         string   `json:"url"`
			Thumbnail   string   `json:"thumbnail"`
			Title       string   `json:"title"`
			Description string   `json:"description"`
			Date        string   `json:"date"`
			Location    string   `json:"location"`
			City        string   `json:"city"`
			Country     string   `json:"country"`
			Tags        []string `json:"tags"`
			AspectRatio string   `json:"aspectRatio"`
		} `json:"photos"`
	}

	if err := json.Unmarshal(jsonData, &data); err != nil {
		return err
	}

	for _, p := range data.Photos {
		// Convert tags array to JSON string
		tagsJSON, _ := json.Marshal(p.Tags)

		// Parse date
		var date string
		if p.Date != "" {
			date = p.Date
		}

		photo := models.Photo{
			URL:         p.URL,
			Thumbnail:   p.Thumbnail,
			Title:       p.Title,
			Description: p.Description,
			Location:    p.Location,
			City:        p.City,
			Country:     p.Country,
			Tags:        string(tagsJSON),
			AspectRatio: p.AspectRatio,
		}

		// Parse date string
		if date != "" {
			// Try parsing common date formats
			formats := []string{"2006-01-02", "2006/01/02", "2006-01-02T15:04:05Z"}
			for _, format := range formats {
				if t, err := parseDate(date, format); err == nil {
					photo.Date = t
					break
				}
			}
		}

		// Check if photo with same URL already exists
		var existing models.Photo
		if err := s.db.Where("url = ?", p.URL).First(&existing).Error; err == nil {
			// Update existing
			photo.ID = existing.ID
			s.db.Save(&photo)
		} else {
			// Create new
			s.db.Create(&photo)
		}
	}

	return nil
}

// ParseTags parses comma-separated tags string into slice
func ParseTags(tagsStr string) []string {
	if tagsStr == "" {
		return nil
	}
	tags := strings.Split(tagsStr, ",")
	result := make([]string, 0, len(tags))
	for _, tag := range tags {
		tag = strings.TrimSpace(tag)
		if tag != "" {
			result = append(result, tag)
		}
	}
	return result
}

// CreatePhoto creates a new photo
func (s *PhotoService) CreatePhoto(photo *models.Photo) error {
	return s.db.Create(photo).Error
}

// UpdatePhoto updates an existing photo
func (s *PhotoService) UpdatePhoto(id uint, photo *models.Photo) error {
	photo.ID = id
	result := s.db.Model(&models.Photo{}).Where("id = ?", id).Updates(photo)
	if result.RowsAffected == 0 {
		return gorm.ErrRecordNotFound
	}
	return result.Error
}

// DeletePhoto deletes a photo by ID
func (s *PhotoService) DeletePhoto(id uint) error {
	result := s.db.Delete(&models.Photo{}, id)
	if result.RowsAffected == 0 {
		return gorm.ErrRecordNotFound
	}
	return result.Error
}

// GetPhotoByID returns a single photo by ID
func (s *PhotoService) GetPhotoByID(id uint) (*models.Photo, error) {
	var photo models.Photo
	err := s.db.First(&photo, id).Error
	if err != nil {
		return nil, err
	}
	return &photo, nil
}

func parseDate(dateStr, format string) (time.Time, error) {
	return time.Parse(format, dateStr)
}
