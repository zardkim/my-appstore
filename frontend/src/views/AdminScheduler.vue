<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
    <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">자동 스캔 스케줄러</h2>

    <!-- Scheduler Status -->
    <div v-if="status" class="mb-6 p-4 rounded-lg" :class="status.is_running ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700' : 'bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600'">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center space-x-2">
          <div class="w-3 h-3 rounded-full" :class="status.is_running ? 'bg-green-500 dark:bg-green-400' : 'bg-gray-400 dark:bg-gray-500'"></div>
          <span class="font-medium text-gray-900 dark:text-white">
            {{ status.is_running ? '실행 중' : '중지됨' }}
          </span>
        </div>
        <button
          @click="status.is_running ? stopScheduler() : showConfigModal = true"
          class="px-4 py-2 rounded-lg transition-colors"
          :class="status.is_running
            ? 'bg-red-500 dark:bg-red-600 text-white hover:bg-red-600 dark:hover:bg-red-700'
            : 'bg-blue-500 dark:bg-blue-600 text-white hover:bg-blue-600 dark:hover:bg-blue-700'"
        >
          {{ status.is_running ? '중지' : '시작' }}
        </button>
      </div>

      <div class="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p class="text-gray-600 dark:text-gray-400">스케줄</p>
          <p class="font-medium text-gray-900 dark:text-white">{{ status.cron_schedule }}</p>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ getCronDescription(status.cron_schedule) }}</p>
        </div>
        <div>
          <p class="text-gray-600 dark:text-gray-400">다음 실행 시간</p>
          <p class="font-medium text-gray-900 dark:text-white">{{ formatDateTime(status.next_run_time) }}</p>
        </div>
        <div>
          <p class="text-gray-600 dark:text-gray-400">마지막 스캔</p>
          <p class="font-medium text-gray-900 dark:text-white">{{ formatDateTime(status.last_scan_time) }}</p>
        </div>
        <div>
          <p class="text-gray-600 dark:text-gray-400">스캔 경로</p>
          <p class="font-medium text-gray-900 dark:text-white">{{ status.scan_paths.length }}개 경로</p>
        </div>
      </div>
    </div>

    <!-- Last Scan Result -->
    <div v-if="status?.last_scan_result" class="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg">
      <h3 class="font-semibold text-blue-900 dark:text-blue-400 mb-2">마지막 스캔 결과</h3>
      <div class="grid grid-cols-2 md:grid-cols-5 gap-3 text-sm">
        <div>
          <p class="text-blue-700 dark:text-blue-300">신규 프로그램</p>
          <p class="text-2xl font-bold text-blue-900 dark:text-blue-400">{{ status.last_scan_result.new_products }}</p>
        </div>
        <div>
          <p class="text-blue-700 dark:text-blue-300">신규 버전</p>
          <p class="text-2xl font-bold text-blue-900 dark:text-blue-400">{{ status.last_scan_result.new_versions }}</p>
        </div>
        <div>
          <p class="text-blue-700 dark:text-blue-300">업데이트</p>
          <p class="text-2xl font-bold text-blue-900 dark:text-blue-400">{{ status.last_scan_result.updated_products }}</p>
        </div>
        <div>
          <p class="text-blue-700 dark:text-blue-300">AI 생성</p>
          <p class="text-2xl font-bold text-blue-900 dark:text-blue-400">{{ status.last_scan_result.ai_generated || 0 }}</p>
        </div>
        <div>
          <p class="text-blue-700 dark:text-blue-300">아이콘</p>
          <p class="text-2xl font-bold text-blue-900 dark:text-blue-400">{{ status.last_scan_result.icons_cached || 0 }}</p>
        </div>
      </div>
    </div>

    <!-- Manual Scan Button -->
    <button
      @click="runManualScan"
      :disabled="scanning"
      class="w-full bg-purple-500 dark:bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-600 dark:hover:bg-purple-700 transition-colors disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:cursor-not-allowed font-medium"
    >
      {{ scanning ? '스캔 중...' : '지금 즉시 스캔 실행' }}
    </button>

    <!-- Config Modal -->
    <div v-if="showConfigModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="showConfigModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-2xl m-4">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">스케줄러 설정</h3>

        <div class="space-y-4">
          <!-- Cron Schedule -->
          <div>
            <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">스캔 스케줄 (Cron 표현식)</label>
            <select
              v-model="configForm.cron_schedule"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="0 2 * * *">매일 새벽 2시</option>
              <option value="0 */6 * * *">6시간마다</option>
              <option value="0 */12 * * *">12시간마다</option>
              <option value="0 0 * * 0">매주 일요일 자정</option>
              <option value="0 0 1 * *">매월 1일 자정</option>
            </select>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ getCronDescription(configForm.cron_schedule) }}</p>
          </div>

          <!-- Scan Paths -->
          <div>
            <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">스캔 경로</label>
            <div class="space-y-2">
              <div v-for="(path, index) in configForm.scan_paths" :key="index" class="flex gap-2">
                <input
                  v-model="configForm.scan_paths[index]"
                  type="text"
                  class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                  placeholder="/mnt/software"
                />
                <button
                  @click="configForm.scan_paths.splice(index, 1)"
                  class="px-4 py-2 bg-red-500 dark:bg-red-600 text-white rounded-lg hover:bg-red-600 dark:hover:bg-red-700"
                >
                  제거
                </button>
              </div>
            </div>
            <button
              @click="configForm.scan_paths.push('')"
              class="mt-2 text-sm text-blue-600 dark:text-blue-400 hover:underline"
            >
              + 경로 추가
            </button>
          </div>

          <!-- AI Toggle -->
          <div>
            <label class="flex items-center space-x-2">
              <input
                type="checkbox"
                v-model="configForm.use_ai"
                class="w-4 h-4 text-blue-600 rounded"
              />
              <span class="text-sm font-medium text-gray-900 dark:text-white">AI 메타데이터 생성 활성화</span>
            </label>
          </div>
        </div>

        <!-- Modal Actions -->
        <div class="flex justify-end space-x-3 mt-6">
          <button
            @click="showConfigModal = false"
            class="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
          >
            취소
          </button>
          <button
            @click="saveAndStartScheduler"
            class="px-4 py-2 bg-blue-500 dark:bg-blue-600 text-white rounded-lg hover:bg-blue-600 dark:hover:bg-blue-700"
          >
            저장 및 시작
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { schedulerApi } from '../api/scheduler'
import { useDialog } from '../composables/useDialog'

const { alert } = useDialog()

const status = ref(null)
const showConfigModal = ref(false)
const scanning = ref(false)

const configForm = ref({
  cron_schedule: '0 2 * * *',
  scan_paths: ['/mnt/software'],
  use_ai: true
})

const loadStatus = async () => {
  try {
    const response = await schedulerApi.getStatus()
    status.value = response.data
  } catch (error) {
    console.error('Failed to load scheduler status:', error)
  }
}

const stopScheduler = async () => {
  try {
    await schedulerApi.stop()
    await loadStatus()
  } catch (error) {
    console.error('Failed to stop scheduler:', error)
  }
}

const saveAndStartScheduler = async () => {
  try {
    await schedulerApi.start(configForm.value)
    showConfigModal.value = false
    await loadStatus()
  } catch (error) {
    console.error('Failed to start scheduler:', error)
  }
}

const runManualScan = async () => {
  scanning.value = true
  try {
    const response = await schedulerApi.runNow()
    await alert.success(`스캔 완료!\n신규 프로그램: ${response.data.result.new_products}개\n신규 버전: ${response.data.result.new_versions}개`)
    await loadStatus()
  } catch (error) {
    console.error('Failed to run manual scan:', error)
    await alert.error('스캔 실행 실패')
  } finally {
    scanning.value = false
  }
}

const getCronDescription = (cron) => {
  const descriptions = {
    '0 2 * * *': '매일 새벽 2시에 실행',
    '0 */6 * * *': '6시간마다 실행',
    '0 */12 * * *': '12시간마다 실행',
    '0 0 * * 0': '매주 일요일 자정에 실행',
    '0 0 1 * *': '매월 1일 자정에 실행'
  }
  return descriptions[cron] || cron
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('ko-KR')
}

onMounted(async () => {
  await loadStatus()
  try {
    const configResponse = await schedulerApi.getConfig()
    if (configResponse.data.scan_paths.length > 0) {
      configForm.value = configResponse.data
    }
  } catch (error) {
    console.error('Failed to load config:', error)
  }
})
</script>
