<template>
  <footer class="footer">
    <div class="container">
      <p class="footer-copy">&copy; 2024 Windsong Blog. Built with Go + Vue + PostgreSQL.</p>
      <a class="rss-link" href="/rss.xml">
        <svg
          class="rss-icon"
          viewBox="0 0 24 24"
          aria-hidden="true"
          focusable="false"
        >
          <circle cx="5" cy="19" r="2" />
          <path d="M4 11a9 9 0 0 1 9 9" />
          <path d="M4 4a16 16 0 0 1 16 16" />
        </svg>
        <span>RSS 订阅</span>
      </a>
    </div>
  </footer>
</template>

<script setup>
// Footer 组件
</script>

<style scoped>
.footer {
  background: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border);
  padding: 1.5rem 0;
  color: var(--color-text-secondary);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem 2rem;
}

.footer-copy {
  margin: 0;
}

.rss-link {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  flex-shrink: 0;
  padding: 0.25rem 0;
  color: var(--color-text-secondary);
  font-weight: 600;
  text-underline-offset: 0.2em;
  transition: color 160ms ease, transform 160ms ease;
}

.rss-icon {
  width: 1rem;
  height: 1rem;
  fill: currentColor;
  transition: transform 160ms ease;
}

.rss-icon path {
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
}

.rss-link:hover {
  color: var(--color-primary-hover);
  transform: translateY(-1px);
  text-decoration: underline;
}

.rss-link:hover .rss-icon {
  transform: scale(1.08);
}

.rss-link:focus-visible {
  color: var(--color-primary-hover);
  outline: 2px solid var(--color-primary);
  outline-offset: 4px;
}

@media (max-width: 640px) {
  .container {
    flex-direction: column;
    text-align: center;
  }
}
</style>
