<template>
  <div class="monitor-page">
    <Header />

    <main class="monitor-main">
      <div class="monitor-container">
        <!-- Breadcrumb -->
        <div class="breadcrumb">
          <router-link to="/services">Services</router-link>
          <span class="separator">/</span>
          <span class="current">Monitor</span>
        </div>

        <!-- Page Header -->
        <div class="page-header">
          <h1 class="page-title">Real-time Monitor</h1>
          <p class="page-subtitle">Configure and simulate real-time data streams</p>
        </div>

        <!-- Configuration Phase -->
        <div v-if="!store.isRunning" class="config-phase">
          <div v-if="store.chartConfigs.length" class="config-list">
            <ChartConfigForm
              v-for="config in store.chartConfigs"
              :key="config.id"
              :config="config"
              @remove="store.removeConfig(config.id)"
              @update="(updates) => store.updateConfig(config.id, updates)"
            />
          </div>

          <div v-else class="empty-state">
            <p class="empty-text">No charts configured yet. Add a chart to get started.</p>
          </div>

          <div class="config-actions">
            <button class="btn btn-secondary" @click="store.addConfig">
              + Add Chart
            </button>
            <button
              class="btn btn-primary"
              :disabled="!store.hasConfigs"
              @click="store.startMonitoring"
            >
              Start Monitoring
            </button>
          </div>
        </div>

        <!-- Running Phase -->
        <div v-else class="running-phase">
          <div class="running-header">
            <span class="running-indicator">Live</span>
            <button class="btn btn-danger" @click="store.stopMonitoring">
              Stop
            </button>
          </div>

          <div class="charts-grid">
            <RealtimeChart
              v-for="config in store.chartConfigs"
              :key="config.id"
              :config="config"
            />
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import ChartConfigForm from '@/components/monitor/ChartConfigForm.vue'
import RealtimeChart from '@/components/monitor/RealtimeChart.vue'
import { useMonitorStore } from '@/stores/monitor'

const store = useMonitorStore()
</script>

<style scoped>
.monitor-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
}

.monitor-main {
  flex: 1;
  padding: 2rem 1rem 4rem;
}

.monitor-container {
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

/* Configuration Phase */
.config-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem 2rem;
  background: var(--color-bg-secondary);
  border-radius: 12px;
  border: 1px solid var(--color-border);
  margin-bottom: 1.5rem;
}

.empty-text {
  color: var(--color-text-secondary);
  margin: 0;
}

.config-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

/* Buttons */
.btn {
  padding: 0.6rem 1.25rem;
  font-size: 0.95rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  color: var(--color-text);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.btn-primary {
  color: #fff;
  background: var(--color-primary);
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-danger {
  color: #fff;
  background: #ef4444;
}

.btn-danger:hover {
  background: #dc2626;
}

/* Running Phase */
.running-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.running-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #10b981;
  font-weight: 600;
  font-size: 1rem;
}

.running-indicator::before {
  content: '';
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .config-actions {
    flex-direction: column;
  }
}
</style>
