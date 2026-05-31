package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"

	"windsong/middleware"
	"windsong/services"
)

// PostHandler handles post-related HTTP requests
type PostHandler struct {
	postService PostServiceInterface
}

// NewPostHandler creates a new PostHandler
func NewPostHandler(postService PostServiceInterface) *PostHandler {
	return &PostHandler{postService: postService}
}

// SyncPosts godoc
// @Summary      Sync posts from git repository
// @Description  Triggers a sync of blog posts from the configured git repository
// @Tags         webhooks
// @Produce      json
// @Security     ApiKeyAuth
// @Success      200  {object}  Response{data=services.SyncResult}
// @Failure      500  {object}  Response
// @Router       /webhooks/sync [post]
func (h *PostHandler) SyncPosts(c *gin.Context) {
	result, err := h.postService.SyncPosts()
	if err != nil {
		middleware.GetLogger(c).Error().Err(err).Msg("post sync failed")
		Error(c, http.StatusInternalServerError, CodeInternalError, "Sync failed: "+err.Error())
		return
	}

	Success(c, result)
}

// PostListQuery is the query parameter structure for listing posts
type PostListQuery struct {
	Page     int    `form:"page" binding:"omitempty,min=1"`
	PageSize int    `form:"pageSize" binding:"omitempty,min=1,max=100"`
	Tag      string `form:"tag" binding:"omitempty,max=50"`
}

// GetPosts godoc
// @Summary      List blog posts
// @Description  Returns paginated blog posts with optional tag filter
// @Tags         posts
// @Produce      json
// @Param        page      query  int     false  "Page number"     default(1)
// @Param        pageSize  query  int     false  "Items per page"  default(20)
// @Param        tag       query  string  false  "Filter by tag"
// @Success      200  {object}  Response{data=models.PostListResponse}
// @Failure      400  {object}  Response
// @Failure      500  {object}  Response
// @Router       /posts [get]
func (h *PostHandler) GetPosts(c *gin.Context) {
	var query PostListQuery
	if err := c.ShouldBindQuery(&query); err != nil {
		ValidationError(c, err)
		return
	}

	// Apply defaults
	if query.Page == 0 {
		query.Page = 1
	}
	if query.PageSize == 0 {
		query.PageSize = 20
	}

	// Build service query
	serviceQuery := services.PostQuery{
		Page:     query.Page,
		PageSize: query.PageSize,
		Tag:      query.Tag,
	}

	// Get posts
	response, err := h.postService.GetPosts(serviceQuery)
	if err != nil {
		middleware.GetLogger(c).Error().Err(err).Msg("failed to fetch posts")
		Error(c, http.StatusInternalServerError, CodeInternalError, "Failed to fetch posts")
		return
	}

	Success(c, response)
}

// GetTags godoc
// @Summary      List blog post tags
// @Description  Returns all unique tags from published blog posts
// @Tags         posts
// @Produce      json
// @Success      200  {object}  Response{data=[]string}
// @Failure      500  {object}  Response
// @Router       /posts/tags [get]
func (h *PostHandler) GetTags(c *gin.Context) {
	tags, err := h.postService.GetAllTags()
	if err != nil {
		middleware.GetLogger(c).Error().Err(err).Msg("failed to fetch post tags")
		Error(c, http.StatusInternalServerError, CodeInternalError, "Failed to fetch post tags")
		return
	}

	Success(c, tags)
}

// GetPost godoc
// @Summary      Get a blog post
// @Description  Returns a single blog post by its slug
// @Tags         posts
// @Produce      json
// @Param        slug  path  string  true  "Post slug"
// @Success      200   {object}  Response{data=models.Post}
// @Failure      400   {object}  Response
// @Failure      404   {object}  Response
// @Router       /posts/{slug} [get]
func (h *PostHandler) GetPost(c *gin.Context) {
	slug := c.Param("slug")
	if slug == "" {
		Error(c, http.StatusBadRequest, CodeBadRequest, "Slug is required")
		return
	}

	post, err := h.postService.GetPostBySlug(slug)
	if err != nil {
		middleware.GetLogger(c).Warn().Err(err).Str("slug", slug).Msg("post not found")
		Error(c, http.StatusNotFound, CodeNotFound, "Post not found")
		return
	}

	Success(c, post)
}
