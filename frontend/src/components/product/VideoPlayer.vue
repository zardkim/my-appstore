<template>
  <div class="lg:max-w-[50%] bg-gray-900 dark:bg-black rounded-xl overflow-hidden shadow-lg">
    <!-- Video.js 플레이어 -->
    <div class="relative">
      <video
        :id="`vjs-player-${video.id}`"
        class="video-js vjs-big-play-centered w-full"
        controls
        preload="metadata"
        playsinline
        webkit-playsinline
        x5-playsinline
      >
        <source :src="videoUrl" :type="video.mime_type" />
        <p class="vjs-no-js">
          동영상을 재생하려면 JavaScript를 활성화하거나 Video.js를 지원하는 브라우저를 사용하세요.
        </p>
      </video>
    </div>

    <!-- 영상 정보 -->
    <div class="p-3 sm:p-4 bg-white dark:bg-gray-800">
      <!-- 제목 (편집 모드) -->
      <div v-if="editingTitle" class="flex items-center gap-2 mb-2">
        <input
          v-model="editTitle"
          type="text"
          class="flex-1 px-2 py-1 text-sm border border-blue-400 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          @keyup.enter="saveTitle"
          @keyup.esc="cancelEditTitle"
          ref="titleInput"
        />
        <button
          @click="saveTitle"
          class="px-2 py-1 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700"
        >
          {{ t('common.save') }}
        </button>
        <button
          @click="cancelEditTitle"
          class="px-2 py-1 bg-gray-400 text-white text-xs rounded-lg hover:bg-gray-500"
        >
          {{ t('common.cancel') }}
        </button>
      </div>

      <!-- 제목 (보기 모드) -->
      <div v-else class="flex items-start justify-between gap-2 mb-1.5">
        <h4 class="text-sm sm:text-base font-semibold text-gray-900 dark:text-white flex-1 leading-snug">
          {{ video.title || video.file_name }}
        </h4>
        <!-- 관리자 버튼 -->
        <div v-if="isAdmin" class="flex items-center gap-1.5 flex-shrink-0">
          <button
            @click="startEditTitle"
            class="p-1.5 text-gray-400 hover:text-blue-500 transition-colors"
            :title="t('product.installation.videoGuide.editTitle')"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            @click="confirmDelete"
            class="p-1.5 text-gray-400 hover:text-red-500 transition-colors"
            :title="t('common.delete')"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>

      <!-- 설명 -->
      <p v-if="video.description" class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-2 leading-relaxed">
        {{ video.description }}
      </p>

      <!-- 메타정보 -->
      <div class="flex items-center gap-3 text-[10px] sm:text-xs text-gray-400 dark:text-gray-500">
        <span class="flex items-center gap-1">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          {{ formatDate(video.created_at) }}
        </span>
        <span class="flex items-center gap-1">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          {{ formatSize(video.file_size) }}
        </span>
        <!-- 출처 배지 -->
        <span
          :class="video.source === 'scan'
            ? 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300'
            : 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300'"
          class="px-1.5 py-0.5 rounded text-[9px] font-medium"
        >
          {{ video.source === 'scan'
            ? t('product.installation.videoGuide.scanBadge')
            : t('product.installation.videoGuide.uploadBadge') }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { productVideosApi } from '../../api/productVideos'
import { useDialog } from '../../composables/useDialog'

const { t } = useI18n({ useScope: 'global' })
const { confirm, alert } = useDialog()

const props = defineProps({
  video: { type: Object, required: true },
  isAdmin: { type: Boolean, default: false },
})
const emit = defineEmits(['deleted', 'updated'])

const editingTitle = ref(false)
const editTitle = ref('')
const titleInput = ref(null)
let player = null

const videoUrl = computed(() =>
  `/static/videos/${props.video.product_id}/${props.video.file_name}`
)

// ── Video.js 초기화 ──────────────────────────────────────────────
const loadVideoJs = () =>
  new Promise((resolve) => {
    if (window.videojs) return resolve()
    // CSS
    if (!document.getElementById('videojs-css')) {
      const link = document.createElement('link')
      link.id = 'videojs-css'
      link.rel = 'stylesheet'
      link.href = '/videojs/video-js.min.css'
      document.head.appendChild(link)
    }
    // JS
    const script = document.createElement('script')
    script.src = '/videojs/video.min.js'
    script.onload = resolve
    document.head.appendChild(script)
  })

onMounted(async () => {
  await loadVideoJs()
  const el = document.getElementById(`vjs-player-${props.video.id}`)
  if (!el || !window.videojs) return
  player = window.videojs(el, {
    fluid: true,
    controls: true,
    playbackRates: [0.5, 0.75, 1, 1.25, 1.5, 2],
    language: document.documentElement.lang === 'ko' ? 'ko' : 'en',
    playsinline: true,
    html5: {
      nativeVideoTracks: false,
      nativeAudioTracks: false,
      nativeTextTracks: false,
    },
  })
})

onBeforeUnmount(() => {
  if (player && !player.isDisposed()) {
    player.dispose()
    player = null
  }
})

// ── 제목 편집 ────────────────────────────────────────────────────
const startEditTitle = () => {
  editTitle.value = props.video.title || props.video.file_name
  editingTitle.value = true
  nextTick(() => titleInput.value?.focus())
}
const cancelEditTitle = () => { editingTitle.value = false }
const saveTitle = async () => {
  if (!editTitle.value.trim()) return
  try {
    await productVideosApi.update(props.video.id, { title: editTitle.value.trim() })
    editingTitle.value = false
    emit('updated')
  } catch {
    await alert.error(t('common.error'))
  }
}

// ── 삭제 ─────────────────────────────────────────────────────────
const confirmDelete = async () => {
  const ok = await confirm.danger(t('product.installation.videoGuide.deleteConfirm'))
  if (!ok) return
  try {
    await productVideosApi.delete(props.video.id)
    emit('deleted')
  } catch {
    await alert.error(t('common.error'))
  }
}

// ── 유틸 ─────────────────────────────────────────────────────────
const formatDate = (dt) => {
  if (!dt) return ''
  return new Date(dt).toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' })
}
const formatSize = (bytes) => {
  if (!bytes) return ''
  if (bytes >= 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024 / 1024).toFixed(1)} GB`
  if (bytes >= 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`
  return `${(bytes / 1024).toFixed(0)} KB`
}
</script>

<style scoped>
/* Video.js 반응형 */
:deep(.video-js) {
  width: 100%;
  border-radius: 0;
}
:deep(.video-js .vjs-big-play-button) {
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  margin: 0;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  line-height: 60px;
  border: none;
  background-color: rgba(0, 0, 0, 0.6);
}
:deep(.video-js:-webkit-full-screen),
:deep(.video-js:fullscreen) {
  border-radius: 0;
}
@media (max-width: 640px) {
  :deep(.video-js .vjs-big-play-button) {
    width: 48px;
    height: 48px;
    line-height: 48px;
  }
}
</style>
