<template>
  <div class="services-page">
    <Header />

    <main class="services-main">
      <section class="services-hero">
        <div class="hero-copy">
          <p class="eyebrow">Windsong Services</p>
          <h1 class="page-title">服务目录</h1>
        </div>
        <div class="hero-status">
          <span class="status-dot"></span>
          <span class="status-text">{{ services.length }} services online</span>
        </div>
      </section>

      <section class="toolbar">
        <button class="toolbar-chip toolbar-chip--active" type="button">All</button>
        <button class="toolbar-chip" type="button">Finance</button>
        <button class="toolbar-chip" type="button">Backtests</button>
        <button class="toolbar-chip" type="button">Thermal</button>
      </section>

      <section class="service-grid">
        <router-link
          v-for="(service, index) in services"
          :key="service.slug"
          class="service-card"
          :class="`service-card--${service.accent}`"
          :to="service.to"
        >
          <div class="card-header">
            <span class="service-number">0{{ index + 1 }}</span>
            <span class="service-kind">{{ service.kind }}</span>
            <span class="service-state" :class="{ 'service-state--live': service.live }">
              {{ service.live ? 'Live' : 'Soon' }}
            </span>
          </div>

          <h2 class="service-title">{{ service.title }}</h2>
          <p class="service-description">{{ service.description }}</p>

          <div class="topic-row">
            <span v-for="topic in service.topics" :key="topic" class="topic-chip">
              {{ topic }}
            </span>
          </div>

          <div class="meta-grid">
            <div class="meta-item">
              <span class="meta-label">Type</span>
              <strong>{{ service.type }}</strong>
            </div>
            <div class="meta-item">
              <span class="meta-label">Output</span>
              <strong>{{ service.output }}</strong>
            </div>
          </div>

          <div class="service-footer">
            <span class="service-link">Open</span>
            <span class="service-arrow">&rarr;</span>
          </div>
        </router-link>
      </section>

      <section class="service-note">
        <p class="note-title">Index Notes</p>
        <p class="note-text">
          和风与静海，那是老水手的离别。
        </p>
      </section>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import Footer from '@/components/layout/Footer.vue'
import Header from '@/components/layout/Header.vue'

const services = [
  {
    slug: 'family-portfolio',
    to: '/services/family-portfolio',
    kind: 'Finance',
    accent: 'orange',
    title: '家庭投资组合',
    description: '面向家人的组合报告页，展示净值、持仓、投资逻辑与历史曲线。',
    topics: ['Portfolio', 'Family Office', 'Report'],
    type: 'Dashboard',
    output: 'View + Admin',
    live: true
  },
  {
    slug: 'valuation-backtest',
    to: '/services/valuation-backtest',
    kind: 'Finance',
    accent: 'teal',
    title: '老唐估值回测',
    description: '基于利润、国债收益率与历史股本变化，输出价格、内在价值、买点与卖点曲线。',
    topics: ['A-share', 'Valuation', 'ECharts'],
    type: 'Interactive',
    output: 'Chart + JSON',
    live: true
  },
  {
    slug: 'heat-dissipation-calculator',
    to: '/services/heat-dissipation-calculator',
    kind: 'Thermal',
    accent: 'gold',
    title: '流体换热计算',
    description: '基于 CoolProp 焓值差计算换热量，适合实验数据的单组估算与批量处理。',
    topics: ['CoolProp', 'Heat Transfer', 'Batch'],
    type: 'Calculator',
    output: 'W + CSV',
    live: true
  }
]
</script>

<style scoped>
.services-page {
  --surface: #ffffff;
  --surface-secondary: #f9fafb;
  --border: #e5e7eb;
  --text-primary: #111827;
  --text-secondary: #6b7280;
  --text-muted: #9ca3af;
  --accent: #1b9fff;
  --accent-orange: #f97316;
  --accent-teal: #14b8a6;
  --accent-gold: #eab308;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.08);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
  color: var(--text-primary);
  background: var(--surface-secondary);
}

.services-main {
  flex: 1;
  width: min(1280px, calc(100% - 64px));
  margin: 0 auto;
  padding: 3rem 0 5rem;
}

/* ── Hero ── */
.services-hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding: 2.5rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
}

.hero-copy {
  max-width: 640px;
}

.eyebrow {
  margin: 0 0 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: var(--accent);
  text-transform: uppercase;
}

.page-title {
  margin: 0;
  font-size: clamp(2rem, 5vw, 3.25rem);
  font-weight: 700;
  line-height: 1.08;
  color: var(--text-primary);
  letter-spacing: -0.03em;
}

.hero-status {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
  padding: 0.45rem 1rem;
  background: var(--surface-secondary);
  border: 1px solid var(--border);
  border-radius: 999px;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2);
}

/* ── Toolbar ── */
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.toolbar-chip {
  padding: 0.4rem 1rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface);
  color: var(--text-secondary);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: default;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.toolbar-chip:hover {
  background: var(--surface-secondary);
  border-color: #d1d5db;
}

.toolbar-chip--active {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}

/* ── Grid ── */
.service-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.25rem;
}

/* ── Card ── */
.service-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0 1.25rem 1.25rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  border-top: 3px solid var(--border);
  box-shadow: var(--shadow-sm);
  transition:
    box-shadow 0.2s ease,
    transform 0.2s ease,
    border-color 0.2s ease;
}

.service-card--orange { border-top-color: var(--accent-orange); }
.service-card--teal   { border-top-color: var(--accent-teal); }
.service-card--gold   { border-top-color: var(--accent-gold); }

.service-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
  border-color: #d1d5db;
}

.service-card--orange:hover { border-top-color: var(--accent-orange); }
.service-card--teal:hover   { border-top-color: var(--accent-teal); }
.service-card--gold:hover   { border-top-color: var(--accent-gold); }

/* ── Card header ── */
.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-top: 0.85rem;
}

.service-number {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  padding: 0.15rem 0.55rem;
  background: var(--surface-secondary);
  border-radius: 999px;
}

.service-kind {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.service-state {
  margin-left: auto;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-muted);
  padding: 0.2rem 0.55rem;
  background: var(--surface-secondary);
  border-radius: 999px;
}

.service-state--live {
  color: #15803d;
  background: #f0fdf4;
}

/* ── Card body ── */
.service-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--text-primary);
}

.service-description {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.55;
  color: var(--text-secondary);
}

/* ── Topics ── */
.topic-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.topic-chip {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-secondary);
  padding: 0.2rem 0.55rem;
  background: var(--surface-secondary);
  border-radius: 4px;
}

/* ── Meta ── */
.meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  margin-top: auto;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  padding: 0.5rem 0.75rem;
  background: var(--surface-secondary);
  border-radius: 6px;
}

.meta-label {
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.meta-item strong {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-primary);
}

/* ── Card footer ── */
.service-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.service-link {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--accent);
}

.service-arrow {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  font-size: 0.8rem;
  transition: transform 0.2s ease;
}

.service-card:hover .service-arrow {
  transform: translateX(3px);
}

/* ── Note ── */
.service-note {
  margin-top: 2rem;
  padding: 1rem 1.25rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
}

.note-title {
  margin: 0;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.note-text {
  margin: 0.2rem 0 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* ── Responsive ── */
@media (max-width: 720px) {
  .services-main {
    width: min(100% - 24px, 1280px);
    padding: 1.5rem 0 3rem;
  }

  .services-hero {
    flex-direction: column;
    align-items: stretch;
    padding: 1.5rem;
  }

  .service-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .meta-grid {
    grid-template-columns: 1fr;
  }
}
</style>
