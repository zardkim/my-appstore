<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50"
    @click.self="close"
  >
    <!-- Background overlay -->
    <div
      class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75 dark:bg-gray-900 dark:bg-opacity-75"
      @click="close"
    ></div>

    <!-- Modal content — 모바일: 전체화면, 데스크톱: 중앙 정렬 -->
    <div class="fixed inset-0 sm:inset-4 md:inset-y-6 md:inset-x-0 md:mx-auto md:max-w-4xl flex flex-col bg-white dark:bg-gray-800 sm:rounded-2xl shadow-2xl overflow-hidden" style="max-height: 100dvh; max-height: 100vh;">
      <!-- Header -->
      <div class="bg-gradient-to-r from-blue-500 to-purple-600 px-4 sm:px-6 py-3 sm:py-4 flex-shrink-0">
        <div class="flex items-center justify-between">
          <h3 class="text-base sm:text-xl font-bold text-white flex items-center gap-2">
            <svg class="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            {{ t('violationAISearchDialog.title') }}
          </h3>
          <button
            @click="close"
            class="text-white hover:text-gray-200 transition-colors p-1.5 sm:p-2 hover:bg-white/10 rounded-lg"
          >
            <svg class="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- 모바일 전용 액션 버튼 바 (헤더 바로 아래 - 항상 보임) -->
      <div class="sm:hidden flex-shrink-0 bg-gray-50 dark:bg-gray-700 px-4 py-2.5 border-b border-gray-200 dark:border-gray-600 flex items-center gap-2">
        <button
          @click="close"
          class="px-3 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors text-sm whitespace-nowrap"
        >
          {{ t('violationAISearchDialog.cancel') }}
        </button>
        <div class="flex-1"></div>
        <!-- 중복 발견 시: AI 검색으로 새 제품 생성 버튼 -->
        <button
          v-if="showDuplicateWarning && duplicates.length > 0"
          @click="proceedWithAISearch"
          class="px-3 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg transition-colors font-medium text-xs"
        >
          새 제품 생성
        </button>
        <!-- 메타데이터 완료 시: 제품 등록 버튼 -->
        <button
          v-else-if="metadata"
          @click="saveMetadata"
          :disabled="saving"
          class="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed text-sm"
        >
          {{ saving ? t('violationAISearchDialog.saving') : t('violationAISearchDialog.createAndMatch') }}
        </button>
      </div>

      <!-- Body (스크롤 영역) -->
      <div class="flex-1 overflow-y-auto px-3 sm:px-6 py-4 sm:py-6">
          <!-- Violation Info -->
          <div class="mb-4 sm:mb-6 p-3 sm:p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg space-y-1.5 sm:space-y-2">
            <p class="text-sm text-blue-900 dark:text-blue-300">
              <strong>{{ t('violationAISearchDialog.searchTarget') }}:</strong> {{ softwareName }}
            </p>
            <p class="text-xs text-blue-700 dark:text-blue-400 truncate">
              <strong>{{ t('violationAISearchDialog.folder') }}:</strong> {{ violation?.folder_path || '' }}
            </p>
            <p class="text-xs text-blue-700 dark:text-blue-400 truncate">
              <strong>{{ t('violationAISearchDialog.file') }}:</strong> {{ violation?.file_name || '' }}
            </p>
          </div>

          <!-- 중복 검사 중 -->
          <div v-if="checkingDuplicates" class="flex flex-col items-center justify-center py-8 sm:py-12">
            <div class="animate-spin rounded-full h-12 w-12 sm:h-16 sm:w-16 border-b-2 border-yellow-500 dark:border-yellow-400 mb-4"></div>
            <p class="text-sm sm:text-base text-gray-600 dark:text-gray-400">중복 제품 확인 중...</p>
          </div>

          <!-- 중복 발견 -->
          <div v-else-if="showDuplicateWarning && duplicates.length > 0" class="space-y-4">
            <div class="p-3 sm:p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-300 dark:border-yellow-600 rounded-lg">
              <div class="flex items-start gap-3">
                <svg class="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div>
                  <p class="text-sm font-semibold text-yellow-800 dark:text-yellow-300">동일한 제품이 이미 등록되어 있습니다</p>
                  <p class="text-xs text-yellow-700 dark:text-yellow-400 mt-1">버전을 기존 제품에 추가하거나, AI 검색으로 새 제품을 생성할 수 있습니다.</p>
                </div>
              </div>
            </div>

            <!-- 중복 목록 -->
            <div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
              <div
                v-for="(dup, idx) in duplicates"
                :key="dup.id"
                class="flex items-center justify-between p-3 sm:p-4 border-b border-gray-100 dark:border-gray-700 last:border-b-0 bg-white dark:bg-gray-800"
              >
                <div class="flex-1 min-w-0 mr-3">
                  <p class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{{ dup.title }}</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{{ dup.vendor || '-' }} · {{ dup.category || '-' }}</p>
                </div>
                <button
                  @click="addVersionToProduct(dup)"
                  :disabled="addingVersion"
                  class="flex-shrink-0 px-3 py-1.5 text-xs bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:opacity-50 whitespace-nowrap"
                >
                  {{ addingVersion ? '추가 중...' : '버전 추가' }}
                </button>
              </div>
            </div>

            <!-- 데스크톱 버튼 -->
            <div class="hidden sm:flex justify-end gap-3 pt-2">
              <button
                @click="close"
                class="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors border border-gray-300 dark:border-gray-600"
              >
                {{ t('violationAISearchDialog.cancel') }}
              </button>
              <button
                @click="proceedWithAISearch"
                class="px-4 py-2 text-sm bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-colors font-medium"
              >
                AI 검색으로 새 제품 생성
              </button>
            </div>
          </div>

          <!-- Loading -->
          <div v-else-if="loading" class="flex flex-col items-center justify-center py-8 sm:py-12">
            <div class="animate-spin rounded-full h-12 w-12 sm:h-16 sm:w-16 border-b-2 border-blue-600 dark:border-blue-400 mb-4"></div>
            <p class="text-sm sm:text-base text-gray-600 dark:text-gray-400">{{ t('violationAISearchDialog.generating') }}</p>
            <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-500 mt-2">{{ t('violationAISearchDialog.maxTime') }}</p>
          </div>

          <!-- Error -->
          <div v-else-if="errorMessage" class="space-y-4">
            <div class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg">
              <div class="flex items-start gap-3">
                <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div class="flex-1">
                  <p class="text-red-700 dark:text-red-400 font-medium">{{ errorMessage }}</p>
                  <p v-if="apiErrorDetail" class="text-sm text-red-600 dark:text-red-500 mt-1">{{ apiErrorDetail }}</p>
                </div>
              </div>
            </div>

            <!-- API Error Actions -->
            <div v-if="isApiError" class="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <button
                @click="testApiConnection"
                :disabled="testingApi"
                class="w-full px-3 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <svg v-if="testingApi" class="animate-spin w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <svg v-else class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                {{ t('violationAISearchDialog.testApiConnection') }}
              </button>
              <button
                @click="goToSettings"
                class="w-full px-3 py-2.5 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors text-sm flex items-center justify-center gap-2"
              >
                <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {{ t('violationAISearchDialog.goToSettings') }}
              </button>
              <button
                @click="startAISearch"
                class="w-full px-3 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors text-sm flex items-center justify-center gap-2"
              >
                <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                {{ t('violationAISearchDialog.retry') }}
              </button>
            </div>

            <!-- API Test Result -->
            <div v-if="apiTestResult" class="p-4 rounded-lg" :class="apiTestResult.success ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700' : 'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700'">
              <div class="flex items-start gap-3">
                <svg v-if="apiTestResult.success" class="w-5 h-5 text-green-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <svg v-else class="w-5 h-5 text-yellow-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div class="flex-1">
                  <p class="font-medium" :class="apiTestResult.success ? 'text-green-700 dark:text-green-400' : 'text-yellow-700 dark:text-yellow-400'">
                    {{ apiTestResult.message }}
                  </p>
                  <div class="text-sm mt-1" :class="apiTestResult.success ? 'text-green-600 dark:text-green-500' : 'text-yellow-600 dark:text-yellow-500'">
                    <p>Provider: {{ apiTestResult.provider }} | Model: {{ apiTestResult.model }}</p>
                    <p v-if="apiTestResult.rate_limit?.remaining_requests">
                      {{ t('violationAISearchDialog.remainingRequests') }}: {{ apiTestResult.rate_limit.remaining_requests }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Success - Metadata Display -->
          <div v-else-if="metadata" class="space-y-4 sm:space-y-6">
            <div class="p-3 sm:p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-lg text-green-700 dark:text-green-400 text-sm">
              ✓ {{ t('violationAISearchDialog.generationComplete') }}
            </div>

            <!-- Metadata: 모바일 카드 / 데스크톱 테이블 -->
            <!-- 모바일 카드 레이아웃 -->
            <div class="sm:hidden space-y-2">
              <div
                v-for="(value, key) in filteredMetadata"
                :key="key"
                class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3 border border-gray-100 dark:border-gray-600"
              >
                <p class="text-[10px] font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1">{{ key }}</p>
                <div class="text-sm text-gray-900 dark:text-gray-200 break-words">
                  <!-- Array values -->
                  <div v-if="Array.isArray(value)" class="space-y-0.5">
                    <div v-for="(item, index) in value" :key="index" class="flex items-start">
                      <span class="text-blue-500 mr-1.5">•</span>
                      <span class="text-xs">{{ typeof item === 'object' ? JSON.stringify(item) : item }}</span>
                    </div>
                    <span v-if="value.length === 0" class="text-gray-400 text-xs">[ ]</span>
                  </div>
                  <!-- Objects -->
                  <div v-else-if="typeof value === 'object' && value !== null" class="space-y-0.5">
                    <div v-for="(v, k) in value" :key="k" class="text-xs">
                      <span class="font-medium text-gray-600 dark:text-gray-400">{{ k }}:</span>
                      <span class="ml-1">{{ typeof v === 'object' ? JSON.stringify(v) : v }}</span>
                    </div>
                  </div>
                  <!-- Empty values -->
                  <span v-else-if="value === '' || value === null" class="text-gray-400 text-xs">{{ t('violationAISearchDialog.empty') }}</span>
                  <!-- Normal values -->
                  <span v-else class="text-sm">{{ value }}</span>
                </div>
              </div>
            </div>

            <!-- 데스크톱 테이블 레이아웃 -->
            <div class="hidden sm:block border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
              <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead class="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase w-1/4">{{ t('violationAISearchDialog.field') }}</th>
                    <th class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">{{ t('violationAISearchDialog.value') }}</th>
                  </tr>
                </thead>
                <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  <tr v-for="(value, key) in filteredMetadata" :key="key">
                    <td class="px-4 sm:px-6 py-3 sm:py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-200">
                      {{ key }}
                    </td>
                    <td class="px-4 sm:px-6 py-3 sm:py-4 text-sm text-gray-700 dark:text-gray-300">
                      <!-- Array values -->
                      <div v-if="Array.isArray(value)" class="space-y-1">
                        <div v-for="(item, index) in value" :key="index" class="flex items-start">
                          <span class="text-blue-500 mr-2">•</span>
                          <span>{{ typeof item === 'object' ? JSON.stringify(item) : item }}</span>
                        </div>
                        <span v-if="value.length === 0" class="text-gray-400">[ ]</span>
                      </div>
                      <!-- Objects -->
                      <div v-else-if="typeof value === 'object' && value !== null" class="bg-gray-50 dark:bg-gray-900 rounded p-3 text-xs">
                        <div v-for="(v, k) in value" :key="k" class="flex items-start">
                          <span class="font-semibold text-gray-600 dark:text-gray-400 mr-2">{{ k }}:</span>
                          <span>{{ typeof v === 'object' ? JSON.stringify(v) : v }}</span>
                        </div>
                      </div>
                      <!-- Empty values -->
                      <span v-else-if="value === '' || value === null" class="text-gray-400">{{ t('violationAISearchDialog.empty') }}</span>
                      <!-- Normal values -->
                      <span v-else>{{ value }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Image Manager (사용 안 함) -->
            <!--
            <ImageManager
              v-if="metadata"
              :product-id="999999"
              :product="metadata"
              :initial-search-query="aiSearchQuery"
              @update:logo="handleLogoUpdate"
              @update:screenshots="handleScreenshotsUpdate"
            />
            -->
          </div>

          <!-- Initial state -->
          <div v-else class="text-center py-8 sm:py-12">
            <svg class="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <p class="text-sm sm:text-base text-gray-600 dark:text-gray-400 mb-4">{{ t('violationAISearchDialog.startSearch') }}</p>
            <button
              @click="startAISearch"
              class="px-5 sm:px-6 py-2.5 sm:py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-colors font-medium text-sm sm:text-base"
            >
              {{ t('violationAISearchDialog.startButton') }}
            </button>
          </div>
        </div>

      <!-- Footer (데스크톱 전용 - 모바일은 상단 버튼 바 사용) -->
      <div class="hidden sm:flex flex-shrink-0 bg-gray-50 dark:bg-gray-700 px-4 sm:px-6 py-3 sm:py-4 border-t border-gray-200 dark:border-gray-600 items-center gap-2 sm:gap-3">
        <button
          @click="close"
          class="px-3 sm:px-4 py-2 sm:py-2.5 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors text-sm whitespace-nowrap"
        >
          {{ t('violationAISearchDialog.cancel') }}
        </button>
        <div class="flex-1"></div>
        <button
          v-if="metadata"
          @click="saveMetadata"
          :disabled="saving"
          class="flex-1 sm:flex-none px-4 sm:px-6 py-2 sm:py-2.5 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base text-center"
        >
          {{ saving ? t('violationAISearchDialog.saving') : t('violationAISearchDialog.createAndMatch') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { metadataApi } from '../../api/metadata'
import { filenameViolationsApi } from '../../api/filenameViolations'
import { productsApi } from '../../api/products'
import { configApi } from '../../api/config'
import { scanApi } from '../../api/scan'
// import ImageManager from '../ImageManager.vue' // 사용 안 함
import { useDialog } from '../../composables/useDialog'

const router = useRouter()
const { t } = useI18n({ useScope: 'global' })
const { alert } = useDialog()

const props = defineProps({
  violation: {
    type: Object,
    default: null
  },
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const apiErrorDetail = ref('')
const isApiError = ref(false)
const testingApi = ref(false)
const apiTestResult = ref(null)
const metadata = ref(null)

// 중복 검사
const checkingDuplicates = ref(false)
const duplicates = ref([])
const showDuplicateWarning = ref(false)
const addingVersion = ref(false)

// AI 설정 (API 키는 서버가 config에서 직접 읽음 - 프론트에서 키를 보관하지 않음)
const aiProvider = ref('gemini')
const aiModel = ref('gemini-2.5-flash')
const useCustomPrompt = ref(false)
const customPromptOpenai = ref('')
const customPromptGemini = ref('')

// 소프트웨어 이름 추출 (폴더명 사용)
const softwareName = computed(() => {
  if (!props.violation?.folder_path) return ''
  const parts = props.violation.folder_path.split('/')
  return parts[parts.length - 1] || ''
})

// 설정 로드 (API 키는 서버가 config에서 직접 읽으므로 provider/model만 로드)
onMounted(async () => {
  try {
    const response = await configApi.getSection('metadata')
    if (response.data) {
      aiProvider.value = response.data.aiProvider || 'gemini'
      aiModel.value = response.data.aiModel || 'gemini-2.5-flash'
      useCustomPrompt.value = !(response.data.useDefaultPrompt !== false)
      customPromptOpenai.value = response.data.customPromptOpenai || ''
      customPromptGemini.value = response.data.customPromptGemini || ''
    }
  } catch (error) {
    console.error('설정 로드 오류:', error)
  }
})

// 다이얼로그 열릴 때 중복 검사 먼저 실행
watch(() => props.isOpen, async (isOpen) => {
  if (isOpen) {
    await nextTick() // props.violation이 완전히 반영될 때까지 대기
    if (!metadata.value && !checkingDuplicates.value) {
      checkDuplicates()
    }
  }
})

// AI 결과의 title + 주요 버전으로 이미지 검색어 구성
const aiSearchQuery = computed(() => {
  if (!metadata.value) return softwareName.value
  const title = metadata.value.title || softwareName.value
  const version = metadata.value.parsed_info?.version || ''
  // 주요 버전만 사용 (v16.0.0 → v16)
  const majorVersion = version.replace(/^(v?\d+).*/, '$1')
  return majorVersion ? `${title} ${majorVersion}` : title
})

const filteredMetadata = computed(() => {
  if (!metadata.value) return {}

  const filtered = {}
  const excludeKeys = ['ai_raw_response', 'ai_provider', 'parsed_info', 'confidence', 'crawl_info', 'screenshots', 'icon_url']

  for (const [key, value] of Object.entries(metadata.value)) {
    if (!excludeKeys.includes(key)) {
      filtered[key] = value
    }
  }

  return filtered
})

const checkDuplicates = async () => {
  if (!props.violation?.id) {
    startAISearch()
    return
  }

  checkingDuplicates.value = true
  duplicates.value = []
  showDuplicateWarning.value = false

  try {
    // 백엔드와 동일한 로직으로 중복 검사 (folder_path 정확매칭 → 유사도 매칭)
    const response = await filenameViolationsApi.findSimilarProducts(props.violation.id)
    const found = response.data.similar_products || []

    if (found.length > 0) {
      duplicates.value = found
      showDuplicateWarning.value = true
    } else {
      startAISearch()
    }
  } catch (error) {
    console.error('중복 검사 오류:', error)
    startAISearch()
  } finally {
    checkingDuplicates.value = false
  }
}

const proceedWithAISearch = () => {
  showDuplicateWarning.value = false
  duplicates.value = []
  startAISearch()
}

const addVersionToProduct = async (targetProduct) => {
  if (!props.violation?.id) return

  addingVersion.value = true
  try {
    const response = await filenameViolationsApi.createProductWithMetadata(
      props.violation.id,
      { title: targetProduct.title }
    )
    if (response.data.success) {
      emit('saved', response.data)
      close()
    } else {
      errorMessage.value = response.data.error || '버전 추가에 실패했습니다.'
    }
  } catch (error) {
    console.error('Version add error:', error)
    errorMessage.value = error.response?.data?.detail || '버전 추가에 실패했습니다.'
  } finally {
    addingVersion.value = false
  }
}

const testApiConnection = async () => {
  testingApi.value = true
  apiTestResult.value = null

  try {
    const response = await scanApi.testAiApi()
    apiTestResult.value = response.data
  } catch (error) {
    console.error('API test error:', error)
    apiTestResult.value = {
      success: false,
      provider: aiProvider.value,
      model: aiModel.value,
      message: error.response?.data?.detail || t('violationAISearchDialog.apiTestFailed')
    }
  } finally {
    testingApi.value = false
  }
}

const goToSettings = () => {
  close()
  router.push('/settings?section=metadata')
}

const startAISearch = async () => {
  if (!softwareName.value) {
    errorMessage.value = t('violationAISearchDialog.noSoftwareName')
    return
  }

  loading.value = true
  errorMessage.value = ''
  apiErrorDetail.value = ''
  isApiError.value = false
  apiTestResult.value = null
  metadata.value = null

  try {
    // 설정을 다시 확인 (최신 설정 반영) - 키는 서버가 config에서 직접 읽으므로 provider/model만 갱신
    const configResponse = await configApi.getSection('metadata')
    if (configResponse.data) {
      aiProvider.value = configResponse.data.aiProvider || 'gemini'
      aiModel.value = configResponse.data.aiModel || 'gemini-2.5-flash'
      useCustomPrompt.value = !(configResponse.data.useDefaultPrompt !== false)
      customPromptOpenai.value = configResponse.data.customPromptOpenai || ''
      customPromptGemini.value = configResponse.data.customPromptGemini || ''
    }

    // 현재 provider에 맞는 커스텀 프롬프트 선택
    const customPrompt = aiProvider.value === 'openai' ? customPromptOpenai.value : customPromptGemini.value

    // 메타데이터 생성 요청 (API 키는 서버가 config에서 직접 읽음)
    const response = await metadataApi.testGeneration(
      softwareName.value.trim(),
      {
        aiProvider: aiProvider.value,
        aiModel: aiModel.value,
        useCustomPrompt: useCustomPrompt.value,
        customPrompt: useCustomPrompt.value ? customPrompt : null
      }
    )

    if (response.data.success) {
      if (response.data.metadata) {
        // AI 에러가 있는 경우 확인
        if (response.data.metadata.ai_error) {
          const aiError = response.data.metadata.ai_error
          isApiError.value = true
          errorMessage.value = aiError.message || t('violationAISearchDialog.apiError')
          apiErrorDetail.value = aiError.detail || ''

          // 에러 유형에 따른 추가 안내
          if (aiError.type === 'rate_limit') {
            apiErrorDetail.value = t('violationAISearchDialog.rateLimitHint')
          } else if (aiError.type === 'insufficient_quota') {
            apiErrorDetail.value = t('violationAISearchDialog.quotaHint')
          } else if (aiError.type === 'invalid_api_key' || aiError.type === 'api_key_blocked') {
            apiErrorDetail.value = t('violationAISearchDialog.apiKeyHint')
          }
        } else {
          metadata.value = response.data.metadata
        }
      } else {
        errorMessage.value = t('violationAISearchDialog.metadataNotFound')
      }
    } else {
      errorMessage.value = response.data.error || t('violationAISearchDialog.generateFailed')
      isApiError.value = true
    }
  } catch (error) {
    console.error('AI search error:', error)
    isApiError.value = true

    if (error.response?.status === 403) {
      errorMessage.value = t('violationAISearchDialog.noPermission')
    } else if (error.response?.status === 429) {
      errorMessage.value = t('violationAISearchDialog.rateLimitError')
      apiErrorDetail.value = t('violationAISearchDialog.rateLimitHint')
    } else if (error.response?.status === 401) {
      errorMessage.value = t('violationAISearchDialog.invalidApiKey')
      apiErrorDetail.value = t('violationAISearchDialog.apiKeyHint')
    } else {
      errorMessage.value = t('violationAISearchDialog.searchError')
      apiErrorDetail.value = error.message || ''
    }
  } finally {
    loading.value = false
  }
}

const saveMetadata = async () => {
  if (!metadata.value || !props.violation?.id) return

  saving.value = true
  errorMessage.value = '' // 이전 에러 초기화

  try {
    // 값이 있는지 확인하는 헬퍼 함수
    const hasValue = (value) => {
      if (value === null || value === undefined) return false
      if (typeof value === 'string') return value.trim().length > 0
      if (Array.isArray(value)) return value.length > 0
      if (typeof value === 'object') return Object.keys(value).length > 0
      return true
    }

    // AI 메타데이터 필드명 → 백엔드 스키마 필드명 매핑 (빈 값 제거)
    const mappedMetadata = {}

    // 기본 필드
    if (hasValue(metadata.value.title)) mappedMetadata.title = metadata.value.title
    if (hasValue(metadata.value.subtitle)) mappedMetadata.subtitle = metadata.value.subtitle
    if (hasValue(metadata.value.category)) mappedMetadata.category = metadata.value.category
    if (hasValue(metadata.value.icon_url)) mappedMetadata.icon_url = metadata.value.icon_url

    // AI: description_short → Backend: description
    const description = metadata.value.description_short || metadata.value.description
    if (hasValue(description)) mappedMetadata.description = description

    // AI: developer → Backend: vendor
    const vendor = metadata.value.developer || metadata.value.vendor
    if (hasValue(vendor)) mappedMetadata.vendor = vendor

    // AI: description_detailed → Backend: detailed_description
    const detailedDesc = metadata.value.description_detailed || metadata.value.detailed_description
    if (hasValue(detailedDesc)) mappedMetadata.detailed_description = detailedDesc

    // 확장 필드
    if (hasValue(metadata.value.official_website)) mappedMetadata.official_website = metadata.value.official_website
    if (hasValue(metadata.value.license_type)) mappedMetadata.license_type = metadata.value.license_type
    if (hasValue(metadata.value.platform)) mappedMetadata.platform = metadata.value.platform
    if (hasValue(metadata.value.features)) mappedMetadata.features = metadata.value.features
    if (hasValue(metadata.value.system_requirements)) mappedMetadata.system_requirements = metadata.value.system_requirements
    if (hasValue(metadata.value.supported_formats)) mappedMetadata.supported_formats = metadata.value.supported_formats
    if (hasValue(metadata.value.release_notes)) mappedMetadata.release_notes = metadata.value.release_notes
    if (hasValue(metadata.value.release_date)) mappedMetadata.release_date = metadata.value.release_date
    if (hasValue(metadata.value.installation_info)) mappedMetadata.installation_info = metadata.value.installation_info
    if (hasValue(metadata.value.screenshots)) mappedMetadata.screenshots = metadata.value.screenshots

    // Create product from violation with AI metadata
    const response = await filenameViolationsApi.createProductWithMetadata(
      props.violation.id,
      mappedMetadata
    )

    if (response.data.success) {
      // 알림은 부모(FilenameViolations.vue handleAIMatchingSaved)에서 처리
      emit('saved', response.data)
      close()
    } else {
      errorMessage.value = response.data.error || t('violationAISearchDialog.createProductFailed')
      await alert.error(errorMessage.value)
    }
  } catch (error) {
    console.error('Save metadata error:', error)
    console.error('Error response:', error.response)

    let errorMsg = t('violationAISearchDialog.createProductFailed')

    if (error.response?.data?.detail) {
      if (typeof error.response.data.detail === 'string') {
        errorMsg = error.response.data.detail
      } else if (Array.isArray(error.response.data.detail)) {
        errorMsg = error.response.data.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ')
      } else {
        errorMsg = JSON.stringify(error.response.data.detail)
      }
    } else if (error.message) {
      errorMsg = error.message
    }

    errorMessage.value = errorMsg
    await alert.error(errorMsg)
  } finally {
    saving.value = false
  }
}

// Helper function to convert full URL to relative path
const toRelativePath = (url) => {
  if (!url) return url
  // http://localhost:8110/static/icons/1.png → /static/icons/1.png
  // https://app.nuripc.kr/static/icons/1.png → /static/icons/1.png
  if (url.includes('/static/')) {
    const afterStatic = url.split('/static/')[1].split('?')[0]
    return '/static/' + afterStatic
  }
  return url
}

// Image update handlers
const handleLogoUpdate = (iconUrl) => {
  if (metadata.value) {
    // Convert full URL to relative path before saving
    const relativePath = toRelativePath(iconUrl)
    console.log('Logo saved from dialog', { icon_url: relativePath })
    metadata.value = {
      ...metadata.value,
      icon_url: relativePath
    }
  }
}

const handleScreenshotsUpdate = (screenshots) => {
  if (metadata.value) {
    // Convert full URLs to relative paths
    const normalizedScreenshots = screenshots.map(s => {
      if (typeof s === 'string') {
        return { type: 'local', url: toRelativePath(s) }
      } else {
        return { ...s, url: toRelativePath(s.url) }
      }
    })
    console.log('Screenshots saved from dialog', { count: normalizedScreenshots.length })
    metadata.value = {
      ...metadata.value,
      screenshots: normalizedScreenshots
    }
  }
}

const close = () => {
  metadata.value = null
  errorMessage.value = ''
  apiErrorDetail.value = ''
  isApiError.value = false
  apiTestResult.value = null
  checkingDuplicates.value = false
  duplicates.value = []
  showDuplicateWarning.value = false
  addingVersion.value = false
  emit('close')
}
</script>
