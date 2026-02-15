<template>
  <div class="services-page">
    <Header />

    <main class="services-main">
      <div class="services-container">
        <!-- Page Title -->
        <div class="page-header">
          <h1 class="page-title">Services</h1>
          <p class="page-subtitle">AI-powered tools and analysis</p>
        </div>

        <!-- Services Grid -->
        <div class="services-grid">
          <!-- Gold Analysis Card -->
          <router-link to="/gold" class="service-card">
            <div class="card-icon">💰</div>
            <h2 class="card-title">Gold Analysis</h2>
            <p class="card-description">
              Daily gold market analysis powered by AI. Get insights on price trends,
              technical indicators, and trading suggestions.
            </p>
            <div class="card-footer">
              <span class="card-tag">📊 Market Analysis</span>
              <span class="card-arrow">→</span>
            </div>
          </router-link>

          <!-- Real-time Monitor Card -->
          <router-link to="/monitor" class="service-card">
            <div class="card-icon">📡</div>
            <h2 class="card-title">Real-time Monitor</h2>
            <p class="card-description">
              Configure and simulate real-time data monitoring dashboards
              with customizable charts and mock data streams.
            </p>
            <div class="card-footer">
              <span class="card-tag">📈 Simulation</span>
              <span class="card-arrow">→</span>
            </div>
          </router-link>
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

/* Services Grid */
.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

/* Service Card */
.service-card {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
}

.service-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.card-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 0.75rem 0;
}

.card-description {
  font-size: 0.95rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0 0 1rem 0;
  flex: 1;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.card-tag {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  background: var(--color-bg-secondary);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.card-arrow {
  font-size: 1.2rem;
  color: var(--color-primary);
  transition: transform 0.2s;
}

.service-card:hover .card-arrow {
  transform: translateX(4px);
}

/* Responsive */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .services-grid {
    grid-template-columns: 1fr;
  }
}
</style>
