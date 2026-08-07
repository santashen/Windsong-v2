package services

import (
	"encoding/xml"
	"errors"
	"strings"
	"testing"
	"time"

	"github.com/lib/pq"

	"windsong/models"
)

type fakeRSSPostRepository struct {
	posts []models.Post
	err   error
	limit int
}

func (r *fakeRSSPostRepository) ListPublishedPosts(limit int) ([]models.Post, error) {
	r.limit = limit
	return r.posts, r.err
}

func TestRSSServiceGenerate(t *testing.T) {
	date := time.Date(2026, time.August, 7, 8, 30, 0, 0, time.FixedZone("CST", 8*60*60))
	updated := date.Add(2 * time.Hour)
	repository := &fakeRSSPostRepository{posts: []models.Post{
		{
			Slug:        "hello-world",
			Title:       "Hello & RSS",
			Date:        date,
			UpdatedAt:   updated,
			Tags:        pq.StringArray{"Vue", "Go"},
			Content:     "# Welcome\n\nRead the [guide](/guide).\n\n![cover](images/cover.png)",
			IsPublished: true,
		},
		{
			Slug:        "draft",
			Title:       "Draft",
			Date:        date.Add(time.Hour),
			Content:     "must not appear",
			IsPublished: false,
		},
	}}
	service := NewRSSService(nil, RSSConfig{
		SiteURL:     "https://v2.windsong.top/",
		Title:       "Windsong Blog",
		Description: "A personal blog",
		Author:      "author@example.com",
		MaxItems:    10,
	}, repository)

	feed, err := service.Generate()
	if err != nil {
		t.Fatalf("Generate() error = %v", err)
	}
	if repository.limit != 10 {
		t.Fatalf("repository limit = %d, want 10", repository.limit)
	}
	if feed.LastModified != updated.UTC() {
		t.Fatalf("LastModified = %v, want %v", feed.LastModified, updated.UTC())
	}
	if feed.ETag == "" {
		t.Fatal("ETag is empty")
	}

	contents := string(feed.XML)
	checks := []string{
		`<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">`,
		`<title>Hello &amp; RSS</title>`,
		`<link>https://v2.windsong.top/posts/hello-world</link>`,
		`<guid isPermaLink="true">https://v2.windsong.top/posts/hello-world</guid>`,
		`<category>Go</category>`,
		`<category>Vue</category>`,
		`href=&#34;https://v2.windsong.top/guide&#34;`,
		`src=&#34;https://v2.windsong.top/posts/images/cover.png&#34;`,
		`<author>author@example.com</author>`,
	}
	for _, check := range checks {
		if !strings.Contains(contents, check) {
			t.Errorf("feed does not contain %q\n%s", check, contents)
		}
	}
	if strings.Contains(contents, "Draft") || strings.Contains(contents, "must not appear") {
		t.Errorf("feed contains an unpublished post:\n%s", contents)
	}

	decoder := xml.NewDecoder(strings.NewReader(contents))
	for {
		if _, decodeErr := decoder.Token(); decodeErr != nil {
			if decodeErr.Error() == "EOF" {
				break
			}
			t.Fatalf("generated feed is not valid XML: %v", decodeErr)
		}
	}

	second, err := service.Generate()
	if err != nil {
		t.Fatalf("second Generate() error = %v", err)
	}
	if second.ETag != feed.ETag {
		t.Errorf("ETag is not deterministic: %q != %q", second.ETag, feed.ETag)
	}
}

func TestRSSServiceGenerateRepositoryError(t *testing.T) {
	repository := &fakeRSSPostRepository{err: errors.New("database unavailable")}
	service := NewRSSService(nil, RSSConfig{SiteURL: "https://example.com", MaxItems: 20}, repository)

	_, err := service.Generate()
	if err == nil || !strings.Contains(err.Error(), "query published posts") {
		t.Fatalf("Generate() error = %v, want wrapped repository error", err)
	}
}

func TestRSSServiceUsesDefaultItemLimit(t *testing.T) {
	repository := &fakeRSSPostRepository{}
	service := NewRSSService(nil, RSSConfig{SiteURL: "https://example.com", MaxItems: 200}, repository)

	if _, err := service.Generate(); err != nil {
		t.Fatalf("Generate() error = %v", err)
	}
	if repository.limit != 20 {
		t.Fatalf("repository limit = %d, want default 20", repository.limit)
	}
}
