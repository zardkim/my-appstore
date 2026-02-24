<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
    <div class="w-full max-w-lg">

      <!-- 로고 / 브랜딩 -->
      <div class="text-center mb-6">
        <div class="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl mb-3 shadow-lg">
          <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
        </div>
        <p class="text-sm text-gray-500 dark:text-gray-400">MyApp Store</p>
      </div>

      <!-- 로딩 -->
      <div v-if="loading" class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 text-center">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-500 dark:text-gray-400 text-sm">{{ t('common.loading') }}</p>
      </div>

      <!-- 오류: 링크 없음 -->
      <div v-else-if="notFound" class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 text-center">
        <div class="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">{{ t('share.linkNotFound') }}</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('share.linkNotFoundDesc') }}</p>
      </div>

      <!-- 오류: 만료됨 -->
      <div v-else-if="pageInfo?.is_expired" class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 text-center">
        <div class="w-16 h-16 bg-orange-100 dark:bg-orange-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">{{ t('share.linkExpired') }}</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('share.linkExpiredDesc') }}</p>
        <p v-if="pageInfo?.expires_at" class="text-xs text-gray-400 dark:text-gray-500 mt-2">
          {{ t('share.expiredAt') }}: {{ formatDate(pageInfo.expires_at) }}
        </p>
      </div>

      <!-- 오류: 이미 사용됨 -->
      <div v-else-if="pageInfo?.is_used" class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 text-center">
        <div class="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">{{ t('share.alreadyUsed') }}</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('share.alreadyUsedDesc') }}</p>
      </div>

      <!-- 성공: 제품 정보 표시 -->
      <div v-else-if="productData" class="space-y-4">
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden">
          <!-- 제품 헤더 -->
          <div class="p-6 border-b border-gray-100 dark:border-gray-700">
            <div class="flex items-start gap-4">
              <img
                v-if="productData.icon_url"
                :src="productData.icon_url"
                class="w-16 h-16 rounded-xl object-cover flex-shrink-0 shadow"
                @error="e => e.target.style.display='none'"
              />
              <div v-else class="w-16 h-16 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900 dark:to-purple-900 rounded-xl flex items-center justify-center flex-shrink-0">
                <svg class="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <div class="min-w-0 flex-1">
                <h1 class="text-xl font-bold text-gray-900 dark:text-white">{{ productData.title }}</h1>
                <p v-if="productData.subtitle" class="text-sm text-gray-500 dark:text-gray-400">{{ productData.subtitle }}</p>
                <div class="flex flex-wrap gap-2 mt-2">
                  <span v-if="productData.vendor" class="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-2 py-0.5 rounded-full">{{ productData.vendor }}</span>
                  <span v-if="productData.license_type" class="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 px-2 py-0.5 rounded-full">{{ productData.license_type }}</span>
                  <span v-if="productData.platform" class="text-xs bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 px-2 py-0.5 rounded-full">{{ productData.platform }}</span>
                </div>
              </div>
            </div>
            <p v-if="productData.description" class="mt-4 text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{{ productData.description }}</p>
          </div>

          <!-- 버전 목록 -->
          <div class="p-6">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">{{ t('share.availableVersions') }}</h3>
            <div v-if="versions.length > 0" class="space-y-2">
              <div
                v-for="v in versions"
                :key="v.id"
                class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-xl"
              >
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ v.file_name }}</p>
                  <div class="flex items-center gap-3 mt-0.5">
                    <span v-if="v.version_name" class="text-xs text-blue-600 dark:text-blue-400">{{ v.version_name }}</span>
                    <span v-if="v.file_size" class="text-xs text-gray-400">{{ formatSize(v.file_size) }}</span>
                    <span v-if="v.is_portable" class="text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 px-1.5 py-0.5 rounded">Portable</span>
                  </div>
                </div>
              </div>
            </div>
            <p v-else class="text-sm text-gray-400 dark:text-gray-500">{{ t('common.noData') }}</p>
          </div>
        </div>

        <!-- 안내 메시지 -->
        <div class="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-xl text-sm text-blue-700 dark:text-blue-300 text-center">
          {{ t('share.sharedByInfo') }}
        </div>
      </div>

      <!-- 비밀번호 입력 화면 -->
      <div v-else-if="pageInfo" class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
        <!-- 제품 기본 정보 -->
        <div class="flex items-center gap-3 mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-xl">
          <img
            v-if="pageInfo.product_icon"
            :src="pageInfo.product_icon"
            class="w-12 h-12 rounded-lg object-cover flex-shrink-0"
            @error="e => e.target.style.display='none'"
          />
          <div v-else class="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center flex-shrink-0">
            <svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
          <div>
            <p class="font-semibold text-gray-900 dark:text-white">{{ pageInfo.product_title }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
              {{ t('share.expiresAt') }}: {{ formatDate(pageInfo.expires_at) }}
            </p>
          </div>
        </div>

        <h2 class="text-base font-semibold text-gray-900 dark:text-white mb-1">{{ t('share.enterPassword') }}</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">{{ t('share.enterPasswordDesc') }}</p>

        <div class="space-y-3">
          <input
            v-model="passwordInput"
            type="text"
            :placeholder="t('share.passwordPlaceholder')"
            class="w-full text-center text-lg font-mono tracking-widest bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl px-4 py-3 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            @keyup.enter="submitPassword"
            autocomplete="off"
          />

          <!-- 오류 메시지 -->
          <div v-if="accessError" class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg text-sm text-red-600 dark:text-red-400 text-center">
            <span v-if="accessError === 'invalid_password'">
              {{ t('share.invalidPassword') }}
              <span v-if="remainingAttempts !== null"> ({{ t('share.remainingAttempts', { n: remainingAttempts }) }})</span>
            </span>
            <span v-else-if="accessError === 'locked'">{{ t('share.locked') }}</span>
            <span v-else>{{ t('common.error') }}</span>
          </div>

          <button
            @click="submitPassword"
            :disabled="submitting || !passwordInput.trim()"
            class="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
          >
            <svg v-if="submitting" class="animate-spin w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {{ submitting ? t('common.loading') : t('share.accessProduct') }}
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { shareApi } from '../api/share'

const route = useRoute()
const { t } = useI18n({ useScope: 'global' })

const loading = ref(true)
const notFound = ref(false)
const pageInfo = ref(null)
const productData = ref(null)
const versions = ref([])

const passwordInput = ref('')
const submitting = ref(false)
const accessError = ref(null)
const remainingAttempts = ref(null)

const token = route.params.token

onMounted(async () => {
  try {
    const res = await shareApi.viewShare(token)
    pageInfo.value = res.data
  } catch (err) {
    if (err.response?.status === 404) {
      notFound.value = true
    } else {
      notFound.value = true
    }
  } finally {
    loading.value = false
  }
})

const submitPassword = async () => {
  if (submitting.value || !passwordInput.value.trim()) return
  submitting.value = true
  accessError.value = null
  try {
    const res = await shareApi.accessShare(token, passwordInput.value.trim())
    const data = res.data
    if (data.success) {
      productData.value = data.product
      versions.value = data.versions || []
    } else {
      accessError.value = data.error
      remainingAttempts.value = data.remaining_attempts ?? null
      if (data.error === 'expired') {
        pageInfo.value = { ...pageInfo.value, is_expired: true }
      } else if (data.error === 'already_used') {
        pageInfo.value = { ...pageInfo.value, is_used: true }
      }
    }
  } catch (err) {
    accessError.value = 'error'
  } finally {
    submitting.value = false
  }
}

const formatDate = (isoString) => {
  if (!isoString) return ''
  const d = new Date(isoString)
  return d.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const formatSize = (bytes) => {
  if (!bytes) return ''
  if (bytes >= 1073741824) return (bytes / 1073741824).toFixed(1) + ' GB'
  if (bytes >= 1048576) return (bytes / 1048576).toFixed(1) + ' MB'
  if (bytes >= 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return bytes + ' B'
}
</script>
