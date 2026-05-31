import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { postsApi } from '@/api'

export const useBlogStore = defineStore('blog', () => {
  // State
  const posts = ref([])
  const currentPost = ref(null)
  const selectedTag = ref(null)
  const allTags = ref([])
  const pagination = ref({
    page: 1,
    pageSize: 12,
    total: 0,
    totalPages: 0
  })
  const isLoading = ref(false)
  const isLoadingTags = ref(false)
  const isLoadingPost = ref(false)
  const error = ref(null)

  // Getters
  const hasActiveFilter = computed(() => selectedTag.value !== null)

  // Actions
  async function fetchPosts() {
    isLoading.value = true
    error.value = null

    try {
      const params = {
        page: pagination.value.page,
        pageSize: pagination.value.pageSize
      }

      if (selectedTag.value) {
        params.tag = selectedTag.value
      }

      const response = await postsApi.getPosts(params)
      posts.value = response.data.posts || []
      pagination.value = response.data.pagination || pagination.value
    } catch (err) {
      error.value = 'Failed to fetch posts'
      console.error('Error fetching posts:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchTags() {
    isLoadingTags.value = true

    try {
      const response = await postsApi.getTags()
      allTags.value = response.data || []
    } catch (err) {
      console.error('Error fetching post tags:', err)
    } finally {
      isLoadingTags.value = false
    }
  }

  async function fetchPost(slug) {
    isLoadingPost.value = true
    error.value = null
    currentPost.value = null

    try {
      const response = await postsApi.getPost(slug)
      currentPost.value = response.data
    } catch (err) {
      error.value = 'Post not found'
      console.error('Error fetching post:', err)
    } finally {
      isLoadingPost.value = false
    }
  }

  function setTagFilter(tag) {
    selectedTag.value = tag
    pagination.value.page = 1
    fetchPosts()
  }

  function clearFilter() {
    selectedTag.value = null
    pagination.value.page = 1
    fetchPosts()
  }

  function setPage(page) {
    if (page >= 1 && page <= pagination.value.totalPages) {
      pagination.value.page = page
      fetchPosts()
    }
  }

  function clearCurrentPost() {
    currentPost.value = null
  }

  return {
    // State
    posts,
    currentPost,
    selectedTag,
    allTags,
    pagination,
    isLoading,
    isLoadingTags,
    isLoadingPost,
    error,
    // Getters
    hasActiveFilter,
    // Actions
    fetchPosts,
    fetchTags,
    fetchPost,
    setTagFilter,
    clearFilter,
    setPage,
    clearCurrentPost
  }
})
