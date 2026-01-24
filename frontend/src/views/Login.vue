<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600 dark:from-blue-700 dark:to-purple-800 px-4">
    <!-- Language Selector - Top Right -->
    <div class="absolute top-4 right-4 sm:top-6 sm:right-6">
      <select
        v-model="selectedLanguage"
        class="px-3 py-2 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm border border-white/20 dark:border-gray-700 rounded-lg text-sm text-gray-700 dark:text-gray-300 focus:ring-2 focus:ring-white/50 focus:border-transparent cursor-pointer hover:bg-white dark:hover:bg-gray-800 transition-all shadow-lg"
      >
        <option value="ko">🇰🇷 {{ t('auth.languageKorean') }}</option>
        <option value="en">🇺🇸 {{ t('auth.languageEnglish') }}</option>
      </select>
    </div>

    <div class="bg-white dark:bg-gray-800 p-6 sm:p-8 rounded-2xl shadow-2xl w-full max-w-md">
      <div class="text-center mb-6 sm:mb-8">
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-800 dark:text-white mb-2">MyApp Store</h1>
        <p class="text-sm sm:text-base text-gray-600 dark:text-gray-400">{{ t('auth.personalLibrary') }}</p>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('auth.username') }}</label>
          <input
            v-model="username"
            type="text"
            autocomplete="username"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            :placeholder="t('auth.usernamePlaceholder')"
            required
          />
        </div>

        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('auth.password') }}</label>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            :placeholder="t('auth.passwordPlaceholder')"
            required
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-500 dark:bg-blue-600 text-white py-2.5 sm:py-3 text-sm sm:text-base rounded-lg hover:bg-blue-600 dark:hover:bg-blue-700 transition-colors disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:cursor-not-allowed font-medium"
        >
          {{ loading ? t('auth.loggingIn') : t('auth.loginButton') }}
        </button>
      </form>

      <p v-if="error" class="text-red-500 dark:text-red-400 text-sm mt-4 text-center">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../store/auth'
import { useLocaleStore } from '../store/locale'
import { authApi } from '../api/auth'

const { t } = useI18n({ useScope: 'global' })

const router = useRouter()
const authStore = useAuthStore()
const localeStore = useLocaleStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

// Selected language (synced with localeStore)
const selectedLanguage = ref(localeStore.locale)

// Watch for language changes and apply immediately
watch(selectedLanguage, (newLocale) => {
  localeStore.setLocale(newLocale)
})

onMounted(async () => {
  // Apply saved language preference from localeStore
  localeStore.setLocale(localeStore.locale)

  // Check if setup is needed
  try {
    const response = await authApi.checkSetup()
    console.log('Setup check response:', response.data)
    if (response.data.needs_setup) {
      console.log('Redirecting to setup page...')
      router.push('/setup')
    }
  } catch (err) {
    console.error('Setup check failed:', err)
    // If it's a network error, might be initial setup - redirect to setup
    if (err.code === 'ERR_NETWORK' || err.message.includes('Network Error')) {
      console.log('Network error detected, redirecting to setup...')
      router.push('/setup')
    }
  }
})

const handleLogin = async () => {
  error.value = ''
  loading.value = true

  try {
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (err) {
    error.value = t('auth.loginFailed')
  } finally {
    loading.value = false
  }
}
</script>
