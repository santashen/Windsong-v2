package services

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io/fs"
	"log"
	"math"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/adrg/frontmatter"
	"github.com/lib/pq"
	"gorm.io/gorm"

	"windsong/models"
)

// PostService handles post business logic
type PostService struct {
	db        *gorm.DB
	repoURL   string
	postsDir  string
	gitSyncer GitSyncer
	syncMutex sync.Mutex
}

// NewPostService creates a new PostService
func NewPostService(db *gorm.DB, repoURL, postsDir string, gitSyncer ...GitSyncer) *PostService {
	var syncer GitSyncer
	if len(gitSyncer) > 0 && gitSyncer[0] != nil {
		syncer = gitSyncer[0]
	} else {
		syncer = &defaultGitSyncer{}
	}
	return &PostService{
		db:        db,
		repoURL:   repoURL,
		postsDir:  postsDir,
		gitSyncer: syncer,
	}
}

// defaultGitSyncer implements GitSyncer using os/exec git commands
type defaultGitSyncer struct{}

func (g *defaultGitSyncer) Sync(repoURL, postsDir string) error {
	if repoURL == "" {
		return fmt.Errorf("POSTS_REPO_URL not configured")
	}

	if _, err := os.Stat(postsDir); os.IsNotExist(err) {
		log.Printf("Cloning posts repository to %s", postsDir)
		cmd := exec.Command("git", "clone", "--depth", "1", repoURL, postsDir)
		output, err := cmd.CombinedOutput()
		if err != nil {
			return fmt.Errorf("git clone failed: %s - %v", string(output), err)
		}
		log.Println("Repository cloned successfully")
	} else {
		log.Printf("Pulling latest changes in %s", postsDir)
		cmd := exec.Command("git", "-C", postsDir, "pull", "--ff-only")
		output, err := cmd.CombinedOutput()
		if err != nil {
			return fmt.Errorf("git pull failed: %s - %v", string(output), err)
		}
		log.Println("Repository updated successfully")
	}

	return nil
}

// PostQuery holds query parameters for post list
type PostQuery struct {
	Page     int
	PageSize int
	Tag      string
}

// SyncResult holds the result of a sync operation
type SyncResult struct {
	Created int      `json:"created"`
	Updated int      `json:"updated"`
	Deleted int      `json:"deleted"`
	Skipped int      `json:"skipped"`
	Errors  []string `json:"errors,omitempty"`
}

// PostFrontMatter represents the YAML front matter in markdown files
type PostFrontMatter struct {
	Title     string   `yaml:"title"`
	Slug      string   `yaml:"slug"`
	Date      string   `yaml:"date"`
	Tags      []string `yaml:"tags"`
	Published *bool    `yaml:"published"`
}

// parsedPost holds parsed post data
type parsedPost struct {
	FrontMatter PostFrontMatter
	Content     string
	Hash        string
}

// SyncPosts synchronizes posts from git repository to database
func (s *PostService) SyncPosts() (*SyncResult, error) {
	s.syncMutex.Lock()
	defer s.syncMutex.Unlock()

	result := &SyncResult{}

	// Step 1: Git sync (clone or pull)
	if err := s.gitSyncer.Sync(s.repoURL, s.postsDir); err != nil {
		return nil, fmt.Errorf("git sync failed: %w", err)
	}

	// Step 2: Walk and process all markdown files
	seenSlugs := make(map[string]bool)

	err := filepath.WalkDir(s.postsDir, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}

		// Skip directories and non-markdown files
		if d.IsDir() || !strings.HasSuffix(strings.ToLower(d.Name()), ".md") {
			return nil
		}

		// Parse the markdown file
		parsed, parseErr := s.parseMarkdownFile(path)
		if parseErr != nil {
			result.Errors = append(result.Errors, fmt.Sprintf("%s: %v", path, parseErr))
			return nil // Continue processing other files
		}

		// Derive slug from filename if not specified
		slug := parsed.FrontMatter.Slug
		if slug == "" {
			slug = strings.TrimSuffix(d.Name(), filepath.Ext(d.Name()))
		}
		seenSlugs[slug] = true

		// Determine published status (default true)
		isPublished := true
		if parsed.FrontMatter.Published != nil {
			isPublished = *parsed.FrontMatter.Published
		}

		// Parse date
		var postDate time.Time
		if parsed.FrontMatter.Date != "" {
			formats := []string{"2006-01-02", "2006-01-02T15:04:05Z", "2006-01-02 15:04:05"}
			for _, format := range formats {
				if t, err := time.Parse(format, parsed.FrontMatter.Date); err == nil {
					postDate = t
					break
				}
			}
		}

		// Check if post exists in database
		var existing models.Post
		err = s.db.Where("slug = ?", slug).First(&existing).Error

		if err == gorm.ErrRecordNotFound {
			// Create new post
			post := models.Post{
				Slug:        slug,
				Title:       parsed.FrontMatter.Title,
				Date:        postDate,
				Tags:        pq.StringArray(parsed.FrontMatter.Tags),
				Content:     parsed.Content,
				ContentHash: parsed.Hash,
				IsPublished: isPublished,
			}
			if createErr := s.db.Create(&post).Error; createErr != nil {
				result.Errors = append(result.Errors, fmt.Sprintf("create %s: %v", slug, createErr))
			} else {
				result.Created++
			}
		} else if err == nil {
			// Post exists, check if content changed
			if existing.ContentHash != parsed.Hash {
				// Update post
				existing.Title = parsed.FrontMatter.Title
				existing.Date = postDate
				existing.Tags = pq.StringArray(parsed.FrontMatter.Tags)
				existing.Content = parsed.Content
				existing.ContentHash = parsed.Hash
				existing.IsPublished = isPublished

				if saveErr := s.db.Save(&existing).Error; saveErr != nil {
					result.Errors = append(result.Errors, fmt.Sprintf("update %s: %v", slug, saveErr))
				} else {
					result.Updated++
				}
			} else {
				result.Skipped++
			}
		} else {
			result.Errors = append(result.Errors, fmt.Sprintf("query %s: %v", slug, err))
		}

		return nil
	})

	if err != nil {
		return nil, fmt.Errorf("walk directory failed: %w", err)
	}

	// Step 3: Delete posts that no longer exist in the repository
	var allPosts []models.Post
	if err := s.db.Select("id", "slug").Find(&allPosts).Error; err != nil {
		return nil, fmt.Errorf("query all posts failed: %w", err)
	}

	for _, post := range allPosts {
		if !seenSlugs[post.Slug] {
			if err := s.db.Delete(&post).Error; err != nil {
				result.Errors = append(result.Errors, fmt.Sprintf("delete %s: %v", post.Slug, err))
			} else {
				result.Deleted++
			}
		}
	}

	return result, nil
}

// parseMarkdownFile parses a markdown file and extracts front matter and content
func (s *PostService) parseMarkdownFile(path string) (*parsedPost, error) {
	// Read file content
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read file failed: %w", err)
	}

	// Calculate hash of entire file
	hash := sha256.Sum256(data)
	hashStr := hex.EncodeToString(hash[:])

	// Parse front matter
	var fm PostFrontMatter
	content, err := frontmatter.Parse(strings.NewReader(string(data)), &fm)
	if err != nil {
		return nil, fmt.Errorf("parse front matter failed: %w", err)
	}

	return &parsedPost{
		FrontMatter: fm,
		Content:     string(content),
		Hash:        hashStr,
	}, nil
}

// GetPosts returns paginated posts (without content)
func (s *PostService) GetPosts(query PostQuery) (*models.PostListResponse, error) {
	// Set defaults
	if query.Page < 1 {
		query.Page = 1
	}
	if query.PageSize < 1 || query.PageSize > 100 {
		query.PageSize = 20
	}

	var posts []models.Post
	var total int64

	// Build query - only published posts
	db := s.db.Model(&models.Post{}).Where("is_published = ?", true)

	// Apply tag filter
	if query.Tag != "" {
		db = db.Where("? = ANY(tags)", query.Tag)
	}

	// Get total count
	if err := db.Count(&total).Error; err != nil {
		return nil, err
	}

	// Get paginated results (select only list fields, exclude content)
	offset := (query.Page - 1) * query.PageSize
	if err := db.Select("id", "slug", "title", "date", "tags", "is_published", "created_at", "updated_at").
		Order("date DESC").
		Offset(offset).
		Limit(query.PageSize).
		Find(&posts).Error; err != nil {
		return nil, err
	}

	// Convert to PostListItem
	items := make([]models.PostListItem, len(posts))
	for i, p := range posts {
		items[i] = models.PostListItem{
			ID:          p.ID,
			Slug:        p.Slug,
			Title:       p.Title,
			Date:        p.Date,
			Tags:        p.Tags,
			IsPublished: p.IsPublished,
			CreatedAt:   p.CreatedAt,
			UpdatedAt:   p.UpdatedAt,
		}
	}

	// Calculate total pages
	totalPages := int(math.Ceil(float64(total) / float64(query.PageSize)))

	return &models.PostListResponse{
		Posts: items,
		Pagination: models.Pagination{
			Page:       query.Page,
			PageSize:   query.PageSize,
			Total:      total,
			TotalPages: totalPages,
		},
	}, nil
}

// GetPostBySlug returns a single post by slug
func (s *PostService) GetPostBySlug(slug string) (*models.Post, error) {
	var post models.Post
	err := s.db.Where("slug = ? AND is_published = ?", slug, true).First(&post).Error
	if err != nil {
		return nil, err
	}
	return &post, nil
}
