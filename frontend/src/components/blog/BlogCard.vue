<template>
  <div class="blog-card" @click="$emit('click', post)">
    <!-- Pixel corner decorations -->
    <div class="pixel-corner top-left"></div>
    <div class="pixel-corner top-right"></div>
    <div class="pixel-corner bottom-left"></div>
    <div class="pixel-corner bottom-right"></div>

    <div class="card-inner">
      <!-- Title with pixel underline -->
      <h3 class="card-title">{{ post.title }}</h3>
      <div class="pixel-divider"></div>

      <!-- Meta info -->
      <div class="card-meta">
        <span class="card-date">
          <span class="pixel-icon">📅</span>
          {{ formatDate(post.date) }}
        </span>
      </div>

      <!-- Tags -->
      <div class="card-tags" v-if="post.tags && post.tags.length > 0">
        <span
          class="pixel-tag"
          v-for="tag in post.tags"
          :key="tag"
          @click.stop="$emit('tag-click', tag)"
        >
          #{{ tag }}
        </span>
      </div>
    </div>

    <!-- Hover indicator -->
    <div class="read-more">
      <span class="arrow">▶</span> 阅读
    </div>
  </div>
</template>

<script setup>
defineProps({
  post: {
    type: Object,
    required: true
  }
})

defineEmits(['click', 'tag-click'])

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}
</script>

<style scoped>
/* Pixel font simulation - using system fonts with specific styling */
.blog-card {
  position: relative;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border: 4px solid #64748b;
  padding: 0;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  image-rendering: pixelated;

  /* Pixel-style outer glow */
  box-shadow:
    0 4px 0 #475569,
    0 6px 0 rgba(71, 85, 105, 0.3),
    inset 0 2px 0 rgba(255, 255, 255, 0.8);
}

.blog-card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 8px 0 #475569,
    0 12px 0 rgba(71, 85, 105, 0.2),
    inset 0 2px 0 rgba(255, 255, 255, 0.9);
}

.blog-card:active {
  transform: translateY(0);
  box-shadow:
    0 2px 0 #475569,
    inset 0 2px 0 rgba(255, 255, 255, 0.8);
}

/* Pixel corners */
.pixel-corner {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #ffffff;
  z-index: 1;
}

.pixel-corner::before,
.pixel-corner::after {
  content: '';
  position: absolute;
  background: #64748b;
}

.top-left {
  top: -4px;
  left: -4px;
}
.top-left::before {
  width: 4px;
  height: 8px;
  top: 0;
  right: 0;
}
.top-left::after {
  width: 8px;
  height: 4px;
  bottom: 0;
  left: 0;
}

.top-right {
  top: -4px;
  right: -4px;
}
.top-right::before {
  width: 4px;
  height: 8px;
  top: 0;
  left: 0;
}
.top-right::after {
  width: 8px;
  height: 4px;
  bottom: 0;
  right: 0;
}

.bottom-left {
  bottom: -4px;
  left: -4px;
}
.bottom-left::before {
  width: 4px;
  height: 8px;
  bottom: 0;
  right: 0;
}
.bottom-left::after {
  width: 8px;
  height: 4px;
  top: 0;
  left: 0;
}

.bottom-right {
  bottom: -4px;
  right: -4px;
}
.bottom-right::before {
  width: 4px;
  height: 8px;
  bottom: 0;
  left: 0;
}
.bottom-right::after {
  width: 8px;
  height: 4px;
  top: 0;
  right: 0;
}

/* Card content */
.card-inner {
  padding: 1rem 1.25rem;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #334155;
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
  /* Pixel-style text shadow */
  text-shadow: 1px 1px 0 rgba(255, 255, 255, 0.8);
}

/* Pixel divider */
.pixel-divider {
  height: 4px;
  margin: 0.75rem 0;
  background: repeating-linear-gradient(
    90deg,
    #94a3b8 0px,
    #94a3b8 4px,
    transparent 4px,
    transparent 8px
  );
}

/* Meta */
.card-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.card-date {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 500;
}

.pixel-icon {
  font-size: 0.9rem;
}

/* Tags */
.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.pixel-tag {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #065f46;
  background: linear-gradient(180deg, #a7f3d0 0%, #6ee7b7 100%);
  border: 2px solid #047857;
  box-shadow: 0 2px 0 #065f46;
  transition: all 0.1s ease;
}

.pixel-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 3px 0 #065f46;
  background: linear-gradient(180deg, #6ee7b7 0%, #34d399 100%);
}

.pixel-tag:active {
  transform: translateY(1px);
  box-shadow: 0 1px 0 #065f46;
}

/* Read more indicator */
.read-more {
  position: absolute;
  bottom: 0.75rem;
  right: 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #3b82f6;
  opacity: 0;
  transform: translateX(-8px);
  transition: all 0.2s ease;
}

.blog-card:hover .read-more {
  opacity: 1;
  transform: translateX(0);
}

.read-more .arrow {
  display: inline-block;
  animation: bounce-right 0.6s ease infinite;
}

@keyframes bounce-right {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(3px); }
}

/* Responsive */
@media (max-width: 640px) {
  .card-inner {
    padding: 0.875rem 1rem;
  }

  .card-title {
    font-size: 1rem;
  }

  .pixel-tag {
    font-size: 0.7rem;
    padding: 0.2rem 0.5rem;
  }
}
</style>
