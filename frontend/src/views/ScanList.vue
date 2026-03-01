<template>
  <div class="h-full flex flex-col" @click="onOutsideClick">
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
          <!-- Select All -->
          <button
            v-if="filteredItems.length > 0"
            @click.stop="toggleAll"
            class="px-2 sm:px-3 py-1.5 sm:py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors flex items-center text-xs sm:text-sm"
          >
            <svg class="w-4 h-4 sm:mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
            <span class="hidden sm:inline">{{ isAllSelected ? t('detectedList.deselectAll') : t('detectedList.selectAll') }}</span>
          </button>

          <!-- Batch Delete -->
          <button
            v-if="selectedIds.length > 0"
            @click.stop="batchDeleteSelected"
            class="px-2 sm:px-3 py-1.5 sm:py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors flex items-center text-xs sm:text-sm"
          >
            <svg class="w-4 h-4 sm:mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            <span class="hidden sm:inline">{{ t('detectedList.batchDelete') }}</span>
            <span>({{ selectedIds.length }})</span>
          </button>

          <!-- Refresh -->
          <button
            @click.stop="loadItems"
            class="px-2 sm:px-3 py-1.5 sm:py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center text-xs sm:text-sm"
          >
            <svg class="w-4 h-4 sm:mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span class="hidden sm:inline">{{ t('detectedList.refresh') }}</span>
          </button>

          <!-- Scan -->
          <button
            @click.stop="openScanModal"
            :disabled="isScanning"
            class="px-2 sm:px-3 py-1.5 sm:py-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white rounded-lg transition-all flex items-center text-xs sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
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
      <!-- Title -->
      <div class="px-4 sm:px-6 lg:px-8 pt-4 sm:pt-6 pb-3">
        <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white mb-1">{{ t('scanList.pageTitle') }}</h1>
        <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('scanList.pageDescription') }}</p>
      </div>

      <!-- Stats Cards -->
      <div class="px-4 sm:px-6 lg:px-8 pb-3">
        <div class="grid grid-cols-3 sm:grid-cols-6 gap-2">
          <div
            v-for="cls in classifications"
            :key="cls.key"
            class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-2.5 sm:p-3 border border-gray-100 dark:border-gray-700 text-center cursor-pointer hover:shadow-md transition-shadow"
            @click.stop="activeFilter = cls.key"
            :class="{ 'ring-2': activeFilter === cls.key, [`ring-${cls.ringColor}`]: activeFilter === cls.key }"
          >
            <div class="text-xl sm:text-2xl mb-0.5">{{ cls.icon }}</div>
            <div class="text-base sm:text-lg font-bold" :class="cls.textColor">{{ stats.by_classification?.[cls.key] || 0 }}</div>
            <div class="text-[9px] sm:text-[11px] text-gray-500 dark:text-gray-400 leading-tight">{{ cls.label }}</div>
          </div>
        </div>
      </div>

      <!-- Classification Filter Tabs -->
      <div class="px-4 sm:px-6 lg:px-8 pb-3">
        <div class="flex gap-1.5 overflow-x-auto pb-1 scrollbar-hide">
          <button
            @click.stop="activeFilter = 'all'"
            class="px-3 py-1.5 rounded-full text-xs sm:text-sm font-medium whitespace-nowrap transition-all flex-shrink-0"
            :class="activeFilter === 'all'
              ? 'bg-gray-800 dark:bg-gray-200 text-white dark:text-gray-900 shadow-sm'
              : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-750'"
          >
            📋 {{ t('scanList.filter.all') }} ({{ stats.total || 0 }})
          </button>
          <button
            v-for="cls in classifications"
            :key="cls.key"
            @click.stop="activeFilter = cls.key"
            class="px-3 py-1.5 rounded-full text-xs sm:text-sm font-medium whitespace-nowrap transition-all flex-shrink-0"
            :class="activeFilter === cls.key
              ? `${cls.activeBgClass} shadow-sm`
              : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-750'"
          >
            {{ cls.icon }} {{ cls.label }} ({{ stats.by_classification?.[cls.key] || 0 }})
          </button>
        </div>
      </div>

      <!-- List -->
      <div class="px-4 sm:px-6 lg:px-8 pb-4 sm:pb-8">
        <div v-if="loading" class="flex justify-center items-center h-64">
          <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
        </div>

        <div v-else-if="filteredItems.length === 0" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-8 sm:p-12">
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

        <div v-else class="space-y-2 sm:space-y-2.5">
          <div
            v-for="item in filteredItems"
            :key="item.id"
            class="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-xl shadow-sm p-3 sm:p-4 hover:shadow-md transition-all"
            :class="{ 'ring-2 ring-blue-500': isSelected(item.id) }"
          >
            <div class="flex items-start gap-2 sm:gap-3">
              <!-- Checkbox -->
              <input
                type="checkbox"
                :checked="isSelected(item.id)"
                @change="toggleSelection(item.id)"
                class="mt-1.5 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 cursor-pointer flex-shrink-0"
              />

              <!-- Classification Badge with Dropdown -->
              <div class="relative flex-shrink-0 mt-0.5">
                <button
                  @click.stop="toggleClassifyMenu(item.id)"
                  class="px-2 py-1 rounded-full text-[10px] sm:text-xs font-bold flex items-center gap-1 cursor-pointer hover:opacity-80 transition-opacity"
                  :class="getClassBg(item.classification)"
                  :title="t('scanList.changeClassification')"
                >
                  <span>{{ getClassIcon(item.classification) }}</span>
                  <span class="hidden sm:inline">{{ getClassLabel(item.classification) }}</span>
                  <svg class="w-2.5 h-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                <!-- Classification Dropdown Menu -->
                <div
                  v-if="classifyMenuId === item.id"
                  class="absolute left-0 top-full mt-1 z-30 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 py-1 min-w-[140px]"
                  @click.stop
                >
                  <button
                    v-for="cls in classifications"
                    :key="cls.key"
                    @click="changeClassification(item.id, cls.key)"
                    class="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-2 transition-colors"
                  >
                    <span>{{ cls.icon }}</span>
                    <span :class="cls.textColor" class="font-medium">{{ cls.label }}</span>
                    <svg v-if="item.classification === cls.key" class="w-3.5 h-3.5 ml-auto text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>

              <!-- File Info -->
              <div class="flex-1 min-w-0">
                <!-- View mode -->
                <div v-if="editingId !== item.id">
                  <h3 class="text-sm sm:text-base font-semibold text-gray-900 dark:text-white break-all leading-tight">{{ item.file_name }}</h3>
                  <p class="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">📁 {{ item.folder_path }}</p>
                  <p class="text-[10px] text-gray-400 dark:text-gray-500 mt-0.5">{{ formatDate(item.created_at) }}</p>

                  <!-- Mobile actions -->
                  <div class="flex items-center gap-1 mt-2 sm:hidden">
                    <!-- AI Search (product only) -->
                    <button
                      v-if="item.classification === 'product'"
                      @click.stop="openAIMatchingDialog(item)"
                      class="p-1.5 text-white bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg"
                      :title="t('detectedList.aiMatching')"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </button>
                    <!-- Register (non-product) -->
                    <button
                      v-else
                      @click.stop="openRegisterDialog(item)"
                      class="p-1.5 text-white bg-gradient-to-r from-orange-500 to-amber-600 rounded-lg"
                      :title="t('scanList.register')"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                      </svg>
                    </button>
                    <!-- Edit filename -->
                    <button
                      @click.stop="startEdit(item)"
                      class="p-1.5 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg"
                      :title="t('detectedList.editFilename')"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <!-- Scan exclude -->
                    <button
                      @click.stop="addToExclusions(item)"
                      class="p-1.5 text-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/20 rounded-lg"
                      :title="t('detectedList.addToExclusions')"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                      </svg>
                    </button>
                    <!-- Delete -->
                    <button
                      @click.stop="deleteItem(item.id)"
                      class="p-1.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
                      :title="t('detectedList.deleteItem')"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>

                <!-- Edit mode -->
                <div v-else class="space-y-2">
                  <input
                    v-model="editingFilename"
                    type="text"
                    class="w-full px-3 py-2 border border-blue-300 dark:border-blue-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 text-sm"
                    :placeholder="t('detectedList.filenamePlaceholder')"
                    @keyup.enter="saveEdit(item.id)"
                    @keyup.esc="cancelEdit"
                    @click.stop
                  />
                  <div class="flex gap-2">
                    <button
                      @click.stop="saveEdit(item.id)"
                      class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
                    >
                      {{ t('detectedList.save') }}
                    </button>
                    <button
                      @click.stop="cancelEdit"
                      class="px-3 py-1.5 bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500 text-gray-900 dark:text-white rounded-lg text-sm font-medium transition-colors"
                    >
                      {{ t('detectedList.cancel') }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- Desktop action buttons -->
              <div v-if="editingId !== item.id" class="hidden sm:flex items-center gap-1.5 flex-shrink-0">
                <!-- AI Search (product only) -->
                <button
                  v-if="item.classification === 'product'"
                  @click.stop="openAIMatchingDialog(item)"
                  :title="t('detectedList.aiMatching')"
                  class="p-2 text-white bg-gradient-to-r from-blue-500 to-purple-600 hover:shadow-lg rounded-xl transition-all"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </button>
                <!-- Register (non-product) -->
                <button
                  v-else
                  @click.stop="openRegisterDialog(item)"
                  :title="t('scanList.register')"
                  class="p-2 text-white bg-gradient-to-r from-orange-500 to-amber-600 hover:shadow-lg rounded-xl transition-all"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                </button>
                <!-- Edit filename -->
                <button
                  @click.stop="startEdit(item)"
                  :title="t('detectedList.editFilename')"
                  class="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-xl transition-all"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <!-- Scan exclude -->
                <button
                  @click.stop="addToExclusions(item)"
                  :title="t('detectedList.addToExclusions')"
                  class="p-2 text-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/20 rounded-xl transition-all"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                  </svg>
                </button>
                <!-- Delete -->
                <button
                  @click.stop="deleteItem(item.id)"
                  :title="t('detectedList.deleteItem')"
                  class="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-all"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
      :violation="selectedItem"
      @close="closeAIMatchingDialog"
      @saved="handleAIMatchingSaved"
    />

    <!-- Register Attachment Dialog -->
    <div
      v-if="registerDialogOpen"
      class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50 p-4"
      @click.self="closeRegisterDialog"
    >
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden">
        <!-- Dialog Header -->
        <div class="px-6 py-4 flex items-center gap-3" :class="getRegisterHeaderClass(registerItem?.classification)">
          <span class="text-2xl">{{ getClassIcon(registerItem?.classification) }}</span>
          <h3 class="text-lg font-bold text-white">
            {{ t('scanList.registerDialog.title', { type: getClassLabel(registerItem?.classification) }) }}
          </h3>
          <button @click="closeRegisterDialog" class="ml-auto text-white/80 hover:text-white">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-6 space-y-4">
          <!-- File info -->
          <div class="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-xl text-sm border border-gray-100 dark:border-gray-700">
            <p class="font-medium text-gray-900 dark:text-white break-all">{{ registerItem?.file_name }}</p>
            <p class="text-gray-500 dark:text-gray-400 text-xs mt-0.5 truncate">📁 {{ registerItem?.folder_path }}</p>
          </div>

          <!-- Software Selection -->
          <div class="space-y-3">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              {{ t('scanList.registerDialog.selectProduct') }}
            </label>

            <!-- Selected Software Display -->
            <div v-if="selectedProduct" class="px-3 py-2 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800 flex items-center gap-2">
              <img v-if="selectedProduct.icon_url" :src="selectedProduct.icon_url" class="w-6 h-6 rounded object-cover flex-shrink-0" />
              <div v-else class="w-6 h-6 rounded bg-orange-100 dark:bg-orange-800 flex items-center justify-center flex-shrink-0">
                <svg class="w-3.5 h-3.5 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2v-4M9 21H5a2 2 0 01-2-2v-4m0 0h18" />
                </svg>
              </div>
              <span class="text-sm font-semibold text-orange-700 dark:text-orange-300 flex-1 truncate">{{ selectedProduct.title }}</span>
              <svg class="w-4 h-4 text-orange-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              <button @click.stop="clearProductSelection" class="text-orange-400 hover:text-orange-600 ml-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- Same Folder Software -->
            <div>
              <p class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1.5 flex items-center gap-1">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
                {{ t('scanList.registerDialog.sameFolderSoftware') }}
              </p>
              <div v-if="loadingFolderProducts" class="flex items-center justify-center py-3">
                <svg class="animate-spin w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
              </div>
              <div v-else-if="sameFolderProducts.length > 0" class="rounded-xl border border-blue-200 dark:border-blue-700 bg-blue-50 dark:bg-blue-900/20 overflow-hidden">
                <button
                  v-for="product in sameFolderProducts"
                  :key="product.id"
                  @click.stop="selectProduct(product)"
                  class="w-full text-left px-3 py-2.5 text-sm flex items-center gap-2.5 transition-colors border-b border-blue-100 dark:border-blue-800 last:border-0"
                  :class="selectedProduct?.id === product.id
                    ? 'bg-orange-50 dark:bg-orange-900/30'
                    : 'hover:bg-blue-100 dark:hover:bg-blue-800/40'"
                >
                  <img v-if="product.icon_url" :src="product.icon_url" class="w-7 h-7 rounded object-cover flex-shrink-0" />
                  <div v-else class="w-7 h-7 rounded bg-blue-200 dark:bg-blue-700 flex items-center justify-center flex-shrink-0">
                    <svg class="w-3.5 h-3.5 text-blue-500 dark:text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2v-4M9 21H5a2 2 0 01-2-2v-4m0 0h18" />
                    </svg>
                  </div>
                  <span class="flex-1 truncate font-medium text-blue-900 dark:text-blue-100">{{ product.title }}</span>
                  <svg v-if="selectedProduct?.id === product.id" class="w-4 h-4 text-orange-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </button>
              </div>
              <p v-else class="text-xs text-gray-400 dark:text-gray-500 italic">{{ t('scanList.registerDialog.noSameFolderSoftware') }}</p>
            </div>

            <!-- All Software Search -->
            <div>
              <p class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1.5">
                {{ t('scanList.registerDialog.allSoftware') }}
              </p>
              <div class="relative mb-2">
                <input
                  v-model="registerProductSearch"
                  @input="onProductSearchInput"
                  @click.stop
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 text-sm pr-8"
                  :placeholder="t('scanList.registerDialog.searchPlaceholder')"
                />
                <div v-if="searchingProducts" class="absolute right-2.5 top-2.5">
                  <svg class="animate-spin w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                  </svg>
                </div>
                <svg v-else class="absolute right-2.5 top-2.5 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <div class="max-h-44 overflow-y-auto rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                <button
                  v-for="product in productSearchResults"
                  :key="product.id"
                  @click.stop="selectProduct(product)"
                  class="w-full text-left px-3 py-2.5 text-sm flex items-center gap-2.5 transition-colors border-b border-gray-100 dark:border-gray-700 last:border-0"
                  :class="selectedProduct?.id === product.id
                    ? 'bg-orange-50 dark:bg-orange-900/20'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700'"
                >
                  <img v-if="product.icon_url" :src="product.icon_url" class="w-6 h-6 rounded object-cover flex-shrink-0" />
                  <div v-else class="w-6 h-6 rounded bg-gray-100 dark:bg-gray-600 flex items-center justify-center flex-shrink-0">
                    <svg class="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2v-4M9 21H5a2 2 0 01-2-2v-4m0 0h18" />
                    </svg>
                  </div>
                  <span class="flex-1 truncate">{{ product.title }}</span>
                  <svg v-if="selectedProduct?.id === product.id" class="w-4 h-4 text-orange-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </button>
                <p v-if="productSearchResults.length === 0 && !searchingProducts" class="px-3 py-3 text-xs text-gray-400 dark:text-gray-500 text-center">
                  {{ t('scanList.registerDialog.noResults') }}
                </p>
              </div>
            </div>
          </div>

          <!-- Note -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
              {{ t('scanList.registerDialog.note') }}
            </label>
            <input
              v-model="registerNote"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 text-sm"
              :placeholder="t('scanList.registerDialog.notePlaceholder')"
              @click.stop
            />
          </div>

          <!-- Actions -->
          <div class="flex gap-3 pt-2">
            <button
              @click="closeRegisterDialog"
              class="flex-1 px-4 py-2.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium text-sm"
            >
              {{ t('common.cancel') }}
            </button>
            <button
              @click="submitRegister"
              :disabled="!selectedProduct || registering"
              class="flex-1 px-4 py-2.5 bg-gradient-to-r from-orange-500 to-amber-600 text-white rounded-xl hover:from-orange-600 hover:to-amber-700 transition-all font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <svg v-if="registering" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
              {{ registering ? t('scanList.registerDialog.registering') : t('scanList.registerDialog.register') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Scan Modal -->
    <div
      v-if="showScanModal"
      class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50 p-4"
      @click.self="closeScanModal"
    >
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
          <div class="space-y-3 mb-6">
            <label class="flex items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-xl cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
              <input type="radio" v-model="scanMode" value="all" class="w-4 h-4 text-green-600 border-gray-300 focus:ring-green-500" />
              <div class="ml-3">
                <span class="font-medium text-gray-900 dark:text-white">{{ t('detectedList.scanAllFolders') }}</span>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{{ t('detectedList.scanAllFoldersDesc') }}</p>
              </div>
            </label>
            <label class="flex items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-xl cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
              <input type="radio" v-model="scanMode" value="select" class="w-4 h-4 text-green-600 border-gray-300 focus:ring-green-500" />
              <div class="ml-3">
                <span class="font-medium text-gray-900 dark:text-white">{{ t('detectedList.scanSelectFolders') }}</span>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{{ t('detectedList.scanSelectFoldersDesc') }}</p>
              </div>
            </label>
          </div>
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
                <input type="checkbox" v-model="selectedScanFolders" :value="folder" class="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500" />
                <span class="ml-3 text-sm text-gray-900 dark:text-white font-mono truncate">{{ folder }}</span>
              </label>
            </div>
          </div>
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
              class="flex-1 px-4 py-2.5 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl hover:from-green-600 hover:to-emerald-700 transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <svg v-if="isScanning" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
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
import { ref, computed, onMounted } from 'vue'
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

// ── State ──────────────────────────────────────────────────────
const loading = ref(true)
const items = ref([])
const stats = ref({ total: 0, by_classification: {} })
const activeFilter = ref('all')
const editingId = ref(null)
const editingFilename = ref('')
const selectedIds = ref([])
const isAllSelected = ref(false)
const classifyMenuId = ref(null)

// AI Dialog
const aiMatchingDialogOpen = ref(false)
const selectedItem = ref(null)

// Register Dialog
const registerDialogOpen = ref(false)
const registerItem = ref(null)
const registerProductSearch = ref('')
const productSearchResults = ref([])
const sameFolderProducts = ref([])
const loadingFolderProducts = ref(false)
const selectedProduct = ref(null)
const registerNote = ref('')
const registering = ref(false)
const searchingProducts = ref(false)
let searchDebounce = null

// Scan Modal
const showScanModal = ref(false)
const isScanning = ref(false)
const scanMode = ref('all')
const scanFolders = ref([])
const selectedScanFolders = ref([])
const useAI = ref(false)

// ── Classifications ─────────────────────────────────────────────
const classifications = computed(() => [
  {
    key: 'product',
    label: t('scanList.classification.product'),
    icon: '🖥️',
    textColor: 'text-blue-600 dark:text-blue-400',
    bgClass: 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300',
    activeBgClass: 'bg-blue-600 text-white',
    ringColor: 'blue-400',
    headerClass: 'bg-gradient-to-r from-blue-500 to-blue-700',
  },
  {
    key: 'patch',
    label: t('scanList.classification.patch'),
    icon: '🔧',
    textColor: 'text-orange-600 dark:text-orange-400',
    bgClass: 'bg-orange-100 dark:bg-orange-900/40 text-orange-700 dark:text-orange-300',
    activeBgClass: 'bg-orange-500 text-white',
    ringColor: 'orange-400',
    headerClass: 'bg-gradient-to-r from-orange-500 to-amber-600',
  },
  {
    key: 'language_pack',
    label: t('scanList.classification.language_pack'),
    icon: '🌐',
    textColor: 'text-green-600 dark:text-green-400',
    bgClass: 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300',
    activeBgClass: 'bg-green-600 text-white',
    ringColor: 'green-400',
    headerClass: 'bg-gradient-to-r from-green-500 to-emerald-600',
  },
  {
    key: 'manual',
    label: t('scanList.classification.manual'),
    icon: '📄',
    textColor: 'text-purple-600 dark:text-purple-400',
    bgClass: 'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300',
    activeBgClass: 'bg-purple-600 text-white',
    ringColor: 'purple-400',
    headerClass: 'bg-gradient-to-r from-purple-500 to-violet-600',
  },
  {
    key: 'update',
    label: t('scanList.classification.update'),
    icon: '⬆️',
    textColor: 'text-sky-600 dark:text-sky-400',
    bgClass: 'bg-sky-100 dark:bg-sky-900/40 text-sky-700 dark:text-sky-300',
    activeBgClass: 'bg-sky-500 text-white',
    ringColor: 'sky-400',
    headerClass: 'bg-gradient-to-r from-sky-500 to-cyan-600',
  },
])

const filteredItems = computed(() => {
  if (activeFilter.value === 'all') return items.value
  return items.value.filter(item => item.classification === activeFilter.value)
})

// ── Helpers ─────────────────────────────────────────────────────
const getClassLabel = (cls) => {
  const found = classifications.value.find(c => c.key === cls)
  return found ? found.label : cls || ''
}

const getClassIcon = (cls) => {
  const found = classifications.value.find(c => c.key === cls)
  return found ? found.icon : '📦'
}

const getClassBg = (cls) => {
  const found = classifications.value.find(c => c.key === cls)
  return found ? found.bgClass : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
}

const getRegisterHeaderClass = (cls) => {
  const found = classifications.value.find(c => c.key === cls)
  return found ? found.headerClass : 'bg-gradient-to-r from-orange-500 to-amber-600'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

// ── Outside click handler ────────────────────────────────────────
const onOutsideClick = () => {
  if (classifyMenuId.value !== null) {
    classifyMenuId.value = null
  }
}

// ── Selection ───────────────────────────────────────────────────
const toggleAll = () => {
  if (isAllSelected.value) {
    selectedIds.value = []
    isAllSelected.value = false
  } else {
    selectedIds.value = filteredItems.value.map(v => v.id)
    isAllSelected.value = true
  }
}

const toggleSelection = (id) => {
  const index = selectedIds.value.indexOf(id)
  if (index > -1) selectedIds.value.splice(index, 1)
  else selectedIds.value.push(id)
  isAllSelected.value = selectedIds.value.length === filteredItems.value.length && filteredItems.value.length > 0
}

const isSelected = (id) => selectedIds.value.includes(id)

// ── Load ────────────────────────────────────────────────────────
const loadItems = async () => {
  loading.value = true
  try {
    const itemsRes = await filenameViolationsApi.getScanItems({ resolved: false })
    items.value = itemsRes.data || []
    selectedIds.value = []
    isAllSelected.value = false
  } catch (error) {
    console.error('Failed to load scan items:', error)
    items.value = []
  } finally {
    loading.value = false
  }
  // Load stats separately (non-critical - don't block items display)
  try {
    const statsRes = await filenameViolationsApi.getScanStats()
    stats.value = statsRes.data
  } catch (e) {
    console.warn('Failed to load stats:', e)
  }
}

const loadStats = async () => {
  try {
    const res = await filenameViolationsApi.getScanStats()
    stats.value = res.data
  } catch (e) {
    console.error('Failed to load stats:', e)
  }
}

// ── Classification ───────────────────────────────────────────────
const toggleClassifyMenu = (id) => {
  classifyMenuId.value = classifyMenuId.value === id ? null : id
}

const changeClassification = async (id, newClassification) => {
  classifyMenuId.value = null
  try {
    await filenameViolationsApi.classifyItem(id, newClassification)
    const item = items.value.find(i => i.id === id)
    if (item) {
      item.classification = newClassification
      item.classification_auto = false
    }
    await loadStats()
  } catch (error) {
    console.error('Failed to classify item:', error)
    await alert.error(t('scanList.classifyFailed'))
  }
}

// ── Delete ──────────────────────────────────────────────────────
const deleteItem = async (id) => {
  const shouldDelete = await confirm.danger(t('detectedList.deleteConfirm'))
  if (!shouldDelete) return
  try {
    await filenameViolationsApi.deleteViolation(id)
    items.value = items.value.filter(v => v.id !== id)
    await loadStats()
    await alert.success(t('detectedList.deleteSuccess'))
  } catch (error) {
    console.error('Failed to delete:', error)
    await alert.error(t('detectedList.deleteFailed'))
  }
}

const batchDeleteSelected = async () => {
  if (selectedIds.value.length === 0) {
    await alert.warning(t('detectedList.selectItems'))
    return
  }
  const shouldDelete = await confirm.danger(t('detectedList.batchDeleteConfirm', { count: selectedIds.value.length }))
  if (!shouldDelete) return
  try {
    const response = await filenameViolationsApi.batchDelete(selectedIds.value)
    await loadItems()
    const result = response.data
    if (result.failed_count > 0) {
      await alert.warning(result.message)
    } else {
      await alert.success(result.message)
    }
  } catch (error) {
    await alert.error(t('detectedList.batchDeleteFailed'))
  }
}

// ── Exclusions ──────────────────────────────────────────────────
const addToExclusions = async (item) => {
  try {
    await scanApi.addScanExclusion(item.file_name, 'pattern')
    await filenameViolationsApi.deleteViolation(item.id)
    items.value = items.value.filter(v => v.id !== item.id)
    await loadStats()
    await alert.success(t('detectedList.addedToExclusions', { pattern: item.file_name }))
  } catch (error) {
    console.error('Failed to add to exclusions:', error)
    await alert.error(t('detectedList.addToExclusionsFailed'))
  }
}

// ── Edit Filename ───────────────────────────────────────────────
const startEdit = (item) => {
  editingId.value = item.id
  editingFilename.value = item.file_name
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
    await loadItems()
    editingId.value = null
    editingFilename.value = ''
    await alert.success(t('detectedList.renameSuccess'))
  } catch (error) {
    const errorMsg = error.response?.data?.detail || t('detectedList.renameFailed')
    await alert.error(errorMsg)
  }
}

// ── AI Matching (product type) ───────────────────────────────────
const openAIMatchingDialog = async (item) => {
  try {
    const folderName = item.folder_path.split('/').filter(Boolean).pop() || ''
    const fileNameWithoutExt = item.file_name.replace(/\.(exe|msi|zip|rar|7z|iso|dmg|pkg|deb|rpm|tar\.gz|tar\.bz2)$/i, '')
    const searchNames = [folderName, fileNameWithoutExt].filter(Boolean)

    let matchedProduct = null
    for (const searchName of searchNames) {
      if (!searchName || searchName.length < 2) continue
      const searchResponse = await productsApi.getAll({ search: searchName, limit: 20 })
      const products = searchResponse.data.items || searchResponse.data
      if (!products || products.length === 0) continue

      matchedProduct = products.find(p => p.title.toLowerCase() === searchName.toLowerCase())
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
      await filenameViolationsApi.addToProduct(item.id, matchedProduct.id)
      items.value = items.value.filter(v => v.id !== item.id)
      await loadStats()
      await alert.success(t('detectedList.versionAddedToProduct', { title: matchedProduct.title }))
    } else {
      selectedItem.value = item
      aiMatchingDialogOpen.value = true
    }
  } catch (error) {
    console.error('Failed to check existing product:', error)
    selectedItem.value = item
    aiMatchingDialogOpen.value = true
  }
}

const closeAIMatchingDialog = () => {
  aiMatchingDialogOpen.value = false
  selectedItem.value = null
}

const handleAIMatchingSaved = async (data) => {
  const matchedCount = data.matched_files || 1
  if (selectedItem.value?.id) {
    const folderPath = selectedItem.value.folder_path
    if (folderPath && matchedCount > 1) {
      items.value = items.value.filter(v => v.folder_path !== folderPath)
    } else {
      items.value = items.value.filter(v => v.id !== selectedItem.value.id)
    }
  }
  await loadStats()

  const productTitle = data.product?.title || '제품'
  if (data.product?.is_duplicate) {
    await alert.info(
      `이미 존재하는 제품입니다.\n\n제품명: ${productTitle}\n${data.product.duplicate_reason || '버전만 추가되었습니다.'}\n\n제품 상세페이지의 버전 탭에서 확인하세요.`
    )
  } else {
    const fileMsg = matchedCount > 1 ? ` (같은 폴더 ${matchedCount}개 파일)` : ''
    await alert.success(`${t('detectedList.productCreateSuccess')}\n\n제품명: ${productTitle}${fileMsg}`)
  }
  if (items.value.length === 0) await loadItems()
}

// ── Register Attachment (non-product types) ─────────────────────
const openRegisterDialog = async (item) => {
  registerItem.value = item
  registerProductSearch.value = ''
  productSearchResults.value = []
  sameFolderProducts.value = []
  selectedProduct.value = null
  registerNote.value = ''
  registerDialogOpen.value = true

  // 같은 폴더의 소프트웨어 자동 로드
  loadingFolderProducts.value = true
  try {
    const res = await productsApi.getAll({ folder_path: item.folder_path, limit: 20 })
    sameFolderProducts.value = res.data.products || []
  } catch (e) {
    sameFolderProducts.value = []
  } finally {
    loadingFolderProducts.value = false
  }

  // 전체 소프트웨어 목록 초기 로드 (검색 전 기본 목록)
  try {
    const res = await productsApi.getAll({ limit: 50, sort_by: 'title', sort_order: 'asc' })
    productSearchResults.value = res.data.products || []
  } catch (e) {
    productSearchResults.value = []
  }
}

const closeRegisterDialog = () => {
  registerDialogOpen.value = false
  registerItem.value = null
  sameFolderProducts.value = []
  productSearchResults.value = []
  clearTimeout(searchDebounce)
}

const onProductSearchInput = () => {
  selectedProduct.value = null
  clearTimeout(searchDebounce)
  const q = registerProductSearch.value.trim()
  if (!q) {
    // 검색어 없으면 전체 목록으로 복원
    searchDebounce = setTimeout(async () => {
      try {
        const res = await productsApi.getAll({ limit: 50, sort_by: 'title', sort_order: 'asc' })
        productSearchResults.value = res.data.products || []
      } catch (e) {
        productSearchResults.value = []
      }
    }, 200)
    return
  }
  searchDebounce = setTimeout(async () => {
    searchingProducts.value = true
    try {
      const res = await productsApi.getAll({ search: q, limit: 30 })
      productSearchResults.value = res.data.products || []
    } catch (e) {
      productSearchResults.value = []
    } finally {
      searchingProducts.value = false
    }
  }, 300)
}

const selectProduct = (product) => {
  selectedProduct.value = product
  registerProductSearch.value = product.title
}

const clearProductSelection = () => {
  selectedProduct.value = null
  registerProductSearch.value = ''
}

const submitRegister = async () => {
  if (!selectedProduct.value || !registerItem.value) return
  registering.value = true
  try {
    await filenameViolationsApi.registerAsAttachment(
      registerItem.value.id,
      selectedProduct.value.id,
      registerItem.value.classification,
      registerNote.value
    )
    const itemType = getClassLabel(registerItem.value.classification)
    const productTitle = selectedProduct.value.title
    items.value = items.value.filter(v => v.id !== registerItem.value.id)
    await loadStats()
    closeRegisterDialog()
    await alert.success(t('scanList.registerDialog.success', { type: itemType, product: productTitle }))
  } catch (error) {
    const msg = error.response?.data?.detail || t('scanList.registerDialog.failed')
    await alert.error(msg)
  } finally {
    registering.value = false
  }
}

// ── Scan Modal ───────────────────────────────────────────────────
const openScanModal = async () => {
  try {
    const response = await configApi.getConfig()
    const config = response.data
    if (config.folders?.scanFolders) {
      scanFolders.value = config.folders.scanFolders
    } else {
      scanFolders.value = []
    }
    if (config.metadata?.scanMethod) {
      useAI.value = config.metadata.scanMethod === 'ai'
    }
  } catch (error) {
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
    const foldersToScan = scanMode.value === 'all'
      ? (scanFolders.value.length > 0 ? scanFolders.value : ['/library'])
      : selectedScanFolders.value

    const errorMessages = []
    for (const folder of foldersToScan) {
      try {
        const res = await scanApi.startScan(folder, useAI.value)
        const data = res.data || {}
        // Show file-level errors from scan response
        if (data.errors && data.errors.length > 0) {
          data.errors.slice(0, 3).forEach(e => errorMessages.push(`[${folder}] ${e}`))
          if (data.errors.length > 3) errorMessages.push(`[${folder}] ... +${data.errors.length - 3}건 오류`)
        }
      } catch (error) {
        const errorDetail = error.response?.data?.detail || error.message
        errorMessages.push(`${folder}: ${errorDetail}`)
      }
    }

    if (errorMessages.length > 0) {
      await alert.warning(t('detectedList.scanComplete') + '\n\n' + errorMessages.join('\n'))
    } else {
      await alert.success(t('detectedList.scanComplete'))
    }
    await loadItems()
  } catch (error) {
    await alert.error(t('detectedList.scanFailed'))
  } finally {
    isScanning.value = false
  }
}

onMounted(() => {
  loadItems()
})
</script>
