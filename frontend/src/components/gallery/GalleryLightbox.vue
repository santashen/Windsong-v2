<template>
  <Teleport to="body">
    <Transition name="lightbox">
      <div class="lightbox-overlay" v-if="store.selectedPhoto" @click.self="store.closeLightbox()">
        <!-- Close button -->
        <button class="lightbox-close" @click="store.closeLightbox()">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        <!-- Previous button -->
        <button
          class="lightbox-nav lightbox-prev"
          v-if="store.selectedIndex > 0"
          @click.stop="store.prevPhoto()"
        >
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>

        <!-- Photo content -->
        <div class="lightbox-content" @click.stop>
          <div class="lightbox-image-wrapper">
            <img
              :src="store.selectedPhoto.url"
              :alt="store.selectedPhoto.title"
              class="lightbox-image"
            />
          </div>
          <div class="lightbox-info">
            <h2 class="lightbox-title">{{ store.selectedPhoto.title }}</h2>
            <p class="lightbox-description" v-if="store.selectedPhoto.description">
              {{ store.selectedPhoto.description }}
            </p>
            <div class="lightbox-meta">
              <span class="lightbox-date" v-if="store.selectedPhoto.date">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="16" y1="2" x2="16" y2="6"></line>
                  <line x1="8" y1="2" x2="8" y2="6"></line>
                  <line x1="3" y1="10" x2="21" y2="10"></line>
                </svg>
                {{ formatDate(store.selectedPhoto.date) }}
              </span>
              <span class="lightbox-location" v-if="store.selectedPhoto.location">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                  <circle cx="12" cy="10" r="3"></circle>
                </svg>
                {{ store.selectedPhoto.location }}
              </span>
            </div>
            <div class="lightbox-tags" v-if="parsedTags.length > 0">
              <span class="lightbox-tag" v-for="tag in parsedTags" :key="tag">{{ tag }}</span>
            </div>
            <div class="lightbox-counter">
              {{ store.selectedIndex + 1 }} / {{ store.photos.length }}
            </div>
          </div>
        </div>

        <!-- Next button -->
        <button
          class="lightbox-nav lightbox-next"
          v-if="store.selectedIndex < store.photos.length - 1"
          @click.stop="store.nextPhoto()"
        >
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, watch, onUnmounted } from 'vue'
import { useGalleryStore } from '@/stores/gallery'

const store = useGalleryStore()

const parsedTags = computed(() => {
  if (!store.selectedPhoto?.tags) return []
  if (Array.isArray(store.selectedPhoto.tags)) return store.selectedPhoto.tags
  try {
    return JSON.parse(store.selectedPhoto.tags)
  } catch {
    return []
  }
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Keyboard navigation
function handleKeydown(e) {
  if (!store.selectedPhoto) return
  switch (e.key) {
    case 'Escape':
      store.closeLightbox()
      break
    case 'ArrowLeft':
      store.prevPhoto()
      break
    case 'ArrowRight':
      store.nextPhoto()
      break
  }
}

// Watch for lightbox open/close to manage body scroll and keyboard
watch(() => store.selectedPhoto, (photo) => {
  if (photo) {
    document.body.style.overflow = 'hidden'
    document.addEventListener('keydown', handleKeydown)
  } else {
    document.body.style.overflow = ''
    document.removeEventListener('keydown', handleKeydown)
  }
})

onUnmounted(() => {
  document.body.style.overflow = ''
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.lightbox-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Transition */
.lightbox-enter-active,
.lightbox-leave-active {
  transition: opacity 0.3s ease;
}

.lightbox-enter-from,
.lightbox-leave-to {
  opacity: 0;
}

.lightbox-enter-active .lightbox-content,
.lightbox-leave-active .lightbox-content {
  transition: transform 0.3s ease;
}

.lightbox-enter-from .lightbox-content {
  transform: scale(0.9);
}

.lightbox-leave-to .lightbox-content {
  transform: scale(0.9);
}

/* Close button */
.lightbox-close {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  color: white;
  cursor: pointer;
  transition: background 0.2s;
  z-index: 10;
}

.lightbox-close:hover {
  background: rgba(255, 255, 255, 0.25);
}

/* Navigation buttons */
.lightbox-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  color: white;
  cursor: pointer;
  transition: background 0.2s;
  z-index: 10;
}

.lightbox-nav:hover {
  background: rgba(255, 255, 255, 0.25);
}

.lightbox-prev { left: 1.5rem; }
.lightbox-next { right: 1.5rem; }

/* Content */
.lightbox-content {
  display: flex;
  flex-direction: column;
  max-width: 90vw;
  max-height: 90vh;
}

.lightbox-image-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-height: 0;
}

.lightbox-image {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: var(--aero-border-radius);
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.4);
}

/* Info panel */
.lightbox-info {
  padding: 1.2rem 0.5rem 0;
  color: white;
  text-align: center;
}

.lightbox-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
}

.lightbox-description {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.75);
  margin-bottom: 0.6rem;
}

.lightbox-meta {
  display: flex;
  justify-content: center;
  gap: 1.2rem;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.65);
  margin-bottom: 0.6rem;
}

.lightbox-date,
.lightbox-location {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.lightbox-tags {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 0.6rem;
}

.lightbox-tag {
  padding: 0.2rem 0.6rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 999px;
}

.lightbox-counter {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
}

/* Responsive */
@media (max-width: 768px) {
  .lightbox-nav {
    width: 40px;
    height: 40px;
  }

  .lightbox-prev { left: 0.75rem; }
  .lightbox-next { right: 0.75rem; }

  .lightbox-image {
    max-height: 55vh;
  }

  .lightbox-title {
    font-size: 1.1rem;
  }
}
</style>
