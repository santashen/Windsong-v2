<template>
  <div class="heat-page">
    <Header />

    <main class="heat-main">
      <section class="heat-head">
        <div>
          <p class="eyebrow">Thermal Workbench</p>
          <h1 class="page-title">流体换热计算</h1>
          <p class="page-subtitle">
            使用工质、压力、流量和进出口温度计算换热量。
          </p>
        </div>

        <router-link class="back-link" to="/services">返回服务目录</router-link>
      </section>

      <section class="workspace-shell" aria-label="换热计算工作区">
        <aside class="parameter-panel">
          <div class="panel-head">
            <p class="panel-title">统一工况</p>
            <p class="panel-note">工质、压力和流量会应用到本次计算的所有温度行。</p>
          </div>

          <div class="placeholder-stack">
            <div class="placeholder-field">
              <span>工质</span>
              <strong>CoolProp fluid selector</strong>
            </div>
            <div class="placeholder-field">
              <span>压力</span>
              <strong>Pressure + unit</strong>
            </div>
            <div class="placeholder-field">
              <span>流量</span>
              <strong>Flow rate + unit</strong>
            </div>
          </div>
        </aside>

        <section class="input-panel">
          <div class="panel-head">
            <p class="panel-title">温度输入</p>
            <p class="panel-note">下一步会接入单组计算和批量粘贴。</p>
          </div>

          <div class="mode-strip" aria-hidden="true">
            <span class="mode-pill mode-pill--active">单组计算</span>
            <span class="mode-pill">批量计算</span>
          </div>

          <div class="input-skeleton">
            <span></span>
            <span></span>
            <span class="wide"></span>
          </div>
        </section>

        <aside class="result-panel">
          <div class="panel-head">
            <p class="panel-title">结果</p>
            <p class="panel-note">计算完成后展示 Q 和批量结果表。</p>
          </div>

          <div class="result-value">Q_W</div>
          <div class="result-lines" aria-hidden="true">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </aside>
      </section>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import Footer from '@/components/layout/Footer.vue'
import Header from '@/components/layout/Header.vue'
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=VT323&family=Nunito:wght@400;600;700&display=swap');

.heat-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at 14% 16%, rgba(255, 198, 233, 0.28), transparent 24%),
    radial-gradient(circle at 88% 10%, rgba(170, 226, 255, 0.28), transparent 26%),
    linear-gradient(180deg, #fbfcff 0%, #f8fbff 100%);
  color: #27334c;
  position: relative;
}

.heat-page::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  opacity: 0.16;
  background-image:
    linear-gradient(rgba(130, 150, 255, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(130, 150, 255, 0.08) 1px, transparent 1px);
  background-size: 24px 24px;
}

.heat-main {
  position: relative;
  z-index: 1;
  flex: 1;
  width: min(1260px, calc(100% - 32px));
  margin: 0 auto;
  padding: 2rem 0 4rem;
}

.heat-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.4rem;
}

.eyebrow {
  margin: 0 0 0.6rem;
  font-family: 'VT323', monospace;
  font-size: 1.35rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #6471dc;
}

.page-title {
  margin: 0;
  font-family: 'VT323', monospace;
  font-size: clamp(2.4rem, 5vw, 4rem);
  line-height: 0.95;
  letter-spacing: 0.05em;
  color: #283652;
}

.page-subtitle {
  margin: 0.9rem 0 0;
  max-width: 38ch;
  color: #64748e;
}

.back-link {
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  padding: 0 0.9rem;
  border: 1px solid rgba(213, 220, 244, 0.95);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.72);
  color: #5060dc;
  font-weight: 700;
}

.workspace-shell {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr) 280px;
  gap: 1rem;
  align-items: start;
}

.parameter-panel,
.input-panel,
.result-panel {
  padding: 1rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(222, 228, 255, 0.95);
  box-shadow: 0 14px 32px rgba(116, 132, 171, 0.08);
  backdrop-filter: blur(14px);
}

.panel-head {
  margin-bottom: 1rem;
}

.panel-title {
  margin: 0;
  font-family: 'VT323', monospace;
  font-size: 1.35rem;
  letter-spacing: 0.06em;
  color: #5f6de0;
}

.panel-note {
  margin: 0.2rem 0 0;
  color: #7a88a6;
  font-size: 0.9rem;
}

.placeholder-stack {
  display: grid;
  gap: 0.75rem;
}

.placeholder-field {
  display: grid;
  gap: 0.25rem;
  min-height: 64px;
  padding: 0.8rem;
  border-radius: 8px;
  background: rgba(248, 250, 255, 0.8);
  border: 1px dashed rgba(200, 211, 244, 0.95);
}

.placeholder-field span {
  font-family: 'VT323', monospace;
  font-size: 1.05rem;
  color: #8794ad;
}

.placeholder-field strong {
  color: #394861;
  font-size: 0.92rem;
}

.mode-strip {
  display: flex;
  gap: 0.7rem;
  margin-bottom: 1rem;
}

.mode-pill {
  min-height: 36px;
  display: inline-flex;
  align-items: center;
  padding: 0 0.9rem;
  border: 1px solid rgba(213, 220, 244, 0.95);
  border-radius: 8px;
  color: #61708d;
  background: rgba(255, 255, 255, 0.7);
}

.mode-pill--active {
  color: #4453d0;
  background: #eef2ff;
}

.input-skeleton,
.result-lines {
  display: grid;
  gap: 0.75rem;
}

.input-skeleton span,
.result-lines span {
  display: block;
  height: 44px;
  border-radius: 8px;
  background: linear-gradient(90deg, rgba(234, 239, 255, 0.9), rgba(248, 250, 255, 0.9));
}

.input-skeleton .wide {
  height: 120px;
}

.result-value {
  display: grid;
  place-items: center;
  min-height: 120px;
  margin-bottom: 1rem;
  border-radius: 8px;
  background: #f8faff;
  color: #5060dc;
  font-family: 'VT323', monospace;
  font-size: 2rem;
  letter-spacing: 0.08em;
}

@media (max-width: 1080px) {
  .workspace-shell {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .heat-main {
    width: min(100% - 24px, 1260px);
    padding: 1.4rem 0 3rem;
  }

  .heat-head {
    flex-direction: column;
  }

  .mode-strip {
    flex-wrap: wrap;
  }
}
</style>
