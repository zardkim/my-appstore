<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50 p-4">
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-3xl w-full max-h-[80vh] flex flex-col">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">{{ t('folderBrowser.title') }}</h2>
          <button @click="close" class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
            <svg class="w-5 h-5 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Current Path -->
        <div class="flex items-center space-x-2 text-sm">
          <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
          </svg>
          <input
            v-model="currentPath"
            type="text"
            class="flex-1 px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 text-sm font-mono"
            @keyup.enter="navigateToPath"
          />
          <button @click="navigateToPath" class="px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm">
            {{ t('folderBrowser.go') }}
          </button>
        </div>
      </div>

      <!-- Breadcrumb -->
      <div class="px-6 py-3 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600 overflow-x-auto">
        <div class="flex items-center space-x-2 text-sm">
          <button
            @click="navigateTo('/')"
            class="px-2 py-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition-colors text-gray-700 dark:text-gray-300"
          >
            /
          </button>
          <template v-for="(part, index) in pathParts" :key="index">
            <svg class="w-4 h-4 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            <button
              @click="navigateToPathPart(index)"
              class="px-2 py-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition-colors text-gray-700 dark:text-gray-300"
            >
              {{ part }}
            </button>
          </template>
        </div>
      </div>

      <!-- Folder List -->
      <div class="flex-1 overflow-y-auto p-4">
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>

        <div v-else-if="error" class="text-center py-12">
          <svg class="w-16 h-16 text-red-500 dark:text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-red-600 dark:text-red-400 font-medium">{{ error }}</p>
          <button @click="loadDirectory(currentPath)" class="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
            {{ t('folderBrowser.retry') }}
          </button>
        </div>

        <div v-else class="space-y-1">
          <!-- Parent Directory -->
          <button
            v-if="parentPath"
            @click="navigateTo(parentPath)"
            class="w-full flex items-center p-3 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors text-left group"
          >
            <svg class="w-6 h-6 text-gray-400 dark:text-gray-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            <span class="text-gray-600 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white">..</span>
          </button>

          <!-- Directories -->
          <button
            v-for="item in items"
            :key="item.path"
            @click="selectItem(item)"
            :class="[
              'w-full flex items-center justify-between p-3 rounded-lg transition-all text-left',
              selectedPath === item.path
                ? 'bg-blue-50 dark:bg-blue-900/30 border-2 border-blue-500 dark:border-blue-400'
                : 'hover:bg-gray-100 dark:hover:bg-gray-700 border-2 border-transparent'
            ]"
            :disabled="!item.is_readable"
          >
            <div class="flex items-center flex-1 min-w-0">
              <svg
                class="w-6 h-6 mr-3 flex-shrink-0"
                :class="item.is_readable ? 'text-blue-500' : 'text-gray-300'"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
              <span
                :class="[
                  'truncate',
                  item.is_readable ? 'text-gray-900 dark:text-white' : 'text-gray-400 dark:text-gray-600'
                ]"
              >
                {{ item.name }}
              </span>
            </div>
            <svg
              v-if="item.is_readable"
              class="w-5 h-5 text-gray-400 dark:text-gray-500 flex-shrink-0 ml-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>

          <!-- Empty State -->
          <div v-if="items.length === 0" class="text-center py-12 text-gray-400 dark:text-gray-500">
            <svg class="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
            <p class="text-sm">{{ t('folderBrowser.emptyFolder') }}</p>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-600 dark:text-gray-400">
            <span v-if="selectedPath" class="font-mono">{{ selectedPath }}</span>
            <span v-else class="text-gray-400 dark:text-gray-500">{{ t('folderBrowser.selectFolder') }}</span>
          </div>
          <div class="flex items-center space-x-3">
            <button @click="close" class="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors">
              {{ t('folderBrowser.cancel') }}
            </button>
            <button
              @click="confirmSelection"
              :disabled="!selectedPath"
              class="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ t('folderBrowser.select') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { filesystemApi } from '../api/filesystem'

const { t } = useI18n({ useScope: 'global' })

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  initialPath: {
    type: String,
    default: '/library'
  }
})

const emit = defineEmits(['close', 'select'])

const loading = ref(false)
const error = ref(null)
const currentPath = ref(props.initialPath)
const parentPath = ref(null)
const items = ref([])
const selectedPath = ref(null)

// Computed
const pathParts = computed(() => {
  if (!currentPath.value || currentPath.value === '/') return []
  return currentPath.value.split('/').filter(p => p)
})

// Watch
watch(() => props.show, (show) => {
  if (show) {
    currentPath.value = props.initialPath
    selectedPath.value = null
    loadDirectory(currentPath.value)
  }
})

// Methods
const loadDirectory = async (path) => {
  loading.value = true
  error.value = null

  try {
    const response = await filesystemApi.browse(path)
    currentPath.value = response.data.current_path
    parentPath.value = response.data.parent_path
    items.value = response.data.items
  } catch (err) {
    console.error('Failed to browse directory:', err)
    error.value = err.response?.data?.detail || t('folderBrowser.loadFailed')
  } finally {
    loading.value = false
  }
}

const navigateTo = (path) => {
  selectedPath.value = null
  loadDirectory(path)
}

const navigateToPath = () => {
  if (currentPath.value) {
    loadDirectory(currentPath.value)
  }
}

const navigateToPathPart = (index) => {
  const parts = pathParts.value.slice(0, index + 1)
  const path = '/' + parts.join('/')
  navigateTo(path)
}

const selectItem = (item) => {
  if (!item.is_readable) return

  if (item.is_dir) {
    // 디렉토리를 더블클릭하면 이동, 싱글클릭하면 선택
    if (selectedPath.value === item.path) {
      // 더블클릭 효과
      navigateTo(item.path)
    } else {
      selectedPath.value = item.path
    }
  }
}

const confirmSelection = () => {
  if (selectedPath.value) {
    emit('select', selectedPath.value)
    close()
  }
}

const close = () => {
  emit('close')
}
</script>
