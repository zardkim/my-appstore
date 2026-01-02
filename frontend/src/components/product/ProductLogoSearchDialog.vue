<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 overflow-y-auto"
    @click.self="close"
  >
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div
        class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75 dark:bg-gray-900 dark:bg-opacity-75"
        @click="close"
      ></div>

      <!-- Modal content -->
      <div class="inline-block w-full max-w-6xl my-8 overflow-hidden text-left align-middle transition-all transform bg-white dark:bg-gray-800 shadow-2xl rounded-2xl">
        <!-- Header -->
        <div class="bg-gradient-to-r from-blue-500 to-indigo-600 px-6 py-4">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-bold text-white flex items-center gap-2">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              로고 검색 - {{ product?.title || '알 수 없음' }}
            </h3>
            <button
              @click="close"
              class="text-white hover:text-gray-200 transition-colors p-2 hover:bg-white/10 rounded-lg"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Body -->
        <div class="px-6 py-6 max-h-[calc(100vh-200px)] overflow-y-auto">
          <div class="mb-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg">
            <p class="text-sm text-blue-900 dark:text-blue-300">
              <strong>검색 대상:</strong> {{ product?.title || '알 수 없음' }}
            </p>
            <p class="text-xs text-blue-700 dark:text-blue-400 mt-1">
              Google 이미지 검색으로 로고를 찾아 선택하세요.
            </p>
          </div>

          <!-- Image Manager -->
          <ImageManager
            v-if="product?.id"
            :product-id="product.id"
            :product="product"
            :initial-search-query="product.title"
            default-tab="logo"
            :visible-tabs="['logo']"
            @update:logo="handleLogoUpdate"
            @update:screenshots="handleScreenshotsUpdate"
          />
        </div>

        <!-- Footer -->
        <div class="sticky bottom-0 bg-gray-50 dark:bg-gray-700 px-6 py-4 border-t border-gray-200 dark:border-gray-600">
          <button
            @click="close"
            class="w-full px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import ImageManager from '../ImageManager.vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  product: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'saved'])

const handleLogoUpdate = (iconUrl) => {
  // 로고 저장 후 부모 컴포넌트에 전달 (부모에서 다이얼로그 닫기 처리)
  console.log('Logo updated:', iconUrl)
  emit('saved', { icon_url: iconUrl })
}

const handleScreenshotsUpdate = (screenshots) => {
  // 스크린샷은 로고 검색 다이얼로그에서 사용하지 않음
  console.log('Screenshots updated (ignored in logo dialog)')
}

const close = () => {
  emit('close')
}
</script>
