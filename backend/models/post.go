package models

import (
	"time"

	"github.com/lib/pq"
)

// Post represents a blog post
type Post struct {
	ID          uint           `gorm:"primaryKey" json:"id"`
	Slug        string         `gorm:"uniqueIndex;not null" json:"slug"`
	Title       string         `gorm:"not null" json:"title"`
	Date        time.Time      `gorm:"index" json:"date"`
	Tags        pq.StringArray `gorm:"type:text[]" json:"tags" swaggertype:"array,string"`
	Content     string         `gorm:"type:text" json:"content"`
	ContentHash string         `gorm:"size:64" json:"-"`
	IsPublished bool           `gorm:"default:true;index" json:"isPublished"`
	CreatedAt   time.Time      `json:"createdAt"`
	UpdatedAt   time.Time      `json:"updatedAt"`
}

// PostListItem is a summary for list responses (excludes content)
type PostListItem struct {
	ID          uint           `json:"id"`
	Slug        string         `json:"slug"`
	Title       string         `json:"title"`
	Date        time.Time      `json:"date"`
	Tags        pq.StringArray `json:"tags" swaggertype:"array,string"`
	IsPublished bool           `json:"isPublished"`
	CreatedAt   time.Time      `json:"createdAt"`
	UpdatedAt   time.Time      `json:"updatedAt"`
}

// PostListResponse is the response structure for post list API
type PostListResponse struct {
	Posts      []PostListItem `json:"posts"`
	Pagination Pagination     `json:"pagination"`
}
