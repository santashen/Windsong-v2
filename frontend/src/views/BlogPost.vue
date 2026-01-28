<template>
  <div class="post-page">
    <Header />

    <main class="post-main">
      <!-- Back button -->
      <div class="post-container">
        <button class="back-btn" @click="goBack">
          ◀ 返回列表
        </button>

        <!-- Loading State -->
        <div v-if="store.isLoadingPost" class="post-loading">
          <div class="loading-spinner">⏳</div>
          <p>加载中...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="store.error" class="post-error">
          <div class="error-icon">😕</div>
          <p>{{ store.error }}</p>
          <button class="back-btn" @click="goBack">返回列表</button>
        </div>

        <!-- Post Content -->
        <article v-else-if="store.currentPost" class="post-article">
          <!-- Post Header -->
          <header class="post-header">
            <h1 class="post-title">{{ store.currentPost.title }}</h1>
            <div class="post-meta">
              <span class="post-date">
                📅 {{ formatDate(store.currentPost.date) }}
              </span>
              <div class="post-tags" v-if="store.currentPost.tags?.length > 0">
                <span
                  class="pixel-tag"
                  v-for="tag in store.currentPost.tags"
                  :key="tag"
                >
                  #{{ tag }}
                </span>
              </div>
            </div>
          </header>

          <!-- Pixel Divider -->
          <div class="pixel-divider-large"></div>

          <!-- Post Content -->
          <div class="post-content markdown-body" v-html="renderedContent"></div>
        </article>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import { useBlogStore } from '@/stores/blog'

const store = useBlogStore()
const route = useRoute()
const router = useRouter()

// Configure marked
marked.setOptions({
  breaks: true,
  gfm: true
})

const renderedContent = computed(() => {
  if (!store.currentPost?.content) return ''
  return marked(store.currentPost.content)
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

function goBack() {
  router.push('/posts')
}

function fetchPost() {
  const slug = route.params.slug
  if (slug) {
    store.fetchPost(slug)
  }
}

onMounted(() => {
  fetchPost()
})

onUnmounted(() => {
  store.clearCurrentPost()
})

// Watch for route changes (if navigating between posts)
watch(() => route.params.slug, (newSlug) => {
  if (newSlug) {
    store.fetchPost(newSlug)
  }
})
</script>

<style scoped>
.post-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 50%, #f1f5f9 100%);
}

.post-main {
  flex: 1;
  padding: 2rem 1rem 4rem;
}

.post-container {
  max-width: 800px;
  margin: 0 auto;
}

/* Back button */
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  font-family: inherit;
  font-weight: 600;
  color: #334155;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border: 3px solid #64748b;
  box-shadow: 0 3px 0 #475569;
  cursor: pointer;
  transition: all 0.1s ease;
  margin-bottom: 1.5rem;
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 0 #475569;
}

.back-btn:active {
  transform: translateY(1px);
  box-shadow: 0 1px 0 #475569;
}

/* Loading */
.post-loading {
  text-align: center;
  padding: 4rem 2rem;
  color: #64748b;
}

.loading-spinner {
  font-size: 3rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Error */
.post-error {
  text-align: center;
  padding: 4rem 2rem;
  color: #64748b;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

/* Article */
.post-article {
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border: 4px solid #64748b;
  box-shadow: 0 6px 0 #475569;
  padding: 2rem;
}

/* Header */
.post-header {
  margin-bottom: 1rem;
}

.post-title {
  font-size: 2rem;
  font-weight: 700;
  color: #334155;
  text-shadow: 2px 2px 0 rgba(255, 255, 255, 0.8);
  margin: 0 0 1rem 0;
  line-height: 1.3;
}

.post-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
}

.post-date {
  font-size: 0.95rem;
  color: #64748b;
  font-weight: 500;
}

.post-tags {
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
}

/* Pixel divider */
.pixel-divider-large {
  height: 6px;
  margin: 1.5rem 0 2rem;
  background: repeating-linear-gradient(
    90deg,
    #94a3b8 0px,
    #94a3b8 6px,
    transparent 6px,
    transparent 12px
  );
}

/* Markdown content styling */
.post-content {
  color: #334155;
  line-height: 1.8;
  font-size: 1.05rem;
}

.post-content :deep(h1),
.post-content :deep(h2),
.post-content :deep(h3),
.post-content :deep(h4),
.post-content :deep(h5),
.post-content :deep(h6) {
  color: #1e293b;
  font-weight: 700;
  margin-top: 2rem;
  margin-bottom: 1rem;
  text-shadow: 1px 1px 0 rgba(255, 255, 255, 0.5);
}

.post-content :deep(h1) { font-size: 1.75rem; }
.post-content :deep(h2) { font-size: 1.5rem; }
.post-content :deep(h3) { font-size: 1.25rem; }

.post-content :deep(p) {
  margin-bottom: 1.25rem;
}

.post-content :deep(a) {
  color: #3b82f6;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.post-content :deep(a:hover) {
  color: #2563eb;
}

.post-content :deep(strong) {
  color: #1e293b;
  font-weight: 700;
}

.post-content :deep(code) {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  padding: 0.15rem 0.4rem;
  font-size: 0.9em;
  font-family: 'Consolas', 'Monaco', monospace;
}

.post-content :deep(pre) {
  background: #1e293b;
  color: #e2e8f0;
  border: 3px solid #475569;
  box-shadow: 0 4px 0 #334155;
  padding: 1.25rem;
  overflow-x: auto;
  margin: 1.5rem 0;
}

.post-content :deep(pre code) {
  background: transparent;
  border: none;
  padding: 0;
  color: inherit;
}

.post-content :deep(blockquote) {
  border-left: 4px solid #3b82f6;
  background: #f1f5f9;
  margin: 1.5rem 0;
  padding: 1rem 1.25rem;
  color: #475569;
  font-style: italic;
}

.post-content :deep(ul),
.post-content :deep(ol) {
  margin: 1rem 0;
  padding-left: 1.5rem;
}

.post-content :deep(li) {
  margin-bottom: 0.5rem;
}

.post-content :deep(hr) {
  border: none;
  height: 4px;
  margin: 2rem 0;
  background: repeating-linear-gradient(
    90deg,
    #94a3b8 0px,
    #94a3b8 4px,
    transparent 4px,
    transparent 8px
  );
}

.post-content :deep(img) {
  max-width: 100%;
  height: auto;
  border: 3px solid #64748b;
  box-shadow: 0 4px 0 #475569;
  margin: 1.5rem 0;
}

.post-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
  border: 2px solid #64748b;
}

.post-content :deep(th),
.post-content :deep(td) {
  border: 1px solid #94a3b8;
  padding: 0.75rem;
  text-align: left;
}

.post-content :deep(th) {
  background: #f1f5f9;
  font-weight: 600;
  color: #334155;
}

.post-content :deep(tr:nth-child(even)) {
  background: #f8fafc;
}

/* Responsive */
@media (max-width: 768px) {
  .post-article {
    padding: 1.5rem;
  }

  .post-title {
    font-size: 1.5rem;
  }

  .post-content {
    font-size: 1rem;
  }
}
</style>
