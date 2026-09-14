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
    // 공유 링크 접근 페이지 (비인증)
    path: '/share/:token',
    name: 'ShareView',
    component: () => import('../views/ShareView.vue'),
    meta: { requiresAuth: false }
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
        path: 'search',
        name: 'Search',
        component: () => import('../views/Search.vue')
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
      },
      {
        path: 'scan-list',
        name: 'ScanList',
        component: () => import('../views/ScanList.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'activity-log',
        name: 'ActivityLog',
        redirect: '/settings?section=activity-log',
        meta: { requiresAdmin: true }
      },
      {
        path: 'my/share-links',
        name: 'ShareManage',
        component: () => import('../views/ShareManage.vue')
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

// 지연 로드 청크를 가져오지 못하면 vue-router의 화면 전환이 조용히 실패한다.
// (재배포로 청크 해시가 바뀐 뒤 낡은 index.html을 캐시에 들고 있는 경우 —
//  특히 홈 화면에 추가한 PWA에서 상세 페이지 클릭이 먹지 않는 증상으로 나타난다)
// 이럴 때 한 번만 하드 내비게이션해서 최신 index.html을 받아오게 한다.
const CHUNK_RELOAD_KEY = 'chunk-reload-at'
const CHUNK_RELOAD_COOLDOWN_MS = 10000

const isChunkLoadError = (error) => {
  const message = `${error?.message || ''} ${error?.name || ''}`
  return /Failed to fetch dynamically imported module|Importing a module script failed|error loading dynamically imported module|Unable to preload CSS/i.test(message)
}

router.onError((error, to) => {
  if (!isChunkLoadError(error)) {
    console.error('Router error:', error)
    return
  }

  // 새로고침 후에도 같은 오류가 나면 무한 루프가 되므로 쿨다운을 둔다
  let last = 0
  try {
    last = Number(sessionStorage.getItem(CHUNK_RELOAD_KEY) || 0)
  } catch (e) {
    // 프라이빗 모드 등에서 sessionStorage 접근이 막힐 수 있다 - 1회는 시도
  }

  if (Date.now() - last < CHUNK_RELOAD_COOLDOWN_MS) {
    console.error('Chunk load failed again after reload:', error)
    return
  }

  try {
    sessionStorage.setItem(CHUNK_RELOAD_KEY, String(Date.now()))
  } catch (e) {
    // 무시 - 저장에 실패해도 아래 새로고침은 진행한다
  }

  window.location.assign(to?.fullPath || window.location.pathname)
})

export default router
