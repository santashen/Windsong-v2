<template>
  <div class="blog-page">
    <Header />

    <main class="blog-main">
      <!-- Decorative pixel elements -->
      <div class="pixel-decoration pixel-star star-1">✦</div>
      <div class="pixel-decoration pixel-star star-2">✦</div>
      <div class="pixel-decoration pixel-star star-3">★</div>

      <div class="blog-container">
        <!-- Page Title -->
        <div class="page-header">
          <h1 class="page-title">📜 博客文章</h1>
          <p class="page-subtitle">记录技术探索与生活点滴</p>
        </div>

        <!-- Filter -->
        <BlogFilter v-if="store.allTags.length > 0" />

        <!-- Loading State -->
        <div v-if="store.isLoading" class="blog-grid">
          <div class="skeleton-card" v-for="i in 6" :key="i">
            <div class="skeleton-title"></div>
            <div class="skeleton-divider"></div>
            <div class="skeleton-meta"></div>
            <div class="skeleton-tags"></div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else-if="store.posts.length === 0" class="empty-state">
          <div class="empty-icon">📭</div>
          <p class="empty-text">暂无文章</p>
          <button v-if="store.hasActiveFilter" class="clear-filter-btn" @click="store.clearFilter()">
            清除筛选
          </button>
        </div>

        <!-- Posts Grid -->
        <TransitionGroup v-else name="card" tag="div" class="blog-grid">
          <BlogCard
            v-for="post in store.posts"
            :key="post.id"
            :post="post"
            @click="goToPost(post)"
            @tag-click="handleTagClick"
          />
        </TransitionGroup>

        <!-- Pagination -->
        <BlogPagination />
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import BlogCard from '@/components/blog/BlogCard.vue'
import BlogFilter from '@/components/blog/BlogFilter.vue'
import BlogPagination from '@/components/blog/BlogPagination.vue'
import { useBlogStore } from '@/stores/blog'

const store = useBlogStore()
const router = useRouter()

onMounted(() => {
  store.fetchPosts()
  store.fetchTags()
})

function goToPost(post) {
  router.push(`/posts/${post.slug}`)
}

function handleTagClick(tag) {
  store.setTagFilter(tag)
}
</script>

<style scoped>
.blog-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 50%, #f1f5f9 100%);
}

.blog-main {
  flex: 1;
  position: relative;
  padding: 2rem 1rem 4rem;
  overflow: hidden;
}

/* Decorative stars */
.pixel-decoration {
  position: absolute;
  font-size: 1.5rem;
  color: #94a3b8;
  opacity: 0.5;
  animation: twinkle 2s ease-in-out infinite;
  pointer-events: none;
  user-select: none;
}

.star-1 {
  top: 10%;
  left: 5%;
  animation-delay: 0s;
}

.star-2 {
  top: 20%;
  right: 8%;
  animation-delay: 0.7s;
}

.star-3 {
  top: 40%;
  left: 3%;
  animation-delay: 1.4s;
  font-size: 2rem;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.1); }
}

.blog-container {
  max-width: 1100px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

/* Page Header */
.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #334155;
  text-shadow: 2px 2px 0 rgba(255, 255, 255, 0.8);
  margin: 0 0 0.5rem 0;
}

.page-subtitle {
  font-size: 1rem;
  color: #64748b;
  margin: 0;
}

/* Blog Grid */
.blog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

/* Skeleton */
.skeleton-card {
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border: 4px solid #cbd5e1;
  padding: 1rem 1.25rem;
  box-shadow: 0 4px 0 #94a3b8;
}

.skeleton-title {
  height: 1.5rem;
  width: 70%;
  background: linear-gradient(90deg, #e5e7eb 25%, #d1d5db 50%, #e5e7eb 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  margin-bottom: 0.75rem;
}

.skeleton-divider {
  height: 4px;
  background: #cbd5e1;
  margin: 0.75rem 0;
}

.skeleton-meta {
  height: 1rem;
  width: 40%;
  background: linear-gradient(90deg, #e5e7eb 25%, #d1d5db 50%, #e5e7eb 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  margin-bottom: 0.75rem;
}

.skeleton-tags {
  height: 1.5rem;
  width: 60%;
  background: linear-gradient(90deg, #e5e7eb 25%, #d1d5db 50%, #e5e7eb 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-text {
  font-size: 1.25rem;
  color: #64748b;
  margin-bottom: 1.5rem;
}

.clear-filter-btn {
  padding: 0.5rem 1.25rem;
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

.clear-filter-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 0 #475569;
}

/* Transition animations */
.card-enter-active {
  transition: all 0.3s ease;
}

.card-leave-active {
  transition: all 0.2s ease;
}

.card-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.card-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

.card-move {
  transition: transform 0.3s ease;
}

/* Responsive */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .blog-grid {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }
}
</style>
