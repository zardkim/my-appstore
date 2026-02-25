<template>
  <div class="image-manager border border-gray-300 dark:border-gray-600 rounded-lg p-3 sm:p-6 mt-4 sm:mt-6">
    <h3 class="text-base sm:text-lg font-bold text-gray-900 dark:text-white mb-3 sm:mb-4">🖼️ {{ t('imageManager.title') }}</h3>

    <!-- Tabs -->
    <div class="flex space-x-1 sm:space-x-2 border-b border-gray-200 dark:border-gray-700 mb-3 sm:mb-4">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="[
          'px-3 sm:px-4 py-1.5 sm:py-2 font-medium transition-colors text-sm sm:text-base',
          activeTab === tab.id
            ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
            : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
        ]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Tab 1: Logo -->
    <div v-if="activeTab === 'logo'" class="space-y-4">
      <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-3">
        <p class="text-sm text-blue-800 dark:text-blue-300">
          {{ t('imageManager.searchingLogoFor', { name: searchQuery || props.product?.title || t('imageManager.software') }) }}
        </p>
      </div>

      <!-- Editable Search Query -->
      <div class="flex gap-2">
        <div class="flex-1">
          <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ t('imageManager.searchQuery') }}
          </label>
          <input
            v-model="editableSearchQuery"
            type="text"
            class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            :placeholder="t('imageManager.searchQueryPlaceholder')"
            @keyup.enter="searchLogos(false)"
          />
        </div>
        <div class="flex items-end">
          <button
            @click="searchLogos(false)"
            :disabled="!editableSearchQuery.trim()"
            class="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ t('imageManager.search') }}
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="searchLoading" class="flex items-center justify-center py-8">
        <svg class="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="ml-3 text-gray-600 dark:text-gray-400">{{ t('imageManager.searchingLogo') }}</span>
      </div>

      <!-- Error Message -->
      <div v-if="searchError" class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg text-red-700 dark:text-red-400 text-sm whitespace-pre-line">
        {{ searchError }}
      </div>

      <!-- Search Results -->
      <div v-if="!searchLoading && searchResults.length > 0" class="space-y-3">
        <div class="flex items-center justify-between">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ t('imageManager.foundLogos', { count: searchResults.length }) }}
            <span v-if="hasMore" class="text-blue-500">({{ t('imageManager.scrollForMore') }})</span>
          </p>
          <button
            v-if="selectedImages.length > 0"
            @click="downloadSelectedImages"
            class="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors"
          >
            {{ t('imageManager.saveSelectedLogo') }}
          </button>
        </div>
        <div class="grid grid-cols-3 md:grid-cols-5 gap-4">
          <div
            v-for="(result, index) in searchResults"
            :key="index"
            @click="toggleImageSelection(result)"
            @mouseenter="handleImageHover(result, $event)"
            @mouseleave="handleImageLeave"
            :class="[
              'cursor-pointer border-2 rounded-lg p-2 transition-colors relative',
              isImageSelected(result)
                ? 'border-green-500 dark:border-green-400 bg-green-50 dark:bg-green-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-400'
            ]"
          >
            <img
              :src="result.thumbnail"
              :alt="result.title"
              class="w-full h-24 object-contain bg-gray-50 dark:bg-gray-800 rounded"
              @error="handleImageError"
            />
            <p class="text-xs text-gray-600 dark:text-gray-400 mt-1 truncate" :title="result.title">
              {{ result.title }}
            </p>
            <!-- 선택 표시 -->
            <div
              v-if="isImageSelected(result)"
              class="absolute top-1 right-1 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center"
            >
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
        </div>

        <!-- Infinite Scroll Trigger & Loading -->
        <div ref="loadMoreTrigger" class="py-4">
          <div v-if="isLoadingMore" class="flex items-center justify-center">
            <svg class="animate-spin h-6 w-6 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span class="ml-2 text-sm text-gray-600 dark:text-gray-400">{{ t('imageManager.loadingMore') }}</span>
          </div>
          <div v-else-if="!hasMore" class="text-center text-sm text-gray-500 dark:text-gray-400">
            {{ t('imageManager.allResultsLoaded') }}
          </div>
        </div>
      </div>

      <div v-else-if="!searchLoading && searchResults.length === 0 && searchPerformed" class="text-center py-8 text-gray-500 dark:text-gray-400">
        {{ t('imageManager.errors.noResults') }}
      </div>
    </div>

    <!-- Tab 2: Screenshot -->
    <div v-if="activeTab === 'screenshot'" class="space-y-4">
      <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-700 rounded-lg p-3">
        <p class="text-sm text-purple-800 dark:text-purple-300">
          {{ t('imageManager.searchingScreenshotFor', { name: searchQuery || props.product?.title || t('imageManager.software') }) }}
          <span class="text-xs block mt-1">({{ t('imageManager.maxSelectHint') }})</span>
        </p>
      </div>

      <!-- Editable Search Query -->
      <div class="flex gap-2">
        <div class="flex-1">
          <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ t('imageManager.searchQuery') }}
          </label>
          <input
            v-model="editableSearchQuery"
            type="text"
            class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            :placeholder="t('imageManager.searchQueryPlaceholder')"
            @keyup.enter="searchScreenshots(false)"
          />
        </div>
        <div class="flex items-end">
          <button
            @click="searchScreenshots(false)"
            :disabled="!editableSearchQuery.trim()"
            class="px-4 py-2 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ t('imageManager.search') }}
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="searchLoading" class="flex items-center justify-center py-8">
        <svg class="animate-spin h-8 w-8 text-purple-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="ml-3 text-gray-600 dark:text-gray-400">{{ t('imageManager.searchingScreenshot') }}</span>
      </div>

      <!-- Error Message -->
      <div v-if="searchError" class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg text-red-700 dark:text-red-400 text-sm whitespace-pre-line">
        {{ searchError }}
      </div>

      <!-- Search Results -->
      <div v-if="!searchLoading && searchResults.length > 0" class="space-y-3">
        <div class="flex items-center justify-between">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ t('imageManager.foundScreenshots', { count: searchResults.length }) }}
            <span v-if="hasMore" class="text-purple-500">({{ t('imageManager.scrollForMore') }})</span>
            <span class="text-purple-600 dark:text-purple-400">
              ({{ t('imageManager.selectedCount', { count: selectedImages.length }) }})
            </span>
          </p>
          <button
            v-if="selectedImages.length > 0"
            @click="downloadSelectedImages"
            class="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors"
          >
            {{ t('imageManager.saveSelectedScreenshots', { count: selectedImages.length }) }}
          </button>
        </div>
        <div class="grid grid-cols-3 md:grid-cols-5 gap-4">
          <div
            v-for="(result, index) in searchResults"
            :key="index"
            @click="toggleImageSelection(result)"
            @mouseenter="handleImageHover(result, $event)"
            @mouseleave="handleImageLeave"
            :class="[
              'cursor-pointer border-2 rounded-lg p-2 transition-colors relative',
              isImageSelected(result)
                ? 'border-green-500 dark:border-green-400 bg-green-50 dark:bg-green-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-purple-500 dark:hover:border-purple-400'
            ]"
          >
            <img
              :src="result.thumbnail"
              :alt="result.title"
              class="w-full h-24 object-contain bg-gray-50 dark:bg-gray-800 rounded"
              @error="handleImageError"
            />
            <p class="text-xs text-gray-600 dark:text-gray-400 mt-1 truncate" :title="result.title">
              {{ result.title }}
            </p>
            <!-- 선택 표시 -->
            <div
              v-if="isImageSelected(result)"
              class="absolute top-1 right-1 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center"
            >
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
        </div>

        <!-- Infinite Scroll Trigger & Loading (스크린샷 탭용) -->
        <div ref="loadMoreTrigger" class="py-4">
          <div v-if="isLoadingMore" class="flex items-center justify-center">
            <svg class="animate-spin h-6 w-6 text-purple-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span class="ml-2 text-sm text-gray-600 dark:text-gray-400">{{ t('imageManager.loadingMore') }}</span>
          </div>
          <div v-else-if="!hasMore" class="text-center text-sm text-gray-500 dark:text-gray-400">
            {{ t('imageManager.allResultsLoaded') }}
          </div>
        </div>
      </div>

      <div v-else-if="!searchLoading && searchResults.length === 0 && searchPerformed" class="text-center py-8 text-gray-500 dark:text-gray-400">
        {{ t('imageManager.errors.noResults') }}
      </div>
    </div>

    <!-- Tab 3: Manual Upload -->
    <div v-if="activeTab === 'upload'" class="space-y-6">
      <!-- Logo Upload -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {{ t('imageManager.uploadLogo') }}
        </label>
        <input
          type="file"
          ref="logoFileInput"
          @change="handleLogoUpload"
          accept="image/*"
          class="block w-full text-sm text-gray-900 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer bg-gray-50 dark:bg-gray-700 focus:outline-none"
        />
        <p class="text-xs text-gray-500 dark:text-gray-400">
          {{ t('imageManager.supportedFormats') }}
        </p>
      </div>

      <!-- Screenshot Upload -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {{ t('imageManager.uploadScreenshots') }}
        </label>
        <input
          type="file"
          ref="screenshotFileInput"
          @change="handleScreenshotUpload"
          accept="image/*"
          multiple
          class="block w-full text-sm text-gray-900 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer bg-gray-50 dark:bg-gray-700 focus:outline-none"
        />
        <p class="text-xs text-gray-500 dark:text-gray-400">
          {{ t('imageManager.multiSelectHint') }}
        </p>
      </div>

      <!-- Upload Error -->
      <div v-if="uploadError" class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg text-red-700 dark:text-red-400 text-sm">
        {{ uploadError }}
      </div>

      <!-- Upload Success -->
      <div v-if="uploadSuccess" class="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-lg text-green-700 dark:text-green-400 text-sm">
        {{ uploadSuccess }}
      </div>
    </div>

    <!-- Tab 4: Current Images -->
    <div v-if="activeTab === 'current'" class="space-y-6">
      <!-- Current Logo -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {{ t('imageManager.currentLogo') }}
        </label>
        <div v-if="currentLogo" class="flex items-center space-x-4">
          <img
            :src="currentLogo"
            alt="Current logo"
            class="w-24 h-24 object-contain border border-gray-200 dark:border-gray-700 rounded"
            @error="handleImageError"
          />
          <button
            @click="deleteLogo"
            class="px-3 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition-colors"
          >
            {{ t('common.delete') }}
          </button>
        </div>
        <div v-else class="text-sm text-gray-500 dark:text-gray-400">
          {{ t('imageManager.noLogo') }}
        </div>
      </div>

      <!-- Current Screenshots -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {{ t('imageManager.currentScreenshots', { count: currentScreenshots.length }) }}
        </label>
        <div v-if="currentScreenshots.length > 0" class="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div v-for="(screenshot, index) in currentScreenshots" :key="index" class="relative group">
            <img
              :src="screenshot.url"
              :alt="t('imageManager.screenshotAlt', { index: index + 1 })"
              class="w-full h-32 object-cover border border-gray-200 dark:border-gray-700 rounded cursor-pointer"
              @click="openImageInNewTab(screenshot.url)"
              @error="handleImageError"
            />
            <button
              @click="deleteScreenshot(index)"
              class="absolute top-2 right-2 px-2 py-1 bg-red-600 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity"
            >
              {{ t('common.delete') }}
            </button>
            <span class="absolute bottom-2 left-2 px-2 py-1 bg-black bg-opacity-50 text-white text-xs rounded">
              {{ screenshot.type === 'local' ? t('imageManager.local') : t('imageManager.external') }}
            </span>
          </div>
        </div>
        <div v-else class="text-sm text-gray-500 dark:text-gray-400">
          {{ t('imageManager.noScreenshots') }}
        </div>
      </div>

      <!-- Delete All Button -->
      <div v-if="currentLogo || currentScreenshots.length > 0">
        <button
          @click="deleteAll"
          class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          {{ t('imageManager.deleteAll') }}
        </button>
      </div>
    </div>

    <!-- Image Preview Overlay (Hover) -->
    <Teleport to="body">
      <div
        v-if="hoveredImage"
        :style="{
          position: 'fixed',
          left: `${hoverPosition.x}px`,
          top: `${hoverPosition.y}px`,
          zIndex: 9999,
          pointerEvents: 'none'
        }"
        class="bg-white dark:bg-gray-800 border-2 border-blue-500 dark:border-blue-400 rounded-lg shadow-2xl p-3 transition-opacity duration-200"
        style="animation: fadeIn 0.15s ease-in;"
      >
        <div class="space-y-2">
          <img
            :src="hoveredImage.url"
            :alt="hoveredImage.title"
            class="w-96 h-72 object-contain bg-gray-50 dark:bg-gray-900 rounded"
            @error="(e) => e.target.src = hoveredImage?.thumbnail || ''"
          />
          <div class="max-w-96">
            <p class="text-sm font-medium text-gray-900 dark:text-white truncate" :title="hoveredImage.title">
              {{ hoveredImage.title }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400 truncate" :title="hoveredImage.url">
              {{ hoveredImage.url }}
            </p>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { imagesApi } from '../api/images'
import { useDialog } from '../composables/useDialog'

const { t, locale } = useI18n({ useScope: 'global' })
const { alert, confirm: confirmDialog } = useDialog()

const props = defineProps({
  productId: {
    type: Number,
    required: true
  },
  product: {
    type: Object,
    required: true
  },
  initialSearchQuery: {
    type: String,
    default: ''
  },
  testMode: {
    type: Boolean,
    default: false
  },
  defaultTab: {
    type: String,
    default: 'logo',
    validator: (value) => ['logo', 'screenshot', 'upload', 'current'].includes(value)
  },
  visibleTabs: {
    type: Array,
    default: () => ['logo', 'screenshot', 'upload', 'current'],
    validator: (value) => value.every(tab => ['logo', 'screenshot', 'upload', 'current'].includes(tab))
  }
})

const emit = defineEmits(['update:logo', 'update:screenshots'])

// Tabs
const allTabs = computed(() => [
  { id: 'logo', label: t('imageManager.tabs.logo') },
  { id: 'screenshot', label: t('imageManager.tabs.screenshot') },
  { id: 'upload', label: t('imageManager.tabs.upload') },
  { id: 'current', label: t('imageManager.tabs.current') }
])

// visibleTabs prop에 따라 표시할 탭만 필터링
const tabs = computed(() => {
  return allTabs.value.filter(tab => props.visibleTabs.includes(tab.id))
})

const activeTab = ref(props.defaultTab)

// Search
const searchQuery = ref('')
const editableSearchQuery = ref('') // 사용자가 편집 가능한 최종 검색어
const searchResults = ref([])
const searchLoading = ref(false)
const searchError = ref('')
const searchPerformed = ref(false)
const searchType = ref('') // 'logo' or 'screenshot'
const selectedImages = ref([]) // 선택된 이미지들

// Infinite scroll
const searchOffset = ref(0)
const hasMore = ref(true)
const isLoadingMore = ref(false)
const scrollObserver = ref(null)
const loadMoreTrigger = ref(null) // 스크롤 감지 요소

// Image preview on hover
const hoveredImage = ref(null)
const hoverPosition = ref({ x: 0, y: 0 })

// Upload
const logoFileInput = ref(null)
const screenshotFileInput = ref(null)
const uploadError = ref('')
const uploadSuccess = ref('')

// Current images - ref로 변경하여 직접 제어
const currentLogo = ref(props.product?.icon_url || null)
const currentScreenshots = ref([])

// props.product 변경 감지하여 current images 업데이트
watch(() => props.product, (newProduct) => {

  // 로고 업데이트
  currentLogo.value = newProduct?.icon_url || null

  // 스크린샷 업데이트
  const screenshots = newProduct?.screenshots || []
  if (Array.isArray(screenshots)) {
    if (screenshots.length > 0 && typeof screenshots[0] === 'object') {
      currentScreenshots.value = screenshots
    } else {
      currentScreenshots.value = screenshots.map(url => ({ type: 'external', url }))
    }
  } else {
    currentScreenshots.value = []
  }
}, { deep: true, immediate: true })

// 검색어 정리 함수 (세부 버전을 주요 버전으로 축소, 불필요한 키워드 제거)
const cleanSearchQuery = (query) => {
  if (!query) return ''

  let cleaned = query.trim()

  // Build xxxxx 패턴 제거
  cleaned = cleaned.replace(/\s+Build\s+\d+/gi, '')

  // 세부 버전을 주요 버전으로 축소 (v16.0.0 → v16, v22.1.2529 → v22)
  cleaned = cleaned.replace(/\b(v\d+)\.\d+(\.\d+)*/gi, '$1')

  // 연도가 아닌 독립적인 긴 숫자 제거 (예: 16894299)
  cleaned = cleaned.replace(/\s+\d{5,}/g, '')

  // RePackk, Portable, x64, x86 등의 불필요한 키워드 제거
  cleaned = cleaned.replace(/\s+(repack|portable|x64|x86|win|windows|macos|linux|crack|keygen|patch|final).*$/i, '')

  // 여러 공백을 하나로
  cleaned = cleaned.replace(/\s+/g, ' ').trim()

  return cleaned
}

// Search logos
const searchLogos = async (isLoadMore = false) => {
  if (!searchQuery.value.trim() && !editableSearchQuery.value.trim()) return

  // 초기 검색인 경우
  if (!isLoadMore) {
    searchLoading.value = true
    searchError.value = ''
    searchResults.value = []
    searchPerformed.value = true
    searchType.value = 'logo'
    selectedImages.value = []
    searchOffset.value = 0
    hasMore.value = true

    // editableSearchQuery가 비어있으면 자동 생성
    if (!editableSearchQuery.value.trim()) {
      const cleanedQuery = cleanSearchQuery(searchQuery.value)
      const keyword = locale.value === 'ko' ? '로고' : 'logo'
      editableSearchQuery.value = `${cleanedQuery} ${keyword}`
    }
  } else {
    // 추가 로딩인 경우
    isLoadingMore.value = true
  }

  try {
    const baseQuery = editableSearchQuery.value.trim()

    if (!isLoadMore) {
      // 초기 검색: 한국어와 영어 두 번 검색
      const koreanQuery = baseQuery.replace(/\s+logo$/i, ' 로고')
      const englishQuery = baseQuery.replace(/\s+로고$/i, ' logo')

      // 한국어 검색
      const response1 = await imagesApi.searchLogo(koreanQuery, 10, 0)
      const koreanResults = response1.data.success ? (response1.data.images || []) : []

      // 영어 검색
      const response2 = await imagesApi.searchLogo(englishQuery, 10, 0)
      const englishResults = response2.data.success ? (response2.data.images || []) : []

      // 결과 병합 및 중복 제거
      const allResults = [...koreanResults, ...englishResults]
      const uniqueResults = allResults.filter((item, index, self) =>
        index === self.findIndex(t => t.url === item.url)
      )

      searchResults.value = uniqueResults
      searchOffset.value = uniqueResults.length

      // 더 로드 가능 여부
      hasMore.value = koreanResults.length >= 10 || englishResults.length >= 10

      if (searchResults.value.length === 0) {
        searchError.value = response1.data.error || response2.data.error || t('imageManager.errors.noResults')
      }
    } else {
      // 추가 로딩: 기존 방식 유지
      const response = await imagesApi.searchLogo(baseQuery, 20, searchOffset.value)

      if (response.data.success) {
        const newResults = response.data.images || []
        searchResults.value = [...searchResults.value, ...newResults]

        if (newResults.length < 20 || searchOffset.value >= 80) {
          hasMore.value = false
        } else {
          searchOffset.value += newResults.length
        }
      } else {
        searchError.value = response.data.error || t('imageManager.errors.searchFailed')
      }
    }
  } catch (error) {
    console.error('Logo search error:', error)
    searchError.value = t('imageManager.errors.googleApiError', { error: error.message || t('imageManager.errors.unknownError') })
  } finally {
    searchLoading.value = false
    isLoadingMore.value = false
  }
}

// Search screenshots
const searchScreenshots = async (isLoadMore = false) => {
  if (!searchQuery.value.trim() && !editableSearchQuery.value.trim()) return

  // 초기 검색인 경우
  if (!isLoadMore) {
    searchLoading.value = true
    searchError.value = ''
    searchResults.value = []
    searchPerformed.value = true
    searchType.value = 'screenshot'
    selectedImages.value = []
    searchOffset.value = 0
    hasMore.value = true

    // editableSearchQuery가 비어있으면 자동 생성
    if (!editableSearchQuery.value.trim()) {
      const cleanedQuery = cleanSearchQuery(searchQuery.value)
      const keyword = locale.value === 'ko' ? '스크린샷' : 'screenshot'
      editableSearchQuery.value = `${cleanedQuery} ${keyword}`
    }
  } else {
    // 추가 로딩인 경우
    isLoadingMore.value = true
  }

  try {
    const baseQuery = editableSearchQuery.value.trim()

    if (!isLoadMore) {
      // 초기 검색: 한국어와 영어 두 번 검색
      const koreanQuery = baseQuery.replace(/\s+screenshot$/i, ' 스크린샷')
      const englishQuery = baseQuery.replace(/\s+스크린샷$/i, ' screenshot')

      // 한국어 검색
      const response1 = await imagesApi.searchScreenshots(koreanQuery, 10, 0)
      const koreanResults = response1.data.success ? (response1.data.images || []) : []

      // 영어 검색
      const response2 = await imagesApi.searchScreenshots(englishQuery, 10, 0)
      const englishResults = response2.data.success ? (response2.data.images || []) : []

      // 결과 병합 및 중복 제거
      const allResults = [...koreanResults, ...englishResults]
      const uniqueResults = allResults.filter((item, index, self) =>
        index === self.findIndex(t => t.url === item.url)
      )

      searchResults.value = uniqueResults
      searchOffset.value = uniqueResults.length

      // 더 로드 가능 여부
      hasMore.value = koreanResults.length >= 10 || englishResults.length >= 10

      if (searchResults.value.length === 0) {
        searchError.value = response1.data.error || response2.data.error || t('imageManager.errors.noResults')
      }
    } else {
      // 추가 로딩: 기존 방식 유지
      const response = await imagesApi.searchScreenshots(baseQuery, 20, searchOffset.value)

      if (response.data.success) {
        const newResults = response.data.images || []
        searchResults.value = [...searchResults.value, ...newResults]

        if (newResults.length < 20 || searchOffset.value >= 80) {
          hasMore.value = false
        } else {
          searchOffset.value += newResults.length
        }
      } else {
        searchError.value = response.data.error || t('imageManager.errors.searchFailed')
      }
    }
  } catch (error) {
    console.error('Screenshot search error:', error)
    searchError.value = t('imageManager.errors.googleApiError', { error: error.message || t('imageManager.errors.unknownError') })
  } finally {
    searchLoading.value = false
    isLoadingMore.value = false
  }
}

// Load more images (infinite scroll)
const loadMore = async () => {
  if (!hasMore.value || isLoadingMore.value || searchLoading.value) {
    return
  }


  if (searchType.value === 'logo') {
    await searchLogos(true)
  } else if (searchType.value === 'screenshot') {
    await searchScreenshots(true)
  }
}

// Setup intersection observer for infinite scroll
const setupIntersectionObserver = () => {
  // Clean up existing observer
  if (scrollObserver.value) {
    scrollObserver.value.disconnect()
  }

  // Find the scrollable container (dialog content)
  const scrollContainer = loadMoreTrigger.value?.closest('.overflow-y-auto')

  // Create new observer
  scrollObserver.value = new IntersectionObserver(
    (entries) => {
      const target = entries[0]
      if (target.isIntersecting && hasMore.value && !isLoadingMore.value && !searchLoading.value) {
        loadMore()
      }
    },
    {
      root: scrollContainer, // Use dialog's scrollable container instead of viewport
      rootMargin: '100px', // 미리 로드 (100px 전에 로딩 시작)
      threshold: 0.1
    }
  )

  // Observe the trigger element
  if (loadMoreTrigger.value) {
    scrollObserver.value.observe(loadMoreTrigger.value)
  }
}

// 이미지 선택/선택 해제 토글
const toggleImageSelection = async (result) => {
  const index = selectedImages.value.findIndex(img => img.url === result.url)

  if (index >= 0) {
    // 이미 선택됨 -> 선택 해제
    selectedImages.value.splice(index, 1)
  } else {
    // 로고 검색의 경우 1개만 선택 가능
    if (searchType.value === 'logo') {
      selectedImages.value = [result]
    } else {
      // 스크린샷 검색의 경우 여러 개 선택 가능 (최대 10개)
      if (selectedImages.value.length < 10) {
        selectedImages.value.push(result)
      } else {
        await alert.warning(t('imageManager.errors.maxSelectionLimit'))
      }
    }
  }
}

// 이미지가 선택되었는지 확인
const isImageSelected = (result) => {
  return selectedImages.value.some(img => img.url === result.url)
}

// Handle image hover for preview
const handleImageHover = (result, event) => {
  hoveredImage.value = result
  updateHoverPosition(event)
}

const handleImageLeave = () => {
  hoveredImage.value = null
}

const updateHoverPosition = (event) => {
  const rect = event.currentTarget.getBoundingClientRect()
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight

  // 미리보기 크기 (고정)
  const previewWidth = 400
  const previewHeight = 300

  // 기본 위치는 이미지 오른쪽
  let x = rect.right + 10
  let y = rect.top

  // 화면 오른쪽을 벗어나면 왼쪽에 표시
  if (x + previewWidth > viewportWidth) {
    x = rect.left - previewWidth - 10
  }

  // 화면 아래를 벗어나면 위로 조정
  if (y + previewHeight > viewportHeight) {
    y = viewportHeight - previewHeight - 10
  }

  // 화면 위를 벗어나면 아래로 조정
  if (y < 10) {
    y = 10
  }

  hoverPosition.value = { x, y }
}

// 선택한 이미지 다운로드 및 저장
const downloadSelectedImages = async () => {
  if (selectedImages.value.length === 0) return

  try {
    if (searchType.value === 'logo') {
      // 로고 다운로드
      const imageUrl = selectedImages.value[0].url
      const response = await imagesApi.downloadLogo(props.productId, imageUrl)

      if (response.data.success) {
        emit('update:logo', response.data.url)
        await alert.success(t('imageManager.success.logoSaved'))
        // 검색 결과 초기화
        searchResults.value = []
        selectedImages.value = []
        searchPerformed.value = false
        // 현재 이미지 탭으로 전환 (current 탭이 visible일 때만)
        if (props.visibleTabs.includes('current')) {
          activeTab.value = 'current'
        }
      } else {
        await alert.error(t('imageManager.errors.logoSaveFailed') + ': ' + (response.data.error || t('imageManager.errors.unknownError')))
      }
    } else {
      // 스크린샷 다운로드
      // 기존 스크린샷 URL 추출
      const existingScreenshots = props.product?.screenshots || []
      const existingUrls = existingScreenshots.map(s => typeof s === 'string' ? s : s.url)

      // 새로 선택한 이미지 URL (최대 4개)
      const newUrls = selectedImages.value.map(img => img.url).slice(0, 4)

      if (selectedImages.value.length > 4) {
        await alert.warning(t('imageManager.errors.maxScreenshotLimit'))
      }

      // 교체 로직: 새로운 스크린샷으로 앞에서부터 교체
      // 예: 기존 4개 있고 새로 3개 선택 → 1,2,3번 교체, 4번 유지
      const finalUrls = [...newUrls]

      // 새로운 스크린샷 개수보다 기존 스크린샷이 더 많으면 나머지 유지
      if (newUrls.length < existingUrls.length && existingUrls.length <= 4) {
        for (let i = newUrls.length; i < Math.min(existingUrls.length, 4); i++) {
          finalUrls.push(existingUrls[i])
        }
      }


      const response = await imagesApi.downloadScreenshots(props.productId, finalUrls)

      if (response.data.success) {
        const screenshots = (response.data.urls || []).map(url => ({
          type: url.startsWith('/static/') ? 'local' : 'external',
          url
        }))
        emit('update:screenshots', screenshots)

        // 검색 결과 초기화
        searchResults.value = []
        selectedImages.value = []
        searchPerformed.value = false
        // 현재 이미지 탭으로 전환 (current 탭이 visible일 때만)
        if (props.visibleTabs.includes('current')) {
          activeTab.value = 'current'
        }
      } else {
        await alert.error(t('imageManager.errors.screenshotSaveFailed') + ': ' + (response.data.error || t('imageManager.errors.unknownError')))
      }
    }
  } catch (error) {
    console.error('Image download error:', error)
    console.error('Error response:', error.response?.data)
    await alert.error(t('imageManager.errors.imageSaveError') + ': ' + (error.response?.data?.detail || error.message))
  }
}

// Handle logo upload
const handleLogoUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  uploadError.value = ''
  uploadSuccess.value = ''

  try {
    const response = await imagesApi.uploadLogo(props.productId, file)
    if (response.data.success) {
      uploadSuccess.value = t('imageManager.success.logoUploaded')
      emit('update:logo', response.data.url)
      logoFileInput.value.value = ''
    } else {
      uploadError.value = response.data.error || t('imageManager.errors.logoUploadFailed')
    }
  } catch (error) {
    console.error('Logo upload error:', error)
    uploadError.value = t('imageManager.errors.logoUploadError')
  }
}

// Handle screenshot upload
const handleScreenshotUpload = async (event) => {
  const files = Array.from(event.target.files)
  if (files.length === 0) return

  if (files.length > 10) {
    uploadError.value = t('imageManager.errors.maxFileUploadLimit')
    return
  }

  uploadError.value = ''
  uploadSuccess.value = ''

  try {
    const response = await imagesApi.uploadScreenshots(props.productId, files)
    if (response.data.success) {
      const screenshots = (response.data.urls || []).map(url => ({ type: 'local', url }))
      emit('update:screenshots', screenshots)
      screenshotFileInput.value.value = ''
    } else {
      uploadError.value = response.data.error || t('imageManager.errors.screenshotUploadFailed')
    }
  } catch (error) {
    console.error('Screenshot upload error:', error)
    uploadError.value = t('imageManager.errors.screenshotUploadError')
  }
}

// Delete logo
const deleteLogo = async () => {
  if (!confirm(t('imageManager.confirm.deleteLogo'))) return

  try {
    const response = await imagesApi.deleteImages(props.productId, 'logo')
    if (response.data.success) {
      emit('update:logo', null)
      await alert.success(t('imageManager.success.logoDeleted'))
    } else {
      await alert.error(t('imageManager.errors.logoDeleteFailed'))
    }
  } catch (error) {
    console.error('Logo delete error:', error)
    await alert.error(t('imageManager.errors.logoDeleteError'))
  }
}

// Delete single screenshot
const deleteScreenshot = async (index) => {
  if (!confirm(t('imageManager.confirm.deleteScreenshot'))) return

  // For now, delete all screenshots as the API doesn't support single deletion
  // In a full implementation, we'd need a separate endpoint for single screenshot deletion
  await alert.info(t('imageManager.info.singleDeleteNotSupported'))
}

// Delete all images
const deleteAll = async () => {
  if (!confirm(t('imageManager.confirm.deleteAll'))) return

  try {
    const response = await imagesApi.deleteImages(props.productId, 'all')
    if (response.data.success) {
      emit('update:logo', null)
      emit('update:screenshots', [])
      await alert.success(t('imageManager.success.imagesDeleted', { count: response.data.deleted_count }))
    } else {
      await alert.error(t('imageManager.errors.imageDeleteFailed'))
    }
  } catch (error) {
    console.error('Delete all error:', error)
    await alert.error(t('imageManager.errors.imageDeleteError'))
  }
}

// Open image in new tab
const openImageInNewTab = (url) => {
  window.open(url, '_blank')
}

// Handle image error
const handleImageError = (event) => {
  event.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="150"%3E%3Crect fill="%23f0f0f0" width="200" height="150"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%23999"%3E이미지 없음%3C/text%3E%3C/svg%3E'
}

// Initialize with search query from props and auto-search
onMounted(() => {

  // defaultTab이 지정되지 않은 경우에만 current 탭으로 자동 전환
  // visible-tabs에 current가 포함된 경우에만 current 탭으로 전환
  if (props.defaultTab === 'logo' && props.visibleTabs.includes('current') && (props.product?.icon_url || (props.product?.screenshots && props.product.screenshots.length > 0))) {
    activeTab.value = 'current'
    return // 검색 실행하지 않음
  }

  if (props.initialSearchQuery) {
    searchQuery.value = props.initialSearchQuery

    // 초기 탭에서 자동으로 검색 실행
    if (activeTab.value === 'logo') {
      searchLogos()
    } else if (activeTab.value === 'screenshot') {
      searchScreenshots()
    }
  }
})

// Watch activeTab and auto-search when switching to logo/screenshot tabs
watch(activeTab, (newTab) => {

  // 현재 이미지 탭으로 전환 시 현재 값 로깅
  if (newTab === 'current') {
  }

  if (!searchQuery.value) {
    // searchQuery가 없으면 initialSearchQuery 사용
    if (props.initialSearchQuery) {
      searchQuery.value = props.initialSearchQuery
    } else if (props.product?.title) {
      searchQuery.value = props.product.title
    }
  }

  // 탭 전환 시 editableSearchQuery 초기화하여 자동 생성되도록
  editableSearchQuery.value = ''

  // 탭 전환 시 자동 검색
  if (newTab === 'logo' && searchQuery.value) {
    searchLogos()
  } else if (newTab === 'screenshot' && searchQuery.value) {
    searchScreenshots()
  }
})

// Watch search results and setup infinite scroll
watch(searchResults, async (newResults) => {
  if (newResults.length > 0) {
    // 검색 결과가 있으면 DOM이 업데이트된 후 IntersectionObserver 설정
    await nextTick()
    setupIntersectionObserver()
  }
})

// Cleanup on unmount
onUnmounted(() => {
  if (scrollObserver.value) {
    scrollObserver.value.disconnect()
  }
})
</script>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
