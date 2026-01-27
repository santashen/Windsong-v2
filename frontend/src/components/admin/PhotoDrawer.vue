<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div class="drawer-overlay" v-if="open" @click.self="$emit('close')">
        <div class="drawer-panel">
          <div class="drawer-header">
            <h2>{{ isEdit ? 'Edit Photo' : 'Add Photo' }}</h2>
            <button class="close-btn" @click="$emit('close')">
              <CloseIcon />
            </button>
          </div>

          <form class="drawer-form" @submit.prevent="handleSubmit">
            <div class="form-group">
              <label for="url">Image URL <span class="required">*</span></label>
              <input
                id="url"
                v-model="form.url"
                type="url"
                required
                placeholder="https://example.com/image.jpg"
              />
            </div>

            <div class="form-group">
              <label for="thumbnail">Thumbnail URL</label>
              <input
                id="thumbnail"
                v-model="form.thumbnail"
                type="url"
                placeholder="Optional smaller version"
              />
            </div>

            <div class="form-group">
              <label for="title">Title <span class="required">*</span></label>
              <input
                id="title"
                v-model="form.title"
                type="text"
                required
                placeholder="Photo title"
              />
            </div>

            <div class="form-group">
              <label for="description">Description</label>
              <textarea
                id="description"
                v-model="form.description"
                rows="3"
                placeholder="Optional description"
              ></textarea>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="date">Date <span class="required">*</span></label>
                <input id="date" v-model="form.date" type="date" required />
              </div>
              <div class="form-group">
                <label for="location">Location</label>
                <input
                  id="location"
                  v-model="form.location"
                  type="text"
                  placeholder="e.g., Beach, Mountain"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="city">City</label>
                <input
                  id="city"
                  v-model="form.city"
                  type="text"
                  placeholder="e.g., Tokyo"
                />
              </div>
              <div class="form-group">
                <label for="country">Country</label>
                <input
                  id="country"
                  v-model="form.country"
                  type="text"
                  placeholder="e.g., Japan"
                />
              </div>
            </div>

            <div class="form-group">
              <label for="tags">Tags</label>
              <input
                id="tags"
                v-model="tagsInput"
                type="text"
                placeholder="Comma separated: nature, travel, sunset"
              />
              <span class="form-hint">Separate tags with commas</span>
            </div>

            <div class="form-group">
              <label for="aspectRatio">Aspect Ratio</label>
              <select id="aspectRatio" v-model="form.aspectRatio">
                <option value="">Auto</option>
                <option value="16:9">16:9 (Landscape)</option>
                <option value="4:3">4:3 (Standard)</option>
                <option value="3:2">3:2 (Classic)</option>
                <option value="1:1">1:1 (Square)</option>
                <option value="9:16">9:16 (Portrait)</option>
              </select>
            </div>

            <!-- Image preview -->
            <div class="form-group" v-if="form.url">
              <label>Preview</label>
              <div class="image-preview">
                <img
                  :src="form.url"
                  alt="Preview"
                  @error="imageError = true"
                  @load="imageError = false"
                />
                <p v-if="imageError" class="preview-error">Failed to load image</p>
              </div>
            </div>

            <div class="drawer-footer">
              <button type="button" class="cancel-btn" @click="$emit('close')">
                Cancel
              </button>
              <button type="submit" class="submit-btn" :disabled="isSubmitting">
                {{ isSubmitting ? 'Saving...' : (isEdit ? 'Update' : 'Create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { adminPhotoApi } from '@/api/admin/photos'
import { CloseIcon } from '@/components/icons'

const props = defineProps({
  open: Boolean,
  photo: Object
})

const emit = defineEmits(['close', 'saved'])

const isEdit = computed(() => !!props.photo)

const defaultForm = {
  url: '',
  thumbnail: '',
  title: '',
  description: '',
  date: '',
  location: '',
  city: '',
  country: '',
  tags: [],
  aspectRatio: ''
}

const form = ref({ ...defaultForm })
const tagsInput = ref('')
const isSubmitting = ref(false)
const imageError = ref(false)

// Sync form with photo prop
watch(() => props.photo, (photo) => {
  if (photo) {
    form.value = {
      url: photo.url || '',
      thumbnail: photo.thumbnail || '',
      title: photo.title || '',
      description: photo.description || '',
      date: photo.date ? photo.date.split('T')[0] : '',
      location: photo.location || '',
      city: photo.city || '',
      country: photo.country || '',
      tags: parseTags(photo.tags),
      aspectRatio: photo.aspectRatio || ''
    }
    tagsInput.value = form.value.tags.join(', ')
  } else {
    form.value = { ...defaultForm }
    tagsInput.value = ''
  }
  imageError.value = false
}, { immediate: true })

// Reset form when drawer closes
watch(() => props.open, (open) => {
  if (!open) {
    form.value = { ...defaultForm }
    tagsInput.value = ''
    imageError.value = false
  }
})

function parseTags(tags) {
  if (!tags) return []
  if (Array.isArray(tags)) return tags
  try {
    return JSON.parse(tags)
  } catch {
    return []
  }
}

async function handleSubmit() {
  isSubmitting.value = true

  // Parse tags from input
  const tags = tagsInput.value
    .split(',')
    .map(t => t.trim())
    .filter(t => t)

  const payload = {
    ...form.value,
    tags
  }

  try {
    if (isEdit.value) {
      await adminPhotoApi.updatePhoto(props.photo.id, payload)
    } else {
      await adminPhotoApi.createPhoto(payload)
    }
    emit('saved')
  } catch (error) {
    console.error('Failed to save photo:', error)
    const message = error.response?.data?.error || 'Failed to save photo. Please check your input and try again.'
    alert(message)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
}

.drawer-panel {
  width: 500px;
  max-width: 100%;
  height: 100%;
  background: var(--color-bg);
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.15);
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.drawer-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text);
}

.close-btn {
  padding: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-secondary);
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text);
}

.drawer-form {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--color-text);
}

.required {
  color: var(--color-danger);
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 0.95rem;
  font-family: inherit;
  background: var(--color-bg);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-hint {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.image-preview {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  overflow: hidden;
  background: var(--color-bg-secondary);
}

.image-preview img {
  width: 100%;
  max-height: 200px;
  object-fit: contain;
}

.preview-error {
  padding: 2rem;
  text-align: center;
  color: var(--color-danger);
  font-size: 0.9rem;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-bg);
  flex-shrink: 0;
}

.cancel-btn,
.submit-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.95rem;
}

.cancel-btn {
  background: none;
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.cancel-btn:hover {
  background: var(--color-bg-secondary);
}

.submit-btn {
  background: var(--color-primary);
  border: none;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Transition */
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.3s ease;
}

.drawer-enter-active .drawer-panel,
.drawer-leave-active .drawer-panel {
  transition: transform 0.3s ease;
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

.drawer-enter-from .drawer-panel,
.drawer-leave-to .drawer-panel {
  transform: translateX(100%);
}

@media (max-width: 640px) {
  .drawer-panel {
    width: 100%;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
