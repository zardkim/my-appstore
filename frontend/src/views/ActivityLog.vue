<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="bg-gradient-to-r from-gray-700 to-gray-900 dark:from-gray-800 dark:to-gray-950 px-4 sm:px-6 lg:px-8 py-4 sm:py-6 text-white">
      <h1 class="text-xl sm:text-2xl font-bold mb-1">🗒️ {{ t('activityLog.title') }}</h1>
      <p class="text-sm text-gray-300">{{ t('activityLog.description') }}</p>
    </div>

    <!-- Filter Bar -->
    <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 sm:px-6 lg:px-8 py-3">
      <div class="flex flex-wrap gap-2 items-center">
        <select v-model="filterAction" @change="resetAndLoad" class="px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
          <option value="">{{ t('activityLog.allActions') }}</option>
          <option v-for="(label, key) in actionLabels" :key="key" :value="key">{{ label }}</option>
        </select>
        <input
          v-model="filterUsername"
          @input="handleFilterInput"
          type="text"
          :placeholder="t('activityLog.filterByUser')"
          class="px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white w-40"
        />
        <input v-model="filterDateFrom" @change="resetAndLoad" type="date" class="px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        <span class="text-gray-400 text-sm">~</span>
        <input v-model="filterDateTo" @change="resetAndLoad" type="date" class="px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        <button @click="resetFilters" class="px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-gray-700 dark:text-gray-300 transition-colors">
          {{ t('activityLog.reset') }}
        </button>
        <div class="ml-auto flex items-center gap-2">
          <span class="text-sm text-gray-500 dark:text-gray-400">{{ t('activityLog.total', { n: total }) }}</span>
          <button @click="showClearDialog = true" class="px-3 py-1.5 text-sm bg-red-100 dark:bg-red-900/30 hover:bg-red-200 dark:hover:bg-red-900/50 text-red-700 dark:text-red-400 rounded-lg transition-colors">
            {{ t('activityLog.clearOld') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Log Table -->
    <div class="flex-1 overflow-y-auto px-4 sm:px-6 lg:px-8 py-4 pb-20 lg:pb-6">
      <div v-if="loading" class="flex justify-center py-20">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
      </div>

      <div v-else-if="logs.length === 0" class="text-center py-20 text-gray-400 dark:text-gray-500">
        <p class="text-lg font-medium">{{ t('activityLog.noLogs') }}</p>
      </div>

      <div v-else>
        <!-- Desktop Table -->
        <div class="hidden md:block bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase w-40">{{ t('activityLog.time') }}</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase w-32">{{ t('activityLog.user') }}</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase w-36">{{ t('activityLog.action') }}</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">{{ t('activityLog.resource') }}</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase w-32">{{ t('activityLog.ip') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
              <tr v-for="log in logs" :key="log.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                <td class="px-4 py-3 text-gray-500 dark:text-gray-400 text-xs">{{ formatDate(log.created_at) }}</td>
                <td class="px-4 py-3 font-medium text-gray-900 dark:text-white">{{ log.username }}</td>
                <td class="px-4 py-3">
                  <span :class="getActionClass(log.action)" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium">
                    {{ log.action_label }}
                  </span>
                </td>
                <td class="px-4 py-3 text-gray-700 dark:text-gray-300">
                  <span v-if="log.resource_name" class="truncate max-w-xs block">{{ log.resource_name }}</span>
                  <span v-else class="text-gray-400 dark:text-gray-500">-</span>
                </td>
                <td class="px-4 py-3 text-gray-500 dark:text-gray-400 text-xs font-mono">{{ log.ip_address || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Cards -->
        <div class="md:hidden space-y-2">
          <div v-for="log in logs" :key="log.id" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4">
            <div class="flex items-start justify-between gap-2 mb-2">
              <span :class="getActionClass(log.action)" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium">
                {{ log.action_label }}
              </span>
              <span class="text-xs text-gray-400 dark:text-gray-500">{{ formatDate(log.created_at) }}</span>
            </div>
            <p class="text-sm font-medium text-gray-900 dark:text-white mb-1">{{ log.username }}</p>
            <p v-if="log.resource_name" class="text-sm text-gray-600 dark:text-gray-400 truncate">{{ log.resource_name }}</p>
          </div>
        </div>

        <!-- Load More -->
        <div v-if="hasMore" class="flex justify-center mt-4">
          <button @click="loadMore" :disabled="loadingMore" class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm transition-colors disabled:opacity-50">
            {{ loadingMore ? t('common.loading') : t('activityLog.loadMore') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Clear Dialog -->
    <div v-if="showClearDialog" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-sm w-full">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">{{ t('activityLog.clearOldTitle') }}</h3>
        <div class="mb-4">
          <label class="block text-sm text-gray-600 dark:text-gray-400 mb-2">{{ t('activityLog.clearDays') }}</label>
          <select v-model="clearDays" class="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
            <option :value="7">7일</option>
            <option :value="30">30일</option>
            <option :value="90">90일</option>
            <option :value="180">180일</option>
          </select>
        </div>
        <div class="flex gap-2">
          <button @click="clearOldLogs" class="flex-1 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm font-medium transition-colors">
            {{ t('activityLog.delete') }}
          </button>
          <button @click="showClearDialog = false" class="flex-1 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
            {{ t('common.cancel') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { activityLogApi } from '../api/activityLog'
import { useDialog } from '../composables/useDialog'

const { t } = useI18n({ useScope: 'global' })
const { alert } = useDialog()

const logs = ref([])
const total = ref(0)
const loading = ref(false)
const loadingMore = ref(false)
const skip = ref(0)
const limit = 50

const filterAction = ref('')
const filterUsername = ref('')
const filterDateFrom = ref('')
const filterDateTo = ref('')
const actionLabels = ref({})
const showClearDialog = ref(false)
const clearDays = ref(30)

let filterTimer = null

const hasMore = computed(() => logs.value.length < total.value)

const ACTION_COLORS = {
  download: 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300',
  scan: 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300',
  ai_search: 'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300',
  post_create: 'bg-teal-100 dark:bg-teal-900/40 text-teal-700 dark:text-teal-300',
  post_update: 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-300',
  post_delete: 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300',
  product_create: 'bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300',
  product_update: 'bg-orange-100 dark:bg-orange-900/40 text-orange-700 dark:text-orange-300',
  product_delete: 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300',
  user_login: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
}

const getActionClass = (action) => ACTION_COLORS[action] || 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('ko-KR', { year: '2-digit', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const buildParams = () => {
  const params = { skip: skip.value, limit }
  if (filterAction.value) params.action = filterAction.value
  if (filterUsername.value) params.username = filterUsername.value
  if (filterDateFrom.value) params.date_from = filterDateFrom.value
  if (filterDateTo.value) params.date_to = filterDateTo.value + 'T23:59:59'
  return params
}

const loadLogs = async (append = false) => {
  if (append) loadingMore.value = true
  else loading.value = true
  try {
    const res = await activityLogApi.getLogs(buildParams())
    if (append) {
      logs.value = [...logs.value, ...res.data.logs]
    } else {
      logs.value = res.data.logs
      actionLabels.value = res.data.action_labels || {}
    }
    total.value = res.data.total
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const resetAndLoad = () => {
  skip.value = 0
  logs.value = []
  loadLogs()
}

const loadMore = () => {
  skip.value += limit
  loadLogs(true)
}

const handleFilterInput = () => {
  clearTimeout(filterTimer)
  filterTimer = setTimeout(() => resetAndLoad(), 500)
}

const resetFilters = () => {
  filterAction.value = ''
  filterUsername.value = ''
  filterDateFrom.value = ''
  filterDateTo.value = ''
  resetAndLoad()
}

const clearOldLogs = async () => {
  try {
    const res = await activityLogApi.clearOldLogs(clearDays.value)
    await alert.success(res.data.message)
    showClearDialog.value = false
    resetAndLoad()
  } catch (e) {
    await alert.error('삭제 중 오류가 발생했습니다.')
  }
}

onMounted(() => loadLogs())
</script>
