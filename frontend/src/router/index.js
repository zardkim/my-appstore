import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'
import MainLayout from '../components/layout/MainLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/setup',
    name: 'Setup',
    component: () => import('../views/Setup.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('../views/Home.vue')
      },
      {
        path: 'discover',
        name: 'Discover',
        component: () => import('../views/Discover.vue')
      },
      {
        path: 'tips',
        name: 'Tips',
        component: () => import('../views/Tips.vue')
      },
      {
        path: 'tips/write',
        name: 'TipsWrite',
        component: () => import('../views/TipsWrite.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'tips/edit/:id',
        name: 'TipsEdit',
        component: () => import('../views/TipsWrite.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'tips/:id',
        name: 'TipsDetail',
        component: () => import('../views/TipsDetail.vue')
      },
      {
        path: 'product/:id',
        name: 'ProductDetail',
        component: () => import('../views/ProductDetail.vue')
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/Settings.vue')
      },
      {
        path: 'admin',
        name: 'Admin',
        component: () => import('../views/Admin.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'favorites',
        name: 'Favorites',
        component: () => import('../views/Favorites.vue')
      },
      {
        path: 'scraps',
        name: 'Scraps',
        component: () => import('../views/Scraps.vue')
      },
      {
        path: 'change-password',
        name: 'ChangePassword',
        component: () => import('../views/ChangePassword.vue')
      },
      {
        path: 'filing-rules',
        name: 'FilingRules',
        component: () => import('../views/FilingRules.vue')
      },
      {
        path: 'filename-violations',
        name: 'FilenameViolations',
        component: () => import('../views/FilenameViolations.vue'),
        meta: { requiresAdmin: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresAdmin && authStore.user?.role !== 'admin') {
    next('/')
  } else {
    next()
  }
})

export default router
