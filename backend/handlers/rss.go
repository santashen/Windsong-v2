package handlers

import (
	"bytes"
	"net/http"

	"github.com/gin-gonic/gin"

	"windsong/middleware"
)

// RSSHandler handles the public RSS document.
type RSSHandler struct {
	rssService RSSServiceInterface
}

// NewRSSHandler creates an RSS handler.
func NewRSSHandler(rssService RSSServiceInterface) *RSSHandler {
	return &RSSHandler{rssService: rssService}
}

// GetFeed godoc
// @Summary      Get the blog RSS feed
// @Description  Returns the latest published posts as an RSS 2.0 document
// @Tags         rss
// @Produce      application/rss+xml
// @Success      200  {string}  string  "RSS 2.0 XML"
// @Failure      500  {object}  Response
// @Router       /rss.xml [get]
func (h *RSSHandler) GetFeed(c *gin.Context) {
	feed, err := h.rssService.Generate()
	if err != nil {
		middleware.GetLogger(c).Error().Err(err).Msg("failed to generate RSS feed")
		Error(c, http.StatusInternalServerError, CodeInternalError, "Failed to generate RSS feed")
		return
	}

	c.Header("Cache-Control", "public, max-age=300")
	c.Header("Content-Type", "application/rss+xml; charset=utf-8")
	c.Header("ETag", feed.ETag)
	http.ServeContent(c.Writer, c.Request, "rss.xml", feed.LastModified, bytes.NewReader(feed.XML))
}
