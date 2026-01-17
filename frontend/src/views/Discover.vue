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
            <span class="text-xs opacity-75">{{ totalProducts }}</span>
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
          <div class="flex items-center gap-2 sm:gap-3">
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
                <svg class="w-4 h-4 sm:w-5 sm:h-5 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                v-model="searchQuery"
                type="text"
                :placeholder="t('discover.searchPlaceholder')"
                class="block w-full pl-10 sm:pl-12 pr-3 sm:pr-4 py-2.5 sm:py-3 border border-gray-200 dark:border-gray-600 rounded-lg sm:rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                @input="handleSearch"
              />
            </div>
            <select
              v-model="sortBy"
              class="px-3 sm:px-4 py-2.5 sm:py-3 border border-gray-200 dark:border-gray-600 rounded-lg sm:rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white flex-shrink-0"
              @change="loadProducts"
            >
              <option value="id">{{ t('discover.sortByLatest') }}</option>
              <option value="title">{{ t('discover.sortByName') }}</option>
              <option value="category">{{ t('discover.sortByCategory') }}</option>
            </select>
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
              />
            </div>

            <!-- Pagination -->
            <div v-if="totalProducts > pageSize" class="mt-8 flex justify-center">
              <nav class="flex items-center gap-1">
                <button
                  @click="goToPage(currentPage - 1)"
                  :disabled="currentPage === 1"
                  class="px-3 py-2 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>

                <button
                  v-for="page in visiblePages"
                  :key="page"
                  @click="goToPage(page)"
                  :class="[
                    'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                    page === currentPage
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-md'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  ]"
                >
                  {{ page }}
                </button>

                <button
                  @click="goToPage(currentPage + 1)"
                  :disabled="currentPage === totalPages"
                  class="px-3 py-2 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </nav>
            </div>
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
              <span class="text-xs opacity-75">{{ totalProducts }}</span>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { productsApi } from '../api/products'
import ProductCard from '../components/product/ProductCard.vue'
import ProductAISearchDialog from '../components/product/ProductAISearchDialog.vue'
import ProductManualEditDialog from '../components/product/ProductManualEditDialog.vue'
import { useAuthStore } from '../store/auth'

const { t } = useI18n({ useScope: 'global' })

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
const currentPage = ref(1)
const pageSize = 20

// Dialog state
const aiSearchDialogOpen = ref(false)
const manualEditDialogOpen = ref(false)
const selectedProduct = ref(null)
const showCategoryModal = ref(false)

const totalPages = computed(() => Math.ceil(totalProducts.value / pageSize))

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

let searchTimeout = null

const handleSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadProducts()
  }, 500)
}

const loadProducts = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
      sort_by: sortBy.value,
      sort_order: 'desc'
    }

    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }

    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }

    const response = await productsApi.getAll(params)
    products.value = response.data.products
    totalProducts.value = response.data.total
  } catch (error) {
    console.error('Failed to load products:', error)
    products.value = []
    totalProducts.value = 0
  } finally {
    loading.value = false
  }
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
  currentPage.value = 1
  loadProducts()
}

const selectCategoryMobile = (category) => {
  selectedCategory.value = category
  currentPage.value = 1
  showCategoryModal.value = false
  loadProducts()
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadProducts()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
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
  console.log('Metadata saved:', metadata)
  // Refresh the product list to show updated data
  await loadProducts()
}

const closeManualEditDialog = () => {
  manualEditDialogOpen.value = false
  selectedProduct.value = null
}

const handleManualEditSaved = async (data) => {
  console.log('Manual edit saved:', data)
  // Refresh the product list to show updated data
  await loadProducts()
}

onMounted(() => {
  if (route.query.category) {
    selectedCategory.value = route.query.category
  }
  if (route.query.search) {
    searchQuery.value = route.query.search
  }
  loadProducts()
  loadCategoryStats()
})

watch(
  () => route.query,
  (newQuery) => {
    if (newQuery.category !== selectedCategory.value) {
      selectedCategory.value = newQuery.category || null
      currentPage.value = 1
      loadProducts()
    }
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
