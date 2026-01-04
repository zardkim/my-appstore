<template>
  <div class="h-full flex flex-col lg:flex-row">
    <!-- Left Sidebar (Desktop only) -->
    <div class="hidden lg:block w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 overflow-y-auto flex-shrink-0">
      <div class="p-6">
        <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.title') }}</h2>
        <nav class="space-y-1">
          <button
            v-for="section in sections"
            :key="section.id"
            @click="activeSection = section.id"
            :class="[
              'w-full text-left px-4 py-3 rounded-xl text-sm font-medium transition-all flex items-center',
              activeSection === section.id
                ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-md'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            ]"
          >
            <span class="text-lg mr-3">{{ section.icon }}</span>
            <span>{{ section.label }}</span>
          </button>
        </nav>
      </div>
    </div>

    <!-- Mobile Section Selector -->
    <div class="lg:hidden sticky top-0 z-10 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
      <select
        v-model="activeSection"
        class="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option v-for="section in sections" :key="section.id" :value="section.id">
          {{ section.icon }} {{ section.label }}
        </option>
      </select>
    </div>

    <!-- Main Content -->
    <div class="flex-1 overflow-y-auto pb-20 lg:pb-0">
      <div class="max-w-5xl mx-auto p-4 sm:p-6 lg:p-8">

        <!-- General Settings -->
        <div v-show="activeSection === 'general'" class="space-y-4 sm:space-y-6">
          <div>
            <h1 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-1 sm:mb-2">{{ t('settings.general.title') }}</h1>
            <p class="text-sm sm:text-base text-gray-500 dark:text-gray-400">{{ t('settings.general.description') }}</p>
          </div>

          <div class="bg-white dark:bg-gray-800 rounded-xl sm:rounded-2xl shadow-sm p-4 sm:p-5 lg:p-6 border border-gray-100 dark:border-gray-700">
            <h3 class="text-base sm:text-lg font-bold text-gray-900 dark:text-white mb-3 sm:mb-4">{{ t('settings.general.systemSettings') }}</h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.general.language') }}</label>
                <select v-model="language" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="ko">{{ t('settings.general.korean') }}</option>
                  <option value="en">{{ t('settings.general.english') }}</option>
                </select>
              </div>
            </div>
          </div>

          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.general.networkSettings') }}</h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.general.frontendUrl') }}</label>
                <input v-model="accessUrl" type="text" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" :placeholder="t('settings.general.frontendUrlPlaceholder')" />
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">{{ t('settings.general.frontendUrlDesc') }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.general.backendUrl') }}</label>
                <input v-model="apiUrl" type="text" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" :placeholder="t('settings.general.backendUrlPlaceholder')" />
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">{{ t('settings.general.backendUrlDesc') }}</p>
              </div>
              <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-xl p-4">
                <div class="flex items-start">
                  <svg class="w-5 h-5 text-blue-600 dark:text-blue-400 mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div class="text-sm text-blue-800 dark:text-blue-300">
                    <p class="font-semibold mb-1">{{ t('settings.general.guideTitle') }}</p>
                    <ul class="list-disc list-inside space-y-1 text-xs">
                      <li><strong>{{ t('settings.general.guideLocal') }}</strong> {{ t('settings.general.guideLocalDesc') }}</li>
                      <li><strong>{{ t('settings.general.guideProxy') }}</strong> {{ t('settings.general.guideProxyDesc') }}</li>
                      <li><strong>{{ t('settings.general.guideRestart') }}</strong> {{ t('settings.general.guideRestartDesc') }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Apply Button -->
          <div class="flex justify-end">
            <button @click="saveGeneralSettings" class="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all shadow-md font-medium flex items-center">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              {{ t('settings.general.apply') }}
            </button>
          </div>
        </div>

        <!-- Cache Management -->
        <div v-show="activeSection === 'cache'" class="space-y-4 sm:space-y-6">
          <div>
            <h1 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-1 sm:mb-2">{{ t('settings.cache.title') }}</h1>
            <p class="text-sm sm:text-base text-gray-500 dark:text-gray-400">{{ t('settings.cache.description') }}</p>
          </div>

          <!-- Cache Statistics -->
          <div class="bg-white dark:bg-gray-800 rounded-xl sm:rounded-2xl shadow-sm p-4 sm:p-5 lg:p-6 border border-gray-100 dark:border-gray-700">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-base sm:text-lg font-bold text-gray-900 dark:text-white flex items-center">
                <span class="mr-2">⚡</span>
                {{ t('settings.cache.statistics') }}
              </h3>
              <button
                @click="loadCacheStats"
                :disabled="cacheLoading"
                class="px-3 py-1.5 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                <svg v-if="cacheLoading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ t('settings.cache.refresh') }}
              </button>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <!-- Status -->
              <div class="bg-gray-50 dark:bg-gray-700 rounded-xl p-4">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-gray-600 dark:text-gray-400">{{ t('settings.cache.status') }}</span>
                  <span v-if="cacheStats.enabled" class="text-green-500">●</span>
                  <span v-else class="text-red-500">●</span>
                </div>
                <p class="text-lg font-bold text-gray-900 dark:text-white">
                  {{ cacheStats.enabled ? t('settings.cache.enabled') : t('settings.cache.disabled') }}
                </p>
              </div>

              <!-- Total Keys -->
              <div class="bg-gray-50 dark:bg-gray-700 rounded-xl p-4">
                <div class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">{{ t('settings.cache.totalKeys') }}</div>
                <p class="text-lg font-bold text-gray-900 dark:text-white">{{ cacheStats.total_keys?.toLocaleString() || 0 }}</p>
              </div>

              <!-- Memory Used -->
              <div class="bg-gray-50 dark:bg-gray-700 rounded-xl p-4">
                <div class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">{{ t('settings.cache.memoryUsed') }}</div>
                <p class="text-lg font-bold text-gray-900 dark:text-white">{{ cacheStats.memory_used || 'N/A' }}</p>
              </div>

              <!-- Uptime -->
              <div class="bg-gray-50 dark:bg-gray-700 rounded-xl p-4">
                <div class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">{{ t('settings.cache.uptime') }}</div>
                <p class="text-lg font-bold text-gray-900 dark:text-white">
                  {{ cacheStats.uptime_seconds ? Math.floor(cacheStats.uptime_seconds / 3600) + t('settings.cache.hours') : 'N/A' }}
                </p>
              </div>
            </div>

            <div v-if="!cacheStats.enabled" class="mt-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-xl p-4">
              <div class="flex items-start">
                <svg class="w-5 h-5 text-yellow-600 dark:text-yellow-400 mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div class="text-sm text-yellow-800 dark:text-yellow-300">
                  <p class="font-semibold mb-1">{{ t('settings.cache.warning') }}</p>
                  <p class="text-xs">{{ t('settings.cache.warningDesc') }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Cache Actions -->
          <div class="bg-white dark:bg-gray-800 rounded-xl sm:rounded-2xl shadow-sm p-4 sm:p-5 lg:p-6 border border-gray-100 dark:border-gray-700">
            <h3 class="text-base sm:text-lg font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.cache.management') }}</h3>

            <div class="space-y-3">
              <!-- Clear Products Cache -->
              <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-xl">
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-white">{{ t('settings.cache.clearProducts') }}</h4>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('settings.cache.clearProductsDesc') }}</p>
                </div>
                <button
                  @click="clearProductsCache"
                  :disabled="cacheLoading || !cacheStats.enabled"
                  class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
                >
                  {{ t('settings.cache.delete') }}
                </button>
              </div>

              <!-- Clear Stats Cache -->
              <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-xl">
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-white">{{ t('settings.cache.clearStats') }}</h4>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('settings.cache.clearStatsDesc') }}</p>
                </div>
                <button
                  @click="clearStatsCache"
                  :disabled="cacheLoading || !cacheStats.enabled"
                  class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
                >
                  {{ t('settings.cache.delete') }}
                </button>
              </div>

              <!-- Clear All Cache -->
              <div class="flex items-center justify-between p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-xl">
                <div>
                  <h4 class="font-medium text-red-900 dark:text-red-300">{{ t('settings.cache.clearAll') }}</h4>
                  <p class="text-sm text-red-600 dark:text-red-400">{{ t('settings.cache.clearAllDesc') }}</p>
                </div>
                <button
                  @click="clearAllCache"
                  :disabled="cacheLoading || !cacheStats.enabled"
                  class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
                >
                  {{ t('settings.cache.deleteAll') }}
                </button>
              </div>
            </div>

            <div class="mt-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-xl p-4">
              <div class="flex items-start">
                <svg class="w-5 h-5 text-blue-600 dark:text-blue-400 mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="text-sm text-blue-800 dark:text-blue-300">
                  <p class="font-semibold mb-1">{{ t('settings.cache.infoTitle') }}</p>
                  <ul class="list-disc list-inside space-y-1 text-xs">
                    <li>{{ t('settings.cache.info1') }}</li>
                    <li>{{ t('settings.cache.info2') }}</li>
                    <li>{{ t('settings.cache.info3') }}</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- User Management -->
        <div v-show="activeSection === 'users'" class="space-y-4 sm:space-y-6">
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-4">
            <div>
              <h1 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-1 sm:mb-2">{{ t('settings.users.title') }}</h1>
              <p class="text-sm sm:text-base text-gray-500 dark:text-gray-400">{{ t('settings.users.description') }}</p>
            </div>
            <div v-if="isAdmin" class="w-full sm:w-auto flex flex-col sm:flex-row gap-2 sm:gap-3">
              <button @click="showAddUserModal = true" class="w-full sm:w-auto px-3 sm:px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg sm:rounded-xl hover:from-green-600 hover:to-emerald-700 transition-all shadow-md font-medium flex items-center justify-center text-sm sm:text-base">
                <svg class="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                </svg>
                사용자 추가
              </button>
              <button @click="showInviteModal = true" class="w-full sm:w-auto px-3 sm:px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg sm:rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all shadow-md font-medium flex items-center justify-center text-sm sm:text-base">
                <svg class="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                사용자 초대
              </button>
            </div>
          </div>

          <div v-if="!isAdmin" class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-2xl p-6">
            <div class="flex items-start">
              <svg class="w-6 h-6 text-yellow-600 dark:text-yellow-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
              <div>
                <h3 class="text-sm font-semibold text-yellow-800 dark:text-yellow-400">관리자 권한 필요</h3>
                <p class="text-sm text-yellow-700 dark:text-yellow-300 mt-1">사용자 관리는 관리자만 접근할 수 있습니다.</p>
              </div>
            </div>
          </div>

          <!-- Desktop Table View -->
          <div v-else class="hidden md:block bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
            <table class="w-full">
              <thead class="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">사용자명</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">역할</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">상태</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">생성일</th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">작업</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td class="px-6 py-4">
                    <div class="flex items-center">
                      <div class="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mr-3">
                        <span class="text-xs font-bold text-white">{{ user.username.charAt(0).toUpperCase() }}</span>
                      </div>
                      <span class="text-sm font-medium text-gray-900 dark:text-white">{{ user.username }}</span>
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <span v-if="user.role === 'admin'" class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gradient-to-r from-blue-500 to-purple-600 text-white">
                      <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
                      관리자
                    </span>
                    <span v-else class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">일반 사용자</span>
                  </td>
                  <td class="px-6 py-4">
                    <label class="relative inline-block w-12 h-6">
                      <input type="checkbox" v-model="user.is_active" @change="toggleUserStatus(user)" class="sr-only peer" :disabled="user.role === 'admin'">
                      <div :class="[
                        'w-12 h-6 rounded-full peer transition-colors cursor-pointer',
                        user.role === 'admin' ? 'bg-gray-300 cursor-not-allowed' : 'peer-focus:ring-4 peer-focus:ring-blue-300 peer-checked:bg-blue-600 bg-gray-200',
                        'after:content-[\'\'] after:absolute after:top-1 after:left-1 after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-6'
                      ]"></div>
                    </label>
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{{ formatDate(user.created_at) }}</td>
                  <td class="px-6 py-4 text-right">
                    <div class="flex items-center justify-end space-x-2">
                      <button v-if="user.role !== 'admin'" @click="openEditUserModal(user)" class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium text-sm">수정</button>
                      <button v-if="user.role !== 'admin'" @click="openPasswordModal(user)" class="text-purple-600 dark:text-purple-400 hover:text-purple-800 dark:hover:text-purple-300 font-medium text-sm">비밀번호</button>
                      <button v-if="user.role !== 'admin'" @click="deleteUser(user)" class="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 font-medium text-sm">삭제</button>
                      <span v-else class="text-gray-400 dark:text-gray-500 text-sm">시스템 관리자</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Mobile Card View -->
          <div v-if="isAdmin" class="md:hidden space-y-3">
            <div
              v-for="user in users"
              :key="user.id"
              class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4"
            >
              <!-- User Header -->
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center flex-1 min-w-0">
                  <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                    <span class="text-sm font-bold text-white">{{ user.username.charAt(0).toUpperCase() }}</span>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-semibold text-gray-900 dark:text-white truncate">{{ user.username }}</p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ formatDate(user.created_at) }}</p>
                  </div>
                </div>
              </div>

              <!-- Role & Status -->
              <div class="flex items-center justify-between mb-3 pb-3 border-b border-gray-100 dark:border-gray-700">
                <div>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">역할</p>
                  <span v-if="user.role === 'admin'" class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gradient-to-r from-blue-500 to-purple-600 text-white">
                    <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
                    관리자
                  </span>
                  <span v-else class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">일반 사용자</span>
                </div>
                <div>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mb-1 text-right">상태</p>
                  <label class="relative inline-block w-11 h-6">
                    <input type="checkbox" v-model="user.is_active" @change="toggleUserStatus(user)" class="sr-only peer" :disabled="user.role === 'admin'">
                    <div :class="[
                      'w-11 h-6 rounded-full peer transition-colors',
                      user.role === 'admin' ? 'bg-gray-300 cursor-not-allowed' : 'cursor-pointer peer-focus:ring-2 peer-focus:ring-blue-300 peer-checked:bg-blue-600 bg-gray-200',
                      'after:content-[\'\'] after:absolute after:top-1 after:left-1 after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-5'
                    ]"></div>
                  </label>
                </div>
              </div>

              <!-- Actions -->
              <div v-if="user.role !== 'admin'" class="flex gap-2">
                <button @click="openEditUserModal(user)" class="flex-1 px-3 py-2 text-sm text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 font-medium transition-colors">수정</button>
                <button @click="openPasswordModal(user)" class="flex-1 px-3 py-2 text-sm text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/30 font-medium transition-colors">비밀번호</button>
                <button @click="deleteUser(user)" class="flex-1 px-3 py-2 text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 font-medium transition-colors">삭제</button>
              </div>
              <div v-else class="text-center py-2">
                <span class="text-xs text-gray-500 dark:text-gray-400">시스템 관리자</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Folders -->
        <div v-show="activeSection === 'folders'" class="space-y-4 sm:space-y-6">
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-4">
            <div>
              <h1 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-1 sm:mb-2">{{ t('settings.folders.title') }}</h1>
              <p class="text-sm sm:text-base text-gray-500 dark:text-gray-400">{{ t('settings.folders.description') }}</p>
            </div>
            <button v-if="isAdmin" @click="addFolder" class="w-full sm:w-auto px-3 sm:px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg sm:rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all shadow-md font-medium flex items-center justify-center text-sm sm:text-base">
              <svg class="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
              {{ t('settings.folders.addFolder') }}
            </button>
          </div>

          <!-- 폴더 관리 안내 -->
          <div v-if="isAdmin" class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-xl p-4">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-blue-600 dark:text-blue-400 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="text-sm text-blue-800 dark:text-blue-300 space-y-2">
                <p class="font-semibold">{{ t('settings.folders.guideTitle') }}</p>
                <ul class="list-disc list-inside space-y-1 ml-2">
                  <li><strong>{{ t('settings.folders.dockerMount') }}</strong> <code class="bg-blue-100 dark:bg-blue-800 px-1 rounded">-v /path/to/your/software:/library/MyFolder</code></li>
                  <li><strong>{{ t('settings.folders.symbolicLink') }}</strong> <code class="bg-blue-100 dark:bg-blue-800 px-1 rounded">ln -s /path/to/your/software /library/MyFolder</code></li>
                  <li><strong>{{ t('settings.folders.directAdd') }}</strong> {{ t('settings.folders.directAddDesc') }}</li>
                </ul>
                <p class="text-xs text-blue-700 dark:text-blue-400 mt-2">
                  {{ t('settings.folders.guideTip') }}
                </p>
              </div>
            </div>
          </div>

          <div v-if="!isAdmin" class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-2xl p-6">
            <p class="text-sm text-yellow-700 dark:text-yellow-300">{{ t('settings.folders.adminOnly') }}</p>
          </div>

          <div v-else class="space-y-3">
            <!-- 폴더 목록이 비어있을 때 -->
            <div v-if="scanFolders.length === 0" class="bg-gray-50 dark:bg-gray-800 rounded-2xl border-2 border-dashed border-gray-300 dark:border-gray-600 p-8 text-center">
              <svg class="w-16 h-16 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
              <p class="text-gray-600 dark:text-gray-400 mb-2 font-medium">{{ t('settings.folders.noFolders') }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-500">{{ t('settings.folders.noFoldersDesc') }}</p>
            </div>

            <!-- 폴더 목록 -->
            <div v-for="(folder, index) in scanFolders" :key="index" class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-4 border border-gray-100 dark:border-gray-700 flex items-center justify-between">
              <div class="flex items-center flex-1 min-w-0">
                <svg class="w-5 h-5 text-blue-500 dark:text-blue-400 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" /></svg>
                <div class="flex-1 min-w-0 mr-3">
                  <div class="flex items-center gap-2">
                    <p class="text-sm font-mono text-gray-900 dark:text-white truncate">{{ folder.path }}</p>
                    <span v-if="folder.path === defaultLibraryPath" class="px-2 py-0.5 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full flex-shrink-0">{{ t('settings.folders.default') }}</span>
                  </div>
                </div>
                <button
                  @click="scanFolder(folder.path)"
                  :disabled="folder.scanning"
                  class="px-3 py-1.5 text-sm text-green-600 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg transition-colors flex-shrink-0 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5"
                  :title="t('settings.folders.scanThisFolder')"
                >
                  <svg v-if="!folder.scanning" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <svg v-else class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  {{ folder.scanning ? t('settings.folders.scanning') : t('settings.folders.scan') }}
                </button>
                <button
                  v-if="folder.path !== defaultLibraryPath"
                  @click="editFolder(index)"
                  class="px-3 py-1.5 text-sm text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors flex-shrink-0"
                >
                  {{ t('settings.folders.change') }}
                </button>
              </div>
              <button
                v-if="folder.path !== defaultLibraryPath"
                @click="removeFolder(index)"
                class="ml-3 p-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors flex-shrink-0"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
              </button>
              <div
                v-else
                class="ml-3 p-2 text-gray-400 dark:text-gray-600 cursor-not-allowed flex-shrink-0"
                :title="t('settings.folders.cannotDeleteDefault')"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
              </div>
            </div>
            <button
              v-if="scanFolders.length > 0"
              @click="saveFolders"
              class="w-full px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all shadow-md font-medium"
            >
              💾 {{ t('settings.folders.save') }}
            </button>
          </div>

          <!-- Folder Browser Modal -->
          <FolderBrowser
            :show="showFolderBrowser"
            :initial-path="editingFolderIndex !== null ? scanFolders[editingFolderIndex].path : defaultLibraryPath"
            @select="onFolderSelected"
            @close="showFolderBrowser = false"
          />
        </div>

        <!-- Categories -->
        <div v-show="activeSection === 'categories'" class="space-y-6">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">{{ t('settings.categoriesManagement.title') }}</h1>
              <p class="text-gray-500 dark:text-gray-400">{{ t('settings.categoriesManagement.description') }}</p>
            </div>
            <button v-if="isAdmin" @click="showAddCategoryModal = true" class="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all shadow-md font-medium flex items-center">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
              {{ t('settings.categoriesManagement.addCategory') }}
            </button>
          </div>

          <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div v-for="category in categories" :key="category.name" class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-4 border border-gray-100 dark:border-gray-700 hover:border-blue-200 dark:hover:border-blue-500 transition-all group">
              <div class="flex items-center justify-between mb-2">
                <span class="text-2xl">{{ category.icon }}</span>
                <div v-if="isAdmin" class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button @click="openEditCategoryModal(category)" class="p-1 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                  </button>
                  <button @click="deleteCategory(category)" class="p-1 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                  </button>
                </div>
              </div>
              <p class="font-medium text-gray-900 dark:text-white">{{ category.label }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">{{ category.name }}</p>
            </div>
          </div>

          <!-- Apply Button -->
          <div v-if="isAdmin" class="flex justify-end">
            <button @click="saveCategories" class="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all shadow-md font-medium flex items-center">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              {{ t('settings.categoriesManagement.apply') }}
            </button>
          </div>
        </div>

        <!-- Board Management -->
        <div v-show="activeSection === 'board'" class="space-y-6">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">{{ t('settings.board.title') }}</h1>
              <p class="text-gray-500 dark:text-gray-400">{{ t('settings.board.description') }}</p>
            </div>
          </div>

          <!-- Board Categories -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-bold text-gray-900 dark:text-white">{{ t('settings.board.categories') }}</h3>
              <button v-if="isAdmin" @click="showAddBoardCategoryModal = true" class="px-4 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium flex items-center">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                {{ t('settings.board.add') }}
              </button>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
              <div v-for="category in boardCategories" :key="category.value" class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 hover:border-blue-200 dark:hover:border-blue-500 transition-all group">
                <div class="flex items-center justify-between mb-3">
                  <span :class="getBoardCategoryStyle(category.color)" class="text-sm font-medium">{{ category.label }}</span>
                  <div v-if="isAdmin" class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button @click="openEditBoardCategoryModal(category)" class="p-1 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-colors">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                    </button>
                    <button @click="deleteBoardCategory(category)" class="p-1 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                    </button>
                  </div>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ category.value }}</p>
              </div>
            </div>
          </div>

          <!-- Board Settings -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.board.boardBasicSettings') }}</h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.board.postsPerPage') }}</label>
                <select v-model="postsPerPage" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="10">10개</option>
                  <option value="20">20개</option>
                  <option value="30">30개</option>
                  <option value="50">50개</option>
                </select>
              </div>

              <div class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-600 rounded-xl">
                <div>
                  <p class="font-medium text-gray-900 dark:text-white">{{ t('settings.board.allowComments') }}</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('settings.board.allowCommentsDesc') }}</p>
                </div>
                <label class="relative inline-block w-12 h-6">
                  <input type="checkbox" v-model="allowComments" class="sr-only peer" />
                  <div class="w-12 h-6 bg-gray-200 dark:bg-gray-600 peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-6 after:content-[''] after:absolute after:top-1 after:left-1 after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              <div class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-600 rounded-xl">
                <div>
                  <p class="font-medium text-gray-900 dark:text-white">{{ t('settings.board.allowAttachments') }}</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('settings.board.allowAttachmentsDesc') }}</p>
                </div>
                <label class="relative inline-block w-12 h-6">
                  <input type="checkbox" v-model="allowAttachments" class="sr-only peer" />
                  <div class="w-12 h-6 bg-gray-200 dark:bg-gray-600 peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-6 after:content-[''] after:absolute after:top-1 after:left-1 after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>
          </div>

          <!-- Apply Button -->
          <div class="flex justify-end">
            <button @click="saveBoardSettings" class="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all shadow-md font-medium flex items-center">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              {{ t('settings.board.apply') }}
            </button>
          </div>
        </div>

        <!-- Filing Rules -->
        <div v-show="activeSection === 'filing-rules'" class="space-y-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">{{ t('settings.filingRules.title') }}</h1>
            <p class="text-gray-500 dark:text-gray-400">{{ t('settings.filingRules.description') }}</p>
          </div>

          <!-- 표준 형식 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 border border-gray-100 dark:border-gray-700">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
              <span class="mr-2">📐</span>
              표준 형식
            </h2>

            <div class="space-y-6">
              <div>
                <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">기본 형식 (버전 있음)</h3>
                <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 font-mono text-sm">
                  <code class="text-blue-600 dark:text-blue-400">제품명.v버전-기타내용.확장자</code>
                </div>
              </div>

              <div>
                <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">버전 없는 경우</h3>
                <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 font-mono text-sm">
                  <code class="text-blue-600 dark:text-blue-400">제품명-기타내용.확장자</code>
                </div>
              </div>

              <div>
                <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">최소 형식</h3>
                <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 font-mono text-sm space-y-1">
                  <div><code class="text-blue-600 dark:text-blue-400">제품명.v버전.확장자</code></div>
                  <div><code class="text-blue-600 dark:text-blue-400">제품명.확장자</code></div>
                </div>
              </div>

              <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-6 border border-blue-200 dark:border-blue-800">
                <h3 class="text-lg font-semibold text-blue-800 dark:text-blue-300 mb-3 flex items-center">
                  <span class="mr-2">💡</span>
                  포터블/설치형 구분
                </h3>
                <div class="space-y-3 text-sm text-gray-700 dark:text-gray-300">
                  <p><strong class="text-blue-700 dark:text-blue-400">포터블(Portable) 판별 규칙:</strong></p>
                  <ul class="list-disc list-inside ml-4 space-y-1">
                    <li>파일명에 <code class="bg-white dark:bg-gray-800 px-2 py-0.5 rounded text-blue-600 dark:text-blue-400">Portable</code> 또는 <code class="bg-white dark:bg-gray-800 px-2 py-0.5 rounded text-blue-600 dark:text-blue-400">무설치</code> 키워드가 포함된 경우</li>
                    <li>대소문자 구분 없음 (portable, PORTABLE, Portable 모두 인식)</li>
                    <li>제품 상세 페이지에 "포터블" 또는 "설치형" 뱃지로 표시됨</li>
                  </ul>
                  <p class="mt-3"><strong class="text-blue-700 dark:text-blue-400">예시:</strong></p>
                  <div class="space-y-1 ml-4">
                    <div class="bg-white dark:bg-gray-800 rounded p-2 font-mono text-xs">
                      <span class="text-green-600 dark:text-green-400">✓</span> Total Commander.v10.51-Portable.zip
                    </div>
                    <div class="bg-white dark:bg-gray-800 rounded p-2 font-mono text-xs">
                      <span class="text-green-600 dark:text-green-400">✓</span> Adobe Photoshop.v2024-무설치.exe
                    </div>
                    <div class="bg-white dark:bg-gray-800 rounded p-2 font-mono text-xs">
                      <span class="text-green-600 dark:text-green-400">✓</span> 7-Zip-Portable Korean.exe
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 올바른 예시 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 border border-gray-100 dark:border-gray-700">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
              <span class="mr-2">✅</span>
              올바른 예시
            </h2>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 class="text-sm font-semibold text-green-600 dark:text-green-400 mb-3">패턴 1: 완전한 정보</h3>
                <div class="space-y-2">
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 font-mono text-xs text-gray-800 dark:text-gray-200">
                    Total Commander.v10.51-Final.zip
                  </div>
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 font-mono text-xs text-gray-800 dark:text-gray-200">
                    ACDSee Photo Studio.v2024-Ultimate.exe
                  </div>
                </div>
              </div>

              <div>
                <h3 class="text-sm font-semibold text-green-600 dark:text-green-400 mb-3">패턴 2: 버전 없음</h3>
                <div class="space-y-2">
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 font-mono text-xs text-gray-800 dark:text-gray-200">
                    Adobe Photoshop-Portable.exe
                  </div>
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 font-mono text-xs text-gray-800 dark:text-gray-200">
                    Total Commander-Korean.zip
                  </div>
                </div>
              </div>

              <div>
                <h3 class="text-sm font-semibold text-green-600 dark:text-green-400 mb-3">패턴 3: 기본 정보만</h3>
                <div class="space-y-2">
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 font-mono text-xs text-gray-800 dark:text-gray-200">
                    Acronis True Image.v2019.exe
                  </div>
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 font-mono text-xs text-gray-800 dark:text-gray-200">
                    Microsoft Office.v2021.iso
                  </div>
                </div>
              </div>

              <div>
                <h3 class="text-sm font-semibold text-green-600 dark:text-green-400 mb-3">패턴 4: 제품명만</h3>
                <div class="space-y-2">
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 font-mono text-xs text-gray-800 dark:text-gray-200">
                    VLC Media Player.exe
                  </div>
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 font-mono text-xs text-gray-800 dark:text-gray-200">
                    Notepad++.zip
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 피해야 할 형식 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 border border-gray-100 dark:border-gray-700">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
              <span class="mr-2">❌</span>
              피해야 할 형식
            </h2>

            <div class="space-y-4">
              <div class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4">
                <div class="font-mono text-sm text-gray-800 dark:text-gray-200 mb-2">
                  Total_Commander_10.51_Final_with_Key_x64.zip
                </div>
                <p class="text-sm text-red-700 dark:text-red-400">→ 너무 복잡하고 언더스코어 과다 사용</p>
              </div>

              <div class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4">
                <div class="font-mono text-sm text-gray-800 dark:text-gray-200 mb-2">
                  TCMDv1051.zip
                </div>
                <p class="text-sm text-red-700 dark:text-red-400">→ 제품명이 불분명함</p>
              </div>

              <div class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4">
                <div class="font-mono text-sm text-gray-800 dark:text-gray-200 mb-2">
                  total-commander-v10-51-final.zip
                </div>
                <p class="text-sm text-red-700 dark:text-red-400">→ 소문자, 버전 구분자 혼란</p>
              </div>

              <div class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4">
                <div class="font-mono text-sm text-gray-800 dark:text-gray-200 mb-2">
                  [Total Commander] v10.51 - Final.zip
                </div>
                <p class="text-sm text-red-700 dark:text-red-400">→ 대괄호 입력 불편</p>
              </div>
            </div>
          </div>

          <!-- 세부 규칙 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 border border-gray-100 dark:border-gray-700">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
              <span class="mr-2">📐</span>
              세부 규칙
            </h2>

            <div class="space-y-6">
              <!-- 제품명 -->
              <div>
                <h3 class="text-lg font-semibold text-indigo-600 dark:text-indigo-400 mb-3">1. 제품명 (Product Name)</h3>
                <ul class="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
                  <li><strong>공식 제품명</strong> 사용 (대소문자 구분)</li>
                  <li>띄어쓰기 포함 가능</li>
                  <li>특수문자는 피하기 (<code>.</code> <code>-</code> 제외)</li>
                </ul>
                <div class="mt-3 grid grid-cols-2 gap-3">
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                    <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                    <code class="text-sm text-gray-800 dark:text-gray-200">Total Commander</code>
                  </div>
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                    <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                    <code class="text-sm text-gray-800 dark:text-gray-200">Adobe Photoshop CC</code>
                  </div>
                  <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                    <span class="text-red-600 dark:text-red-400 mr-2">❌</span>
                    <code class="text-sm text-gray-800 dark:text-gray-200">Total_Commander</code>
                  </div>
                  <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                    <span class="text-red-600 dark:text-red-400 mr-2">❌</span>
                    <code class="text-sm text-gray-800 dark:text-gray-200">TotalCommander</code>
                  </div>
                </div>
              </div>

              <!-- 버전 -->
              <div>
                <h3 class="text-lg font-semibold text-indigo-600 dark:text-indigo-400 mb-3">2. 버전 (Version)</h3>
                <ul class="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
                  <li><code>.v</code> 접두사 사용 (필수)</li>
                  <li>숫자와 점(<code>.</code>)만 사용</li>
                  <li>연도도 버전으로 간주 (2023, 2024 등)</li>
                </ul>
                <div class="mt-3 grid grid-cols-2 gap-3">
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                    <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                    <code class="text-sm text-gray-800 dark:text-gray-200">.v10.51</code>
                  </div>
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                    <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                    <code class="text-sm text-gray-800 dark:text-gray-200">.v2024</code>
                  </div>
                  <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                    <span class="text-red-600 dark:text-red-400 mr-2">❌</span>
                    <code class="text-sm text-gray-800 dark:text-gray-200">.10.51</code>
                    <span class="text-xs text-red-600 dark:text-red-400"> (v 누락)</span>
                  </div>
                  <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                    <span class="text-red-600 dark:text-red-400 mr-2">❌</span>
                    <code class="text-sm text-gray-800 dark:text-gray-200">.vBuild14110</code>
                    <span class="text-xs text-red-600 dark:text-red-400"> (숫자가 아님)</span>
                  </div>
                </div>
              </div>

              <!-- 기타내용 -->
              <div>
                <h3 class="text-lg font-semibold text-indigo-600 dark:text-indigo-400 mb-3">3. 기타내용 (Description)</h3>
                <ul class="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
                  <li><code>-</code> 구분자 사용</li>
                  <li>간단명료하게</li>
                  <li>여러 정보는 쉼표 또는 띄어쓰기로 구분</li>
                </ul>
                <div class="mt-3 grid grid-cols-2 gap-3">
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                    <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                    <code class="text-sm text-gray-800 dark:text-gray-200">-Final</code>
                  </div>
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                    <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                    <code class="text-sm text-gray-800 dark:text-gray-200">-Portable</code>
                  </div>
                  <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                    <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                    <code class="text-sm text-gray-800 dark:text-gray-200">-Multilingual</code>
                  </div>
                  <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                    <span class="text-red-600 dark:text-red-400 mr-2">❌</span>
                    <code class="text-sm text-gray-800 dark:text-gray-200">-Final_with_Key</code>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 특수 카테고리 자동 인식 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 border border-gray-100 dark:border-gray-700">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
            <span class="mr-2">🏷️</span>
            특수 카테고리 자동 인식
          </h2>

          <div class="space-y-6">
            <!-- Portable 규칙 -->
            <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-700 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-purple-700 dark:text-purple-300 mb-4 flex items-center">
                <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Portable (포터블) 프로그램
              </h3>

              <div class="space-y-4">
                <div>
                  <p class="text-gray-700 dark:text-gray-300 mb-3">
                    파일명이나 폴더명에 <code class="bg-white dark:bg-gray-800 px-2 py-1 rounded text-purple-600 dark:text-purple-400 font-semibold">Portable</code> 키워드가 포함되면 자동으로 <strong>"Portable"</strong> 카테고리로 분류됩니다.
                  </p>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                    <div>
                      <p class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">파일명 예시:</p>
                      <div class="space-y-2">
                        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                          <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                          <code class="text-sm text-gray-800 dark:text-gray-200">Adobe Photoshop-Portable.exe</code>
                        </div>
                        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                          <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                          <code class="text-sm text-gray-800 dark:text-gray-200">VLC Media Player.v3.0-Portable.zip</code>
                        </div>
                        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                          <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                          <code class="text-sm text-gray-800 dark:text-gray-200">Notepad++ Portable.v8.5.exe</code>
                        </div>
                      </div>
                    </div>

                    <div>
                      <p class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">폴더명 예시:</p>
                      <div class="space-y-2">
                        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                          <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                          <code class="text-sm text-gray-800 dark:text-gray-200">Adobe Photoshop Portable/</code>
                        </div>
                        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                          <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                          <code class="text-sm text-gray-800 dark:text-gray-200">Total Commander-Portable/</code>
                        </div>
                        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                          <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                          <code class="text-sm text-gray-800 dark:text-gray-200">PortableApps/</code>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500 p-4 mt-4">
                  <div class="flex">
                    <svg class="w-5 h-5 text-blue-600 dark:text-blue-400 mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div class="text-sm text-blue-700 dark:text-blue-300">
                      <p class="font-semibold mb-1">💡 자동 인식 규칙</p>
                      <ul class="list-disc list-inside space-y-1 ml-2">
                        <li>대소문자 구분 없음 (portable, Portable, PORTABLE 모두 인식)</li>
                        <li>파일명과 폴더명 모두 적용</li>
                        <li>AI 스캔 시 자동으로 "Portable" 카테고리로 분류</li>
                        <li>설치가 필요 없는 실행 파일 형식에 권장</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <div class="mt-4">
                  <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">권장 파일명 형식:</p>
                  <div class="space-y-2">
                    <div class="flex items-center space-x-2">
                      <code class="bg-white dark:bg-gray-800 px-3 py-2 rounded text-sm text-gray-800 dark:text-gray-200 flex-1 font-mono">
                        제품명-Portable.확장자
                      </code>
                      <span class="text-xs text-gray-500 dark:text-gray-400">(버전 없음)</span>
                    </div>
                    <div class="flex items-center space-x-2">
                      <code class="bg-white dark:bg-gray-800 px-3 py-2 rounded text-sm text-gray-800 dark:text-gray-200 flex-1 font-mono">
                        제품명.v버전-Portable.확장자
                      </code>
                      <span class="text-xs text-gray-500 dark:text-gray-400">(버전 있음)</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 향후 추가 가능한 특수 카테고리 안내 -->
            <div class="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <p class="text-sm text-gray-600 dark:text-gray-400">
                <strong>참고:</strong> 향후 Patch, Crack, Keygen 등 다른 특수 카테고리에 대한 자동 인식 규칙이 추가될 수 있습니다.
              </p>
            </div>
          </div>
          </div>

          <!-- 자동 파싱 규칙 (TOP 4 패턴) -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 border border-gray-100 dark:border-gray-700">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
              <span class="mr-2">🔍</span>
              자동 파싱 규칙 (AI 매칭 최적화)
            </h2>

            <div class="space-y-6">
              <!-- 통계 안내 -->
              <div class="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-6">
                <div class="flex items-start">
                  <svg class="w-6 h-6 text-blue-600 dark:text-blue-400 mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <div>
                    <p class="text-gray-700 dark:text-gray-300 font-semibold mb-2">
                      실제 파일 1,836개 분석 결과
                    </p>
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                      NAS에 저장된 실제 소프트웨어 파일명을 통계 분석하여, 가장 빈도가 높은 <strong>4가지 핵심 패턴</strong>을 자동으로 처리합니다.
                      이를 통해 파일명이 복잡하거나 불규칙해도 AI가 올바르게 매칭할 수 있습니다.
                    </p>
                  </div>
                </div>
              </div>

              <!-- TOP 4 패턴 -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- 패턴 1: 버전 추출 우선 처리 -->
                <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-700 rounded-lg p-6">
                  <div class="flex items-center mb-4">
                    <span class="text-2xl font-bold text-purple-600 dark:text-purple-400 mr-3">1</span>
                    <div class="flex-1">
                      <h3 class="text-lg font-semibold text-purple-800 dark:text-purple-300">버전 추출 우선 처리</h3>
                      <p class="text-sm text-purple-600 dark:text-purple-400 font-medium">빈도: 30.7%</p>
                    </div>
                  </div>
                  <p class="text-sm text-gray-700 dark:text-gray-300 mb-3">
                    노이즈 제거 전에 버전 정보를 먼저 추출하여 손실을 방지합니다.
                  </p>
                  <div class="space-y-2">
                    <div class="bg-white dark:bg-gray-800 rounded p-3">
                      <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">Before:</p>
                      <code class="text-xs text-gray-700 dark:text-gray-300">Pure Flat 2013 v2.1</code>
                    </div>
                    <div class="bg-green-50 dark:bg-green-900/30 rounded p-3">
                      <p class="text-xs text-green-600 dark:text-green-400 mb-1">After:</p>
                      <code class="text-xs text-green-700 dark:text-green-300">Pure Flat → v2.1 (2013이 아님)</code>
                    </div>
                  </div>
                </div>

                <!-- 패턴 2: x64/x86 아키텍처 제거 -->
                <div class="bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-700 rounded-lg p-6">
                  <div class="flex items-center mb-4">
                    <span class="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mr-3">2</span>
                    <div class="flex-1">
                      <h3 class="text-lg font-semibold text-indigo-800 dark:text-indigo-300">x64/x86 아키텍처 제거</h3>
                      <p class="text-sm text-indigo-600 dark:text-indigo-400 font-medium">빈도: 4.5%</p>
                    </div>
                  </div>
                  <p class="text-sm text-gray-700 dark:text-gray-300 mb-3">
                    _x64_, .x86., (x64) 등의 아키텍처 정보를 자동 제거합니다.
                  </p>
                  <div class="space-y-2">
                    <div class="bg-white dark:bg-gray-800 rounded p-3">
                      <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">Before:</p>
                      <code class="text-xs text-gray-700 dark:text-gray-300">EaseUS_Todo_Backup_13.5.0_x64.rar</code>
                    </div>
                    <div class="bg-green-50 dark:bg-green-900/30 rounded p-3">
                      <p class="text-xs text-green-600 dark:text-green-400 mb-1">After:</p>
                      <code class="text-xs text-green-700 dark:text-green-300">EaseUS Todo Backup 13.5.0</code>
                    </div>
                  </div>
                </div>

                <!-- 패턴 3: 대괄호 패턴 제거 -->
                <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-6">
                  <div class="flex items-center mb-4">
                    <span class="text-2xl font-bold text-blue-600 dark:text-blue-400 mr-3">3</span>
                    <div class="flex-1">
                      <h3 class="text-lg font-semibold text-blue-800 dark:text-blue-300">[대괄호] 패턴 제거</h3>
                      <p class="text-sm text-blue-600 dark:text-blue-400 font-medium">빈도: 2.3%</p>
                    </div>
                  </div>
                  <p class="text-sm text-gray-700 dark:text-gray-300 mb-3">
                    릴리즈 그룹이나 추가 정보가 포함된 [대괄호]를 자동 제거합니다.
                  </p>
                  <div class="space-y-2">
                    <div class="bg-white dark:bg-gray-800 rounded p-3">
                      <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">Before:</p>
                      <code class="text-xs text-gray-700 dark:text-gray-300">MiniTool Partition [SadeemPC].zip</code>
                    </div>
                    <div class="bg-green-50 dark:bg-green-900/30 rounded p-3">
                      <p class="text-xs text-green-600 dark:text-green-400 mb-1">After:</p>
                      <code class="text-xs text-green-700 dark:text-green-300">MiniTool Partition</code>
                    </div>
                  </div>
                </div>

                <!-- 패턴 4: 구분자 정규화 -->
                <div class="bg-cyan-50 dark:bg-cyan-900/20 border border-cyan-200 dark:border-cyan-700 rounded-lg p-6">
                  <div class="flex items-center mb-4">
                    <span class="text-2xl font-bold text-cyan-600 dark:text-cyan-400 mr-3">4</span>
                    <div class="flex-1">
                      <h3 class="text-lg font-semibold text-cyan-800 dark:text-cyan-300">구분자 정규화</h3>
                      <p class="text-sm text-cyan-600 dark:text-cyan-400 font-medium">빈도: 36.8%</p>
                    </div>
                  </div>
                  <p class="text-sm text-gray-700 dark:text-gray-300 mb-3">
                    언더스코어(_), 하이픈(-), 점(.) 등을 공백으로 통일합니다.
                  </p>
                  <div class="space-y-2">
                    <div class="bg-white dark:bg-gray-800 rounded p-3">
                      <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">Before:</p>
                      <code class="text-xs text-gray-700 dark:text-gray-300">EaseUS_Todo_Backup_13.5.0.rar</code>
                    </div>
                    <div class="bg-green-50 dark:bg-green-900/30 rounded p-3">
                      <p class="text-xs text-green-600 dark:text-green-400 mb-1">After:</p>
                      <code class="text-xs text-green-700 dark:text-green-300">EaseUS Todo Backup 13.5.0</code>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 종합 개선 효과 -->
              <div class="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-700 rounded-lg p-6">
                <h3 class="text-lg font-semibold text-green-800 dark:text-green-300 mb-4 flex items-center">
                  <span class="mr-2">📈</span>
                  종합 개선 효과
                </h3>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div class="bg-white dark:bg-gray-800 rounded-lg p-4 text-center">
                    <p class="text-2xl font-bold text-green-600 dark:text-green-400 mb-1">30% → 70%</p>
                    <p class="text-sm text-gray-600 dark:text-gray-400">파싱 정확도</p>
                  </div>
                  <div class="bg-white dark:bg-gray-800 rounded-lg p-4 text-center">
                    <p class="text-2xl font-bold text-blue-600 dark:text-blue-400 mb-1">40% → 80%</p>
                    <p class="text-sm text-gray-600 dark:text-gray-400">AI 매칭 성공률</p>
                  </div>
                  <div class="bg-white dark:bg-gray-800 rounded-lg p-4 text-center">
                    <p class="text-2xl font-bold text-purple-600 dark:text-purple-400 mb-1">-50%</p>
                    <p class="text-sm text-gray-600 dark:text-gray-400">불필요한 API 호출</p>
                  </div>
                </div>
              </div>

              <!-- 실제 적용 예시 -->
              <div class="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4 flex items-center">
                  <span class="mr-2">✨</span>
                  실제 적용 예시
                </h3>
                <div class="space-y-4">
                  <div>
                    <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">복잡한 파일명:</p>
                    <div class="bg-white dark:bg-gray-900 rounded p-3 mb-2">
                      <code class="text-xs text-gray-700 dark:text-gray-300 break-all">
                        EaseUS_Todo_Backup_13.5.0_Build_20210129_Enterprise_Technician_WinPE_x64_Downloadly.ir.rar
                      </code>
                    </div>
                    <div class="flex items-center text-xs text-gray-500 dark:text-gray-400 mb-2">
                      <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                      </svg>
                      4가지 패턴 자동 처리
                    </div>
                    <div class="bg-green-50 dark:bg-green-900/30 rounded p-3">
                      <code class="text-xs text-green-700 dark:text-green-300">
                        <strong>EaseUS Todo Backup Enterprise Technician</strong> v13.5.0
                      </code>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 참고 사항 -->
              <div class="bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-500 p-4">
                <div class="flex">
                  <svg class="w-5 h-5 text-yellow-600 dark:text-yellow-400 mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div class="text-sm text-yellow-700 dark:text-yellow-300">
                    <p class="font-semibold mb-1">💡 자동 파싱 규칙 작동 방식</p>
                    <ul class="list-disc list-inside space-y-1 ml-2">
                      <li>파일 스캔 시 자동으로 적용되며 별도 설정이 필요 없습니다</li>
                      <li>복잡한 파일명도 AI가 이해하기 쉬운 형태로 자동 변환됩니다</li>
                      <li>기존 파일명을 변경하지 않아도 AI 매칭이 정확하게 작동합니다</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 변환 예시 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 border border-gray-100 dark:border-gray-700">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
              <span class="mr-2">📊</span>
              변환 예시
            </h2>

            <div class="overflow-x-auto">
              <table class="w-full">
                <thead class="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">기존 파일명</th>
                    <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">표준 형식</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                  <tr>
                    <td class="px-4 py-3 font-mono text-sm text-gray-600 dark:text-gray-400">Total_Commander_10.51_Final.zip</td>
                    <td class="px-4 py-3 font-mono text-sm text-green-600 dark:text-green-400 font-semibold">Total Commander.v10.51-Final.zip</td>
                  </tr>
                  <tr>
                    <td class="px-4 py-3 font-mono text-sm text-gray-600 dark:text-gray-400">ACDSee_2024_Ultimate.exe</td>
                    <td class="px-4 py-3 font-mono text-sm text-green-600 dark:text-green-400 font-semibold">ACDSee Photo Studio.v2024-Ultimate.exe</td>
                  </tr>
                  <tr>
                    <td class="px-4 py-3 font-mono text-sm text-gray-600 dark:text-gray-400">adobe_photoshop_cc_2023_portable.zip</td>
                    <td class="px-4 py-3 font-mono text-sm text-green-600 dark:text-green-400 font-semibold">Adobe Photoshop CC.v2023-Portable.zip</td>
                  </tr>
                  <tr>
                    <td class="px-4 py-3 font-mono text-sm text-gray-600 dark:text-gray-400">vlc-media-player-portable.exe</td>
                    <td class="px-4 py-3 font-mono text-sm text-green-600 dark:text-green-400 font-semibold">VLC Media Player-Portable.exe</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 체크리스트 -->
          <div class="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-2xl shadow-sm p-8 border border-blue-200 dark:border-blue-700">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
              <span class="mr-2">📝</span>
              파일 업로드 전 체크리스트
            </h2>

            <div class="space-y-3">
              <div class="flex items-start space-x-3">
                <svg class="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-gray-700 dark:text-gray-300">제품명이 공식 명칭인가?</span>
              </div>
              <div class="flex items-start space-x-3">
                <svg class="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-gray-700 dark:text-gray-300">버전이 있다면 <code class="bg-white dark:bg-gray-800 px-2 py-1 rounded">.v</code> 형식인가?</span>
              </div>
              <div class="flex items-start space-x-3">
                <svg class="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-gray-700 dark:text-gray-300">기타내용이 있다면 <code class="bg-white dark:bg-gray-800 px-2 py-1 rounded">-</code>로 시작하는가?</span>
              </div>
              <div class="flex items-start space-x-3">
                <svg class="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-gray-700 dark:text-gray-300">언더스코어(<code class="bg-white dark:bg-gray-800 px-2 py-1 rounded">_</code>)를 띄어쓰기로 변경했는가?</span>
              </div>
              <div class="flex items-start space-x-3">
                <svg class="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-gray-700 dark:text-gray-300">확장자가 소문자인가?</span>
              </div>
              <div class="flex items-start space-x-3">
                <svg class="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-gray-700 dark:text-gray-300">파일명이 간결한가? (불필요한 정보 제거)</span>
              </div>
            </div>
          </div>

          <!-- 빠른 참조 -->
          <div class="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-2xl shadow-sm p-8 border border-purple-200 dark:border-purple-700">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
              <span class="mr-2">📌</span>
              빠른 참조
            </h2>

            <div class="space-y-4">
              <div class="bg-white dark:bg-gray-800 rounded-lg p-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">완전한 형식:</p>
                    <code class="text-blue-600 dark:text-blue-400 font-mono">제품명.v버전-기타내용.확장자</code>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">버전 없음:</p>
                    <code class="text-blue-600 dark:text-blue-400 font-mono">제품명-기타내용.확장자</code>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">기본 형식:</p>
                    <code class="text-blue-600 dark:text-blue-400 font-mono">제품명.v버전.확장자</code>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">최소 형식:</p>
                    <code class="text-blue-600 dark:text-blue-400 font-mono">제품명.확장자</code>
                  </div>
                </div>
              </div>

              <div class="space-y-2">
                <p class="text-sm font-semibold text-gray-700 dark:text-gray-300">예시:</p>
                <div class="space-y-2">
                  <div class="flex items-center space-x-2">
                    <span class="text-green-600 dark:text-green-400">✅</span>
                    <code class="font-mono text-sm text-gray-800 dark:text-gray-200">Total Commander.v10.51-Final.zip</code>
                  </div>
                  <div class="flex items-center space-x-2">
                    <span class="text-green-600 dark:text-green-400">✅</span>
                    <code class="font-mono text-sm text-gray-800 dark:text-gray-200">ACDSee Photo Studio.v2024-Ultimate.exe</code>
                  </div>
                  <div class="flex items-center space-x-2">
                    <span class="text-green-600 dark:text-green-400">✅</span>
                    <code class="font-mono text-sm text-gray-800 dark:text-gray-200">Adobe Photoshop-Portable.exe</code>
                  </div>
                  <div class="flex items-center space-x-2">
                    <span class="text-green-600 dark:text-green-400">✅</span>
                    <code class="font-mono text-sm text-gray-800 dark:text-gray-200">Notepad++.exe</code>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Metadata -->
        <div v-show="activeSection === 'metadata'" class="space-y-6">
          <div class="flex items-start justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">{{ t('settings.metadata.title') }}</h1>
              <p class="text-gray-500 dark:text-gray-400">{{ t('settings.metadata.description') }}</p>
            </div>
            <button
              v-if="isAdmin"
              @click="showMetadataDialog = true"
              class="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-xl hover:from-purple-600 hover:to-pink-700 transition-all shadow-md hover:shadow-lg font-medium text-sm flex items-center"
            >
              <span class="mr-2">🤖</span>
              {{ t('settings.metadata.testMetadata') }}
            </button>
          </div>

          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.metadata.scanMethod') }}</h3>
            <div class="space-y-3">
              <label class="flex items-center p-4 border border-gray-200 dark:border-gray-600 rounded-xl cursor-pointer hover:border-blue-200 dark:hover:border-blue-500 transition-all">
                <input type="radio" name="scanMethod" value="ai" v-model="scanMethod" class="w-4 h-4 text-blue-600" />
                <div class="ml-3">
                  <p class="font-medium text-gray-900 dark:text-white">{{ t('settings.metadata.aiOnly') }}</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('settings.metadata.aiOnlyDesc') }}</p>
                </div>
              </label>
            </div>
          </div>

          <div v-if="scanMethod === 'ai'" class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.metadata.aiSettings') }}</h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.metadata.aiProvider') }}</label>
                <select v-model="aiProvider" @change="onProviderChange" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="gemini">Google Gemini</option>
                  <option value="openai">OpenAI</option>
                </select>
              </div>

              <!-- OpenAI Models -->
              <div v-if="aiProvider === 'openai'">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.metadata.openaiModel') }}</label>
                <select v-model="aiModel" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <optgroup label="o1 시리즈 (최신 추론 모델)">
                    <option value="o1">o1 (유료 - 최신 추론)</option>
                    <option value="o1-preview">o1 Preview (유료 - 미리보기)</option>
                    <option value="o1-mini">o1 Mini (유료 - 빠름)</option>
                  </optgroup>
                  <optgroup label="GPT-4o (추천)">
                    <option value="gpt-4o-mini">GPT-4o Mini (유료 - 저렴, 추천)</option>
                    <option value="gpt-4o">GPT-4o (유료 - 최신)</option>
                    <option value="gpt-4o-2024-11-20">GPT-4o (2024-11-20) (유료)</option>
                    <option value="gpt-4o-2024-08-06">GPT-4o (2024-08-06) (유료)</option>
                    <option value="gpt-4o-2024-05-13">GPT-4o (2024-05-13) (유료)</option>
                  </optgroup>
                  <optgroup label="GPT-4 Turbo">
                    <option value="gpt-4-turbo">GPT-4 Turbo (유료)</option>
                    <option value="gpt-4-turbo-2024-04-09">GPT-4 Turbo (2024-04-09) (유료)</option>
                    <option value="gpt-4-turbo-preview">GPT-4 Turbo Preview (유료)</option>
                  </optgroup>
                  <optgroup label="GPT-4">
                    <option value="gpt-4">GPT-4 (유료)</option>
                    <option value="gpt-4-0613">GPT-4 (0613) (유료)</option>
                  </optgroup>
                </select>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  💡 GPT-4o Mini가 가격 대비 성능이 좋아 추천됩니다. o1은 복잡한 추론 작업에 적합합니다.
                </p>
              </div>

              <!-- Gemini Models -->
              <div v-if="aiProvider === 'gemini'">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.metadata.geminiModel') }}</label>
                <select v-model="aiModel" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <optgroup label="Gemini 3 (최신 Preview) 🚀">
                    <option value="gemini-3-flash-preview">Gemini 3 Flash Preview</option>
                    <option value="gemini-3-pro-preview">Gemini 3 Pro Preview (고성능)</option>
                  </optgroup>
                  <optgroup label="Gemini 2.5 (안정 버전) ⭐ 추천">
                    <option value="gemini-2.5-flash">Gemini 2.5 Flash (무료 - 안정)</option>
                    <option value="gemini-2.5-pro">Gemini 2.5 Pro (무료 - 고성능)</option>
                    <option value="gemini-2.5-flash-lite">Gemini 2.5 Flash Lite (경량)</option>
                  </optgroup>
                  <optgroup label="Gemini 2.0">
                    <option value="gemini-2.0-flash-exp">Gemini 2.0 Flash Exp</option>
                    <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
                    <option value="gemini-2.0-flash-lite">Gemini 2.0 Flash Lite (경량)</option>
                  </optgroup>
                </select>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  💡 <strong>Gemini 2.5 Flash</strong>가 안정적이며 할당량이 넉넉합니다. (추천)
                </p>
                <p class="text-xs text-orange-600 dark:text-orange-400 mt-1">
                  ⚠️ 무료 할당량 초과 시 429 에러가 발생할 수 있습니다.
                </p>
              </div>

              <!-- Gemini API Key -->
              <div v-if="aiProvider === 'gemini'">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Gemini API 키
                  <span class="text-xs text-gray-500">(Google AI Studio API Key)</span>
                </label>
                <div class="relative">
                  <input
                    v-model="geminiApiKey"
                    :type="showGeminiApiKey ? 'text' : 'password'"
                    placeholder="AIzaSy..."
                    class="w-full px-4 py-2 pr-12 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                  />
                  <button
                    @click="showGeminiApiKey = !showGeminiApiKey"
                    type="button"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  >
                    <!-- Eye Icon (show) -->
                    <svg v-if="!showGeminiApiKey" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <!-- Eye Slash Icon (hide) -->
                    <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  </button>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  Gemini API 키는 https://aistudio.google.com/apikey 에서 발급받을 수 있습니다.
                </p>
              </div>

              <!-- OpenAI API Key -->
              <div v-if="aiProvider === 'openai'">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  OpenAI API 키
                  <span class="text-xs text-gray-500">(OpenAI API Key)</span>
                </label>
                <div class="relative">
                  <input
                    v-model="openaiApiKey"
                    :type="showOpenaiApiKey ? 'text' : 'password'"
                    placeholder="sk-..."
                    class="w-full px-4 py-2 pr-12 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                  />
                  <button
                    @click="showOpenaiApiKey = !showOpenaiApiKey"
                    type="button"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  >
                    <!-- Eye Icon (show) -->
                    <svg v-if="!showOpenaiApiKey" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <!-- Eye Slash Icon (hide) -->
                    <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  </button>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  OpenAI API 키는 https://platform.openai.com/api-keys 에서 발급받을 수 있습니다.
                </p>
              </div>

              <!-- Pricing Info -->
              <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-xl p-4">
                <h4 class="text-sm font-semibold text-blue-900 dark:text-blue-300 mb-2">💰 요금 정보</h4>
                <div class="text-xs text-blue-800 dark:text-blue-400 space-y-1">
                  <p v-if="aiProvider === 'openai'">
                    <strong>OpenAI (모두 유료):</strong><br>
                    • o1: $15/1M 입력, $60/1M 출력 (고급 추론)<br>
                    • GPT-4o Mini: $0.15/1M 입력, $0.60/1M 출력 (가장 저렴, 추천)<br>
                    • GPT-4o: $2.50/1M 입력, $10.00/1M 출력<br>
                    • GPT-4 Turbo: $10/1M 입력, $30/1M 출력<br>
                    • GPT-4: $30/1M 입력, $60/1M 출력
                  </p>
                  <p v-if="aiProvider === 'gemini'">
                    <strong>Gemini (무료 할당량 제공 ⭐):</strong><br>
                    • <strong class="text-green-600 dark:text-green-400">무료 할당량: 분당 15회, 일일 1,500회</strong><br>
                    • Gemini 3.0 Flash Exp: 무료 (최신)<br>
                    • Gemini 2.5 Flash Exp: 무료 (안정적, 추천)<br>
                    • Gemini 2.5 Pro Exp: 무료 (고성능)
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Google Custom Search API Settings -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">🔍 Google Custom Search API 설정</h3>
            <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
              이미지 검색 기능을 사용하려면 Google Custom Search API 키와 Search Engine ID가 필요합니다.
            </p>

            <div class="space-y-4">
              <!-- Google API Key -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Google Custom Search API 키
                  <span class="text-xs text-gray-500">(Custom Search JSON API)</span>
                </label>
                <div class="relative">
                  <input
                    v-model="googleApiKey"
                    :type="showGoogleApiKey ? 'text' : 'password'"
                    placeholder="AIzaSy..."
                    class="w-full px-4 py-2 pr-12 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                  />
                  <button
                    @click="showGoogleApiKey = !showGoogleApiKey"
                    type="button"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  >
                    <!-- Eye Icon (show) -->
                    <svg v-if="!showGoogleApiKey" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <!-- Eye Slash Icon (hide) -->
                    <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  </button>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  Google Cloud Console에서 Custom Search JSON API를 활성화하고 API 키를 발급받으세요.
                  <a href="https://console.cloud.google.com/apis/credentials" target="_blank" class="text-blue-600 dark:text-blue-400 hover:underline">
                    API 키 발급받기 →
                  </a>
                </p>
              </div>

              <!-- Search Engine ID -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Programmable Search Engine ID
                  <span class="text-xs text-gray-500">(cx 파라미터)</span>
                </label>
                <input
                  v-model="googleSearchEngineId"
                  type="text"
                  placeholder="a1b2c3d4e5f6g7h8i..."
                  class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                />
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  Programmable Search Engine에서 이미지 검색을 활성화한 검색 엔진을 만들고 ID를 복사하세요.
                  <a href="https://programmablesearchengine.google.com/" target="_blank" class="text-blue-600 dark:text-blue-400 hover:underline">
                    Search Engine 만들기 →
                  </a>
                </p>
              </div>

              <!-- Info Box -->
              <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-xl p-4">
                <h4 class="text-sm font-semibold text-green-900 dark:text-green-300 mb-2">💡 설정 가이드</h4>
                <div class="text-xs text-green-800 dark:text-green-400 space-y-2">
                  <p><strong>1. API 키 발급:</strong></p>
                  <ul class="list-disc ml-5 space-y-1">
                    <li>Google Cloud Console → API 및 서비스 → 사용자 인증 정보</li>
                    <li>"Custom Search JSON API" 활성화</li>
                    <li>API 키 생성</li>
                  </ul>
                  <p class="mt-2"><strong>2. Search Engine 생성:</strong></p>
                  <ul class="list-disc ml-5 space-y-1">
                    <li>Programmable Search Engine 페이지 접속</li>
                    <li>새 검색 엔진 만들기 (전체 웹 검색)</li>
                    <li>"이미지 검색" 활성화</li>
                    <li>검색 엔진 ID 복사 (cx 파라미터)</li>
                  </ul>
                  <p class="mt-2">
                    <strong>무료 할당량:</strong> 일일 100회 검색 가능
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Custom Prompt Editor -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h3 class="text-lg font-bold text-gray-900 dark:text-white">📝 커스텀 프롬프트</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">AI에게 질문할 프롬프트를 커스터마이징할 수 있습니다</p>
              </div>
              <label class="flex items-center cursor-pointer">
                <input type="checkbox" v-model="useCustomPrompt" class="w-5 h-5 text-blue-600 rounded" />
                <span class="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">사용</span>
              </label>
            </div>

            <div v-if="useCustomPrompt" class="space-y-4">
              <!-- Info Box -->
              <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-xl p-4">
                <p class="text-sm text-amber-800 dark:text-amber-300">
                  💡 <strong>사용 가능한 변수:</strong><br>
                  <code class="bg-amber-100 dark:bg-amber-800 px-2 py-0.5 rounded">{software_name}</code> - 소프트웨어 이름으로 자동 치환됩니다<br>
                  <br>
                  <strong>팁:</strong> 더 상세하고 구체적인 질문을 하면 AI가 더 정확한 정보를 제공합니다.
                </p>
              </div>

              <!-- OpenAI Prompt -->
              <div v-if="aiProvider === 'openai'">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  OpenAI 프롬프트
                  <button
                    @click="customPromptOpenai = defaultPromptOpenai"
                    type="button"
                    class="ml-2 text-xs text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    기본값으로 복원
                  </button>
                </label>
                <textarea
                  v-model="customPromptOpenai"
                  rows="15"
                  class="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono text-sm"
                  placeholder="OpenAI에게 질문할 프롬프트를 입력하세요..."
                ></textarea>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  현재 문자 수: {{ customPromptOpenai.length }}
                </p>
              </div>

              <!-- Gemini Prompt -->
              <div v-if="aiProvider === 'gemini'">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Gemini 프롬프트
                  <button
                    @click="customPromptGemini = defaultPromptGemini"
                    type="button"
                    class="ml-2 text-xs text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    기본값으로 복원
                  </button>
                </label>
                <textarea
                  v-model="customPromptGemini"
                  rows="15"
                  class="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono text-sm"
                  placeholder="Gemini에게 질문할 프롬프트를 입력하세요..."
                ></textarea>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  현재 문자 수: {{ customPromptGemini.length }}
                </p>
              </div>
            </div>

            <div v-else class="text-sm text-gray-500 dark:text-gray-400 text-center py-8">
              커스텀 프롬프트를 사용하려면 위의 '사용' 체크박스를 선택하세요.
            </div>
          </div>

          <!-- Apply Button -->
          <div class="flex justify-end">
            <button @click="saveMetadataSettings" class="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all shadow-md font-medium flex items-center">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              적용
            </button>
          </div>
        </div>

        <!-- Scan Exceptions -->
        <div v-show="activeSection === 'exceptions'" class="space-y-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">{{ t('settings.exceptions.title') }}</h1>
            <p class="text-gray-500 dark:text-gray-400">{{ t('settings.exceptions.description') }}</p>
          </div>

          <!-- File Patterns -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.exceptions.filePatterns') }}</h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              {{ t('settings.exceptions.filePatternsDesc') }}
            </p>

            <div class="mb-4">
              <div class="flex gap-2">
                <input
                  v-model="newExceptionPattern"
                  type="text"
                  :placeholder="t('settings.exceptions.placeholder')"
                  class="flex-1 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  @keyup.enter="addExceptionPattern"
                />
                <button
                  @click="addExceptionPattern"
                  class="px-6 py-2 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-colors whitespace-nowrap"
                >
                  {{ t('settings.exceptions.add') }}
                </button>
              </div>
            </div>

            <div class="space-y-2">
              <div
                v-for="(pattern, index) in exceptionPatterns"
                :key="index"
                class="flex items-center justify-between px-4 py-2 bg-gray-50 dark:bg-gray-700 rounded-lg"
              >
                <span class="text-sm text-gray-900 dark:text-white font-mono">{{ pattern }}</span>
                <button
                  @click="exceptionPatterns.splice(index, 1)"
                  class="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 text-sm"
                >
                  {{ t('settings.exceptions.delete') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Folder Names -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">📁 폴더명</h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              제외할 폴더명을 입력하세요. 경로의 어느 부분에서라도 이 이름이 포함되면 제외됩니다.
            </p>

            <div class="mb-4">
              <div class="flex gap-2">
                <input
                  v-model="newExceptionFolder"
                  type="text"
                  placeholder="예: .git, node_modules, __MACOSX"
                  class="flex-1 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  @keyup.enter="addExceptionFolder"
                />
                <button
                  @click="addExceptionFolder"
                  class="px-6 py-2 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-colors whitespace-nowrap"
                >
                  추가
                </button>
              </div>
            </div>

            <div class="space-y-2">
              <div
                v-for="(folder, index) in exceptionFolders"
                :key="index"
                class="flex items-center justify-between px-4 py-2 bg-gray-50 dark:bg-gray-700 rounded-lg"
              >
                <span class="text-sm text-gray-900 dark:text-white font-mono">{{ folder }}</span>
                <button
                  @click="exceptionFolders.splice(index, 1)"
                  class="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 text-sm"
                >
                  삭제
                </button>
              </div>
            </div>
          </div>

          <!-- Specific Paths -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">🗂️ 특정 경로</h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              전체 경로를 입력하여 특정 폴더를 제외합니다.
            </p>

            <div class="mb-4">
              <div class="flex gap-2">
                <input
                  v-model="newExceptionPath"
                  type="text"
                  placeholder="예: /library/temp, /library/backup"
                  class="flex-1 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  @keyup.enter="addExceptionPath"
                />
                <button
                  @click="addExceptionPath"
                  class="px-6 py-2 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-colors whitespace-nowrap"
                >
                  추가
                </button>
              </div>
            </div>

            <div v-if="exceptionPaths.length === 0" class="text-center py-8 text-gray-400 dark:text-gray-500">
              추가된 경로가 없습니다
            </div>

            <div v-else class="space-y-2">
              <div
                v-for="(path, index) in exceptionPaths"
                :key="index"
                class="flex items-center justify-between px-4 py-2 bg-gray-50 dark:bg-gray-700 rounded-lg"
              >
                <span class="text-sm text-gray-900 dark:text-white font-mono">{{ path }}</span>
                <button
                  @click="exceptionPaths.splice(index, 1)"
                  class="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 text-sm"
                >
                  삭제
                </button>
              </div>
            </div>
          </div>

          <!-- Info Box -->
          <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-xl p-4">
            <h4 class="text-sm font-bold text-blue-900 dark:text-blue-300 mb-2">ℹ️ 예외 설정 안내</h4>
            <ul class="text-sm text-blue-800 dark:text-blue-300 space-y-1">
              <li>• 파일 패턴: 파일명 매칭에 사용됩니다 (예: *.txt는 모든 텍스트 파일 제외)</li>
              <li>• 폴더명: 경로의 어느 부분에서든 해당 이름이 포함되면 제외됩니다</li>
              <li>• 특정 경로: 정확한 전체 경로로 시작하는 모든 파일/폴더를 제외합니다</li>
              <li>• 변경 사항은 다음 스캔부터 적용됩니다</li>
            </ul>
          </div>

          <!-- Apply Button -->
          <div class="flex justify-end">
            <button @click="saveExceptionSettings" :disabled="savingExceptions" class="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all shadow-md font-medium flex items-center disabled:opacity-50 disabled:cursor-not-allowed">
              <svg v-if="!savingExceptions" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else class="animate-spin w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {{ savingExceptions ? '저장 중...' : '적용' }}
            </button>
          </div>
        </div>

        <!-- System -->
        <div v-show="activeSection === 'system'" class="space-y-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">{{ t('settings.system.title') }}</h1>
            <p class="text-gray-500 dark:text-gray-400">{{ t('settings.system.description') }}</p>
          </div>

          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.system.versionInfo') }}</h3>
            <div class="space-y-3">
              <div class="flex justify-between items-center py-3 border-b border-gray-100 dark:border-gray-700">
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ t('settings.system.appVersion') }}</span>
                <span class="text-sm font-medium text-gray-900 dark:text-white">{{ appVersion }}</span>
              </div>
              <div class="flex justify-between items-center py-3 border-b border-gray-100 dark:border-gray-700">
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ t('settings.system.frontend') }}</span>
                <span class="text-sm font-medium text-gray-900 dark:text-white">Vue.js 3</span>
              </div>
              <div class="flex justify-between items-center py-3 border-b border-gray-100 dark:border-gray-700">
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ t('settings.system.backend') }}</span>
                <span class="text-sm font-medium text-gray-900 dark:text-white">FastAPI</span>
              </div>
              <div class="flex justify-between items-center py-3 border-b border-gray-100 dark:border-gray-700">
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ t('settings.system.database') }}</span>
                <span class="text-sm font-medium text-gray-900 dark:text-white">PostgreSQL</span>
              </div>
              <div class="flex justify-between items-center py-3 border-b border-gray-100 dark:border-gray-700">
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ t('settings.system.cache') }}</span>
                <span class="text-sm font-medium text-gray-900 dark:text-white">Redis</span>
              </div>
              <div class="flex justify-between items-center py-3">
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ t('settings.system.license') }}</span>
                <span class="text-sm font-medium text-gray-900 dark:text-white">MIT</span>
              </div>
            </div>
          </div>

          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.system.openSourceLicenses') }}</h3>
            <div class="space-y-3">
              <div class="p-4 border border-gray-200 dark:border-gray-600 rounded-xl">
                <div class="flex items-start justify-between mb-2">
                  <div>
                    <p class="font-medium text-gray-900 dark:text-white">TinyMCE</p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">Rich Text Editor</p>
                  </div>
                  <span class="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs rounded-lg font-medium">MIT License</span>
                </div>
                <p class="text-xs text-gray-600 dark:text-gray-400 mb-2">
                  Copyright (c) 2022 Ephox Corporation DBA Tiny Technologies, Inc.
                </p>
                <a href="https://github.com/tinymce/tinymce" target="_blank" class="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                  https://github.com/tinymce/tinymce
                </a>
              </div>
            </div>
          </div>

          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">리소스</h3>
            <a href="https://github.com/zardkim/my-appstore" target="_blank" class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-600 rounded-xl hover:border-blue-200 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all group">
              <div class="flex items-center">
                <svg class="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 mr-3" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                <div>
                  <p class="font-medium text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400">GitHub 저장소</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">소스 코드 및 이슈 트래킹</p>
                </div>
              </div>
              <svg class="w-5 h-5 text-gray-400 dark:text-gray-500 group-hover:text-blue-600 dark:group-hover:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
            </a>
          </div>
        </div>

      </div>
    </div>

    <!-- Add User Modal -->
    <div v-if="showAddUserModal" class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50" @click.self="showAddUserModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md w-full mx-4">
        <div class="flex items-center mb-4">
          <div class="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center mr-3">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">사용자 추가</h3>
        </div>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">새 사용자를 직접 생성합니다. 일반 사용자 권한으로 추가됩니다.</p>
        <form @submit.prevent="addUser" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">사용자명</label>
            <input
              v-model="newUser.username"
              type="text"
              required
              minlength="3"
              placeholder="사용자명 (최소 3자)"
              class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">비밀번호</label>
            <input
              v-model="newUser.password"
              type="password"
              required
              minlength="8"
              placeholder="비밀번호 (최소 8자)"
              class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">비밀번호 확인</label>
            <input
              v-model="newUser.passwordConfirm"
              type="password"
              required
              minlength="8"
              placeholder="비밀번호 재입력"
              class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            />
          </div>
          <div class="flex space-x-3">
            <button type="button" @click="showAddUserModal = false" class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700">취소</button>
            <button type="submit" class="flex-1 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl hover:from-green-600 hover:to-emerald-700 shadow-md">추가</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Invite User Modal -->
    <div v-if="showInviteModal" class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50" @click.self="showInviteModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md w-full mx-4">
        <div class="flex items-center mb-4">
          <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mr-3">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">사용자 초대</h3>
        </div>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">이메일 주소를 입력하면 회원가입 링크가 포함된 초대 이메일이 발송됩니다.</p>
        <form @submit.prevent="sendInvitation" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">이메일 주소</label>
            <input
              v-model="inviteEmail"
              type="email"
              required
              placeholder="user@example.com"
              class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">초대 링크는 7일간 유효하며, 한 번만 사용할 수 있습니다.</p>
          </div>
          <div class="flex space-x-3">
            <button type="button" @click="showInviteModal = false" class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700">취소</button>
            <button type="submit" class="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 shadow-md">초대 보내기</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add Category Modal -->
    <div v-if="showAddCategoryModal" class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50" @click.self="showAddCategoryModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">카테고리 추가</h3>
        <form @submit.prevent="addCategory" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">카테고리명 (영문)</label>
            <input v-model="newCategory.name" @input="autoSuggestIcon('add')" type="text" required placeholder="Graphics" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">한글명</label>
            <input v-model="newCategory.label" type="text" required placeholder="그래픽" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">아이콘 (이모지)</label>
            <div class="flex items-center space-x-2 mb-2">
              <div class="flex-shrink-0 w-12 h-12 bg-gray-100 dark:bg-gray-700 rounded-xl flex items-center justify-center text-2xl border-2 border-blue-500">
                {{ newCategory.icon || '❓' }}
              </div>
              <input v-model="newCategory.icon" type="text" required placeholder="🎨" maxlength="2" class="flex-1 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
            </div>

            <!-- Emoji Picker -->
            <div class="bg-gray-50 dark:bg-gray-900 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
              <p class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-3">자주 사용하는 이모지</p>

              <!-- Emoji Categories -->
              <div class="space-y-3">
                <div v-for="(group, groupName) in emojiGroups" :key="groupName">
                  <p class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">{{ groupName }}</p>
                  <div class="grid grid-cols-10 gap-2">
                    <button
                      v-for="emoji in group"
                      :key="emoji"
                      type="button"
                      @click="selectEmoji('add', emoji)"
                      class="w-8 h-8 flex items-center justify-center text-xl hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
                      :class="newCategory.icon === emoji ? 'bg-blue-500 dark:bg-blue-600' : ''"
                    >
                      {{ emoji }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="flex space-x-3">
            <button type="button" @click="closeAddCategoryModal" class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700">취소</button>
            <button type="submit" class="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 shadow-md">추가</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add Board Category Modal -->
    <div v-if="showAddBoardCategoryModal" class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50" @click.self="showAddBoardCategoryModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">게시판 카테고리 추가</h3>
        <form @submit.prevent="addBoardCategory" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">카테고리값 (영문)</label>
            <input v-model="newBoardCategory.value" type="text" required placeholder="tutorial" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">한글명</label>
            <input v-model="newBoardCategory.label" type="text" required placeholder="튜토리얼" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">색상</label>
            <div class="grid grid-cols-4 gap-2">
              <button
                v-for="colorOption in categoryColorOptions"
                :key="colorOption.value"
                type="button"
                @click="newBoardCategory.color = colorOption.value"
                class="px-3 py-2 rounded-lg border-2 transition-all"
                :class="[
                  newBoardCategory.color === colorOption.value
                    ? 'border-blue-500 ring-2 ring-blue-200 dark:ring-blue-800'
                    : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500',
                  colorOption.bg,
                  colorOption.text
                ]"
              >
                {{ colorOption.label }}
              </button>
            </div>
          </div>
          <div class="flex space-x-3">
            <button type="button" @click="closeAddBoardCategoryModal" class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700">취소</button>
            <button type="submit" class="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 shadow-md">추가</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Board Category Modal -->
    <div v-if="showEditBoardCategoryModal" class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50" @click.self="showEditBoardCategoryModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">게시판 카테고리 수정</h3>
        <form @submit.prevent="updateBoardCategory" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">카테고리값 (영문)</label>
            <input v-model="editingBoardCategory.value" type="text" required placeholder="tutorial" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">한글명</label>
            <input v-model="editingBoardCategory.label" type="text" required placeholder="튜토리얼" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">색상</label>
            <div class="grid grid-cols-4 gap-2">
              <button
                v-for="colorOption in categoryColorOptions"
                :key="colorOption.value"
                type="button"
                @click="editingBoardCategory.color = colorOption.value"
                class="px-3 py-2 rounded-lg border-2 transition-all"
                :class="[
                  editingBoardCategory.color === colorOption.value
                    ? 'border-blue-500 ring-2 ring-blue-200 dark:ring-blue-800'
                    : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500',
                  colorOption.bg,
                  colorOption.text
                ]"
              >
                {{ colorOption.label }}
              </button>
            </div>
          </div>
          <div class="flex space-x-3">
            <button type="button" @click="closeEditBoardCategoryModal" class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700">취소</button>
            <button type="submit" class="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 shadow-md">저장</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Category Modal -->
    <div v-if="showEditCategoryModal" class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50" @click.self="showEditCategoryModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">카테고리 수정</h3>
        <form @submit.prevent="updateCategory" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">카테고리명 (영문)</label>
            <input v-model="editingCategory.name" @input="autoSuggestIcon('edit')" type="text" required placeholder="Graphics" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">한글명</label>
            <input v-model="editingCategory.label" type="text" required placeholder="그래픽" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">아이콘 (이모지)</label>
            <div class="flex items-center space-x-2 mb-2">
              <div class="flex-shrink-0 w-12 h-12 bg-gray-100 dark:bg-gray-700 rounded-xl flex items-center justify-center text-2xl border-2 border-blue-500">
                {{ editingCategory.icon || '❓' }}
              </div>
              <input v-model="editingCategory.icon" type="text" required placeholder="🎨" maxlength="2" class="flex-1 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
            </div>

            <!-- Emoji Picker -->
            <div class="bg-gray-50 dark:bg-gray-900 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
              <p class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-3">자주 사용하는 이모지</p>

              <!-- Emoji Categories -->
              <div class="space-y-3">
                <div v-for="(group, groupName) in emojiGroups" :key="groupName">
                  <p class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">{{ groupName }}</p>
                  <div class="grid grid-cols-10 gap-2">
                    <button
                      v-for="emoji in group"
                      :key="emoji"
                      type="button"
                      @click="selectEmoji('edit', emoji)"
                      class="w-8 h-8 flex items-center justify-center text-xl hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
                      :class="editingCategory.icon === emoji ? 'bg-blue-500 dark:bg-blue-600' : ''"
                    >
                      {{ emoji }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="flex space-x-3">
            <button type="button" @click="closeEditCategoryModal" class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700">취소</button>
            <button type="submit" class="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 shadow-md">저장</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit User Modal -->
    <div v-if="showEditUserModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="showEditUserModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">사용자 정보 수정</h3>
        <form @submit.prevent="updateUser" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">사용자명</label>
            <input v-model="editingUser.username" type="text" required class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
          </div>
          <div class="flex space-x-3">
            <button type="button" @click="showEditUserModal = false" class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700">취소</button>
            <button type="submit" class="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 shadow-md">저장</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Change Password Modal -->
    <div v-if="showPasswordModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="showPasswordModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">비밀번호 변경</h3>
        <form @submit.prevent="changeUserPassword" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">사용자</label>
            <input :value="editingUser.username" type="text" disabled class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">새 비밀번호</label>
            <input v-model="newPassword" type="password" required minlength="8" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" placeholder="최소 8자 이상" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">비밀번호 확인</label>
            <input v-model="confirmPassword" type="password" required minlength="8" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" placeholder="비밀번호 재입력" />
          </div>
          <div v-if="passwordError" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-xl p-3">
            <p class="text-sm text-red-600 dark:text-red-400">{{ passwordError }}</p>
          </div>
          <div class="flex space-x-3">
            <button type="button" @click="showPasswordModal = false" class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700">취소</button>
            <button type="submit" class="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 shadow-md">변경</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Metadata Test Dialog -->
    <MetadataTestDialog
      :is-open="showMetadataDialog"
      @close="showMetadataDialog = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../store/auth'
import { useLocaleStore } from '../store/locale'
import axios from 'axios'
import FolderBrowser from '../components/FolderBrowser.vue'
import MetadataTestDialog from '../components/MetadataTestDialog.vue'
import { configApi } from '../api/config'
import { scanApi } from '../api/scan'
import { usersApi } from '../api/users'
import { invitationsApi } from '../api/invitations'
import { cacheApi } from '../api/cache'
import { ENV } from '../utils/env'
import { useDialog } from '../composables/useDialog'
import { version } from '../version.js'

const { t } = useI18n()

const route = useRoute()
const authStore = useAuthStore()
const localeStore = useLocaleStore()
const { alert, confirm } = useDialog()

const appVersion = version

const sections = computed(() => [
  { id: 'general', label: t('settings.sections.general'), icon: '⚙️' },
  { id: 'cache', label: t('settings.sections.cache'), icon: '⚡' },
  { id: 'users', label: t('settings.sections.users'), icon: '👥' },
  { id: 'folders', label: t('settings.sections.folders'), icon: '📁' },
  { id: 'categories', label: t('settings.sections.categories'), icon: '🏷️' },
  { id: 'board', label: t('settings.sections.board'), icon: '📋' },
  { id: 'filing-rules', label: t('settings.sections.filingRules'), icon: '📄' },
  { id: 'metadata', label: t('settings.sections.metadata'), icon: '🤖' },
  { id: 'exceptions', label: t('settings.sections.exceptions'), icon: '🚫' },
  { id: 'system', label: t('settings.sections.system'), icon: 'ℹ️' }
])

const activeSection = ref('general')
const userInfo = computed(() => authStore.user || { username: '', role: 'user' })
const isAdmin = computed(() => authStore.user?.role === 'admin')

// General
const language = computed({
  get: () => localeStore.locale,
  set: (value) => localeStore.setLocale(value)
})
const accessUrl = ref(ENV.APP_URL)
const apiUrl = ref('http://localhost:8100')
const passwordForm = ref({ currentPassword: '', newPassword: '', confirmPassword: '' })
const passwordLoading = ref(false)
const passwordError = ref('')
const passwordSuccess = ref('')

// Cache
const cacheStats = ref({
  enabled: false,
  total_keys: 0,
  memory_used: 'N/A',
  uptime_seconds: 0
})
const cacheLoading = ref(false)

const loadCacheStats = async () => {
  try {
    cacheLoading.value = true
    const response = await cacheApi.getStats()
    cacheStats.value = response.data
  } catch (error) {
    console.error('캐쉬 통계 로드 실패:', error)
    await alert.error('캐쉬 통계를 불러올 수 없습니다.')
  } finally {
    cacheLoading.value = false
  }
}

const clearAllCache = async () => {
  const shouldClear = await confirm.warning('모든 캐쉬를 삭제하시겠습니까?\\n\\n삭제 후 다음 요청 시 데이터가 다시 캐쉬됩니다.')

  if (!shouldClear) return

  try {
    cacheLoading.value = true
    await cacheApi.clearCache('*')
    await alert.success('모든 캐쉬가 삭제되었습니다.')
    await loadCacheStats()
  } catch (error) {
    console.error('캐쉬 삭제 실패:', error)
    await alert.error('캐쉬 삭제 중 오류가 발생했습니다.')
  } finally {
    cacheLoading.value = false
  }
}

const clearProductsCache = async () => {
  try {
    cacheLoading.value = true
    await cacheApi.clearCache('products*')
    await alert.success('제품 캐쉬가 삭제되었습니다.')
    await loadCacheStats()
  } catch (error) {
    console.error('제품 캐쉬 삭제 실패:', error)
    await alert.error('제품 캐쉬 삭제 중 오류가 발생했습니다.')
  } finally {
    cacheLoading.value = false
  }
}

const clearStatsCache = async () => {
  try {
    cacheLoading.value = true
    await cacheApi.clearCache('stats*')
    await alert.success('통계 캐쉬가 삭제되었습니다.')
    await loadCacheStats()
  } catch (error) {
    console.error('통계 캐쉬 삭제 실패:', error)
    await alert.error('통계 캐쉬 삭제 중 오류가 발생했습니다.')
  } finally {
    cacheLoading.value = false
  }
}

// Users
const users = ref([])
const showAddUserModal = ref(false)
const showInviteModal = ref(false)
const showPasswordModal = ref(false)
const inviteEmail = ref('')
const newUser = ref({ username: '', password: '', passwordConfirm: '' })
const editingUser = ref({ id: null, username: '' })
const newPassword = ref('')
const confirmPassword = ref('')
const loadingUsers = ref(false)

// Folders
const defaultLibraryPath = import.meta.env.VITE_LIBRARY_PATH || '/library'
const scanFolders = ref([
  { path: defaultLibraryPath, scanning: false }
])
const showFolderBrowser = ref(false)
const editingFolderIndex = ref(null)

// Categories
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
  { name: 'Business', label: '업무용', icon: '💼' },
  { name: 'Engineering', label: '공학용', icon: '📐' },
  { name: 'Theme', label: '테마&스킨', icon: '🎭' },
  { name: 'Hardware', label: '하드웨어', icon: '🔌' },
  { name: 'Font', label: '글꼴', icon: '🔤' },
  { name: 'Uncategorized', label: '미분류', icon: '📂' }
])
const showAddCategoryModal = ref(false)
const showEditCategoryModal = ref(false)
const newCategory = ref({ name: '', label: '', icon: '' })
const editingCategory = ref({ oldName: '', name: '', label: '', icon: '' })

// 카테고리명에 따른 이모지 매핑
const categoryIconMap = {
  'graphics': '🎨',
  'design': '🎨',
  'office': '📊',
  'productivity': '📊',
  'development': '💻',
  'dev': '💻',
  'programming': '💻',
  'code': '💻',
  'utility': '🛠️',
  'tool': '🛠️',
  'media': '🎬',
  'video': '🎬',
  'audio': '🎵',
  'music': '🎵',
  'os': '💿',
  'system': '💿',
  'security': '🔒',
  'network': '🌐',
  'internet': '🌐',
  'mac': '🍎',
  'apple': '🍎',
  'mobile': '📱',
  'android': '📱',
  'ios': '📱',
  'patch': '🔧',
  'driver': '⚙️',
  'source': '📦',
  'backup': '💾',
  'recovery': '💾',
  'portable': '🎒',
  'business': '💼',
  'engineering': '📐',
  'theme': '🎭',
  'skin': '🎭',
  'hardware': '🔌',
  'game': '🎮',
  'gaming': '🎮',
  'database': '🗄️',
  'server': '🖥️',
  'cloud': '☁️',
  'education': '📚',
  'finance': '💰',
  'photo': '📷',
  'image': '📷',
  'communication': '💬',
  'social': '👥',
  'browser': '🌍',
  'web': '🌍',
  'uncategorized': '📂',
  'others': '📂',
  'misc': '📂',
  'miscellaneous': '📂',
  '미분류': '📂',
  '기타': '📂'
}

// Board Management
const boardCategories = ref([
  { value: 'tip', label: '팁', color: 'green' },
  { value: 'tech', label: '기술', color: 'blue' },
  { value: 'tutorial', label: '튜토리얼', color: 'purple' },
  { value: 'qna', label: 'Q&A', color: 'yellow' },
  { value: 'news', label: '뉴스', color: 'red' }
])
const showAddBoardCategoryModal = ref(false)
const showEditBoardCategoryModal = ref(false)
const newBoardCategory = ref({ value: '', label: '', color: 'blue' })
const editingBoardCategory = ref({ oldValue: '', value: '', label: '', color: 'blue' })

// 게시판 카테고리 색상 옵션
const categoryColorOptions = [
  { value: 'green', label: '초록색', bg: 'bg-green-100 dark:bg-green-900/50', text: 'text-green-800 dark:text-green-300' },
  { value: 'blue', label: '파란색', bg: 'bg-blue-100 dark:bg-blue-900/50', text: 'text-blue-800 dark:text-blue-300' },
  { value: 'purple', label: '보라색', bg: 'bg-purple-100 dark:bg-purple-900/50', text: 'text-purple-800 dark:text-purple-300' },
  { value: 'yellow', label: '노란색', bg: 'bg-yellow-100 dark:bg-yellow-900/50', text: 'text-yellow-800 dark:text-yellow-300' },
  { value: 'red', label: '빨간색', bg: 'bg-red-100 dark:bg-red-900/50', text: 'text-red-800 dark:text-red-300' },
  { value: 'pink', label: '분홍색', bg: 'bg-pink-100 dark:bg-pink-900/50', text: 'text-pink-800 dark:text-pink-300' },
  { value: 'orange', label: '주황색', bg: 'bg-orange-100 dark:bg-orange-900/50', text: 'text-orange-800 dark:text-orange-300' },
  { value: 'indigo', label: '남색', bg: 'bg-indigo-100 dark:bg-indigo-900/50', text: 'text-indigo-800 dark:text-indigo-300' }
]

const postsPerPage = ref('20')
const allowComments = ref(true)
const allowAttachments = ref(true)

// 이모지 그룹
const emojiGroups = {
  '소프트웨어': ['💻', '🖥️', '⌨️', '🖱️', '💾', '💿', '📀', '🔌', '🖨️', '⚙️'],
  '작업 & 도구': ['🛠️', '🔧', '🔨', '⚒️', '🪛', '🗜️', '⛏️', '🪚', '📐', '📏'],
  '문서 & 오피스': ['📊', '📈', '📉', '📝', '📋', '📄', '📃', '📑', '🗂️', '📁'],
  '미디어': ['🎬', '🎥', '📹', '🎞️', '📷', '📸', '🎨', '🖼️', '🎭', '🎪'],
  '음악 & 사운드': ['🎵', '🎶', '🎼', '🎤', '🎧', '📻', '🎸', '🎹', '🎺', '🎷'],
  '통신 & 네트워크': ['🌐', '🌍', '🌎', '🌏', '💬', '📱', '📞', '☎️', '📡', '📶'],
  '보안 & 시스템': ['🔒', '🔐', '🔑', '🛡️', '🔓', '🔏', '⚠️', '🚨', '🆘', '⛔'],
  '게임 & 엔터': ['🎮', '🕹️', '🎯', '🎲', '🧩', '♠️', '♥️', '♦️', '♣️', '🃏'],
  '비즈니스': ['💼', '🏢', '🏦', '💰', '💵', '💴', '💶', '💷', '💳', '📊'],
  '교육 & 학습': ['📚', '📖', '📕', '📗', '📘', '📙', '📓', '📔', '📒', '🎓'],
  '기타': ['📦', '📮', '📫', '📪', '📬', '📭', '🎒', '💾', '🗄️', '☁️']
}

// Metadata
const scanMethod = ref('ai')
const aiProvider = ref('gemini')
const aiModel = ref('gemini-2.5-flash')
const geminiApiKey = ref('')
const openaiApiKey = ref('')
const showGeminiApiKey = ref(false)
const showOpenaiApiKey = ref(false)
const googleApiKey = ref('')
const googleSearchEngineId = ref('')
const showGoogleApiKey = ref(false)
const useCustomPrompt = ref(false)
const customPromptOpenai = ref('')
const customPromptGemini = ref('')

// 기본 프롬프트 템플릿
const defaultPromptOpenai = `다음 소프트웨어에 대한 상세한 메타데이터를 JSON 형식으로 제공해주세요.

소프트웨어: {software_name}

**반드시 아래 모든 필드를 포함한 JSON을 작성하세요:**

{
  "title": "정확한 공식 소프트웨어 이름",
  "version": "버전 정보 (파일명에서 추출)",
  "platform": "Windows/macOS/Linux/Cross-platform",
  "developer": "개발사/제조사 공식 이름",
  "category": "Graphics/Office/Development/Utility/Media/OS/Security/Network/Mac/Mobile 등",
  "official_website": "공식 웹사이트 전체 URL (https://...)",
  "license_type": "Commercial/Free/Freemium/Trial/Open Source",
  "language": "지원 언어 (예: 영어, 한국어, 일본어 또는 다국어)",
  "description_short": "50-100자 이내의 간결한 한 줄 설명",
  "description_detailed": "200-300자의 상세 설명. 주요 특징, 용도, 워크플로우, 장점을 구체적으로 설명",
  "features": [
    "주요 기능 1 (구체적으로)",
    "주요 기능 2",
    "주요 기능 3",
    "주요 기능 4",
    "주요 기능 5"
  ],
  "supported_formats": ["포맷1", "포맷2", "포맷3"],
  "system_requirements": {
    "os": "Windows XP/Vista/7/8/10/11 (32/64비트) 등 구체적으로",
    "cpu": "프로세서 요구사항 (예: Intel Core 2 Duo 2.0GHz 이상)",
    "ram": "최소 2GB, 권장 4GB 이상",
    "disk_space": "500MB ~ 1GB 등",
    "gpu": "GPU 요구사항 (있으면 작성, 없으면 빈 문자열)",
    "additional": "DirectX, .NET Framework 등 추가 요구사항"
  },
  "installation_info": {
    "installer_type": "EXE 설치 파일/MSI/Portable/ZIP 압축",
    "file_size": "약 XXX MB",
    "internet_required": "필요/불필요/라이선스 인증 시 필요"
  },
  "release_notes": "이 버전의 주요 특징이나 변경사항 (2-3줄)"
}

**필수 지침:**
1. 위 JSON 구조를 정확히 따르세요
2. 모든 필드를 반드시 포함하세요 (알 수 없으면 빈 문자열 "" 또는 빈 배열 [])
3. features는 최소 5개 이상 작성
4. 공식 웹사이트는 정확한 URL (https://... 형태)
5. JSON만 응답하고 추가 설명 금지
6. 정확한 정보만 제공하고 추측 금지`


const defaultPromptGemini = `다음 소프트웨어에 대한 상세한 메타데이터를 JSON 형식으로 제공해주세요.

소프트웨어: {software_name}

**반드시 아래 모든 필드를 포함한 JSON을 작성하세요:**

{
  "title": "정확한 공식 소프트웨어 이름",
  "version": "버전 정보 (파일명에서 추출)",
  "platform": "Windows/macOS/Linux/Cross-platform",
  "developer": "개발사/제조사 공식 이름",
  "category": "Graphics/Office/Development/Utility/Media/OS/Security/Network/Mac/Mobile 등",
  "official_website": "공식 웹사이트 전체 URL (https://...)",
  "license_type": "Commercial/Free/Freemium/Trial/Open Source",
  "language": "지원 언어 (예: 영어, 한국어, 일본어 또는 다국어)",
  "description_short": "50-100자 이내의 간결한 한 줄 설명",
  "description_detailed": "200-300자의 상세 설명. 주요 특징, 용도, 워크플로우, 장점을 구체적으로 설명",
  "features": [
    "주요 기능 1 (구체적으로)",
    "주요 기능 2",
    "주요 기능 3",
    "주요 기능 4",
    "주요 기능 5",
    "주요 기능 6"
  ],
  "supported_formats": ["포맷1", "포맷2", "포맷3"],
  "system_requirements": {
    "os": "Windows XP/Vista/7/8/10/11 (32/64비트) 등 구체적으로",
    "cpu": "프로세서 요구사항 (예: Intel Core 2 Duo 2.0GHz 이상)",
    "ram": "최소 2GB, 권장 4GB 이상",
    "disk_space": "500MB ~ 1GB 등",
    "gpu": "GPU 요구사항 (있으면 작성, 없으면 빈 문자열)",
    "additional": "DirectX, .NET Framework 등 추가 요구사항"
  },
  "installation_info": {
    "installer_type": "EXE 설치 파일/MSI/Portable/ZIP 압축",
    "file_size": "약 XXX MB",
    "internet_required": "필요/불필요/라이선스 인증 시 필요"
  },
  "release_notes": "이 버전의 주요 특징이나 변경사항 (2-3줄)"
}

**필수 지침:**
1. 위 JSON 구조를 정확히 따르세요
2. 모든 필드를 반드시 포함하세요 (알 수 없으면 빈 문자열 "" 또는 빈 배열 [])
3. features는 최소 5개 이상 작성
4. 공식 웹사이트는 정확한 URL (https://... 형태)
5. JSON만 응답하고 추가 설명이나 마크다운 코드블록 사용 금지
6. 정확한 정보만 제공하고 추측 금지`
const showMetadataDialog = ref(false)

// 커스텀 프롬프트 활성화 시 기본값으로 초기화
watch(useCustomPrompt, (newValue) => {
  if (newValue) {
    // 커스텀 프롬프트가 활성화되었는데 비어있으면 기본값으로 채움
    if (!customPromptOpenai.value || customPromptOpenai.value.trim() === '') {
      customPromptOpenai.value = defaultPromptOpenai
    }
    if (!customPromptGemini.value || customPromptGemini.value.trim() === '') {
      customPromptGemini.value = defaultPromptGemini
    }
  }
})

// AI 제공자 변경 시 기본 모델 설정
const onProviderChange = () => {
  if (aiProvider.value === 'openai') {
    aiModel.value = 'gpt-4o-mini'
  } else if (aiProvider.value === 'gemini') {
    aiModel.value = 'gemini-2.5-flash'
  }
}

// Scan Exceptions
const exceptionPatterns = ref([])
const exceptionFolders = ref([])
const exceptionPaths = ref([])
const newExceptionPattern = ref('')
const newExceptionFolder = ref('')
const newExceptionPath = ref('')
const savingExceptions = ref(false)

const changePassword = async () => {
  passwordError.value = ''
  passwordSuccess.value = ''

  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    passwordError.value = '새 비밀번호가 일치하지 않습니다.'
    return
  }

  if (passwordForm.value.newPassword.length < 8) {
    passwordError.value = '비밀번호는 최소 8자 이상이어야 합니다.'
    return
  }

  passwordLoading.value = true

  try {
    await axios.post('/api/auth/change-password', {
      current_password: passwordForm.value.currentPassword,
      new_password: passwordForm.value.newPassword
    })
    passwordSuccess.value = '비밀번호가 성공적으로 변경되었습니다.'
    passwordForm.value = { currentPassword: '', newPassword: '', confirmPassword: '' }
  } catch (error) {
    passwordError.value = error.response?.status === 401 ? '현재 비밀번호가 올바르지 않습니다.' : '비밀번호 변경에 실패했습니다.'
  } finally {
    passwordLoading.value = false
  }
}

// Exception management
const addExceptionPattern = () => {
  const pattern = newExceptionPattern.value.trim()
  if (pattern && !exceptionPatterns.value.includes(pattern)) {
    exceptionPatterns.value.push(pattern)
    newExceptionPattern.value = ''
  }
}

const addExceptionFolder = () => {
  const folder = newExceptionFolder.value.trim()
  if (folder && !exceptionFolders.value.includes(folder)) {
    exceptionFolders.value.push(folder)
    newExceptionFolder.value = ''
  }
}

const addExceptionPath = () => {
  const path = newExceptionPath.value.trim()
  if (path && !exceptionPaths.value.includes(path)) {
    exceptionPaths.value.push(path)
    newExceptionPath.value = ''
  }
}

// 스캔 예외 설정 저장
const saveExceptionSettings = async () => {
  savingExceptions.value = true
  try {
    await scanApi.saveScanExclusions(exceptionFolders.value)
    await alert.success('스캔 예외 설정이 저장되었습니다.')
  } catch (error) {
    console.error('스캔 예외 설정 저장 오류:', error)
    await alert.error('스캔 예외 설정 저장에 실패했습니다.')
  } finally {
    savingExceptions.value = false
  }
}

// 스캔 예외 설정 불러오기
const loadExceptionSettings = async () => {
  try {
    const response = await scanApi.getScanExclusions()
    if (response && response.data && response.data.exclusions) {
      exceptionFolders.value = response.data.exclusions
    } else {
      // 기본값 설정
      exceptionFolders.value = ['.git', 'node_modules', '__MACOSX', '$RECYCLE.BIN', '.Trash']
    }
  } catch (error) {
    console.error('스캔 예외 설정 불러오기 오류:', error)
    // 기본값 설정
    exceptionFolders.value = ['.git', 'node_modules', '__MACOSX', '$RECYCLE.BIN', '.Trash']
  }
}

const formatDate = (dateStr) => new Date(dateStr).toLocaleDateString('ko-KR')

const loadUsers = async () => {
  try {
    loadingUsers.value = true
    users.value = await usersApi.getAll()
  } catch (error) {
    console.error('사용자 목록 로드 오류:', error)

    // Fallback: 최소한 현재 로그인한 사용자는 표시
    if (authStore.user) {
      users.value = [{
        id: authStore.user.id || 1,
        username: authStore.user.username,
        role: authStore.user.role || 'admin',
        is_active: true,
        created_at: new Date().toISOString()
      }]
    }

    // 에러는 콘솔에만 출력 (사용자에게는 표시하지 않음)
    console.warn('백엔드 API 연결 실패. Fallback 데이터 사용 중.')
  } finally {
    loadingUsers.value = false
  }
}

const addUser = async () => {
  // 사용자명 검증
  if (!newUser.value.username || newUser.value.username.trim().length < 3) {
    await alert.warning('사용자명은 최소 3자 이상이어야 합니다.')
    return
  }

  // 비밀번호 길이 검증
  if (newUser.value.password.length < 8) {
    await alert.warning('비밀번호는 최소 8자 이상이어야 합니다.')
    return
  }

  // 비밀번호 일치 검증
  if (newUser.value.password !== newUser.value.passwordConfirm) {
    await alert.warning('비밀번호가 일치하지 않습니다.')
    return
  }

  try {
    await usersApi.create(newUser.value.username, newUser.value.password, 'user')
    await loadUsers() // 사용자 목록 새로고침
    await alert.success('사용자가 추가되었습니다.')
    showAddUserModal.value = false
    newUser.value = { username: '', password: '', passwordConfirm: '' }
  } catch (error) {
    console.error('사용자 추가 오류:', error)
    const errorMessage = error.response?.data?.detail || '사용자 추가에 실패했습니다.'
    await alert.error(errorMessage)
  }
}

const sendInvitation = async () => {
  if (!inviteEmail.value) {
    await alert.warning('이메일 주소를 입력해주세요.')
    return
  }

  // 이메일 형식 검증
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(inviteEmail.value)) {
    await alert.warning('올바른 이메일 주소를 입력해주세요.')
    return
  }

  try {
    await invitationsApi.send(inviteEmail.value)
    await alert.success('초대 이메일이 발송되었습니다.')
    showInviteModal.value = false
    inviteEmail.value = ''
  } catch (error) {
    console.error('초대 발송 오류:', error)
    const errorMessage = error.response?.data?.detail || '초대 이메일 발송에 실패했습니다.'
    await alert.error(errorMessage)
  }
}

const openPasswordModal = (user) => {
  editingUser.value = { id: user.id, username: user.username }
  newPassword.value = ''
  confirmPassword.value = ''
  passwordError.value = ''
  showPasswordModal.value = true
}

const changeUserPassword = async () => {
  passwordError.value = ''

  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = '새 비밀번호가 일치하지 않습니다.'
    return
  }

  if (newPassword.value.length < 8) {
    passwordError.value = '비밀번호는 최소 8자 이상이어야 합니다.'
    return
  }

  try {
    await usersApi.changePassword(editingUser.value.id, newPassword.value)
    showPasswordModal.value = false
    editingUser.value = { id: null, username: '' }
    newPassword.value = ''
    confirmPassword.value = ''
    await alert.success('비밀번호가 변경되었습니다.')
  } catch (error) {
    console.error('비밀번호 변경 오류:', error)
    passwordError.value = error.response?.data?.detail || '비밀번호 변경에 실패했습니다.'
  }
}

const toggleUserStatus = async (user) => {
  try {
    await usersApi.toggleStatus(user.id, user.is_active)
  } catch (error) {
    console.error('상태 변경 오류:', error)
    // Revert status on error
    user.is_active = !user.is_active
    await alert.error('사용자 상태 변경에 실패했습니다.')
  }
}

const deleteUser = async (user) => {
  const shouldDelete = await confirm.danger(`${user.username} 사용자를 삭제하시겠습니까?`, '사용자 삭제')
  if (!shouldDelete) return

  try {
    await usersApi.delete(user.id)
    await loadUsers() // Reload users list
    await alert.success('사용자가 삭제되었습니다.')
  } catch (error) {
    console.error('사용자 삭제 오류:', error)
    const errorMessage = error.response?.data?.detail || '사용자 삭제에 실패했습니다.'
    await alert.error(errorMessage)
  }
}

const addFolder = () => {
  editingFolderIndex.value = null
  showFolderBrowser.value = true
}

const editFolder = async (index) => {
  // 기본 폴더는 수정 불가
  if (scanFolders.value[index].path === defaultLibraryPath) {
    await alert.warning('기본 폴더는 수정할 수 없습니다.')
    return
  }

  editingFolderIndex.value = index
  showFolderBrowser.value = true
}

const onFolderSelected = async (path) => {
  if (editingFolderIndex.value !== null) {
    // 기존 폴더 경로 수정
    // 다른 폴더와 중복 체크 (자기 자신 제외)
    const isDuplicate = scanFolders.value.some((folder, index) =>
      index !== editingFolderIndex.value && folder.path === path
    )

    if (isDuplicate) {
      await alert.warning('이미 추가된 폴더입니다.')
      return
    }

    scanFolders.value[editingFolderIndex.value].path = path
  } else {
    // 새 폴더 추가 - 중복 체크
    const isDuplicate = scanFolders.value.some(folder => folder.path === path)

    if (isDuplicate) {
      await alert.warning('이미 추가된 폴더입니다.')
      return
    }

    scanFolders.value.push({ path, scanning: false })
  }
  showFolderBrowser.value = false
  editingFolderIndex.value = null
}

const removeFolder = async (index) => {
  // 기본 폴더는 삭제 불가
  if (scanFolders.value[index].path === defaultLibraryPath) {
    await alert.warning('기본 폴더는 삭제할 수 없습니다.')
    return
  }

  const shouldConfirm = await confirm.warning('이 폴더를 삭제하시겠습니까?')
  if (shouldConfirm) {
    scanFolders.value.splice(index, 1)
  }
}

const scanFolder = async (path) => {
  const folder = scanFolders.value.find(f => f.path === path)
  if (!folder) return

  const shouldScan = await confirm.info(`${path} 폴더를 스캔하시겠습니까?`)
  if (!shouldScan) {
    return
  }

  try {
    folder.scanning = true

    // 스캔 방식에 따라 AI 사용 여부 결정
    const useAI = scanMethod.value === 'ai'

    const response = await scanApi.startScan(path, useAI)

    if (response.data) {
      const result = response.data
      await alert.success(`스캔 완료!\n\n새 프로그램: ${result.new_products || 0}개\n새 버전: ${result.new_versions || 0}개\n업데이트: ${result.updated_products || 0}개`)
    }
  } catch (error) {
    console.error('폴더 스캔 오류:', error)
    const errorMessage = error.response?.data?.detail || error.message || '스캔 중 오류가 발생했습니다.'
    await alert.error(`스캔 실패: ${errorMessage}`)
  } finally {
    folder.scanning = false
  }
}

const saveFolders = async () => {
  try {
    // 최소 1개 이상의 폴더가 필요
    if (scanFolders.value.length === 0) {
      await alert.warning(' 최소 1개 이상의 폴더를 추가해주세요.')
      return
    }

    // 폴더 경로만 추출 (scanning 상태 제외)
    const folderPaths = scanFolders.value.map(folder => folder.path)

    // API 호출로 서버에 저장
    await configApi.updateSection('folders', {
      scanFolders: folderPaths
    })

    await alert.success('폴더 설정이 저장되었습니다.')
  } catch (error) {
    console.error('폴더 저장 오류:', error)
    const errorMessage = error.response?.data?.detail || error.message || '폴더 설정 저장에 실패했습니다.'
    await alert.error(`저장 실패: ${errorMessage}`)
  }
}

// 이모지 선택 함수
const selectEmoji = (mode, emoji) => {
  if (mode === 'add') {
    newCategory.value.icon = emoji
  } else {
    editingCategory.value.icon = emoji
  }
}

// 카테고리명 입력 시 자동으로 이모지 추천
const autoSuggestIcon = (mode) => {
  const categoryName = mode === 'add' ? newCategory.value.name : editingCategory.value.name
  if (!categoryName) return

  const lowerName = categoryName.toLowerCase()

  // 정확히 일치하는 이모지 찾기
  if (categoryIconMap[lowerName]) {
    if (mode === 'add') {
      newCategory.value.icon = categoryIconMap[lowerName]
    } else {
      editingCategory.value.icon = categoryIconMap[lowerName]
    }
    return
  }

  // 부분 일치하는 이모지 찾기
  for (const [key, icon] of Object.entries(categoryIconMap)) {
    if (lowerName.includes(key) || key.includes(lowerName)) {
      if (mode === 'add') {
        newCategory.value.icon = icon
      } else {
        editingCategory.value.icon = icon
      }
      return
    }
  }

  // 일치하는 이모지가 없으면 기본값
  if (mode === 'add' && !newCategory.value.icon) {
    newCategory.value.icon = '📦'
  } else if (mode === 'edit' && !editingCategory.value.icon) {
    editingCategory.value.icon = '📦'
  }
}

const addCategory = async () => {
  // 중복 체크
  if (categories.value.some(c => c.name === newCategory.value.name)) {
    await alert.warning('이미 존재하는 카테고리명입니다.')
    return
  }

  categories.value.push({ ...newCategory.value })
  showAddCategoryModal.value = false
  newCategory.value = { name: '', label: '', icon: '' }
}

const closeAddCategoryModal = () => {
  showAddCategoryModal.value = false
  newCategory.value = { name: '', label: '', icon: '' }
}

const openEditCategoryModal = (category) => {
  editingCategory.value = {
    oldName: category.name,
    name: category.name,
    label: category.label,
    icon: category.icon
  }
  showEditCategoryModal.value = true
}

const updateCategory = async () => {
  // 중복 체크 (자신 제외)
  if (editingCategory.value.name !== editingCategory.value.oldName) {
    if (categories.value.some(c => c.name === editingCategory.value.name)) {
      await alert.warning('이미 존재하는 카테고리명입니다.')
      return
    }
  }

  const index = categories.value.findIndex(c => c.name === editingCategory.value.oldName)
  if (index !== -1) {
    categories.value[index] = {
      name: editingCategory.value.name,
      label: editingCategory.value.label,
      icon: editingCategory.value.icon
    }
  }
  closeEditCategoryModal()
}

const closeEditCategoryModal = () => {
  showEditCategoryModal.value = false
  editingCategory.value = { oldName: '', name: '', label: '', icon: '' }
}

const deleteCategory = async (category) => {
  const shouldDelete = await confirm.danger(`${category.label} 카테고리를 삭제하시겠습니까?`, '카테고리 삭제')
  if (shouldDelete) {
    categories.value = categories.value.filter(c => c.name !== category.name)
  }
}

// 일반 설정 저장
const saveGeneralSettings = async () => {
  try {
    const data = {
      language: language.value,
      accessUrl: accessUrl.value,
      apiUrl: apiUrl.value
    }

    await configApi.updateSection('general', data)
    await alert.success('일반 설정이 저장되었습니다.')
    console.log('일반 설정 저장 성공:', data)
  } catch (error) {
    console.error('일반 설정 저장 실패:', error)
    await alert.error('일반 설정 저장에 실패했습니다.')
  }
}

// 카테고리 설정 저장
const saveCategories = async () => {
  try {
    await configApi.updateSection('categories', categories.value)
    await alert.success('카테고리 설정이 저장되었습니다.')
    console.log('카테고리 설정 저장 성공:', categories.value)
  } catch (error) {
    console.error('카테고리 설정 저장 실패:', error)
    await alert.error('카테고리 설정 저장에 실패했습니다.')
  }
}

// 메타데이터 설정 저장
const saveMetadataSettings = async () => {
  try {
    const data = {
      scanMethod: scanMethod.value,
      aiProvider: aiProvider.value,
      aiModel: aiModel.value,
      geminiApiKey: geminiApiKey.value,
      openaiApiKey: openaiApiKey.value,
      googleApiKey: googleApiKey.value,
      googleSearchEngineId: googleSearchEngineId.value,
      useCustomPrompt: useCustomPrompt.value,
      customPromptOpenai: customPromptOpenai.value,
      customPromptGemini: customPromptGemini.value
    }

    await configApi.updateSection('metadata', data)
    await alert.success('메타데이터 설정이 저장되었습니다.')
    console.log('메타데이터 설정 저장 성공')
  } catch (error) {
    console.error('메타데이터 설정 저장 실패:', error)
    await alert.error('메타데이터 설정 저장에 실패했습니다.')
  }
}

// 게시판 카테고리 스타일 (Tips.vue와 동일)
const getBoardCategoryStyle = (color) => {
  const colorMap = {
    green: 'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300',
    blue: 'bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300',
    purple: 'bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-300',
    yellow: 'bg-yellow-100 dark:bg-yellow-900/50 text-yellow-800 dark:text-yellow-300',
    red: 'bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-300',
    pink: 'bg-pink-100 dark:bg-pink-900/50 text-pink-800 dark:text-pink-300',
    orange: 'bg-orange-100 dark:bg-orange-900/50 text-orange-800 dark:text-orange-300',
    indigo: 'bg-indigo-100 dark:bg-indigo-900/50 text-indigo-800 dark:text-indigo-300'
  }
  return `inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${colorMap[color] || colorMap.blue}`
}

// 게시판 카테고리 색상 (구버전 - 제거 가능)
const getBoardCategoryColor = (value) => {
  const colors = {
    tip: 'bg-green-500',
    tech: 'bg-blue-500',
    tutorial: 'bg-purple-500',
    qna: 'bg-yellow-500',
    news: 'bg-red-500'
  }
  return colors[value] || 'bg-gray-500'
}

// 게시판 카테고리 추가
const addBoardCategory = async () => {
  // 중복 체크
  if (boardCategories.value.some(c => c.value === newBoardCategory.value.value)) {
    await alert.warning('이미 존재하는 카테고리값입니다.')
    return
  }

  boardCategories.value.push({ ...newBoardCategory.value })
  closeAddBoardCategoryModal()
}

const closeAddBoardCategoryModal = () => {
  showAddBoardCategoryModal.value = false
  newBoardCategory.value = { value: '', label: '', color: 'blue' }
}

// 게시판 카테고리 수정
const openEditBoardCategoryModal = (category) => {
  editingBoardCategory.value = {
    oldValue: category.value,
    value: category.value,
    label: category.label,
    color: category.color || 'blue'
  }
  showEditBoardCategoryModal.value = true
}

const updateBoardCategory = async () => {
  // 중복 체크 (자신 제외)
  if (editingBoardCategory.value.value !== editingBoardCategory.value.oldValue) {
    if (boardCategories.value.some(c => c.value === editingBoardCategory.value.value)) {
      await alert.warning('이미 존재하는 카테고리값입니다.')
      return
    }
  }

  const index = boardCategories.value.findIndex(c => c.value === editingBoardCategory.value.oldValue)
  if (index !== -1) {
    boardCategories.value[index] = {
      value: editingBoardCategory.value.value,
      label: editingBoardCategory.value.label,
      color: editingBoardCategory.value.color || 'blue'
    }
  }
  closeEditBoardCategoryModal()
}

const closeEditBoardCategoryModal = () => {
  showEditBoardCategoryModal.value = false
  editingBoardCategory.value = { oldValue: '', value: '', label: '', color: 'blue' }
}

// 게시판 카테고리 삭제
const deleteBoardCategory = async (category) => {
  const shouldDelete = await confirm.danger(`${category.label} 카테고리를 삭제하시겠습니까?`, '카테고리 삭제')
  if (shouldDelete) {
    boardCategories.value = boardCategories.value.filter(c => c.value !== category.value)
  }
}

// 게시판 설정 저장
const saveBoardSettings = async () => {
  try {
    const data = {
      categories: boardCategories.value,
      postsPerPage: postsPerPage.value,
      allowComments: allowComments.value,
      allowAttachments: allowAttachments.value
    }

    await configApi.updateSection('board', data)

    // localStorage에도 저장 (TipsWrite, TipsDetail에서 사용)
    localStorage.setItem('boardSettings', JSON.stringify(data))

    await alert.success('게시판 설정이 저장되었습니다.')
    console.log('게시판 설정 저장 성공:', data)
  } catch (error) {
    console.error('게시판 설정 저장 실패:', error)
    await alert.error('게시판 설정 저장에 실패했습니다.')
  }
}

// 페이지 로드 시 저장된 설정 불러오기
onMounted(async () => {
  try {
    // URL 쿼리 파라미터에서 섹션 확인
    const section = route.query.section
    if (section && sections.some(s => s.id === section)) {
      activeSection.value = section
    }

    // 사용자 목록 로드
    await loadUsers()

    // 스캔 예외 설정 로드
    await loadExceptionSettings()

    // config.json에서 모든 설정 로드
    const response = await configApi.getConfig()
    const config = response.data

    // 일반 설정
    if (config.general) {
      language.value = config.general.language || 'ko'
      accessUrl.value = config.general.accessUrl || 'http://localhost:5900'
      apiUrl.value = config.general.apiUrl || 'http://localhost:8100'
    }

    // 폴더 설정
    if (config.folders && config.folders.scanFolders && config.folders.scanFolders.length > 0) {
      scanFolders.value = config.folders.scanFolders.map(path => ({ path, scanning: false }))
    } else {
      // 설정이 없으면 기본 경로 사용
      scanFolders.value = [{ path: defaultLibraryPath, scanning: false }]
    }

    // 카테고리 설정
    if (config.categories && Array.isArray(config.categories)) {
      categories.value = config.categories

      // Font 카테고리가 없으면 추가 (신규 카테고리)
      if (!categories.value.find(c => c.name === 'Font')) {
        const uncategorizedIndex = categories.value.findIndex(c => c.name === 'Uncategorized')
        if (uncategorizedIndex !== -1) {
          // Uncategorized 앞에 삽입
          categories.value.splice(uncategorizedIndex, 0, { name: 'Font', label: '글꼴', icon: '🔤' })
        } else {
          // Uncategorized가 없으면 끝에 추가
          categories.value.push({ name: 'Font', label: '글꼴', icon: '🔤' })
        }
      }
    }

    // 메타데이터 설정
    if (config.metadata) {
      scanMethod.value = config.metadata.scanMethod || 'ai'
      aiProvider.value = config.metadata.aiProvider || 'gemini'
      aiModel.value = config.metadata.aiModel || 'gemini-2.5-flash'
      geminiApiKey.value = config.metadata.geminiApiKey || ''
      openaiApiKey.value = config.metadata.openaiApiKey || ''
      googleApiKey.value = config.metadata.googleApiKey || ''
      googleSearchEngineId.value = config.metadata.googleSearchEngineId || ''
      useCustomPrompt.value = config.metadata.useCustomPrompt || false
      customPromptOpenai.value = config.metadata.customPromptOpenai || defaultPromptOpenai
      customPromptGemini.value = config.metadata.customPromptGemini || defaultPromptGemini
    }

    // 게시판 설정
    if (config.board) {
      if (config.board.categories) boardCategories.value = config.board.categories
      if (config.board.postsPerPage) postsPerPage.value = config.board.postsPerPage
      if (config.board.allowComments !== undefined) allowComments.value = config.board.allowComments
      if (config.board.allowAttachments !== undefined) allowAttachments.value = config.board.allowAttachments

      // localStorage에도 저장 (TipsWrite, TipsDetail에서 사용)
      localStorage.setItem('boardSettings', JSON.stringify(config.board))
    }

    console.log('설정 로드 완료:', config)
  } catch (error) {
    console.error('설정 로드 실패:', error)

    // Fallback: localStorage에서 게시판 설정 로드
    const savedSettings = localStorage.getItem('boardSettings')
    if (savedSettings) {
      const settings = JSON.parse(savedSettings)
      if (settings.categories) boardCategories.value = settings.categories
      if (settings.postsPerPage) postsPerPage.value = settings.postsPerPage
      if (settings.allowComments !== undefined) allowComments.value = settings.allowComments
      if (settings.allowAttachments !== undefined) allowAttachments.value = settings.allowAttachments
    }
  }
})

// Watch activeSection for cache
watch(activeSection, (newSection) => {
  if (newSection === 'cache' && isAdmin.value) {
    loadCacheStats()
  }
})

// Load cache stats on mount if cache section is active
onMounted(() => {
  if (activeSection.value === 'cache' && isAdmin.value) {
    loadCacheStats()
  }
})
</script>
