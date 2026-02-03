<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 overflow-y-auto"
    @click.self="close"
  >
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div
        class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75 dark:bg-gray-900 dark:bg-opacity-75"
        @click="close"
      ></div>

      <!-- Modal content -->
      <div class="inline-block w-full max-w-4xl my-8 overflow-hidden text-left align-middle transition-all transform bg-white dark:bg-gray-800 shadow-2xl rounded-2xl">
        <!-- Header -->
        <div class="bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-4">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-bold text-white flex items-center gap-2">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              {{ t('violationAISearchDialog.title') }}
            </h3>
            <button
              @click="close"
              class="text-white hover:text-gray-200 transition-colors p-2 hover:bg-white/10 rounded-lg"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Body -->
        <div class="px-6 py-6 max-h-[calc(100vh-200px)] overflow-y-auto">
          <!-- Violation Info -->
          <div class="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg space-y-2">
            <p class="text-sm text-blue-900 dark:text-blue-300">
              <strong>{{ t('violationAISearchDialog.searchTarget') }}:</strong> {{ softwareName }}
            </p>
            <p class="text-xs text-blue-700 dark:text-blue-400">
              <strong>{{ t('violationAISearchDialog.folder') }}:</strong> {{ violation?.folder_path || '' }}
            </p>
            <p class="text-xs text-blue-700 dark:text-blue-400">
              <strong>{{ t('violationAISearchDialog.file') }}:</strong> {{ violation?.file_name || '' }}
            </p>
          </div>

          <!-- Loading -->
          <div v-if="loading" class="flex flex-col items-center justify-center py-12">
            <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 dark:border-blue-400 mb-4"></div>
            <p class="text-gray-600 dark:text-gray-400">{{ t('violationAISearchDialog.generating') }}</p>
            <p class="text-sm text-gray-500 dark:text-gray-500 mt-2">{{ t('violationAISearchDialog.maxTime') }}</p>
          </div>

          <!-- Error -->
          <div v-else-if="errorMessage" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg text-red-700 dark:text-red-400">
            {{ errorMessage }}
          </div>

          <!-- Success - Metadata Display -->
          <div v-else-if="metadata" class="space-y-6">
            <div class="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-lg text-green-700 dark:text-green-400 text-sm">
              ✓ {{ t('violationAISearchDialog.generationComplete') }}
            </div>

            <!-- Metadata Table -->
            <div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
              <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead class="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase w-1/4">{{ t('violationAISearchDialog.field') }}</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">{{ t('violationAISearchDialog.value') }}</th>
                  </tr>
                </thead>
                <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  <tr v-for="(value, key) in filteredMetadata" :key="key">
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-200">
                      {{ key }}
                    </td>
                    <td class="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">
                      <!-- Array values -->
                      <div v-if="Array.isArray(value)" class="space-y-1">
                        <div v-for="(item, index) in value" :key="index" class="flex items-start">
                          <span class="text-blue-500 mr-2">•</span>
                          <span>{{ typeof item === 'object' ? JSON.stringify(item) : item }}</span>
                        </div>
                        <span v-if="value.length === 0" class="text-gray-400">[ ]</span>
                      </div>
                      <!-- Objects -->
                      <div v-else-if="typeof value === 'object' && value !== null" class="bg-gray-50 dark:bg-gray-900 rounded p-3 text-xs">
                        <div v-for="(v, k) in value" :key="k" class="flex items-start">
                          <span class="font-semibold text-gray-600 dark:text-gray-400 mr-2">{{ k }}:</span>
                          <span>{{ typeof v === 'object' ? JSON.stringify(v) : v }}</span>
                        </div>
                      </div>
                      <!-- Empty values -->
                      <span v-else-if="value === '' || value === null" class="text-gray-400">{{ t('violationAISearchDialog.empty') }}</span>
                      <!-- Normal values -->
                      <span v-else>{{ value }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Image Manager -->
            <ImageManager
              v-if="metadata"
              :product-id="999999"
              :product="metadata"
              :initial-search-query="aiSearchQuery"
              @update:logo="handleLogoUpdate"
              @update:screenshots="handleScreenshotsUpdate"
            />
          </div>

          <!-- Initial state -->
          <div v-else class="text-center py-12">
            <svg class="w-16 h-16 mx-auto mb-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <p class="text-gray-600 dark:text-gray-400 mb-4">{{ t('violationAISearchDialog.startSearch') }}</p>
            <button
              @click="startAISearch"
              class="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-colors font-medium"
            >
              {{ t('violationAISearchDialog.startButton') }}
            </button>
          </div>
        </div>

        <!-- Footer -->
        <div class="sticky bottom-0 bg-gray-50 dark:bg-gray-700 px-6 py-4 border-t border-gray-200 dark:border-gray-600 flex justify-between gap-3">
          <button
            @click="close"
            class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors"
          >
            {{ t('violationAISearchDialog.cancel') }}
          </button>
          <button
            v-if="metadata"
            @click="saveMetadata"
            :disabled="saving"
            class="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ saving ? t('violationAISearchDialog.saving') : t('violationAISearchDialog.createAndMatch') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { metadataApi } from '../../api/metadata'
import { filenameViolationsApi } from '../../api/filenameViolations'
import { configApi } from '../../api/config'
import ImageManager from '../ImageManager.vue'
import { useDialog } from '../../composables/useDialog'

const { t } = useI18n({ useScope: 'global' })
const { alert } = useDialog()

const props = defineProps({
  violation: {
    type: Object,
    default: null
  },
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const metadata = ref(null)

// AI 설정
const aiProvider = ref('gemini')
const aiModel = ref('gemini-2.5-flash')
const geminiApiKey = ref('')
const openaiApiKey = ref('')
const useCustomPrompt = ref(false)
const customPromptOpenai = ref('')
const customPromptGemini = ref('')

// 소프트웨어 이름 추출 (폴더명 사용)
const softwareName = computed(() => {
  if (!props.violation?.folder_path) return ''
  const parts = props.violation.folder_path.split('/')
  return parts[parts.length - 1] || ''
})

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

// Auto-start AI search when dialog opens
watch(() => props.isOpen, (isOpen) => {
  if (isOpen && softwareName.value && !metadata.value) {
    startAISearch()
  }
})

// AI 결과의 title + 주요 버전으로 이미지 검색어 구성
const aiSearchQuery = computed(() => {
  if (!metadata.value) return softwareName.value
  const title = metadata.value.title || softwareName.value
  const version = metadata.value.parsed_info?.version || ''
  // 주요 버전만 사용 (v16.0.0 → v16)
  const majorVersion = version.replace(/^(v?\d+).*/, '$1')
  return majorVersion ? `${title} ${majorVersion}` : title
})

const filteredMetadata = computed(() => {
  if (!metadata.value) return {}

  const filtered = {}
  const excludeKeys = ['ai_raw_response', 'ai_provider', 'parsed_info', 'confidence', 'crawl_info', 'screenshots', 'icon_url']

  for (const [key, value] of Object.entries(metadata.value)) {
    if (!excludeKeys.includes(key)) {
      filtered[key] = value
    }
  }

  return filtered
})

const startAISearch = async () => {
  if (!softwareName.value) {
    errorMessage.value = t('violationAISearchDialog.noSoftwareName')
    return
  }

  loading.value = true
  errorMessage.value = ''
  metadata.value = null

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
        errorMessage.value = t('violationAISearchDialog.metadataNotFound')
      }
    } else {
      errorMessage.value = response.data.error || t('violationAISearchDialog.generateFailed')
    }
  } catch (error) {
    console.error('AI search error:', error)
    if (error.response?.status === 403) {
      errorMessage.value = t('violationAISearchDialog.noPermission')
    } else {
      errorMessage.value = t('violationAISearchDialog.searchError')
    }
  } finally {
    loading.value = false
  }
}

const saveMetadata = async () => {
  if (!metadata.value || !props.violation?.id) return

  saving.value = true
  errorMessage.value = '' // 이전 에러 초기화

  try {
    // 값이 있는지 확인하는 헬퍼 함수
    const hasValue = (value) => {
      if (value === null || value === undefined) return false
      if (typeof value === 'string') return value.trim().length > 0
      if (Array.isArray(value)) return value.length > 0
      if (typeof value === 'object') return Object.keys(value).length > 0
      return true
    }

    // AI 메타데이터 필드명 → 백엔드 스키마 필드명 매핑 (빈 값 제거)
    const mappedMetadata = {}

    // 기본 필드
    if (hasValue(metadata.value.title)) mappedMetadata.title = metadata.value.title
    if (hasValue(metadata.value.subtitle)) mappedMetadata.subtitle = metadata.value.subtitle
    if (hasValue(metadata.value.category)) mappedMetadata.category = metadata.value.category
    if (hasValue(metadata.value.icon_url)) mappedMetadata.icon_url = metadata.value.icon_url

    // AI: description_short → Backend: description
    const description = metadata.value.description_short || metadata.value.description
    if (hasValue(description)) mappedMetadata.description = description

    // AI: developer → Backend: vendor
    const vendor = metadata.value.developer || metadata.value.vendor
    if (hasValue(vendor)) mappedMetadata.vendor = vendor

    // AI: description_detailed → Backend: detailed_description
    const detailedDesc = metadata.value.description_detailed || metadata.value.detailed_description
    if (hasValue(detailedDesc)) mappedMetadata.detailed_description = detailedDesc

    // 확장 필드
    if (hasValue(metadata.value.official_website)) mappedMetadata.official_website = metadata.value.official_website
    if (hasValue(metadata.value.license_type)) mappedMetadata.license_type = metadata.value.license_type
    if (hasValue(metadata.value.platform)) mappedMetadata.platform = metadata.value.platform
    if (hasValue(metadata.value.features)) mappedMetadata.features = metadata.value.features
    if (hasValue(metadata.value.system_requirements)) mappedMetadata.system_requirements = metadata.value.system_requirements
    if (hasValue(metadata.value.supported_formats)) mappedMetadata.supported_formats = metadata.value.supported_formats
    if (hasValue(metadata.value.release_notes)) mappedMetadata.release_notes = metadata.value.release_notes
    if (hasValue(metadata.value.release_date)) mappedMetadata.release_date = metadata.value.release_date
    if (hasValue(metadata.value.installation_info)) mappedMetadata.installation_info = metadata.value.installation_info
    if (hasValue(metadata.value.screenshots)) mappedMetadata.screenshots = metadata.value.screenshots

    // Create product from violation with AI metadata
    const response = await filenameViolationsApi.createProductWithMetadata(
      props.violation.id,
      mappedMetadata
    )

    if (response.data.success) {
      emit('saved', response.data)
      close()
    } else {
      errorMessage.value = response.data.error || t('violationAISearchDialog.createProductFailed')
      await alert.error(errorMessage.value)
    }
  } catch (error) {
    console.error('Save metadata error:', error)
    console.error('Error response:', error.response)

    let errorMsg = t('violationAISearchDialog.createProductFailed')

    if (error.response?.data?.detail) {
      if (typeof error.response.data.detail === 'string') {
        errorMsg = error.response.data.detail
      } else if (Array.isArray(error.response.data.detail)) {
        errorMsg = error.response.data.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ')
      } else {
        errorMsg = JSON.stringify(error.response.data.detail)
      }
    } else if (error.message) {
      errorMsg = error.message
    }

    errorMessage.value = errorMsg
    await alert.error(errorMsg)
  } finally {
    saving.value = false
  }
}

// Image update handlers
const handleLogoUpdate = (iconUrl) => {
  if (metadata.value) {
    metadata.value = {
      ...metadata.value,
      icon_url: iconUrl
    }
  }
}

const handleScreenshotsUpdate = (screenshots) => {
  if (metadata.value) {
    metadata.value = {
      ...metadata.value,
      screenshots: screenshots
    }
  }
}

const close = () => {
  metadata.value = null
  errorMessage.value = ''
  emit('close')
}
</script>
