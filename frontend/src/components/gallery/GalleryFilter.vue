<template>
  <div class="gallery-filter">
    <div class="filter-bar">
      <!-- Year filter -->
      <div class="filter-group">
        <select
          class="filter-select"
          :value="store.filters.year"
          @change="store.setYearFilter($event.target.value ? Number($event.target.value) : null)"
        >
          <option :value="null">All Years</option>
          <option v-for="year in store.filterOptions.years" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
      </div>

      <!-- Location filter -->
      <div class="filter-group">
        <select
          class="filter-select"
          :value="store.filters.location"
          @change="store.setLocationFilter($event.target.value || null)"
        >
          <option value="">All Locations</option>
          <option v-for="loc in store.filterOptions.locations" :key="loc" :value="loc">
            {{ loc }}
          </option>
        </select>
      </div>

      <!-- Clear filters -->
      <button
        class="filter-clear"
        v-if="store.hasActiveFilters"
        @click="store.clearFilters()"
      >
        Clear Filters
        <span class="filter-count">{{ store.activeFilterCount }}</span>
      </button>
    </div>

    <!-- Tag chips -->
    <div class="filter-tags" v-if="store.filterOptions.tags && store.filterOptions.tags.length > 0">
      <button
        v-for="tag in store.filterOptions.tags"
        :key="tag"
        class="tag-chip"
        :class="{ active: store.filters.tags.includes(tag) }"
        @click="store.toggleTagFilter(tag)"
      >
        {{ tag }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { useGalleryStore } from '@/stores/gallery'

const store = useGalleryStore()
</script>

<style scoped>
.gallery-filter {
  margin-bottom: 2rem;
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-bottom: 1rem;
}

.filter-select {
  appearance: none;
  -webkit-appearance: none;
  padding: 0.55rem 2.2rem 0.55rem 1rem;
  font-size: 0.9rem;
  font-family: inherit;
  color: var(--color-text);
  background: var(--aero-glass-bg-solid);
  backdrop-filter: blur(8px);
  border: 1px solid var(--aero-glass-border);
  border-radius: var(--aero-border-radius-sm);
  box-shadow: var(--aero-glass-shadow), inset 0 1px 0 rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
  /* Arrow icon */
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
}

.filter-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15), var(--aero-glass-shadow);
}

.filter-clear {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 1rem;
  font-size: 0.85rem;
  font-family: inherit;
  color: var(--color-danger);
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: var(--aero-border-radius-sm);
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.filter-clear:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.35);
}

.filter-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
  background: var(--color-danger);
  border-radius: 50%;
}

/* Tag chips */
.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag-chip {
  padding: 0.35rem 0.85rem;
  font-size: 0.8rem;
  font-family: inherit;
  color: var(--color-text-secondary);
  background: var(--aero-glass-bg-solid);
  border: 1px solid var(--aero-glass-border);
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tag-chip:hover {
  background: rgba(59, 130, 246, 0.08);
  border-color: rgba(59, 130, 246, 0.3);
  color: var(--color-primary);
}

.tag-chip.active {
  background: rgba(59, 130, 246, 0.12);
  border-color: var(--color-primary);
  color: var(--color-primary);
  font-weight: 500;
  box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.15);
}

/* Responsive */
@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-select {
    width: 100%;
  }
}
</style>
