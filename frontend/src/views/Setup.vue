<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-500 to-blue-600 dark:from-green-700 dark:to-blue-800">
    <!-- Language Selector - Top Right -->
    <div class="absolute top-4 right-4 sm:top-6 sm:right-6">
      <select
        v-model="selectedLanguage"
        class="px-3 py-2 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm border border-white/20 dark:border-gray-700 rounded-lg text-sm text-gray-700 dark:text-gray-300 focus:ring-2 focus:ring-white/50 focus:border-transparent cursor-pointer hover:bg-white dark:hover:bg-gray-800 transition-all shadow-lg"
      >
        <option value="auto">🌐 {{ t('auth.languageAuto') }}</option>
        <option value="ko">🇰🇷 {{ t('auth.languageKorean') }}</option>
        <option value="en">🇺🇸 {{ t('auth.languageEnglish') }}</option>
      </select>
    </div>

    <div class="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-2xl w-96">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800 dark:text-white mb-2">{{ t('setup.title') }}</h1>
        <p class="text-gray-600 dark:text-gray-400">{{ t('setup.subtitle') }}</p>
      </div>

      <form @submit.prevent="handleSetup">
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('setup.adminUsername') }}</label>
          <input
            v-model="username"
            type="text"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent"
            :placeholder="t('setup.usernamePlaceholder')"
            required
          />
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('setup.adminPassword') }}</label>
          <input
            v-model="password"
            type="password"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent"
            :placeholder="t('setup.passwordPlaceholder')"
            required
            minlength="8"
          />
        </div>

        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('setup.confirmPassword') }}</label>
          <input
            v-model="passwordConfirm"
            type="password"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent"
            :placeholder="t('setup.confirmPasswordPlaceholder')"
            required
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-green-500 text-white py-3 rounded-lg hover:bg-green-600 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
        >
          {{ loading ? t('setup.creating') : t('setup.createAccount') }}
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
import { authApi } from '../api/auth'
import { useDialog } from '../composables/useDialog'
import { useLocaleStore } from '../store/locale'

const { t } = useI18n({ useScope: 'global' })

const router = useRouter()
const { alert } = useDialog()
const localeStore = useLocaleStore()

const username = ref('')
const password = ref('')
const passwordConfirm = ref('')
const error = ref('')
const loading = ref(false)

// Selected language (synced with localeStore)
const selectedLanguage = ref(localeStore.locale)

// Watch for language changes and apply immediately
watch(selectedLanguage, (newLocale) => {
  localeStore.setLocale(newLocale)
})

onMounted(() => {
  // Apply saved language preference from localeStore
  localeStore.setLocale(localeStore.locale)
})

const handleSetup = async () => {
  error.value = ''

  if (password.value !== passwordConfirm.value) {
    error.value = t('setup.passwordMismatch')
    return
  }

  if (password.value.length < 8) {
    error.value = t('setup.passwordMismatch')
    return
  }

  loading.value = true

  try {
    await authApi.setup(username.value, password.value)
    await alert.success(t('setup.setupSuccess'))
    router.push('/login')
  } catch (err) {
    error.value = err.response?.data?.detail || t('setup.setupFailed')
  } finally {
    loading.value = false
  }
}
</script>
