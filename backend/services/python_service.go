package services

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net"
	"net/http"
	"strings"
	"time"
)

var ErrPythonServiceTimeout = errors.New("Python service request timed out")

// PhotoMetadataImportRequest is the raw text submitted by the administrator.
type PhotoMetadataImportRequest struct {
	Content string `json:"content" binding:"required,max=30000"`
}

// PhotoMetadataImportItem is one parsed photo draft returned by the Python service.
type PhotoMetadataImportItem struct {
	Index            int      `json:"index"`
	Status           string   `json:"status"`
	URL              string   `json:"url"`
	Thumbnail        string   `json:"thumbnail"`
	Title            string   `json:"title"`
	Description      string   `json:"description"`
	Date             string   `json:"date"`
	Location         string   `json:"location"`
	City             string   `json:"city"`
	Country          string   `json:"country"`
	Tags             []string `json:"tags"`
	AspectRatio      string   `json:"aspectRatio"`
	Warnings         []string `json:"warnings"`
	MissingFields    []string `json:"missingFields"`
	Existing         bool     `json:"existing"`
	DuplicateInBatch bool     `json:"duplicateInBatch"`
}

// PhotoMetadataImportResponse is the stable contract exposed by the Go API.
type PhotoMetadataImportResponse struct {
	Items []PhotoMetadataImportItem `json:"items"`
}

// PythonServiceClient calls the internal Python service.
type PythonServiceClient struct {
	baseURL string
	client  *http.Client
}

func NewPythonServiceClient(baseURL string, timeoutSeconds int) *PythonServiceClient {
	if timeoutSeconds < 1 {
		timeoutSeconds = 120
	}
	return &PythonServiceClient{
		baseURL: strings.TrimRight(baseURL, "/"),
		client:  &http.Client{Timeout: time.Duration(timeoutSeconds) * time.Second},
	}
}

func (c *PythonServiceClient) ParsePhotoMetadata(ctx context.Context, request PhotoMetadataImportRequest) (*PhotoMetadataImportResponse, error) {
	body, err := json.Marshal(request)
	if err != nil {
		return nil, fmt.Errorf("marshal AI request: %w", err)
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, c.baseURL+"/api/photo-metadata/parse", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create AI request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.client.Do(req)
	if err != nil {
		var networkError net.Error
		if errors.Is(err, context.DeadlineExceeded) || (errors.As(err, &networkError) && networkError.Timeout()) {
			return nil, fmt.Errorf("%w: %v", ErrPythonServiceTimeout, err)
		}
		return nil, fmt.Errorf("call Python service: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		body, _ := io.ReadAll(io.LimitReader(resp.Body, 2048))
		if resp.StatusCode == http.StatusGatewayTimeout {
			return nil, fmt.Errorf("%w: %s", ErrPythonServiceTimeout, strings.TrimSpace(string(body)))
		}
		return nil, fmt.Errorf("Python service returned status %d: %s", resp.StatusCode, strings.TrimSpace(string(body)))
	}

	var result PhotoMetadataImportResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode Python service response: %w", err)
	}
	return &result, nil
}
