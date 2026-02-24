<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 sm:px-6 py-3 sm:py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
          <h1 class="text-lg font-semibold text-gray-900 dark:text-white">{{ t('share.myLinks') }}</h1>
        </div>
        <span class="text-sm text-gray-500 dark:text-gray-400">{{ t('share.totalLinks', { n: total }) }}</span>
      </div>

      <!-- 필터 탭 -->
      <div class="flex gap-1 mt-3">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          @click="activeFilter = tab.value; loadLinks()"
          :class="[
            'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
            activeFilter === tab.value
              ? 'bg-blue-600 text-white'
              : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
          ]"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- 로딩 -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
    </div>

    <!-- 빈 상태 -->
    <div v-else-if="links.length === 0" class="flex-1 flex items-center justify-center p-8">
      <div class="text-center">
        <div class="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
        </div>
        <p class="text-gray-500 dark:text-gray-400 text-sm">{{ t('share.noLinks') }}</p>
        <p class="text-gray-400 dark:text-gray-500 text-xs mt-1">{{ t('share.noLinksDesc') }}</p>
      </div>
    </div>

    <!-- 링크 목록 -->
    <div v-else class="flex-1 overflow-y-auto">
      <div class="p-4 space-y-3 max-w-2xl mx-auto">
        <div
          v-for="link in links"
          :key="link.id"
          class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4"
        >
          <div class="flex items-start gap-3">
            <!-- 제품 아이콘 -->
            <img
              v-if="link.product_icon"
              :src="link.product_icon"
              class="w-12 h-12 rounded-lg object-cover flex-shrink-0"
              @error="e => e.target.style.display='none'"
            />
            <div v-else class="w-12 h-12 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>

            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-2">
                <div>
                  <p class="font-medium text-gray-900 dark:text-white text-sm">{{ link.product_title }}</p>
                  <p v-if="link.note" class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{{ link.note }}</p>
                </div>
                <!-- 상태 배지 -->
                <span :class="[
                  'flex-shrink-0 text-xs px-2 py-0.5 rounded-full font-medium',
                  link.is_used
                    ? 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
                    : link.is_expired
                      ? 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400'
                      : 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                ]">
                  {{ link.is_used ? t('share.status.used') : link.is_expired ? t('share.status.expired') : t('share.status.active') }}
                </span>
              </div>

              <!-- 만료 시간 -->
              <p class="text-xs text-gray-400 dark:text-gray-500 mt-1.5">
                {{ t('share.expiresAt') }}: {{ formatDate(link.expires_at) }}
              </p>
              <p class="text-xs text-gray-300 dark:text-gray-600">
                {{ t('share.createdAt') }}: {{ formatDate(link.created_at) }}
              </p>
            </div>
          </div>

          <!-- 버튼 행 -->
          <div class="flex gap-2 mt-3">
            <button
              v-if="link.is_active"
              @click="copyShareUrl(link.token)"
              class="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-medium transition-colors"
            >
              <svg v-if="copiedToken === link.token" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              {{ copiedToken === link.token ? t('share.copied') : t('share.copyLink') }}
            </button>

            <router-link
              :to="`/product/${link.product_id}`"
              class="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg text-xs font-medium transition-colors"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              {{ t('share.viewProduct') }}
            </router-link>

            <button
              @click="deleteLink(link.id)"
              :disabled="deleting === link.id"
              class="ml-auto flex items-center gap-1.5 px-3 py-1.5 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg text-xs font-medium transition-colors"
            >
              <svg v-if="deleting === link.id" class="animate-spin w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              {{ t('common.delete') }}
            </button>
          </div>
        </div>
      </div>

      <!-- 더 보기 -->
      <div v-if="hasMore" class="flex justify-center py-4">
        <button
          @click="loadMore"
          :disabled="loadingMore"
          class="px-6 py-2 text-sm text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
        >
          {{ loadingMore ? t('common.loading') : t('share.loadMore') }}
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { shareApi } from '../api/share'

const { t } = useI18n({ useScope: 'global' })

const loading = ref(true)
const loadingMore = ref(false)
const links = ref([])
const total = ref(0)
const page = ref(1)
const LIMIT = 20
const activeFilter = ref(null)
const deleting = ref(null)
const copiedToken = ref(null)

const tabs = computed(() => [
  { value: null, label: t('share.filterAll') },
  { value: 'active', label: t('share.status.active') },
  { value: 'expired', label: t('share.status.expired') },
  { value: 'used', label: t('share.status.used') },
])

const hasMore = computed(() => links.value.length < total.value)

const loadLinks = async () => {
  loading.value = true
  page.value = 1
  try {
    const res = await shareApi.getMyLinks(1, LIMIT, activeFilter.value)
    links.value = res.data.links
    total.value = res.data.total
  } catch {
    // 오류 무시
  } finally {
    loading.value = false
  }
}

const loadMore = async () => {
  if (loadingMore.value) return
  loadingMore.value = true
  page.value++
  try {
    const res = await shareApi.getMyLinks(page.value, LIMIT, activeFilter.value)
    links.value.push(...res.data.links)
  } finally {
    loadingMore.value = false
  }
}

const deleteLink = async (id) => {
  if (deleting.value) return
  deleting.value = id
  try {
    await shareApi.deleteLink(id)
    links.value = links.value.filter(l => l.id !== id)
    total.value = Math.max(0, total.value - 1)
  } catch {
    // 오류 무시
  } finally {
    deleting.value = null
  }
}

const copyShareUrl = async (token) => {
  const url = `${window.location.origin}/share/${token}`
  try {
    await navigator.clipboard.writeText(url)
    copiedToken.value = token
    setTimeout(() => { copiedToken.value = null }, 2000)
  } catch {
    const el = document.createElement('textarea')
    el.value = url
    document.body.appendChild(el)
    el.select()
    document.execCommand('copy')
    document.body.removeChild(el)
  }
}

const formatDate = (isoString) => {
  if (!isoString) return ''
  const d = new Date(isoString)
  return d.toLocaleDateString('ko-KR', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => loadLinks())
</script>
