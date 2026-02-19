package services

import "net/http"

// HTTPClient abstracts HTTP calls for testing
type HTTPClient interface {
	Do(req *http.Request) (*http.Response, error)
}

// GitSyncer abstracts git operations for testing
type GitSyncer interface {
	Sync(repoURL, postsDir string) error
}
