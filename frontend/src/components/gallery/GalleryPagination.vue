<template>
  <div class="gallery-pagination" v-if="store.pagination.totalPages > 1">
    <button
      class="page-btn"
      :disabled="store.pagination.page <= 1"
      @click="store.setPage(store.pagination.page - 1)"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="15 18 9 12 15 6"></polyline>
      </svg>
      Prev
    </button>

    <div class="page-numbers">
      <button
        v-for="page in visiblePages"
        :key="page"
        class="page-num"
        :class="{ active: page === store.pagination.page, ellipsis: page === '...' }"
        :disabled="page === '...'"
        @click="page !== '...' && store.setPage(page)"
      >
        {{ page }}
      </button>
    </div>

    <button
      class="page-btn"
      :disabled="store.pagination.page >= store.pagination.totalPages"
      @click="store.setPage(store.pagination.page + 1)"
    >
      Next
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="9 18 15 12 9 6"></polyline>
      </svg>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useGalleryStore } from '@/stores/gallery'

const store = useGalleryStore()

const visiblePages = computed(() => {
  const total = store.pagination.totalPages
  const current = store.pagination.page
  const pages = []

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
    return pages
  }

  // Always show first page
  pages.push(1)

  if (current > 3) {
    pages.push('...')
  }

  // Pages around current
  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  if (current < total - 2) {
    pages.push('...')
  }

  // Always show last page
  pages.push(total)

  return pages
})
</script>

<style scoped>
.gallery-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  padding: 2rem 0 3rem;
}

.page-btn {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  font-family: inherit;
  color: var(--color-text);
  background: var(--aero-glass-bg-solid);
  backdrop-filter: blur(8px);
  border: 1px solid var(--aero-glass-border);
  border-radius: var(--aero-border-radius-sm);
  box-shadow: var(--aero-glass-shadow), inset 0 1px 0 rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.95);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 0.25rem;
}

.page-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  font-size: 0.85rem;
  font-family: inherit;
  color: var(--color-text);
  background: var(--aero-glass-bg-solid);
  border: 1px solid var(--aero-glass-border);
  border-radius: var(--aero-border-radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-num:hover:not(:disabled):not(.active) {
  background: rgba(255, 255, 255, 0.95);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.page-num.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.page-num.ellipsis {
  background: transparent;
  border-color: transparent;
  cursor: default;
  box-shadow: none;
  color: var(--color-text-secondary);
}

/* Responsive */
@media (max-width: 480px) {
  .page-btn span {
    display: none;
  }

  .page-num {
    width: 32px;
    height: 32px;
    font-size: 0.8rem;
  }
}
</style>
