<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50" @click.self="closeDialog">
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="sticky top-0 bg-gradient-to-r from-orange-500 to-red-600 px-6 py-4 flex items-center justify-between">
        <h2 class="text-xl font-bold text-white flex items-center">
          <span class="mr-2">⚠️</span>
          {{ t('unmatchedDialog.title') }}
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
      <div class="p-6 space-y-6" v-if="item">
        <!-- File Info -->
        <div class="bg-gray-50 dark:bg-gray-700 rounded-xl p-4">
          <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">📁 {{ t('unmatchedDialog.fileInfo') }}</h3>
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div>
              <p class="text-gray-500 dark:text-gray-400">{{ t('unmatchedDialog.fileName') }}</p>
              <p class="font-medium text-gray-900 dark:text-white">{{ item.file_name }}</p>
            </div>
            <div>
              <p class="text-gray-500 dark:text-gray-400">{{ t('unmatchedDialog.filePath') }}</p>
              <p class="font-medium text-gray-900 dark:text-white truncate" :title="item.file_path">{{ item.file_path }}</p>
            </div>
            <div>
              <p class="text-gray-500 dark:text-gray-400">{{ t('unmatchedDialog.parsedName') }}</p>
              <p class="font-medium text-gray-900 dark:text-white">{{ item.parsed_name || 'N/A' }}</p>
            </div>
            <div>
              <p class="text-gray-500 dark:text-gray-400">{{ t('unmatchedDialog.parsedVersion') }}</p>
              <p class="font-medium text-gray-900 dark:text-white">{{ item.parsed_version || 'N/A' }}</p>
            </div>
          </div>
        </div>

        <!-- Confidence Score -->
        <div class="border-2 rounded-xl p-5" :class="getConfidenceBorderClass(item.confidence_score)">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('unmatchedDialog.confidenceScore') }}</h3>
            <div class="text-right">
              <div class="text-2xl font-bold" :class="getConfidenceTextClass(item.confidence_score)">
                {{ Math.round(item.confidence_score * 100) }}%
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400">
                {{ getConfidenceLevel(item.confidence_score) }}
              </div>
            </div>
          </div>
          <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
            <div
              class="h-3 rounded-full transition-all duration-500"
              :class="getConfidenceBarClass(item.confidence_score)"
              :style="{ width: Math.round(item.confidence_score * 100) + '%' }"
            ></div>
          </div>
          <p class="text-xs text-gray-600 dark:text-gray-400 mt-2">
            {{ t('unmatchedDialog.confidenceNote') }}
          </p>
        </div>

        <!-- AI Suggestion -->
        <div v-if="item.suggested_metadata" class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-xl p-5">
          <h3 class="text-sm font-medium text-blue-900 dark:text-blue-300 mb-3">🤖 {{ t('unmatchedDialog.aiSuggestion') }}</h3>

          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p class="text-xs text-blue-700 dark:text-blue-400 mb-1">{{ t('unmatchedDialog.productName') }}</p>
              <p class="font-semibold text-blue-900 dark:text-blue-200">{{ item.suggested_metadata.title }}</p>
            </div>
            <div>
              <p class="text-xs text-blue-700 dark:text-blue-400 mb-1">{{ t('unmatchedDialog.manufacturer') }}</p>
              <p class="font-semibold text-blue-900 dark:text-blue-200">{{ item.suggested_metadata.vendor }}</p>
            </div>
            <div>
              <p class="text-xs text-blue-700 dark:text-blue-400 mb-1">{{ t('unmatchedDialog.categoryLabel') }}</p>
              <p class="font-semibold text-blue-900 dark:text-blue-200">{{ item.suggested_metadata.category }}</p>
            </div>
            <div v-if="item.suggested_metadata.license_type">
              <p class="text-xs text-blue-700 dark:text-blue-400 mb-1">{{ t('unmatchedDialog.license') }}</p>
              <p class="font-semibold text-blue-900 dark:text-blue-200">{{ item.suggested_metadata.license_type }}</p>
            </div>
          </div>

          <div v-if="item.suggested_metadata.description">
            <p class="text-xs text-blue-700 dark:text-blue-400 mb-1">{{ t('unmatchedDialog.descriptionLabel') }}</p>
            <p class="text-sm text-blue-900 dark:text-blue-200">{{ item.suggested_metadata.description }}</p>
          </div>
        </div>

        <!-- Action Tabs -->
        <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
          <div class="flex space-x-2 mb-4">
            <button
              v-for="tab in actionTabs"
              :key="tab.id"
              @click="activeAction = tab.id"
              :class="[
                'px-4 py-2 rounded-lg font-medium transition-colors',
                activeAction === tab.id
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              ]"
            >
              {{ tab.label }}
            </button>
          </div>

          <!-- Approve Action -->
          <div v-if="activeAction === 'approve'" class="space-y-4">
            <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-lg p-4">
              <p class="text-sm text-green-800 dark:text-green-300">
                {{ t('unmatchedDialog.approveDescription') }}
              </p>
            </div>
            <button
              @click="approveItem"
              :disabled="processing"
              class="w-full px-6 py-3 bg-green-500 text-white rounded-xl hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {{ processing ? t('unmatchedDialog.processing') : t('unmatchedDialog.approveButton') }}
            </button>
          </div>

          <!-- Search Action -->
          <div v-if="activeAction === 'search'" class="space-y-4">
            <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-700 rounded-lg p-4">
              <p class="text-sm text-purple-800 dark:text-purple-300 mb-3">
                {{ t('unmatchedDialog.searchDescription') }}
              </p>
              <input
                v-model="searchQuery"
                type="text"
                :placeholder="t('unmatchedDialog.searchPlaceholder')"
                class="w-full px-4 py-2 border border-purple-300 dark:border-purple-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                @keyup.enter="searchMetadata"
              />
            </div>
            <button
              @click="searchMetadata"
              :disabled="processing || !searchQuery.trim()"
              class="w-full px-6 py-3 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {{ processing ? t('unmatchedDialog.searching') : t('unmatchedDialog.searchButton') }}
            </button>
          </div>

          <!-- Manual Action -->
          <div v-if="activeAction === 'manual'" class="space-y-4">
            <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-4">
              <p class="text-sm text-blue-800 dark:text-blue-300 mb-3">
                {{ t('unmatchedDialog.manualDescription') }}
              </p>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {{ t('unmatchedDialog.productNameLabel') }} <span class="text-red-500">{{ t('unmatchedDialog.required') }}</span>
                </label>
                <input
                  v-model="manualData.title"
                  type="text"
                  class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {{ t('unmatchedDialog.manufacturerLabel') }} <span class="text-red-500">{{ t('unmatchedDialog.required') }}</span>
                </label>
                <input
                  v-model="manualData.vendor"
                  type="text"
                  class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ t('unmatchedDialog.categorySelectLabel') }} <span class="text-red-500">{{ t('unmatchedDialog.required') }}</span>
              </label>
              <select
                v-model="manualData.category"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">{{ t('unmatchedDialog.selectPlaceholder') }}</option>
                <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ t('unmatchedDialog.descriptionLabelManual') }} <span class="text-red-500">{{ t('unmatchedDialog.required') }}</span>
              </label>
              <textarea
                v-model="manualData.description"
                rows="4"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              ></textarea>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {{ t('unmatchedDialog.officialWebsite') }}
                </label>
                <input
                  v-model="manualData.official_website"
                  type="url"
                  placeholder="https://..."
                  class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {{ t('unmatchedDialog.iconUrl') }}
                </label>
                <input
                  v-model="manualData.icon_url"
                  type="url"
                  placeholder="https://..."
                  class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>

            <button
              @click="saveManualData"
              :disabled="processing || !isManualDataValid"
              class="w-full px-6 py-3 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {{ processing ? t('unmatchedDialog.saving') : t('unmatchedDialog.manualSaveButton') }}
            </button>
          </div>

          <!-- Ignore Action -->
          <div v-if="activeAction === 'ignore'" class="space-y-4">
            <div class="bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <p class="text-sm text-gray-700 dark:text-gray-300">
                {{ t('unmatchedDialog.ignoreDescription') }}
              </p>
            </div>
            <button
              @click="ignoreItem"
              :disabled="processing"
              class="w-full px-6 py-3 bg-gray-500 text-white rounded-xl hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {{ processing ? t('unmatchedDialog.processing') : t('unmatchedDialog.ignoreButton') }}
            </button>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-xl text-red-700 dark:text-red-400 text-sm">
          {{ errorMessage }}
        </div>

        <!-- Success Message -->
        <div v-if="successMessage" class="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-xl text-green-700 dark:text-green-400 text-sm">
          {{ successMessage }}
        </div>
      </div>

      <!-- Footer -->
      <div class="sticky bottom-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-6 py-4">
        <button
          @click="closeDialog"
          class="w-full px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium"
        >
          {{ t('unmatchedDialog.close') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { unmatchedApi } from '../api/unmatched'

const { t } = useI18n({ useScope: 'global' })

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  item: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'updated'])

// State
const activeAction = ref('approve')
const processing = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const searchQuery = ref('')
const manualData = ref({
  title: '',
  vendor: '',
  category: '',
  description: '',
  official_website: '',
  icon_url: ''
})

const actionTabs = computed(() => [
  { id: 'approve', label: `✓ ${t('unmatchedDialog.approve')}` },
  { id: 'search', label: `🔍 ${t('unmatchedDialog.search')}` },
  { id: 'manual', label: `✏️ ${t('unmatchedDialog.manual')}` },
  { id: 'ignore', label: `🚫 ${t('unmatchedDialog.ignore')}` }
])

const categories = [
  'Graphics', 'Office', 'Development', 'Utility', 'Media',
  'OS', 'Security', 'Network', 'Mac', 'Mobile', 'Patch',
  'Driver', 'Source', 'Backup', 'Portable', 'Business',
  'Engineering', 'Theme', 'Hardware', 'Uncategorized'
]

const isManualDataValid = computed(() => {
  return manualData.value.title &&
         manualData.value.vendor &&
         manualData.value.category &&
         manualData.value.description
})

// Methods
const approveItem = async () => {
  if (!props.item) return

  processing.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await unmatchedApi.approve(props.item.id)
    successMessage.value = t('unmatchedDialog.approveSuccess')
    setTimeout(() => {
      emit('updated')
      closeDialog()
    }, 1500)
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || t('unmatchedDialog.approveError')
  } finally {
    processing.value = false
  }
}

const searchMetadata = async () => {
  if (!props.item || !searchQuery.value.trim()) return

  processing.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await unmatchedApi.search(props.item.id, searchQuery.value.trim())
    successMessage.value = t('unmatchedDialog.searchSuccess', { percentage: response.data.confidence_percentage })

    // 아이템 정보 업데이트
    if (response.data.metadata) {
      props.item.suggested_metadata = response.data.metadata
      props.item.confidence_score = response.data.confidence_score
    }

    emit('updated')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || t('unmatchedDialog.searchError')
  } finally {
    processing.value = false
  }
}

const saveManualData = async () => {
  if (!props.item || !isManualDataValid.value) return

  processing.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await unmatchedApi.saveManual(props.item.id, manualData.value)
    successMessage.value = t('unmatchedDialog.manualSaveSuccess')
    setTimeout(() => {
      emit('updated')
      closeDialog()
    }, 1500)
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || t('unmatchedDialog.manualSaveError')
  } finally{
    processing.value = false
  }
}

const ignoreItem = async () => {
  if (!props.item) return

  processing.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await unmatchedApi.ignore(props.item.id)
    successMessage.value = t('unmatchedDialog.ignoreSuccess')
    setTimeout(() => {
      emit('updated')
      closeDialog()
    }, 1500)
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || t('unmatchedDialog.ignoreError')
  } finally {
    processing.value = false
  }
}

const closeDialog = () => {
  activeAction.value = 'approve'
  errorMessage.value = ''
  successMessage.value = ''
  searchQuery.value = ''
  manualData.value = {
    title: '',
    vendor: '',
    category: '',
    description: '',
    official_website: '',
    icon_url: ''
  }
  emit('close')
}

// Helpers
const getConfidenceLevel = (score) => {
  if (score >= 0.9) return t('unmatchedDialog.confidenceLevelHigh')
  if (score >= 0.7) return t('unmatchedDialog.confidenceLevelMedium')
  return t('unmatchedDialog.confidenceLevelLow')
}

const getConfidenceBorderClass = (score) => {
  if (score >= 0.9) return 'border-green-300 dark:border-green-700 bg-green-50 dark:bg-green-900/10'
  if (score >= 0.7) return 'border-yellow-300 dark:border-yellow-700 bg-yellow-50 dark:bg-yellow-900/10'
  return 'border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/10'
}

const getConfidenceTextClass = (score) => {
  if (score >= 0.9) return 'text-green-600 dark:text-green-400'
  if (score >= 0.7) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
}

const getConfidenceBarClass = (score) => {
  if (score >= 0.9) return 'bg-gradient-to-r from-green-500 to-green-600'
  if (score >= 0.7) return 'bg-gradient-to-r from-yellow-500 to-yellow-600'
  return 'bg-gradient-to-r from-red-500 to-red-600'
}

// Watch item changes
watch(() => props.item, (newItem) => {
  if (newItem) {
    // AI 제안이 있으면 수동 입력 폼에 미리 채우기
    if (newItem.suggested_metadata) {
      manualData.value = {
        title: newItem.suggested_metadata.title || '',
        vendor: newItem.suggested_metadata.vendor || '',
        category: newItem.suggested_metadata.category || '',
        description: newItem.suggested_metadata.description || '',
        official_website: newItem.suggested_metadata.official_website || '',
        icon_url: newItem.suggested_metadata.icon_url || ''
      }
    }
    // 파싱된 이름을 검색 쿼리로 설정
    searchQuery.value = newItem.parsed_name || newItem.file_name || ''
  }
})
</script>
