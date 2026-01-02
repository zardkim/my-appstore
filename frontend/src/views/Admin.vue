<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 sm:px-6 lg:px-8 py-4 sm:py-5 lg:py-6">
      <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white">시스템 관리</h1>
      <p class="text-sm sm:text-base text-gray-600 dark:text-gray-400 mt-1">파일 스캔 및 스케줄러 설정</p>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-5 lg:py-6 pb-20 lg:pb-6">
      <!-- Tabs -->
      <div class="mb-4 sm:mb-6 border-b border-gray-200 dark:border-gray-700 overflow-x-auto">
        <nav class="flex gap-4 sm:gap-6 lg:gap-8 min-w-max">
          <button
            @click="activeTab = 'scan'"
            :class="tabClass('scan')"
          >
            수동 스캔
          </button>
          <button
            @click="activeTab = 'scheduler'"
            :class="tabClass('scheduler')"
          >
            자동 스캔 스케줄러
          </button>
          <button
            @click="activeTab = 'unmatched'"
            :class="tabClass('unmatched')"
          >
            <span class="flex items-center">
              불일치 목록
              <span v-if="unmatchedStats.pending > 0" class="ml-2 px-2 py-1 bg-orange-500 text-white text-xs rounded-full">
                {{ unmatchedStats.pending }}
              </span>
            </span>
          </button>
          <button
            @click="activeTab = 'info'"
            :class="tabClass('info')"
          >
            시스템 정보
          </button>
        </nav>
      </div>

      <!-- Scan Tab -->
      <section v-if="activeTab === 'scan'" class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 sm:p-5 lg:p-6 mb-4 sm:mb-6">
        <h2 class="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white mb-3 sm:mb-4">수동 파일 스캔</h2>

        <div class="mb-4">
          <label class="flex items-center space-x-2 mb-3">
            <input
              type="checkbox"
              v-model="useAI"
              class="w-4 h-4 text-blue-600 rounded"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              AI 메타데이터 생성 활성화 (OpenAI API 필요)
            </span>
          </label>
          <div v-if="useAI" class="text-xs text-gray-600 dark:text-gray-400 ml-6 space-y-1">
            <p>✓ 정확한 프로그램 이름, 설명, 제조사 자동 생성</p>
            <p>✓ 적절한 카테고리 자동 분류</p>
            <p>✓ 공식 아이콘 이미지 다운로드 및 캐싱</p>
          </div>
        </div>

        <div class="flex gap-4">
          <input
            v-model="scanPath"
            type="text"
            placeholder="/mnt/software"
            class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
          />
          <button
            @click="startScan"
            :disabled="scanning"
            class="bg-blue-500 dark:bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-600 dark:hover:bg-blue-700 transition-colors disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:cursor-not-allowed whitespace-nowrap"
          >
            {{ scanning ? '스캔 중...' : '스캔 시작' }}
          </button>
        </div>

        <div v-if="scanResult" class="mt-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-lg">
          <h3 class="font-semibold text-green-800 dark:text-green-400 mb-2">✓ 스캔 완료</h3>
          <ul class="space-y-1 text-sm text-gray-700 dark:text-gray-300">
            <li>• 새로운 프로그램: <span class="font-medium">{{ scanResult.new_products }}개</span></li>
            <li>• 새로운 버전: <span class="font-medium">{{ scanResult.new_versions }}개</span></li>
            <li>• 업데이트된 프로그램: <span class="font-medium">{{ scanResult.updated_products }}개</span></li>
            <li v-if="scanResult.ai_generated !== undefined">
              • AI 메타데이터 생성: <span class="font-medium text-blue-600 dark:text-blue-400">{{ scanResult.ai_generated }}개</span>
            </li>
            <li v-if="scanResult.icons_cached !== undefined">
              • 아이콘 캐싱: <span class="font-medium text-purple-600 dark:text-purple-400">{{ scanResult.icons_cached }}개</span>
            </li>
            <li v-if="scanResult.errors?.length > 0" class="text-red-600 dark:text-red-400">
              • 에러: {{ scanResult.errors.length }}개
              <details class="mt-2">
                <summary class="cursor-pointer hover:underline">에러 상세보기</summary>
                <ul class="mt-2 ml-4 text-xs space-y-1">
                  <li v-for="(error, index) in scanResult.errors" :key="index">{{ error }}</li>
                </ul>
              </details>
            </li>
          </ul>
        </div>

        <p v-if="scanError" class="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 text-red-700 dark:text-red-400 rounded-lg text-sm">
          {{ scanError }}
        </p>
      </section>

      <!-- Scheduler Tab -->
      <AdminScheduler v-if="activeTab === 'scheduler'" />

      <!-- Unmatched Tab -->
      <section v-if="activeTab === 'unmatched'" class="space-y-4 sm:space-y-6">
        <!-- Stats Cards -->
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4">
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-3 sm:p-4">
            <p class="text-xs text-gray-500 dark:text-gray-400">전체</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ unmatchedStats.total }}</p>
          </div>
          <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg shadow p-3 sm:p-4 border-2 border-orange-200 dark:border-orange-700">
            <p class="text-xs text-orange-600 dark:text-orange-400">대기중</p>
            <p class="text-xl sm:text-2xl font-bold text-orange-600 dark:text-orange-400">{{ unmatchedStats.pending }}</p>
          </div>
          <div class="bg-green-50 dark:bg-green-900/20 rounded-lg shadow p-3 sm:p-4">
            <p class="text-xs text-green-600 dark:text-green-400">승인됨</p>
            <p class="text-xl sm:text-2xl font-bold text-green-600 dark:text-green-400">{{ unmatchedStats.approved }}</p>
          </div>
          <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg shadow p-3 sm:p-4">
            <p class="text-xs text-blue-600 dark:text-blue-400">수동입력</p>
            <p class="text-xl sm:text-2xl font-bold text-blue-600 dark:text-blue-400">{{ unmatchedStats.manual }}</p>
          </div>
          <div class="bg-gray-50 dark:bg-gray-700 rounded-lg shadow p-3 sm:p-4">
            <p class="text-xs text-gray-500 dark:text-gray-400">무시됨</p>
            <p class="text-xl sm:text-2xl font-bold text-gray-500 dark:text-gray-400">{{ unmatchedStats.ignored }}</p>
          </div>
        </div>

        <!-- Filter -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-3 sm:p-4">
          <div class="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">상태 필터:</label>
            <select
              v-model="unmatchedFilter"
              @change="loadUnmatchedItems"
              class="flex-1 sm:flex-initial px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            >
              <option value="">전체</option>
              <option value="pending">대기중</option>
              <option value="approved">승인됨</option>
              <option value="manual">수동입력</option>
              <option value="ignored">무시됨</option>
            </select>
            <button
              @click="loadUnmatchedItems"
              class="w-full sm:w-auto sm:ml-auto px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
            >
              🔄 새로고침
            </button>
          </div>
        </div>

        <!-- Items List -->
        <div v-if="loadingUnmatched" class="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center text-gray-500 dark:text-gray-400">
          로딩 중...
        </div>

        <div v-else-if="unmatchedItems.length === 0" class="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center text-gray-500 dark:text-gray-400">
          <p class="text-base sm:text-lg">{{ unmatchedFilter ? '해당 상태의 항목이 없습니다.' : '불일치 항목이 없습니다.' }}</p>
          <p class="text-xs sm:text-sm mt-2">스캔 시 정확도 90% 미만인 항목이 여기에 표시됩니다.</p>
        </div>

        <!-- Desktop Table View -->
        <div v-else-if="!loadingUnmatched && unmatchedItems.length > 0" class="hidden md:block bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">파일명</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">파싱명</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">정확도</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">AI 제안</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">상태</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">등록일</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">작업</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-600">
                <tr
                  v-for="item in unmatchedItems"
                  :key="item.id"
                  class="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">
                    <p class="font-medium truncate max-w-xs" :title="item.file_name">{{ item.file_name }}</p>
                    <p class="text-xs text-gray-500 dark:text-gray-400 truncate" :title="item.file_path">{{ item.file_path }}</p>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
                    {{ item.parsed_name || 'N/A' }}
                  </td>
                  <td class="px-4 py-3 text-sm">
                    <div class="flex items-center">
                      <span
                        :class="getConfidenceClass(item.confidence_score)"
                        class="font-medium"
                      >
                        {{ Math.round(item.confidence_score * 100) }}%
                      </span>
                    </div>
                  </td>
                  <td class="px-4 py-3 text-sm">
                    <div v-if="item.suggested_metadata" class="max-w-xs">
                      <p class="font-medium text-gray-900 dark:text-white truncate">{{ item.suggested_metadata.title }}</p>
                      <p class="text-xs text-gray-500 dark:text-gray-400">{{ item.suggested_metadata.vendor }}</p>
                    </div>
                    <span v-else class="text-gray-400 dark:text-gray-500">없음</span>
                  </td>
                  <td class="px-4 py-3 text-sm">
                    <span :class="getStatusBadgeClass(item.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                      {{ getStatusText(item.status) }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
                    {{ formatDate(item.created_at) }}
                  </td>
                  <td class="px-4 py-3 text-sm text-right">
                    <button
                      @click="viewUnmatchedItem(item)"
                      class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium"
                    >
                      상세
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Mobile Card View -->
        <div v-if="!loadingUnmatched && unmatchedItems.length > 0" class="md:hidden space-y-3">
          <div
            v-for="item in unmatchedItems"
            :key="item.id"
            class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4"
          >
            <!-- File Info Header -->
            <div class="mb-3 pb-3 border-b border-gray-100 dark:border-gray-700">
              <p class="text-sm font-semibold text-gray-900 dark:text-white truncate mb-1" :title="item.file_name">
                {{ item.file_name }}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400 truncate" :title="item.file_path">
                {{ item.file_path }}
              </p>
            </div>

            <!-- Parsed Name & Confidence -->
            <div class="grid grid-cols-2 gap-3 mb-3">
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">파싱명</p>
                <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {{ item.parsed_name || 'N/A' }}
                </p>
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">정확도</p>
                <p class="text-sm font-bold" :class="getConfidenceClass(item.confidence_score)">
                  {{ Math.round(item.confidence_score * 100) }}%
                </p>
              </div>
            </div>

            <!-- AI Suggestion -->
            <div class="mb-3">
              <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">AI 제안</p>
              <div v-if="item.suggested_metadata" class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-2 border border-blue-100 dark:border-blue-800">
                <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {{ item.suggested_metadata.title }}
                </p>
                <p class="text-xs text-gray-600 dark:text-gray-400">
                  {{ item.suggested_metadata.vendor }}
                </p>
              </div>
              <p v-else class="text-sm text-gray-400 dark:text-gray-500">없음</p>
            </div>

            <!-- Status & Date -->
            <div class="flex items-center justify-between mb-3 pb-3 border-b border-gray-100 dark:border-gray-700">
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">상태</p>
                <span :class="getStatusBadgeClass(item.status)" class="inline-flex px-2.5 py-1 rounded-full text-xs font-medium">
                  {{ getStatusText(item.status) }}
                </span>
              </div>
              <div class="text-right">
                <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">등록일</p>
                <p class="text-xs text-gray-600 dark:text-gray-400">
                  {{ formatDate(item.created_at) }}
                </p>
              </div>
            </div>

            <!-- Action Button -->
            <button
              @click="viewUnmatchedItem(item)"
              class="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
            >
              상세 보기
            </button>
          </div>
        </div>
      </section>

      <!-- Info Tab -->
      <section v-if="activeTab === 'info'" class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 sm:p-5 lg:p-6">
        <h2 class="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white mb-3 sm:mb-4">🚀 Phase 2 기능 활성화됨</h2>
        <div class="space-y-3 sm:space-y-4 text-sm sm:text-base text-gray-700 dark:text-gray-300">
          <div class="flex items-start space-x-2 sm:space-x-3">
            <span class="text-green-500 dark:text-green-400 mt-0.5 text-lg">✓</span>
            <div>
              <p class="font-medium text-sm sm:text-base">파일명 파싱 알고리즘</p>
              <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-0.5">파일명에서 소프트웨어 이름, 버전, 제조사 자동 추출</p>
            </div>
          </div>
          <div class="flex items-start space-x-2 sm:space-x-3">
            <span class="text-green-500 dark:text-green-400 mt-0.5 text-lg">✓</span>
            <div>
              <p class="font-medium text-sm sm:text-base">AI 메타데이터 생성</p>
              <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-0.5">OpenAI GPT를 사용하여 정확한 설명, 제조사, 카테고리 생성</p>
            </div>
          </div>
          <div class="flex items-start space-x-2 sm:space-x-3">
            <span class="text-green-500 dark:text-green-400 mt-0.5 text-lg">✓</span>
            <div>
              <p class="font-medium text-sm sm:text-base">아이콘 다운로드 및 캐싱</p>
              <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-0.5">공식 아이콘을 자동으로 찾아서 로컬에 캐쉬</p>
            </div>
          </div>
          <div class="flex items-start space-x-2 sm:space-x-3">
            <span class="text-green-500 dark:text-green-400 mt-0.5 text-lg">✓</span>
            <div>
              <p class="font-medium text-sm sm:text-base">Fallback 메커니즘</p>
              <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-0.5">AI API 키가 없거나 오류 발생 시 파싱 정보로 자동 대체</p>
            </div>
          </div>
        </div>

        <div class="mt-4 sm:mt-6 p-3 sm:p-4 bg-blue-50 dark:bg-blue-900/20 border dark:border-blue-700 rounded-lg">
          <h3 class="font-semibold text-sm sm:text-base text-blue-900 dark:text-blue-400 mb-2">💡 사용 팁</h3>
          <ul class="text-xs sm:text-sm text-blue-800 dark:text-blue-300 space-y-1.5 sm:space-y-2">
            <li class="flex items-start">
              <span class="mr-2">•</span>
              <span>OpenAI API 키를 설정하려면 <code class="bg-white dark:bg-gray-700 px-1 rounded text-xs">.env</code> 파일에서 OPENAI_API_KEY를 설정하세요</span>
            </li>
            <li class="flex items-start">
              <span class="mr-2">•</span>
              <span>AI 기능 없이도 기본 메타데이터로 동작합니다</span>
            </li>
            <li class="flex items-start">
              <span class="mr-2">•</span>
              <span>폴더명이 명확할수록 더 정확한 메타데이터가 생성됩니다</span>
            </li>
          </ul>
        </div>
      </section>
    </div>

    <!-- Unmatched Detail Dialog -->
    <UnmatchedDetailDialog
      :is-open="showDetailDialog"
      :item="selectedItem"
      @close="handleDialogClose"
      @updated="handleDialogUpdated"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { scanApi } from '../api/scan'
import { unmatchedApi } from '../api/unmatched'
import AdminScheduler from './AdminScheduler.vue'
import UnmatchedDetailDialog from '../components/UnmatchedDetailDialog.vue'

const activeTab = ref('scan')
const scanPath = ref('/tmp/myappstore_scan_test')
const useAI = ref(true)
const scanning = ref(false)
const scanResult = ref(null)
const scanError = ref('')

// Unmatched 관련 state
const unmatchedStats = ref({
  total: 0,
  pending: 0,
  approved: 0,
  manual: 0,
  ignored: 0
})
const unmatchedItems = ref([])
const unmatchedFilter = ref('')
const loadingUnmatched = ref(false)
const showDetailDialog = ref(false)
const selectedItem = ref(null)

const tabClass = (tab) => {
  return activeTab.value === tab
    ? 'py-4 border-b-2 border-blue-500 text-blue-600 dark:text-blue-400 font-medium'
    : 'py-4 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
}

const startScan = async () => {
  if (!scanPath.value) {
    scanError.value = '스캔 경로를 입력하세요.'
    return
  }

  scanning.value = true
  scanError.value = ''
  scanResult.value = null

  try {
    const response = await scanApi.startScan(scanPath.value, useAI.value)
    scanResult.value = response.data
  } catch (error) {
    scanError.value = error.response?.data?.detail || '스캔에 실패했습니다.'
  } finally {
    scanning.value = false
  }
}

// Unmatched 관련 메서드
const loadUnmatchedStats = async () => {
  try {
    const response = await unmatchedApi.getStats()
    unmatchedStats.value = response.data
  } catch (error) {
    console.error('통계 로딩 오류:', error)
  }
}

const loadUnmatchedItems = async () => {
  loadingUnmatched.value = true
  try {
    const response = await unmatchedApi.getList(unmatchedFilter.value || null, 0, 100)
    unmatchedItems.value = response.data.items
  } catch (error) {
    console.error('항목 로딩 오류:', error)
  } finally {
    loadingUnmatched.value = false
  }
}

const viewUnmatchedItem = (item) => {
  selectedItem.value = item
  showDetailDialog.value = true
}

const handleDialogClose = () => {
  showDetailDialog.value = false
  selectedItem.value = null
}

const handleDialogUpdated = () => {
  // 목록 및 통계 새로고침
  loadUnmatchedStats()
  loadUnmatchedItems()
}

const getConfidenceClass = (score) => {
  if (score >= 0.9) return 'text-green-600 dark:text-green-400'
  if (score >= 0.7) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
}

const getStatusBadgeClass = (status) => {
  const classes = {
    pending: 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-400',
    approved: 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400',
    manual: 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400',
    ignored: 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-400'
  }
  return classes[status] || classes.pending
}

const getStatusText = (status) => {
  const texts = {
    pending: '대기중',
    approved: '승인됨',
    manual: '수동입력',
    ignored: '무시됨'
  }
  return texts[status] || status
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 탭 변경 감지
watch(activeTab, (newTab) => {
  if (newTab === 'unmatched') {
    loadUnmatchedStats()
    loadUnmatchedItems()
  }
})

// 초기 로드
onMounted(() => {
  loadUnmatchedStats()
})
</script>
