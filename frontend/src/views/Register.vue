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
        <p class="text-gray-600 dark:text-gray-400">초대를 받아 회원가입하세요</p>
      </div>

      <!-- Invitation Info (if code is valid) -->
      <div v-if="invitationInfo && invitationInfo.is_valid" class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-xl p-4 mb-6">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-blue-600 dark:text-blue-400 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <div class="text-sm text-blue-800 dark:text-blue-300">
            <p class="font-semibold">초대장 확인됨</p>
            <p class="mt-1">{{ invitationInfo.email }}님을 위한 초대장입니다.</p>
          </div>
        </div>
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
        <p class="text-gray-600 dark:text-gray-400">초대장을 확인하는 중...</p>
      </div>

      <!-- Invalid/Expired Invitation -->
      <div v-else-if="!invitationInfo || !invitationInfo.is_valid" class="text-center py-8">
        <svg class="w-16 h-16 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-2">유효하지 않은 초대 코드</h2>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          초대 코드가 유효하지 않거나 만료되었습니다.<br/>
          관리자에게 새로운 초대를 요청하세요.
        </p>
        <router-link
          to="/login"
          class="inline-block px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all shadow-md font-medium"
        >
          로그인 페이지로 이동
        </router-link>
      </div>

      <!-- Registration Form -->
      <form v-else @submit.prevent="register" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">사용자명</label>
          <input
            v-model="username"
            type="text"
            required
            minlength="3"
            maxlength="50"
            placeholder="사용자명을 입력하세요"
            class="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
          />
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">3-50자 사이로 입력해주세요</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">비밀번호</label>
          <input
            v-model="password"
            type="password"
            required
            minlength="8"
            placeholder="비밀번호를 입력하세요"
            class="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
          />
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">최소 8자 이상 입력해주세요</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">비밀번호 확인</label>
          <input
            v-model="passwordConfirm"
            type="password"
            required
            minlength="8"
            placeholder="비밀번호를 다시 입력하세요"
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
          {{ registering ? '회원가입 중...' : '회원가입' }}
        </button>

        <div class="text-center">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            이미 계정이 있으신가요?
            <router-link to="/login" class="text-blue-600 dark:text-blue-400 hover:underline font-medium">로그인</router-link>
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { invitationsApi } from '../api/invitations'
import { useDialog } from '../composables/useDialog'

const router = useRouter()
const route = useRoute()
const { alert } = useDialog()

const invitationCode = ref('')
const invitationInfo = ref(null)
const loading = ref(true)
const registering = ref(false)
const error = ref('')

const username = ref('')
const password = ref('')
const passwordConfirm = ref('')

onMounted(async () => {
  // Get invitation code from URL query parameter
  invitationCode.value = route.query.code

  if (!invitationCode.value) {
    error.value = '초대 코드가 제공되지 않았습니다.'
    loading.value = false
    return
  }

  // Verify invitation code
  try {
    invitationInfo.value = await invitationsApi.verify(invitationCode.value)

    if (!invitationInfo.value.is_valid) {
      error.value = '초대 코드가 유효하지 않거나 만료되었습니다.'
    }
  } catch (err) {
    console.error('초대 코드 확인 오류:', err)
    error.value = '초대 코드 확인 중 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
})

const register = async () => {
  error.value = ''

  // Validate
  if (password.value !== passwordConfirm.value) {
    error.value = '비밀번호가 일치하지 않습니다.'
    return
  }

  if (password.value.length < 8) {
    error.value = '비밀번호는 최소 8자 이상이어야 합니다.'
    return
  }

  if (username.value.length < 3) {
    error.value = '사용자명은 최소 3자 이상이어야 합니다.'
    return
  }

  try {
    registering.value = true
    await invitationsApi.register(invitationCode.value, username.value, password.value)

    await alert.success('회원가입이 완료되었습니다!\n로그인 페이지로 이동합니다.')
    router.push('/login')
  } catch (err) {
    console.error('회원가입 오류:', err)
    error.value = err.response?.data?.detail || '회원가입에 실패했습니다.'
  } finally {
    registering.value = false
  }
}
</script>
