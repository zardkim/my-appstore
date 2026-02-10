<template>
  <div class="flex h-screen overflow-hidden bg-gray-50 dark:bg-gray-900">
    <!-- Sidebar (Desktop only) -->
    <div class="hidden lg:block">
      <Sidebar />
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Main Content Area -->
      <main class="flex-1 overflow-y-auto main-content-area lg:pb-0 overscroll-contain">
        <router-view />
      </main>

      <!-- Footer (Desktop only) -->
      <div class="hidden lg:block">
        <Footer />
      </div>
    </div>

    <!-- Mobile Bottom Navigation -->
    <nav class="lg:hidden fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 z-50 safe-area-bottom overflow-x-auto scrollbar-hide scroll-smooth touch-pan-x">
      <div class="flex items-center h-16 px-2">
        <!-- Home -->
        <router-link
          to="/"
          class="mobile-nav-item flex-shrink-0"
          :class="{ 'active': $route.path === '/' }"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          <span class="mobile-nav-text">{{ $t('nav.home') }}</span>
        </router-link>

        <!-- Discover -->
        <router-link
          to="/discover"
          class="mobile-nav-item flex-shrink-0"
          :class="{ 'active': $route.path === '/discover' || $route.path.startsWith('/product/') }"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
          <span class="mobile-nav-text">{{ $t('nav.discover') }}</span>
        </router-link>

        <!-- Detected List (Admin Only) -->
        <router-link
          v-if="isAdmin"
          to="/filename-violations"
          class="mobile-nav-item flex-shrink-0"
          :class="{ 'active': $route.path === '/filename-violations' }"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span class="mobile-nav-text">{{ $t('nav.detectedList') }}</span>
        </router-link>

        <!-- Tips -->
        <router-link
          to="/tips"
          class="mobile-nav-item flex-shrink-0"
          :class="{ 'active': $route.path.startsWith('/tips') }"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <span class="mobile-nav-text">{{ $t('nav.tips') }}</span>
        </router-link>

        <!-- Favorites -->
        <router-link
          to="/favorites"
          class="mobile-nav-item flex-shrink-0"
          :class="{ 'active': $route.path === '/favorites' }"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
          <span class="mobile-nav-text">{{ $t('nav.favorites') }}</span>
        </router-link>

        <!-- Scraps -->
        <router-link
          to="/scraps"
          class="mobile-nav-item flex-shrink-0"
          :class="{ 'active': $route.path === '/scraps' }"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
          </svg>
          <span class="mobile-nav-text">{{ $t('nav.scraps') }}</span>
        </router-link>

        <!-- Settings (Admin only) -->
        <router-link
          v-if="isAdmin"
          to="/settings"
          class="mobile-nav-item flex-shrink-0"
          :class="{ 'active': $route.path === '/settings' }"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span class="mobile-nav-text">{{ $t('nav.settings') }}</span>
        </router-link>

        <!-- More Menu -->
        <button
          @click="toggleMobileMenu"
          class="mobile-nav-item flex-shrink-0"
          :class="{ 'active': showMobileMenu }"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <span class="mobile-nav-text">{{ $t('nav.more') }}</span>
        </button>
      </div>
    </nav>

    <!-- Mobile Full Menu (More 클릭 시) -->
    <transition name="slide-up">
      <div
        v-if="showMobileMenu"
        class="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
        @click="toggleMobileMenu"
      >
        <div
          class="absolute left-0 right-0 bg-white dark:bg-gray-800 rounded-t-3xl max-h-[70vh] overflow-y-auto"
          :style="{ bottom: 'calc(4rem + env(safe-area-inset-bottom, 0px))' }"
          @click.stop
        >
          <!-- User Info Header -->
          <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
            <div class="flex items-center space-x-3">
              <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg">
                <span class="text-lg font-bold text-white">{{ userInitial }}</span>
              </div>
              <div>
                <p class="text-base font-bold text-gray-900 dark:text-white">{{ username }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400 capitalize">{{ userRole }}</p>
              </div>
            </div>
          </div>

          <!-- Menu Items -->
          <div class="p-3">
            <router-link
              to="/change-password"
              @click="toggleMobileMenu"
              class="mobile-menu-item"
            >
              <svg class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
              <span class="text-sm">{{ $t('nav.changePassword') }}</span>
            </router-link>

            <div class="border-t border-gray-200 dark:border-gray-700 my-1"></div>

            <button
              @click="toggleLanguage"
              class="mobile-menu-item w-full"
            >
              <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
              </svg>
              <span class="text-sm">{{ localeStore.locale === 'ko' ? 'English' : '한국어' }}</span>
            </button>

            <button
              @click="toggleTheme"
              class="mobile-menu-item w-full"
            >
              <svg v-if="!themeStore.isDark" class="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
              <svg v-else class="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              <span class="text-sm">{{ themeStore.isDark ? $t('theme.light') : $t('theme.dark') }}</span>
            </button>

            <div class="border-t border-gray-200 dark:border-gray-700 my-1"></div>

            <button
              @click="logout"
              class="mobile-menu-item w-full text-red-600 dark:text-red-400"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span class="text-sm">{{ $t('nav.logout') }}</span>
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import { useThemeStore } from '../../store/theme'
import { useLocaleStore } from '../../store/locale'
import Sidebar from './Sidebar.vue'
import Footer from './Footer.vue'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const localeStore = useLocaleStore()

const showMobileMenu = ref(false)

const username = computed(() => authStore.user?.username || 'User')
const userRole = computed(() => authStore.user?.role || 'user')
const isAdmin = computed(() => authStore.user?.role === 'admin')
const userInitial = computed(() => username.value.charAt(0).toUpperCase())

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
}

const toggleLanguage = () => {
  const newLocale = localeStore.locale === 'ko' ? 'en' : 'ko'
  localeStore.setLocale(newLocale)
  showMobileMenu.value = false
}

const toggleTheme = () => {
  themeStore.toggleTheme()
  showMobileMenu.value = false
}

const logout = () => {
  showMobileMenu.value = false
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
/* Mobile Navigation Styles */
.mobile-nav-item {
  @apply flex flex-col items-center justify-center space-y-1 text-gray-600 dark:text-gray-400 transition-colors;
  min-width: 70px;
  padding: 0.5rem 0.75rem;
}

.mobile-nav-item.active {
  @apply text-blue-600 dark:text-blue-400;
}

.mobile-nav-item:hover {
  @apply text-blue-500 dark:text-blue-300;
}

.mobile-nav-text {
  @apply text-xs font-medium;
}

/* Mobile Menu Items */
.mobile-menu-item {
  @apply flex items-center space-x-2 p-2.5 rounded-lg transition-colors;
  @apply text-gray-700 dark:text-gray-300;
  @apply hover:bg-gray-100 dark:hover:bg-gray-700;
}

.mobile-menu-item:active {
  @apply bg-gray-200 dark:bg-gray-600;
}

/* Slide-up transition */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease-out;
}

.slide-up-enter-from {
  opacity: 0;
}

.slide-up-leave-to {
  opacity: 0;
}

.slide-up-enter-from .absolute,
.slide-up-leave-to .absolute {
  transform: translateY(100%);
}

.slide-up-enter-active .absolute,
.slide-up-leave-active .absolute {
  transition: transform 0.3s ease-out;
}

/* Safe area for mobile devices (iOS notch) */
.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom, 0px);
}

/* Smooth horizontal scrolling */
.scroll-smooth {
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}

/* 메인 콘텐츠 스크롤 영역: 바운스 방지 */
.overscroll-contain {
  overscroll-behavior: contain;
  -webkit-overflow-scrolling: touch;
}

/* 하단 네비게이션: 수평 스크롤만 허용, 수직 터치 전파 방지 */
.touch-pan-x {
  touch-action: pan-x;
  overscroll-behavior: none;
}

/* 메인 콘텐츠: 하단 네비바 + safe area 만큼 패딩 */
.main-content-area {
  padding-bottom: calc(4rem + env(safe-area-inset-bottom, 0px));
}
@media (min-width: 1024px) {
  .main-content-area {
    padding-bottom: 0;
  }
}
</style>
