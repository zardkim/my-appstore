<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
    <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">{{ t('settings.scheduler.title') }}</h2>

    <!-- Scheduler Status -->
    <div v-if="status" class="mb-6 p-4 rounded-lg" :class="status.is_running ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700' : 'bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600'">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center space-x-2">
          <div class="w-3 h-3 rounded-full" :class="status.is_running ? 'bg-green-500 dark:bg-green-400' : 'bg-gray-400 dark:bg-gray-500'"></div>
          <span class="font-medium text-gray-900 dark:text-white">
            {{ status.is_running ? t('settings.scheduler.running') : t('settings.scheduler.stopped') }}
          </span>
        </div>
        <button
          @click="status.is_running ? stopScheduler() : openConfigModal()"
          class="px-4 py-2 rounded-lg transition-colors"
          :class="status.is_running
            ? 'bg-red-500 dark:bg-red-600 text-white hover:bg-red-600 dark:hover:bg-red-700'
            : 'bg-blue-500 dark:bg-blue-600 text-white hover:bg-blue-600 dark:hover:bg-blue-700'"
        >
          {{ status.is_running ? t('settings.scheduler.stop') : t('settings.scheduler.start') }}
        </button>
      </div>

      <div class="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p class="text-gray-600 dark:text-gray-400">{{ t('settings.scheduler.schedule') }}</p>
          <p class="font-medium text-gray-900 dark:text-white">{{ getCronDescription(status.cron_schedule) }}</p>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ status.cron_schedule }}</p>
        </div>
        <div>
          <p class="text-gray-600 dark:text-gray-400">{{ t('settings.scheduler.nextRunTime') }}</p>
          <p class="font-medium text-gray-900 dark:text-white">{{ formatDateTime(status.next_run_time) }}</p>
        </div>
        <div>
          <p class="text-gray-600 dark:text-gray-400">{{ t('settings.scheduler.lastScan') }}</p>
          <p class="font-medium text-gray-900 dark:text-white">{{ formatDateTime(status.last_scan_time) }}</p>
        </div>
        <div>
          <p class="text-gray-600 dark:text-gray-400">{{ t('settings.scheduler.scanPaths') }}</p>
          <p class="font-medium text-gray-900 dark:text-white">{{ t('settings.scheduler.pathsCount', { count: status.scan_paths.length }) }}</p>
        </div>
      </div>
    </div>

    <!-- Last Scan Result -->
    <div v-if="status?.last_scan_result" class="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg">
      <h3 class="font-semibold text-blue-900 dark:text-blue-400 mb-2">{{ t('settings.scheduler.lastScanResult') }}</h3>
      <div class="grid grid-cols-2 md:grid-cols-5 gap-3 text-sm">
        <div>
          <p class="text-blue-700 dark:text-blue-300">{{ t('settings.scheduler.newProducts') }}</p>
          <p class="text-2xl font-bold text-blue-900 dark:text-blue-400">{{ status.last_scan_result.new_products }}</p>
        </div>
        <div>
          <p class="text-blue-700 dark:text-blue-300">{{ t('settings.scheduler.newVersions') }}</p>
          <p class="text-2xl font-bold text-blue-900 dark:text-blue-400">{{ status.last_scan_result.new_versions }}</p>
        </div>
        <div>
          <p class="text-blue-700 dark:text-blue-300">{{ t('settings.scheduler.updates') }}</p>
          <p class="text-2xl font-bold text-blue-900 dark:text-blue-400">{{ status.last_scan_result.updated_products }}</p>
        </div>
        <div>
          <p class="text-blue-700 dark:text-blue-300">{{ t('settings.scheduler.aiGenerated') }}</p>
          <p class="text-2xl font-bold text-blue-900 dark:text-blue-400">{{ status.last_scan_result.ai_generated || 0 }}</p>
        </div>
        <div>
          <p class="text-blue-700 dark:text-blue-300">{{ t('settings.scheduler.icons') }}</p>
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
      {{ scanning ? t('settings.scheduler.scanning') : t('settings.scheduler.runNow') }}
    </button>

    <!-- Config Modal -->
    <div v-if="showConfigModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="showConfigModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-2xl m-4">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.scheduler.configTitle') }}</h3>

        <div class="space-y-4">
          <!-- Schedule Type -->
          <div>
            <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">{{ t('settings.scheduler.scheduleType') }}</label>
            <select
              v-model="scheduleType"
              @change="onScheduleTypeChange"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="specific">{{ t('settings.scheduler.specificTime') }}</option>
              <option value="interval">{{ t('settings.scheduler.interval') }}</option>
            </select>
          </div>

          <!-- Specific Times Mode -->
          <div v-if="scheduleType === 'specific'" class="space-y-3">
            <label class="block text-sm font-medium text-gray-900 dark:text-white">{{ t('settings.scheduler.executionTime') }}</label>

            <div v-for="(time, index) in specificTimes" :key="index" class="flex items-center gap-2">
              <div class="flex items-center gap-2 flex-1">
                <select
                  v-model="time.hour"
                  class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option v-for="h in 24" :key="h-1" :value="h-1">{{ String(h-1).padStart(2, '0') }}{{ t('settings.scheduler.hour') }}</option>
                </select>
                <span class="text-gray-500 dark:text-gray-400">:</span>
                <select
                  v-model="time.minute"
                  class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="0">{{ t('settings.scheduler.minute00') }}</option>
                  <option value="15">{{ t('settings.scheduler.minute15') }}</option>
                  <option value="30">{{ t('settings.scheduler.minute30') }}</option>
                  <option value="45">{{ t('settings.scheduler.minute45') }}</option>
                </select>
              </div>
              <button
                v-if="specificTimes.length > 1"
                @click="removeSpecificTime(index)"
                class="px-3 py-2 bg-red-500 dark:bg-red-600 text-white rounded-lg hover:bg-red-600 dark:hover:bg-red-700"
              >
                {{ t('settings.scheduler.delete') }}
              </button>
            </div>

            <button
              @click="addSpecificTime"
              class="text-sm text-blue-600 dark:text-blue-400 hover:underline"
            >
              {{ t('settings.scheduler.addTime') }}
            </button>

            <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-3 mt-2">
              <p class="text-sm text-blue-900 dark:text-blue-300">
                <strong>{{ t('settings.scheduler.preview') }}</strong> {{ getSpecificTimesPreview() }}
              </p>
            </div>
          </div>

          <!-- Interval Mode -->
          <div v-if="scheduleType === 'interval'" class="space-y-3">
            <label class="block text-sm font-medium text-gray-900 dark:text-white">{{ t('settings.scheduler.intervalLabel') }}</label>
            <select
              v-model="intervalHours"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option :value="1">{{ t('settings.scheduler.every1Hour') }}</option>
              <option :value="2">{{ t('settings.scheduler.every2Hours') }}</option>
              <option :value="3">{{ t('settings.scheduler.every3Hours') }}</option>
              <option :value="4">{{ t('settings.scheduler.every4Hours') }}</option>
              <option :value="6">{{ t('settings.scheduler.every6Hours') }}</option>
              <option :value="8">{{ t('settings.scheduler.every8Hours') }}</option>
              <option :value="12">{{ t('settings.scheduler.every12Hours') }}</option>
            </select>

            <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-3 mt-2">
              <p class="text-sm text-blue-900 dark:text-blue-300">
                <strong>{{ t('settings.scheduler.preview') }}</strong> {{ getIntervalPreview() }}
              </p>
            </div>
          </div>

          <!-- Scan Paths -->
          <div>
            <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">{{ t('settings.scheduler.scanPathsLabel') }}</label>
            <div class="space-y-2">
              <div v-for="(path, index) in configForm.scan_paths" :key="index" class="flex gap-2">
                <input
                  v-model="configForm.scan_paths[index]"
                  type="text"
                  class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                  :placeholder="t('settings.scheduler.scanPathPlaceholder')"
                />
                <button
                  @click="configForm.scan_paths.splice(index, 1)"
                  class="px-4 py-2 bg-red-500 dark:bg-red-600 text-white rounded-lg hover:bg-red-600 dark:hover:bg-red-700"
                >
                  {{ t('settings.scheduler.remove') }}
                </button>
              </div>
            </div>
            <button
              @click="configForm.scan_paths.push('')"
              class="mt-2 text-sm text-blue-600 dark:text-blue-400 hover:underline"
            >
              {{ t('settings.scheduler.addPath') }}
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
              <span class="text-sm font-medium text-gray-900 dark:text-white">{{ t('settings.scheduler.useAI') }}</span>
            </label>
          </div>
        </div>

        <!-- Modal Actions -->
        <div class="flex justify-end space-x-3 mt-6">
          <button
            @click="showConfigModal = false"
            class="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
          >
            {{ t('settings.scheduler.cancel') }}
          </button>
          <button
            @click="saveAndStartScheduler"
            class="px-4 py-2 bg-blue-500 dark:bg-blue-600 text-white rounded-lg hover:bg-blue-600 dark:hover:bg-blue-700"
          >
            {{ t('settings.scheduler.saveAndStart') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { schedulerApi } from '../api/scheduler'
import { configApi } from '../api/config'
import { useDialog } from '../composables/useDialog'

const { t } = useI18n({ useScope: 'global' })
const { alert } = useDialog()

const status = ref(null)
const showConfigModal = ref(false)
const scanning = ref(false)

const configForm = ref({
  cron_schedule: '0 5,22 * * *',
  scan_paths: ['/mnt/software'],
  use_ai: true
})

// Schedule configuration
const scheduleType = ref('specific') // 'specific' or 'interval'
const specificTimes = ref([
  { hour: 5, minute: 0 },
  { hour: 22, minute: 0 }
])
const intervalHours = ref(6)

const loadStatus = async () => {
  try {
    const response = await schedulerApi.getStatus()
    status.value = response.data
  } catch (error) {
    console.error('Failed to load scheduler status:', error)
  }
}

const openConfigModal = async () => {
  try {
    // 폴더 설정에서 최신 등록된 경로 불러오기
    const foldersConfig = await configApi.getSection('folders')

    if (foldersConfig.data && foldersConfig.data.scanFolders && foldersConfig.data.scanFolders.length > 0) {
      // 현재 스캔 경로가 비어있거나 기본값인 경우, 폴더 설정으로 업데이트
      if (configForm.value.scan_paths.length === 0 ||
          (configForm.value.scan_paths.length === 1 && configForm.value.scan_paths[0] === '/mnt/software')) {
        configForm.value.scan_paths = foldersConfig.data.scanFolders
      }
    }
  } catch (error) {
    console.error('Failed to load folder config:', error)
  }

  showConfigModal.value = true
}

const stopScheduler = async () => {
  try {
    await schedulerApi.stop()
    await loadStatus()
  } catch (error) {
    console.error('Failed to stop scheduler:', error)
  }
}

const onScheduleTypeChange = () => {
  // Update cron expression when schedule type changes
  updateCronExpression()
}

const addSpecificTime = () => {
  specificTimes.value.push({ hour: 5, minute: 0 })
}

const removeSpecificTime = (index) => {
  specificTimes.value.splice(index, 1)
  updateCronExpression()
}

const getSpecificTimesPreview = () => {
  const times = specificTimes.value
    .map(timeObj => {
      const hour = timeObj.hour
      const minute = String(timeObj.minute).padStart(2, '0')
      const period = hour < 12 ? t('settings.scheduler.am') : t('settings.scheduler.pm')
      const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour
      return `${period} ${displayHour}:${minute}`
    })
    .sort((a, b) => {
      const amText = t('settings.scheduler.am')
      const getHour = (str) => {
        const [period, time] = str.split(' ')
        const [h] = time.split(':').map(Number)
        return period === amText ? (h === 12 ? 0 : h) : (h === 12 ? 12 : h + 12)
      }
      return getHour(a) - getHour(b)
    })
    .join(', ')

  return t('settings.scheduler.dailyAtTimes', { times, count: specificTimes.value.length })
}

const getIntervalPreview = () => {
  const hours = intervalHours.value
  const timesPerDay = 24 / hours
  return t('settings.scheduler.everyHourText', { hours, times: timesPerDay })
}

const updateCronExpression = () => {
  if (scheduleType.value === 'specific') {
    // Sort times by hour and minute
    const sortedTimes = [...specificTimes.value].sort((a, b) => {
      if (a.hour !== b.hour) return a.hour - b.hour
      return a.minute - b.minute
    })

    // Group by minute
    const minuteGroups = {}
    sortedTimes.forEach(timeObj => {
      const min = timeObj.minute
      if (!minuteGroups[min]) minuteGroups[min] = []
      minuteGroups[min].push(timeObj.hour)
    })

    // If all times have the same minute, use simplified format
    const minutes = Object.keys(minuteGroups)
    if (minutes.length === 1) {
      const minute = minutes[0]
      const hours = minuteGroups[minute].join(',')
      configForm.value.cron_schedule = `${minute} ${hours} * * *`
    } else {
      // Use first time's minute for now (simplified)
      const minute = sortedTimes[0].minute
      const hours = sortedTimes.map(timeObj => timeObj.hour).join(',')
      configForm.value.cron_schedule = `${minute} ${hours} * * *`
    }
  } else {
    // Interval mode
    configForm.value.cron_schedule = `0 */${intervalHours.value} * * *`
  }
}

const parseCronExpression = (cron) => {
  const parts = cron.split(' ')
  if (parts.length < 5) return

  const [minute, hour] = parts

  // Check if it's interval format (*/N)
  if (hour.startsWith('*/')) {
    scheduleType.value = 'interval'
    intervalHours.value = parseInt(hour.substring(2))
  } else if (hour.includes(',')) {
    // Specific times format
    scheduleType.value = 'specific'
    const hours = hour.split(',').map(hourStr => parseInt(hourStr))
    const min = parseInt(minute)
    specificTimes.value = hours.map(hourNum => ({ hour: hourNum, minute: min }))
  } else {
    // Single time
    scheduleType.value = 'specific'
    specificTimes.value = [{ hour: parseInt(hour), minute: parseInt(minute) }]
  }
}

const saveAndStartScheduler = async () => {
  try {
    updateCronExpression()
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
    await alert.success(`${t('settings.scheduler.scanComplete')}\n${t('settings.scheduler.newProducts')}: ${response.data.result.new_products}개\n${t('settings.scheduler.newVersions')}: ${response.data.result.new_versions}개`)
    await loadStatus()
  } catch (error) {
    console.error('Failed to run manual scan:', error)
    await alert.error(t('settings.scheduler.scanFailed'))
  } finally {
    scanning.value = false
  }
}

const getCronDescription = (cron) => {
  if (!cron) return ''

  const parts = cron.split(' ')
  if (parts.length < 5) return cron

  const [minute, hour, day, month, weekday] = parts

  // Interval format (*/N)
  if (hour.startsWith('*/')) {
    const hours = parseInt(hour.substring(2))
    const timesPerDay = 24 / hours
    return t('settings.scheduler.everyHourText', { hours, times: timesPerDay })
  }

  // Specific times format
  if (hour.includes(',') || (!hour.includes('*') && !hour.includes('/'))) {
    const hours = hour.includes(',') ? hour.split(',').map(h => parseInt(h)) : [parseInt(hour)]
    const min = minute === '0' ? '00' : minute

    const timeStrings = hours.map(h => {
      const period = h < 12 ? t('settings.scheduler.am') : t('settings.scheduler.pm')
      const displayHour = h === 0 ? 12 : h > 12 ? h - 12 : h
      return `${period} ${displayHour}:${min}`
    }).sort((a, b) => {
      const amText = t('settings.scheduler.am')
      const getHour = (str) => {
        const [period, time] = str.split(' ')
        const [h] = time.split(':').map(Number)
        return period === amText ? (h === 12 ? 0 : h) : (h === 12 ? 12 : h + 12)
      }
      return getHour(a) - getHour(b)
    })

    if (timeStrings.length === 1) {
      return t('settings.scheduler.dailyAtTime', { time: timeStrings[0] })
    } else {
      return t('settings.scheduler.dailyAtTimes', { times: timeStrings.join(', '), count: timeStrings.length })
    }
  }

  // Weekly
  if (weekday !== '*') {
    const days = [
      t('settings.scheduler.sunday'),
      t('settings.scheduler.monday'),
      t('settings.scheduler.tuesday'),
      t('settings.scheduler.wednesday'),
      t('settings.scheduler.thursday'),
      t('settings.scheduler.friday'),
      t('settings.scheduler.saturday')
    ]
    return t('settings.scheduler.weeklyAt', { day: days[parseInt(weekday)], time: `${hour}:${minute}` })
  }

  // Monthly
  if (day !== '*') {
    return t('settings.scheduler.monthlyAt', { day, time: `${hour}:${minute}` })
  }

  return cron
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('ko-KR')
}

// Watch for changes in time settings
watch(specificTimes, () => {
  if (scheduleType.value === 'specific') {
    updateCronExpression()
  }
}, { deep: true })

watch(intervalHours, () => {
  if (scheduleType.value === 'interval') {
    updateCronExpression()
  }
})

onMounted(async () => {
  await loadStatus()

  try {
    // 폴더 설정에서 등록된 경로 불러오기
    const foldersConfig = await configApi.getSection('folders')
    let defaultScanPaths = ['/library'] // 기본값

    if (foldersConfig.data && foldersConfig.data.scanFolders && foldersConfig.data.scanFolders.length > 0) {
      // 폴더 설정에 등록된 경로들을 기본값으로 사용
      defaultScanPaths = foldersConfig.data.scanFolders
    }

    // 스케줄러 설정 불러오기
    const schedulerConfig = await schedulerApi.getConfig()
    if (schedulerConfig.data.scan_paths && schedulerConfig.data.scan_paths.length > 0) {
      // 기존에 저장된 스케줄러 설정이 있으면 사용
      configForm.value = schedulerConfig.data
    } else {
      // 없으면 폴더 설정의 경로를 기본값으로 사용
      configForm.value.scan_paths = defaultScanPaths
    }

    // Parse cron expression to update UI
    parseCronExpression(configForm.value.cron_schedule)
  } catch (error) {
    console.error('Failed to load config:', error)
  }
})
</script>
