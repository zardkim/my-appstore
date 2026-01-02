<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600 dark:from-blue-700 dark:to-purple-800 px-4">
    <div class="bg-white dark:bg-gray-800 p-6 sm:p-8 rounded-2xl shadow-2xl w-full max-w-md">
      <div class="text-center mb-6 sm:mb-8">
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-800 dark:text-white mb-2">MyApp Store</h1>
        <p class="text-sm sm:text-base text-gray-600 dark:text-gray-400">개인용 소프트웨어 라이브러리</p>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">사용자 이름</label>
          <input
            v-model="username"
            type="text"
            autocomplete="username"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            placeholder="Username"
            required
          />
        </div>

        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">비밀번호</label>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            placeholder="Password"
            required
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-500 dark:bg-blue-600 text-white py-2.5 sm:py-3 text-sm sm:text-base rounded-lg hover:bg-blue-600 dark:hover:bg-blue-700 transition-colors disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:cursor-not-allowed font-medium"
        >
          {{ loading ? '로그인 중...' : '로그인' }}
        </button>
      </form>

      <p v-if="error" class="text-red-500 dark:text-red-400 text-sm mt-4 text-center">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { authApi } from '../api/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

onMounted(async () => {
  // Check if setup is needed
  try {
    const response = await authApi.checkSetup()
    if (response.data.needs_setup) {
      router.push('/setup')
    }
  } catch (err) {
    // Setup check failed - silently continue to login page
  }
})

const handleLogin = async () => {
  error.value = ''
  loading.value = true

  try {
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (err) {
    error.value = '로그인에 실패했습니다. 사용자 이름과 비밀번호를 확인하세요.'
  } finally {
    loading.value = false
  }
}
</script>
