package handlers

import (
	"windsong/models"
	"windsong/services"
)

// PostServiceInterface defines the contract handlers need from PostService
type PostServiceInterface interface {
	SyncPosts() (*services.SyncResult, error)
	GetPosts(query services.PostQuery) (*models.PostListResponse, error)
	GetAllTags() ([]string, error)
	GetPostBySlug(slug string) (*models.Post, error)
}

// PhotoServiceInterface defines the contract handlers need from PhotoService
type PhotoServiceInterface interface {
	GetPhotos(query services.PhotoQuery) (*models.PhotoResponse, error)
	GetFilterOptions() (*models.FilterOptions, error)
	GetPhotoByID(id uint) (*models.Photo, error)
	CreatePhoto(photo *models.Photo) error
	UpdatePhoto(id uint, photo *models.Photo) error
	DeletePhoto(id uint) error
}
