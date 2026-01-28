<template>
  <div class="blog-filter">
    <div class="filter-label">
      <span class="pixel-icon">🏷️</span>
      标签筛选:
    </div>
    <div class="filter-tags">
      <button
        class="filter-tag"
        :class="{ active: !store.selectedTag }"
        @click="store.clearFilter()"
      >
        全部
      </button>
      <button
        v-for="tag in store.allTags"
        :key="tag"
        class="filter-tag"
        :class="{ active: store.selectedTag === tag }"
        @click="store.setTagFilter(tag)"
      >
        #{{ tag }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { useBlogStore } from '@/stores/blog'

const store = useBlogStore()
</script>

<style scoped>
.blog-filter {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border: 4px solid #64748b;
  box-shadow: 0 4px 0 #475569;
  margin-bottom: 2rem;
}

.filter-label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: #334155;
  white-space: nowrap;
}

.pixel-icon {
  font-size: 1rem;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.filter-tag {
  padding: 0.35rem 0.75rem;
  font-size: 0.8rem;
  font-family: inherit;
  font-weight: 600;
  color: #065f46;
  background: linear-gradient(180deg, #d1fae5 0%, #a7f3d0 100%);
  border: 2px solid #047857;
  box-shadow: 0 2px 0 #065f46;
  cursor: pointer;
  transition: all 0.1s ease;
}

.filter-tag:hover:not(.active) {
  transform: translateY(-1px);
  box-shadow: 0 3px 0 #065f46;
  background: linear-gradient(180deg, #a7f3d0 0%, #6ee7b7 100%);
}

.filter-tag:active:not(.active) {
  transform: translateY(1px);
  box-shadow: 0 1px 0 #065f46;
}

.filter-tag.active {
  color: #fef3c7;
  background: linear-gradient(180deg, #059669 0%, #047857 100%);
  border-color: #065f46;
  box-shadow: 0 2px 0 #065f46, inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* Responsive */
@media (max-width: 640px) {
  .blog-filter {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .filter-tag {
    font-size: 0.75rem;
    padding: 0.3rem 0.6rem;
  }
}
</style>
