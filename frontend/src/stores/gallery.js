import { defineStore } from 'pinia'
import { galleryApi } from '@/api'

export const useGalleryStore = defineStore('gallery', {
  state: () => ({
    // Photo data
    photos: [],

    // Filter state
    filters: {
      year: null,
      location: null,
      tags: []
    },

    // Filter options from API
    filterOptions: {
      years: [],
      locations: [],
      tags: []
    },

    // Pagination
    pagination: {
      page: 1,
      pageSize: 20,
      total: 0,
      totalPages: 0
    },

    // Lightbox state
    selectedPhoto: null,
    selectedIndex: -1,

    // Loading state
    isLoading: false,
    error: null
  }),

  getters: {
    // Check if any filter is active
    hasActiveFilters: (state) => {
      return state.filters.year !== null ||
             state.filters.location !== null ||
             state.filters.tags.length > 0
    },

    // Get active filter count
    activeFilterCount: (state) => {
      let count = 0
      if (state.filters.year) count++
      if (state.filters.location) count++
      count += state.filters.tags.length
      return count
    }
  },

  actions: {
    // Fetch photos with current filters and pagination
    async fetchPhotos() {
      this.isLoading = true
      this.error = null

      try {
        const params = {
          page: this.pagination.page,
          pageSize: this.pagination.pageSize
        }

        // Add filters
        if (this.filters.year) {
          params.year = this.filters.year
        }
        if (this.filters.location) {
          params.location = this.filters.location
        }
        if (this.filters.tags.length > 0) {
          params.tags = this.filters.tags.join(',')
        }

        const response = await galleryApi.getPhotos(params)
        this.photos = response.data.photos || []
        this.pagination = response.data.pagination || this.pagination
      } catch (error) {
        this.error = 'Failed to fetch photos'
        console.error('Error fetching photos:', error)
      } finally {
        this.isLoading = false
      }
    },

    // Fetch filter options
    async fetchFilterOptions() {
      try {
        const response = await galleryApi.getFilterOptions()
        this.filterOptions = response.data || { years: [], locations: [], tags: [] }
      } catch (error) {
        console.error('Error fetching filter options:', error)
      }
    },

    // Set year filter
    setYearFilter(year) {
      this.filters.year = year
      this.pagination.page = 1
      this.fetchPhotos()
    },

    // Set location filter
    setLocationFilter(location) {
      this.filters.location = location
      this.pagination.page = 1
      this.fetchPhotos()
    },

    // Toggle tag filter
    toggleTagFilter(tag) {
      const index = this.filters.tags.indexOf(tag)
      if (index === -1) {
        this.filters.tags.push(tag)
      } else {
        this.filters.tags.splice(index, 1)
      }
      this.pagination.page = 1
      this.fetchPhotos()
    },

    // Clear all filters
    clearFilters() {
      this.filters = {
        year: null,
        location: null,
        tags: []
      }
      this.pagination.page = 1
      this.fetchPhotos()
    },

    // Set page
    setPage(page) {
      if (page >= 1 && page <= this.pagination.totalPages) {
        this.pagination.page = page
        this.fetchPhotos()
      }
    },

    // Open lightbox
    openLightbox(photo) {
      this.selectedPhoto = photo
      this.selectedIndex = this.photos.findIndex(p => p.id === photo.id)
    },

    // Close lightbox
    closeLightbox() {
      this.selectedPhoto = null
      this.selectedIndex = -1
    },

    // Navigate to next photo in lightbox
    nextPhoto() {
      if (this.selectedIndex < this.photos.length - 1) {
        this.selectedIndex++
        this.selectedPhoto = this.photos[this.selectedIndex]
      }
    },

    // Navigate to previous photo in lightbox
    prevPhoto() {
      if (this.selectedIndex > 0) {
        this.selectedIndex--
        this.selectedPhoto = this.photos[this.selectedIndex]
      }
    }
  }
})
