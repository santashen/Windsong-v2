<template>
  <aside class="admin-sidebar" :class="{ collapsed }">
    <!-- Logo -->
    <div class="sidebar-header">
      <router-link to="/admin" class="sidebar-logo">
        <span class="logo-icon">W</span>
        <span class="logo-text" v-if="!collapsed">Windsong</span>
      </router-link>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
      >
        <component :is="item.icon" class="nav-icon" />
        <span class="nav-text" v-if="!collapsed">{{ item.label }}</span>
      </router-link>
    </nav>

    <!-- Footer -->
    <div class="sidebar-footer">
      <router-link to="/" class="nav-item">
        <HomeIcon class="nav-icon" />
        <span class="nav-text" v-if="!collapsed">View Site</span>
      </router-link>
    </div>
  </aside>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { PhotoIcon, HomeIcon } from '@/components/icons'

defineProps({
  collapsed: Boolean
})

defineEmits(['toggle'])

const route = useRoute()

const menuItems = [
  { path: '/admin/photos', label: 'Photos', icon: PhotoIcon }
  // Future menu items can be added here:
  // { path: '/admin/posts', label: 'Posts', icon: PostIcon },
  // { path: '/admin/settings', label: 'Settings', icon: SettingsIcon }
]

function isActive(path) {
  return route.path.startsWith(path)
}
</script>

<style scoped>
.admin-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 240px;
  height: 100vh;
  background: var(--color-bg);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  z-index: 100;
}

.admin-sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--color-primary);
  font-weight: 600;
  font-size: 1.1rem;
}

.logo-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  border-radius: 8px;
  font-weight: 700;
  flex-shrink: 0;
}

.logo-text {
  white-space: nowrap;
  overflow: hidden;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: var(--color-text-secondary);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text);
}

.nav-item.active {
  background: rgba(59, 130, 246, 0.1);
  color: var(--color-primary);
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.nav-text {
  white-space: nowrap;
  overflow: hidden;
}

.sidebar-footer {
  padding: 0.75rem;
  border-top: 1px solid var(--color-border);
}

/* Collapsed state */
.collapsed .nav-item {
  justify-content: center;
  padding: 0.75rem;
}

.collapsed .sidebar-logo {
  justify-content: center;
}

@media (max-width: 768px) {
  .admin-sidebar {
    transform: translateX(-100%);
  }

  .admin-sidebar.active {
    transform: translateX(0);
  }
}
</style>
