import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import About from '@/views/About.vue'
import Gallery from '@/views/Gallery.vue'
import BlogList from '@/views/BlogList.vue'
import BlogPost from '@/views/BlogPost.vue'
import Services from '@/views/Services.vue'
import ValuationBacktest from '@/views/ValuationBacktest.vue'
import FamilyPortfolio from '@/views/FamilyPortfolio.vue'
import HeatDissipationCalculator from '@/views/HeatDissipationCalculator.vue'

// Admin views (lazy loaded)
const AdminLayout = () => import('@/views/admin/AdminLayout.vue')
const AdminLogin = () => import('@/views/admin/Login.vue')
const AdminPhotos = () => import('@/views/admin/Photos.vue')
const AdminFamilyPortfolio = () => import('@/views/admin/FamilyPortfolioAdmin.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/gallery',
    name: 'Gallery',
    component: Gallery
  },
  {
    path: '/posts',
    name: 'BlogList',
    component: BlogList
  },
  {
    path: '/posts/:slug',
    name: 'BlogPost',
    component: BlogPost
  },
  {
    path: '/about',
    name: 'About',
    component: About
  },
  {
    path: '/services',
    name: 'Services',
    component: Services
  },
  {
    path: '/services/valuation-backtest',
    name: 'ValuationBacktest',
    component: ValuationBacktest
  },
  {
    path: '/services/family-portfolio',
    name: 'FamilyPortfolio',
    component: FamilyPortfolio
  },
  {
    path: '/services/heat-dissipation-calculator',
    name: 'HeatDissipationCalculator',
    component: HeatDissipationCalculator
  },
  // Admin routes
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: AdminLogin,
    meta: { requiresGuest: true }
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/admin/photos'
      },
      {
        path: 'photos',
        name: 'AdminPhotos',
        component: AdminPhotos
      },
      {
        path: 'family-portfolio',
        name: 'AdminFamilyPortfolio',
        component: AdminFamilyPortfolio
      }
      // Future admin routes can be added here
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  // Lazy import to avoid circular dependency
  const { useAuthStore } = await import('@/stores/auth')
  const authStore = useAuthStore()

  // Initialize auth on first navigation if we have a stored key
  if (authStore.hasStoredKey && !authStore.isAuthenticated && !authStore.isLoading) {
    await authStore.initAuth()
  }

  // Check if route requires authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!authStore.isAuthenticated) {
      next({
        path: '/admin/login',
        query: { redirect: to.fullPath }
      })
      return
    }
  }

  // Check if route requires guest (login page - redirect if already logged in)
  if (to.matched.some(record => record.meta.requiresGuest)) {
    if (authStore.isAuthenticated) {
      next('/admin')
      return
    }
  }

  next()
})

export default router
