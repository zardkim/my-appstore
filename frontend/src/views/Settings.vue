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
                  <option value="ko">🇰🇷 {{ t('settings.general.korean') }}</option>
                  <option value="en">🇺🇸 {{ t('settings.general.english') }}</option>
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
                {{ t('settings.users.addUser') }}
              </button>
            </div>
          </div>

          <div v-if="!isAdmin" class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-2xl p-6">
            <div class="flex items-start">
              <svg class="w-6 h-6 text-yellow-600 dark:text-yellow-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
              <div>
                <h3 class="text-sm font-semibold text-yellow-800 dark:text-yellow-400">{{ t('settings.users.adminRequired') }}</h3>
                <p class="text-sm text-yellow-700 dark:text-yellow-300 mt-1">{{ t('settings.users.adminOnlyAccess') }}</p>
              </div>
            </div>
          </div>

          <!-- Registration Settings -->
          <div v-if="isAdmin" class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-4 sm:p-6 border border-gray-100 dark:border-gray-700">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div class="min-w-0">
                <h3 class="text-sm sm:text-base font-bold text-gray-900 dark:text-white flex items-center">
                  <svg class="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2 text-blue-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                  </svg>
                  {{ t('settings.users.registrationSettings') }}
                </h3>
                <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-0.5 sm:mt-1">{{ t('settings.users.registrationSettingsDesc') }}</p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer flex-shrink-0">
                <input
                  type="checkbox"
                  v-model="registrationOpen"
                  @change="toggleRegistration"
                  class="sr-only peer"
                />
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                <span class="ml-3 text-sm font-medium whitespace-nowrap" :class="registrationOpen ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'">
                  {{ registrationOpen ? t('settings.users.registrationOpen') : t('settings.users.registrationClosed') }}
                </span>
              </label>
            </div>
          </div>

          <!-- Desktop Table View -->
          <div v-if="isAdmin" class="hidden md:block bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
            <table class="w-full">
              <thead class="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">{{ t('settings.users.username') }}</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">{{ t('settings.users.role') }}</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">{{ t('settings.users.status') }}</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">{{ t('settings.users.createdAt') }}</th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">{{ t('settings.users.actions') }}</th>
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
                      {{ t('settings.users.admin') }}
                    </span>
                    <span v-else class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">{{ t('settings.users.normalUser') }}</span>
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
                      <button v-if="user.role !== 'admin'" @click="openEditUserModal(user)" class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium text-sm">{{ t('settings.users.edit') }}</button>
                      <button v-if="user.role !== 'admin'" @click="openPasswordModal(user)" class="text-purple-600 dark:text-purple-400 hover:text-purple-800 dark:hover:text-purple-300 font-medium text-sm">{{ t('settings.users.password') }}</button>
                      <button v-if="user.role !== 'admin'" @click="deleteUser(user)" class="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 font-medium text-sm">{{ t('settings.users.delete') }}</button>
                      <span v-else class="text-gray-400 dark:text-gray-500 text-sm">{{ t('settings.users.systemAdmin') }}</span>
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
                  <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">{{ t('settings.users.role') }}</p>
                  <span v-if="user.role === 'admin'" class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gradient-to-r from-blue-500 to-purple-600 text-white">
                    <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
                    {{ t('settings.users.admin') }}
                  </span>
                  <span v-else class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">{{ t('settings.users.normalUser') }}</span>
                </div>
                <div>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mb-1 text-right">{{ t('settings.users.status') }}</p>
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
                <button @click="openEditUserModal(user)" class="flex-1 px-3 py-2 text-sm text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 font-medium transition-colors">{{ t('settings.users.edit') }}</button>
                <button @click="openPasswordModal(user)" class="flex-1 px-3 py-2 text-sm text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/30 font-medium transition-colors">{{ t('settings.users.password') }}</button>
                <button @click="deleteUser(user)" class="flex-1 px-3 py-2 text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 font-medium transition-colors">{{ t('settings.users.delete') }}</button>
              </div>
              <div v-else class="text-center py-2">
                <span class="text-xs text-gray-500 dark:text-gray-400">{{ t('settings.users.systemAdmin') }}</span>
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
            <div v-for="(folder, index) in scanFolders" :key="index" class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-3 sm:p-4 border border-gray-100 dark:border-gray-700">
              <!-- 모바일: 세로 배치 / 데스크탑: 가로 배치 -->
              <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-0">
                <!-- 폴더 경로 -->
                <div class="flex items-center flex-1 min-w-0">
                  <svg class="w-5 h-5 text-blue-500 dark:text-blue-400 mr-2 sm:mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" /></svg>
                  <p class="text-xs sm:text-sm font-mono text-gray-900 dark:text-white truncate">{{ folder.path }}</p>
                  <span v-if="folder.path === defaultLibraryPath" class="ml-2 px-2 py-0.5 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full flex-shrink-0">{{ t('settings.folders.default') }}</span>
                </div>
                <!-- 버튼 그룹 -->
                <div class="flex items-center gap-1 sm:gap-0 pl-7 sm:pl-0">
                  <button
                    @click="scanFolder(folder.path)"
                    :disabled="folder.scanning"
                    class="px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm text-green-600 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg transition-colors flex-shrink-0 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                    :title="t('settings.folders.scanThisFolder')"
                  >
                    <svg v-if="!folder.scanning" class="w-3.5 h-3.5 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    <svg v-else class="w-3.5 h-3.5 sm:w-4 sm:h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    {{ folder.scanning ? t('settings.folders.scanning') : t('settings.folders.scan') }}
                  </button>
                  <button
                    v-if="folder.path !== defaultLibraryPath"
                    @click="editFolder(index)"
                    class="px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors flex-shrink-0"
                  >
                    {{ t('settings.folders.change') }}
                  </button>
                  <button
                    v-if="folder.path !== defaultLibraryPath"
                    @click="removeFolder(index)"
                    class="p-1.5 sm:p-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors flex-shrink-0"
                  >
                    <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                  </button>
                  <div
                    v-if="folder.path === defaultLibraryPath"
                    class="p-1.5 sm:p-2 text-gray-400 dark:text-gray-600 cursor-not-allowed flex-shrink-0"
                    :title="t('settings.folders.cannotDeleteDefault')"
                  >
                    <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
                  </div>
                </div>
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

        <!-- Auto Scan Scheduler -->
        <div v-show="activeSection === 'scheduler'" class="space-y-4 sm:space-y-6">
          <div>
            <h1 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-1 sm:mb-2">{{ t('settings.scheduler.title') }}</h1>
            <p class="text-sm sm:text-base text-gray-500 dark:text-gray-400">{{ t('settings.scheduler.description') }}</p>
          </div>

          <div v-if="!isAdmin" class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-2xl p-6">
            <p class="text-sm text-yellow-700 dark:text-yellow-300">{{ t('settings.scheduler.adminOnly') }}</p>
          </div>

          <AdminScheduler v-else />
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
              <p class="font-medium text-gray-900 dark:text-white">{{ getCategoryLabel(category) }}</p>
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
                  <option value="10">{{ t('settings.board.postsPerPageOption', { n: 10 }) }}</option>
                  <option value="20">{{ t('settings.board.postsPerPageOption', { n: 20 }) }}</option>
                  <option value="30">{{ t('settings.board.postsPerPageOption', { n: 30 }) }}</option>
                  <option value="50">{{ t('settings.board.postsPerPageOption', { n: 50 }) }}</option>
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
        <!-- Filing Rules -->
        <div v-show="activeSection === 'filing-rules'" class="space-y-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">{{ t('settings.filingRules.title') }}</h1>
            <p class="text-gray-500 dark:text-gray-400">{{ t('settings.filingRules.description') }}</p>
          </div>

          <!-- 개요 -->
          <div class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-2xl p-6 border border-blue-200 dark:border-blue-700">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-3 flex items-center">
              {{ t('settings.filingRules.overview') }}
            </h2>
            <p class="text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.overviewDesc') }}</p>
          </div>

          <!-- 규칙 1: 구분자 자동 인식 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.filingRules.rule1Title') }}</h2>
            <p class="text-gray-600 dark:text-gray-400 mb-4">{{ t('settings.filingRules.rule1Desc') }}</p>

            <div class="mb-4">
              <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.filingRules.rule1Supported') }}</p>
              <div class="grid grid-cols-2 md:grid-cols-5 gap-2">
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-2 text-center">
                  <span class="text-sm text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.rule1Space') }}</span>
                </div>
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-2 text-center">
                  <span class="text-sm text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.rule1Underscore') }}</span>
                </div>
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-2 text-center">
                  <span class="text-sm text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.rule1Dot') }}</span>
                </div>
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-2 text-center">
                  <span class="text-sm text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.rule1Hyphen') }}</span>
                </div>
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-2 text-center">
                  <span class="text-sm text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.rule1Mixed') }}</span>
                </div>
              </div>
            </div>

            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-700">
              <p class="text-sm font-semibold text-green-800 dark:text-green-300 mb-2">{{ t('settings.filingRules.rule1Examples') }}</p>
              <div class="space-y-1 text-xs font-mono">
                <div class="text-gray-700 dark:text-gray-300">✓ Total Commander 10.51.zip</div>
                <div class="text-gray-700 dark:text-gray-300">✓ Total_Commander_10.51.zip</div>
                <div class="text-gray-700 dark:text-gray-300">✓ EaseUS Partition Master 15.8 Multilingual.zip</div>
                <div class="text-gray-700 dark:text-gray-300">✓ Macrium_Reflect_7.3.5854_Server_Plus_x64.rar</div>
              </div>
            </div>
          </div>

          <!-- 규칙 2: 버전 패턴 자동 인식 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.filingRules.rule2Title') }}</h2>
            <p class="text-gray-600 dark:text-gray-400 mb-4">{{ t('settings.filingRules.rule2Desc') }}</p>

            <div class="mb-4">
              <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.filingRules.rule2Patterns') }}</p>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-2 font-mono text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.rule2Pattern1') }}</div>
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-2 font-mono text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.rule2Pattern2') }}</div>
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-2 font-mono text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.rule2Pattern3') }}</div>
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-2 font-mono text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.rule2Pattern4') }}</div>
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-2 font-mono text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.rule2Pattern5') }}</div>
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-2 font-mono text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.rule2Pattern6') }}</div>
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-2 font-mono text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.rule2Pattern7') }}</div>
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-2 font-mono text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.rule2Pattern8') }}</div>
              </div>
            </div>

            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-700">
              <p class="text-sm font-semibold text-green-800 dark:text-green-300 mb-2">{{ t('settings.filingRules.rule2NasExamples') }}</p>
              <div class="space-y-1 text-xs font-mono">
                <div class="text-gray-700 dark:text-gray-300">Total Commander v10.51 → 버전: 10.51</div>
                <div class="text-gray-700 dark:text-gray-300">Adobe Photoshop 2024 v25.0 → 제품년도: 2024, 버전: v25.0</div>
                <div class="text-gray-700 dark:text-gray-300">Microsoft Office 2016-2019 → 버전: 2016-2019</div>
                <div class="text-gray-700 dark:text-gray-300">Java Runtime Environment 7 Update 45 → 버전: 7 Update 45</div>
              </div>
            </div>
          </div>

          <!-- 규칙 3: 제품명 유연 추출 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.filingRules.rule3Title') }}</h2>
            <p class="text-gray-600 dark:text-gray-400 mb-4">{{ t('settings.filingRules.rule3Desc') }}</p>

            <div class="mb-4">
              <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.filingRules.rule3Methods') }}</p>
              <ul class="list-disc list-inside space-y-1 text-sm text-gray-600 dark:text-gray-400">
                <li>{{ t('settings.filingRules.rule3Method1') }}</li>
                <li>{{ t('settings.filingRules.rule3Method2') }}</li>
                <li>{{ t('settings.filingRules.rule3Method3') }}</li>
              </ul>
            </div>

            <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-700">
              <p class="text-sm font-semibold text-purple-800 dark:text-purple-300 mb-2">{{ t('settings.filingRules.rule3Example1') }}</p>
              <div class="space-y-1 text-xs">
                <div class="text-gray-600 dark:text-gray-400">{{ t('settings.filingRules.rule3Example1Folder') }}</div>
                <div class="text-gray-600 dark:text-gray-400">{{ t('settings.filingRules.rule3Example1File') }}</div>
                <div class="font-semibold text-purple-700 dark:text-purple-300">{{ t('settings.filingRules.rule3Example1Result') }}</div>
              </div>
            </div>
          </div>

          <!-- 규칙 4: 부가정보 자동 태깅 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.filingRules.rule4Title') }}</h2>
            <p class="text-gray-600 dark:text-gray-400 mb-4">{{ t('settings.filingRules.rule4Desc') }}</p>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">🖥️ {{ t('settings.filingRules.rule4Architecture') }}</p>
                <p class="text-xs text-gray-600 dark:text-gray-400">{{ t('settings.filingRules.rule4ArchKeywords') }}</p>
              </div>
              <div>
                <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">⭐ {{ t('settings.filingRules.rule4Edition') }}</p>
                <p class="text-xs text-gray-600 dark:text-gray-400">{{ t('settings.filingRules.rule4EditionKeywords') }}</p>
              </div>
              <div>
                <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">🌐 {{ t('settings.filingRules.rule4Language') }}</p>
                <p class="text-xs text-gray-600 dark:text-gray-400">{{ t('settings.filingRules.rule4LanguageKeywords') }}</p>
              </div>
              <div>
                <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">📦 {{ t('settings.filingRules.rule4Packaging') }}</p>
                <p class="text-xs text-gray-600 dark:text-gray-400">{{ t('settings.filingRules.rule4PackagingKeywords') }}</p>
              </div>
              <div class="md:col-span-2">
                <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">🔖 {{ t('settings.filingRules.rule4Others') }}</p>
                <p class="text-xs text-gray-600 dark:text-gray-400">{{ t('settings.filingRules.rule4OthersKeywords') }}</p>
              </div>
            </div>

            <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 border border-yellow-200 dark:border-yellow-700">
              <p class="text-sm font-semibold text-yellow-800 dark:text-yellow-300 mb-2">{{ t('settings.filingRules.rule4Example') }}</p>
              <div class="space-y-2 text-xs font-mono">
                <div class="text-gray-700 dark:text-gray-300">
                  Total_Commander_10.51_Final_with_Key_x64.zip<br>
                  <span class="text-yellow-700 dark:text-yellow-400">→ 제품: Total Commander | 버전: 10.51 | 태그: Final, With Key, x64</span>
                </div>
                <div class="text-gray-700 dark:text-gray-300">
                  Adobe Photoshop 2024 v25.0 x64 Multilingual Portable.exe<br>
                  <span class="text-yellow-700 dark:text-yellow-400">→ 제품: Adobe Photoshop 2024 | 버전: v25.0 | 태그: x64, Multilingual, Portable</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 규칙 5: 불명확한 파일명 처리 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.filingRules.rule5Title') }}</h2>
            <p class="text-gray-600 dark:text-gray-400 mb-4">{{ t('settings.filingRules.rule5Desc') }}</p>

            <div class="space-y-3">
              <div class="border-l-4 border-blue-500 pl-4">
                <p class="text-sm font-semibold text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.rule5Case1') }}</p>
                <p class="text-xs text-gray-600 dark:text-gray-400">{{ t('settings.filingRules.rule5Case1Desc') }}</p>
              </div>
              <div class="border-l-4 border-green-500 pl-4">
                <p class="text-sm font-semibold text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.rule5Case2') }}</p>
                <p class="text-xs text-gray-600 dark:text-gray-400">{{ t('settings.filingRules.rule5Case2Desc') }}</p>
              </div>
              <div class="border-l-4 border-purple-500 pl-4">
                <p class="text-sm font-semibold text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.rule5Case3') }}</p>
                <p class="text-xs text-gray-600 dark:text-gray-400">{{ t('settings.filingRules.rule5Case3Desc') }}</p>
              </div>
              <div class="border-l-4 border-orange-500 pl-4">
                <p class="text-sm font-semibold text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.rule5Case4') }}</p>
                <p class="text-xs text-gray-600 dark:text-gray-400">{{ t('settings.filingRules.rule5Case4Desc') }}</p>
              </div>
            </div>
          </div>

          <!-- 인식 예제 모음 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.filingRules.recognitionExamples') }}</h2>
            <p class="text-gray-600 dark:text-gray-400 mb-4">{{ t('settings.filingRules.recognitionExamplesDesc') }}</p>

            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead class="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th class="px-4 py-2 text-left text-xs font-semibold text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.beforeLabel') }}</th>
                    <th class="px-4 py-2 text-left text-xs font-semibold text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.afterLabel') }}</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 dark:divide-gray-600">
                  <tr>
                    <td class="px-4 py-2 font-mono text-xs text-gray-700 dark:text-gray-300">Total_Commander_10.51_Final_with_Key_x64.zip</td>
                    <td class="px-4 py-2 text-xs text-green-700 dark:text-green-400">Total Commander v10.51 x64 Final</td>
                  </tr>
                  <tr>
                    <td class="px-4 py-2 font-mono text-xs text-gray-700 dark:text-gray-300">EaseUS_Partition_Master_15.8_Multilingual.zip</td>
                    <td class="px-4 py-2 text-xs text-green-700 dark:text-green-400">EaseUS Partition Master v15.8 Multilingual</td>
                  </tr>
                  <tr>
                    <td class="px-4 py-2 font-mono text-xs text-gray-700 dark:text-gray-300">Macrium_Reflect_7.3.5854_Server_Plus_x64.rar</td>
                    <td class="px-4 py-2 text-xs text-green-700 dark:text-green-400">Macrium Reflect v7.3 x64 Server Plus</td>
                  </tr>
                  <tr>
                    <td class="px-4 py-2 font-mono text-xs text-gray-700 dark:text-gray-300">Microsoft.Office.2016-2019x64.v2020.10.iso</td>
                    <td class="px-4 py-2 text-xs text-green-700 dark:text-green-400">Microsoft Office 2016-2019 x64 v2020.10</td>
                  </tr>
                  <tr>
                    <td class="px-4 py-2 font-mono text-xs text-gray-700 dark:text-gray-300">ko_office_professional_plus_2013_x64.iso</td>
                    <td class="px-4 py-2 text-xs text-green-700 dark:text-green-400">Office Professional Plus 2013 x64 Korean</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 권장사항 -->
          <div class="bg-blue-50 dark:bg-blue-900/20 rounded-2xl p-6 border border-blue-200 dark:border-blue-700">
            <h2 class="text-xl font-bold text-blue-900 dark:text-blue-300 mb-4">{{ t('settings.filingRules.recommendations') }}</h2>
            <p class="text-gray-700 dark:text-gray-300 mb-4">{{ t('settings.filingRules.recommendationsDesc') }}</p>

            <ul class="list-disc list-inside space-y-2 mb-4 text-sm text-gray-700 dark:text-gray-300">
              <li>{{ t('settings.filingRules.rec1') }}</li>
              <li>{{ t('settings.filingRules.rec2') }}</li>
              <li>{{ t('settings.filingRules.rec3') }}</li>
              <li>{{ t('settings.filingRules.rec4') }}</li>
            </ul>

            <div class="bg-white dark:bg-gray-800 rounded-lg p-4">
              <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.filingRules.recExample') }}</p>
              <div class="space-y-1 text-xs font-mono">
                <div class="text-green-600 dark:text-green-400">{{ t('settings.filingRules.recExampleGood') }}</div>
                <div class="text-red-600 dark:text-red-400">{{ t('settings.filingRules.recExampleBad') }}</div>
              </div>
              <p class="text-xs text-gray-600 dark:text-gray-400 mt-2">{{ t('settings.filingRules.recNote') }}</p>
            </div>
          </div>

          <!-- 문제 해결 -->
          <div class="bg-orange-50 dark:bg-orange-900/20 rounded-2xl p-6 border border-orange-200 dark:border-orange-700">
            <h2 class="text-xl font-bold text-orange-900 dark:text-orange-300 mb-4">{{ t('settings.filingRules.troubleshooting') }}</h2>
            <ul class="space-y-2 text-sm text-gray-700 dark:text-gray-300">
              <li>• {{ t('settings.filingRules.trouble1') }}</li>
              <li>• {{ t('settings.filingRules.trouble2') }}</li>
              <li>• {{ t('settings.filingRules.trouble3') }}</li>
              <li>• {{ t('settings.filingRules.trouble4') }}</li>
            </ul>
          </div>

          <!-- 요약 -->
          <div class="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-2xl p-6 border border-green-200 dark:border-green-700">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.filingRules.summary') }}</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <div class="flex items-start">
                <span class="text-green-600 dark:text-green-400 mr-2">✓</span>
                <span class="text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.summaryPoint1') }}</span>
              </div>
              <div class="flex items-start">
                <span class="text-green-600 dark:text-green-400 mr-2">✓</span>
                <span class="text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.summaryPoint2') }}</span>
              </div>
              <div class="flex items-start">
                <span class="text-green-600 dark:text-green-400 mr-2">✓</span>
                <span class="text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.summaryPoint3') }}</span>
              </div>
              <div class="flex items-start">
                <span class="text-green-600 dark:text-green-400 mr-2">✓</span>
                <span class="text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.summaryPoint4') }}</span>
              </div>
              <div class="flex items-start md:col-span-2">
                <span class="text-green-600 dark:text-green-400 mr-2">✓</span>
                <span class="text-gray-700 dark:text-gray-300">{{ t('settings.filingRules.summaryPoint5') }}</span>
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
                  <optgroup :label="t('settings.metadata.openaiGroupO1')">
                    <option value="o1">{{ t('settings.metadata.openaiO1') }}</option>
                    <option value="o1-preview">{{ t('settings.metadata.openaiO1Preview') }}</option>
                    <option value="o1-mini">{{ t('settings.metadata.openaiO1Mini') }}</option>
                  </optgroup>
                  <optgroup :label="t('settings.metadata.openaiGroupGpt4o')">
                    <option value="gpt-4o-mini">{{ t('settings.metadata.openaiGpt4oMini') }}</option>
                    <option value="gpt-4o">{{ t('settings.metadata.openaiGpt4o') }}</option>
                    <option value="gpt-4o-2024-11-20">{{ t('settings.metadata.openaiGpt4oDate1') }}</option>
                    <option value="gpt-4o-2024-08-06">{{ t('settings.metadata.openaiGpt4oDate2') }}</option>
                    <option value="gpt-4o-2024-05-13">{{ t('settings.metadata.openaiGpt4oDate3') }}</option>
                  </optgroup>
                  <optgroup :label="t('settings.metadata.openaiGroupGpt4Turbo')">
                    <option value="gpt-4-turbo">{{ t('settings.metadata.openaiGpt4Turbo') }}</option>
                    <option value="gpt-4-turbo-2024-04-09">{{ t('settings.metadata.openaiGpt4TurboDate') }}</option>
                    <option value="gpt-4-turbo-preview">{{ t('settings.metadata.openaiGpt4TurboPreview') }}</option>
                  </optgroup>
                  <optgroup :label="t('settings.metadata.openaiGroupGpt4')">
                    <option value="gpt-4">{{ t('settings.metadata.openaiGpt4') }}</option>
                    <option value="gpt-4-0613">{{ t('settings.metadata.openaiGpt4Date') }}</option>
                  </optgroup>
                </select>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  {{ t('settings.metadata.openaiModelTip') }}
                </p>
              </div>

              <!-- Gemini Models -->
              <div v-if="aiProvider === 'gemini'">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.metadata.geminiModel') }}</label>
                <select v-model="aiModel" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <optgroup :label="t('settings.metadata.geminiGroup3')">
                    <option value="gemini-3-flash-preview">{{ t('settings.metadata.gemini3FlashPreview') }}</option>
                    <option value="gemini-3-pro-preview">{{ t('settings.metadata.gemini3ProPreview') }}</option>
                  </optgroup>
                  <optgroup :label="t('settings.metadata.geminiGroup25')">
                    <option value="gemini-2.5-flash">{{ t('settings.metadata.gemini25Flash') }}</option>
                    <option value="gemini-2.5-pro">{{ t('settings.metadata.gemini25Pro') }}</option>
                    <option value="gemini-2.5-flash-lite">{{ t('settings.metadata.gemini25FlashLite') }}</option>
                  </optgroup>
                  <optgroup :label="t('settings.metadata.geminiGroup20')">
                    <option value="gemini-2.0-flash-exp">{{ t('settings.metadata.gemini20FlashExp') }}</option>
                    <option value="gemini-2.0-flash">{{ t('settings.metadata.gemini20Flash') }}</option>
                    <option value="gemini-2.0-flash-lite">{{ t('settings.metadata.gemini20FlashLite') }}</option>
                  </optgroup>
                </select>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  {{ t('settings.metadata.geminiModelTip') }}
                </p>
                <p class="text-xs text-orange-600 dark:text-orange-400 mt-1">
                  {{ t('settings.metadata.geminiQuotaWarning') }}
                </p>
              </div>

              <!-- Gemini API Key -->
              <div v-if="aiProvider === 'gemini'">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Gemini API 키
                  <span class="text-xs text-gray-500">(Google AI Studio API Key)</span>
                </label>
                <!-- 저장됨 상태 표시 (키가 있고 편집 모드가 아닐 때) -->
                <div v-if="hasGeminiKey && !editingGeminiKey" class="flex items-center gap-2">
                  <div class="flex-1 flex items-center gap-2 px-4 py-2 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-xl">
                    <svg class="w-4 h-4 text-green-600 dark:text-green-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span class="text-sm text-green-700 dark:text-green-400 font-mono tracking-widest">AIzaSy••••••••••••••••••••••••••••</span>
                  </div>
                  <button @click="editingGeminiKey = true; geminiApiKey = ''" type="button"
                    class="px-3 py-2 text-sm bg-yellow-500 hover:bg-yellow-600 text-white rounded-xl transition-colors whitespace-nowrap">
                    수정
                  </button>
                </div>
                <!-- 입력 모드 (키가 없거나 편집 중) -->
                <div v-else class="flex items-center gap-2">
                  <input
                    v-model="geminiApiKey"
                    type="password"
                    placeholder="AIzaSy..."
                    class="flex-1 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                  />
                  <button v-if="editingGeminiKey" @click="editingGeminiKey = false; geminiApiKey = ''" type="button"
                    class="px-3 py-2 text-sm bg-gray-500 hover:bg-gray-600 text-white rounded-xl transition-colors whitespace-nowrap">
                    취소
                  </button>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  Gemini API 키는 https://aistudio.google.com/apikey 에서 발급받을 수 있습니다.
                  <span v-if="hasGeminiKey && !editingGeminiKey" class="text-green-600 dark:text-green-400">• 저장됨</span>
                </p>
              </div>

              <!-- OpenAI API Key -->
              <div v-if="aiProvider === 'openai'">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  OpenAI API 키
                  <span class="text-xs text-gray-500">(OpenAI API Key)</span>
                </label>
                <!-- 저장됨 상태 표시 -->
                <div v-if="hasOpenaiKey && !editingOpenaiKey" class="flex items-center gap-2">
                  <div class="flex-1 flex items-center gap-2 px-4 py-2 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-xl">
                    <svg class="w-4 h-4 text-green-600 dark:text-green-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span class="text-sm text-green-700 dark:text-green-400 font-mono tracking-widest">sk-••••••••••••••••••••••••••••••</span>
                  </div>
                  <button @click="editingOpenaiKey = true; openaiApiKey = ''" type="button"
                    class="px-3 py-2 text-sm bg-yellow-500 hover:bg-yellow-600 text-white rounded-xl transition-colors whitespace-nowrap">
                    수정
                  </button>
                </div>
                <!-- 입력 모드 -->
                <div v-else class="flex items-center gap-2">
                  <input
                    v-model="openaiApiKey"
                    type="password"
                    placeholder="sk-..."
                    class="flex-1 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                  />
                  <button v-if="editingOpenaiKey" @click="editingOpenaiKey = false; openaiApiKey = ''" type="button"
                    class="px-3 py-2 text-sm bg-gray-500 hover:bg-gray-600 text-white rounded-xl transition-colors whitespace-nowrap">
                    취소
                  </button>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  OpenAI API 키는 https://platform.openai.com/api-keys 에서 발급받을 수 있습니다.
                  <span v-if="hasOpenaiKey && !editingOpenaiKey" class="text-green-600 dark:text-green-400">• 저장됨</span>
                </p>
              </div>

              <!-- Pricing Info -->
              <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-xl p-4">
                <h4 class="text-sm font-semibold text-blue-900 dark:text-blue-300 mb-2">{{ t('settings.metadata.pricingInfo') }}</h4>
                <div class="text-xs text-blue-800 dark:text-blue-400 space-y-1">
                  <p v-if="aiProvider === 'openai'">
                    <strong>{{ t('settings.metadata.openaiPricingTitle') }}</strong><br>
                    • {{ t('settings.metadata.openaiO1') }}<br>
                    • {{ t('settings.metadata.openaiGpt4oMini') }}<br>
                    • {{ t('settings.metadata.openaiGpt4o') }}<br>
                    • {{ t('settings.metadata.openaiGpt4Turbo') }}<br>
                    • {{ t('settings.metadata.openaiGpt4') }}
                  </p>
                  <p v-if="aiProvider === 'gemini'">
                    <strong>{{ t('settings.metadata.geminiPricingTitle') }}</strong><br>
                    • <strong class="text-green-600 dark:text-green-400">{{ t('settings.metadata.geminiFreeQuota') }}</strong><br>
                    • {{ t('settings.metadata.gemini30FlashExp') }}<br>
                    • {{ t('settings.metadata.gemini25FlashExp') }}<br>
                    • {{ t('settings.metadata.gemini25ProExp') }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Bing Image Search API Settings -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h3 class="text-lg font-bold text-gray-900 dark:text-white">{{ t('settings.metadata.bingImageSearchTitle') }}</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ t('settings.metadata.bingImageSearchDesc') }}</p>
              </div>
              <!-- ON/OFF 토글 -->
              <label class="flex items-center gap-2 cursor-pointer flex-shrink-0 ml-4">
                <span class="text-sm font-medium" :class="bingImageSearch ? 'text-blue-600 dark:text-blue-400' : 'text-gray-400 dark:text-gray-500'">
                  {{ bingImageSearch ? 'ON' : 'OFF' }}
                </span>
                <div class="relative">
                  <input type="checkbox" v-model="bingImageSearch" class="sr-only" />
                  <div class="w-12 h-6 rounded-full transition-colors duration-200"
                    :class="bingImageSearch ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600'">
                  </div>
                  <div class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform duration-200"
                    :class="bingImageSearch ? 'translate-x-6' : 'translate-x-0'">
                  </div>
                </div>
              </label>
            </div>

            <div v-if="bingImageSearch" class="space-y-4">
              <!-- Bing API Key -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ t('settings.metadata.bingApiKeyLabel') }}
                  <span class="text-xs text-gray-500">{{ t('settings.metadata.bingApiKeySubLabel') }}</span>
                </label>
                <!-- 저장됨 상태 표시 -->
                <div v-if="hasBingKey && !editingBingKey" class="flex items-center gap-2">
                  <div class="flex-1 flex items-center gap-2 px-4 py-2 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-xl">
                    <svg class="w-4 h-4 text-green-600 dark:text-green-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span class="text-sm text-green-700 dark:text-green-400 font-mono tracking-widest">••••••••••••••••••••••••••••••••</span>
                  </div>
                  <button @click="editingBingKey = true; bingApiKey = ''" type="button"
                    class="px-3 py-2 text-sm bg-yellow-500 hover:bg-yellow-600 text-white rounded-xl transition-colors whitespace-nowrap">
                    수정
                  </button>
                </div>
                <!-- 입력 모드 -->
                <div v-else class="flex items-center gap-2">
                  <input
                    v-model="bingApiKey"
                    type="password"
                    :placeholder="t('settings.metadata.bingApiKeyPlaceholder')"
                    class="flex-1 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                  />
                  <button v-if="editingBingKey" @click="editingBingKey = false; bingApiKey = ''" type="button"
                    class="px-3 py-2 text-sm bg-gray-500 hover:bg-gray-600 text-white rounded-xl transition-colors whitespace-nowrap">
                    취소
                  </button>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  {{ t('settings.metadata.bingApiKeyHelper') }}
                  <a href="https://portal.azure.com/" target="_blank" class="text-blue-600 dark:text-blue-400 hover:underline">
                    {{ t('settings.metadata.bingApiKeyLink') }}
                  </a>
                </p>
              </div>

              <!-- Info Box -->
              <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-xl p-4">
                <h4 class="text-sm font-semibold text-blue-900 dark:text-blue-300 mb-2">{{ t('settings.metadata.bingSetupGuideTitle') }}</h4>
                <div class="text-xs text-blue-800 dark:text-blue-400 space-y-1">
                  <p>{{ t('settings.metadata.bingSetupStep1') }}</p>
                  <p>{{ t('settings.metadata.bingSetupStep2') }}</p>
                  <p>{{ t('settings.metadata.bingSetupStep3') }}</p>
                  <p class="mt-2">
                    <strong>{{ t('settings.metadata.bingFreeQuotaLabel') }}</strong> {{ t('settings.metadata.bingFreeQuotaValue') }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Custom Prompt Editor -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h3 class="text-lg font-bold text-gray-900 dark:text-white">{{ t('settings.metadata.customPromptTitle') }}</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ t('settings.metadata.customPromptDescription') }}</p>
              </div>
              <label class="flex items-center cursor-pointer">
                <input type="checkbox" v-model="useDefaultPrompt" class="w-5 h-5 text-blue-600 rounded" />
                <span class="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('settings.metadata.useDefaultPrompt') }}</span>
              </label>
            </div>

            <!-- 기본값 사용 시 예시 프롬프트 표시 -->
            <div v-if="useDefaultPrompt" class="space-y-4">
              <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-xl p-4">
                <p class="text-sm text-blue-800 dark:text-blue-300 mb-2">
                  <strong>{{ t('settings.metadata.defaultPromptTitle') }}</strong>
                </p>
                <div v-if="aiProvider === 'openai'" class="bg-white dark:bg-gray-800 rounded-lg p-4 font-mono text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ defaultPromptOpenai }}</div>
                <div v-if="aiProvider === 'gemini'" class="bg-white dark:bg-gray-800 rounded-lg p-4 font-mono text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ defaultPromptGemini }}</div>
              </div>
            </div>

            <!-- 커스텀 프롬프트 입력 -->
            <div v-if="!useDefaultPrompt" class="space-y-4">
              <!-- Info Box -->
              <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-xl p-4">
                <p class="text-sm text-amber-800 dark:text-amber-300">
                  <strong>{{ t('settings.metadata.availableVariables') }}</strong><br>
                  <code class="bg-amber-100 dark:bg-amber-800 px-2 py-0.5 rounded">{software_name}</code> {{ t('settings.metadata.softwareNameVariable') }}<br>
                  <br>
                  <strong>{{ t('settings.metadata.customPromptTip') }}</strong> {{ t('settings.metadata.customPromptTipText') }}
                </p>
              </div>

              <!-- OpenAI Prompt -->
              <div v-if="aiProvider === 'openai'">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ t('settings.metadata.openaiPromptLabel') }}
                  <button
                    @click="customPromptOpenai = defaultPromptOpenai"
                    type="button"
                    class="ml-2 text-xs text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    {{ t('settings.metadata.restoreDefault') }}
                  </button>
                </label>
                <textarea
                  v-model="customPromptOpenai"
                  rows="15"
                  class="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono text-sm"
                  :placeholder="t('settings.metadata.openaiPromptPlaceholder')"
                ></textarea>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  {{ t('settings.metadata.currentCharCount') }} {{ customPromptOpenai.length }}
                </p>
              </div>

              <!-- Gemini Prompt -->
              <div v-if="aiProvider === 'gemini'">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ t('settings.metadata.geminiPromptLabel') }}
                  <button
                    @click="customPromptGemini = defaultPromptGemini"
                    type="button"
                    class="ml-2 text-xs text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    {{ t('settings.metadata.restoreDefault') }}
                  </button>
                </label>
                <textarea
                  v-model="customPromptGemini"
                  rows="15"
                  class="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono text-sm"
                  :placeholder="t('settings.metadata.geminiPromptPlaceholder')"
                ></textarea>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  {{ t('settings.metadata.currentCharCount') }} {{ customPromptGemini.length }}
                </p>
              </div>
            </div>
          </div>

          <!-- Apply Button -->
          <div class="flex justify-end">
            <button @click="saveMetadataSettings" class="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all shadow-md font-medium flex items-center">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              {{ t('settings.metadata.apply') }}
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
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.exceptions.folderNamesTitle') }}</h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              {{ t('settings.exceptions.folderNamesDescription') }}
            </p>

            <div class="mb-4">
              <div class="flex gap-2">
                <input
                  v-model="newExceptionFolder"
                  type="text"
                  :placeholder="t('settings.exceptions.folderNamePlaceholder')"
                  class="flex-1 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  @keyup.enter="addExceptionFolder"
                />
                <button
                  @click="addExceptionFolder"
                  class="px-6 py-2 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-colors whitespace-nowrap"
                >
                  {{ t('settings.exceptions.add') }}
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
                  {{ t('settings.exceptions.delete') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Specific Paths -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.exceptions.specificPathsTitle') }}</h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              {{ t('settings.exceptions.specificPathsDescription') }}
            </p>

            <div class="mb-4">
              <div class="flex gap-2">
                <input
                  v-model="newExceptionPath"
                  type="text"
                  :placeholder="t('settings.exceptions.specificPathPlaceholder')"
                  class="flex-1 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  @keyup.enter="addExceptionPath"
                />
                <button
                  @click="addExceptionPath"
                  class="px-6 py-2 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-colors whitespace-nowrap"
                >
                  {{ t('settings.exceptions.add') }}
                </button>
              </div>
            </div>

            <div v-if="exceptionPaths.length === 0" class="text-center py-8 text-gray-400 dark:text-gray-500">
              {{ t('settings.exceptions.noPathsAdded') }}
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
                  {{ t('settings.exceptions.delete') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Supported Extensions -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center">
              <span class="mr-2">✅</span>
              {{ t('settings.exceptions.supportedExtensionsTitle') }}
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              {{ t('settings.exceptions.supportedExtensionsDesc') }}
            </p>

            <div v-if="loadingSupportedExtensions" class="text-center py-4">
              <svg class="animate-spin h-6 w-6 mx-auto text-blue-500" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>

            <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="(extensions, category) in supportedExtensions"
                :key="category"
                class="bg-gray-50 dark:bg-gray-700 rounded-xl p-4"
              >
                <h4 class="font-medium text-gray-900 dark:text-white mb-2">
                  {{ t('settings.exceptions.' + category) || category }}
                </h4>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="ext in extensions"
                    :key="ext"
                    class="px-2 py-1 text-xs font-mono bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded"
                  >
                    {{ ext }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Info Box -->
          <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-xl p-4">
            <h4 class="text-sm font-bold text-blue-900 dark:text-blue-300 mb-2">{{ t('settings.exceptions.exceptionGuideTitle') }}</h4>
            <ul class="text-sm text-blue-800 dark:text-blue-300 space-y-1">
              <li>{{ t('settings.exceptions.exceptionGuide1') }}</li>
              <li>{{ t('settings.exceptions.exceptionGuide2') }}</li>
              <li>{{ t('settings.exceptions.exceptionGuide3') }}</li>
              <li>{{ t('settings.exceptions.exceptionGuide4') }}</li>
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
              {{ savingExceptions ? t('settings.exceptions.saving') : t('settings.exceptions.apply') }}
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
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.system.resources') }}</h3>
            <a href="https://github.com/zardkim/my-appstore" target="_blank" class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-600 rounded-xl hover:border-blue-200 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all group">
              <div class="flex items-center">
                <svg class="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 mr-3" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                <div>
                  <p class="font-medium text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400">{{ t('settings.system.githubRepository') }}</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('settings.system.sourceCodeAndIssues') }}</p>
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
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">{{ t('settings.users.addUserTitle') }}</h3>
        </div>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">{{ t('settings.users.addUserDescription') }}</p>
        <form @submit.prevent="addUser" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.users.username') }}</label>
            <input
              v-model="newUser.username"
              type="text"
              required
              minlength="3"
              :placeholder="t('settings.users.usernamePlaceholder')"
              class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.users.password') }}</label>
            <input
              v-model="newUser.password"
              type="password"
              required
              minlength="8"
              :placeholder="t('settings.users.passwordPlaceholder')"
              class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.users.passwordConfirm') }}</label>
            <input
              v-model="newUser.passwordConfirm"
              type="password"
              required
              minlength="8"
              :placeholder="t('settings.users.passwordConfirmPlaceholder')"
              class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            />
          </div>
          <div class="flex space-x-3">
            <button type="button" @click="showAddUserModal = false" class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700">{{ t('settings.users.cancel') }}</button>
            <button type="submit" class="flex-1 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl hover:from-green-600 hover:to-emerald-700 shadow-md">{{ t('settings.users.add') }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add Category Modal -->
    <div v-if="showAddCategoryModal" class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50" @click.self="showAddCategoryModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.categoriesManagement.addCategoryTitle') }}</h3>
        <form @submit.prevent="addCategory" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.categoriesManagement.categoryNameEn') }}</label>
            <input v-model="newCategory.name" @input="autoSuggestIcon('add')" type="text" required :placeholder="t('settings.categoriesManagement.categoryNameEnPlaceholder')" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.categoriesManagement.koreanName') }}</label>
            <input v-model="newCategory.label" type="text" required :placeholder="t('settings.categoriesManagement.koreanNamePlaceholder')" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.categoriesManagement.iconEmoji') }}</label>
            <div class="flex items-center space-x-2 mb-2">
              <div class="flex-shrink-0 w-12 h-12 bg-gray-100 dark:bg-gray-700 rounded-xl flex items-center justify-center text-2xl border-2 border-blue-500">
                {{ newCategory.icon || '❓' }}
              </div>
              <input v-model="newCategory.icon" type="text" required :placeholder="t('settings.categoriesManagement.iconEmojiPlaceholder')" maxlength="2" class="flex-1 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
            </div>

            <!-- Emoji Picker -->
            <div class="bg-gray-50 dark:bg-gray-900 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
              <p class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-3">{{ t('settings.categoriesManagement.frequentEmojis') }}</p>

              <!-- Emoji Categories -->
              <div class="space-y-3">
                <div v-for="(group, groupName) in emojiGroups" :key="groupName">
                  <p class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">{{ t('settings.categoriesManagement.emojiGroups.' + groupName) }}</p>
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
            <button type="button" @click="closeAddCategoryModal" class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700">{{ t('settings.categoriesManagement.cancel') }}</button>
            <button type="submit" class="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 shadow-md">{{ t('settings.categoriesManagement.add') }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add Board Category Modal -->
    <div v-if="showAddBoardCategoryModal" class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50" @click.self="showAddBoardCategoryModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.board.addBoardCategoryTitle') }}</h3>
        <form @submit.prevent="addBoardCategory" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.board.categoryValueEn') }}</label>
            <input v-model="newBoardCategory.value" type="text" required :placeholder="t('settings.board.categoryValueEnPlaceholder')" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.categoriesManagement.koreanName') }}</label>
            <input v-model="newBoardCategory.label" type="text" required :placeholder="t('settings.board.koreanNamePlaceholder')" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.board.color') }}</label>
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
            <button type="button" @click="closeAddBoardCategoryModal" class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700">{{ t('settings.board.cancel') }}</button>
            <button type="submit" class="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 shadow-md">{{ t('settings.board.add') }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Board Category Modal -->
    <div v-if="showEditBoardCategoryModal" class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50" @click.self="showEditBoardCategoryModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.board.editBoardCategoryTitle') }}</h3>
        <form @submit.prevent="updateBoardCategory" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.board.categoryValueEn') }}</label>
            <input v-model="editingBoardCategory.value" type="text" required :placeholder="t('settings.board.categoryValueEnPlaceholder')" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.categoriesManagement.koreanName') }}</label>
            <input v-model="editingBoardCategory.label" type="text" required :placeholder="t('settings.board.koreanNamePlaceholder')" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.board.color') }}</label>
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
            <button type="button" @click="closeEditBoardCategoryModal" class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700">{{ t('settings.board.cancel') }}</button>
            <button type="submit" class="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 shadow-md">{{ t('settings.board.save') }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Category Modal -->
    <div v-if="showEditCategoryModal" class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50" @click.self="showEditCategoryModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">{{ t('settings.categoriesManagement.editCategoryTitle') }}</h3>
        <form @submit.prevent="updateCategory" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.categoriesManagement.categoryNameEn') }}</label>
            <input v-model="editingCategory.name" @input="autoSuggestIcon('edit')" type="text" required :placeholder="t('settings.categoriesManagement.categoryNameEnPlaceholder')" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.categoriesManagement.koreanName') }}</label>
            <input v-model="editingCategory.label" type="text" required :placeholder="t('settings.categoriesManagement.koreanNamePlaceholder')" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('settings.categoriesManagement.iconEmoji') }}</label>
            <div class="flex items-center space-x-2 mb-2">
              <div class="flex-shrink-0 w-12 h-12 bg-gray-100 dark:bg-gray-700 rounded-xl flex items-center justify-center text-2xl border-2 border-blue-500">
                {{ editingCategory.icon || '❓' }}
              </div>
              <input v-model="editingCategory.icon" type="text" required placeholder="🎨" maxlength="2" class="flex-1 px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" />
            </div>

            <!-- Emoji Picker -->
            <div class="bg-gray-50 dark:bg-gray-900 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
              <p class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-3">{{ t('settings.categoriesManagement.frequentEmojis') }}</p>

              <!-- Emoji Categories -->
              <div class="space-y-3">
                <div v-for="(group, groupName) in emojiGroups" :key="groupName">
                  <p class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">{{ t('settings.categoriesManagement.emojiGroups.' + groupName) }}</p>
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
            <button type="button" @click="closeEditCategoryModal" class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700">{{ t('settings.categoriesManagement.cancel') }}</button>
            <button type="submit" class="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 shadow-md">{{ t('settings.categoriesManagement.save') }}</button>
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
import AdminScheduler from './AdminScheduler.vue'
import { configApi } from '../api/config'
import { scanApi } from '../api/scan'
import { usersApi } from '../api/users'
import { cacheApi } from '../api/cache'
import { authApi } from '../api/auth'
import { ENV } from '../utils/env'
import { useDialog } from '../composables/useDialog'

const { t, locale } = useI18n({ useScope: 'global' })

const route = useRoute()
const authStore = useAuthStore()
const localeStore = useLocaleStore()
const { alert, confirm } = useDialog()

// Use version injected by Vite from package.json
const appVersion = __APP_VERSION__

const sections = computed(() => {
  const allSections = [
    { id: 'general', label: t('settings.sections.general'), icon: '⚙️' },
    { id: 'cache', label: t('settings.sections.cache'), icon: '⚡' },
    { id: 'users', label: t('settings.sections.users'), icon: '👥' },
    { id: 'folders', label: t('settings.sections.folders'), icon: '📁' },
    { id: 'scheduler', label: t('settings.sections.scheduler'), icon: '⏰' },
    { id: 'categories', label: t('settings.sections.categories'), icon: '🏷️' },
    { id: 'board', label: t('settings.sections.board'), icon: '📋' },
    { id: 'filing-rules', label: t('settings.sections.filingRules'), icon: '📄' },
    { id: 'metadata', label: t('settings.sections.metadata'), icon: '🤖' },
    { id: 'exceptions', label: t('settings.sections.exceptions'), icon: '🚫' },
    { id: 'system', label: t('settings.sections.system'), icon: 'ℹ️' }
  ]

  // 일반 사용자는 general 섹션만 표시
  if (!isAdmin.value) {
    return allSections.filter(section => section.id === 'general')
  }

  return allSections
})

const activeSection = ref('general')
const userInfo = computed(() => authStore.user || { username: '', role: 'user' })
const isAdmin = computed(() => authStore.user?.role === 'admin')
const isLoadingConfig = ref(false) // config 로딩 중 플래그

// General
const language = computed({
  get: () => localeStore.locale,
  set: async (value) => {
    // 언어 변경 즉시 적용
    await localeStore.setLocale(value)

    // config 로딩 중이 아닐 때만 저장 (loadConfig에서 설정할 때는 저장 스킵)
    if (!isLoadingConfig.value) {
      // 즉시 config.json에 저장하여 새로고침 후에도 유지
      try {
        await configApi.updateSection('general', {
          language: value,
          frontendUrl: accessUrl.value,
          backendUrl: apiUrl.value
        })
      } catch (error) {
        console.error('언어 설정 저장 실패:', error)
      }
    }
  }
})
const accessUrl = ref(ENV.APP_URL)
const apiUrl = ref(ENV.BACKEND_URL)
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
    console.error('Cache stats load failed:', error)
    await alert.error(t('settings.cache.loadFailed'))
  } finally {
    cacheLoading.value = false
  }
}

const clearAllCache = async () => {
  const shouldClear = await confirm.warning(t('settings.cache.clearAllConfirm'))

  if (!shouldClear) return

  try {
    cacheLoading.value = true
    await cacheApi.clearCache('*')
    await alert.success(t('settings.cache.allCleared'))
    await loadCacheStats()
  } catch (error) {
    console.error('Cache clear failed:', error)
    await alert.error(t('settings.cache.clearError'))
  } finally {
    cacheLoading.value = false
  }
}

const clearProductsCache = async () => {
  try {
    cacheLoading.value = true
    await cacheApi.clearCache('products*')
    await alert.success(t('settings.cache.productsCleared'))
    await loadCacheStats()
  } catch (error) {
    console.error('Products cache clear failed:', error)
    await alert.error(t('settings.cache.productsClearError'))
  } finally {
    cacheLoading.value = false
  }
}

const clearStatsCache = async () => {
  try {
    cacheLoading.value = true
    await cacheApi.clearCache('stats*')
    await alert.success(t('settings.cache.statsCleared'))
    await loadCacheStats()
  } catch (error) {
    console.error('Stats cache clear failed:', error)
    await alert.error(t('settings.cache.statsClearError'))
  } finally {
    cacheLoading.value = false
  }
}

// Users
const users = ref([])
const showAddUserModal = ref(false)
const showEditUserModal = ref(false)
const showPasswordModal = ref(false)
const newUser = ref({ username: '', password: '', passwordConfirm: '' })
const editingUser = ref({ id: null, username: '' })
const newPassword = ref('')
const confirmPassword = ref('')
const loadingUsers = ref(false)
const registrationOpen = ref(false)

// Folders
const defaultLibraryPath = import.meta.env.VITE_LIBRARY_PATH || '/app/data/library'
const scanFolders = ref([
  { path: defaultLibraryPath, scanning: false }
])
const showFolderBrowser = ref(false)
const editingFolderIndex = ref(null)

// Categories - config.json에서 로드됨 (단일 소스)
const categories = ref([])
const showAddCategoryModal = ref(false)
const showEditCategoryModal = ref(false)
const newCategory = ref({ name: '', label: '', icon: '' })
const editingCategory = ref({ oldName: '', name: '', label: '', icon: '' })

// 카테고리 라벨 가져오기 (config.json의 label 우선 사용)
// 카테고리 관리에서는 config.json이 단일 소스이므로 저장된 label을 직접 표시
const getCategoryLabel = (category) => {
  // config.json의 label이 있으면 그것을 사용
  if (category.label) {
    return category.label
  }
  // label이 없는 경우에만 번역 시도
  const translationKey = `categories.${category.name}`
  const translated = t(translationKey)
  if (translated !== translationKey && translated !== category.name) {
    return translated
  }
  return category.name
}

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
const categoryColorOptions = computed(() => [
  { value: 'green', label: t('settings.board.colors.green'), bg: 'bg-green-100 dark:bg-green-900/50', text: 'text-green-800 dark:text-green-300' },
  { value: 'blue', label: t('settings.board.colors.blue'), bg: 'bg-blue-100 dark:bg-blue-900/50', text: 'text-blue-800 dark:text-blue-300' },
  { value: 'purple', label: t('settings.board.colors.purple'), bg: 'bg-purple-100 dark:bg-purple-900/50', text: 'text-purple-800 dark:text-purple-300' },
  { value: 'yellow', label: t('settings.board.colors.yellow'), bg: 'bg-yellow-100 dark:bg-yellow-900/50', text: 'text-yellow-800 dark:text-yellow-300' },
  { value: 'red', label: t('settings.board.colors.red'), bg: 'bg-red-100 dark:bg-red-900/50', text: 'text-red-800 dark:text-red-300' },
  { value: 'pink', label: t('settings.board.colors.pink'), bg: 'bg-pink-100 dark:bg-pink-900/50', text: 'text-pink-800 dark:text-pink-300' },
  { value: 'orange', label: t('settings.board.colors.orange'), bg: 'bg-orange-100 dark:bg-orange-900/50', text: 'text-orange-800 dark:text-orange-300' },
  { value: 'indigo', label: t('settings.board.colors.indigo'), bg: 'bg-indigo-100 dark:bg-indigo-900/50', text: 'text-indigo-800 dark:text-indigo-300' }
])

const postsPerPage = ref('20')
const allowComments = ref(true)
const allowAttachments = ref(true)

// 이모지 그룹
const emojiGroups = {
  'software': ['💻', '🖥️', '⌨️', '🖱️', '💾', '💿', '📀', '🔌', '🖨️', '⚙️'],
  'tools': ['🛠️', '🔧', '🔨', '⚒️', '🪛', '🗜️', '⛏️', '🪚', '📐', '📏'],
  'documents': ['📊', '📈', '📉', '📝', '📋', '📄', '📃', '📑', '🗂️', '📁'],
  'media': ['🎬', '🎥', '📹', '🎞️', '📷', '📸', '🎨', '🖼️', '🎭', '🎪'],
  'music': ['🎵', '🎶', '🎼', '🎤', '🎧', '📻', '🎸', '🎹', '🎺', '🎷'],
  'network': ['🌐', '🌍', '🌎', '🌏', '💬', '📱', '📞', '☎️', '📡', '📶'],
  'security': ['🔒', '🔐', '🔑', '🛡️', '🔓', '🔏', '⚠️', '🚨', '🆘', '⛔'],
  'games': ['🎮', '🕹️', '🎯', '🎲', '🧩', '♠️', '♥️', '♦️', '♣️', '🃏'],
  'business': ['💼', '🏢', '🏦', '💰', '💵', '💴', '💶', '💷', '💳', '📊'],
  'education': ['📚', '📖', '📕', '📗', '📘', '📙', '📓', '📔', '📒', '🎓'],
  'other': ['📦', '📮', '📫', '📪', '📬', '📭', '🎒', '💾', '🗄️', '☁️']
}

// Metadata
const scanMethod = ref('ai')
const aiProvider = ref('gemini')
const aiModel = ref('gemini-2.5-flash')
const geminiApiKey = ref('')
const openaiApiKey = ref('')
const bingApiKey = ref('')
const bingImageSearch = ref(true)
// API 키 상태 관리: 저장 여부 + 편집 모드
const hasGeminiKey = ref(false)
const hasOpenaiKey = ref(false)
const hasBingKey = ref(false)
const editingGeminiKey = ref(false)
const editingOpenaiKey = ref(false)
const editingBingKey = ref(false)
const useDefaultPrompt = ref(true) // 기본값 사용 체크박스 (기본적으로 체크됨)
const customPromptOpenai = ref('')
const customPromptGemini = ref('')

// 기본 프롬프트 템플릿 (i18n으로부터 가져오기)
const defaultPromptOpenai = computed(() => t('settings.metadata.defaultPromptOpenai'))
const defaultPromptGemini = computed(() => t('settings.metadata.defaultPromptGemini'))
const showMetadataDialog = ref(false)

// 기본값 사용 체크박스 해제 시 커스텀 프롬프트를 기본값으로 초기화
watch(useDefaultPrompt, (newValue) => {
  if (!newValue) {
    // 커스텀 프롬프트로 전환 시 비어있으면 기본값으로 채움
    if (!customPromptOpenai.value || customPromptOpenai.value.trim() === '') {
      customPromptOpenai.value = defaultPromptOpenai.value
    }
    if (!customPromptGemini.value || customPromptGemini.value.trim() === '') {
      customPromptGemini.value = defaultPromptGemini.value
    }
  }
})

// 이전 언어의 기본 프롬프트 저장 (언어 변경 감지용)
let prevDefaultPromptOpenai = ''
let prevDefaultPromptGemini = ''

// 언어 변경 시 기본 프롬프트 자동 업데이트
watch(locale, () => {
  // 현재 프롬프트가 이전 언어의 기본 프롬프트와 같거나 비어있으면 새 언어의 기본 프롬프트로 업데이트
  if (!customPromptOpenai.value ||
      customPromptOpenai.value.trim() === '' ||
      customPromptOpenai.value === prevDefaultPromptOpenai) {
    customPromptOpenai.value = defaultPromptOpenai.value
  }
  if (!customPromptGemini.value ||
      customPromptGemini.value.trim() === '' ||
      customPromptGemini.value === prevDefaultPromptGemini) {
    customPromptGemini.value = defaultPromptGemini.value
  }
  // 현재 기본 프롬프트를 저장
  prevDefaultPromptOpenai = defaultPromptOpenai.value
  prevDefaultPromptGemini = defaultPromptGemini.value
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

// Supported Extensions
const supportedExtensions = ref({})
const loadingSupportedExtensions = ref(false)

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
const addExceptionPattern = async () => {
  const pattern = newExceptionPattern.value.trim()
  if (!pattern) return
  if (exceptionPatterns.value.includes(pattern)) return

  // 지원되는 소프트웨어 확장자 패턴 추가 차단
  const extMatch = pattern.match(/\*(\.[a-zA-Z0-9]+)$/)
  if (extMatch) {
    const ext = extMatch[1].toLowerCase()
    // supportedExtensions에서 플랫 배열 생성, 없으면 기본값 사용
    const allSupported = Object.values(supportedExtensions.value).flat().length > 0
      ? Object.values(supportedExtensions.value).flat()
      : ['.exe', '.msi', '.msp', '.msu', '.app', '.dmg', '.deb', '.rpm',
         '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.cab',
         '.iso', '.img', '.vhd', '.vmdk', '.vdi', '.vmx', '.ova', '.ovf',
         '.sh', '.bat', '.cmd', '.ps1', '.py',
         '.apk', '.ipa', '.jar', '.war', '.bin', '.run']
    if (allSupported.includes(ext)) {
      await alert.warning(t('settings.exceptions.cannotExcludeSupportedExt', { ext }))
      return
    }
  }

  exceptionPatterns.value.push(pattern)
  newExceptionPattern.value = ''
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
    await scanApi.saveScanExclusions({
      folders: exceptionFolders.value,
      patterns: exceptionPatterns.value,
      paths: exceptionPaths.value
    })
    await alert.success(t('settings.exceptions.saved'))
  } catch (error) {
    console.error('Scan exception settings save error:', error)
    await alert.error(t('settings.exceptions.saveFailed'))
  } finally {
    savingExceptions.value = false
  }
}

// 스캔 예외 설정 불러오기
const loadExceptionSettings = async () => {
  try {
    const response = await scanApi.getScanExclusions()


    if (response && response.data) {
      // 폴더 예외
      if (response.data.folders && response.data.folders.length > 0) {
        exceptionFolders.value = response.data.folders
      } else if (response.data.exclusions) {
        // 하위 호환성을 위한 처리
        exceptionFolders.value = response.data.exclusions
      } else {
        exceptionFolders.value = ['.DAV', '.git', '.node_modules', '_MACOSX', '#recycle', '@eaDir']
      }

      // 파일 패턴 예외
      if (response.data.patterns && response.data.patterns.length > 0) {
        exceptionPatterns.value = response.data.patterns
      } else {
        exceptionPatterns.value = ['*.txt', '*.log', 'thumbs.db', 'desktop.ini', '*.nfo', '*.sfv', '*.sha1', '*.md5', '*.md4']
      }

      // 경로 예외
      if (response.data.paths && response.data.paths.length > 0) {
        exceptionPaths.value = response.data.paths
      }


    } else {
      console.warn('❌ No exception data in response')
      // 기본값 설정
      exceptionFolders.value = ['.DAV', '.git', '.node_modules', '_MACOSX', '#recycle', '@eaDir']
      exceptionPatterns.value = ['*.txt', '*.log', 'thumbs.db', 'desktop.ini', '*.nfo', '*.sfv', '*.sha1', '*.md5', '*.md4']
    }
  } catch (error) {
    console.error('❌ 스캔 예외 설정 불러오기 오류:', error)
    // 기본값 설정
    exceptionFolders.value = ['.DAV', '.git', '.node_modules', '_MACOSX', '#recycle', '@eaDir']
    exceptionPatterns.value = ['*.txt', '*.log', 'thumbs.db', 'desktop.ini', '*.nfo', '*.sfv', '*.sha1', '*.md5', '*.md4']
  }
}

// 지원 확장자 목록 불러오기
const loadSupportedExtensions = async () => {
  loadingSupportedExtensions.value = true
  try {
    const response = await scanApi.getScanInfo()
    if (response && response.data && response.data.supported_extensions) {
      supportedExtensions.value = response.data.supported_extensions
    }
  } catch (error) {
    console.error('❌ 지원 확장자 불러오기 오류:', error)
    // 기본값 설정
    supportedExtensions.value = {
      executables: ['.exe', '.msi', '.app', '.dmg', '.deb', '.rpm'],
      archives: ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
      diskImages: ['.iso', '.img', '.vhd', '.vmdk', '.vdi'],
      scripts: ['.sh', '.bat', '.cmd', '.ps1'],
      others: ['.apk', '.ipa', '.jar']
    }
  } finally {
    loadingSupportedExtensions.value = false
  }
}

const formatDate = (dateStr) => new Date(dateStr).toLocaleDateString('ko-KR')

const loadUsers = async () => {
  try {
    loadingUsers.value = true
    const result = await usersApi.getAll()

    users.value = result
  } catch (error) {
    console.error('❌ 사용자 목록 로드 오류:', error)

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
    await alert.warning(t('settings.users.usernameMinLength'))
    return
  }

  // 비밀번호 길이 검증
  if (newUser.value.password.length < 8) {
    await alert.warning(t('settings.users.passwordMinLength'))
    return
  }

  // 비밀번호 일치 검증
  if (newUser.value.password !== newUser.value.passwordConfirm) {
    await alert.warning(t('settings.users.passwordMismatch'))
    return
  }

  try {
    await usersApi.create(newUser.value.username, newUser.value.password, 'user')
    await loadUsers() // 사용자 목록 새로고침
    await alert.success(t('settings.users.userAdded'))
    showAddUserModal.value = false
    newUser.value = { username: '', password: '', passwordConfirm: '' }
  } catch (error) {
    console.error('User add error:', error)
    const errorMessage = error.response?.data?.detail || t('settings.users.addFailed')
    await alert.error(errorMessage)
  }
}

const toggleRegistration = async () => {
  try {
    // Update config with new registration status
    const response = await configApi.getConfig()
    const config = response.data
    const generalConfig = config.general || {}
    generalConfig.registrationOpen = registrationOpen.value
    await configApi.updateSection('general', generalConfig)

    if (registrationOpen.value) {
      await alert.success(t('settings.users.registrationOpened'))
    } else {
      await alert.success(t('settings.users.registrationClosedMsg'))
    }
  } catch (error) {
    console.error('Toggle registration error:', error)
    // Revert on error
    registrationOpen.value = !registrationOpen.value
    await alert.error(t('settings.users.registrationToggleFailed'))
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
    passwordError.value = t('settings.users.newPasswordMismatch')
    return
  }

  if (newPassword.value.length < 8) {
    passwordError.value = t('settings.users.passwordMinLength')
    return
  }

  try {
    await usersApi.changePassword(editingUser.value.id, newPassword.value)
    showPasswordModal.value = false
    editingUser.value = { id: null, username: '' }
    newPassword.value = ''
    confirmPassword.value = ''
    await alert.success(t('settings.users.passwordChanged'))
  } catch (error) {
    console.error('Password change error:', error)
    passwordError.value = error.response?.data?.detail || t('settings.users.passwordChangeFailed')
  }
}

const toggleUserStatus = async (user) => {
  try {
    await usersApi.toggleStatus(user.id, user.is_active)
  } catch (error) {
    console.error('Status change error:', error)
    // Revert status on error
    user.is_active = !user.is_active
    await alert.error(t('settings.users.statusChangeFailed'))
  }
}

const deleteUser = async (user) => {
  const shouldDelete = await confirm.danger(t('settings.users.deleteConfirm', { username: user.username }), t('settings.users.deleteTitle'))
  if (!shouldDelete) return

  try {
    await usersApi.delete(user.id)
    await loadUsers() // Reload users list
    await alert.success(t('settings.users.userDeleted'))
  } catch (error) {
    console.error('User delete error:', error)
    const errorMessage = error.response?.data?.detail || t('settings.users.deleteFailed')
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
    await alert.warning(t('settings.folders.cannotEditDefault'))
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
      await alert.warning(t('settings.folders.duplicateFolder'))
      return
    }

    scanFolders.value[editingFolderIndex.value].path = path
  } else {
    // 새 폴더 추가 - 중복 체크
    const isDuplicate = scanFolders.value.some(folder => folder.path === path)

    if (isDuplicate) {
      await alert.warning(t('settings.folders.duplicateFolder'))
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
    await alert.warning(t('settings.folders.cannotDeleteDefault'))
    return
  }

  const shouldConfirm = await confirm.warning(t('settings.folders.deleteConfirm'))
  if (shouldConfirm) {
    scanFolders.value.splice(index, 1)
  }
}

const scanFolder = async (path) => {
  const folder = scanFolders.value.find(f => f.path === path)
  if (!folder) return

  const shouldScan = await confirm.info(t('settings.folders.scanConfirm', { path }))
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
      await alert.success(t('settings.folders.scanComplete', {
        newProducts: result.new_products || 0,
        newVersions: result.new_versions || 0,
        updates: result.updated_products || 0
      }))
    }
  } catch (error) {
    console.error('Folder scan error:', error)
    const errorMessage = error.response?.data?.detail || error.message || t('settings.folders.scanError')
    await alert.error(t('settings.folders.scanFailed') + ': ' + errorMessage)
  } finally {
    folder.scanning = false
  }
}

const saveFolders = async () => {
  try {
    // 최소 1개 이상의 폴더가 필요
    if (scanFolders.value.length === 0) {
      await alert.warning(t('settings.folders.minFolderRequired'))
      return
    }

    // 폴더 경로만 추출 (scanning 상태 제외)
    const folderPaths = scanFolders.value.map(folder => folder.path)

    // API 호출로 서버에 저장
    await configApi.updateSection('folders', {
      scanFolders: folderPaths
    })

    await alert.success(t('settings.folders.saved'))
  } catch (error) {
    console.error('Folder save error:', error)
    const errorMessage = error.response?.data?.detail || error.message || t('settings.folders.saveFailed')
    await alert.error(t('settings.folders.saveFailed') + ': ' + errorMessage)
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
    await alert.warning(t('settings.categoriesManagement.categoryDuplicateWarning'))
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
      await alert.warning(t('settings.categoriesManagement.categoryDuplicateWarning'))
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
  const shouldDelete = await confirm.danger(
    t('settings.categoriesManagement.categoryDeleteConfirm', { name: getCategoryLabel(category) }),
    t('settings.categoriesManagement.categoryDeleteTitle')
  )
  if (shouldDelete) {
    categories.value = categories.value.filter(c => c.name !== category.name)
  }
}

// 일반 설정 저장
const saveGeneralSettings = async () => {
  try {
    const data = {
      language: language.value,
      frontendUrl: accessUrl.value,
      backendUrl: apiUrl.value
    }

    await configApi.updateSection('general', data)
    await alert.success(t('settings.general.saved'))
  } catch (error) {
    console.error('General settings save failed:', error)
    await alert.error(t('settings.general.saveFailed'))
  }
}

// 카테고리 설정 저장
const saveCategories = async () => {
  try {
    await configApi.updateSection('categories', categories.value)
    await alert.success(t('settings.categoriesManagement.categorySaved'))
  } catch (error) {
    console.error('Category settings save failed:', error)
    await alert.error(t('settings.categoriesManagement.categorySaveFailed'))
  }
}

// 메타데이터 설정 저장
const saveMetadataSettings = async () => {
  try {
    const data = {
      scanMethod: scanMethod.value,
      aiProvider: aiProvider.value,
      aiModel: aiModel.value,
      // 편집 모드이거나 기존 키가 없을 때(최초 입력) 새 값 전송, 그 외 빈 문자열 (백엔드가 기존 값 보존)
      geminiApiKey: (editingGeminiKey.value || !hasGeminiKey.value) ? geminiApiKey.value : '',
      openaiApiKey: (editingOpenaiKey.value || !hasOpenaiKey.value) ? openaiApiKey.value : '',
      bingApiKey: (editingBingKey.value || !hasBingKey.value) ? bingApiKey.value : '',
      bingImageSearch: bingImageSearch.value,
      useDefaultPrompt: useDefaultPrompt.value,
      customPromptOpenai: customPromptOpenai.value,
      customPromptGemini: customPromptGemini.value
    }

    await configApi.updateSection('metadata', data)

    // 저장 후 편집 모드 해제 및 상태 업데이트 (최초 입력 또는 편집 모드)
    if ((editingGeminiKey.value || !hasGeminiKey.value) && geminiApiKey.value) {
      hasGeminiKey.value = true
      editingGeminiKey.value = false
      geminiApiKey.value = ''
    }
    if ((editingOpenaiKey.value || !hasOpenaiKey.value) && openaiApiKey.value) {
      hasOpenaiKey.value = true
      editingOpenaiKey.value = false
      openaiApiKey.value = ''
    }
    if ((editingBingKey.value || !hasBingKey.value) && bingApiKey.value) {
      hasBingKey.value = true
      editingBingKey.value = false
      bingApiKey.value = ''
    }

    await alert.success(t('settings.metadata.saved'))
  } catch (error) {
    console.error('Metadata settings save failed:', error)
    console.error('Error response:', error.response)

    let errorMessage = t('settings.metadata.saveFailed')
    if (error.response?.data?.detail) {
      errorMessage += `: ${error.response.data.detail}`
    } else if (error.message) {
      errorMessage += `: ${error.message}`
    }

    await alert.error(errorMessage)
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
    await alert.warning(t('settings.board.boardCategoryDuplicateWarning'))
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
      await alert.warning(t('settings.board.boardCategoryDuplicateWarning'))
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
  const shouldDelete = await confirm.danger(
    t('settings.board.boardCategoryDeleteConfirm', { name: category.label }),
    t('settings.board.boardCategoryDeleteTitle')
  )
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

    await alert.success(t('settings.board.saved'))
  } catch (error) {
    console.error('Board settings save failed:', error)
    await alert.error(t('settings.board.saveFailed'))
  }
}

// 페이지 로드 시 저장된 설정 불러오기
onMounted(async () => {
  try {
    // URL 쿼리 파라미터에서 섹션 확인
    const section = route.query.section
    if (section && sections.value.some(s => s.id === section)) {
      activeSection.value = section
    }

    // 사용자 목록 로드
    await loadUsers()

    // 스캔 예외 설정 로드
    await loadExceptionSettings()

    // 지원 확장자 목록 로드
    await loadSupportedExtensions()

    // config.json에서 모든 설정 로드
    isLoadingConfig.value = true
    const response = await configApi.getConfig()
    const config = response.data

    // 일반 설정
    if (config.general) {
      // 언어 설정: language는 computed로 localeStore.locale을 자동 반영하므로 별도 설정 불필요
      // localeStore는 초기화 시 localStorage에서 값을 읽어옴

      // 필드명 호환성 처리 (frontendUrl/backendUrl 또는 accessUrl/apiUrl)
      accessUrl.value = config.general.frontendUrl || config.general.accessUrl || ENV.APP_URL
      apiUrl.value = config.general.backendUrl || config.general.apiUrl || ENV.BACKEND_URL

      // 회원가입 설정
      registrationOpen.value = config.general.registrationOpen || false
    }
    isLoadingConfig.value = false

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

    } else {
      console.warn('❌ No categories in config:', config.categories)
    }

    // 메타데이터 설정
    if (config.metadata) {
      scanMethod.value = config.metadata.scanMethod || 'ai'
      aiProvider.value = config.metadata.aiProvider || 'gemini'
      aiModel.value = config.metadata.aiModel || 'gemini-2.5-flash'
      // API 키: 실제 값을 UI에 표시하지 않음 - 저장 여부만 체크
      // 저장됨 표시 후 "수정" 버튼을 눌러야만 변경 가능
      hasGeminiKey.value = !!(config.metadata.geminiApiKey)
      hasOpenaiKey.value = !!(config.metadata.openaiApiKey)
      hasBingKey.value = !!(config.metadata.bingApiKey)
      bingImageSearch.value = config.metadata.bingImageSearch !== false  // 기본값 true
      geminiApiKey.value = ''
      openaiApiKey.value = ''
      bingApiKey.value = ''
      editingGeminiKey.value = false
      editingOpenaiKey.value = false
      editingBingKey.value = false
      // useDefaultPrompt가 설정되어 있으면 그 값을 사용, 없으면 true (기본값)
      useDefaultPrompt.value = config.metadata.useDefaultPrompt !== undefined
        ? config.metadata.useDefaultPrompt
        : (config.metadata.useCustomPrompt !== undefined ? !config.metadata.useCustomPrompt : true)
      customPromptOpenai.value = config.metadata.customPromptOpenai || defaultPromptOpenai.value
      customPromptGemini.value = config.metadata.customPromptGemini || defaultPromptGemini.value
      // 이전 기본 프롬프트 초기화 (언어 변경 감지용)
      prevDefaultPromptOpenai = defaultPromptOpenai.value
      prevDefaultPromptGemini = defaultPromptGemini.value
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

    // 이전 기본 프롬프트 초기화 (언어 변경 감지용) - config.metadata가 없는 경우 대비
    if (!prevDefaultPromptOpenai) {
      prevDefaultPromptOpenai = defaultPromptOpenai.value
    }
    if (!prevDefaultPromptGemini) {
      prevDefaultPromptGemini = defaultPromptGemini.value
    }
  } catch (error) {
    console.error('설정 로드 실패:', error)
    isLoadingConfig.value = false // 에러 발생 시에도 플래그 해제

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
