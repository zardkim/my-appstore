<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-500 to-blue-600 dark:from-green-700 dark:to-blue-800">
    <div class="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-2xl w-96">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800 dark:text-white mb-2">초기 설정</h1>
        <p class="text-gray-600 dark:text-gray-400">관리자 계정을 생성하세요</p>
      </div>

      <form @submit.prevent="handleSetup">
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">관리자 이름</label>
          <input
            v-model="username"
            type="text"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent"
            placeholder="admin"
            required
          />
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">비밀번호</label>
          <input
            v-model="password"
            type="password"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent"
            placeholder="8자 이상"
            required
            minlength="8"
          />
        </div>

        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">비밀번호 확인</label>
          <input
            v-model="passwordConfirm"
            type="password"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent"
            placeholder="비밀번호 재입력"
            required
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-green-500 text-white py-3 rounded-lg hover:bg-green-600 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
        >
          {{ loading ? '생성 중...' : '관리자 계정 생성' }}
        </button>
      </form>

      <p v-if="error" class="text-red-500 dark:text-red-400 text-sm mt-4 text-center">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../api/auth'
import { useDialog } from '../composables/useDialog'

const router = useRouter()
const { alert } = useDialog()

const username = ref('')
const password = ref('')
const passwordConfirm = ref('')
const error = ref('')
const loading = ref(false)

const handleSetup = async () => {
  error.value = ''

  if (password.value !== passwordConfirm.value) {
    error.value = '비밀번호가 일치하지 않습니다.'
    return
  }

  if (password.value.length < 8) {
    error.value = '비밀번호는 최소 8자 이상이어야 합니다.'
    return
  }

  loading.value = true

  try {
    await authApi.setup(username.value, password.value)
    await alert.success('관리자 계정이 생성되었습니다. 로그인 페이지로 이동합니다.')
    router.push('/login')
  } catch (err) {
    error.value = err.response?.data?.detail || '계정 생성에 실패했습니다.'
  } finally {
    loading.value = false
  }
}
</script>
