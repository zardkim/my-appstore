<template>
  <div class="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-8 py-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">비밀번호 변경</h1>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">보안을 위해 주기적으로 비밀번호를 변경해주세요</p>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto px-8 py-6">
      <div class="max-w-2xl mx-auto">
        <!-- Change Password Form -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-8">
          <form @submit.prevent="handleChangePassword" class="space-y-6">
            <!-- Current Password -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                현재 비밀번호 *
              </label>
              <input
                v-model="form.currentPassword"
                type="password"
                required
                class="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                placeholder="현재 비밀번호를 입력하세요"
              />
            </div>

            <!-- New Password -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                새 비밀번호 *
              </label>
              <input
                v-model="form.newPassword"
                type="password"
                required
                minlength="8"
                class="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                placeholder="새 비밀번호를 입력하세요 (최소 8자)"
              />
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">비밀번호는 최소 8자 이상이어야 합니다</p>
            </div>

            <!-- Confirm New Password -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                새 비밀번호 확인 *
              </label>
              <input
                v-model="form.confirmPassword"
                type="password"
                required
                class="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                placeholder="새 비밀번호를 다시 입력하세요"
              />
            </div>

            <!-- Error Message -->
            <div v-if="errorMessage" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-xl p-4">
              <div class="flex items-start">
                <svg class="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="text-sm text-red-800 dark:text-red-300">{{ errorMessage }}</p>
              </div>
            </div>

            <!-- Success Message -->
            <div v-if="successMessage" class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-xl p-4">
              <div class="flex items-start">
                <svg class="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="text-sm text-green-800 dark:text-green-300">{{ successMessage }}</p>
              </div>
            </div>

            <!-- Security Notice -->
            <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-xl p-4">
              <div class="flex items-start">
                <svg class="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="text-sm text-blue-800 dark:text-blue-300">
                  <p class="font-medium mb-1">비밀번호 보안 팁</p>
                  <ul class="list-disc list-inside space-y-1 text-blue-700 dark:text-blue-300">
                    <li>추측하기 어려운 비밀번호를 사용하세요</li>
                    <li>다른 서비스와 다른 비밀번호를 사용하세요</li>
                    <li>주기적으로 비밀번호를 변경하세요</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Buttons -->
            <div class="flex space-x-3">
              <button
                type="button"
                @click="goBack"
                class="flex-1 px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 font-medium transition-colors"
              >
                취소
              </button>
              <button
                type="submit"
                :disabled="loading"
                class="flex-1 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 shadow-md font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="loading">변경 중...</span>
                <span v-else>비밀번호 변경</span>
              </button>
            </div>
          </form>
        </div>

        <!-- Additional Info -->
        <div class="mt-6 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-xl p-4">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p class="text-sm text-yellow-800 dark:text-yellow-300">
              비밀번호를 변경하면 모든 디바이스에서 자동으로 로그아웃됩니다. 새로운 비밀번호로 다시 로그인해야 합니다.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const form = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const errorMessage = ref('')
const successMessage = ref('')
const loading = ref(false)

const goBack = () => {
  router.go(-1)
}

const handleChangePassword = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  // Validation
  if (form.value.newPassword !== form.value.confirmPassword) {
    errorMessage.value = '새 비밀번호가 일치하지 않습니다.'
    return
  }

  if (form.value.newPassword.length < 8) {
    errorMessage.value = '비밀번호는 최소 8자 이상이어야 합니다.'
    return
  }

  if (form.value.currentPassword === form.value.newPassword) {
    errorMessage.value = '현재 비밀번호와 새 비밀번호가 동일합니다.'
    return
  }

  loading.value = true

  try {
    await axios.post('/api/auth/change-password', {
      current_password: form.value.currentPassword,
      new_password: form.value.newPassword
    })

    successMessage.value = '비밀번호가 성공적으로 변경되었습니다.'

    // Reset form
    form.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    }

    // Redirect to home after 2 seconds
    setTimeout(() => {
      router.push('/')
    }, 2000)
  } catch (error) {
    if (error.response?.status === 401) {
      errorMessage.value = '현재 비밀번호가 올바르지 않습니다.'
    } else {
      errorMessage.value = '비밀번호 변경에 실패했습니다. 다시 시도해주세요.'
    }
  } finally {
    loading.value = false
  }
}
</script>
