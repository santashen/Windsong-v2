<template>
  <div class="home">
    <Header />
    <main class="main-content">
      <div class="container">
        <div class="hero">
          <h1>Welcome to Windsong Blog</h1>
          <p>A simple blog powered by Go + Vue + PostgreSQL</p>
          <button @click="testApi" class="btn-primary">Test API</button>
          <p v-if="apiMessage" class="api-message">{{ apiMessage }}</p>
        </div>
      </div>
    </main>
    <Footer />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import api from '@/api'

const apiMessage = ref('')

const testApi = async () => {
  try {
    const response = await api.get('/hello')
    apiMessage.value = response.data.message
  } catch (error) {
    apiMessage.value = 'Error: ' + error.message
  }
}
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  padding: 2rem 0;
}

.hero {
  text-align: center;
  padding: 4rem 0;
}

.hero h1 {
  font-size: 2.5rem;
  color: var(--color-text);
  margin-bottom: 1rem;
}

.hero p {
  color: var(--color-text-secondary);
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

.btn-primary {
  padding: 0.75rem 2rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-primary:hover {
  background: var(--color-primary-hover);
}

.api-message {
  margin-top: 1.5rem;
  color: var(--color-success);
}
</style>
