package models

import (
	"time"
)

// Photo represents a photo in the gallery
type Photo struct {
	ID          uint      `gorm:"primaryKey" json:"id"`
	URL         string    `gorm:"not null" json:"url"`
	Thumbnail   string    `json:"thumbnail"`
	Title       string    `gorm:"not null" json:"title"`
	Description string    `json:"description"`
	Date        time.Time `gorm:"index" json:"date"`
	Location    string    `gorm:"index" json:"location"`
	City        string    `json:"city"`
	Country     string    `json:"country"`
	Tags        string    `json:"tags"` // JSON array stored as string, e.g. ["nature","travel"]
	AspectRatio string    `json:"aspectRatio"`
	CreatedAt   time.Time `json:"createdAt"`
	UpdatedAt   time.Time `json:"updatedAt"`
}

// PhotoResponse is the response structure for photo list API
type PhotoResponse struct {
	Photos     []Photo    `json:"photos"`
	Pagination Pagination `json:"pagination"`
}

// Pagination holds pagination information
type Pagination struct {
	Page       int   `json:"page"`
	PageSize   int   `json:"pageSize"`
	Total      int64 `json:"total"`
	TotalPages int   `json:"totalPages"`
}

// FilterOptions holds available filter options
type FilterOptions struct {
	Years     []int    `json:"years"`
	Locations []string `json:"locations"`
	Tags      []string `json:"tags"`
}
