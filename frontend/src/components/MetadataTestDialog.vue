<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50" @click.self="closeDialog">
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="sticky top-0 bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-4 flex items-center justify-between z-10">
        <h2 class="text-xl font-bold text-white flex items-center">
          <span class="mr-2">🤖</span>
          {{ t('metadataTest.title') }}
        </h2>
        <button
          @click="closeDialog"
          class="text-white hover:text-gray-200 transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 space-y-6">
        <!-- Input Section -->
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ t('metadataTest.softwareName') }}
            </label>
            <input
              v-model="softwareName"
              type="text"
              class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              :placeholder="t('metadataTest.softwareNamePlaceholder')"
              @keyup.enter="generateMetadata"
            />
          </div>

          <div class="space-y-3">
            <button
              @click="generateMetadata"
              :disabled="loading || !softwareName.trim()"
              class="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ loading ? t('metadataTest.analyzing') : t('metadataTest.generateMetadata') }}
            </button>

            <div class="grid grid-cols-2 gap-3">
              <button
                @click="showLogoSearchOnly"
                :disabled="!softwareName.trim()"
                class="px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {{ t('metadataTest.logoSearch') }}
              </button>

              <button
                @click="showScreenshotSearchOnly"
                :disabled="!softwareName.trim()"
                class="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-lg hover:from-purple-600 hover:to-pink-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {{ t('metadataTest.screenshotSearch') }}
              </button>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg text-red-700 dark:text-red-400">
          {{ errorMessage }}
        </div>

        <!-- AI Response Data -->
        <div v-if="metadata" class="space-y-6">
          <!-- Header with Icon and Provider Badge -->
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <h3 class="text-lg font-bold text-gray-900 dark:text-white">{{ t('metadataTest.aiResponseData') }}</h3>
              <div v-if="metadata.icon_url" class="flex items-center">
                <img
                  :src="metadata.icon_url"
                  :alt="metadata.title + ' 로고'"
                  class="w-12 h-12 object-contain rounded border border-gray-200 dark:border-gray-700"
                  @error="handleImageError($event)"
                />
              </div>
            </div>
            <span v-if="metadata.ai_provider" class="px-3 py-1 bg-indigo-100 dark:bg-indigo-900/50 text-indigo-800 dark:text-indigo-200 text-sm font-medium rounded-full">
              {{ metadata.ai_provider.toUpperCase() }}
            </span>
          </div>

          <!-- AI Response Values Table -->
          <div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider w-1/4">
                    {{ t('metadataTest.fieldName') }}
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    {{ t('metadataTest.value') }}
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="(value, key) in filteredMetadata" :key="key">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-200">
                    {{ key }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">
                    <div v-if="Array.isArray(value)" class="space-y-1">
                      <div v-for="(item, index) in value" :key="index" class="flex items-start">
                        <span class="text-blue-500 mr-2">•</span>
                        <span>{{ typeof item === 'object' ? JSON.stringify(item, null, 2) : item }}</span>
                      </div>
                      <span v-if="value.length === 0" class="text-gray-400 dark:text-gray-500">[ ]</span>
                    </div>
                    <!-- system_requirements 특별 처리 -->
                    <div v-else-if="key === 'system_requirements' && typeof value === 'object' && value !== null" class="space-y-2">
                      <div v-if="value.os" class="flex items-start">
                        <span class="font-semibold text-blue-600 dark:text-blue-400 min-w-[100px]">{{ t('metadataTest.sysReq.os') }}:</span>
                        <span class="flex-1">{{ value.os }}</span>
                      </div>
                      <div v-if="value.cpu" class="flex items-start">
                        <span class="font-semibold text-blue-600 dark:text-blue-400 min-w-[100px]">{{ t('metadataTest.sysReq.cpu') }}:</span>
                        <span class="flex-1">{{ value.cpu }}</span>
                      </div>
                      <div v-if="value.ram" class="flex items-start">
                        <span class="font-semibold text-blue-600 dark:text-blue-400 min-w-[100px]">{{ t('metadataTest.sysReq.ram') }}:</span>
                        <span class="flex-1">{{ value.ram }}</span>
                      </div>
                      <div v-if="value.disk_space" class="flex items-start">
                        <span class="font-semibold text-blue-600 dark:text-blue-400 min-w-[100px]">{{ t('metadataTest.sysReq.disk') }}:</span>
                        <span class="flex-1">{{ value.disk_space }}</span>
                      </div>
                      <div v-if="value.gpu" class="flex items-start">
                        <span class="font-semibold text-blue-600 dark:text-blue-400 min-w-[100px]">{{ t('metadataTest.sysReq.gpu') }}:</span>
                        <span class="flex-1">{{ value.gpu }}</span>
                      </div>
                      <div v-if="value.additional" class="flex items-start">
                        <span class="font-semibold text-blue-600 dark:text-blue-400 min-w-[100px]">{{ t('metadataTest.sysReq.additional') }}:</span>
                        <span class="flex-1">{{ value.additional }}</span>
                      </div>
                    </div>
                    <!-- installation_info 특별 처리 -->
                    <div v-else-if="key === 'installation_info' && typeof value === 'object' && value !== null" class="space-y-2">
                      <div v-if="value.installer_type" class="flex items-start">
                        <span class="font-semibold text-green-600 dark:text-green-400 min-w-[120px]">{{ t('metadataTest.installInfo.type') }}:</span>
                        <span class="flex-1">{{ value.installer_type }}</span>
                      </div>
                      <div v-if="value.file_size" class="flex items-start">
                        <span class="font-semibold text-green-600 dark:text-green-400 min-w-[120px]">{{ t('metadataTest.installInfo.fileSize') }}:</span>
                        <span class="flex-1">{{ value.file_size }}</span>
                      </div>
                      <div v-if="value.internet_required" class="flex items-start">
                        <span class="font-semibold text-green-600 dark:text-green-400 min-w-[120px]">{{ t('metadataTest.installInfo.internet') }}:</span>
                        <span class="flex-1">{{ value.internet_required }}</span>
                      </div>
                    </div>
                    <!-- 기타 객체 -->
                    <div v-else-if="typeof value === 'object' && value !== null" class="bg-gray-50 dark:bg-gray-900 rounded p-3 text-xs space-y-1">
                      <div v-for="(v, k) in value" :key="k" class="flex items-start">
                        <span class="font-semibold text-gray-600 dark:text-gray-400 mr-2">{{ k }}:</span>
                        <span class="flex-1">{{ typeof v === 'object' ? JSON.stringify(v) : v }}</span>
                      </div>
                    </div>
                    <span v-else-if="value === '' || value === null || value === undefined" class="text-gray-400 dark:text-gray-500">
                      {{ t('metadataTest.empty') }}
                    </span>
                    <span v-else class="whitespace-pre-wrap">{{ value }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Original AI Response -->
          <div v-if="metadata.ai_raw_response" class="mt-6">
            <details class="border border-indigo-200 dark:border-indigo-700 rounded-lg bg-indigo-50 dark:bg-indigo-900/20">
              <summary class="px-4 py-3 cursor-pointer font-medium text-gray-900 dark:text-white hover:bg-indigo-100 dark:hover:bg-indigo-900/30 rounded-lg transition-colors">
                🔍 {{ t('metadataTest.viewOriginalResponse') }}
              </summary>
              <div class="p-4 border-t border-indigo-200 dark:border-indigo-700">
                <pre class="p-4 bg-gray-900 dark:bg-black text-gray-100 rounded-lg overflow-x-auto text-xs leading-relaxed">{{ metadata.ai_raw_response }}</pre>
              </div>
            </details>
          </div>

          <!-- Full JSON -->
          <div class="mt-4">
            <details class="border border-gray-300 dark:border-gray-600 rounded-lg">
              <summary class="px-4 py-3 cursor-pointer font-medium text-gray-900 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                📋 {{ t('metadataTest.viewFullJson') }}
              </summary>
              <div class="p-4 border-t border-gray-300 dark:border-gray-600">
                <pre class="p-4 bg-gray-900 dark:bg-black text-gray-100 rounded-lg overflow-x-auto text-xs">{{ JSON.stringify(metadata, null, 2) }}</pre>
              </div>
            </details>
          </div>

          <!-- Image Manager (메타데이터 생성 후 - 직접 업로드 제외) -->
          <ImageManager
            v-if="testProductId && metadata"
            key="metadata-mode"
            :product-id="testProductId"
            :product="metadata"
            :initial-search-query="softwareName"
            :visible-tabs="['logo', 'screenshot', 'current']"
            @update:logo="handleLogoUpdate"
            @update:screenshots="handleScreenshotsUpdate"
          />
        </div>

        <!-- Logo Search Only Mode -->
        <div v-if="showImageSearchMode === 'logo' && !metadata" class="space-y-6">
          <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-4">
            <div class="flex items-start">
              <svg class="w-6 h-6 text-blue-600 dark:text-blue-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <div>
                <h3 class="text-sm font-semibold text-blue-900 dark:text-blue-400">{{ t('metadataTest.logoSearchMode') }}</h3>
                <p class="text-sm text-blue-800 dark:text-blue-300 mt-1">
                  {{ t('metadataTest.searchKeyword') }}: <strong>{{ softwareName }}</strong>
                </p>
                <p class="text-xs text-blue-700 dark:text-blue-400 mt-1">
                  {{ t('metadataTest.logoSearchDesc') }}
                </p>
              </div>
            </div>
          </div>

          <ImageManager
            key="logo-search-only-mode"
            :product-id="testProductId"
            :product="{ title: softwareName }"
            :initial-search-query="softwareName"
            default-tab="logo"
            :visible-tabs="['logo']"
            @update:logo="handleLogoUpdate"
            @update:screenshots="handleScreenshotsUpdate"
            :test-mode="true"
          />
        </div>

        <!-- Screenshot Search Only Mode -->
        <div v-if="showImageSearchMode === 'screenshot' && !metadata" class="space-y-6">
          <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-700 rounded-lg p-4">
            <div class="flex items-start">
              <svg class="w-6 h-6 text-purple-600 dark:text-purple-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <div>
                <h3 class="text-sm font-semibold text-purple-900 dark:text-purple-400">{{ t('metadataTest.screenshotSearchMode') }}</h3>
                <p class="text-sm text-purple-800 dark:text-purple-300 mt-1">
                  {{ t('metadataTest.searchKeyword') }}: <strong>{{ softwareName }}</strong>
                </p>
                <p class="text-xs text-purple-700 dark:text-purple-400 mt-1">
                  {{ t('metadataTest.screenshotSearchDesc') }}
                </p>
              </div>
            </div>
          </div>

          <ImageManager
            key="screenshot-search-only-mode"
            :product-id="testProductId"
            :product="{ title: softwareName }"
            :initial-search-query="softwareName"
            default-tab="screenshot"
            :visible-tabs="['screenshot']"
            @update:logo="handleLogoUpdate"
            @update:screenshots="handleScreenshotsUpdate"
            :test-mode="true"
          />
        </div>
      </div>

      <!-- Footer -->
      <div class="sticky bottom-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-6 py-4">
        <button
          @click="closeDialog"
          class="w-full px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium"
        >
          {{ t('metadataTest.close') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { metadataApi } from '../api/metadata'
import { configApi } from '../api/config'
import ImageManager from './ImageManager.vue'

const { t } = useI18n({ useScope: 'global' })

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['close'])

// State
const softwareName = ref('')
const loading = ref(false)
const errorMessage = ref('')
const metadata = ref(null)
const testProductId = ref(999999)  // Temporary product ID for testing
const showImageSearchMode = ref(null)  // 이미지 검색 모드: null, 'logo', 'screenshot'

// 메타데이터 설정
const aiProvider = ref('gemini')
const aiModel = ref('gemini-2.5-flash')
const geminiApiKey = ref('')
const openaiApiKey = ref('')
const useCustomPrompt = ref(false)
const customPromptOpenai = ref('')
const customPromptGemini = ref('')

// 설정 로드
onMounted(async () => {
  try {
    const response = await configApi.getSection('metadata')
    if (response.data) {
      aiProvider.value = response.data.aiProvider || 'gemini'
      aiModel.value = response.data.aiModel || 'gemini-2.5-flash'
      geminiApiKey.value = response.data.geminiApiKey || ''
      openaiApiKey.value = response.data.openaiApiKey || ''
      useCustomPrompt.value = response.data.useCustomPrompt || false
      customPromptOpenai.value = response.data.customPromptOpenai || ''
      customPromptGemini.value = response.data.customPromptGemini || ''
    }
  } catch (error) {
    console.error('설정 로드 오류:', error)
  }
})

// AI 내부 필드 제외하고 필터링
const filteredMetadata = computed(() => {
  if (!metadata.value) return {}

  const filtered = {}
  const excludeKeys = ['ai_raw_response', 'ai_provider', 'parsed_info', 'confidence', 'crawl_info', 'screenshots']

  for (const [key, value] of Object.entries(metadata.value)) {
    if (!excludeKeys.includes(key)) {
      filtered[key] = value
    }
  }

  return filtered
})

// 로고 검색만 표시
const showLogoSearchOnly = () => {
  if (!softwareName.value.trim()) {
    errorMessage.value = t('metadataTest.errors.enterSoftwareName')
    return
  }

  showImageSearchMode.value = 'logo'
  metadata.value = null
  errorMessage.value = ''
}

// 스크린샷 검색만 표시
const showScreenshotSearchOnly = () => {
  if (!softwareName.value.trim()) {
    errorMessage.value = t('metadataTest.errors.enterSoftwareName')
    return
  }

  showImageSearchMode.value = 'screenshot'
  metadata.value = null
  errorMessage.value = ''
}

// 메타데이터 생성
const generateMetadata = async () => {
  if (!softwareName.value.trim()) {
    errorMessage.value = t('metadataTest.errors.enterSoftwareName')
    return
  }

  loading.value = true
  errorMessage.value = ''
  metadata.value = null
  showImageSearchMode.value = null

  try {
    // 설정을 다시 확인 (최신 설정 반영)
    const configResponse = await configApi.getSection('metadata')
    if (configResponse.data) {
      aiProvider.value = configResponse.data.aiProvider || 'gemini'
      aiModel.value = configResponse.data.aiModel || 'gemini-2.5-flash'
      geminiApiKey.value = configResponse.data.geminiApiKey || ''
      openaiApiKey.value = configResponse.data.openaiApiKey || ''
      useCustomPrompt.value = configResponse.data.useCustomPrompt || false
      customPromptOpenai.value = configResponse.data.customPromptOpenai || ''
      customPromptGemini.value = configResponse.data.customPromptGemini || ''
    }

    // 현재 provider에 맞는 커스텀 프롬프트 선택
    const customPrompt = aiProvider.value === 'openai' ? customPromptOpenai.value : customPromptGemini.value

    // 메타데이터 생성 요청
    const response = await metadataApi.testGeneration(
      softwareName.value.trim(),
      {
        aiProvider: aiProvider.value,
        aiModel: aiModel.value,
        geminiApiKey: geminiApiKey.value,
        openaiApiKey: openaiApiKey.value,
        useCustomPrompt: useCustomPrompt.value,
        customPrompt: useCustomPrompt.value ? customPrompt : null
      }
    )

    if (response.data.success) {
      if (response.data.metadata) {
        metadata.value = response.data.metadata
      } else {
        errorMessage.value = t('metadataTest.errors.metadataNotFound')
      }
    } else {
      errorMessage.value = response.data.error || t('metadataTest.errors.generationFailed')
    }
  } catch (error) {
    console.error('메타데이터 생성 오류:', error)
    if (error.response?.status === 403) {
      errorMessage.value = t('metadataTest.errors.noPermission')
    } else {
      errorMessage.value = t('metadataTest.errors.generationError')
    }
  } finally {
    loading.value = false
  }
}

// 이미지 관련 함수
const openImageInNewTab = (url) => {
  window.open(url, '_blank')
}

const handleImageError = (event) => {
  event.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="150"%3E%3Crect fill="%23f0f0f0" width="200" height="150"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%23999"%3E이미지 없음%3C/text%3E%3C/svg%3E'
}

// Helper function to convert full URL to relative path
const toRelativePath = (url) => {
  if (!url) return url
  if (url.includes('/static/')) {
    const afterStatic = url.split('/static/')[1].split('?')[0]
    return '/static/' + afterStatic
  }
  return url
}

// Image update handlers
const handleLogoUpdate = (iconUrl) => {
  const relativePath = toRelativePath(iconUrl)
  console.log('[MetadataTestDialog] handleLogoUpdate called with:', relativePath)

  // 이미지 검색 전용 모드일 때 metadata 객체 생성
  if (!metadata.value && showImageSearchMode.value) {
    metadata.value = {
      title: softwareName.value,
      icon_url: relativePath,
      screenshots: []
    }
    console.log('[MetadataTestDialog] Created new metadata object')
  } else if (metadata.value) {
    // 기존 객체 업데이트 - 반응성 유지를 위해 전체 재할당
    metadata.value = {
      ...metadata.value,
      icon_url: relativePath
    }
    console.log('[MetadataTestDialog] Updated existing metadata object')
  }

  console.log('[MetadataTestDialog] Updated metadata.value:', JSON.stringify(metadata.value, null, 2))
}

const handleScreenshotsUpdate = (screenshots) => {
  // Convert full URLs to relative paths
  const normalizedScreenshots = screenshots.map(s => {
    if (typeof s === 'string') {
      return { type: 'local', url: toRelativePath(s) }
    } else {
      return { ...s, url: toRelativePath(s.url) }
    }
  })

  console.log('[MetadataTestDialog] handleScreenshotsUpdate called with:', normalizedScreenshots)

  // 이미지 검색 전용 모드일 때 metadata 객체 생성
  if (!metadata.value && showImageSearchMode.value) {
    metadata.value = {
      title: softwareName.value,
      icon_url: null,
      screenshots: normalizedScreenshots
    }
    console.log('[MetadataTestDialog] Created new metadata object with screenshots')
  } else if (metadata.value) {
    // 기존 객체 업데이트 - 반응성 유지를 위해 전체 재할당
    metadata.value = {
      ...metadata.value,
      screenshots: normalizedScreenshots
    }
    console.log('[MetadataTestDialog] Updated existing metadata object with screenshots')
  }

  console.log('[MetadataTestDialog] Updated metadata.value:', JSON.stringify(metadata.value, null, 2))
}

const closeDialog = () => {
  softwareName.value = ''
  metadata.value = null
  errorMessage.value = ''
  showImageSearchMode.value = null
  emit('close')
}
</script>
