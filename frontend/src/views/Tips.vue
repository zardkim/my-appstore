<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="bg-gradient-to-r from-blue-500 to-purple-600 dark:from-blue-700 dark:to-purple-800 px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8 text-white">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold mb-1 sm:mb-2">{{ t('tips.title') }}</h1>
          <p class="text-sm sm:text-base text-blue-100 dark:text-blue-200">{{ t('tips.description') }}</p>
        </div>
        <button @click="goToWrite" class="px-4 sm:px-5 lg:px-6 py-2 sm:py-2.5 lg:py-3 bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400 rounded-lg sm:rounded-xl hover:shadow-lg transition-all font-medium flex items-center text-sm sm:text-base self-start sm:self-auto">
          <svg class="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          {{ t('tips.writeNew') }}
        </button>
      </div>
    </div>

    <!-- Search & Filter -->
    <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 sm:px-6 lg:px-8 py-3 sm:py-4">
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center sm:justify-between gap-3">
        <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-3">
          <select v-model="selectedCategory" class="px-3 sm:px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg sm:rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm">
            <option value="all">{{ t('tips.allCategories') }}</option>
            <option value="tip">{{ t('tips.categoryTip') }}</option>
            <option value="tech">{{ t('tips.categoryTech') }}</option>
            <option value="tutorial">{{ t('tips.categoryTutorial') }}</option>
            <option value="qna">{{ t('tips.categoryQna') }}</option>
            <option value="news">{{ t('tips.categoryNews') }}</option>
          </select>
          <select v-model="sortBy" class="px-3 sm:px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg sm:rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm">
            <option value="latest">{{ t('tips.sortLatest') }}</option>
            <option value="views">{{ t('tips.sortViews') }}</option>
            <option value="comments">{{ t('tips.sortComments') }}</option>
          </select>
        </div>
        <div class="relative">
          <input v-model="searchQuery" type="text" :placeholder="t('tips.searchPlaceholder')" class="w-full sm:w-64 lg:w-80 pl-9 sm:pl-10 pr-3 sm:pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg sm:rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 text-sm">
          <svg class="w-4 h-4 sm:w-5 sm:h-5 text-gray-400 dark:text-gray-500 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Board List -->
    <div class="flex-1 overflow-y-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 pb-20 lg:pb-6">
      <div>
        <!-- Desktop Table View -->
        <div class="hidden md:block bg-white dark:bg-gray-800 rounded-xl sm:rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
          <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
              <tr>
                <th class="px-4 lg:px-6 py-3 lg:py-4 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase w-20">{{ t('tips.number') }}</th>
                <th class="px-4 lg:px-6 py-3 lg:py-4 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase w-32">{{ t('tips.category') }}</th>
                <th class="px-4 lg:px-6 py-3 lg:py-4 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">{{ t('tips.titleColumn') }}</th>
                <th class="px-4 lg:px-6 py-3 lg:py-4 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase w-32">{{ t('tips.author') }}</th>
                <th class="px-4 lg:px-6 py-3 lg:py-4 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase w-24">{{ t('tips.views') }}</th>
                <th class="px-4 lg:px-6 py-3 lg:py-4 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase w-24">{{ t('tips.comments') }}</th>
                <th class="px-4 lg:px-6 py-3 lg:py-4 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase w-40">{{ t('tips.date') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <!-- Notice Posts -->
              <tr v-for="post in noticePosts" :key="'notice-' + post.id" class="bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30 cursor-pointer transition-colors" @click="goToDetail(post.id)">
                <td class="px-6 py-4">
                  <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-bold bg-red-500 dark:bg-red-600 text-white">{{ t('tips.notice') }}</span>
                </td>
                <td class="px-6 py-4">
                  <span :class="getCategoryStyle(post.category)">{{ getCategoryLabel(post.category) }}</span>
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center">
                    <svg v-if="post.is_notice" class="w-4 h-4 text-red-500 dark:text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
                    </svg>
                    <span class="font-medium text-gray-900 dark:text-white">{{ post.title }}</span>
                    <span v-if="isNew(post.created_at)" class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-300">{{ t('tips.new') }}</span>
                  </div>
                </td>
                <td class="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">{{ post.author_username }}</td>
                <td class="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">{{ post.views }}</td>
                <td class="px-6 py-4 text-center text-sm">
                  <span class="text-blue-600 dark:text-blue-400 font-medium">{{ post.comments_count }}</span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{{ formatDate(post.created_at) }}</td>
              </tr>

              <!-- Normal Posts -->
              <tr v-for="post in paginatedPosts" :key="post.id" class="hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors" @click="goToDetail(post.id)">
                <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{{ post.id }}</td>
                <td class="px-6 py-4">
                  <span :class="getCategoryStyle(post.category)">{{ getCategoryLabel(post.category) }}</span>
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center">
                      <span class="font-medium text-gray-900 dark:text-white">{{ post.title }}</span>
                      <span v-if="isNew(post.created_at)" class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-300">{{ t('tips.new') }}</span>
                      <span v-if="post.has_image" class="ml-2">📷</span>
                    </div>
                    <button
                      v-if="authStore.isAuthenticated"
                      @click.stop="toggleScrap(post)"
                      class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                      :class="isScraped(post.id) ? 'text-amber-500' : 'text-gray-400 dark:text-gray-500'"
                    >
                      <svg class="w-4 h-4" :fill="isScraped(post.id) ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                      </svg>
                    </button>
                  </div>
                </td>
                <td class="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">{{ post.author_username }}</td>
                <td class="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">{{ post.views }}</td>
                <td class="px-6 py-4 text-center text-sm">
                  <span v-if="post.comments_count > 0" class="text-blue-600 dark:text-blue-400 font-medium">{{ post.comments_count }}</span>
                  <span v-else class="text-gray-400 dark:text-gray-500">0</span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{{ formatDate(post.created_at) }}</td>
              </tr>

              <!-- Empty State -->
              <tr v-if="paginatedPosts.length === 0 && noticePosts.length === 0">
                <td colspan="7" class="px-6 py-12 text-center">
                  <div class="text-gray-400 dark:text-gray-500">
                    <svg class="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p class="text-lg font-medium">{{ t('tips.noPosts') }}</p>
                    <p class="text-sm mt-2">{{ t('tips.noPostsDesc') }}</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Card View -->
        <div class="md:hidden space-y-3">
          <!-- Notice Posts -->
          <div
            v-for="post in noticePosts"
            :key="'notice-' + post.id"
            @click="goToDetail(post.id)"
            class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4 cursor-pointer active:scale-[0.98] transition-all"
          >
            <div class="flex items-start justify-between gap-2 mb-2">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-bold bg-red-500 text-white">{{ t('tips.notice') }}</span>
                <span :class="getCategoryStyle(post.category)">{{ getCategoryLabel(post.category) }}</span>
                <span v-if="isNew(post.created_at)" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-300">{{ t('tips.new') }}</span>
              </div>
            </div>
            <h3 class="font-medium text-gray-900 dark:text-white mb-2 line-clamp-2">{{ post.title }}</h3>
            <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
              <div class="flex items-center gap-3">
                <span>{{ post.author_username }}</span>
                <span>{{ t('tips.views') }} {{ post.views }}</span>
                <span class="text-blue-600 dark:text-blue-400 font-medium">{{ t('tips.comments') }} {{ post.comments_count }}</span>
              </div>
              <span>{{ formatDate(post.created_at) }}</span>
            </div>
          </div>

          <!-- Normal Posts -->
          <div
            v-for="post in paginatedPosts"
            :key="post.id"
            @click="goToDetail(post.id)"
            class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4 cursor-pointer hover:shadow-md active:scale-[0.98] transition-all"
          >
            <div class="flex items-start justify-between gap-2 mb-2">
              <div class="flex items-center gap-2 flex-wrap flex-1">
                <span :class="getCategoryStyle(post.category)">{{ getCategoryLabel(post.category) }}</span>
                <span v-if="isNew(post.created_at)" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-300">{{ t('tips.new') }}</span>
                <span v-if="post.has_image">📷</span>
              </div>
              <button
                v-if="authStore.isAuthenticated"
                @click.stop="toggleScrap(post)"
                class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors flex-shrink-0"
                :class="isScraped(post.id) ? 'text-amber-500' : 'text-gray-400 dark:text-gray-500'"
              >
                <svg class="w-4 h-4" :fill="isScraped(post.id) ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                </svg>
              </button>
            </div>
            <h3 class="font-medium text-gray-900 dark:text-white mb-2 line-clamp-2">{{ post.title }}</h3>
            <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
              <div class="flex items-center gap-3">
                <span>{{ post.author_username }}</span>
                <span>{{ t('tips.views') }} {{ post.views }}</span>
                <span v-if="post.comments_count > 0" class="text-blue-600 dark:text-blue-400 font-medium">{{ t('tips.comments') }} {{ post.comments_count }}</span>
              </div>
              <span>{{ formatDate(post.created_at) }}</span>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="paginatedPosts.length === 0 && noticePosts.length === 0" class="bg-white dark:bg-gray-800 rounded-xl p-12 text-center">
            <div class="text-gray-400 dark:text-gray-500">
              <svg class="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p class="text-lg font-medium">{{ t('tips.noPosts') }}</p>
              <p class="text-sm mt-2">{{ t('tips.noPostsDesc') }}</p>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="flex items-center justify-center mt-4 sm:mt-6 gap-1 sm:gap-2">
          <!-- Previous Button -->
          <button
            @click="previousPage"
            :disabled="currentPage === 1"
            class="px-2 sm:px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-gray-300 transition-colors"
          >
            <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <!-- Page Numbers -->
          <button
            v-for="page in pageNumbers"
            :key="page"
            @click="goToPage(page)"
            :class="[
              'px-3 sm:px-4 py-2 rounded-lg font-medium transition-colors text-sm sm:text-base',
              page === currentPage
                ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                : 'border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
            ]"
          >
            {{ page }}
          </button>

          <!-- Next Button -->
          <button
            @click="nextPage"
            :disabled="currentPage === totalPages"
            class="px-2 sm:px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-gray-300 transition-colors"
          >
            <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../store/auth'
import { scrapsApi } from '../api/scraps'
import { postsApi } from '../api/posts'
import { useDialog } from '../composables/useDialog'

const { t } = useI18n({ useScope: 'global' })
const router = useRouter()
const authStore = useAuthStore()
const { alert } = useDialog()
const isAdmin = computed(() => authStore.user?.role === 'admin')

const selectedCategory = ref('all')
const sortBy = ref('latest')
const searchQuery = ref('')
const scrapedPostIds = ref(new Set())
const loading = ref(false)

// Pagination
const currentPage = ref(1)
const itemsPerPage = ref(20)

// Posts data (loaded from API)
const posts = ref([])

const noticePosts = computed(() => posts.value.filter(p => p.is_notice))

const filteredPosts = computed(() => {
  let result = posts.value.filter(p => !p.is_notice)

  // Category filter
  if (selectedCategory.value !== 'all') {
    result = result.filter(p => p.category === selectedCategory.value)
  }

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(p =>
      p.title.toLowerCase().includes(query) ||
      p.content.toLowerCase().includes(query)
    )
  }

  // Sort
  if (sortBy.value === 'views') {
    result.sort((a, b) => b.views - a.views)
  } else if (sortBy.value === 'comments') {
    result.sort((a, b) => b.comments_count - a.comments_count)
  } else {
    result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  }

  return result
})

// Pagination computed properties
const totalPages = computed(() => {
  return Math.ceil(filteredPosts.value.length / itemsPerPage.value) || 1
})

const paginatedPosts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredPosts.value.slice(start, end)
})

const pageNumbers = computed(() => {
  const pages = []
  const maxVisible = 5
  let startPage = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let endPage = Math.min(totalPages.value, startPage + maxVisible - 1)

  if (endPage - startPage < maxVisible - 1) {
    startPage = Math.max(1, endPage - maxVisible + 1)
  }

  for (let i = startPage; i <= endPage; i++) {
    pages.push(i)
  }

  return pages
})

const getCategoryLabel = (category) => {
  const labels = {
    tip: t('tips.categoryTip'),
    tech: t('tips.categoryTech'),
    tutorial: t('tips.categoryTutorial'),
    qna: t('tips.categoryQna'),
    news: t('tips.categoryNews')
  }
  return labels[category] || category
}

const getCategoryStyle = (category) => {
  const styles = {
    tip: 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300',
    tech: 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300',
    tutorial: 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-300',
    qna: 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 dark:bg-yellow-900/50 text-yellow-800 dark:text-yellow-300',
    news: 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-300'
  }
  return styles[category] || styles.tip
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays < 1) {
    return t('tips.today')
  } else if (diffDays < 2) {
    return t('tips.yesterday')
  } else if (diffDays < 7) {
    return t('tips.daysAgo').replace('{n}', diffDays)
  } else {
    return date.toLocaleDateString()
  }
}

const isNew = (dateStr) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  return diffDays <= 3
}

const goToDetail = (postId) => {
  router.push(`/tips/${postId}`)
}

const goToWrite = () => {
  router.push('/tips/write')
}

// Pagination functions
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const previousPage = () => {
  if (currentPage.value > 1) {
    goToPage(currentPage.value - 1)
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    goToPage(currentPage.value + 1)
  }
}

const loadPosts = async () => {
  try {
    loading.value = true
    const response = await postsApi.getPosts({
      category: selectedCategory.value !== 'all' ? selectedCategory.value : undefined,
      search: searchQuery.value || undefined
    })
    posts.value = response.data
  } catch (error) {
    console.error('Failed to load posts:', error)
    await alert.error(t('tips.loadFailed'))
  } finally {
    loading.value = false
  }
}

const loadScraps = async () => {
  try {
    const response = await scrapsApi.getMyScraps()
    scrapedPostIds.value = new Set(response.data.map(scrap => scrap.post_id))
  } catch (error) {
    console.error('Failed to load scraps:', error)
  }
}

const isScraped = (postId) => {
  return scrapedPostIds.value.has(String(postId))
}

const toggleScrap = async (post) => {
  const postId = String(post.id)

  try {
    if (isScraped(post.id)) {
      await scrapsApi.removeScrap(postId)
      scrapedPostIds.value.delete(postId)
    } else {
      await scrapsApi.addScrap(postId, post.title)
      scrapedPostIds.value.add(postId)
    }
  } catch (error) {
    console.error('Failed to toggle scrap:', error)
    if (error.response?.status === 401) {
      await alert.warning(t('tips.loginRequired'))
    } else {
      await alert.error(t('tips.scrapFailed'))
    }
  }
}

// Reset to first page when filters change
watch([selectedCategory, searchQuery, sortBy], () => {
  currentPage.value = 1
})

onMounted(() => {
  loadPosts()
  // Only load scraps if user is authenticated
  if (authStore.isAuthenticated) {
    loadScraps()
  }
})
</script>
