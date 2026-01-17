<template>
  <div class="relative">
    <router-link
      :to="`/product/${product.id}`"
      class="group bg-white dark:bg-gray-800 rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100 dark:border-gray-700 hover:border-blue-200 dark:hover:border-blue-500 block transform hover:-translate-y-1"
    >
      <!-- Icon -->
      <div class="aspect-square bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-700 dark:via-gray-800 dark:to-gray-700 flex items-center justify-center overflow-hidden p-4 sm:p-6 lg:p-8 relative">
        <!-- Background Pattern -->
        <div class="absolute inset-0 opacity-5 dark:opacity-10">
          <div class="absolute inset-0" style="background-image: radial-gradient(circle, #000 1px, transparent 1px); background-size: 20px 20px;"></div>
        </div>

        <img
          v-if="product.icon_url && !imageError"
          :src="iconUrl"
          :alt="product.title"
          class="w-full h-full object-contain group-hover:scale-110 transition-transform duration-300 relative z-10"
          @error="handleImageError"
        />
        <div v-else class="w-12 h-12 sm:w-14 sm:h-14 lg:w-16 lg:h-16 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900 dark:to-purple-900 rounded-xl sm:rounded-2xl flex items-center justify-center relative z-10">
          <svg
            class="w-6 h-6 sm:w-7 sm:h-7 lg:w-8 lg:h-8 text-blue-500 dark:text-blue-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
            />
          </svg>
        </div>
      </div>

    <!-- Info -->
    <div class="p-2.5 sm:p-3 lg:p-4">
      <h3 class="text-sm sm:text-base font-semibold text-gray-900 dark:text-white truncate mb-0.5 sm:mb-1 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
        {{ product.title }}
      </h3>
      <p class="text-[10px] sm:text-xs text-gray-500 dark:text-gray-400 truncate mb-2 sm:mb-3">
        {{ product.vendor || 'Unknown Vendor' }}
      </p>

      <div class="flex items-center justify-between gap-1 sm:gap-2">
        <div class="flex items-center gap-1 sm:gap-1.5 flex-wrap">
          <span
            v-if="product.category"
            class="inline-flex items-center gap-0.5 sm:gap-1 px-1.5 sm:px-2 lg:px-2.5 py-0.5 sm:py-1 rounded-md sm:rounded-lg text-[10px] sm:text-xs font-medium bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900 dark:to-purple-900 text-blue-700 dark:text-blue-300 border border-blue-100 dark:border-blue-700"
          >
            <span class="text-xs sm:text-sm">{{ getCategoryIcon(product.category) }}</span>
            <span class="hidden sm:inline">{{ product.category }}</span>
          </span>
          <span
            v-if="product.is_portable"
            class="inline-flex items-center gap-0.5 sm:gap-1 px-1.5 sm:px-2 lg:px-2.5 py-0.5 sm:py-1 rounded-md sm:rounded-lg text-[10px] sm:text-xs font-medium bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900 dark:to-emerald-900 text-green-700 dark:text-green-300 border border-green-100 dark:border-green-700"
          >
            <span class="text-xs sm:text-sm">🎒</span>
            <span class="hidden sm:inline">Portable</span>
          </span>
        </div>
        <div v-if="versionCount" class="flex items-center text-[10px] sm:text-xs text-gray-400 dark:text-gray-500 flex-shrink-0">
          <svg class="w-3 h-3 sm:w-3.5 sm:h-3.5 mr-0.5 sm:mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          {{ versionCount }}
        </div>
      </div>
    </div>
    </router-link>

    <!-- Favorite Button - 우측 상단 -->
    <button
      @click.prevent="toggleFavorite"
      class="absolute top-2 sm:top-3 right-2 sm:right-3 z-20 p-1.5 sm:p-2 rounded-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl transition-all hover:scale-110 border border-gray-200 dark:border-gray-700"
      :class="isFavorite ? 'text-pink-500' : 'text-gray-400 dark:text-gray-500'"
    >
      <svg class="w-4 h-4 sm:w-5 sm:h-5" :fill="isFavorite ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
      </svg>
    </button>

    <!-- More Menu Button - 우측 하단 -->
    <div class="absolute bottom-2 sm:bottom-3 right-2 sm:right-3 z-20">
      <div class="relative">
        <button
          @click.prevent="toggleMenu"
          class="p-1.5 sm:p-2 rounded-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl transition-all hover:scale-110 border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
        >
          <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
          </svg>
        </button>

        <!-- Dropdown Menu -->
        <div
          v-if="showMenu"
          class="absolute right-0 bottom-full mb-2 w-48 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 py-2 z-30"
          @click.stop
        >
          <button
            @click="handleAISearch"
            class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            {{ t('productCard.aiMatching') }}
          </button>
          <button
            @click="handleManualEdit"
            class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            {{ t('productCard.manualEdit') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { favoritesApi } from '../../api/favorites'
import { getIconUrl } from '../../utils/env'
import { useDialog } from '../../composables/useDialog'

const { t } = useI18n({ useScope: 'global' })
const { alert } = useDialog()

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['ai-search', 'manual-edit'])

const imageError = ref(false)
const isFavorite = ref(false)
const showMenu = ref(false)

const iconUrl = computed(() => {
  if (imageError.value) return ''
  return getIconUrl(props.product.icon_url)
})

const versionCount = computed(() => {
  const count = props.product.versions?.length || 0
  return count > 0 ? `${count}` : ''
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

const handleImageError = () => {
  imageError.value = true
}

const checkFavorite = async () => {
  try {
    const response = await favoritesApi.checkFavorite(props.product.id)
    isFavorite.value = response.data.is_favorite
  } catch (error) {
    console.error('Failed to check favorite:', error)
  }
}

const toggleFavorite = async () => {
  try {
    if (isFavorite.value) {
      await favoritesApi.removeFavorite(props.product.id)
      isFavorite.value = false
    } else {
      await favoritesApi.addFavorite(props.product.id)
      isFavorite.value = true
    }
  } catch (error) {
    console.error('Failed to toggle favorite:', error)
    if (error.response?.status === 401) {
      await alert.warning(t('productCard.loginRequired'))
    } else if (error.response?.status === 400) {
      // 이미 즐겨찾기에 있는 경우 등
      await checkFavorite()
    } else {
      await alert.error(t('productCard.favoriteFailed'))
    }
  }
}

const toggleMenu = () => {
  showMenu.value = !showMenu.value
}

const handleAISearch = () => {
  showMenu.value = false
  emit('ai-search', props.product)
}

const handleManualEdit = () => {
  showMenu.value = false
  emit('manual-edit', props.product)
}

// Close menu when clicking outside
onMounted(() => {
  checkFavorite()

  const handleClickOutside = (event) => {
    if (showMenu.value && !event.target.closest('.relative')) {
      showMenu.value = false
    }
  }

  document.addEventListener('click', handleClickOutside)

  return () => {
    document.removeEventListener('click', handleClickOutside)
  }
})
</script>
