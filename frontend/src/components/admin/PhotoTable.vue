<template>
  <div class="photo-table-container">
    <table class="photo-table">
      <thead>
        <tr>
          <th class="col-image">Image</th>
          <th class="col-title">Title</th>
          <th class="col-date">Date</th>
          <th class="col-location">Location</th>
          <th class="col-tags">Tags</th>
          <th class="col-actions">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td colspan="6" class="loading-cell">
            <div class="loading-spinner"></div>
            Loading...
          </td>
        </tr>
        <tr v-else-if="photos.length === 0">
          <td colspan="6" class="empty-cell">
            No photos found. Click "Add Photo" to create one.
          </td>
        </tr>
        <tr v-else v-for="photo in photos" :key="photo.id">
          <td class="col-image">
            <img
              :src="photo.thumbnail || photo.url"
              :alt="photo.title"
              class="thumbnail"
              loading="lazy"
            />
          </td>
          <td class="col-title">
            <div class="title-cell">
              <span class="photo-title">{{ photo.title }}</span>
              <span class="photo-description" v-if="photo.description">
                {{ photo.description }}
              </span>
            </div>
          </td>
          <td class="col-date">{{ formatDate(photo.date) }}</td>
          <td class="col-location">{{ photo.location || '-' }}</td>
          <td class="col-tags">
            <div class="tags-cell">
              <span
                v-for="tag in parseTags(photo.tags)"
                :key="tag"
                class="tag-chip"
              >
                {{ tag }}
              </span>
              <span v-if="parseTags(photo.tags).length === 0">-</span>
            </div>
          </td>
          <td class="col-actions">
            <button class="action-btn edit" @click="$emit('edit', photo)" title="Edit">
              <EditIcon />
            </button>
            <button class="action-btn delete" @click="$emit('delete', photo)" title="Delete">
              <TrashIcon />
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { EditIcon, TrashIcon } from '@/components/icons'

defineProps({
  photos: {
    type: Array,
    default: () => []
  },
  loading: Boolean
})

defineEmits(['edit', 'delete'])

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

function parseTags(tags) {
  if (!tags) return []
  if (Array.isArray(tags)) return tags
  try {
    return JSON.parse(tags)
  } catch {
    return []
  }
}
</script>

<style scoped>
.photo-table-container {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  overflow: hidden;
  overflow-x: auto;
}

.photo-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 700px;
}

.photo-table th,
.photo-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.photo-table th {
  background: var(--color-bg-secondary);
  font-weight: 600;
  color: var(--color-text-secondary);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.photo-table tbody tr:last-child td {
  border-bottom: none;
}

.photo-table tbody tr:hover {
  background: var(--color-bg-secondary);
}

.col-image {
  width: 80px;
}

.col-title {
  min-width: 200px;
}

.col-date {
  width: 120px;
}

.col-location {
  width: 150px;
}

.col-tags {
  width: 180px;
}

.col-actions {
  width: 100px;
}

.thumbnail {
  width: 60px;
  height: 40px;
  object-fit: cover;
  border-radius: 4px;
  background: var(--color-bg-secondary);
}

.title-cell {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.photo-title {
  font-weight: 500;
  color: var(--color-text);
}

.photo-description {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 250px;
}

.tags-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.tag-chip {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  font-size: 0.75rem;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  color: var(--color-text-secondary);
}

.action-btn {
  padding: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-secondary);
  border-radius: 6px;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--color-bg-secondary);
}

.action-btn.delete:hover {
  color: var(--color-danger);
}

.action-btn.edit:hover {
  color: var(--color-primary);
}

.loading-cell,
.empty-cell {
  text-align: center;
  padding: 3rem !important;
  color: var(--color-text-secondary);
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 0.5rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
