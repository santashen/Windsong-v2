package services

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/xml"
	"fmt"
	"net/url"
	"regexp"
	"sort"
	"strings"
	"time"
	"unicode/utf8"

	"github.com/yuin/goldmark"
	"github.com/yuin/goldmark/ast"
	"github.com/yuin/goldmark/extension"
	"github.com/yuin/goldmark/parser"
	"github.com/yuin/goldmark/text"
	"github.com/yuin/goldmark/util"
	"gorm.io/gorm"

	"windsong/models"
)

const rssExcerptLength = 240

var markdownSyntaxPattern = regexp.MustCompile("(?m)(?:^#{1,6}\\s+|^>\\s*|^[-*+]\\s+|^\\d+\\.\\s+|[*_~`]+|!\\[([^]]*)\\]\\([^)]+\\)|\\[([^]]+)\\]\\([^)]+\\))")

// RSSConfig contains public metadata used by the RSS feed.
type RSSConfig struct {
	SiteURL     string
	Title       string
	Description string
	Author      string
	MaxItems    int
}

// GeneratedFeed is the serialized feed and its HTTP cache metadata.
type GeneratedFeed struct {
	XML          []byte
	ETag         string
	LastModified time.Time
}

// RSSService generates an RSS 2.0 feed from published posts.
type RSSService struct {
	repository RSSPostRepository
	config     RSSConfig
}

type gormRSSPostRepository struct {
	db *gorm.DB
}

// NewRSSService creates an RSS service. A repository can be injected for tests.
func NewRSSService(db *gorm.DB, config RSSConfig, repositories ...RSSPostRepository) *RSSService {
	var repository RSSPostRepository = &gormRSSPostRepository{db: db}
	if len(repositories) > 0 && repositories[0] != nil {
		repository = repositories[0]
	}

	if config.MaxItems < 1 || config.MaxItems > 100 {
		config.MaxItems = 20
	}
	config.SiteURL = strings.TrimRight(config.SiteURL, "/")

	return &RSSService{repository: repository, config: config}
}

func (r *gormRSSPostRepository) ListPublishedPosts(limit int) ([]models.Post, error) {
	var posts []models.Post
	err := r.db.
		Where("is_published = ?", true).
		Order("date DESC").
		Limit(limit).
		Find(&posts).Error
	return posts, err
}

// Generate builds the current RSS document and deterministic cache metadata.
func (s *RSSService) Generate() (*GeneratedFeed, error) {
	posts, err := s.repository.ListPublishedPosts(s.config.MaxItems)
	if err != nil {
		return nil, fmt.Errorf("query published posts: %w", err)
	}

	items := make([]rssItem, 0, len(posts))
	var lastModified time.Time
	for _, post := range posts {
		if !post.IsPublished {
			continue
		}
		postURL := s.config.SiteURL + "/posts/" + url.PathEscape(post.Slug)
		html, renderErr := renderRSSMarkdown(post.Content, postURL)
		if renderErr != nil {
			return nil, fmt.Errorf("render post %q: %w", post.Slug, renderErr)
		}

		modified := post.UpdatedAt
		if modified.IsZero() {
			modified = post.Date
		}
		if modified.After(lastModified) {
			lastModified = modified
		}

		categories := append([]string(nil), post.Tags...)
		sort.Strings(categories)
		items = append(items, rssItem{
			Title:       post.Title,
			Link:        postURL,
			GUID:        rssGUID{IsPermaLink: true, Value: postURL},
			PubDate:     formatRSSDate(post.Date),
			Categories:  categories,
			Description: markdownExcerpt(post.Content, rssExcerptLength),
			Content:     html,
			Author:      s.config.Author,
		})
	}

	document := rssDocument{
		Version:   "2.0",
		ContentNS: "http://purl.org/rss/1.0/modules/content/",
		Channel: rssChannel{
			Title:         s.config.Title,
			Link:          s.config.SiteURL,
			Description:   s.config.Description,
			Language:      "zh-CN",
			LastBuildDate: formatRSSDate(lastModified),
			Items:         items,
		},
	}

	data, err := xml.MarshalIndent(document, "", "  ")
	if err != nil {
		return nil, fmt.Errorf("marshal RSS document: %w", err)
	}
	data = append([]byte(xml.Header), data...)
	data = append(data, '\n')

	hash := sha256.Sum256(data)
	return &GeneratedFeed{
		XML:          data,
		ETag:         `"` + hex.EncodeToString(hash[:]) + `"`,
		LastModified: lastModified.UTC().Truncate(time.Second),
	}, nil
}

func renderRSSMarkdown(source, postURL string) (string, error) {
	markdown := goldmark.New(
		goldmark.WithExtensions(extension.GFM),
		goldmark.WithParserOptions(parser.WithASTTransformers(
			util.Prioritized(&rssURLTransformer{baseURL: postURL}, 100),
		)),
	)
	var output bytes.Buffer
	if err := markdown.Convert([]byte(source), &output); err != nil {
		return "", err
	}
	return output.String(), nil
}

type rssURLTransformer struct {
	baseURL string
}

func (t *rssURLTransformer) Transform(node *ast.Document, _ text.Reader, _ parser.Context) {
	base, err := url.Parse(t.baseURL)
	if err != nil {
		return
	}
	_ = ast.Walk(node, func(n ast.Node, entering bool) (ast.WalkStatus, error) {
		if !entering {
			return ast.WalkContinue, nil
		}
		switch value := n.(type) {
		case *ast.Link:
			value.Destination = resolveRSSURL(base, value.Destination)
		case *ast.Image:
			value.Destination = resolveRSSURL(base, value.Destination)
		}
		return ast.WalkContinue, nil
	})
}

func resolveRSSURL(base *url.URL, destination []byte) []byte {
	reference, err := url.Parse(string(destination))
	if err != nil || reference.IsAbs() || strings.HasPrefix(reference.String(), "#") {
		return destination
	}
	return []byte(base.ResolveReference(reference).String())
}

func markdownExcerpt(source string, maxLength int) string {
	value := markdownSyntaxPattern.ReplaceAllString(source, "$1$2")
	value = strings.Join(strings.Fields(value), " ")
	if utf8.RuneCountInString(value) <= maxLength {
		return value
	}
	runes := []rune(value)
	return strings.TrimSpace(string(runes[:maxLength])) + "…"
}

func formatRSSDate(value time.Time) string {
	if value.IsZero() {
		return ""
	}
	return value.UTC().Format(time.RFC1123Z)
}

type rssDocument struct {
	XMLName   xml.Name   `xml:"rss"`
	Version   string     `xml:"version,attr"`
	ContentNS string     `xml:"xmlns:content,attr"`
	Channel   rssChannel `xml:"channel"`
}

type rssChannel struct {
	Title         string    `xml:"title"`
	Link          string    `xml:"link"`
	Description   string    `xml:"description"`
	Language      string    `xml:"language,omitempty"`
	LastBuildDate string    `xml:"lastBuildDate,omitempty"`
	Items         []rssItem `xml:"item"`
}

type rssItem struct {
	Title       string   `xml:"title"`
	Link        string   `xml:"link"`
	GUID        rssGUID  `xml:"guid"`
	PubDate     string   `xml:"pubDate,omitempty"`
	Categories  []string `xml:"category,omitempty"`
	Description string   `xml:"description"`
	Content     string   `xml:"content:encoded"`
	Author      string   `xml:"author,omitempty"`
}

type rssGUID struct {
	IsPermaLink bool   `xml:"isPermaLink,attr"`
	Value       string `xml:",chardata"`
}
