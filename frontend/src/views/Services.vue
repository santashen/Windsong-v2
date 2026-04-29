<template>
  <div class="services-page">
    <Header />

    <main class="services-main">
      <section class="services-hero">
        <div class="atomic-mark" aria-hidden="true">
          <span></span>
          <span></span>
        </div>

        <div class="hero-copy">
          <p class="eyebrow">Windsong Services</p>
          <h1 class="page-title">服务目录</h1>
        </div>

        <div class="hero-status">
          <div class="status-orb"></div>
          <div>
            <p class="status-label">Directory status</p>
            <p class="status-value">{{ services.length }} services online</p>
          </div>
        </div>

        <div class="pixel-strip" aria-hidden="true">
          <span v-for="n in 16" :key="n"></span>
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
          :to="service.to"
        >
          <div class="card-topline" :class="`card-topline--${service.accent}`">
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
            <span class="service-arrow">↗</span>
          </div>
        </router-link>
      </section>

      <section class="service-note">
        <p class="note-title">Index Notes</p>
        <p class="note-text">
          和风与静海,那是老水手的离别。
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
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;700&family=Epilogue:wght@700;800&family=Space+Grotesk:wght@600;700&display=swap');

.services-page {
  --atomic-paper: #f7f3e3;
  --atomic-surface: #fbf9f8;
  --atomic-surface-low: #f5f3f3;
  --atomic-surface-high: #e4e2e2;
  --atomic-ink: #4b4b4b;
  --atomic-text: #1b1c1c;
  --atomic-muted: #59413a;
  --atomic-orange: #ff6f3c;
  --atomic-orange-deep: #ac3500;
  --atomic-teal: #00a6a6;
  --atomic-teal-deep: #006a6a;
  --atomic-gold: #ffd64f;
  --atomic-shadow: rgba(75, 75, 75, 0.34);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: 'Be Vietnam Pro', system-ui, sans-serif;
  color: var(--atomic-text);
  background:
    radial-gradient(circle at 14% 16%, rgba(255, 111, 60, 0.16) 0 9%, transparent 9.4%),
    radial-gradient(circle at 86% 20%, rgba(0, 166, 166, 0.16) 0 8%, transparent 8.4%),
    linear-gradient(135deg, rgba(75, 75, 75, 0.05) 25%, transparent 25%) 0 0 / 18px 18px,
    linear-gradient(180deg, var(--atomic-paper), #fbf9f8 48%, #f3ebdc);
  position: relative;
  overflow: hidden;
}

.services-page::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  opacity: 0.5;
  background-image:
    linear-gradient(rgba(75, 75, 75, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(75, 75, 75, 0.08) 1px, transparent 1px);
  background-size: 24px 24px;
  mask-image: linear-gradient(180deg, rgba(255, 255, 255, 0.9), transparent 88%);
}

.services-page::after {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  opacity: 0.18;
  background:
    radial-gradient(circle at 18% 24%, var(--atomic-ink) 0 1px, transparent 1.5px),
    radial-gradient(circle at 72% 34%, var(--atomic-ink) 0 1px, transparent 1.5px),
    radial-gradient(circle at 52% 74%, var(--atomic-ink) 0 1px, transparent 1.5px);
  background-size: 150px 150px;
}

.services-main {
  position: relative;
  z-index: 1;
  flex: 1;
  width: min(1280px, calc(100% - 64px));
  margin: 0 auto;
  padding: 3rem 0 5rem;
}

.services-hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 2rem;
  align-items: end;
  margin-bottom: 1.5rem;
  padding: 2rem;
  border: 2px solid var(--atomic-ink);
  border-radius: 0.25rem;
  background:
    linear-gradient(90deg, rgba(255, 214, 79, 0.24), transparent 54%),
    var(--atomic-surface);
  box-shadow: 6px 6px 0 var(--atomic-shadow);
  overflow: hidden;
}

.atomic-mark {
  position: absolute;
  top: 1.25rem;
  right: 1.5rem;
  width: 112px;
  height: 112px;
  pointer-events: none;
}

.atomic-mark::before,
.atomic-mark::after,
.atomic-mark span {
  content: '';
  position: absolute;
  border: 2px solid var(--atomic-ink);
}

.atomic-mark::before {
  inset: 25px;
  border-radius: 999px;
  background: var(--atomic-gold);
}

.atomic-mark::after {
  left: 8px;
  top: 52px;
  width: 96px;
  height: 14px;
  border-radius: 999px;
  background: var(--atomic-teal);
  transform: rotate(-28deg);
}

.atomic-mark span:first-child {
  left: 48px;
  top: 4px;
  width: 15px;
  height: 104px;
  border-radius: 999px;
  background: var(--atomic-orange);
  transform: rotate(28deg);
}

.atomic-mark span:last-child {
  inset: 40px;
  border-radius: 999px;
  background: var(--atomic-surface);
}

.hero-copy {
  max-width: 760px;
  position: relative;
  z-index: 1;
}

.eyebrow {
  margin: 0 0 0.65rem;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.875rem;
  font-weight: 700;
  letter-spacing: 0;
  color: var(--atomic-orange-deep);
  text-transform: uppercase;
}

.page-title {
  margin: 0;
  font-family: 'Epilogue', sans-serif;
  font-size: clamp(2.5rem, 6vw, 4.75rem);
  font-weight: 800;
  line-height: 1.02;
  letter-spacing: 0;
  color: var(--atomic-text);
  text-transform: uppercase;
}

.page-subtitle {
  margin: 0.95rem 0 0;
  max-width: 42ch;
  font-size: 1.125rem;
  line-height: 1.6;
  color: var(--atomic-muted);
}

.hero-status {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  gap: 0.85rem;
  min-width: 245px;
  padding: 0.85rem 1rem;
  border: 2px solid var(--atomic-ink);
  border-radius: 0.25rem;
  background: var(--atomic-teal);
  color: #fff;
  box-shadow: 4px 4px 0 var(--atomic-ink);
}

.status-orb {
  width: 18px;
  height: 18px;
  border: 2px solid var(--atomic-ink);
  border-radius: 999px;
  background: var(--atomic-gold);
  box-shadow: 2px 2px 0 rgba(75, 75, 75, 0.45);
}

.status-label {
  margin: 0;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0;
  color: rgba(255, 255, 255, 0.86);
  text-transform: uppercase;
}

.status-value {
  margin: 0.1rem 0 0;
  color: #fff;
  font-weight: 700;
}

.pixel-strip {
  display: grid;
  grid-column: 1 / -1;
  grid-template-columns: repeat(16, minmax(10px, 1fr));
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.pixel-strip span {
  height: 8px;
  border: 1px solid var(--atomic-ink);
  border-radius: 999px;
  background: var(--atomic-orange);
}

.pixel-strip span:nth-child(3n) {
  background: var(--atomic-teal);
}

.pixel-strip span:nth-child(4n) {
  background: var(--atomic-gold);
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin: 1.75rem 0 1.5rem;
}

.toolbar-chip {
  min-height: 38px;
  padding: 0 1rem;
  border: 2px solid var(--atomic-ink);
  border-radius: 999px;
  background: var(--atomic-surface);
  color: var(--atomic-muted);
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.875rem;
  font-weight: 700;
  text-transform: uppercase;
  cursor: default;
  box-shadow: 3px 3px 0 rgba(75, 75, 75, 0.22);
}

.toolbar-chip--active {
  background: var(--atomic-orange);
  color: #fff;
  box-shadow: 3px 3px 0 var(--atomic-ink);
}

.service-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.5rem;
}

.service-card {
  position: relative;
  display: grid;
  grid-template-rows: auto auto auto auto auto 1fr;
  gap: 1rem;
  min-height: 360px;
  padding: 0 1.25rem 1.25rem;
  border-radius: 0.25rem;
  background: var(--atomic-surface);
  border: 2px solid var(--atomic-ink);
  box-shadow: 6px 6px 0 var(--atomic-shadow);
  overflow: hidden;
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease;
}

.service-card::before {
  content: '✦';
  position: absolute;
  right: 1rem;
  bottom: 0.8rem;
  font-family: 'Epilogue', sans-serif;
  font-size: 3.25rem;
  line-height: 1;
  color: rgba(255, 214, 79, 0.55);
  -webkit-text-stroke: 1px var(--atomic-ink);
  pointer-events: none;
}

.service-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: 9px 9px 0 var(--atomic-ink);
}

.service-card:active {
  transform: translate(3px, 3px);
  box-shadow: 2px 2px 0 var(--atomic-ink);
}

.card-topline,
.service-title,
.service-description,
.topic-row,
.meta-grid,
.service-footer {
  position: relative;
  z-index: 1;
}

.card-topline {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin: 0 -1.25rem;
  padding: 0.85rem 1rem;
  border-bottom: 2px solid var(--atomic-ink);
  color: #fff;
}

.card-topline--orange {
  background: var(--atomic-orange);
}

.card-topline--teal {
  background: var(--atomic-teal);
}

.card-topline--gold {
  background: var(--atomic-gold);
  color: var(--atomic-text);
}

.service-number {
  display: inline-grid;
  place-items: center;
  width: 34px;
  height: 34px;
  flex: 0 0 auto;
  border: 2px solid var(--atomic-ink);
  border-radius: 999px;
  background: var(--atomic-surface);
  color: var(--atomic-text);
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.8rem;
  font-weight: 700;
}

.service-kind {
  min-width: 0;
  flex: 1;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0;
  text-transform: uppercase;
}

.service-state {
  display: inline-flex;
  align-items: center;
  flex: 0 0 auto;
  min-height: 27px;
  padding: 0 0.65rem;
  border: 1px solid var(--atomic-ink);
  border-radius: 999px;
  background: var(--atomic-surface);
  color: var(--atomic-muted);
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
}

.service-state--live {
  background: var(--atomic-gold);
  color: var(--atomic-text);
}

.service-title {
  margin: 0;
  font-family: 'Epilogue', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.2;
  color: var(--atomic-text);
}

.service-description {
  margin: 0;
  color: var(--atomic-muted);
  line-height: 1.55;
  font-size: 0.95rem;
}

.topic-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.topic-chip {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0 0.6rem;
  border: 1px solid var(--atomic-ink);
  border-radius: 999px;
  background: var(--atomic-surface-low);
  color: var(--atomic-muted);
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.74rem;
  font-weight: 700;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
  margin-top: auto;
}

.meta-item {
  display: grid;
  gap: 0.15rem;
  padding: 0.65rem;
  border-radius: 0.25rem;
  background: #fff;
  border: 2px solid var(--atomic-ink);
}

.meta-label {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--atomic-orange-deep);
  letter-spacing: 0;
  text-transform: uppercase;
}

.meta-item strong {
  color: var(--atomic-text);
  font-size: 0.88rem;
  line-height: 1.25;
}

.service-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  align-self: end;
  margin-top: 0.2rem;
  color: var(--atomic-text);
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.9rem;
  font-weight: 700;
  text-transform: uppercase;
}

.service-arrow {
  display: inline-grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border: 2px solid var(--atomic-ink);
  border-radius: 999px;
  background: var(--atomic-orange);
  color: #fff;
  transition: transform 0.2s ease;
}

.service-card:hover .service-arrow {
  transform: translate(2px, -2px);
}

.service-note {
  position: relative;
  margin-top: 2rem;
  padding: 1.25rem 1.5rem;
  border: 2px solid var(--atomic-ink);
  border-radius: 0.25rem;
  background: var(--atomic-gold);
  box-shadow: 5px 5px 0 var(--atomic-shadow);
}

.note-title {
  margin: 0;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--atomic-text);
  text-transform: uppercase;
}

.note-text {
  margin: 0.3rem 0 0;
  color: var(--atomic-muted);
}

@media (max-width: 720px) {
  .services-main {
    width: min(100% - 24px, 1280px);
    padding: 1.5rem 0 3rem;
  }

  .services-hero {
    grid-template-columns: 1fr;
    padding: 1.25rem;
  }

  .atomic-mark {
    opacity: 0.35;
    right: -0.5rem;
  }

  .page-title {
    font-size: clamp(2.2rem, 12vw, 3.25rem);
  }

  .service-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

@media (max-width: 560px) {
  .hero-status {
    width: 100%;
  }

  .pixel-strip {
    grid-template-columns: repeat(8, 1fr);
  }

  .meta-grid {
    grid-template-columns: 1fr;
  }
}
</style>
