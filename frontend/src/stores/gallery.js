import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { galleryApi } from '@/api'

export const useGalleryStore = defineStore('gallery', () => {
  // State
  const photos = ref([])
  const filters = ref({
    year: null,
    location: null,
    tags: []
  })
  const filterOptions = ref({
    years: [],
    locations: [],
    tags: []
  })
  const pagination = ref({
    page: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0
  })
  const selectedPhoto = ref(null)
  const selectedIndex = ref(-1)
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const hasActiveFilters = computed(() => {
    return filters.value.year !== null ||
           filters.value.location !== null ||
           filters.value.tags.length > 0
  })

  const activeFilterCount = computed(() => {
    let count = 0
    if (filters.value.year) count++
    if (filters.value.location) count++
    count += filters.value.tags.length
    return count
  })

  // Actions
  async function fetchPhotos() {
    isLoading.value = true
    error.value = null

    try {
      const params = {
        page: pagination.value.page,
        pageSize: pagination.value.pageSize
      }

      if (filters.value.year) {
        params.year = filters.value.year
      }
      if (filters.value.location) {
        params.location = filters.value.location
      }
      if (filters.value.tags.length > 0) {
        params.tags = filters.value.tags.join(',')
      }

      const response = await galleryApi.getPhotos(params)
      photos.value = response.data.photos || []
      pagination.value = response.data.pagination || pagination.value
    } catch (err) {
      error.value = 'Failed to fetch photos'
      console.error('Error fetching photos:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchFilterOptions() {
    try {
      const response = await galleryApi.getFilterOptions()
      filterOptions.value = response.data || { years: [], locations: [], tags: [] }
    } catch (err) {
      console.error('Error fetching filter options:', err)
    }
  }

  function setYearFilter(year) {
    filters.value.year = year
    pagination.value.page = 1
    fetchPhotos()
  }

  function setLocationFilter(location) {
    filters.value.location = location
    pagination.value.page = 1
    fetchPhotos()
  }

  function toggleTagFilter(tag) {
    const index = filters.value.tags.indexOf(tag)
    if (index === -1) {
      filters.value.tags.push(tag)
    } else {
      filters.value.tags.splice(index, 1)
    }
    pagination.value.page = 1
    fetchPhotos()
  }

  function clearFilters() {
    filters.value = {
      year: null,
      location: null,
      tags: []
    }
    pagination.value.page = 1
    fetchPhotos()
  }

  function setPage(page) {
    if (page >= 1 && page <= pagination.value.totalPages) {
      pagination.value.page = page
      fetchPhotos()
    }
  }

  function openLightbox(photo) {
    selectedPhoto.value = photo
    selectedIndex.value = photos.value.findIndex(p => p.id === photo.id)
  }

  function closeLightbox() {
    selectedPhoto.value = null
    selectedIndex.value = -1
  }

  function nextPhoto() {
    if (selectedIndex.value < photos.value.length - 1) {
      selectedIndex.value++
      selectedPhoto.value = photos.value[selectedIndex.value]
    }
  }

  function prevPhoto() {
    if (selectedIndex.value > 0) {
      selectedIndex.value--
      selectedPhoto.value = photos.value[selectedIndex.value]
    }
  }

  return {
    // State
    photos,
    filters,
    filterOptions,
    pagination,
    selectedPhoto,
    selectedIndex,
    isLoading,
    error,
    // Getters
    hasActiveFilters,
    activeFilterCount,
    // Actions
    fetchPhotos,
    fetchFilterOptions,
    setYearFilter,
    setLocationFilter,
    toggleTagFilter,
    clearFilters,
    setPage,
    openLightbox,
    closeLightbox,
    nextPhoto,
    prevPhoto
  }
})
