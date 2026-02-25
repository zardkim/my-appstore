<template>
  <div
    v-if="modelValue"
    class="fixed inset-0 z-50 flex items-center justify-center p-4"
    @click.self="close"
  >
    <div class="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>
    <div class="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-md">

      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-gray-700">
        <div class="flex items-center gap-2">
          <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
          <span class="text-base font-semibold text-gray-900 dark:text-white">{{ t('share.title') }}</span>
        </div>
        <button @click="close" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Body -->
      <div class="px-6 py-5">

        <!-- 생성 성공 화면 -->
        <div v-if="created" class="space-y-4">
          <div class="flex items-center gap-2 text-green-600 dark:text-green-400 mb-4">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span class="font-medium">{{ t('share.createdSuccess') }}</span>
          </div>

          <!-- 공유 정보 박스 (링크 + 비밀번호 + 만료) -->
          <div class="bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl p-4 space-y-3">
            <!-- 링크 -->
            <div class="flex items-start gap-2">
              <span class="text-xs font-semibold text-gray-400 dark:text-gray-500 w-16 flex-shrink-0 pt-0.5">🔗 링크</span>
              <span class="text-sm text-gray-700 dark:text-gray-300 break-all leading-relaxed">{{ createdData.share_url }}</span>
            </div>
            <!-- 비밀번호 -->
            <div class="flex items-center gap-2">
              <span class="text-xs font-semibold text-gray-400 dark:text-gray-500 w-16 flex-shrink-0">🔑 비밀번호</span>
              <span class="font-mono text-lg font-bold text-blue-600 dark:text-blue-400 tracking-widest">{{ createdData.password }}</span>
            </div>
            <!-- 만료 -->
            <div class="flex items-center gap-2">
              <span class="text-xs font-semibold text-gray-400 dark:text-gray-500 w-16 flex-shrink-0">⏰ 만료</span>
              <span class="text-sm text-gray-600 dark:text-gray-400">{{ formatDate(createdData.expires_at) }}</span>
            </div>
          </div>

          <!-- 한번에 복사 버튼 -->
          <button
            @click="copyAll"
            class="w-full py-3 rounded-xl text-sm font-semibold flex items-center justify-center gap-2 transition-colors"
            :class="copied
              ? 'bg-green-500 text-white'
              : 'bg-blue-600 hover:bg-blue-700 text-white'"
          >
            <svg v-if="copied" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            {{ copied ? t('share.copied') : t('share.copyAll') }}
          </button>

          <!-- 경고 메시지 -->
          <div class="flex items-start gap-2 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-lg">
            <svg class="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span class="text-xs text-amber-700 dark:text-amber-300">{{ t('share.passwordWarning') }}</span>
          </div>

          <!-- 버튼 -->
          <div class="flex gap-2 pt-1">
            <router-link
              to="/my/share-links"
              @click="close"
              class="flex-1 text-center px-4 py-2 text-sm border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              {{ t('share.manageLinks') }}
            </router-link>
            <button
              @click="close"
              class="flex-1 px-4 py-2 text-sm bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors"
            >
              {{ t('common.close') }}
            </button>
          </div>
        </div>

        <!-- 생성 폼 -->
        <div v-else class="space-y-4">
          <!-- 제품명 표시 -->
          <div class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-xl">
            <img
              v-if="product?.icon_url"
              :src="product.icon_url"
              class="w-10 h-10 rounded-lg object-cover flex-shrink-0"
              @error="e => e.target.style.display='none'"
            />
            <div v-else class="w-10 h-10 bg-gray-200 dark:bg-gray-600 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <div class="min-w-0">
              <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ product?.title }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('share.oneTimeShare') }}</p>
            </div>
          </div>

          <!-- 공유 기간 선택 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('share.expiresIn') }}</label>
            <div class="flex gap-2">
              <button
                v-for="day in [1, 2, 3, 4, 5]"
                :key="day"
                @click="selectedDays = day"
                :class="[
                  'flex-1 py-2 rounded-lg text-sm font-medium transition-colors',
                  selectedDays === day
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                ]"
              >
                {{ t('share.days', { n: day }) }}
              </button>
            </div>
          </div>

          <!-- 메모 (선택) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ t('share.note') }}
              <span class="text-xs font-normal text-gray-400 ml-1">({{ t('common.optional') }})</span>
            </label>
            <input
              v-model="noteText"
              type="text"
              maxlength="200"
              :placeholder="t('share.notePlaceholder')"
              class="w-full text-sm bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <!-- 에러 메시지 -->
          <div v-if="errorMsg" class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg text-sm text-red-600 dark:text-red-400">
            {{ errorMsg }}
          </div>

          <!-- 버튼 -->
          <div class="flex gap-2 pt-1">
            <button
              @click="close"
              class="flex-1 px-4 py-2 text-sm border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              {{ t('common.cancel') }}
            </button>
            <button
              @click="createLink"
              :disabled="creating"
              class="flex-1 px-4 py-2 text-sm bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <svg v-if="creating" class="animate-spin w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {{ creating ? t('common.loading') : t('share.createLink') }}
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { shareApi } from '../../api/share'

const props = defineProps({
  modelValue: Boolean,
  product: Object,
})

const emit = defineEmits(['update:modelValue'])

const { t } = useI18n({ useScope: 'global' })

const selectedDays = ref(1)
const noteText = ref('')
const creating = ref(false)
const created = ref(false)
const createdData = ref(null)
const errorMsg = ref('')
const copied = ref(false)

const close = () => {
  emit('update:modelValue', false)
  setTimeout(() => {
    created.value = false
    createdData.value = null
    selectedDays.value = 1
    noteText.value = ''
    errorMsg.value = ''
    copied.value = false
  }, 300)
}

const createLink = async () => {
  if (creating.value) return
  creating.value = true
  errorMsg.value = ''
  try {
    const res = await shareApi.create(props.product.id, selectedDays.value, noteText.value)
    createdData.value = res.data
    created.value = true
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || t('common.error')
  } finally {
    creating.value = false
  }
}

const copyAll = async () => {
  const d = createdData.value
  const expireText = formatDate(d.expires_at)
  const text = [
    `[${props.product?.title}] ${t('share.copyTemplate.title')}`,
    '',
    `🔗 ${t('share.copyTemplate.link')}: ${d.share_url}`,
    `🔑 ${t('share.copyTemplate.password')}: ${d.password}`,
    `⏰ ${t('share.copyTemplate.expires')}: ${expireText}`,
    '',
    `※ ${t('share.copyTemplate.notice')}`,
  ].join('\n')

  try {
    await navigator.clipboard.writeText(text)
  } catch {
    const el = document.createElement('textarea')
    el.value = text
    document.body.appendChild(el)
    el.select()
    document.execCommand('copy')
    document.body.removeChild(el)
  }
  copied.value = true
  setTimeout(() => { copied.value = false }, 2500)
}

const formatDate = (isoString) => {
  if (!isoString) return ''
  const d = new Date(isoString)
  return d.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>
