<template>
  <div class="services-page">
    <Header />

    <main class="services-main">
      <div class="services-container">
        <div class="page-header">
          <h1 class="page-title">Services</h1>
          <p class="page-subtitle">This section is being rebuilt.</p>
        </div>

        <div class="empty-state">
          <p class="empty-title">No services are currently online.</p>
          <p class="empty-description">
            The previous tools have been retired. New service entries will appear here when they are ready.
          </p>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
</script>

<style scoped>
.services-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
}

.services-main {
  flex: 1;
  padding: 2rem 1rem 4rem;
}

.services-container {
  max-width: 900px;
  margin: 0 auto;
}

/* Page Header */
.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 0.5rem 0;
}

.page-subtitle {
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.empty-state {
  padding: 3rem 2rem;
  text-align: center;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 12px;
}

.empty-title {
  margin: 0 0 0.75rem 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--color-text);
}

.empty-description {
  margin: 0;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

/* Responsive */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }
}
</style>
