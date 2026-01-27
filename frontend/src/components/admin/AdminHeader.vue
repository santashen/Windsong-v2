<template>
  <header class="admin-header">
    <div class="header-left">
      <button class="menu-toggle" @click="$emit('toggle-sidebar')">
        <MenuIcon />
      </button>
      <h1 class="page-title">{{ pageTitle }}</h1>
    </div>

    <div class="header-right">
      <button class="logout-btn" @click="handleLogout">
        <LogoutIcon />
        <span>Logout</span>
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { MenuIcon, LogoutIcon } from '@/components/icons'

defineEmits(['toggle-sidebar'])

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const pageTitle = computed(() => {
  const titles = {
    '/admin/photos': 'Photos Management'
    // Add more titles here as you add more admin pages
  }
  return titles[route.path] || 'Admin'
})

function handleLogout() {
  authStore.logout()
  router.push('/admin/login')
}
</script>

<style scoped>
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.menu-toggle {
  display: none;
  padding: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-secondary);
  border-radius: 6px;
}

.menu-toggle:hover {
  background: var(--color-bg-secondary);
}

.page-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: none;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.logout-btn:hover {
  background: var(--color-bg-secondary);
  color: var(--color-danger);
  border-color: var(--color-danger);
}

@media (max-width: 768px) {
  .menu-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .logout-btn span {
    display: none;
  }
}
</style>
