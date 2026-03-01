<template>
  <div>
    <!-- 섹션 헤더 -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4 sm:mb-6">
      <h3 class="text-base sm:text-lg lg:text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
        <span class="text-lg sm:text-xl">🎬</span>
        {{ t('product.installation.videoGuide.title') }}
        <span v-if="videos.length > 0" class="text-sm font-normal text-gray-500 dark:text-gray-400">
          ({{ videos.length }})
        </span>
      </h3>

      <!-- 관리자: 업로드 버튼 -->
      <div v-if="isAdmin" class="w-full sm:w-auto">
        <label
          class="flex items-center justify-center gap-2 px-3 sm:px-4 py-2 sm:py-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg sm:rounded-xl hover:from-indigo-600 hover:to-purple-700 transition-all shadow-md hover:shadow-lg cursor-pointer text-sm font-medium"
        >
          <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          {{ t('product.installation.videoGuide.upload') }}
          <input
            type="file"
            accept=".mp4,.webm,.ogg,.mov,.avi,.mkv,video/*"
            class="hidden"
            @change="handleFileSelect"
          />
        </label>
      </div>
    </div>

    <!-- 업로드 진행바 -->
    <div v-if="uploading" class="mb-4 sm:mb-6">
      <div class="flex items-center justify-between mb-1">
        <span class="text-sm text-gray-600 dark:text-gray-400">
          {{ t('product.installation.videoGuide.uploading') }}
        </span>
        <span class="text-sm font-medium text-indigo-600 dark:text-indigo-400">{{ uploadProgress }}%</span>
      </div>
      <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
        <div
          class="bg-gradient-to-r from-indigo-500 to-purple-600 h-2 rounded-full transition-all duration-300"
          :style="{ width: uploadProgress + '%' }"
        ></div>
      </div>
    </div>

    <!-- 관리자: 드래그 앤 드롭 영역 -->
    <div
      v-if="isAdmin && !uploading"
      class="mb-4 sm:mb-6 border-2 border-dashed rounded-xl p-4 sm:p-6 text-center transition-all cursor-pointer"
      :class="isDragging
        ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
        : 'border-gray-300 dark:border-gray-600 hover:border-indigo-400 dark:hover:border-indigo-500 hover:bg-gray-50 dark:hover:bg-gray-700/30'"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
    >
      <div class="flex sm:flex-col items-center gap-3 sm:gap-2">
        <svg class="w-8 h-8 sm:w-10 sm:h-10 text-gray-400 dark:text-gray-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.069A1 1 0 0121 8.82V15.18a1 1 0 01-1.447.89L15 14M3 8a2 2 0 012-2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" />
        </svg>
        <div class="text-left sm:text-center">
          <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('product.installation.videoGuide.dropzone') }}</p>
          <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{{ t('product.installation.videoGuide.formats') }}</p>
        </div>
      </div>
      <input
        ref="dropzoneInput"
        type="file"
        accept=".mp4,.webm,.ogg,.mov,.avi,.mkv,video/*"
        class="hidden"
        @change="handleFileSelect"
      />
    </div>

    <!-- 영상 목록 -->
    <div v-if="videos.length > 0" class="space-y-4 sm:space-y-6">
      <VideoPlayer
        v-for="video in videos"
        :key="video.id"
        :video="video"
        :is-admin="isAdmin"
        @deleted="loadVideos"
        @updated="loadVideos"
      />
    </div>

    <!-- 빈 상태 -->
    <div v-else-if="!loading" class="text-center py-8 sm:py-10">
      <div class="w-14 h-14 sm:w-16 sm:h-16 mx-auto mb-3 sm:mb-4 bg-gradient-to-br from-gray-100 to-gray-50 dark:from-gray-700 dark:to-gray-800 rounded-2xl flex items-center justify-center">
        <svg class="w-7 h-7 sm:w-8 sm:h-8 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.069A1 1 0 0121 8.82V15.18a1 1 0 01-1.447.89L15 14M3 8a2 2 0 012-2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" />
        </svg>
      </div>
      <p class="text-sm sm:text-base text-gray-500 dark:text-gray-400 font-medium mb-1">
        {{ t('product.installation.videoGuide.noVideos') }}
      </p>
      <p v-if="isAdmin" class="text-xs sm:text-sm text-gray-400 dark:text-gray-500">
        {{ t('product.installation.videoGuide.noVideosAdmin') }}
      </p>
    </div>

    <!-- 로딩 -->
    <div v-if="loading" class="flex justify-center py-8">
      <svg class="animate-spin w-6 h-6 text-indigo-500" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { productVideosApi } from '../../api/productVideos'
import { useDialog } from '../../composables/useDialog'
import VideoPlayer from './VideoPlayer.vue'

const { t } = useI18n({ useScope: 'global' })
const { alert } = useDialog()

const props = defineProps({
  productId: { type: Number, required: true },
  isAdmin: { type: Boolean, default: false },
})

const videos = ref([])
const loading = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const isDragging = ref(false)
const dropzoneInput = ref(null)

const loadVideos = async () => {
  loading.value = true
  try {
    const res = await productVideosApi.getVideos(props.productId)
    videos.value = res.data
  } catch {
    videos.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadVideos)

const triggerFileInput = () => dropzoneInput.value?.click()

const handleDrop = (e) => {
  isDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) uploadFile(file)
}

const handleFileSelect = (e) => {
  const file = e.target?.files?.[0]
  if (file) uploadFile(file)
  e.target.value = ''
}

const uploadFile = async (file) => {
  const allowedExts = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv']
  const ext = '.' + file.name.split('.').pop().toLowerCase()
  if (!allowedExts.includes(ext)) {
    await alert.error(t('product.installation.videoGuide.invalidFormat'))
    return
  }
  if (file.size > 500 * 1024 * 1024) {
    await alert.error(t('product.installation.videoGuide.fileTooLarge'))
    return
  }

  uploading.value = true
  uploadProgress.value = 0

  const formData = new FormData()
  formData.append('file', file)
  formData.append('title', file.name.replace(/\.[^.]+$/, ''))

  try {
    await productVideosApi.upload(props.productId, formData, (pct) => {
      uploadProgress.value = pct
    })
    await loadVideos()
  } catch (e) {
    const msg = e.response?.data?.detail || t('product.installation.videoGuide.uploadFailed')
    await alert.error(msg)
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}
</script>
