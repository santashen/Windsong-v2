<template>
  <div class="gallery-card" @click="$emit('click', photo)">
    <div class="card-image-container">
      <img
        :src="photo.thumbnail || photo.url"
        :alt="photo.title"
        loading="lazy"
        @load="imageLoaded = true"
      />
      <div class="card-image-skeleton" v-if="!imageLoaded"></div>
    </div>
    <div class="card-content">
      <h3 class="card-title">{{ photo.title }}</h3>
      <p class="card-description" v-if="photo.description">{{ photo.description }}</p>
      <div class="card-meta">
        <span class="card-date" v-if="photo.date">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          {{ formatDate(photo.date) }}
        </span>
        <span class="card-location" v-if="photo.location">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
            <circle cx="12" cy="10" r="3"></circle>
          </svg>
          {{ photo.location }}
        </span>
      </div>
      <div class="card-tags" v-if="parsedTags.length > 0">
        <span class="tag" v-for="tag in parsedTags" :key="tag">{{ tag }}</span>
      </div>
    </div>
    <!-- Aero shine overlay -->
    <div class="card-shine"></div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  photo: {
    type: Object,
    required: true
  }
})

defineEmits(['click'])

const imageLoaded = ref(false)

const parsedTags = computed(() => {
  if (!props.photo.tags) return []
  if (Array.isArray(props.photo.tags)) return props.photo.tags
  try {
    return JSON.parse(props.photo.tags)
  } catch {
    return []
  }
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}
</script>

<style scoped>
.gallery-card {
  position: relative;
  background: var(--aero-gradient-card);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid var(--aero-glass-border);
  border-radius: var(--aero-border-radius);
  box-shadow: var(--aero-glass-shadow), inset 0 1px 0 rgba(255, 255, 255, 0.5);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.gallery-card:hover {
  transform: translateY(-6px);
  box-shadow:
    0 12px 40px rgba(31, 38, 135, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

/* Shine effect on hover */
.card-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.3) 50%,
    transparent 100%
  );
  pointer-events: none;
  transition: none;
}

.gallery-card:hover .card-shine {
  animation: shine-sweep 0.6s ease-out;
}

@keyframes shine-sweep {
  from { left: -100%; }
  to { left: 100%; }
}

/* Image */
.card-image-container {
  position: relative;
  width: 100%;
  padding-top: 66.67%; /* 3:2 aspect ratio */
  overflow: hidden;
}

.card-image-container img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.gallery-card:hover .card-image-container img {
  transform: scale(1.05);
}

.card-image-skeleton {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, #e8f0fe 25%, #d0e3ff 50%, #e8f0fe 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Content */
.card-content {
  padding: 1rem;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 0.4rem;
  text-shadow: var(--aero-text-shadow);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-description {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.6rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.6rem;
}

.card-date,
.card-location {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.tag {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  font-size: 0.7rem;
  color: #4a90d9;
  background: rgba(74, 144, 217, 0.1);
  border: 1px solid rgba(74, 144, 217, 0.2);
  border-radius: 999px;
  white-space: nowrap;
}
</style>
