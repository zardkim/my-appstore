<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-8 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <button @click="goBack" class="flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors mr-4">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            {{ t('tips.cancel') }}
          </button>
          <h1 class="text-xl font-bold text-gray-900 dark:text-white">{{ isEdit ? t('tips.editPost') : t('tips.writePost') }}</h1>
        </div>
        <div class="flex items-center space-x-3">
          <button @click="saveDraft" class="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 font-medium">{{ t('tips.saveDraft') }}</button>
          <button @click="submitPost" class="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 shadow-md font-medium">
            {{ isEdit ? t('tips.updateButton') : t('tips.publishButton') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto px-8 py-6">
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-8">
          <form @submit.prevent="submitPost" class="space-y-6">
            <!-- Category & Notice -->
            <div class="flex items-center space-x-4">
              <div class="flex-1">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('tips.categoryLabel') }}</label>
                <select v-model="post.category" required class="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 text-base bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="">{{ t('tips.selectCategory') }}</option>
                  <option v-if="isAdmin" value="notice">{{ t('tips.categoryNotice') }}</option>
                  <option value="tip">💡 {{ t('tips.categoryTip') }}</option>
                  <option value="tech">⚙️ {{ t('tips.categoryTech') }}</option>
                  <option value="tutorial">📚 {{ t('tips.categoryTutorial') }}</option>
                  <option value="qna">❓ {{ t('tips.categoryQna') }}</option>
                  <option value="news">📰 {{ t('tips.categoryNews') }}</option>
                </select>
              </div>
              <div v-if="isAdmin" class="pt-8">
                <label class="flex items-center cursor-pointer">
                  <input type="checkbox" v-model="post.is_notice" class="w-5 h-5 text-blue-600 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500">
                  <span class="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('tips.publishAsNotice') }}</span>
                </label>
              </div>
            </div>

            <!-- Title -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('tips.titleLabel') }}</label>
              <input
                v-model="post.title"
                type="text"
                required
                maxlength="100"
                class="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 text-lg font-medium bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                :placeholder="t('tips.titlePlaceholder')"
              >
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-2 text-right">{{ post.title.length }} / 100</p>
            </div>

            <!-- Content -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('tips.contentLabel') }}</label>
              <textarea
                id="tinymce-editor"
                v-model="post.content"
                class="w-full"
              ></textarea>
            </div>

            <!-- Tags (Optional) -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('tips.tagsLabel') }}</label>
              <input
                v-model="post.tags"
                type="text"
                class="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                :placeholder="t('tips.tagsPlaceholder')"
              >
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">{{ t('tips.tagsHelp') }}</p>
            </div>

            <!-- Attachments -->
            <div v-if="allowAttachments">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('tips.attachmentsLabel') }}</label>

              <!-- File Upload Area -->
              <div
                @dragover.prevent="isDragging = true"
                @dragleave.prevent="isDragging = false"
                @drop.prevent="handleDrop"
                :class="[
                  'border-2 border-dashed rounded-xl p-6 transition-all',
                  isDragging
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900/50'
                ]"
              >
                <div class="text-center">
                  <svg class="w-12 h-12 mx-auto text-gray-400 dark:text-gray-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    {{ t('tips.dragDropFiles') }}
                  </p>
                  <input
                    ref="fileInput"
                    type="file"
                    multiple
                    @change="handleFileSelect"
                    class="hidden"
                  >
                  <button
                    type="button"
                    @click="$refs.fileInput.click()"
                    class="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-sm font-medium"
                  >
                    {{ t('tips.selectFiles') }}
                  </button>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">{{ t('tips.fileLimit') }}</p>
                </div>
              </div>

              <!-- Attached Files List -->
              <div v-if="attachments.length > 0" class="mt-4 space-y-2">
                <div
                  v-for="(file, index) in attachments"
                  :key="index"
                  class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700 rounded-lg"
                >
                  <div class="flex items-center flex-1 min-w-0">
                    <svg class="w-5 h-5 text-gray-500 dark:text-gray-400 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                    </svg>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ file.name }}</p>
                      <p class="text-xs text-gray-500 dark:text-gray-400">{{ formatFileSize(file.size) }}</p>
                    </div>
                  </div>
                  <button
                    type="button"
                    @click="removeAttachment(index)"
                    class="ml-3 p-1 text-red-500 hover:text-red-700 dark:hover:text-red-400 flex-shrink-0"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Notice -->
            <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-xl p-4">
              <div class="flex items-start">
                <svg class="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="text-sm text-blue-800 dark:text-blue-300">
                  <p class="font-medium mb-1">{{ t('tips.beforePostingTitle') }}</p>
                  <ul class="list-disc list-inside space-y-1 text-blue-700 dark:text-blue-300">
                    <li>{{ t('tips.guidelineAppropriate') }}</li>
                    <li>{{ t('tips.guidelineRespect') }}</li>
                    <li>{{ t('tips.guidelineCopyright') }}</li>
                  </ul>
                </div>
              </div>
            </div>
          </form>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../store/auth'
import { useThemeStore } from '../store/theme'
import { useLocaleStore } from '../store/locale'
import { postsApi } from '../api/posts'
import { imagesApi } from '../api/images'
import { useDialog } from '../composables/useDialog'
import { ENV } from '../utils/env'

const { t } = useI18n({ useScope: 'global' })
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const localeStore = useLocaleStore()
const { alert, confirm } = useDialog()

const isAdmin = computed(() => authStore.user?.role === 'admin')
const isEdit = computed(() => route.params.id !== undefined)

// TinyMCE 언어 매핑 (locale code -> tinymce language file)
// 영어는 TinyMCE 기본 언어이므로 언어 파일 불필요 (undefined 반환)
const TINYMCE_LANGUAGE_MAP = {
  ko: 'ko_KR',
  en: undefined,  // 영어는 기본 언어이므로 언어 파일 불필요
  ja: 'ja',
  zh: 'zh_CN',
  // 필요에 따라 추가 언어 매핑
  // de: 'de',
  // fr: 'fr_FR',
  // es: 'es',
}

const editorLanguage = computed(() => {
  return TINYMCE_LANGUAGE_MAP[localeStore.locale] || undefined
})

let editorInstance = null

const post = ref({
  category: '',
  title: '',
  content: '',
  tags: '',
  is_notice: false
})

// 첨부파일 관련
const allowAttachments = ref(true)
const attachments = ref([])
const isDragging = ref(false)
const fileInput = ref(null)

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
const MAX_FILES = 5

// TinyMCE 스크립트 로드 및 초기화
const initTinyMCE = () => {
  // TinyMCE 스크립트가 이미 로드되었는지 확인
  if (window.tinymce) {
    initEditor()
    return
  }

  // 스크립트 태그 생성 및 로드
  const script = document.createElement('script')
  script.src = '/tinymce/tinymce.min.js'
  script.onload = () => {
    initEditor()
  }
  document.head.appendChild(script)
}

// 에디터 초기화
const initEditor = () => {
  window.tinymce.init({
    selector: '#tinymce-editor',

    // 라이센스 관련 설정 (오픈소스/자체 호스팅용)
    license_key: 'gpl',

    height: 500,
    menubar: true,
    plugins: [
      'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
      'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
      'insertdatetime', 'media', 'table', 'help', 'wordcount'
    ],
    toolbar: 'undo redo | blocks | ' +
      'bold italic forecolor backcolor | alignleft aligncenter ' +
      'alignright alignjustify | bullist numlist outdent indent | ' +
      'link image media | removeformat code | help',

    // 이미지 업로드 핸들러 (서버에 업로드)
    images_upload_handler: async (blobInfo, progress) => {
      const formData = new FormData()
      formData.append('file', blobInfo.blob(), blobInfo.filename())

      try {
        const token = localStorage.getItem('access_token')
        const response = await fetch(`${ENV.BACKEND_URL}/api/images/upload-tinymce`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        })

        if (!response.ok) {
          throw new Error('Image upload failed')
        }

        const data = await response.json()
        return data.location
      } catch (error) {
        console.error('Image upload error:', error)
        throw error
      }
    },

    // 자동 URL 변환 설정
    convert_urls: false,
    relative_urls: false,
    remove_script_host: false,

    content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 14px; line-height: 1.6; }',

    // 언어 설정 (언어 파일이 있는 경우만 설정)
    // undefined인 경우 TinyMCE가 기본 영어를 사용
    ...(editorLanguage.value ? { language: editorLanguage.value } : {}),

    branding: false,
    promotion: false,
    resize: false,
    statusbar: true,
    elementpath: false,
    skin: themeStore.isDark ? 'oxide-dark' : 'oxide',
    content_css: themeStore.isDark ? 'dark' : 'default',
    placeholder: t('tips.contentPlaceholder'),

    // 에디터 내용 변경 시 v-model 업데이트
    setup: (editor) => {
      editorInstance = editor
      editor.on('init', () => {
        // 초기 내용 설정
        if (post.value.content) {
          editor.setContent(post.value.content)
        }
      })
      editor.on('change keyup', () => {
        post.value.content = editor.getContent()
      })
    }
  })
}

// 테마 변경 감지하여 에디터 재초기화
watch(() => themeStore.isDark, () => {
  if (editorInstance) {
    const currentContent = editorInstance.getContent()
    editorInstance.remove()
    initEditor()
    // 에디터가 초기화된 후 내용 복원
    setTimeout(() => {
      if (window.tinymce.get('tinymce-editor')) {
        window.tinymce.get('tinymce-editor').setContent(currentContent)
      }
    }, 100)
  }
})

// 언어 변경 감지하여 에디터 재초기화
watch(() => localeStore.locale, () => {
  if (editorInstance) {
    const currentContent = editorInstance.getContent()
    editorInstance.remove()
    initEditor()
    // 에디터가 초기화된 후 내용 복원
    setTimeout(() => {
      if (window.tinymce.get('tinymce-editor')) {
        window.tinymce.get('tinymce-editor').setContent(currentContent)
      }
    }, 100)
  }
})

// 공지사항 체크박스와 카테고리 자동 연동
watch(() => post.value.is_notice, (newValue) => {
  if (newValue) {
    // 공지사항으로 체크하면 카테고리를 자동으로 'notice'로 설정
    post.value.category = 'notice'
  } else {
    // 공지사항 체크 해제하면 카테고리가 'notice'인 경우 초기화
    if (post.value.category === 'notice') {
      post.value.category = ''
    }
  }
})

// 카테고리 변경시 공지사항 체크박스 자동 연동
watch(() => post.value.category, (newValue) => {
  if (newValue === 'notice') {
    // 카테고리를 'notice'로 선택하면 공지사항 체크박스도 자동으로 체크
    post.value.is_notice = true
  } else if (post.value.is_notice && newValue !== 'notice') {
    // 카테고리를 다른 것으로 변경하고 공지사항이 체크되어 있으면 해제
    post.value.is_notice = false
  }
})

// 파일 크기 포맷팅
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 파일 선택 처리
const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  addFiles(files)
  event.target.value = '' // 같은 파일 다시 선택 가능하도록
}

// 드래그 앤 드롭 처리
const handleDrop = (event) => {
  isDragging.value = false
  const files = Array.from(event.dataTransfer.files)
  addFiles(files)
}

// 파일 추가
const addFiles = (files) => {
  for (const file of files) {
    // 최대 파일 개수 체크
    if (attachments.value.length >= MAX_FILES) {
      alert.warning(t('tips.maxFilesError').replace('{n}', MAX_FILES))
      break
    }

    // 파일 크기 체크
    if (file.size > MAX_FILE_SIZE) {
      alert.warning(t('tips.fileTooLargeError').replace('{name}', file.name).replace('{size}', formatFileSize(MAX_FILE_SIZE)))
      continue
    }

    // 중복 파일 체크
    if (attachments.value.some(f => f.name === file.name && f.size === file.size)) {
      alert.warning(t('tips.duplicateFileError').replace('{name}', file.name))
      continue
    }

    attachments.value.push(file)
  }
}

// 첨부파일 제거
const removeAttachment = (index) => {
  attachments.value.splice(index, 1)
}

onMounted(async () => {
  // localStorage에서 게시판 설정 불러오기
  const savedSettings = localStorage.getItem('boardSettings')
  if (savedSettings) {
    const settings = JSON.parse(savedSettings)
    if (settings.allowAttachments !== undefined) {
      allowAttachments.value = settings.allowAttachments
    }
  }

  // TinyMCE 초기화
  initTinyMCE()

  if (isEdit.value) {
    // 수정 모드: 기존 게시글 데이터 불러오기
    const postId = route.params.id
    try {
      const response = await postsApi.getPost(postId)
      const postData = response.data
      post.value = {
        category: postData.category,
        title: postData.title,
        content: postData.content,
        tags: postData.tags || '',
        is_notice: postData.is_notice
      }
    } catch (error) {
      console.error('Failed to load post:', error)
      await alert.error(t('tips.postLoadFailed'))
      router.push('/tips')
    }
  } else {
    // 새 글 작성: 임시저장 데이터 복구
    const draft = localStorage.getItem('tips_draft')
    if (draft) {
      const shouldRestore = await confirm.info(t('tips.restoreDraftConfirm'))
      if (shouldRestore) {
        post.value = JSON.parse(draft)
      }
    }
  }
})

onBeforeUnmount(() => {
  // 에디터 정리
  if (editorInstance) {
    editorInstance.remove()
  }
})

const goBack = async () => {
  if (post.value.title || post.value.content) {
    const shouldLeave = await confirm.warning(t('tips.leaveConfirm'))
    if (shouldLeave) {
      router.push('/tips')
    }
  } else {
    router.push('/tips')
  }
}

const saveDraft = async () => {
  // TODO: 임시저장 API 호출
  localStorage.setItem('tips_draft', JSON.stringify(post.value))
  await alert.success(t('tips.draftSaved'))
}

const submitPost = async () => {
  if (!post.value.category) {
    await alert.warning(t('tips.selectCategoryError'))
    return
  }

  if (!post.value.title.trim()) {
    await alert.warning(t('tips.enterTitleError'))
    return
  }

  if (!post.value.content.trim()) {
    await alert.warning(t('tips.enterContentError'))
    return
  }

  try {
    // 외부 이미지 처리
    let processedContent = post.value.content.trim()
    let downloadedImages = []

    try {
      const imageProcessResult = await imagesApi.processPostContent(processedContent)
      if (imageProcessResult.data) {
        processedContent = imageProcessResult.data.content
        downloadedImages = imageProcessResult.data.images || []

        if (downloadedImages.length > 0) {
          console.log(`[TipsWrite] Downloaded ${downloadedImages.length} external images`)
        }
      }
    } catch (imageError) {
      console.error('이미지 처리 오류:', imageError)
      // 이미지 처리 실패 시에도 게시글 저장은 계속 진행
    }

    // 첨부파일 업로드
    let uploadedAttachments = []
    if (attachments.value.length > 0) {
      for (const file of attachments.value) {
        try {
          const uploadResult = await postsApi.uploadAttachment(file)
          uploadedAttachments.push({
            filename: uploadResult.data.filename,
            original_filename: uploadResult.data.original_filename,
            size: uploadResult.data.size,
            uploaded_at: uploadResult.data.uploaded_at
          })
        } catch (uploadError) {
          console.error(`첨부파일 업로드 실패 (${file.name}):`, uploadError)
          await alert.warning(t('tips.attachmentUploadFailed').replace('{name}', file.name))
        }
      }
    }

    // 게시글 데이터 준비
    const postData = {
      category: post.value.category,
      title: post.value.title.trim(),
      content: processedContent,
      tags: post.value.tags.trim(),
      is_notice: post.value.is_notice,
      images: downloadedImages,
      attachments: uploadedAttachments
    }

    if (isEdit.value) {
      // 게시글 수정
      await postsApi.updatePost(route.params.id, postData)
      await alert.success(t('tips.postUpdated'))
    } else {
      // 게시글 작성
      await postsApi.createPost(postData)
      await alert.success(t('tips.postCreated'))
    }

    // 임시저장 데이터 삭제
    localStorage.removeItem('tips_draft')

    // 목록으로 이동
    router.push('/tips')
  } catch (error) {
    console.error('게시글 저장 오류:', error)
    const errorMessage = error.response?.data?.detail || error.message || t('tips.postSaveFailed')
    await alert.error(`${t('tips.saveFailed')}${errorMessage}`)
  }
}
</script>
