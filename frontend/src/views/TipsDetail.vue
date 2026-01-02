<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-8 py-4">
      <div class="flex items-center justify-between">
        <button @click="goBack" class="flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          목록으로
        </button>
        <div class="flex items-center space-x-2">
          <!-- 스크랩 버튼 (인증된 사용자만) -->
          <button
            v-if="authStore.isAuthenticated"
            @click="toggleScrap"
            class="px-4 py-2 flex items-center space-x-2 hover:bg-amber-50 dark:hover:bg-amber-900/20 rounded-lg transition-colors font-medium text-sm"
            :class="isScraped ? 'text-amber-600 dark:text-amber-400' : 'text-gray-600 dark:text-gray-400'"
          >
            <svg class="w-5 h-5" :fill="isScraped ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
            </svg>
            <span>{{ isScraped ? '스크랩됨' : '스크랩' }}</span>
          </button>
          <!-- 수정/삭제 버튼 (본인 또는 관리자만) -->
          <button v-if="canEditPost" @click="editPost" class="px-4 py-2 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors font-medium text-sm">수정</button>
          <button v-if="canEditPost" @click="deletePost" class="px-4 py-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors font-medium text-sm">삭제</button>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto px-8 py-6">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center h-64">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p class="text-gray-500 dark:text-gray-400">로딩 중...</p>
        </div>
      </div>

      <!-- Post Content -->
      <div v-else-if="post">
      <!-- Post Header -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-8 mb-6">
          <div class="mb-4">
            <span :class="getCategoryStyle(post.category)">{{ getCategoryLabel(post.category) }}</span>
            <span v-if="post.is_notice" class="ml-2 inline-flex items-center px-2 py-1 rounded-md text-xs font-bold bg-red-500 dark:bg-red-600 text-white">공지</span>
          </div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">{{ post.title }}</h1>
          <div class="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 pb-4 border-b border-gray-200 dark:border-gray-700">
            <div class="flex items-center space-x-4">
              <div class="flex items-center">
                <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mr-3">
                  <span class="text-sm font-bold text-white">{{ post.author_username.charAt(0).toUpperCase() }}</span>
                </div>
                <div>
                  <p class="font-medium text-gray-700 dark:text-gray-300">{{ post.author_username }}</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">{{ formatDate(post.created_at) }}</p>
                </div>
              </div>
            </div>
            <div class="flex items-center space-x-4 text-gray-500 dark:text-gray-400">
              <div class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                {{ post.views }}
              </div>
              <div class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                {{ comments.length }}
              </div>
            </div>
          </div>
        </div>

        <!-- Post Content -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-8 mb-6">
          <div class="prose prose-lg dark:prose-invert max-w-none text-gray-900 dark:text-gray-100" v-html="post.content"></div>
        </div>

        <!-- Attachments Section -->
        <div v-if="allowAttachments && attachments.length > 0" class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-8 mb-6">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center">
            <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
            </svg>
            첨부파일 {{ attachments.length }}
          </h3>

          <div class="space-y-2">
            <div
              v-for="(file, index) in attachments"
              :key="index"
              class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-blue-200 dark:hover:border-blue-700 transition-all group"
            >
              <div class="flex items-center flex-1 min-w-0">
                <!-- File Icon -->
                <div class="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mr-4">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>

                <!-- File Info -->
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ file.original_filename }}</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {{ formatFileSize(file.size) }}
                  </p>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="flex items-center space-x-2 ml-4">
                <!-- Download Button -->
                <button
                  @click="downloadAttachment(file)"
                  class="p-2 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
                  title="다운로드"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                </button>

                <!-- Delete Button (Admin or Author only) -->
                <button
                  v-if="canEditPost"
                  @click="deleteAttachment(index)"
                  class="p-2 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                  title="삭제"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Comments Section -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-8">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-6">댓글 {{ comments.length }}</h3>

          <!-- Comment Input -->
          <div class="mb-8 pb-6 border-b border-gray-200 dark:border-gray-700">
            <textarea v-model="newComment" rows="4" class="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" placeholder="댓글을 입력하세요"></textarea>
            <div class="flex justify-end mt-3">
              <button @click="submitComment" class="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 shadow-md font-medium">댓글 작성</button>
            </div>
          </div>

          <!-- Comments List -->
          <div v-if="comments.length > 0" class="space-y-6">
            <div v-for="comment in comments" :key="comment.id" class="flex items-start space-x-4">
              <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-sm font-bold text-white">{{ comment.author.charAt(0).toUpperCase() }}</span>
              </div>
              <div class="flex-1">
                <div class="flex items-center justify-between mb-2">
                  <div class="flex items-center space-x-3">
                    <span class="font-medium text-gray-900 dark:text-white">{{ comment.author }}</span>
                    <span class="text-sm text-gray-500 dark:text-gray-400">{{ formatDate(comment.created_at) }}</span>
                  </div>
                  <!-- 수정/삭제 버튼 (본인 또는 관리자만) -->
                  <div v-if="canEditComment(comment)" class="flex items-center space-x-2">
                    <button
                      v-if="editingCommentId !== comment.id"
                      @click="startEditComment(comment)"
                      class="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                    >수정</button>
                    <button
                      @click="deleteComment(comment.id)"
                      class="text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
                    >삭제</button>
                  </div>
                </div>
                <!-- 수정 모드 -->
                <div v-if="editingCommentId === comment.id" class="space-y-2">
                  <textarea
                    v-model="editingCommentContent"
                    rows="3"
                    class="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  ></textarea>
                  <div class="flex justify-end space-x-2">
                    <button
                      @click="cancelEditComment"
                      class="px-4 py-1.5 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                    >취소</button>
                    <button
                      @click="saveEditComment(comment.id)"
                      class="px-4 py-1.5 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                    >저장</button>
                  </div>
                </div>
                <!-- 일반 모드 -->
                <p v-else class="text-gray-700 dark:text-gray-300 leading-relaxed">{{ comment.content }}</p>
              </div>
            </div>
          </div>

          <!-- Empty Comments -->
          <div v-else class="text-center py-12 text-gray-400 dark:text-gray-500">
            <svg class="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <p class="text-lg font-medium">아직 댓글이 없습니다</p>
            <p class="text-sm mt-2">첫 번째 댓글을 작성해보세요!</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { scrapsApi } from '../api/scraps'
import { postsApi } from '../api/posts'
import { commentsApi } from '../api/comments'
import { useDialog } from '../composables/useDialog'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { alert, confirm } = useDialog()

const currentUser = computed(() => authStore.user?.username || 'admin')
const isAdmin = computed(() => authStore.user?.role === 'admin')
const isAuthor = computed(() => post.value?.author_username === currentUser.value)
const canEditPost = computed(() => isAuthor.value || isAdmin.value)

const loading = ref(true)
const newComment = ref('')
const comments = ref([])
const isScraped = ref(false)

// 댓글 수정 관련
const editingCommentId = ref(null)
const editingCommentContent = ref('')

// 첨부파일 관련
const allowAttachments = ref(true)
const attachments = ref([])

// Post data loaded from API
const post = ref(null)

onMounted(async () => {
  try {
    loading.value = true
    const postId = route.params.id

    // Load post data from API
    const response = await postsApi.getPost(postId)
    post.value = response.data

    // localStorage에서 게시판 설정 불러오기
    const savedSettings = localStorage.getItem('boardSettings')
    if (savedSettings) {
      const settings = JSON.parse(savedSettings)
      if (settings.allowAttachments !== undefined) {
        allowAttachments.value = settings.allowAttachments
      }
    }

    // Load attachments from post data
    attachments.value = post.value.attachments || []

    // Load comments from API
    await loadComments()

    // 스크랩 상태 확인 (인증된 사용자만)
    if (authStore.isAuthenticated) {
      await checkScrap()
    }
  } catch (error) {
    console.error('Failed to load post:', error)
    await alert.error('게시글을 불러오는데 실패했습니다.')
    router.push('/tips')
  } finally {
    loading.value = false
  }
})

const getCategoryLabel = (category) => {
  const labels = {
    tip: '팁',
    tech: '기술',
    tutorial: '튜토리얼',
    qna: 'Q&A',
    news: '뉴스'
  }
  return labels[category] || category
}

const getCategoryStyle = (category) => {
  const styles = {
    tip: 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300',
    tech: 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300',
    tutorial: 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-300',
    qna: 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 dark:bg-yellow-900/50 text-yellow-800 dark:text-yellow-300',
    news: 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-300'
  }
  return styles[category] || styles.tip
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays < 1) {
    const hours = Math.floor(diffTime / (1000 * 60 * 60))
    if (hours < 1) {
      const minutes = Math.floor(diffTime / (1000 * 60))
      return `${minutes}분 전`
    }
    return `${hours}시간 전`
  } else if (diffDays < 2) {
    return '어제'
  } else if (diffDays < 7) {
    return `${diffDays}일 전`
  } else {
    return date.toLocaleDateString('ko-KR')
  }
}

const goBack = () => {
  router.push('/tips')
}

const editPost = () => {
  router.push(`/tips/edit/${post.value.id}`)
}

const deletePost = async () => {
  const shouldDelete = await confirm.danger('정말 이 게시글을 삭제하시겠습니까?', '게시글 삭제')
  if (!shouldDelete) {
    return
  }

  try {
    await postsApi.deletePost(post.value.id)
    await alert.success('게시글이 삭제되었습니다.')
    router.push('/tips')
  } catch (error) {
    console.error('Failed to delete post:', error)
    const errorMessage = error.response?.data?.detail || error.message || '게시글 삭제에 실패했습니다.'
    await alert.error(`삭제 실패: ${errorMessage}`)
  }
}

const loadComments = async () => {
  try {
    const postId = route.params.id
    const response = await commentsApi.getComments(postId)
    comments.value = response.data.map(comment => ({
      id: comment.id,
      author: comment.author_username,
      author_id: comment.author_id,
      content: comment.content,
      created_at: comment.created_at
    }))
  } catch (error) {
    console.error('Failed to load comments:', error)
    // 댓글 로딩 실패는 조용히 처리 (게시글은 볼 수 있어야 함)
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) {
    await alert.warning('댓글 내용을 입력해주세요.')
    return
  }

  try {
    const postId = route.params.id
    const response = await commentsApi.createComment(postId, newComment.value)

    comments.value.push({
      id: response.data.id,
      author: response.data.author_username,
      author_id: response.data.author_id,
      content: response.data.content,
      created_at: response.data.created_at
    })

    newComment.value = ''

    // 게시글 데이터 새로고침 (댓글 수 업데이트)
    const postResponse = await postsApi.getPost(postId)
    post.value.comments_count = postResponse.data.comments_count
  } catch (error) {
    console.error('Failed to create comment:', error)
    if (error.response?.status === 401) {
      await alert.warning('로그인이 필요합니다.')
    } else {
      await alert.error('댓글 작성에 실패했습니다.')
    }
  }
}

// 스크랩 관련 함수
const checkScrap = async () => {
  try {
    const response = await scrapsApi.getMyScraps()
    const postId = String(route.params.id)
    isScraped.value = response.data.some(scrap => String(scrap.post_id) === postId)
  } catch (error) {
    console.error('Failed to check scrap:', error)
  }
}

const toggleScrap = async () => {
  const postId = String(route.params.id)
  try {
    if (isScraped.value) {
      await scrapsApi.removeScrap(postId)
      isScraped.value = false
    } else {
      await scrapsApi.addScrap(postId, post.value.title)
      isScraped.value = true
    }
  } catch (error) {
    console.error('Failed to toggle scrap:', error)
    if (error.response?.status === 401) {
      await alert.warning('로그인이 필요합니다.')
    } else {
      await alert.error('스크랩 처리에 실패했습니다.')
    }
  }
}

// 댓글 수정/삭제 권한 체크
const canEditComment = (comment) => {
  return comment.author === currentUser.value || isAdmin.value || comment.author_id === authStore.user?.id
}

// 댓글 수정 시작
const startEditComment = (comment) => {
  editingCommentId.value = comment.id
  editingCommentContent.value = comment.content
}

// 댓글 수정 취소
const cancelEditComment = () => {
  editingCommentId.value = null
  editingCommentContent.value = ''
}

// 댓글 수정 저장
const saveEditComment = async (commentId) => {
  if (!editingCommentContent.value.trim()) {
    await alert.warning('댓글 내용을 입력해주세요.')
    return
  }

  try {
    const response = await commentsApi.updateComment(commentId, editingCommentContent.value)

    const comment = comments.value.find(c => c.id === commentId)
    if (comment) {
      comment.content = response.data.content
    }

    cancelEditComment()
  } catch (error) {
    console.error('Failed to update comment:', error)
    if (error.response?.status === 401) {
      await alert.warning('로그인이 필요합니다.')
    } else if (error.response?.status === 403) {
      await alert.error('댓글을 수정할 권한이 없습니다.')
    } else {
      await alert.error('댓글 수정에 실패했습니다.')
    }
  }
}

// 댓글 삭제
const deleteComment = async (commentId) => {
  const shouldDelete = await confirm.danger('정말 이 댓글을 삭제하시겠습니까?', '댓글 삭제')
  if (!shouldDelete) {
    return
  }

  try {
    await commentsApi.deleteComment(commentId)

    const index = comments.value.findIndex(c => c.id === commentId)
    if (index !== -1) {
      comments.value.splice(index, 1)
    }

    // 게시글 데이터 새로고침 (댓글 수 업데이트)
    const postId = route.params.id
    const postResponse = await postsApi.getPost(postId)
    post.value.comments_count = postResponse.data.comments_count
  } catch (error) {
    console.error('Failed to delete comment:', error)
    if (error.response?.status === 401) {
      await alert.warning('로그인이 필요합니다.')
    } else if (error.response?.status === 403) {
      await alert.error('댓글을 삭제할 권한이 없습니다.')
    } else {
      await alert.error('댓글 삭제에 실패했습니다.')
    }
  }
}

// 파일 크기 포맷팅
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 첨부파일 다운로드
const downloadAttachment = async (file) => {
  try {
    // 다운로드 URL 생성
    const downloadUrl = postsApi.getAttachmentUrl(file.filename)

    // 브라우저 다운로드 트리거
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = file.original_filename
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Download error:', error)
    await alert.error('파일 다운로드에 실패했습니다.')
  }
}

// 첨부파일 삭제
const deleteAttachment = async (index) => {
  const shouldDelete = await confirm.danger('정말 이 첨부파일을 삭제하시겠습니까?', '첨부파일 삭제')
  if (!shouldDelete) {
    return
  }

  const file = attachments.value[index]
  // TODO: API 호출로 서버에서 삭제
  console.log('Deleting file:', file.name)

  attachments.value.splice(index, 1)
  await alert.success('첨부파일이 삭제되었습니다.')
}
</script>
