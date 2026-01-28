<template>
  <div class="blog-pagination" v-if="store.pagination.totalPages > 1">
    <button
      class="page-btn"
      :disabled="store.pagination.page <= 1"
      @click="store.setPage(store.pagination.page - 1)"
    >
      ◀ 上一页
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
      下一页 ▶
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useBlogStore } from '@/stores/blog'

const store = useBlogStore()

const visiblePages = computed(() => {
  const total = store.pagination.totalPages
  const current = store.pagination.page
  const pages = []

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
    return pages
  }

  pages.push(1)

  if (current > 3) {
    pages.push('...')
  }

  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  if (current < total - 2) {
    pages.push('...')
  }

  pages.push(total)

  return pages
})
</script>

<style scoped>
.blog-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem 0 3rem;
}

.page-btn {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  font-family: inherit;
  font-weight: 600;
  color: #334155;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border: 3px solid #64748b;
  box-shadow: 0 3px 0 #475569;
  cursor: pointer;
  transition: all 0.1s ease;
}

.page-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 0 #475569;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
}

.page-btn:active:not(:disabled) {
  transform: translateY(1px);
  box-shadow: 0 1px 0 #475569;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 0.35rem;
}

.page-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  font-size: 0.9rem;
  font-family: inherit;
  font-weight: 600;
  color: #334155;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border: 3px solid #64748b;
  box-shadow: 0 3px 0 #475569;
  cursor: pointer;
  transition: all 0.1s ease;
}

.page-num:hover:not(:disabled):not(.active) {
  transform: translateY(-2px);
  box-shadow: 0 5px 0 #475569;
}

.page-num:active:not(:disabled):not(.active) {
  transform: translateY(1px);
  box-shadow: 0 1px 0 #475569;
}

.page-num.active {
  color: #ffffff;
  background: linear-gradient(180deg, #3b82f6 0%, #2563eb 100%);
  border-color: #1d4ed8;
  box-shadow: 0 3px 0 #1e40af, inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

.page-num.ellipsis {
  background: transparent;
  border-color: transparent;
  box-shadow: none;
  cursor: default;
  color: #64748b;
}

/* Responsive */
@media (max-width: 480px) {
  .page-btn {
    padding: 0.4rem 0.75rem;
    font-size: 0.8rem;
  }

  .page-num {
    width: 32px;
    height: 32px;
    font-size: 0.8rem;
  }
}
</style>
