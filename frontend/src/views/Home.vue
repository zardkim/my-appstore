<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="bg-gradient-to-r from-blue-500 to-purple-600 px-4 sm:px-6 lg:px-8 py-6 sm:py-8 lg:py-12 text-white">
      <div class="max-w-7xl">
        <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold mb-2">{{ t('home.welcome') }}! 👋</h1>
        <p class="text-blue-100 text-sm sm:text-base lg:text-lg">{{ t('auth.personalLibrary') }}</p>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 sm:gap-4 lg:gap-6 mb-6 lg:mb-8">
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-4 sm:p-5 lg:p-6 border border-gray-100 dark:border-gray-700 hover:shadow-lg transition-shadow">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">{{ t('home.totalProducts') }}</p>
              <p class="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {{ stats.total_products }}
              </p>
            </div>
            <div class="p-2 sm:p-3 lg:p-4 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900 dark:to-purple-900 rounded-2xl">
              <svg class="w-6 h-6 sm:w-7 sm:h-7 lg:w-8 lg:h-8 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-4 sm:p-5 lg:p-6 border border-gray-100 dark:border-gray-700 hover:shadow-lg transition-shadow cursor-pointer" @click="$router.push('/filename-violations')">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">{{ t('home.incompleteProducts') }}</p>
              <p class="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                {{ stats.incomplete_count }}
              </p>
            </div>
            <div class="p-2 sm:p-3 lg:p-4 bg-gradient-to-br from-orange-100 to-red-100 dark:from-orange-900 dark:to-red-900 rounded-2xl">
              <svg class="w-6 h-6 sm:w-7 sm:h-7 lg:w-8 lg:h-8 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-4 sm:p-5 lg:p-6 border border-gray-100 dark:border-gray-700 hover:shadow-lg transition-shadow">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">{{ t('home.lastScan') }}</p>
              <p class="text-sm sm:text-base lg:text-lg font-semibold text-gray-900 dark:text-white mt-2">{{ lastScanFormatted }}</p>
            </div>
            <div class="p-2 sm:p-3 lg:p-4 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900 dark:to-pink-900 rounded-2xl">
              <svg class="w-6 h-6 sm:w-7 sm:h-7 lg:w-8 lg:h-8 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Category Stats -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-4 sm:p-5 lg:p-6 border border-gray-100 dark:border-gray-700 mb-6 lg:mb-8" v-if="Object.keys(stats.category_stats).length > 0">
        <h2 class="text-lg sm:text-xl font-bold text-gray-900 dark:text-white mb-4 sm:mb-5 lg:mb-6 flex items-center">
          <span class="mr-2">📊</span>
          {{ t('home.categoryStats') }}
        </h2>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4">
          <button
            v-for="(count, category) in stats.category_stats"
            :key="category"
            class="flex flex-col items-center justify-center p-3 sm:p-4 lg:p-5 bg-gradient-to-br from-gray-50 to-white dark:from-gray-700 dark:to-gray-800 rounded-2xl hover:from-blue-50 hover:to-purple-50 dark:hover:from-blue-900 dark:hover:to-purple-900 transition-all cursor-pointer border border-gray-100 dark:border-gray-600 hover:border-blue-200 dark:hover:border-blue-500 hover:shadow-lg transform hover:-translate-y-1 group active:scale-95"
            @click="goToCategory(category)"
          >
            <span class="text-2xl sm:text-3xl mb-1 sm:mb-2 transform group-hover:scale-110 transition-transform">{{ getCategoryIcon(category) }}</span>
            <p class="text-[10px] sm:text-xs font-medium text-gray-600 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors text-center">{{ t(`categories.${category}`) }}</p>
            <p class="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ count }}</p>
          </button>
        </div>
      </div>

      <!-- Recent Products -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-4 sm:p-5 lg:p-6 border border-gray-100 dark:border-gray-700">
        <div class="flex items-center justify-between mb-4 sm:mb-5 lg:mb-6">
          <h2 class="text-lg sm:text-xl font-bold text-gray-900 dark:text-white flex items-center">
            <span class="mr-2">🆕</span>
            {{ t('home.recentlyAdded') }}
          </h2>
          <router-link
            to="/discover"
            class="text-xs sm:text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 flex items-center group"
          >
            {{ t('home.viewAll') }}
            <svg class="w-3 h-3 sm:w-4 sm:h-4 ml-1 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </router-link>
        </div>

        <div v-if="loading" class="flex justify-center py-12 sm:py-16">
          <div class="text-center">
            <div class="animate-spin rounded-full h-12 w-12 sm:h-16 sm:w-16 border-b-2 border-blue-600 dark:border-blue-400 mx-auto mb-4"></div>
            <p class="text-gray-500 dark:text-gray-400 text-sm">{{ t('common.loading') }}</p>
          </div>
        </div>

        <div v-else-if="recentProducts.length === 0" class="text-center py-12 sm:py-16">
          <div class="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-gray-100 to-gray-50 dark:from-gray-700 dark:to-gray-800 rounded-3xl flex items-center justify-center">
            <svg class="w-10 h-10 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
          </div>
          <h3 class="text-base sm:text-lg font-semibold text-gray-900 dark:text-white mb-2">{{ t('home.noProducts') }}</h3>
          <p class="text-gray-500 dark:text-gray-400 text-xs sm:text-sm mb-6">{{ t('home.noProductsDesc') }}</p>
          <router-link
            v-if="isAdmin"
            to="/settings"
            class="inline-flex items-center px-4 sm:px-6 py-2.5 sm:py-3 text-sm sm:text-base bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all shadow-md hover:shadow-lg font-medium"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            {{ t('home.scanPrograms') }}
          </router-link>
        </div>

        <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-3 sm:gap-4">
          <ProductCard
            v-for="product in recentProducts"
            :key="product.id"
            :product="product"
            @ai-search="handleAISearch"
            @manual-edit="handleManualEdit"
          />
        </div>
      </div>
    </div>

    <!-- AI Search Dialog -->
    <ProductAISearchDialog
      :is-open="aiSearchDialogOpen"
      :product="selectedProduct"
      @close="closeAISearchDialog"
      @saved="handleMetadataSaved"
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
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../store/auth'
import { productsApi } from '../api/products'
import ProductCard from '../components/product/ProductCard.vue'
import ProductAISearchDialog from '../components/product/ProductAISearchDialog.vue'
import ProductManualEditDialog from '../components/product/ProductManualEditDialog.vue'

const router = useRouter()
const authStore = useAuthStore()
const { t, locale } = useI18n({ useScope: 'global' })

const loading = ref(true)
const stats = ref({
  total_products: 0,
  incomplete_count: 0,
  category_stats: {},
  last_scan: 'Never'
})
const recentProducts = ref([])

// Dialog state
const aiSearchDialogOpen = ref(false)
const manualEditDialogOpen = ref(false)
const selectedProduct = ref(null)

const isAdmin = computed(() => authStore.user?.role === 'admin')

const lastScanFormatted = computed(() => {
  if (stats.value.last_scan === 'Never') return t('home.never')
  try {
    const date = new Date(stats.value.last_scan)
    const dateLocale = locale.value === 'ko' ? 'ko-KR' : 'en-US'
    return date.toLocaleDateString(dateLocale, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return stats.value.last_scan
  }
})

const categoryIcons = {
  'Graphics': '🎨',
  'Office': '📊',
  'Development': '💻',
  'Utility': '🛠️',
  'Media': '🎬',
  'OS': '💿',
  'Security': '🔒',
  'Network': '🌐',
  'Mac': '🍎',
  'Mobile': '📱',
  'Patch': '🔧',
  'Driver': '⚙️',
  'Source': '📦',
  'Backup': '💾',
  'Portable': '🎒',
  'Business': '💼',
  'Engineering': '📐',
  'Theme': '🎭',
  'Hardware': '🔌'
}

const getCategoryIcon = (category) => {
  return categoryIcons[category] || '📦'
}

const fetchStats = async () => {
  try {
    const response = await productsApi.getStats()
    stats.value = response.data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
    stats.value = {
      total_products: 0,
      incomplete_count: 0,
      category_stats: {},
      last_scan: 'Never'
    }
  }
}

const fetchRecentProducts = async () => {
  try {
    const response = await productsApi.getRecent(12)
    recentProducts.value = response.data
  } catch (error) {
    console.error('Failed to fetch recent products:', error)
    recentProducts.value = []
  }
}

const goToCategory = (category) => {
  router.push(`/discover?category=${category}`)
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

const closeManualEditDialog = () => {
  manualEditDialogOpen.value = false
  selectedProduct.value = null
}

const handleMetadataSaved = async () => {
  // Refresh the product list to show updated data
  await fetchRecentProducts()
}

const handleManualEditSaved = async () => {
  // Refresh the product list to show updated data
  await fetchRecentProducts()
}

onMounted(async () => {
  loading.value = true
  await Promise.all([
    fetchStats(),
    fetchRecentProducts()
  ])
  loading.value = false
})
</script>
