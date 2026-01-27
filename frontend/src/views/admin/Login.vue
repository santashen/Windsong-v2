<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="login-logo">W</div>
        <h1>Windsong Admin</h1>
        <p>Enter your API key to continue</p>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="apiKey">API Key</label>
          <input
            id="apiKey"
            v-model="apiKey"
            type="password"
            placeholder="Enter your API key"
            :disabled="authStore.isLoading"
            autocomplete="current-password"
          />
        </div>

        <div class="error-message" v-if="authStore.error">
          {{ authStore.error }}
        </div>

        <button type="submit" class="login-btn" :disabled="authStore.isLoading || !apiKey">
          <span v-if="authStore.isLoading">Verifying...</span>
          <span v-else>Sign In</span>
        </button>
      </form>

      <div class="login-footer">
        <router-link to="/">Back to site</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const apiKey = ref('')

async function handleLogin() {
  const success = await authStore.login(apiKey.value)
  if (success) {
    const redirect = route.query.redirect || '/admin'
    router.push(redirect)
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--aero-gradient-sky);
  padding: 1rem;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: var(--aero-glass-bg-solid);
  backdrop-filter: blur(10px);
  border: 1px solid var(--aero-glass-border);
  border-radius: var(--aero-border-radius);
  box-shadow: var(--aero-glass-shadow);
  padding: 2rem;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-logo {
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  font-size: 1.5rem;
  font-weight: 700;
  border-radius: 16px;
}

.login-header h1 {
  font-size: 1.5rem;
  color: var(--color-text);
  margin-bottom: 0.25rem;
}

.login-header p {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--color-text);
}

.form-group input {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-bg);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.form-group input:disabled {
  background: var(--color-bg-secondary);
  cursor: not-allowed;
}

.error-message {
  padding: 0.75rem;
  margin-bottom: 1rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  color: var(--color-danger);
  font-size: 0.9rem;
}

.login-btn {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  background: var(--color-primary);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.login-btn:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-footer {
  margin-top: 1.5rem;
  text-align: center;
}

.login-footer a {
  color: var(--color-primary);
  font-size: 0.9rem;
}

.login-footer a:hover {
  text-decoration: underline;
}
</style>
