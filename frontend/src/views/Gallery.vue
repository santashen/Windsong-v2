<template>
  <div class="gallery-page">
    <Header />
    <main class="main-content gallery-background">
      <!-- Frutiger Aero background decorations -->
      <div class="aero-decorations">
        <div class="cloud cloud-1"></div>
        <div class="cloud cloud-2"></div>
        <div class="cloud cloud-3"></div>
        <div class="bubble bubble-1"></div>
        <div class="bubble bubble-2"></div>
        <div class="bubble bubble-3"></div>
      </div>

      <div class="container">
        <!-- Page header -->
        <section class="gallery-header">
          <h1 class="gallery-title">Gallery</h1>
          <p class="gallery-subtitle">Moments captured through the lens</p>
        </section>

        <!-- Filters -->
        <GalleryFilter />

        <!-- Loading state -->
        <div class="gallery-loading" v-if="store.isLoading && store.photos.length === 0">
          <div class="loading-grid">
            <div class="skeleton-card" v-for="n in 6" :key="n">
              <div class="skeleton-image"></div>
              <div class="skeleton-content">
                <div class="skeleton-line skeleton-title"></div>
                <div class="skeleton-line skeleton-text"></div>
                <div class="skeleton-line skeleton-text short"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty state -->
        <div class="gallery-empty" v-else-if="!store.isLoading && store.photos.length === 0">
          <div class="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
              <circle cx="8.5" cy="8.5" r="1.5"></circle>
              <polyline points="21 15 16 10 5 21"></polyline>
            </svg>
          </div>
          <p class="empty-text">No photos found</p>
          <p class="empty-hint" v-if="store.hasActiveFilters">
            Try adjusting your filters or <button class="empty-clear" @click="store.clearFilters()">clear all filters</button>
          </p>
        </div>

        <!-- Photo grid with loading overlay -->
        <div class="gallery-content" v-else>
          <Transition name="fade">
            <div class="loading-overlay" v-if="store.isLoading">
              <div class="loading-spinner"></div>
            </div>
          </Transition>
          <section class="gallery-grid">
            <TransitionGroup name="card">
              <GalleryCard
                v-for="photo in store.photos"
                :key="photo.id"
                :photo="photo"
                @click="store.openLightbox(photo)"
              />
            </TransitionGroup>
          </section>
        </div>

        <!-- Pagination -->
        <GalleryPagination />
      </div>
    </main>
    <Footer />

    <!-- Lightbox -->
    <GalleryLightbox />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import GalleryCard from '@/components/gallery/GalleryCard.vue'
import GalleryFilter from '@/components/gallery/GalleryFilter.vue'
import GalleryPagination from '@/components/gallery/GalleryPagination.vue'
import GalleryLightbox from '@/components/gallery/GalleryLightbox.vue'
import { useGalleryStore } from '@/stores/gallery'

const store = useGalleryStore()

onMounted(() => {
  store.fetchPhotos()
  store.fetchFilterOptions()
})
</script>

<style scoped>
/* Aero background */
.gallery-background {
  background: var(--aero-gradient-sky);
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}

/* Decorative elements */
.aero-decorations {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

/* Clouds */
.cloud {
  position: absolute;
  background: white;
  border-radius: 50%;
  opacity: 0.6;
  filter: blur(1px);
}

.cloud::before,
.cloud::after {
  content: '';
  position: absolute;
  background: white;
  border-radius: 50%;
}

.cloud-1 {
  width: 180px;
  height: 50px;
  top: 8%;
  left: 5%;
  animation: cloud-drift 30s linear infinite;
}
.cloud-1::before {
  width: 70px;
  height: 70px;
  top: -30px;
  left: 30px;
}
.cloud-1::after {
  width: 90px;
  height: 60px;
  top: -20px;
  left: 70px;
}

.cloud-2 {
  width: 140px;
  height: 40px;
  top: 15%;
  right: 10%;
  animation: cloud-drift 25s linear infinite reverse;
}
.cloud-2::before {
  width: 55px;
  height: 55px;
  top: -25px;
  left: 20px;
}
.cloud-2::after {
  width: 70px;
  height: 45px;
  top: -18px;
  left: 55px;
}

.cloud-3 {
  width: 120px;
  height: 35px;
  top: 5%;
  left: 45%;
  opacity: 0.4;
  animation: cloud-drift 35s linear infinite;
}
.cloud-3::before {
  width: 45px;
  height: 45px;
  top: -20px;
  left: 15px;
}
.cloud-3::after {
  width: 60px;
  height: 40px;
  top: -15px;
  left: 45px;
}

@keyframes cloud-drift {
  0% { transform: translateX(0); }
  100% { transform: translateX(80px); }
}

/* Bubbles */
.bubble {
  position: absolute;
  border-radius: 50%;
  background: var(--aero-bubble-bg);
  box-shadow:
    inset -4px -4px 12px rgba(0, 0, 0, 0.05),
    inset 4px 4px 12px rgba(255, 255, 255, 0.8),
    0 2px 6px rgba(0, 0, 0, 0.08);
}

.bubble-1 {
  width: 60px;
  height: 60px;
  bottom: 15%;
  left: 3%;
  animation: bubble-float 8s ease-in-out infinite;
}

.bubble-2 {
  width: 35px;
  height: 35px;
  bottom: 30%;
  right: 5%;
  animation: bubble-float 6s ease-in-out infinite 1s;
}

.bubble-3 {
  width: 25px;
  height: 25px;
  top: 35%;
  left: 8%;
  animation: bubble-float 7s ease-in-out infinite 2s;
}

@keyframes bubble-float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-15px) scale(1.05); }
}

/* Container */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  position: relative;
  z-index: 1;
}

/* Page header */
.gallery-header {
  text-align: center;
  padding: 3rem 0 2rem;
}

.gallery-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--color-text);
  text-shadow: var(--aero-text-shadow);
  margin-bottom: 0.5rem;
}

.gallery-subtitle {
  font-size: 1.1rem;
  color: var(--color-text-secondary);
}

/* Photo grid */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  padding-bottom: 3rem;
}

/* Loading skeleton */
.loading-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  padding-bottom: 3rem;
}

.skeleton-card {
  background: var(--aero-glass-bg-solid);
  border-radius: var(--aero-border-radius);
  overflow: hidden;
  border: 1px solid var(--aero-glass-border);
}

.skeleton-image {
  width: 100%;
  padding-top: 66.67%;
  background: linear-gradient(90deg, #e8f0fe 25%, #d0e3ff 50%, #e8f0fe 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-content {
  padding: 1rem;
}

.skeleton-line {
  height: 12px;
  border-radius: 6px;
  background: linear-gradient(90deg, #e8f0fe 25%, #d0e3ff 50%, #e8f0fe 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  margin-bottom: 0.5rem;
}

.skeleton-title {
  width: 70%;
  height: 16px;
}

.skeleton-text {
  width: 100%;
}

.skeleton-text.short {
  width: 50%;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Empty state */
.gallery-empty {
  text-align: center;
  padding: 4rem 0;
}

.empty-icon {
  color: var(--color-text-secondary);
  opacity: 0.4;
  margin-bottom: 1rem;
}

.empty-text {
  font-size: 1.2rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.5rem;
}

.empty-hint {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  opacity: 0.8;
}

.empty-clear {
  background: none;
  border: none;
  color: var(--color-primary);
  font-family: inherit;
  font-size: inherit;
  cursor: pointer;
  text-decoration: underline;
  padding: 0;
}

.empty-clear:hover {
  color: var(--color-primary-hover);
}

/* Gallery content wrapper */
.gallery-content {
  position: relative;
  min-height: 200px;
}

/* Loading overlay */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: var(--aero-border-radius);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--aero-glass-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.card-enter-active {
  transition: all 0.3s ease;
}

.card-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

/* Responsive */
@media (max-width: 768px) {
  .gallery-title {
    font-size: 2rem;
  }

  .gallery-grid,
  .loading-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 16px;
  }

  .cloud { opacity: 0.3; }
  .bubble { opacity: 0.5; }
}

@media (max-width: 480px) {
  .gallery-grid,
  .loading-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}
</style>
