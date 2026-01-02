<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="bg-gradient-to-r from-pink-500 to-rose-600 dark:from-pink-700 dark:to-rose-800 px-8 py-12 text-white">
      <div class="max-w-7xl">
        <h1 class="text-4xl font-bold mb-2">❤️ 즐겨찾기</h1>
        <p class="text-pink-100 dark:text-pink-200">내가 즐겨찾기한 프로그램 목록입니다</p>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto px-8 py-8">
      <div class="max-w-7xl mx-auto">
        <!-- Loading -->
        <div v-if="loading" class="flex items-center justify-center py-20">
          <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-pink-600 dark:border-pink-400"></div>
        </div>

        <!-- Empty State -->
        <div v-else-if="favorites.length === 0" class="text-center py-20">
          <div class="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-gray-100 to-gray-50 dark:from-gray-700 dark:to-gray-800 rounded-full flex items-center justify-center">
            <svg class="w-12 h-12 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">즐겨찾기가 비어있습니다</h3>
          <p class="text-gray-500 dark:text-gray-400 mb-6">스토어에서 마음에 드는 프로그램을 즐겨찾기에 추가해보세요</p>
          <button @click="$router.push('/discover')" class="px-6 py-3 bg-gradient-to-r from-pink-500 to-rose-600 text-white rounded-xl hover:from-pink-600 hover:to-rose-700 shadow-md font-medium">
            스토어로 이동
          </button>
        </div>

        <!-- Favorites Grid -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <div
            v-for="favorite in favorites"
            :key="favorite.id"
            class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-all group cursor-pointer"
            @click="goToProduct(favorite.product_id)"
          >
            <div class="p-6">
              <!-- Icon -->
              <div class="w-20 h-20 bg-gradient-to-br from-gray-50 to-white dark:from-gray-700 dark:to-gray-800 rounded-2xl flex items-center justify-center mb-4 mx-auto">
                <img
                  v-if="favorite.product?.icon_url"
                  :src="favorite.product.icon_url"
                  :alt="favorite.product?.title"
                  class="w-full h-full object-contain p-3"
                />
                <svg
                  v-else
                  class="w-10 h-10 text-blue-500 dark:text-blue-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>

              <!-- Title -->
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white text-center mb-2 line-clamp-2 group-hover:text-pink-600 dark:group-hover:text-pink-400 transition-colors">
                {{ favorite.product?.title || 'Unknown' }}
              </h3>

              <!-- Vendor -->
              <p class="text-sm text-gray-500 dark:text-gray-400 text-center mb-3">
                {{ favorite.product?.vendor || 'Unknown Vendor' }}
              </p>

              <!-- Category -->
              <div class="flex items-center justify-center mb-4">
                <span class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-medium bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-700">
                  {{ favorite.product?.category || 'Uncategorized' }}
                </span>
              </div>

              <!-- Remove Button -->
              <button
                @click.stop="removeFavorite(favorite.product_id)"
                class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-red-50 dark:hover:bg-red-900/20 hover:border-red-300 dark:hover:border-red-700 hover:text-red-600 dark:hover:text-red-400 transition-all text-sm font-medium"
              >
                즐겨찾기 해제
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { favoritesApi } from '../api/favorites'
import { useDialog } from '../composables/useDialog'

const router = useRouter()
const { alert, confirm } = useDialog()

const favorites = ref([])
const loading = ref(true)

onMounted(async () => {
  await loadFavorites()
})

const loadFavorites = async () => {
  loading.value = true
  try {
    const response = await favoritesApi.getMyFavorites()
    favorites.value = response.data
  } catch (error) {
    console.error('Failed to load favorites:', error)
  } finally {
    loading.value = false
  }
}

const goToProduct = (productId) => {
  router.push(`/product/${productId}`)
}

const removeFavorite = async (productId) => {
  const shouldRemove = await confirm.warning('즐겨찾기에서 제거하시겠습니까?')
  if (!shouldRemove) return

  try {
    await favoritesApi.removeFavorite(productId)
    await loadFavorites()
  } catch (error) {
    console.error('Failed to remove favorite:', error)
    await alert.error('즐겨찾기 제거에 실패했습니다.')
  }
}
</script>
