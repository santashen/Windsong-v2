package handlers

import (
	"errors"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/gin-gonic/gin"

	"windsong/services"
)

type fakeRSSService struct {
	feed *services.GeneratedFeed
	err  error
}

func (s *fakeRSSService) Generate() (*services.GeneratedFeed, error) {
	return s.feed, s.err
}

func TestRSSHandlerGetFeed(t *testing.T) {
	gin.SetMode(gin.TestMode)
	modified := time.Date(2026, time.August, 7, 1, 2, 3, 0, time.UTC)
	service := &fakeRSSService{feed: &services.GeneratedFeed{
		XML:          []byte("<?xml version=\"1.0\"?><rss version=\"2.0\"></rss>"),
		ETag:         `"feed-hash"`,
		LastModified: modified,
	}}
	router := gin.New()
	router.GET("/rss.xml", NewRSSHandler(service).GetFeed)

	request := httptest.NewRequest(http.MethodGet, "/rss.xml", nil)
	response := httptest.NewRecorder()
	router.ServeHTTP(response, request)

	if response.Code != http.StatusOK {
		t.Fatalf("status = %d, want 200", response.Code)
	}
	if got := response.Header().Get("Content-Type"); got != "application/rss+xml; charset=utf-8" {
		t.Errorf("Content-Type = %q", got)
	}
	if got := response.Header().Get("Cache-Control"); got != "public, max-age=300" {
		t.Errorf("Cache-Control = %q", got)
	}
	if got := response.Header().Get("ETag"); got != `"feed-hash"` {
		t.Errorf("ETag = %q", got)
	}
	if !strings.Contains(response.Body.String(), "<rss") {
		t.Errorf("body = %q", response.Body.String())
	}

	cachedRequest := httptest.NewRequest(http.MethodGet, "/rss.xml", nil)
	cachedRequest.Header.Set("If-None-Match", `"feed-hash"`)
	cachedResponse := httptest.NewRecorder()
	router.ServeHTTP(cachedResponse, cachedRequest)
	if cachedResponse.Code != http.StatusNotModified {
		t.Fatalf("cached status = %d, want 304", cachedResponse.Code)
	}
	if cachedResponse.Body.Len() != 0 {
		t.Errorf("cached response body = %q, want empty", cachedResponse.Body.String())
	}
}

func TestRSSHandlerGetFeedError(t *testing.T) {
	gin.SetMode(gin.TestMode)
	service := &fakeRSSService{err: errors.New("generation failed")}
	router := gin.New()
	router.GET("/rss.xml", NewRSSHandler(service).GetFeed)

	request := httptest.NewRequest(http.MethodGet, "/rss.xml", nil)
	response := httptest.NewRecorder()
	router.ServeHTTP(response, request)

	if response.Code != http.StatusInternalServerError {
		t.Fatalf("status = %d, want 500", response.Code)
	}
	if !strings.Contains(response.Body.String(), "Failed to generate RSS feed") {
		t.Errorf("body = %q", response.Body.String())
	}
}
