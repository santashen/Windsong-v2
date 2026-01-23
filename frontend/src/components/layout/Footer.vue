<template>
  <footer class="footer">
    <div class="container">
      <p>&copy; 2024 Windsong Blog. Built with Go + Vue + PostgreSQL.</p>
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
  text-align: center;
  color: var(--color-text-secondary);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}
</style>
