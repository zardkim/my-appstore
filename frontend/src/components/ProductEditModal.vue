<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50" @click.self="closeModal">
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">제품 편집</h2>
        <button
          @click="closeModal"
          class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 space-y-6">
        <!-- Icon Preview -->
        <div class="flex justify-center">
          <div class="w-32 h-32 bg-gray-100 dark:bg-gray-700 rounded-2xl flex items-center justify-center overflow-hidden">
            <img
              v-if="form.icon_url"
              :src="form.icon_url"
              alt="Icon"
              class="w-full h-full object-cover"
              @error="onIconError"
            />
            <span v-else class="text-4xl text-gray-400">📦</span>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-xl text-red-700 dark:text-red-400 text-sm">
          {{ errorMessage }}
        </div>

        <!-- Title -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            제품명 <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.title"
            type="text"
            class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            placeholder="예: Adobe Photoshop"
            required
          />
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            설명
          </label>
          <textarea
            v-model="form.description"
            rows="3"
            class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 resize-none"
            placeholder="예: 전문가용 사진 편집 및 그래픽 디자인 소프트웨어"
          ></textarea>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">50-100자 이내의 간단한 설명을 입력하세요</p>
        </div>

        <!-- Vendor -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            제조사
          </label>
          <input
            v-model="form.vendor"
            type="text"
            class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            placeholder="예: Adobe, Microsoft"
          />
        </div>

        <!-- Category -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            카테고리 <span class="text-red-500">*</span>
          </label>
          <select
            v-model="form.category"
            class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            required
          >
            <option value="">카테고리 선택</option>
            <option v-for="cat in categories" :key="cat.name" :value="cat.name">
              {{ cat.icon }} {{ cat.label }}
            </option>
          </select>
        </div>

        <!-- Icon URL -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            아이콘 URL
          </label>
          <input
            v-model="form.icon_url"
            type="text"
            class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            placeholder="예: /static/icons/adobe-photoshop.png"
          />
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">아이콘 이미지 URL 또는 로컬 경로를 입력하세요</p>
        </div>

        <!-- Folder Path (Read-only) -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            폴더 경로 (읽기 전용)
          </label>
          <input
            :value="product.folder_path"
            type="text"
            class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl bg-gray-50 dark:bg-gray-900 text-gray-500 dark:text-gray-400 cursor-not-allowed"
            disabled
          />
        </div>
      </div>

      <!-- Footer -->
      <div class="sticky bottom-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-6 py-4 flex gap-3">
        <button
          @click="closeModal"
          class="flex-1 px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium"
        >
          취소
        </button>
        <button
          @click="saveChanges"
          :disabled="saving || !isFormValid"
          class="flex-1 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ saving ? '저장 중...' : '저장' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { productsApi } from '../api/products'
import { configApi } from '../api/config'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  product: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'updated'])

// State
const form = ref({
  title: '',
  description: '',
  vendor: '',
  category: '',
  icon_url: ''
})

const categories = ref([
  { name: 'Graphics', label: '그래픽', icon: '🎨' },
  { name: 'Office', label: '오피스', icon: '📊' },
  { name: 'Development', label: '개발', icon: '💻' },
  { name: 'Utility', label: '유틸리티', icon: '🛠️' },
  { name: 'Media', label: '미디어', icon: '🎬' },
  { name: 'OS', label: '운영체제', icon: '💿' },
  { name: 'Security', label: '보안', icon: '🔒' },
  { name: 'Network', label: '네트워크', icon: '🌐' },
  { name: 'Mac', label: '맥', icon: '🍎' },
  { name: 'Mobile', label: '모바일', icon: '📱' },
  { name: 'Patch', label: '패치', icon: '🔧' },
  { name: 'Driver', label: '드라이버', icon: '⚙️' },
  { name: 'Source', label: '소스', icon: '📦' },
  { name: 'Backup', label: '백업&복구', icon: '💾' },
  { name: 'Portable', label: '포터블', icon: '🎒' },
  { name: 'Business', label: '업무용', icon: '💼' },
  { name: 'Engineering', label: '공학용', icon: '📐' },
  { name: 'Theme', label: '테마&스킨', icon: '🎭' },
  { name: 'Hardware', label: '하드웨어', icon: '🔌' },
  { name: 'Uncategorized', label: '미분류', icon: '📂' }
])

const saving = ref(false)
const errorMessage = ref('')

// Computed
const isFormValid = computed(() => {
  return form.value.title && form.value.title.trim() !== '' && form.value.category !== ''
})

// Watch for product changes
watch(() => props.product, (newProduct) => {
  if (newProduct && props.isOpen) {
    loadCategories()
    resetForm()
  }
}, { immediate: true })

watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    resetForm()
    errorMessage.value = ''
  }
})

// Methods
const loadCategories = async () => {
  try {
    const response = await configApi.getSection('categories')
    if (response.data && Array.isArray(response.data)) {
      categories.value = response.data
    }
  } catch (error) {
    console.error('카테고리 로드 실패:', error)
    // Fallback to default categories
  }
}

const resetForm = () => {
  form.value = {
    title: props.product.title || '',
    description: props.product.description || '',
    vendor: props.product.vendor || '',
    category: props.product.category || '',
    icon_url: props.product.icon_url || ''
  }
}

const onIconError = (e) => {
  e.target.src = '' // Clear broken image
}

const saveChanges = async () => {
  if (!isFormValid.value) {
    errorMessage.value = '제품명과 카테고리는 필수 항목입니다.'
    return
  }

  saving.value = true
  errorMessage.value = ''

  try {
    // 변경된 필드만 전송
    const updateData = {}
    if (form.value.title !== props.product.title) updateData.title = form.value.title
    if (form.value.description !== props.product.description) updateData.description = form.value.description
    if (form.value.vendor !== props.product.vendor) updateData.vendor = form.value.vendor
    if (form.value.category !== props.product.category) updateData.category = form.value.category
    if (form.value.icon_url !== props.product.icon_url) updateData.icon_url = form.value.icon_url

    // 변경 사항이 없으면 바로 닫기
    if (Object.keys(updateData).length === 0) {
      closeModal()
      return
    }

    await productsApi.updateProduct(props.product.id, updateData)

    emit('updated')
    closeModal()
  } catch (error) {
    console.error('제품 업데이트 실패:', error)
    if (error.response?.status === 400) {
      errorMessage.value = error.response.data.detail || '잘못된 입력입니다.'
    } else if (error.response?.status === 403) {
      errorMessage.value = '권한이 없습니다. 관리자만 제품을 수정할 수 있습니다.'
    } else {
      errorMessage.value = '제품 업데이트에 실패했습니다. 다시 시도해주세요.'
    }
  } finally {
    saving.value = false
  }
}

const closeModal = () => {
  emit('close')
}
</script>
