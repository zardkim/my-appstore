<template>
  <div class="flex flex-col h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300"
       :class="isCollapsed ? 'w-16' : 'w-60'">
    <!-- Logo & Toggle -->
    <div class="flex items-center justify-between px-4 py-5 border-b border-gray-200 dark:border-gray-700">
      <div v-if="!isCollapsed" class="flex items-center space-x-3">
        <div class="w-9 h-9 flex items-center justify-center">
          <img src="/logo/myapp_logo_v2.svg" alt="MyApp Store" class="w-9 h-9" />
        </div>
        <div>
          <h1 class="font-bold text-gray-900 dark:text-white">MyApp Store</h1>
        </div>
      </div>
      <button
        @click="toggleSidebar"
        class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        :class="isCollapsed ? 'mx-auto' : ''"
      >
        <svg class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                :d="isCollapsed ? 'M13 5l7 7-7 7M5 5l7 7-7 7' : 'M11 19l-7-7 7-7m8 14l-7-7 7-7'" />
        </svg>
      </button>
    </div>

    <!-- Menu Items -->
    <nav class="flex-1 overflow-y-auto py-4 px-2 scrollbar-hide">
      <!-- Home -->
      <button
        @click="goToHome"
        :class="[
          'menu-item group',
          isCollapsed ? 'justify-center' : '',
          isHomeActive ? 'bg-gradient-to-r from-blue-500 to-purple-600 !text-white shadow-md' : ''
        ]"
      >
        <div class="menu-icon" :class="isHomeActive ? '!text-white' : ''">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
        </div>
        <span v-if="!isCollapsed" class="menu-text" :class="isHomeActive ? '!text-white' : ''">{{ $t('nav.home') }}</span>
      </button>

      <!-- Store -->
      <router-link
        to="/discover"
        class="menu-item group"
        :class="isCollapsed ? 'justify-center' : ''"
      >
        <div class="menu-icon">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
        </div>
        <span v-if="!isCollapsed" class="menu-text">{{ $t('nav.discover') }}</span>
      </router-link>

      <!-- Tips & Tech -->
      <router-link
        to="/tips"
        class="menu-item group"
        :class="isCollapsed ? 'justify-center' : ''"
      >
        <div class="menu-icon">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <span v-if="!isCollapsed" class="menu-text">{{ $t('nav.tips') }}</span>
      </router-link>

      <!-- Divider -->
      <div v-if="!isCollapsed" class="my-4 border-t border-gray-200 dark:border-gray-700"></div>
      <div v-else class="my-2"></div>

      <!-- Settings -->
      <router-link
        to="/settings"
        class="menu-item group"
        :class="isCollapsed ? 'justify-center' : ''"
      >
        <div class="menu-icon">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <span v-if="!isCollapsed" class="menu-text">{{ $t('nav.settings') }}</span>
      </router-link>

    </nav>

    <!-- User Info with Dropdown -->
    <div class="border-t border-gray-200 dark:border-gray-700 p-3 relative">
      <!-- Expanded View -->
      <div v-if="!isCollapsed">
        <button
          @click="toggleUserMenu"
          class="flex items-center space-x-3 w-full p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors group"
        >
          <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0 shadow-md">
            <span class="text-sm font-bold text-white">{{ userInitial }}</span>
          </div>
          <div class="flex-1 min-w-0 text-left">
            <p class="text-sm font-semibold text-gray-900 dark:text-white truncate">{{ username }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400 capitalize">{{ userRole }}</p>
          </div>
          <svg
            class="w-5 h-5 text-gray-400 dark:text-gray-500 transition-transform"
            :class="showUserMenu ? 'rotate-180' : ''"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- Dropdown Menu -->
        <div
          v-if="showUserMenu"
          class="absolute bottom-full left-0 right-0 mb-2 mx-3 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden z-50"
        >
          <router-link
            to="/favorites"
            @click="showUserMenu = false"
            class="flex items-center px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-gray-700 dark:text-gray-300"
          >
            <svg class="w-5 h-5 mr-3 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            <span class="text-sm font-medium">{{ $t('nav.favorites') }}</span>
          </router-link>

          <router-link
            to="/scraps"
            @click="showUserMenu = false"
            class="flex items-center px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-gray-700 dark:text-gray-300"
          >
            <svg class="w-5 h-5 mr-3 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
            </svg>
            <span class="text-sm font-medium">{{ $t('nav.scraps') }}</span>
          </router-link>

          <div class="border-t border-gray-200 dark:border-gray-700"></div>

          <router-link
            to="/change-password"
            @click="showUserMenu = false"
            class="flex items-center px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-gray-700 dark:text-gray-300"
          >
            <svg class="w-5 h-5 mr-3 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
            </svg>
            <span class="text-sm font-medium">{{ $t('nav.changePassword') }}</span>
          </router-link>

          <div class="border-t border-gray-200 dark:border-gray-700"></div>

          <button
            @click="toggleTheme"
            class="flex items-center w-full px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-gray-700 dark:text-gray-300"
          >
            <svg v-if="!themeStore.isDark" class="w-5 h-5 mr-3 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
            <svg v-else class="w-5 h-5 mr-3 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <span class="text-sm font-medium">{{ themeStore.isDark ? $t('theme.light') : $t('theme.dark') }}</span>
          </button>

          <div class="border-t border-gray-200 dark:border-gray-700"></div>

          <button
            @click="logout"
            class="flex items-center w-full px-4 py-3 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors text-red-600 dark:text-red-400"
          >
            <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            <span class="text-sm font-medium">{{ $t('nav.logout') }}</span>
          </button>
        </div>
      </div>

      <!-- Collapsed View -->
      <div v-else class="flex flex-col items-center space-y-2">
        <button
          @click="toggleUserMenu"
          class="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-md hover:shadow-lg transition-shadow"
        >
          <span class="text-xs font-bold text-white">{{ userInitial }}</span>
        </button>

        <!-- Collapsed Dropdown Menu -->
        <div
          v-if="showUserMenu"
          class="absolute bottom-full left-full ml-2 mb-3 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden z-50 w-48"
        >
          <router-link
            to="/favorites"
            @click="showUserMenu = false"
            class="flex items-center px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-gray-700 dark:text-gray-300"
          >
            <svg class="w-5 h-5 mr-3 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            <span class="text-sm font-medium">{{ $t('nav.favorites') }}</span>
          </router-link>

          <router-link
            to="/scraps"
            @click="showUserMenu = false"
            class="flex items-center px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-gray-700 dark:text-gray-300"
          >
            <svg class="w-5 h-5 mr-3 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
            </svg>
            <span class="text-sm font-medium">{{ $t('nav.scraps') }}</span>
          </router-link>

          <div class="border-t border-gray-200 dark:border-gray-700"></div>

          <router-link
            to="/change-password"
            @click="showUserMenu = false"
            class="flex items-center px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-gray-700 dark:text-gray-300"
          >
            <svg class="w-5 h-5 mr-3 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
            </svg>
            <span class="text-sm font-medium">{{ $t('nav.changePassword') }}</span>
          </router-link>

          <div class="border-t border-gray-200 dark:border-gray-700"></div>

          <button
            @click="toggleTheme"
            class="flex items-center w-full px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-gray-700 dark:text-gray-300"
          >
            <svg v-if="!themeStore.isDark" class="w-5 h-5 mr-3 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
            <svg v-else class="w-5 h-5 mr-3 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <span class="text-sm font-medium">{{ themeStore.isDark ? $t('theme.light') : $t('theme.dark') }}</span>
          </button>

          <div class="border-t border-gray-200 dark:border-gray-700"></div>

          <button
            @click="logout"
            class="flex items-center w-full px-4 py-3 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors text-red-600 dark:text-red-400"
          >
            <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            <span class="text-sm font-medium">{{ $t('nav.logout') }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import { useThemeStore } from '../../store/theme'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const isCollapsed = ref(false)
const showUserMenu = ref(false)

const username = computed(() => authStore.user?.username || 'User')
const userRole = computed(() => authStore.user?.role || 'user')
const isAdmin = computed(() => authStore.user?.role === 'admin')
const userInitial = computed(() => username.value.charAt(0).toUpperCase())

// 홈 메뉴가 정확히 '/' 경로일 때만 활성화되도록
const isHomeActive = computed(() => route.path === '/')

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const goToHome = () => {
  router.push('/')
}

const logout = () => {
  showUserMenu.value = false
  authStore.logout()
  router.push('/login')
}

const toggleTheme = () => {
  themeStore.toggleTheme()
}

// 외부 클릭 시 드롭다운 닫기
const handleClickOutside = (event) => {
  if (showUserMenu.value) {
    const userInfoElement = event.target.closest('.border-t.border-gray-200.dark\\:border-gray-700.p-3.relative')
    if (!userInfoElement) {
      showUserMenu.value = false
    }
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.menu-item {
  @apply flex items-center px-3 py-2.5 mx-1 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-gray-700 hover:text-blue-600 dark:hover:text-blue-400 transition-all cursor-pointer font-medium text-sm;
}

.menu-item.router-link-active {
  @apply bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-md;
}

.menu-item.router-link-active .menu-icon {
  @apply text-white;
}

.menu-icon {
  @apply flex-shrink-0 text-gray-500 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors;
}

.menu-item.router-link-active .menu-icon {
  @apply text-white;
}

.menu-text {
  @apply ml-3 font-medium;
}

/* Hide scrollbar */
.scrollbar-hide {
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;  /* Chrome, Safari and Opera */
}
</style>
