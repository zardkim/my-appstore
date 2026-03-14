<template>
  <div class="h-full flex relative">
    <!-- Left Sidebar - Categories (Desktop only) -->
    <div class="hidden lg:block w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 overflow-y-auto flex-shrink-0 scrollbar-hide">
      <div class="p-6">
        <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">{{ t('discover.categories') }}</h2>
        <nav class="space-y-0.5">
          <button
            @click="selectCategory(null)"
            :class="[
              'w-full text-left px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center justify-between',
              selectedCategory === null
                ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-md'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            ]"
          >
            <span>{{ t('discover.allCategories') }}</span>
            <span class="text-xs opacity-75">{{ allTotal }}</span>
          </button>

          <button
            v-for="category in categories"
            :key="category.name"
            @click="selectCategory(category.name)"
            :class="[
              'w-full text-left px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center',
              selectedCategory === category.name
                ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-md'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            ]"
          >
            <span class="text-lg mr-3">{{ category.icon }}</span>
            <span class="flex-1">{{ t(`categories.${category.name}`) }}</span>
            <span class="text-xs opacity-75">{{ getCategoryCount(category.name) }}</span>
          </button>
        </nav>

      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 overflow-y-auto">
      <div class="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 pb-20 lg:pb-8">
        <!-- Header -->
        <div class="mb-4 sm:mb-6 flex flex-col sm:flex-row items-start sm:items-start justify-between gap-3">
          <div class="flex-1">
            <h1 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-1 sm:mb-2">{{ t('discover.title') }}</h1>
            <p class="text-sm sm:text-base text-gray-500 dark:text-gray-400">{{ totalProducts }}{{ t('discover.productsCount') }}</p>
          </div>

          <div class="flex items-center gap-1.5 sm:gap-2 flex-wrap">
            <!-- Scan Button -->
            <button
              v-if="authStore.isAdmin"
              @click="goToScan"
              class="flex items-center gap-1.5 px-3 sm:px-4 py-2 sm:py-2.5 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg sm:rounded-xl hover:shadow-lg transition-all duration-200 font-medium text-xs sm:text-sm"
              :title="t('discover.scanProgramsTitle')"
            >
              <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>{{ t('discover.scanPrograms') }}</span>
            </button>
          </div>
        </div>

        <!-- Search & Sort -->
        <div class="bg-white dark:bg-gray-800 rounded-xl sm:rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-3 sm:p-4 mb-4 sm:mb-6">
          <!-- 검색 입력 (모바일: 전체 너비) -->
          <div class="flex items-center gap-2 mb-2 sm:mb-0">
            <!-- Category Button (Mobile only) -->
            <button
              @click="showCategoryModal = true"
              class="lg:hidden flex-shrink-0 p-2.5 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
              :title="t('discover.selectCategory')"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            <div class="relative flex-1">
              <div class="absolute inset-y-0 left-0 pl-3 sm:pl-4 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                v-model="searchQuery"
                type="text"
                :placeholder="t('discover.searchPlaceholder')"
                class="block w-full pl-10 sm:pl-12 pr-3 sm:pr-4 py-2.5 sm:py-3 border border-gray-200 dark:border-gray-600 rounded-lg sm:rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                @input="handleSearch"
              />
            </div>

            <!-- 데스크톱: 정렬/정리 버튼을 검색 옆에 -->
            <select
              v-model="sortBy"
              class="hidden sm:block px-3 sm:px-4 py-2.5 sm:py-3 border border-gray-200 dark:border-gray-600 rounded-lg sm:rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white flex-shrink-0"
              @change="resetAndLoad"
            >
              <option value="id">{{ t('discover.sortByLatest') }}</option>
              <option value="title">{{ t('discover.sortByName') }}</option>
              <option value="category">{{ t('discover.sortByCategory') }}</option>
            </select>

            <button
              v-if="authStore.user?.role === 'admin'"
              @click="cleanupDeletedFiles"
              class="hidden sm:flex items-center gap-2 px-3 sm:px-4 py-2.5 sm:py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg sm:rounded-xl hover:from-red-600 hover:to-red-700 transition-all shadow-md hover:shadow-lg font-medium text-sm flex-shrink-0"
            >
              <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              <span>{{ t('discover.cleanupDeleted') }}</span>
            </button>
          </div>

          <!-- 모바일: 정렬/정리 버튼을 아래 줄에 -->
          <div class="flex sm:hidden items-center gap-2">
            <select
              v-model="sortBy"
              class="flex-1 px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              @change="resetAndLoad"
            >
              <option value="id">{{ t('discover.sortByLatest') }}</option>
              <option value="title">{{ t('discover.sortByName') }}</option>
              <option value="category">{{ t('discover.sortByCategory') }}</option>
            </select>

            <button
              v-if="authStore.user?.role === 'admin'"
              @click="cleanupDeletedFiles"
              class="flex items-center gap-1.5 px-3 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg hover:from-red-600 hover:to-red-700 transition-all font-medium text-sm flex-shrink-0"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              {{ t('discover.cleanup') }}
            </button>
          </div>
        </div>

        <!-- Products Grid -->
        <div>
          <!-- Loading State -->
          <div v-if="loading" class="flex justify-center py-20">
            <div class="text-center">
              <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 dark:border-blue-400 mx-auto mb-4"></div>
              <p class="text-gray-500 dark:text-gray-400">{{ t('common.loading') }}</p>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else-if="products.length === 0" class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-12 text-center">
            <div class="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-gray-100 to-gray-50 dark:from-gray-700 dark:to-gray-800 rounded-3xl flex items-center justify-center">
              <svg class="w-10 h-10 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">{{ t('discover.noResults') }}</h3>
            <p class="text-gray-500 dark:text-gray-400 text-sm">{{ t('discover.noResultsDesc') }}</p>
          </div>

          <!-- Products Grid -->
          <div v-else>
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 sm:gap-4">
              <ProductCard
                v-for="product in products"
                :key="product.id"
                :product="product"
                @ai-search="handleAISearch"
                @manual-edit="handleManualEdit"
                @product-deleted="handleProductDeleted"
              />
            </div>

            <!-- Infinite Scroll: Loading More -->
            <div v-if="loadingMore" class="mt-6 flex justify-center py-4">
              <div class="flex items-center gap-3">
                <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 dark:border-blue-400"></div>
                <span class="text-sm text-gray-500 dark:text-gray-400">{{ t('common.loading') }}</span>
              </div>
            </div>

            <!-- Infinite Scroll: Observer Target -->
            <div ref="scrollObserverTarget" class="h-4"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Category Modal -->
    <transition name="fade">
      <div
        v-if="showCategoryModal"
        class="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-50"
        @click="showCategoryModal = false"
      >
        <div
          class="absolute bottom-0 left-0 right-0 bg-white dark:bg-gray-800 rounded-t-3xl max-h-[80vh] overflow-y-auto"
          @click.stop
        >
          <!-- Modal Header -->
          <div class="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 flex items-center justify-between">
            <h2 class="text-lg font-bold text-gray-900 dark:text-white">{{ t('discover.categories') }}</h2>
            <button
              @click="showCategoryModal = false"
              class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <svg class="w-5 h-5 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Category List -->
          <div class="p-4 space-y-1">
            <button
              @click="selectCategoryMobile(null)"
              :class="[
                'w-full text-left px-4 py-3 rounded-xl text-sm font-medium transition-all flex items-center justify-between',
                selectedCategory === null
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-md'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 active:bg-gray-100 dark:active:bg-gray-600'
              ]"
            >
              <span>{{ t('discover.allCategories') }}</span>
              <span class="text-xs opacity-75">{{ allTotal }}</span>
            </button>

            <button
              v-for="category in categories"
              :key="category.name"
              @click="selectCategoryMobile(category.name)"
              :class="[
                'w-full text-left px-4 py-3 rounded-xl text-sm font-medium transition-all flex items-center',
                selectedCategory === category.name
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-md'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 active:bg-gray-100 dark:active:bg-gray-600'
              ]"
            >
              <span class="text-lg mr-3">{{ category.icon }}</span>
              <span class="flex-1">{{ t(`categories.${category.name}`) }}</span>
              <span class="text-xs opacity-75">{{ getCategoryCount(category.name) }}</span>
            </button>

          </div>
        </div>
      </div>
    </transition>

    <!-- AI Search Dialog -->
    <ProductAISearchDialog
      :is-open="aiSearchDialogOpen"
      :product="selectedProduct"
      @close="closeAISearchDialog"
      @saved="handleMetadataSaved"
    />

    <!-- Image Search Dialog -->
    <ProductImageSearchDialog
      :is-open="imageSearchDialogOpen"
      :product="selectedProduct"
      @close="closeImageSearchDialog"
      @saved="handleImagesSaved"
    />

    <!-- Manual Edit Dialog -->
    <ProductManualEditDialog
      :is-open="manualEditDialogOpen"
      :product="selectedProduct"
      @close="closeManualEditDialog"
      @saved="handleManualEditSaved"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { productsApi } from '../api/products'
import ProductCard from '../components/product/ProductCard.vue'
import ProductAISearchDialog from '../components/product/ProductAISearchDialog.vue'
import ProductManualEditDialog from '../components/product/ProductManualEditDialog.vue'
import ProductImageSearchDialog from '../components/product/ProductImageSearchDialog.vue'
import { useAuthStore } from '../store/auth'
import { useDialog } from '../composables/useDialog'

const { t } = useI18n({ useScope: 'global' })
const { alert, confirm } = useDialog()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const categories = [
  { name: 'Graphics', icon: '🎨' },
  { name: 'Office', icon: '📊' },
  { name: 'Development', icon: '💻' },
  { name: 'Utility', icon: '🛠️' },
  { name: 'Media', icon: '🎬' },
  { name: 'OS', icon: '💿' },
  { name: 'Security', icon: '🔒' },
  { name: 'Network', icon: '🌐' },
  { name: 'Mac', icon: '🍎' },
  { name: 'Mobile', icon: '📱' },
  { name: 'Patch', icon: '🔧' },
  { name: 'Driver', icon: '⚙️' },
  { name: 'Source', icon: '📦' },
  { name: 'Backup', icon: '💾' },
  { name: 'Business', icon: '💼' },
  { name: 'Engineering', icon: '📐' },
  { name: 'Theme', icon: '🎭' },
  { name: 'Hardware', icon: '🔌' },
  { name: 'Font', icon: '🔤' },
  { name: 'Uncategorized', icon: '📂' }
]

const searchQuery = ref('')
const selectedCategory = ref(null)
const sortBy = ref('id')
const products = ref([])
const totalProducts = ref(0)
const categoryStats = ref({})
const loading = ref(true)
const loadingMore = ref(false)
const currentPage = ref(1)
const pageSize = 20
let loadVersion = 0  // race condition 방지용
let initialized = false  // 초기 로드 완료 전 watch 차단용

// Infinite scroll
const scrollObserverTarget = ref(null)
let scrollObserver = null

const hasMore = computed(() => products.value.length < totalProducts.value)

// "전체" 버튼용: categoryStats 합계 (개별 카테고리 필터와 무관하게 항상 전체 수량 표시)
const allTotal = computed(() => {
  const sum = Object.values(categoryStats.value).reduce((a, b) => a + b, 0)
  return sum > 0 ? sum : totalProducts.value
})

// Dialog state
const aiSearchDialogOpen = ref(false)
const manualEditDialogOpen = ref(false)
const imageSearchDialogOpen = ref(false)
const selectedProduct = ref(null)
const showCategoryModal = ref(false)

let searchTimeout = null

const handleSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    resetAndLoad()
  }, 500)
}

const resetAndLoad = () => {
  loading.value = true
  currentPage.value = 1
  products.value = []
  // totalProducts는 유지 (0으로 리셋하지 않음 — 새 결과 수신 시 갱신)
  loadProducts()
}

const loadProducts = async (append = false) => {
  const myVersion = ++loadVersion  // 현재 요청 버전 캡처

  if (append) {
    loadingMore.value = true
  } else {
    loading.value = true
  }
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
      sort_by: sortBy.value,
      sort_order: sortBy.value === 'id' ? 'desc' : 'asc'
    }

    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }

    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }

    const response = await productsApi.getAll(params)

    // 더 최신 요청이 시작됐으면 이 응답은 무시
    if (myVersion !== loadVersion) return

    if (append) {
      products.value = [...products.value, ...response.data.products]
    } else {
      products.value = response.data.products
    }
    totalProducts.value = response.data.total
  } catch (error) {
    console.error('Failed to load products:', error)
    if (myVersion === loadVersion && !append) {
      products.value = []
      totalProducts.value = 0
    }
  } finally {
    // 항상 로딩 상태 초기화 (버전 체크 없음 — stuck spinner 방지)
    if (!append) {
      loading.value = false
    } else if (myVersion === loadVersion) {
      loadingMore.value = false
    }
  }
}

const loadMore = () => {
  if (loadingMore.value || !hasMore.value) return
  currentPage.value++
  loadProducts(true)
}

// 삭제된 파일 일괄 정리
const cleanupDeletedFiles = async () => {
  const confirmed = await confirm.danger(t('discover.cleanupConfirm'))
  if (!confirmed) {
    return
  }

  try {
    const response = await productsApi.cleanupDeleted()
    const { deleted_versions, deleted_products } = response.data

    await alert.success(t('discover.cleanupSuccess', { deleted_versions, deleted_products }))

    // 목록 새로고침
    resetAndLoad()
    await loadCategoryStats()
  } catch (error) {
    console.error('Failed to cleanup deleted files:', error)
    await alert.error(t('discover.cleanupFailed'))
  }
}

// 제품 삭제 후 처리
const handleProductDeleted = async (productId) => {
  // 삭제된 제품을 목록에서 제거
  products.value = products.value.filter(p => p.id !== productId)
  totalProducts.value = Math.max(0, totalProducts.value - 1)
  await loadCategoryStats()
}


const loadCategoryStats = async () => {
  try {
    const response = await productsApi.getCategoryStats()
    categoryStats.value = response.data.reduce((acc, stat) => {
      acc[stat.category] = stat.count
      return acc
    }, {})
  } catch (error) {
    console.error('Failed to load category stats:', error)
    categoryStats.value = {}
  }
}

const getCategoryCount = (category) => {
  return categoryStats.value[category] || 0
}

const selectCategory = (category) => {
  selectedCategory.value = category
  resetAndLoad()
}

const selectCategoryMobile = (category) => {
  selectedCategory.value = category
  showCategoryModal.value = false
  resetAndLoad()
}

const goToScan = () => {
  router.push('/admin')
}

// Dialog handlers
const handleAISearch = (product) => {
  selectedProduct.value = product
  aiSearchDialogOpen.value = true
}

const handleManualEdit = (product) => {
  selectedProduct.value = product
  manualEditDialogOpen.value = true
}

const closeAISearchDialog = () => {
  aiSearchDialogOpen.value = false
  selectedProduct.value = null
}

const handleMetadataSaved = async (metadata) => {
  // Refresh the product list to show updated data
  resetAndLoad()
}

const closeManualEditDialog = () => {
  manualEditDialogOpen.value = false
  selectedProduct.value = null
}

const handleManualEditSaved = async (data) => {
  // Refresh the product list to show updated data
  resetAndLoad()
}

const closeImageSearchDialog = () => {
  imageSearchDialogOpen.value = false
  selectedProduct.value = null
}

const handleImagesSaved = async () => {
  // Refresh the product list to show updated data
  resetAndLoad()
}

const setupScrollObserver = () => {
  if (scrollObserver) scrollObserver.disconnect()

  // 모바일에서도 동작하도록 main-content-area를 root로 지정
  const scrollContainer = document.querySelector('.main-content-area')

  scrollObserver = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting && hasMore.value && !loading.value && !loadingMore.value) {
        loadMore()
      }
    },
    {
      root: scrollContainer || null,
      rootMargin: '200px'
    }
  )

  if (scrollObserverTarget.value) {
    scrollObserver.observe(scrollObserverTarget.value)
  }
}

onMounted(async () => {
  if (route.query.category) {
    selectedCategory.value = route.query.category
  }
  if (route.query.search) {
    searchQuery.value = route.query.search
  }
  await loadProducts()
  loadCategoryStats()
  await nextTick()
  setupScrollObserver()
  initialized = true  // 초기 로드 완료
})

onUnmounted(() => {
  if (scrollObserver) {
    scrollObserver.disconnect()
  }
})

watch(
  () => route.query,
  (newQuery) => {
    // 초기 로드 완료 전에는 watch 무시 (onMounted의 loadProducts와 race condition 방지)
    if (!initialized) return
    let changed = false
    if ((newQuery.category || null) !== selectedCategory.value) {
      selectedCategory.value = newQuery.category || null
      changed = true
    }
    if ((newQuery.search || '') !== searchQuery.value) {
      searchQuery.value = newQuery.search || ''
      changed = true
    }
    if (changed) resetAndLoad()
  }
)
</script>

<style scoped>
/* Fade transition for modal */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-active .absolute,
.fade-leave-active .absolute {
  transition: transform 0.3s ease;
}

.fade-enter-from .absolute {
  transform: translateY(100%);
}

.fade-leave-to .absolute {
  transform: translateY(100%);
}
</style>
