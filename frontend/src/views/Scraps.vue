<template>
  <div class="h-full overflow-y-auto lg:overflow-hidden lg:flex lg:flex-col">
    <!-- Header -->
    <div class="bg-gradient-to-r from-amber-500 to-orange-600 dark:from-amber-700 dark:to-orange-800 px-4 sm:px-6 lg:px-8 py-3 sm:py-4 lg:py-8 text-white">
      <div class="max-w-7xl">
        <h1 class="text-xl sm:text-2xl lg:text-4xl font-bold mb-0.5 sm:mb-1 lg:mb-2">📌 {{ t('scraps.title') }}</h1>
        <p class="text-amber-100 dark:text-amber-200 text-xs sm:text-sm lg:text-base">{{ t('scraps.description') }}</p>
      </div>
    </div>

    <!-- Content -->
    <div class="lg:flex-1 lg:overflow-y-auto px-4 sm:px-6 lg:px-8 pt-4 sm:pt-6 lg:pt-8 pb-20 lg:pb-8">
      <div class="max-w-7xl mx-auto">
        <!-- Loading -->
        <div v-if="loading" class="flex items-center justify-center py-20">
          <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-amber-600 dark:border-amber-400"></div>
        </div>

        <!-- Empty State -->
        <div v-else-if="scraps.length === 0" class="text-center py-20">
          <div class="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-gray-100 to-gray-50 dark:from-gray-700 dark:to-gray-800 rounded-full flex items-center justify-center">
            <svg class="w-12 h-12 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">{{ t('scraps.emptyTitle') }}</h3>
          <p class="text-gray-500 dark:text-gray-400 mb-6">{{ t('scraps.emptyDescription') }}</p>
          <button @click="$router.push('/tips')" class="px-6 py-3 bg-gradient-to-r from-amber-500 to-orange-600 text-white rounded-xl hover:from-amber-600 hover:to-orange-700 shadow-md font-medium">
            {{ t('scraps.goToTips') }}
          </button>
        </div>

        <!-- Scraps List -->
        <div v-else>
          <!-- Mobile Card View -->
          <div class="md:hidden space-y-2">
            <router-link
              v-for="scrap in scraps"
              :key="scrap.id"
              :to="'/tips/' + scrap.post_id"
              class="flex items-center justify-between bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 px-4 py-3 active:scale-[0.98] transition-all"
            >
              <div class="flex items-center gap-2 flex-1 min-w-0">
                <svg class="w-4 h-4 text-amber-500 dark:text-amber-400 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                </svg>
                <div class="min-w-0">
                  <p class="text-sm font-medium text-gray-900 dark:text-white line-clamp-1">
                    {{ scrap.post_title || `${t('scraps.postFallback')}${scrap.post_id}` }}
                  </p>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{{ formatDate(scrap.created_at) }}</p>
                </div>
              </div>
              <button
                @click.prevent.stop="removeScrap(scrap.post_id)"
                class="ml-2 px-2 py-1 text-xs border border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 hover:border-red-300 dark:hover:border-red-700 hover:text-red-600 dark:hover:text-red-400 transition-all flex-shrink-0"
              >
                {{ t('scraps.deleteButton') }}
              </button>
            </router-link>
          </div>

          <!-- Desktop Table View -->
          <div class="hidden md:block bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
            <table class="w-full">
              <thead class="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
                <tr>
                  <th class="text-left py-2.5 px-4 text-xs font-semibold text-gray-700 dark:text-gray-300">{{ t('scraps.titleColumn') }}</th>
                  <th class="text-left py-2.5 px-4 text-xs font-semibold text-gray-700 dark:text-gray-300 w-32">{{ t('scraps.scrapDateColumn') }}</th>
                  <th class="text-center py-2.5 px-4 text-xs font-semibold text-gray-700 dark:text-gray-300 w-20">{{ t('scraps.actionsColumn') }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                <tr
                  v-for="scrap in scraps"
                  :key="scrap.id"
                  class="hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                  @click="goToPost(scrap.post_id)"
                >
                  <td class="py-2 px-4">
                    <div class="flex items-center">
                      <svg class="w-4 h-4 text-amber-500 dark:text-amber-400 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                      </svg>
                      <p class="text-sm text-gray-900 dark:text-white font-medium line-clamp-1">
                        {{ scrap.post_title || `${t('scraps.postFallback')}${scrap.post_id}` }}
                      </p>
                    </div>
                  </td>
                  <td class="py-2 px-4 text-xs text-gray-500 dark:text-gray-400">
                    {{ formatDate(scrap.created_at) }}
                  </td>
                  <td class="py-2 px-4 text-center">
                    <button
                      @click.stop="removeScrap(scrap.post_id)"
                      class="px-2.5 py-1 text-xs border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 hover:border-red-300 dark:hover:border-red-700 hover:text-red-600 dark:hover:text-red-400 transition-all font-medium"
                    >
                      {{ t('scraps.deleteButton') }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { scrapsApi } from '../api/scraps'
import { useDialog } from '../composables/useDialog'

const router = useRouter()
const { t } = useI18n({ useScope: 'global' })
const { alert, confirm } = useDialog()

const scraps = ref([])
const loading = ref(true)

onMounted(async () => {
  await loadScraps()
})

const loadScraps = async () => {
  loading.value = true
  try {
    const response = await scrapsApi.getMyScraps()
    scraps.value = response.data
  } catch (error) {
    console.error('Failed to load scraps:', error)
  } finally {
    loading.value = false
  }
}

const goToPost = (postId) => {
  router.push(`/tips/${postId}`)
}

const removeScrap = async (postId) => {
  const shouldRemove = await confirm.warning(t('scraps.deleteConfirm'))
  if (!shouldRemove) return

  try {
    await scrapsApi.removeScrap(postId)
    await loadScraps()
  } catch (error) {
    console.error('Failed to remove scrap:', error)
    await alert.error(t('scraps.deleteFailed'))
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return t('scraps.notAvailable')
  try {
    const date = new Date(dateStr)
    // 현재 언어 설정에 따라 로케일 결정
    const locale = localStorage.getItem('app-language') || navigator.language || 'ko-KR'
    return date.toLocaleDateString(locale, { year: 'numeric', month: 'long', day: 'numeric' })
  } catch {
    return dateStr
  }
}
</script>
