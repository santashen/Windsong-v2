<template>
  <div class="admin-layout">
    <!-- Sidebar -->
    <AdminSidebar :collapsed="sidebarCollapsed" @toggle="toggleSidebar" />

    <!-- Main content area -->
    <div class="admin-main" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <!-- Top header -->
      <AdminHeader @toggle-sidebar="toggleSidebar" />

      <!-- Page content -->
      <main class="admin-content">
        <router-view />
      </main>
    </div>

    <!-- Mobile overlay -->
    <div
      class="mobile-overlay"
      :class="{ active: mobileMenuOpen }"
      @click="mobileMenuOpen = false"
    ></div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import AdminHeader from '@/components/admin/AdminHeader.vue'

const sidebarCollapsed = ref(false)
const mobileMenuOpen = ref(false)

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: var(--color-bg-secondary);
}

.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 240px;
  transition: margin-left 0.3s ease;
}

.admin-main.sidebar-collapsed {
  margin-left: 64px;
}

.admin-content {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

.mobile-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 99;
}

@media (max-width: 768px) {
  .admin-main {
    margin-left: 0;
  }

  .admin-main.sidebar-collapsed {
    margin-left: 0;
  }

  .mobile-overlay.active {
    display: block;
  }
}
</style>
