<template>
  <div class="photos-page">
    <!-- Page header with actions -->
    <div class="page-header">
      <div class="header-info">
        <p class="total-count">{{ pagination.total }} photos total</p>
      </div>
      <button class="add-btn" @click="openDrawer()">
        <PlusIcon />
        Add Photo
      </button>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search photos..."
        class="search-input"
        @input="debouncedSearch"
      />
      <select v-model="selectedYear" class="filter-select" @change="handleFilterChange">
        <option :value="null">All Years</option>
        <option v-for="year in filterOptions.years" :key="year" :value="year">
          {{ year }}
        </option>
      </select>
      <select v-model="selectedLocation" class="filter-select" @change="handleFilterChange">
        <option :value="null">All Locations</option>
        <option v-for="location in filterOptions.locations" :key="location" :value="location">
          {{ location }}
        </option>
      </select>
    </div>

    <!-- Photos table -->
    <PhotoTable
      :photos="photos"
      :loading="isLoading"
      @edit="openDrawer"
      @delete="confirmDelete"
    />

    <!-- Pagination -->
    <div class="pagination" v-if="pagination.totalPages > 1">
      <button
        class="pagination-btn"
        :disabled="pagination.page <= 1"
        @click="setPage(pagination.page - 1)"
      >
        <ChevronLeftIcon />
        Previous
      </button>
      <span class="pagination-info">Page {{ pagination.page }} of {{ pagination.totalPages }}</span>
      <button
        class="pagination-btn"
        :disabled="pagination.page >= pagination.totalPages"
        @click="setPage(pagination.page + 1)"
      >
        Next
        <ChevronRightIcon />
      </button>
    </div>

    <!-- Photo drawer (create/edit form) -->
    <PhotoDrawer
      :open="drawerOpen"
      :photo="selectedPhoto"
      @close="closeDrawer"
      @saved="handleSaved"
    />

    <!-- Delete confirmation dialog -->
    <ConfirmDialog
      :open="deleteDialogOpen"
      title="Delete Photo"
      message="Are you sure you want to delete this photo? This action cannot be undone."
      @confirm="handleDelete"
      @cancel="deleteDialogOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminPhotoApi } from '@/api/admin/photos'
import PhotoTable from '@/components/admin/PhotoTable.vue'
import PhotoDrawer from '@/components/admin/PhotoDrawer.vue'
import ConfirmDialog from '@/components/admin/ConfirmDialog.vue'
import { PlusIcon, ChevronLeftIcon, ChevronRightIcon } from '@/components/icons'

// State
const photos = ref([])
const isLoading = ref(false)
const pagination = ref({ page: 1, pageSize: 20, total: 0, totalPages: 0 })
const filterOptions = ref({ years: [], locations: [], tags: [] })

// Filters
const searchQuery = ref('')
const selectedYear = ref(null)
const selectedLocation = ref(null)

// Drawer state
const drawerOpen = ref(false)
const selectedPhoto = ref(null)

// Delete dialog state
const deleteDialogOpen = ref(false)
const photoToDelete = ref(null)

// Debounce timer
let searchTimeout = null

// Fetch photos
async function fetchPhotos() {
  isLoading.value = true
  try {
    const params = {
      page: pagination.value.page,
      pageSize: pagination.value.pageSize
    }
    if (selectedYear.value) {
      params.year = selectedYear.value
    }
    if (selectedLocation.value) {
      params.location = selectedLocation.value
    }
    const response = await adminPhotoApi.getPhotos(params)
    photos.value = response.data.photos || []
    pagination.value = response.data.pagination
  } catch (error) {
    console.error('Failed to fetch photos:', error)
  } finally {
    isLoading.value = false
  }
}

// Fetch filter options
async function fetchFilterOptions() {
  try {
    const response = await adminPhotoApi.getFilterOptions()
    filterOptions.value = response.data || { years: [], locations: [], tags: [] }
  } catch (error) {
    console.error('Failed to fetch filter options:', error)
  }
}

// Debounced search
function debouncedSearch() {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    pagination.value.page = 1
    fetchPhotos()
  }, 300)
}

// Handle filter change
function handleFilterChange() {
  pagination.value.page = 1
  fetchPhotos()
}

// Pagination
function setPage(page) {
  pagination.value.page = page
  fetchPhotos()
}

// Drawer handlers
function openDrawer(photo = null) {
  selectedPhoto.value = photo
  drawerOpen.value = true
}

function closeDrawer() {
  drawerOpen.value = false
  selectedPhoto.value = null
}

function handleSaved() {
  closeDrawer()
  fetchPhotos()
  fetchFilterOptions() // Refresh filter options in case new locations/tags
}

// Delete handlers
function confirmDelete(photo) {
  photoToDelete.value = photo
  deleteDialogOpen.value = true
}

async function handleDelete() {
  if (!photoToDelete.value) return
  try {
    await adminPhotoApi.deletePhoto(photoToDelete.value.id)
    fetchPhotos()
    fetchFilterOptions()
  } catch (error) {
    console.error('Failed to delete photo:', error)
    alert('Failed to delete photo. Please try again.')
  } finally {
    deleteDialogOpen.value = false
    photoToDelete.value = null
  }
}

// Init
onMounted(() => {
  fetchPhotos()
  fetchFilterOptions()
})
</script>

<style scoped>
.photos-page {
  max-width: 1400px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.total-count {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.add-btn:hover {
  background: var(--color-primary-hover);
}

.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 200px;
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 0.9rem;
  background: var(--color-bg);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-bg);
  font-size: 0.9rem;
  cursor: pointer;
  min-width: 140px;
}

.filter-select:focus {
  outline: none;
  border-color: var(--color-primary);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

.pagination-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-bg);
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--color-bg-secondary);
  border-color: var(--color-primary);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .filters-bar {
    flex-direction: column;
  }

  .search-input,
  .filter-select {
    width: 100%;
  }
}
</style>
