<template>
  <div class="services-page">
    <Header />

    <main class="services-main">
      <section class="services-hero">
        <div class="hero-copy">
          <p class="eyebrow">Windsong Services</p>
          <h1 class="page-title">服务目录</h1>
          <p class="page-subtitle">
            这里是独立工具页的入口。先浏览，再进入具体工作台。
          </p>
        </div>

        <div class="hero-status">
          <div class="status-orb"></div>
          <div>
            <p class="status-label">Directory status</p>
            <p class="status-value">1 service online</p>
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
      </section>

      <section class="service-grid">
        <router-link
          v-for="service in services"
          :key="service.slug"
          class="service-card"
          :to="service.to"
        >
          <div class="card-topline">
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
          目录页只负责索引和筛选；复杂交互会放到子页面里处理。
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
    slug: 'valuation-backtest',
    to: '/services/valuation-backtest',
    kind: 'Finance',
    title: '老唐估值回测',
    description: '基于利润、国债收益率与历史股本变化，输出价格、内在价值、买点与卖点曲线。',
    topics: ['A-share', 'Valuation', 'ECharts'],
    type: 'Interactive',
    output: 'Chart + JSON',
    live: true
  }
]
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=VT323&family=Nunito:wght@400;600;700&display=swap');

.services-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at 10% 12%, rgba(255, 197, 222, 0.34), transparent 22%),
    radial-gradient(circle at 88% 18%, rgba(150, 220, 255, 0.32), transparent 24%),
    radial-gradient(circle at 58% 78%, rgba(194, 181, 255, 0.18), transparent 20%),
    linear-gradient(180deg, #f8fbff 0%, #f9f6ff 44%, #f6fbff 100%);
  position: relative;
  overflow: hidden;
}

.services-page::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  opacity: 0.22;
  background-image:
    linear-gradient(rgba(123, 146, 255, 0.09) 1px, transparent 1px),
    linear-gradient(90deg, rgba(123, 146, 255, 0.09) 1px, transparent 1px);
  background-size: 26px 26px;
  mask-image: linear-gradient(180deg, rgba(255, 255, 255, 0.82), transparent 92%);
}

.services-page::after {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  opacity: 0.12;
  background:
    radial-gradient(circle at 20% 20%, #fff 0 1px, transparent 1.5px),
    radial-gradient(circle at 70% 32%, #fff 0 1px, transparent 1.5px),
    radial-gradient(circle at 54% 68%, #fff 0 1px, transparent 1.5px),
    radial-gradient(circle at 88% 82%, #fff 0 1px, transparent 1.5px);
  background-size: 180px 180px;
  animation: shimmer 12s linear infinite;
}

.services-main {
  position: relative;
  z-index: 1;
  flex: 1;
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
  padding: 2rem 0 4rem;
}

.services-hero {
  position: relative;
  margin-bottom: 1.5rem;
  padding: 1rem 0 1.5rem;
}

.hero-copy {
  max-width: 760px;
  animation: drift-in 0.75s cubic-bezier(0.16, 1, 0.3, 1);
}

.eyebrow {
  margin: 0 0 0.65rem;
  font-family: 'VT323', monospace;
  font-size: 1.4rem;
  letter-spacing: 0.14em;
  color: #5c67d8;
  text-transform: uppercase;
}

.page-title {
  margin: 0;
  font-family: 'VT323', monospace;
  font-size: clamp(2.2rem, 4.2vw, 3.4rem);
  line-height: 0.92;
  letter-spacing: 0.06em;
  color: #22304a;
}

.page-subtitle {
  margin: 0.95rem 0 0;
  max-width: 42ch;
  font-size: 1rem;
  color: #607089;
}

.hero-status {
  display: inline-flex;
  align-items: center;
  gap: 0.85rem;
  margin-top: 1.35rem;
  padding: 0.75rem 0.95rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.52);
  border: 1px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 10px 30px rgba(107, 124, 167, 0.08);
  backdrop-filter: blur(10px);
}

.status-orb {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  background: linear-gradient(180deg, #72f4be, #3fc4a0);
  box-shadow: 0 0 14px rgba(63, 196, 160, 0.75);
  animation: pulse 2.6s ease-in-out infinite;
}

.status-label {
  margin: 0;
  font-family: 'VT323', monospace;
  font-size: 1.1rem;
  letter-spacing: 0.08em;
  color: #7b86a5;
}

.status-value {
  margin: 0.1rem 0 0;
  color: #27334c;
  font-weight: 700;
}

.pixel-strip {
  display: grid;
  grid-template-columns: repeat(16, 10px);
  gap: 6px;
  margin-top: 1.4rem;
}

.pixel-strip span {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(168, 194, 255, 0.75));
  box-shadow: 0 0 10px rgba(140, 170, 255, 0.22);
  animation: blink 4s ease-in-out infinite;
}

.pixel-strip span:nth-child(3n) {
  animation-delay: 0.4s;
}

.pixel-strip span:nth-child(4n) {
  animation-delay: 0.8s;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.7rem;
  margin-bottom: 1.4rem;
}

.toolbar-chip {
  min-height: 34px;
  padding: 0 0.9rem;
  border: 1px solid rgba(193, 203, 255, 0.75);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.58);
  color: #61708d;
  font-family: 'VT323', monospace;
  font-size: 1.15rem;
  cursor: default;
  backdrop-filter: blur(8px);
}

.toolbar-chip--active {
  background: #eef2ff;
  color: #4653d1;
  box-shadow: inset 0 0 0 1px rgba(108, 124, 255, 0.18);
}

.service-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 260px));
  justify-content: start;
  gap: 0.95rem;
}

.service-card {
  position: relative;
  display: grid;
  gap: 0.8rem;
  min-height: 230px;
  padding: 1rem;
  border-radius: 18px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.88), rgba(255, 255, 255, 0.72)),
    linear-gradient(135deg, rgba(191, 206, 255, 0.18), rgba(255, 214, 234, 0.14));
  border: 1px solid rgba(255, 255, 255, 0.95);
  box-shadow:
    0 16px 30px rgba(116, 132, 171, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(14px);
  transition:
    transform 0.22s ease,
    box-shadow 0.22s ease,
    border-color 0.22s ease;
  animation: drift-in 0.65s cubic-bezier(0.16, 1, 0.3, 1);
}

.service-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.36), transparent 44%),
    radial-gradient(circle at 86% 18%, rgba(164, 223, 255, 0.28), transparent 24%);
  opacity: 0.9;
}

.service-card:hover {
  transform: translateY(-4px) scale(1.01);
  border-color: rgba(218, 225, 255, 0.96);
  box-shadow:
    0 22px 42px rgba(116, 132, 171, 0.15),
    0 0 0 1px rgba(172, 188, 255, 0.14);
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
  justify-content: space-between;
  gap: 0.75rem;
}

.service-kind {
  font-family: 'VT323', monospace;
  font-size: 1.15rem;
  color: #6671db;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.service-state {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 0.65rem;
  border-radius: 999px;
  background: rgba(237, 242, 255, 0.9);
  color: #6d7690;
  font-family: 'VT323', monospace;
  font-size: 1.05rem;
}

.service-state--live {
  background: rgba(223, 255, 239, 0.92);
  color: #28956a;
}

.service-title {
  margin: 0;
  font-size: 1.35rem;
  line-height: 1.15;
  color: #24324c;
}

.service-description {
  margin: 0;
  color: #64748e;
  line-height: 1.55;
  font-size: 0.95rem;
}

.topic-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.topic-chip {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 0.55rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid rgba(214, 221, 244, 0.9);
  color: #677691;
  font-size: 0.78rem;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.65rem;
  margin-top: auto;
}

.meta-item {
  display: grid;
  gap: 0.15rem;
  padding: 0.6rem 0.65rem;
  border-radius: 12px;
  background: rgba(252, 253, 255, 0.78);
  border: 1px solid rgba(228, 233, 248, 0.92);
}

.meta-label {
  font-family: 'VT323', monospace;
  font-size: 1rem;
  color: #8a95b0;
  letter-spacing: 0.06em;
}

.meta-item strong {
  color: #31405e;
  font-size: 0.9rem;
}

.service-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #5060dc;
  font-family: 'VT323', monospace;
  font-size: 1.2rem;
}

.service-arrow {
  transition: transform 0.2s ease;
}

.service-card:hover .service-arrow {
  transform: translate(2px, -2px);
}

.service-note {
  margin-top: 1.8rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(214, 223, 255, 0.68);
}

.note-title {
  margin: 0;
  font-family: 'VT323', monospace;
  font-size: 1.2rem;
  color: #6874d8;
}

.note-text {
  margin: 0.3rem 0 0;
  color: #69788f;
}

@keyframes drift-in {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.85;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.14);
  }
}

@keyframes blink {
  0%, 100% {
    opacity: 0.45;
    transform: translateY(0);
  }
  50% {
    opacity: 1;
    transform: translateY(-1px);
  }
}

@keyframes shimmer {
  from {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
  to {
    transform: translateY(0);
  }
}

@media (max-width: 720px) {
  .services-main {
    width: min(100% - 24px, 1180px);
    padding: 1.4rem 0 3rem;
  }

  .page-title {
    font-size: clamp(1.9rem, 10vw, 2.8rem);
  }

  .service-grid {
    grid-template-columns: repeat(2, minmax(0, 240px));
  }
}

@media (max-width: 560px) {
  .service-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .pixel-strip {
    grid-template-columns: repeat(12, 10px);
  }
}
</style>
