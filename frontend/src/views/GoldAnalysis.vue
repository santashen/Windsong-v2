<template>
  <div class="gold-page">
    <Header />

    <main class="gold-main">
      <div class="gold-container">
        <!-- Breadcrumb -->
        <div class="breadcrumb">
          <router-link to="/services">Services</router-link>
          <span class="separator">/</span>
          <span class="current">Gold Analysis</span>
        </div>

        <!-- Page Title -->
        <div class="page-header">
          <h1 class="page-title">💰 Gold Analysis</h1>
          <p class="page-subtitle">Daily gold market analysis powered by AI</p>
        </div>

        <!-- Loading State -->
        <div v-if="store.isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p class="loading-text">Analyzing market data...</p>
          <p class="loading-hint">This may take up to a minute ⏳</p>
        </div>

        <!-- Error State -->
        <div v-else-if="store.error" class="error-state">
          <div class="error-icon">❌</div>
          <p class="error-text">{{ store.error }}</p>
          <button class="retry-btn" @click="store.fetchTodayAnalysis()">
            🔄 Retry
          </button>
        </div>

        <!-- Analysis Content -->
        <div v-else-if="store.hasAnalysis" class="analysis-card">
          <div class="card-header">
            <span class="card-date">📅 {{ store.analysisDate }}</span>
            <span class="card-model">🤖 {{ store.analysis.modelUsed }}</span>
          </div>

          <div class="card-divider"></div>

          <div class="analysis-content" v-html="renderedContent"></div>

          <div class="card-footer">
            <span class="footer-note">⚠️ Analysis is for reference only, not investment advice</span>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="empty-state">
          <div class="empty-icon">📭</div>
          <p class="empty-text">No analysis available</p>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { marked } from 'marked'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import { useGoldStore } from '@/stores/gold'

const store = useGoldStore()

marked.setOptions({
  breaks: true,
  gfm: true
})

const renderedContent = computed(() => {
  if (!store.analysis?.content) return ''
  return marked(store.analysis.content)
})

onMounted(() => {
  store.fetchTodayAnalysis()
})
</script>

<style scoped>
.gold-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
}

.gold-main {
  flex: 1;
  padding: 2rem 1rem 4rem;
}

.gold-container {
  max-width: 900px;
  margin: 0 auto;
}

/* Breadcrumb */
.breadcrumb {
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.breadcrumb a {
  color: var(--color-primary);
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

.breadcrumb .separator {
  margin: 0 0.5rem;
  color: var(--color-text-secondary);
}

.breadcrumb .current {
  color: var(--color-text);
}

/* Page Header */
.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 0.5rem 0;
}

.page-subtitle {
  font-size: 1rem;
  color: var(--color-text-secondary);
  margin: 0;
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 4rem 2rem;
  background: var(--color-bg-secondary);
  border-radius: 12px;
  border: 1px solid var(--color-border);
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: var(--color-text);
  font-size: 1.1rem;
  margin: 0 0 0.5rem 0;
}

.loading-hint {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  margin: 0;
}

/* Error State */
.error-state {
  text-align: center;
  padding: 4rem 2rem;
  background: var(--color-bg-secondary);
  border-radius: 12px;
  border: 1px solid var(--color-border);
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-text {
  color: #ef4444;
  margin-bottom: 1.5rem;
}

.retry-btn {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  background: var(--color-primary);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #2563eb;
}

/* Analysis Card */
.analysis-card {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 2rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-date {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text);
}

.card-model {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  padding: 0.25rem 0.75rem;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 20px;
}

.card-divider {
  height: 1px;
  margin: 1rem 0 1.5rem;
  background: var(--color-border);
}

/* Analysis Content */
.analysis-content {
  color: var(--color-text);
  line-height: 1.8;
  font-size: 1rem;
}

.analysis-content :deep(h1),
.analysis-content :deep(h2),
.analysis-content :deep(h3) {
  color: var(--color-text);
  font-weight: 700;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.analysis-content :deep(h2) {
  font-size: 1.4rem;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 0.5rem;
}

.analysis-content :deep(h3) {
  font-size: 1.2rem;
}

.analysis-content :deep(strong) {
  color: var(--color-primary);
}

.analysis-content :deep(ul),
.analysis-content :deep(ol) {
  margin: 1rem 0;
  padding-left: 1.5rem;
}

.analysis-content :deep(li) {
  margin-bottom: 0.5rem;
}

.analysis-content :deep(blockquote) {
  border-left: 4px solid var(--color-primary);
  background: var(--color-bg-secondary);
  margin: 1rem 0;
  padding: 1rem;
  color: var(--color-text-secondary);
  border-radius: 0 8px 8px 0;
}

.analysis-content :deep(code) {
  background: var(--color-bg-secondary);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  color: var(--color-primary);
  font-size: 0.9em;
}

.analysis-content :deep(pre) {
  background: var(--color-bg-secondary);
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
}

.analysis-content :deep(pre code) {
  background: none;
  padding: 0;
}

/* Card Footer */
.card-footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px dashed var(--color-border);
}

.footer-note {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: var(--color-bg-secondary);
  border-radius: 12px;
  border: 1px solid var(--color-border);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-text {
  color: var(--color-text-secondary);
  margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .analysis-card {
    padding: 1.5rem;
  }

  .card-header {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
}
</style>
