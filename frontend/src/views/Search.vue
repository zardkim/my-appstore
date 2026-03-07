<template>
  <div class="max-w-5xl mx-auto p-4 sm:p-6 lg:p-8 pb-20 lg:pb-8">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-4">{{ t('unifiedSearch.title') }}</h1>
      <!-- 재검색 입력창 -->
      <div class="flex items-center gap-2">
        <div class="relative flex-1">
          <svg class="w-5 h-5 text-gray-400 absolute left-3 top-2.5 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            v-model="searchQuery"
            @keyup.enter="doSearch"
            type="text"
            :placeholder="t('unifiedSearch.placeholder')"
            class="w-full pl-10 pr-4 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
          />
        </div>
        <button
          @click="doSearch"
          class="px-5 py-2.5 bg-blue-500 text-white rounded-xl text-sm font-medium hover:bg-blue-600 transition-colors flex-shrink-0"
        >
          {{ t('common.search') }}
        </button>
      </div>
    </div>

    <!-- 검색어 없음 -->
    <div v-if="!hasSearched" class="flex flex-col items-center justify-center py-20 text-gray-400 dark:text-gray-500">
      <svg class="w-16 h-16 mb-4 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <p class="text-lg font-medium">{{ t('unifiedSearch.enterQuery') }}</p>
      <p class="text-sm mt-1">{{ t('unifiedSearch.enterQueryDesc') }}</p>
    </div>

    <!-- 검색 결과 -->
    <template v-else>
      <!-- 결과 요약 -->
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-5">
        <span class="font-semibold text-gray-700 dark:text-gray-200">"{{ currentQuery }}"</span>
        {{ t('unifiedSearch.resultsFor') }}
        {{ totalCount }}{{ t('unifiedSearch.resultsCount') }}
      </p>

      <!-- 스토어 (Products) -->
      <section class="mb-6">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-base font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2">
            <span class="text-lg">🏪</span> {{ t('nav.discover') }}
            <span v-if="!productsLoading" class="text-xs text-gray-400 dark:text-gray-500 font-normal">({{ productsTotal }})</span>
          </h2>
          <router-link
            v-if="productsTotal > 0"
            :to="`/discover?search=${encodeURIComponent(currentQuery)}`"
            class="text-sm text-blue-500 hover:text-blue-600 hover:underline"
          >
            {{ t('unifiedSearch.viewAll') }}
          </router-link>
        </div>

        <div v-if="productsLoading" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-6 flex justify-center">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
        </div>
        <div v-else-if="products.length === 0" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4 text-sm text-gray-400 dark:text-gray-500 text-center">
          {{ t('unifiedSearch.noResults') }}
        </div>
        <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          <router-link
            v-for="product in products"
            :key="product.id"
            :to="`/product/${product.id}`"
            class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-3 flex flex-col gap-2 hover:shadow-md hover:border-blue-200 dark:hover:border-blue-700 transition-all"
          >
            <div class="flex items-center gap-2">
              <img
                v-if="product.icon_url"
                :src="product.icon_url"
                class="w-8 h-8 rounded-lg object-cover flex-shrink-0"
                @error="e => e.target.style.display='none'"
              />
              <div v-else class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center flex-shrink-0">
                <span class="text-white text-xs font-bold">{{ (product.title || '?').charAt(0) }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ product.title }}</p>
                <p class="text-xs text-gray-400 dark:text-gray-500 truncate">{{ product.vendor || product.category }}</p>
              </div>
            </div>
          </router-link>
        </div>
      </section>

      <!-- 팁&테크 (Tips/Posts) -->
      <section class="mb-6">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-base font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2">
            <span class="text-lg">📝</span> {{ t('nav.tips') }}
            <span v-if="!tipsLoading" class="text-xs text-gray-400 dark:text-gray-500 font-normal">({{ tipsTotal }})</span>
          </h2>
          <router-link
            v-if="tipsTotal > 0"
            :to="`/tips?search=${encodeURIComponent(currentQuery)}`"
            class="text-sm text-blue-500 hover:text-blue-600 hover:underline"
          >
            {{ t('unifiedSearch.viewAll') }}
          </router-link>
        </div>

        <div v-if="tipsLoading" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-6 flex justify-center">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
        </div>
        <div v-else-if="tips.length === 0" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4 text-sm text-gray-400 dark:text-gray-500 text-center">
          {{ t('unifiedSearch.noResults') }}
        </div>
        <div v-else class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 divide-y divide-gray-100 dark:divide-gray-700 overflow-hidden">
          <router-link
            v-for="post in tips"
            :key="post.id"
            :to="`/tips/${post.id}`"
            class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <span class="text-gray-300 dark:text-gray-600 text-xs flex-shrink-0">#{{ post.id }}</span>
            <span class="flex-1 font-medium text-gray-900 dark:text-white text-sm truncate">{{ post.title }}</span>
            <div class="flex items-center gap-2 flex-shrink-0">
              <span class="text-xs text-gray-400 dark:text-gray-500">{{ post.author_username }}</span>
              <span v-if="post.view_count" class="text-xs text-gray-300 dark:text-gray-600">👁 {{ post.view_count }}</span>
            </div>
          </router-link>
        </div>
      </section>

      <!-- 스캔목록 (Admin only) -->
      <section v-if="isAdmin" class="mb-6">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-base font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2">
            <span class="text-lg">🔍</span> {{ t('nav.detectedList') }}
            <span v-if="!scanLoading" class="text-xs text-gray-400 dark:text-gray-500 font-normal">({{ scanTotal }})</span>
          </h2>
          <router-link
            v-if="scanTotal > 0"
            :to="`/scan-list?search=${encodeURIComponent(currentQuery)}`"
            class="text-sm text-blue-500 hover:text-blue-600 hover:underline"
          >
            {{ t('unifiedSearch.viewAll') }}
          </router-link>
        </div>

        <div v-if="scanLoading" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-6 flex justify-center">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
        </div>
        <div v-else-if="scanItems.length === 0" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4 text-sm text-gray-400 dark:text-gray-500 text-center">
          {{ t('unifiedSearch.noResults') }}
        </div>
        <div v-else class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 divide-y divide-gray-100 dark:divide-gray-700 overflow-hidden">
          <router-link
            v-for="item in scanItems"
            :key="item.id"
            to="/scan-list"
            class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <span class="text-lg flex-shrink-0">
              {{ item.classification === 'installation_video' ? '🎬' : item.classification === 'patch' ? '🔧' : item.classification === 'language_pack' ? '🌐' : '📦' }}
            </span>
            <span class="flex-1 text-sm text-gray-900 dark:text-white truncate">{{ item.file_name }}</span>
            <span class="text-xs text-gray-400 dark:text-gray-500 flex-shrink-0 bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded-full">{{ item.classification }}</span>
          </router-link>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../store/auth'
import { productsApi } from '../api/products'
import { postsApi } from '../api/posts'
import { filenameViolationsApi } from '../api/filenameViolations'

const { t } = useI18n({ useScope: 'global' })
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isAdmin = computed(() => authStore.user?.role === 'admin')

const searchQuery = ref('')
const currentQuery = ref('')
const hasSearched = ref(false)

const products = ref([])
const productsTotal = ref(0)
const productsLoading = ref(false)

const tips = ref([])
const tipsTotal = ref(0)
const tipsLoading = ref(false)

const scanItems = ref([])
const scanTotal = ref(0)
const scanLoading = ref(false)

const totalCount = computed(() => productsTotal.value + tipsTotal.value + (isAdmin.value ? scanTotal.value : 0))

const doSearch = () => {
  const q = searchQuery.value.trim()
  if (!q) return
  router.replace({ path: '/search', query: { q } })
}

const runSearch = async (q) => {
  if (!q) return
  currentQuery.value = q
  hasSearched.value = true

  // 병렬 검색
  productsLoading.value = true
  tipsLoading.value = true
  if (isAdmin.value) scanLoading.value = true

  const [productsRes, tipsRes, scanRes] = await Promise.allSettled([
    productsApi.getAll({ search: q, limit: 8, sort_by: 'id', sort_order: 'desc' }),
    postsApi.getPosts({ search: q, limit: 6 }),
    isAdmin.value ? filenameViolationsApi.getScanItems({ search: q, limit: 6, resolved: false }) : Promise.resolve(null)
  ])

  // 스토어
  if (productsRes.status === 'fulfilled') {
    products.value = productsRes.value.data?.products || []
    productsTotal.value = productsRes.value.data?.total || 0
  } else {
    products.value = []
    productsTotal.value = 0
  }
  productsLoading.value = false

  // 팁&테크
  if (tipsRes.status === 'fulfilled') {
    const data = tipsRes.value.data
    const items = Array.isArray(data) ? data : (data?.items || [])
    tips.value = items.filter(p => !p.is_notice).slice(0, 6)
    tipsTotal.value = Array.isArray(data) ? tips.value.length : (data?.total || tips.value.length)
  } else {
    tips.value = []
    tipsTotal.value = 0
  }
  tipsLoading.value = false

  // 스캔목록 (관리자)
  if (isAdmin.value) {
    if (scanRes.status === 'fulfilled' && scanRes.value) {
      scanItems.value = scanRes.value.data?.items || []
      scanTotal.value = scanRes.value.data?.total || scanItems.value.length
    } else {
      scanItems.value = []
      scanTotal.value = 0
    }
    scanLoading.value = false
  }
}

onMounted(() => {
  const q = route.query.q || ''
  if (q) {
    searchQuery.value = q
    runSearch(q)
  }
})

watch(() => route.query.q, (q) => {
  if (q) {
    searchQuery.value = q
    runSearch(q)
  }
})
</script>
