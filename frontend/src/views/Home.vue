<template>
  <div class="home">
    <Header transparent />

    <section class="hero" ref="heroRef">
      <div class="hero-bg" :style="bgStyle"></div>
      <canvas ref="particleCanvas" class="particle-canvas" :style="canvasStyle"></canvas>

      <div class="hero-content" :style="contentStyle">
        <h1 class="hero-title" :class="{ visible: anim.title }">Windsong</h1>
        <div class="hero-rule" :class="{ visible: anim.rule }"></div>
        <p class="hero-sub" :class="{ visible: anim.sub }">
          Code, photos &amp; the stories in between
        </p>
        <nav class="hero-nav" :class="{ visible: anim.nav }">
          <router-link to="/posts" class="hero-btn hero-btn--filled">进入博客</router-link>
          <router-link to="/gallery" class="hero-btn hero-btn--ghost">看相册</router-link>
        </nav>
      </div>

      <button
        class="scroll-cue"
        :class="{ visible: anim.scroll }"
        :style="scrollCueStyle"
        @click="scrollDown"
        aria-label="Scroll to content"
        style="display: none;"
      >
        <span>SCROLL</span>
        <i class="scroll-track"><i class="scroll-thumb"></i></i>
      </button>
    </section>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import Header from '@/components/layout/Header.vue'

const particleCanvas = ref(null)
const heroRef = ref(null)
const scrollProgress = ref(0)
let frameId = null
let onResize = null
let onScroll = null

const anim = reactive({
  title: false,
  rule: false,
  sub: false,
  nav: false,
  scroll: false,
})

const scrollDown = () => {
  // No longer needed, but keep for potential future use
}

// ── Scroll-driven styles ──
const bgStyle = computed(() => {
  const p = scrollProgress.value
  return {
    filter: `blur(${p * 8}px) saturate(${1 - p * 0.6})`,
    transform: `scale(${1 + p * 0.1}) translateY(${p * 30}px)`,
  }
})

const contentStyle = computed(() => {
  const p = scrollProgress.value
  return {
    opacity: 1 - p * 1.5,
    transform: `translateY(${p * -60}px)`,
  }
})

const scrollCueStyle = computed(() => {
  const p = scrollProgress.value
  return {
    opacity: Math.max(0, 1 - p * 3),
  }
})

const canvasStyle = computed(() => {
  const p = scrollProgress.value
  return {
    opacity: 1 - p * 1.2,
  }
})

// ── Scroll listener ──
function handleScroll() {
  if (!heroRef.value) return
  const heroHeight = heroRef.value.offsetHeight
  const scrollY = window.scrollY || window.pageYOffset
  scrollProgress.value = Math.min(Math.max(scrollY / heroHeight, 0), 1)
}

// ── Canvas particle field ──
function initCanvas() {
  const cvs = particleCanvas.value
  if (!cvs) return
  const ctx = cvs.getContext('2d')

  function resize() {
    const dpr = window.devicePixelRatio || 1
    cvs.width = window.innerWidth * dpr
    cvs.height = window.innerHeight * dpr
    cvs.style.width = window.innerWidth + 'px'
    cvs.style.height = window.innerHeight + 'px'
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  }
  resize()
  onResize = resize
  window.addEventListener('resize', onResize)

  const N = Math.min(70, Math.floor(window.innerWidth / 18))
  const dots = Array.from({ length: N }, () => ({
    x: Math.random() * window.innerWidth,
    y: Math.random() * window.innerHeight,
    r: Math.random() * 1.4 + 0.4,
    dx: (Math.random() - 0.5) * 0.3,
    dy: (Math.random() - 0.5) * 0.18,
    a: Math.random() * 0.4 + 0.12,
    p: Math.random() * 6.28,
  }))

  function frame() {
    const W = window.innerWidth
    const H = window.innerHeight
    ctx.clearRect(0, 0, W, H)

    for (const d of dots) {
      d.x += d.dx
      d.y += d.dy
      d.p += 0.007

      if (d.x < -20) d.x += W + 40
      if (d.x > W + 20) d.x -= W + 40
      if (d.y < -20) d.y += H + 40
      if (d.y > H + 20) d.y -= H + 40

      const a = d.a * (0.6 + 0.4 * Math.sin(d.p))

      // soft glow - warm golden
      ctx.beginPath()
      ctx.arc(d.x, d.y, d.r * 4, 0, 6.28)
      ctx.fillStyle = `rgba(255,245,220,${a * 0.08})`
      ctx.fill()

      // core - warm white
      ctx.beginPath()
      ctx.arc(d.x, d.y, d.r, 0, 6.28)
      ctx.fillStyle = `rgba(255,252,240,${a})`
      ctx.fill()
    }

    frameId = requestAnimationFrame(frame)
  }
  frame()
}

// ── Staggered entrance ──
let entranceTimers = []

function entrance() {
  const steps = [
    ['title', 300],
    ['rule', 700],
    ['sub', 1000],
    ['nav', 1400],
    ['scroll', 2000],
  ]
  entranceTimers = steps.map(([key, ms]) =>
    setTimeout(() => { anim[key] = true }, ms),
  )
}

onMounted(() => {
  initCanvas()
  entrance()
  onScroll = handleScroll
  window.addEventListener('scroll', onScroll, { passive: true })
  handleScroll() // initial
})

onBeforeUnmount(() => {
  if (frameId) cancelAnimationFrame(frameId)
  if (onResize) window.removeEventListener('resize', onResize)
  if (onScroll) window.removeEventListener('scroll', onScroll)
  entranceTimers.forEach(clearTimeout)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400&display=swap');

/* ── layout ── */
.home {
  height: 100vh;
  overflow: hidden;
}

/* ── hero ── */
.hero {
  position: relative;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  z-index: 1;
  background-image: url(/background/background.jpg);
  background-size: cover;
  background-position: center;
  will-change: transform, filter;
}

/* overlay for text readability */
.hero::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  background: linear-gradient(
    180deg,
    rgba(0, 0, 0, 0.05) 0%,
    rgba(0, 0, 0, 0.15) 40%,
    rgba(0, 0, 0, 0.35) 100%
  );
}

.particle-canvas {
  position: absolute;
  inset: 0;
  z-index: 3;
  pointer-events: none;
  will-change: opacity;
}

/* ── hero content ── */
.hero-content {
  position: relative;
  z-index: 10;
  text-align: center;
  padding: 0 1.5rem;
  will-change: transform, opacity;
}

.hero-title {
  font-family: 'Cormorant Garamond', Georgia, 'Times New Roman', serif;
  font-weight: 300;
  font-size: clamp(3.2rem, 9vw, 7rem);
  color: #fff;
  letter-spacing: 0.18em;
  margin: 0;
  line-height: 1.1;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.5), 0 0 60px rgba(255, 255, 255, 0.15);
  opacity: 0;
  transform: translateY(28px);
  transition: opacity 1s cubic-bezier(0.16, 1, 0.3, 1),
              transform 1s cubic-bezier(0.16, 1, 0.3, 1);
}

.hero-title.visible {
  opacity: 1;
  transform: none;
}

.hero-rule {
  width: 0;
  height: 1px;
  margin: 1.2rem auto 1.4rem;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.35), transparent);
  transition: width 0.9s cubic-bezier(0.16, 1, 0.3, 1);
}

.hero-rule.visible {
  width: 100px;
}

.hero-sub {
  font-size: clamp(0.9rem, 1.8vw, 1.1rem);
  color: rgba(255, 255, 255, 0.85);
  letter-spacing: 0.1em;
  margin: 0 0 2.8rem;
  font-weight: 400;
  text-shadow: 0 1px 8px rgba(0, 0, 0, 0.4);
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1),
              transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.hero-sub.visible {
  opacity: 1;
  transform: none;
}

/* ── cta buttons ── */
.hero-nav {
  display: flex;
  gap: 0.9rem;
  justify-content: center;
  flex-wrap: wrap;
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1),
              transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.hero-nav.visible {
  opacity: 1;
  transform: none;
}

.hero-btn {
  display: inline-flex;
  align-items: center;
  padding: 0.7rem 2rem;
  border-radius: 5px;
  font-size: 0.88rem;
  letter-spacing: 0.06em;
  text-decoration: none;
  transition: all 0.35s ease;
}

.hero-btn--filled {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(12px);
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

.hero-btn--filled:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3);
}

.hero-btn--ghost {
  background: transparent;
  color: rgba(255, 255, 255, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.15);
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

.hero-btn--ghost:hover {
  color: rgba(255, 255, 255, 0.95);
  border-color: rgba(255, 255, 255, 0.35);
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-2px);
}

/* ── scroll indicator ── */
.scroll-cue {
  position: absolute;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  opacity: 0;
  transition: opacity 1.2s ease;
  will-change: opacity;
}

.scroll-cue.visible {
  opacity: 1;
}

.scroll-cue:hover {
  opacity: 0.85 !important;
}

.scroll-cue > span {
  font-size: 0.6rem;
  letter-spacing: 0.35em;
  color: rgba(255, 255, 255, 0.6);
  font-family: inherit;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.4);
}

.scroll-track {
  display: block;
  width: 1px;
  height: 36px;
  background: rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
  font-style: normal;
}

.scroll-thumb {
  display: block;
  width: 1px;
  height: 10px;
  background: rgba(255, 255, 255, 0.7);
  position: absolute;
  top: -10px;
  font-style: normal;
  animation: thumb-drop 2s ease-in-out infinite;
}

@keyframes thumb-drop {
  0%   { top: -10px; opacity: 0; }
  25%  { opacity: 1; }
  100% { top: 36px; opacity: 0; }
}

/* ── responsive ── */
@media (max-width: 640px) {
  .hero {
    height: 100svh;
  }

  .hero-nav {
    flex-direction: column;
    align-items: center;
  }

  .hero-btn {
    width: 180px;
    justify-content: center;
  }
}
</style>
