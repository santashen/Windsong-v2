package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"

	"windsong/middleware"
	"windsong/services"
)

// PostHandler handles post-related HTTP requests
type PostHandler struct {
	postService *services.PostService
}

// NewPostHandler creates a new PostHandler
func NewPostHandler(postService *services.PostService) *PostHandler {
	return &PostHandler{postService: postService}
}

// SyncPosts handles POST /api/webhooks/sync
func (h *PostHandler) SyncPosts(c *gin.Context) {
	result, err := h.postService.SyncPosts()
	if err != nil {
		middleware.GetLogger(c).Error().Err(err).Msg("post sync failed")
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Sync failed",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, result)
}

// GetPosts handles GET /api/posts
func (h *PostHandler) GetPosts(c *gin.Context) {
	// Parse query parameters
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("pageSize", "20"))
	tag := c.Query("tag")

	// Build query
	query := services.PostQuery{
		Page:     page,
		PageSize: pageSize,
		Tag:      tag,
	}

	// Get posts
	response, err := h.postService.GetPosts(query)
	if err != nil {
		middleware.GetLogger(c).Error().Err(err).Msg("failed to fetch posts")
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to fetch posts",
		})
		return
	}

	c.JSON(http.StatusOK, response)
}

// GetPost handles GET /api/posts/:slug
func (h *PostHandler) GetPost(c *gin.Context) {
	slug := c.Param("slug")
	if slug == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Slug is required"})
		return
	}

	post, err := h.postService.GetPostBySlug(slug)
	if err != nil {
		middleware.GetLogger(c).Warn().Err(err).Str("slug", slug).Msg("post not found")
		c.JSON(http.StatusNotFound, gin.H{"error": "Post not found"})
		return
	}

	c.JSON(http.StatusOK, post)
}
