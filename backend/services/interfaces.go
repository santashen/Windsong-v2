package services

import (
	"net/http"

	"windsong/models"
)

// HTTPClient abstracts HTTP calls for testing
type HTTPClient interface {
	Do(req *http.Request) (*http.Response, error)
}

// GitSyncer abstracts git operations for testing
type GitSyncer interface {
	Sync(repoURL, postsDir string) error
}

// RSSPostRepository abstracts the post query used to build the RSS feed.
type RSSPostRepository interface {
	ListPublishedPosts(limit int) ([]models.Post, error)
}
