<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 sm:px-6 lg:px-8 py-3 sm:py-4">
      <div class="flex items-center justify-between gap-2">
        <button
          @click="$router.back()"
          class="flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors text-sm sm:text-base"
        >
          <svg class="w-4 h-4 sm:w-5 sm:h-5 mr-1 sm:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          <span class="hidden sm:inline">{{ t('detectedList.backButton') }}</span>
        </button>

        <div class="flex items-center gap-1 sm:gap-2 flex-wrap">
          <button
            v-if="violations.length > 0"
            @click="toggleAll"
            class="px-2 sm:px-3 lg:px-4 py-1.5 sm:py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors flex items-center text-xs sm:text-sm"
          >
            <svg class="w-4 h-4 sm:mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
            <span class="hidden sm:inline">{{ isAllSelected ? t('detectedList.deselectAll') : t('detectedList.selectAll') }}</span>
          </button>

          <button
            v-if="selectedIds.length > 0"
            @click="batchRenameSelected"
            class="px-2 sm:px-3 lg:px-4 py-1.5 sm:py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors flex items-center text-xs sm:text-sm"
          >
            <svg class="w-4 h-4 sm:mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span class="hidden sm:inline">{{ t('detectedList.batchRename') }}</span>
            <span>({{ selectedIds.length }})</span>
          </button>

          <button
            v-if="selectedIds.length > 0"
            @click="batchDeleteSelected"
            class="px-2 sm:px-3 lg:px-4 py-1.5 sm:py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors flex items-center text-xs sm:text-sm"
          >
            <svg class="w-4 h-4 sm:mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            <span class="hidden sm:inline">{{ t('detectedList.batchDelete') }}</span>
            <span>({{ selectedIds.length }})</span>
          </button>

          <button
            @click="loadViolations"
            class="px-2 sm:px-3 lg:px-4 py-1.5 sm:py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center text-xs sm:text-sm"
          >
            <svg class="w-4 h-4 sm:mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span class="hidden sm:inline">{{ t('detectedList.refresh') }}</span>
          </button>

          <button
            @click="openScanModal"
            :disabled="isScanning"
            class="px-2 sm:px-3 lg:px-4 py-1.5 sm:py-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white rounded-lg transition-all flex items-center text-xs sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="isScanning" class="animate-spin w-4 h-4 sm:mr-1.5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-4 h-4 sm:mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span class="hidden sm:inline">{{ isScanning ? t('detectedList.scanning') : t('detectedList.scan') }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900 pb-20 lg:pb-8">
      <!-- Title Section -->
      <div class="px-4 sm:px-6 lg:px-8 pt-4 sm:pt-6 lg:pt-8 pb-4 sm:pb-6">
        <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white mb-2">{{ t('detectedList.pageTitle') }}</h1>
        <p class="text-sm sm:text-base text-gray-600 dark:text-gray-400">{{ t('detectedList.pageDescription') }}</p>
      </div>

      <!-- Stats -->
      <div class="px-4 sm:px-6 lg:px-8 pb-4 sm:pb-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 sm:gap-4 lg:gap-6">
          <!-- 전체 항목 -->
          <div class="bg-white dark:bg-gray-800 rounded-xl sm:rounded-2xl shadow-sm p-4 sm:p-5 lg:p-6 border border-gray-100 dark:border-gray-700 hover:shadow-lg transition-shadow">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">{{ t('detectedList.totalItems') }}</p>
              <p class="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {{ stats.total }}
              </p>
            </div>
            <div class="p-2 sm:p-3 lg:p-4 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900 dark:to-purple-900 rounded-xl sm:rounded-2xl">
              <svg class="w-6 h-6 sm:w-7 sm:h-7 lg:w-8 lg:h-8 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
          </div>
          </div>

          <!-- 스캔된 항목 -->
          <div class="bg-white dark:bg-gray-800 rounded-xl sm:rounded-2xl shadow-sm p-4 sm:p-5 lg:p-6 border border-gray-100 dark:border-gray-700 hover:shadow-lg transition-shadow">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">{{ t('detectedList.scannedItems') }}</p>
              <p class="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                {{ stats.scanned }}
              </p>
            </div>
            <div class="p-2 sm:p-3 lg:p-4 bg-gradient-to-br from-green-100 to-emerald-100 dark:from-green-900 dark:to-emerald-900 rounded-xl sm:rounded-2xl">
              <svg class="w-6 h-6 sm:w-7 sm:h-7 lg:w-8 lg:h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          </div>

          <!-- 불일치 항목 -->
          <div class="bg-white dark:bg-gray-800 rounded-xl sm:rounded-2xl shadow-sm p-4 sm:p-5 lg:p-6 border border-gray-100 dark:border-gray-700 hover:shadow-lg transition-shadow">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">{{ t('detectedList.mismatchedItems') }}</p>
              <p class="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent">
                {{ stats.mismatched }}
              </p>
            </div>
            <div class="p-2 sm:p-3 lg:p-4 bg-gradient-to-br from-red-100 to-orange-100 dark:from-red-900 dark:to-orange-900 rounded-xl sm:rounded-2xl">
              <svg class="w-6 h-6 sm:w-7 sm:h-7 lg:w-8 lg:h-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          </div>
          </div>
        </div>
      </div>

      <!-- Violations List -->
      <div class="px-4 sm:px-6 lg:px-8 pb-4 sm:pb-8">
        <div v-if="loading" class="flex justify-center items-center h-64">
          <div class="text-gray-500 dark:text-gray-400">{{ t('detectedList.loading') }}</div>
        </div>

        <div v-else-if="violations.length === 0" class="bg-white dark:bg-gray-800 rounded-xl sm:rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-8 sm:p-12 lg:p-16">
          <div class="flex flex-col items-center justify-center">
            <div class="p-6 bg-gradient-to-br from-green-100 to-emerald-100 dark:from-green-900 dark:to-emerald-900 rounded-3xl mb-6">
              <svg class="w-16 h-16 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p class="text-gray-900 dark:text-white text-xl font-bold mb-2">{{ t('detectedList.noFiles') }}</p>
            <p class="text-gray-500 dark:text-gray-400 text-sm">{{ t('detectedList.noFilesDesc') }}</p>
          </div>
        </div>

        <div v-else class="space-y-3 sm:space-y-4">
          <div
            v-for="violation in violations"
            :key="violation.id"
            class="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-xl sm:rounded-2xl shadow-sm p-3 sm:p-4 lg:p-6 hover:shadow-lg transition-all"
            :class="{ 'ring-2 ring-blue-500': isSelected(violation.id) }"
          >
            <div class="flex items-start justify-between gap-2 sm:gap-4">
              <!-- Checkbox -->
              <div class="flex items-start gap-2 sm:gap-3 lg:gap-4 flex-1">
                <input
                  type="checkbox"
                  :checked="isSelected(violation.id)"
                  @change="toggleSelection(violation.id)"
                  class="mt-1 w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 cursor-pointer"
                />
                <div class="flex-1 min-w-0">
                <!-- 파일명 (일반 모드) -->
                <div v-if="editingId !== violation.id" class="flex items-center gap-1.5 sm:gap-2 flex-wrap">
                  <!-- 매칭 여부에 따른 아이콘 -->
                  <svg v-if="violation.product_id" class="w-4 h-4 sm:w-5 sm:h-5 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <svg v-else class="w-4 h-4 sm:w-5 sm:h-5 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <h3 class="text-sm sm:text-base lg:text-lg font-semibold text-gray-900 dark:text-white break-all">{{ violation.file_name }}</h3>

                  <!-- 매칭 상태 뱃지 -->
                  <span v-if="violation.product_id" class="px-1.5 sm:px-2 py-0.5 sm:py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-[10px] sm:text-xs rounded-full flex-shrink-0">
                    {{ t('detectedList.registered') }}
                  </span>
                  <span v-else class="px-1.5 sm:px-2 py-0.5 sm:py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-[10px] sm:text-xs rounded-full flex-shrink-0">
                    {{ getViolationTypeLabel(violation.violation_type) }}
                  </span>
                </div>

                <!-- 파일명 (편집 모드) -->
                <div v-else class="space-y-2">
                  <div class="flex items-center gap-2">
                    <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    <h3 class="text-lg font-semibold text-blue-600 dark:text-blue-400">{{ t('detectedList.editingTitle') }}</h3>
                  </div>
                  <input
                    v-model="editingFilename"
                    type="text"
                    class="w-full px-4 py-2 border border-blue-300 dark:border-blue-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    :placeholder="t('detectedList.filenamePlaceholder')"
                    @keyup.enter="saveEdit(violation.id)"
                    @keyup.esc="cancelEdit"
                  />
                  <div class="flex gap-2">
                    <button
                      @click="saveEdit(violation.id)"
                      class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
                    >
                      {{ t('detectedList.save') }}
                    </button>
                    <button
                      @click="cancelEdit"
                      class="px-4 py-2 bg-gray-300 hover:bg-gray-400 dark:bg-gray-600 dark:hover:bg-gray-500 text-gray-900 dark:text-white rounded-lg text-sm font-medium transition-colors"
                    >
                      {{ t('detectedList.cancel') }}
                    </button>
                  </div>
                </div>

                <!-- 경로 -->
                <div v-if="editingId !== violation.id" class="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  📁 {{ violation.folder_path }}
                </div>

                <!-- 위반 내용 -->
                <div v-if="editingId !== violation.id" class="mt-3 text-sm text-gray-700 dark:text-gray-300">
                  <span class="font-medium">{{ t('detectedList.problem') }}</span> {{ violation.violation_details }}
                </div>

                <!-- 제안 -->
                <div v-if="editingId !== violation.id && violation.suggestion" class="mt-2 p-3 rounded-lg" :class="violation.file_name === violation.suggestion ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800' : 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'">
                  <span class="text-sm font-medium" :class="violation.file_name === violation.suggestion ? 'text-green-700 dark:text-green-400' : 'text-blue-700 dark:text-blue-400'">
                    {{ violation.file_name === violation.suggestion ? '✓ 일치' : t('detectedList.suggestion') }}
                  </span>
                  <span v-if="violation.file_name !== violation.suggestion" class="text-sm text-blue-600 dark:text-blue-300 ml-2">{{ violation.suggestion }}</span>
                </div>

                <!-- 날짜 -->
                <div v-if="editingId !== violation.id" class="mt-3 text-xs text-gray-500 dark:text-gray-500">
                  {{ t('detectedList.discoveredAt') }} {{ formatDate(violation.created_at) }}
                </div>
                </div>
              </div>

              <!-- Actions -->
              <div v-if="editingId !== violation.id" class="flex items-center gap-1 sm:gap-2 ml-1 sm:ml-2 flex-shrink-0">
                <!-- 스토어 보기 버튼 (이미 매칭된 경우) -->
                <button
                  v-if="violation.product_id"
                  @click="goToProduct(violation.product_id)"
                  :title="t('detectedList.viewInStore')"
                  class="p-1.5 sm:p-2 lg:p-3 text-white bg-gradient-to-r from-green-500 to-emerald-600 hover:shadow-lg rounded-lg sm:rounded-xl transition-all"
                >
                  <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>

                            <!-- AI 매칭 버튼 (아직 매칭되지 않은 경우) -->
                <button
                  v-else
                  @click="openAIMatchingDialog(violation)"
                  :title="t('detectedList.aiMatching')"
                  class="p-1.5 sm:p-2 lg:p-3 text-white bg-gradient-to-r from-blue-500 to-purple-600 hover:shadow-lg rounded-lg sm:rounded-xl transition-all"
                >
                  <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </button>

                <button
                  v-if="violation.suggestion && violation.file_name !== violation.suggestion"
                  @click="renameSingle(violation)"
                  :title="t('detectedList.applySuggestion')"
                  class="p-1.5 sm:p-2 lg:p-3 text-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/20 rounded-lg sm:rounded-xl transition-all hover:shadow-md"
                >
                  <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12" />
                  </svg>
                </button>
                <button
                  @click="startEdit(violation)"
                  :title="t('detectedList.editFilename')"
                  class="p-1.5 sm:p-2 lg:p-3 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg sm:rounded-xl transition-all hover:shadow-md"
                >
                  <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button
                  @click="addToExclusions(violation)"
                  :title="t('detectedList.addToExclusions')"
                  class="p-1.5 sm:p-2 lg:p-3 text-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/20 rounded-lg sm:rounded-xl transition-all hover:shadow-md"
                >
                  <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                  </svg>
                </button>
                <button
                  @click="resolveViolation(violation.id)"
                  :title="t('detectedList.markResolved')"
                  class="p-1.5 sm:p-2 lg:p-3 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg sm:rounded-xl transition-all hover:shadow-md"
                >
                  <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </button>
                <button
                  @click="deleteViolation(violation.id)"
                  :title="t('detectedList.deleteItem')"
                  class="p-1.5 sm:p-2 lg:p-3 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg sm:rounded-xl transition-all hover:shadow-md"
                >
                  <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- AI Matching Dialog -->
    <ViolationAISearchDialog
      :is-open="aiMatchingDialogOpen"
      :violation="selectedViolation"
      @close="closeAIMatchingDialog"
      @saved="handleAIMatchingSaved"
    />

    <!-- Scan Modal -->
    <div v-if="showScanModal" class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50 p-4" @click.self="closeScanModal">
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden">
        <div class="bg-gradient-to-r from-green-500 to-emerald-600 px-6 py-4">
          <h3 class="text-lg font-bold text-white flex items-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            {{ t('detectedList.scanTitle') }}
          </h3>
        </div>

        <div class="p-6">
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">{{ t('detectedList.scanDescription') }}</p>

          <!-- Scan Options -->
          <div class="space-y-3 mb-6">
            <label class="flex items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-xl cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
              <input
                type="radio"
                v-model="scanMode"
                value="all"
                class="w-4 h-4 text-green-600 border-gray-300 focus:ring-green-500"
              />
              <div class="ml-3">
                <span class="font-medium text-gray-900 dark:text-white">{{ t('detectedList.scanAllFolders') }}</span>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{{ t('detectedList.scanAllFoldersDesc') }}</p>
              </div>
            </label>

            <label class="flex items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-xl cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
              <input
                type="radio"
                v-model="scanMode"
                value="select"
                class="w-4 h-4 text-green-600 border-gray-300 focus:ring-green-500"
              />
              <div class="ml-3">
                <span class="font-medium text-gray-900 dark:text-white">{{ t('detectedList.scanSelectFolders') }}</span>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{{ t('detectedList.scanSelectFoldersDesc') }}</p>
              </div>
            </label>
          </div>

          <!-- Folder Selection (when select mode) -->
          <div v-if="scanMode === 'select'" class="mb-6">
            <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('detectedList.selectFoldersToScan') }}</p>
            <div v-if="scanFolders.length === 0" class="text-center py-4 text-gray-500 dark:text-gray-400 text-sm">
              {{ t('detectedList.noFoldersConfigured') }}
            </div>
            <div v-else class="space-y-2 max-h-48 overflow-y-auto">
              <label
                v-for="folder in scanFolders"
                :key="folder"
                class="flex items-center p-2 bg-gray-50 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
              >
                <input
                  type="checkbox"
                  v-model="selectedScanFolders"
                  :value="folder"
                  class="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                />
                <span class="ml-3 text-sm text-gray-900 dark:text-white font-mono truncate">{{ folder }}</span>
              </label>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex space-x-3">
            <button
              @click="closeScanModal"
              class="flex-1 px-4 py-2.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium"
            >
              {{ t('common.cancel') }}
            </button>
            <button
              @click="startScan"
              :disabled="isScanning || (scanMode === 'select' && selectedScanFolders.length === 0)"
              class="flex-1 px-4 py-2.5 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl hover:from-green-600 hover:to-emerald-700 transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              <svg v-if="isScanning" class="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isScanning ? t('detectedList.scanning') : t('detectedList.startScan') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { filenameViolationsApi } from '../api/filenameViolations'
import { productsApi } from '../api/products'
import { scanApi } from '../api/scan'
import { configApi } from '../api/config'
import ViolationAISearchDialog from '../components/violation/ViolationAISearchDialog.vue'
import { useDialog } from '../composables/useDialog'

const router = useRouter()
const { t } = useI18n({ useScope: 'global' })
const { alert, confirm } = useDialog()

const loading = ref(true)
const violations = ref([])
const stats = ref({
  total: 0,
  scanned: 0,
  mismatched: 0,
  by_type: {}
})
const editingId = ref(null)
const editingFilename = ref('')
const selectedIds = ref([])
const isAllSelected = ref(false)
const aiMatchingDialogOpen = ref(false)
const selectedViolation = ref(null)

// Scan Modal
const showScanModal = ref(false)
const isScanning = ref(false)
const scanMode = ref('all')
const scanFolders = ref([])
const selectedScanFolders = ref([])
const useAI = ref(false)

const getViolationTypeLabel = (type) => {
  if (!type) return ''
  const key = `detectedList.violationTypes.${type.toLowerCase()}`
  const translated = t(key)
  // vue-i18n returns the key itself if translation not found
  return translated !== key ? translated : type
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('ko-KR')
}

const loadViolations = async () => {
  loading.value = true
  try {
    const [violationsRes, statsRes] = await Promise.all([
      filenameViolationsApi.getViolations(false), // 미해결 항목만
      filenameViolationsApi.getStats()
    ])
    violations.value = violationsRes.data
    stats.value = statsRes.data
    selectedIds.value = []
    isAllSelected.value = false
  } catch (error) {
    console.error('Failed to load violations:', error)
    await alert.error(t('detectedList.loadFailed'))
  } finally {
    loading.value = false
  }
}

const toggleAll = () => {
  if (isAllSelected.value) {
    selectedIds.value = []
    isAllSelected.value = false
  } else {
    selectedIds.value = violations.value.map(v => v.id)
    isAllSelected.value = true
  }
}

const toggleSelection = (id) => {
  const index = selectedIds.value.indexOf(id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(id)
  }
  isAllSelected.value = selectedIds.value.length === violations.value.length
}

const isSelected = (id) => {
  return selectedIds.value.includes(id)
}

const resolveViolation = async (id) => {
  try {
    await filenameViolationsApi.resolveViolation(id)
    await loadViolations()
    await alert.success(t('detectedList.resolveSuccess'))
  } catch (error) {
    console.error('Failed to resolve violation:', error)
    await alert.error(t('detectedList.resolveFailed'))
  }
}

const deleteViolation = async (id) => {
  const shouldDelete = await confirm.danger(t('detectedList.deleteConfirm'))
  if (!shouldDelete) {
    return
  }

  try {
    await filenameViolationsApi.deleteViolation(id)
    await loadViolations()
    await alert.success(t('detectedList.deleteSuccess'))
  } catch (error) {
    console.error('Failed to delete violation:', error)
    await alert.error(t('detectedList.deleteFailed'))
  }
}

const addToExclusions = async (violation) => {
  const fileName = violation.file_name
  const fileExt = fileName.includes('.') ? fileName.substring(fileName.lastIndexOf('.')) : ''

  let selectedPattern = fileName

  // 확장자가 있으면 패턴 선택 옵션 제공
  if (fileExt) {
    const useExtension = await confirm.info(
      t('detectedList.selectExclusionPattern', { fileName, extension: `*${fileExt}` })
    )

    if (useExtension === null) {
      // 취소됨
      return
    }

    selectedPattern = useExtension ? `*${fileExt}` : fileName
  }

  try {
    // 스캔 예외에 추가
    await scanApi.addScanExclusion(selectedPattern, 'pattern')

    // 서버에서 violation 삭제
    await filenameViolationsApi.deleteViolation(violation.id)

    // 목록에서 해당 항목 제거
    violations.value = violations.value.filter(v => v.id !== violation.id)

    // 통계 업데이트
    if (stats.value) {
      stats.value.scanned = Math.max(0, stats.value.scanned - 1)
      stats.value.total = Math.max(0, stats.value.total - 1)
    }

    // 성공 메시지
    await alert.success(t('detectedList.addedToExclusions', { pattern: selectedPattern }))
  } catch (error) {
    console.error('Failed to add to exclusions:', error)
    await alert.error(t('detectedList.addToExclusionsFailed'))
  }
}

const startEdit = (violation) => {
  editingId.value = violation.id
  editingFilename.value = violation.suggestion || violation.file_name
}

const cancelEdit = () => {
  editingId.value = null
  editingFilename.value = ''
}

const saveEdit = async (id) => {
  if (!editingFilename.value.trim()) {
    await alert.warning(t('detectedList.enterFilename'))
    return
  }

  try {
    await filenameViolationsApi.renameFile(id, editingFilename.value.trim())

    await loadViolations()
    editingId.value = null
    editingFilename.value = ''
    await alert.success(t('detectedList.renameSuccess'))
  } catch (error) {
    console.error('Failed to rename file:', error)
    const errorMsg = error.response?.data?.detail || t('detectedList.renameFailed')
    await alert.error(errorMsg)
  }
}

const renameSingle = async (violation) => {
  if (!violation.suggestion) {
    await alert.warning(t('detectedList.noSuggestion'))
    return
  }

  const shouldRename = await confirm.warning(t('detectedList.renameConfirm', { filename: violation.suggestion }))
  if (!shouldRename) {
    return
  }

  try {
    await filenameViolationsApi.renameFile(violation.id, violation.suggestion)

    await loadViolations()
    await alert.success(t('detectedList.renameSuccess'))
  } catch (error) {
    console.error('Failed to rename file:', error)
    const errorMsg = error.response?.data?.detail || t('detectedList.renameFailed')
    await alert.error(errorMsg)
  }
}

const batchRenameSelected = async () => {
  if (selectedIds.value.length === 0) {
    await alert.warning(t('detectedList.selectItems'))
    return
  }

  const shouldRename = await confirm.warning(t('detectedList.batchRenameConfirm', { count: selectedIds.value.length }))
  if (!shouldRename) {
    return
  }

  try {
    const response = await filenameViolationsApi.batchRename(selectedIds.value)

    await loadViolations()

    const result = response.data
    let message = result.message + '\n'

    if (result.results.failed.length > 0) {
      message += t('detectedList.batchRenamePartialSuccess')
      result.results.failed.forEach(item => {
        message += `- ${item.filename}: ${item.error}\n`
      })
    }

    message += '\n\n' + t('detectedList.renameSuccess').split('\n')[1]
    await alert.info(message)
  } catch (error) {
    console.error('Failed to batch rename:', error)
    await alert.error(t('detectedList.batchRenameFailed'))
  }
}

const batchDeleteSelected = async () => {
  if (selectedIds.value.length === 0) {
    await alert.warning(t('detectedList.selectItems'))
    return
  }

  const shouldDelete = await confirm.danger(
    t('detectedList.batchDeleteConfirm', { count: selectedIds.value.length })
  )
  if (!shouldDelete) {
    return
  }

  try {
    const response = await filenameViolationsApi.batchDelete(selectedIds.value)
    await loadViolations()

    const result = response.data
    if (result.failed_count > 0 && result.errors) {
      let message = result.message + '\n\n'
      message += t('detectedList.errors') + ':\n'
      result.errors.forEach(error => {
        message += `- ${error}\n`
      })
      await alert.warning(message)
    } else {
      await alert.success(result.message)
    }
  } catch (error) {
    console.error('Failed to batch delete:', error)
    await alert.error(t('detectedList.batchDeleteFailed'))
  }
}

const openAIMatchingDialog = async (violation) => {
  try {
    // 1. 폴더명과 파일명에서 제품명 추출
    const folderName = violation.folder_path.split('/').filter(Boolean).pop() || ''
    const fileNameWithoutExt = violation.file_name.replace(/\.(exe|msi|zip|rar|7z|iso|dmg|pkg|deb|rpm|tar\.gz|tar\.bz2)$/i, '')

    // 검색할 이름들 (폴더명 우선, 파일명 차선)
    const searchNames = [folderName, fileNameWithoutExt].filter(Boolean)

    // 2. 각 이름으로 기존 제품 검색
    let matchedProduct = null

    for (const searchName of searchNames) {
      if (!searchName || searchName.length < 2) continue

      const searchResponse = await productsApi.getProducts({ search: searchName, limit: 20 })
      const products = searchResponse.data.items || searchResponse.data

      if (!products || products.length === 0) continue

      // 정확히 일치하는 제품 찾기 (대소문자 구분 없이)
      matchedProduct = products.find(p =>
        p.title.toLowerCase() === searchName.toLowerCase()
      )

      // 정확한 매칭이 없으면 포함 관계 확인 (제품명이 검색어를 포함하거나 검색어가 제품명을 포함)
      if (!matchedProduct) {
        matchedProduct = products.find(p => {
          const pTitle = p.title.toLowerCase()
          const sName = searchName.toLowerCase()
          return pTitle.includes(sName) || sName.includes(pTitle)
        })
      }

      if (matchedProduct) break
    }

    if (matchedProduct) {
      // 제품이 이미 있으면 바로 버전으로 추가
      await filenameViolationsApi.addToProduct(violation.id, matchedProduct.id)

      // 목록에서 제거
      violations.value = violations.value.filter(v => v.id !== violation.id)

      // 통계 업데이트
      if (stats.value) {
        stats.value.scanned = Math.max(0, stats.value.scanned - 1)
        stats.value.total = Math.max(0, stats.value.total - 1)
      }

      await alert.success(t('detectedList.versionAddedToProduct', { title: matchedProduct.title }))
      return
    } else {
      // 제품이 없으면 AI 매칭 다이얼로그 열기
      selectedViolation.value = violation
      aiMatchingDialogOpen.value = true
    }
  } catch (error) {
    console.error('Failed to check existing product:', error)
    // 오류 발생시 기존 동작 (다이얼로그 열기)
    selectedViolation.value = violation
    aiMatchingDialogOpen.value = true
  }
}

const closeAIMatchingDialog = () => {
  aiMatchingDialogOpen.value = false
  selectedViolation.value = null
}

const handleAIMatchingSaved = async (data) => {
  // 목록에서 해당 항목 제거
  if (selectedViolation.value?.id) {
    violations.value = violations.value.filter(v => v.id !== selectedViolation.value.id)

    // 통계 업데이트
    if (stats.value) {
      stats.value.scanned = Math.max(0, stats.value.scanned - 1)
      stats.value.total = Math.max(0, stats.value.total - 1)
    }
  }

  // 성공 메시지 표시
  const productTitle = data.product?.title || '제품'
  await alert.success(`${t('detectedList.productCreateSuccess')}\n\n제품명: ${productTitle}`)

  // 목록이 비었으면 다시 로드
  if (violations.value.length === 0) {
    await loadViolations()
  }
}

const goToProduct = (productId) => {
  // 제품 상세 페이지로 이동
  router.push(`/product/${productId}`)
}

// Scan Modal Functions
const openScanModal = async () => {
  // Load configured folders and AI settings
  try {
    const response = await configApi.getConfig()
    const config = response.data
    if (config.folders && config.folders.scanFolders) {
      scanFolders.value = config.folders.scanFolders
    } else {
      scanFolders.value = []
    }
    // Load AI setting (same as Settings page)
    if (config.metadata && config.metadata.scanMethod) {
      useAI.value = config.metadata.scanMethod === 'ai'
    }
  } catch (error) {
    console.error('Failed to load scan folders:', error)
    scanFolders.value = []
  }

  scanMode.value = 'all'
  selectedScanFolders.value = []
  showScanModal.value = true
}

const closeScanModal = () => {
  showScanModal.value = false
}

const startScan = async () => {
  isScanning.value = true
  closeScanModal()

  try {
    let foldersToScan = []

    if (scanMode.value === 'all') {
      foldersToScan = scanFolders.value.length > 0 ? scanFolders.value : ['/library']
    } else {
      foldersToScan = selectedScanFolders.value
    }

    // Scan each folder (uses same AI setting as Settings page)
    let totalNewProducts = 0
    let totalNewVersions = 0
    let errorMessages = []

    for (const folder of foldersToScan) {
      try {
        const result = await scanApi.startScan(folder, useAI.value)
        if (result.data) {
          totalNewProducts += result.data.new_products || 0
          totalNewVersions += result.data.new_versions || 0
        }
      } catch (error) {
        console.error(`Failed to scan folder ${folder}:`, error)
        const errorDetail = error.response?.data?.detail || error.message
        errorMessages.push(`${folder}: ${errorDetail}`)
      }
    }

    if (errorMessages.length > 0) {
      await alert.warning(t('detectedList.scanComplete') + '\n\n' + errorMessages.join('\n'))
    } else {
      await alert.success(t('detectedList.scanComplete'))
    }

    // Reload violations list
    await loadViolations()
  } catch (error) {
    console.error('Scan failed:', error)
    await alert.error(t('detectedList.scanFailed'))
  } finally {
    isScanning.value = false
  }
}

onMounted(() => {
  loadViolations()
})
</script>
