package handlers

import (
	"context"
	"windsong/models"
	"windsong/services"
)

// PhotoMetadataServiceInterface defines the photo metadata capability used by handlers.
type PhotoMetadataServiceInterface interface {
	ParsePhotoMetadata(ctx context.Context, request services.PhotoMetadataImportRequest) (*services.PhotoMetadataImportResponse, error)
}

// PostServiceInterface defines the contract handlers need from PostService
type PostServiceInterface interface {
	SyncPosts() (*services.SyncResult, error)
	GetPosts(query services.PostQuery) (*models.PostListResponse, error)
	GetAllTags() ([]string, error)
	GetPostBySlug(slug string) (*models.Post, error)
}

// RSSServiceInterface defines the contract handlers need from RSSService.
type RSSServiceInterface interface {
	Generate() (*services.GeneratedFeed, error)
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
