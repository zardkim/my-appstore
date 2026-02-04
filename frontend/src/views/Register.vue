<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 flex items-center justify-center p-4">
    <div class="bg-white dark:bg-gray-800 rounded-3xl shadow-2xl p-8 w-full max-w-md">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl shadow-lg mb-4">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">MyApp Store</h1>
        <p class="text-gray-600 dark:text-gray-400">{{ t('register.subtitle') }}</p>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-xl p-4 mb-6">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-red-600 dark:text-red-400 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-sm text-red-800 dark:text-red-300">{{ error }}</p>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
        <p class="text-gray-600 dark:text-gray-400">{{ t('register.checkingStatus') }}</p>
      </div>

      <!-- Registration Closed -->
      <div v-else-if="!registrationOpen" class="text-center py-8">
        <svg class="w-16 h-16 text-yellow-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-2">{{ t('register.registrationClosed') }}</h2>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          {{ t('register.registrationClosedDesc') }}
        </p>
        <router-link
          to="/login"
          class="inline-block px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all shadow-md font-medium"
        >
          {{ t('register.goToLogin') }}
        </router-link>
      </div>

      <!-- Registration Form -->
      <form v-else @submit.prevent="register" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('register.username') }}</label>
          <input
            v-model="username"
            type="text"
            required
            minlength="3"
            maxlength="20"
            :placeholder="t('register.usernamePlaceholder')"
            class="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
          />
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">{{ t('register.usernameHint') }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('register.email') }}</label>
          <input
            v-model="email"
            type="email"
            required
            :placeholder="t('register.emailPlaceholder')"
            class="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('register.password') }}</label>
          <input
            v-model="password"
            type="password"
            required
            minlength="8"
            :placeholder="t('register.passwordPlaceholder')"
            class="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
          />
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">{{ t('register.passwordHint') }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('register.passwordConfirm') }}</label>
          <input
            v-model="passwordConfirm"
            type="password"
            required
            minlength="8"
            :placeholder="t('register.passwordConfirmPlaceholder')"
            class="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
          />
        </div>

        <button
          type="submit"
          :disabled="registering"
          class="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all shadow-lg font-medium text-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          <svg v-if="registering" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ registering ? t('register.registering') : t('register.registerButton') }}
        </button>

        <div class="text-center">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ t('register.haveAccount') }}
            <router-link to="/login" class="text-blue-600 dark:text-blue-400 hover:underline font-medium">{{ t('register.login') }}</router-link>
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { authApi } from '../api/auth'
import { useDialog } from '../composables/useDialog'

const { t } = useI18n()
const router = useRouter()
const { alert } = useDialog()

const registrationOpen = ref(false)
const loading = ref(true)
const registering = ref(false)
const error = ref('')

const username = ref('')
const email = ref('')
const password = ref('')
const passwordConfirm = ref('')

onMounted(async () => {
  // Check if registration is open
  try {
    const response = await authApi.getRegistrationStatus()
    registrationOpen.value = response.data.registration_open
  } catch (err) {
    console.error('Failed to check registration status:', err)
    error.value = t('register.statusCheckFailed')
  } finally {
    loading.value = false
  }
})

const register = async () => {
  error.value = ''

  // Validate username (alphanumeric and underscore only)
  const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/
  if (!usernameRegex.test(username.value)) {
    error.value = t('register.invalidUsername')
    return
  }

  // Validate email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.value)) {
    error.value = t('register.invalidEmail')
    return
  }

  // Validate password
  if (password.value.length < 8) {
    error.value = t('register.passwordTooShort')
    return
  }

  if (password.value !== passwordConfirm.value) {
    error.value = t('register.passwordMismatch')
    return
  }

  try {
    registering.value = true
    await authApi.register(username.value, password.value, email.value)

    await alert.success(t('register.success'))
    router.push('/login')
  } catch (err) {
    console.error('Registration error:', err)
    error.value = err.response?.data?.detail || t('register.failed')
  } finally {
    registering.value = false
  }
}
</script>
