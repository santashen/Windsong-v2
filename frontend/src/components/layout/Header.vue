<template>
  <header class="header" :class="{ 'header--transparent': transparent }">
    <div class="container">
      <nav class="nav">
        <router-link to="/" class="logo">
          Windsong Blog
        </router-link>
        <ul class="nav-links">
          <li><router-link to="/">Home</router-link></li>
          <li><router-link to="/posts">Blog</router-link></li>
          <li><router-link to="/gallery">Gallery</router-link></li>
          <li><router-link to="/portfolio">Portfolio</router-link></li>
          <li><router-link to="/services">Services</router-link></li>
          <li><router-link to="/about">About</router-link></li>
        </ul>
      </nav>
    </div>
  </header>
</template>

<script setup>
defineProps({
  transparent: {
    type: Boolean,
    default: false,
  },
})
</script>

<style scoped>
.header {
  background: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
  padding: 1rem 0;
}

.header--transparent {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: transparent;
  border-bottom: none;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--color-primary);
  text-decoration: none;
}

.header--transparent .logo {
  color: rgba(255, 255, 255, 0.9);
}

.nav-links {
  display: flex;
  list-style: none;
  gap: 2rem;
  margin: 0;
  padding: 0;
}

.nav-links a {
  color: var(--color-text);
  text-decoration: none;
  transition: color 0.3s;
}

.header--transparent .nav-links a {
  color: rgba(255, 255, 255, 0.55);
}

.nav-links a:hover,
.nav-links a.router-link-active {
  color: var(--color-primary);
}

.header--transparent .nav-links a:hover,
.header--transparent .nav-links a.router-link-active {
  color: rgba(255, 255, 255, 0.95);
}
</style>
