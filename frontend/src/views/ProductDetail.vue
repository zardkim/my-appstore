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
          <span class="hidden sm:inline">{{ t('productDetail.back') }}</span>
        </button>

        <!-- 편집 모드 토글 버튼 -->
        <div v-if="authStore.user?.role === 'admin'" class="flex items-center gap-1.5 sm:gap-2 lg:gap-3">
          <!-- 참조사이트 아이콘 (편집 모드일 때만 표시) -->
          <button
            v-if="isEditing"
            @click="showReferenceSitesDialog = true"
            class="p-2 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
            :title="t('productDetail.viewReferences')"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          </button>
          <button
            v-if="isEditing"
            @click="cancelEdit"
            class="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-colors flex items-center"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            {{ t('productDetail.cancel') }}
          </button>
          <button
            v-if="isEditing"
            @click="saveEdit"
            :disabled="saving"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg transition-colors flex items-center"
          >
            <svg v-if="!saving" class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <svg v-else class="animate-spin w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {{ saving ? t('productDetail.saving') : t('productDetail.save') }}
          </button>
          <button
            v-if="!isEditing"
            @click="startEdit"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            {{ t('productDetail.edit') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="flex-1 flex items-center justify-center p-4">
      <div class="text-center max-w-md">
        <div class="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-red-100 to-red-50 dark:from-red-900 dark:to-red-800 rounded-3xl flex items-center justify-center">
          <svg class="w-10 h-10 text-red-500 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">{{ t('productDetail.cannotLoad') }}</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm mb-6">{{ error }}</p>
        <button
          @click="$router.back()"
          class="inline-flex items-center px-6 py-3 text-sm bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all shadow-md hover:shadow-lg font-medium"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          {{ t('productDetail.back') }}
        </button>
      </div>
    </div>

    <!-- Content -->
    <div v-else-if="product" class="flex-1 overflow-y-auto pb-20 lg:pb-8">
      <!-- Product Header -->
      <div class="bg-gradient-to-r from-blue-500 to-purple-600 dark:from-blue-700 dark:to-purple-800 px-4 sm:px-6 lg:px-8 py-6 sm:py-8 lg:py-12 text-white mb-4 sm:mb-6">
        <div class="max-w-7xl mx-auto">
          <div class="flex flex-col sm:flex-row items-start gap-4 sm:gap-6 lg:gap-8">
            <!-- 아이콘 (클릭하여 검색 가능) -->
            <div
              class="relative w-24 h-24 sm:w-32 sm:h-32 lg:w-40 lg:h-40 bg-white dark:bg-gray-800 rounded-xl sm:rounded-2xl flex-shrink-0 flex items-center justify-center overflow-hidden p-4 sm:p-5 lg:p-6 shadow-xl group"
              :class="{ 'cursor-pointer hover:ring-2 hover:ring-blue-500': authStore.user?.role === 'admin' }"
            >
              <img
                v-if="iconUrlWithTimestamp"
                :src="iconUrlWithTimestamp"
                :alt="product.title"
                class="w-full h-full object-contain"
              />
              <svg
                v-else
                class="w-12 h-12 sm:w-16 sm:h-16 lg:w-20 lg:h-20 text-blue-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                />
              </svg>

              <!-- 로고 버튼들 (Admin만 표시) -->
              <div v-if="authStore.user?.role === 'admin'" class="absolute bottom-1.5 right-1.5 sm:bottom-2 sm:right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-all">
                <!-- 로고 파일 업로드 -->
                <button
                  @click="triggerLogoUpload"
                  class="w-7 h-7 sm:w-8 sm:h-8 bg-purple-600 hover:bg-purple-700 text-white rounded-full flex items-center justify-center shadow-lg hover:scale-110"
                  :title="t('productDetail.uploadLogo')"
                >
                  <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </button>
                <!-- URL로 로고 추가 -->
                <button
                  @click="showLogoUrlDialog = true"
                  class="w-7 h-7 sm:w-8 sm:h-8 bg-green-600 hover:bg-green-700 text-white rounded-full flex items-center justify-center shadow-lg hover:scale-110"
                  :title="t('productDetail.addLogoFromUrl')"
                >
                  <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                </button>
                <!-- 로고 검색 -->
                <button
                  @click="openLogoSearch"
                  class="w-7 h-7 sm:w-8 sm:h-8 bg-blue-600 hover:bg-blue-700 text-white rounded-full flex items-center justify-center shadow-lg hover:scale-110"
                  :title="t('productDetail.searchLogo')"
                >
                  <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </button>
              </div>
              <!-- 로고 업로드용 숨김 input -->
              <input
                ref="logoFileInput"
                type="file"
                accept="image/*"
                class="hidden"
                @change="handleLogoFileUpload"
              />
            </div>

            <div class="flex-1">
              <!-- 제목 (편집 가능) -->
              <div class="mb-1 sm:mb-2">
                <input
                  v-if="isEditing"
                  v-model="editForm.title"
                  type="text"
                  class="w-full text-xl sm:text-2xl lg:text-4xl font-bold bg-white/10 border-2 border-white/30 rounded-lg px-3 sm:px-4 py-1.5 sm:py-2 text-white placeholder-white/50 focus:outline-none focus:border-white/60"
                  placeholder="제품명 (예: Hancom Office)"
                />
                <h1 v-else class="text-xl sm:text-2xl lg:text-4xl font-bold">{{ product.title }}</h1>
              </div>

              <!-- 부제목 (편집 가능) -->
              <div class="mb-2 sm:mb-3">
                <input
                  v-if="isEditing"
                  v-model="editForm.subtitle"
                  type="text"
                  class="w-full text-sm sm:text-base lg:text-xl bg-white/10 border-2 border-white/30 rounded-lg px-3 sm:px-4 py-1.5 sm:py-2 text-blue-100 placeholder-white/50 focus:outline-none focus:border-white/60"
                  placeholder="부제목 (예: 한컴오피스)"
                />
                <p v-else-if="product.subtitle" class="text-sm sm:text-base lg:text-xl text-blue-100">{{ product.subtitle }}</p>
              </div>

              <!-- 개발사 & 공식 웹사이트 -->
              <div class="mb-3 sm:mb-4">
                <div v-if="isEditing" class="space-y-2">
                  <input
                    v-model="editForm.vendor"
                    type="text"
                    class="w-full text-sm sm:text-base lg:text-lg bg-white/10 border-2 border-white/30 rounded-lg px-3 sm:px-4 py-1.5 sm:py-2 text-blue-100 placeholder-white/50 focus:outline-none focus:border-white/60"
                    :placeholder="t('productDetail.vendorPlaceholder')"
                  />
                  <input
                    v-model="editForm.official_website"
                    type="url"
                    class="w-full text-xs sm:text-sm bg-white/10 border-2 border-white/30 rounded-lg px-3 sm:px-4 py-1.5 sm:py-2 text-blue-100 placeholder-white/50 focus:outline-none focus:border-white/60"
                    :placeholder="t('productDetail.officialWebsitePlaceholder')"
                  />
                </div>
                <div v-else class="flex flex-wrap items-center gap-2 sm:gap-3">
                  <p class="text-blue-100 text-sm sm:text-base lg:text-lg">{{ product.vendor || 'Unknown Vendor' }}</p>

                  <!-- 공식 웹사이트 링크 -->
                  <a
                    v-if="product.official_website"
                    :href="product.official_website"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="flex items-center px-2 sm:px-3 py-1.5 sm:py-2 bg-white/20 hover:bg-white/30 backdrop-blur-sm border border-white/30 rounded-lg text-xs sm:text-sm font-medium transition-colors"
                    :title="t('productDetail.officialWebsiteTitle')"
                  >
                    <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                    </svg>
                    <span class="hidden sm:inline">{{ t('productDetail.officialSite') }}</span>
                  </a>
                </div>
              </div>

              <div class="flex flex-wrap items-center gap-2 sm:gap-3">
                <!-- 카테고리 (편집 가능) -->
                <select
                  v-if="isEditing"
                  v-model="editForm.category"
                  class="px-2.5 sm:px-3 lg:px-4 py-1.5 sm:py-2 rounded-lg sm:rounded-xl text-xs sm:text-sm font-medium bg-white backdrop-blur-sm border border-white/30 text-gray-900 focus:outline-none focus:border-blue-500"
                >
                  <option value="" class="text-gray-900">{{ t('productDetail.selectCategory') }}</option>
                  <option v-for="cat in categories" :key="cat" :value="cat" class="text-gray-900">{{ getCategoryIcon(cat) }} {{ getCategoryLabel(cat) }}</option>
                </select>
                <span
                  v-else-if="product.category"
                  class="inline-flex items-center px-2.5 sm:px-3 lg:px-4 py-1.5 sm:py-2 rounded-lg sm:rounded-xl text-xs sm:text-sm font-medium bg-white/20 backdrop-blur-sm border border-white/30"
                >
                  <span class="mr-1">{{ getCategoryIcon(product.category) }}</span>
                  <span class="hidden sm:inline">{{ getCategoryLabel(product.category) }}</span>
                </span>
                <span class="inline-flex items-center px-2.5 sm:px-3 lg:px-4 py-1.5 sm:py-2 rounded-lg sm:rounded-xl text-xs sm:text-sm font-medium bg-white/20 backdrop-blur-sm border border-white/30">
                  {{ product.versions?.length || 0 }} {{ t('productDetail.versions') }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs - 전체 페이지 사용 -->
      <div class="px-4 sm:px-6 lg:px-8">
        <div class="bg-white dark:bg-gray-800 rounded-xl sm:rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
          <div class="border-b border-gray-200 dark:border-gray-700 overflow-x-auto">
            <nav class="flex gap-4 sm:gap-6 lg:gap-8 px-4 sm:px-6 lg:px-8 min-w-max">
              <button
                @click="activeTab = 'info'"
                :class="tabClass('info')"
                class="text-sm sm:text-base whitespace-nowrap"
              >
                {{ t('product.tabs.info') }}
              </button>
              <button
                @click="activeTab = 'versions'"
                :class="tabClass('versions')"
                class="text-sm sm:text-base whitespace-nowrap"
              >
                <span class="hidden sm:inline">{{ t('product.tabs.versions') }} ({{ product.versions?.length || 0 }})</span>
                <span class="sm:hidden">{{ t('product.tabs.versions') }}</span>
              </button>
              <button
                @click="activeTab = 'screenshots'"
                :class="tabClass('screenshots')"
                class="text-sm sm:text-base whitespace-nowrap"
              >
                <span class="hidden sm:inline">{{ t('product.tabs.screenshots') }} ({{ product.screenshots?.length || 0 }})</span>
                <span class="sm:hidden">{{ t('product.tabs.screenshots') }}</span>
              </button>
              <button
                @click="activeTab = 'installation'"
                :class="tabClass('installation')"
                class="text-sm sm:text-base whitespace-nowrap"
              >
                {{ t('product.tabs.installation') }}
              </button>
              <button
                @click="activeTab = 'patches'"
                :class="tabClass('patches')"
                class="text-sm sm:text-base whitespace-nowrap"
              >
                <span class="hidden sm:inline">{{ t('product.tabs.patches') }} ({{ attachments?.length || 0 }})</span>
                <span class="sm:hidden">{{ t('product.tabs.patches') }}</span>
              </button>
            </nav>
          </div>

          <div class="p-4 sm:p-6 lg:p-8">
            <!-- Info Tab -->
            <div v-if="activeTab === 'info'" class="space-y-6 sm:space-y-8">
              <!-- 기본 설명 (편집 가능) -->
              <div>
                <h3 class="text-base sm:text-lg lg:text-xl font-bold text-gray-900 dark:text-white mb-3 sm:mb-4 flex items-center">
                  <span class="mr-2 text-lg sm:text-xl">📝</span>
                  {{ t('product.info.title') }}
                </h3>
                <textarea
                  v-if="isEditing"
                  v-model="editForm.description"
                  rows="3"
                  class="w-full px-3 sm:px-4 py-2 sm:py-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm sm:text-base text-gray-900 dark:text-white focus:outline-none focus:border-blue-500 resize-none"
                  :placeholder="t('product.info.descriptionPlaceholder')"
                ></textarea>
                <p v-else class="text-gray-700 dark:text-gray-300 leading-relaxed text-sm sm:text-base lg:text-lg">{{ product.description || t('product.info.noDescription') }}</p>
              </div>

              <!-- 플랫폼 & 지원 사양 (1번 요구사항: 라이센스를 지원 사양으로 변경) -->
              <div class="border-t border-gray-200 dark:border-gray-700 pt-4 sm:pt-6">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
                  <div>
                    <h4 class="text-xs sm:text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1.5 sm:mb-2">{{ t('product.info.platform') }}</h4>
                    <input
                      v-if="isEditing"
                      v-model="editForm.platform"
                      type="text"
                      class="w-full px-3 sm:px-4 py-1.5 sm:py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm sm:text-base text-gray-900 dark:text-white focus:outline-none focus:border-blue-500"
                      :placeholder="t('product.info.platformPlaceholder')"
                    />
                    <p v-else class="text-sm sm:text-base text-gray-900 dark:text-white">{{ product.platform || 'N/A' }}</p>
                  </div>
                  <div>
                    <h4 class="text-xs sm:text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1.5 sm:mb-2">{{ t('product.info.supportedSpecs') }}</h4>
                    <input
                      v-if="isEditing"
                      v-model="editForm.license_type"
                      type="text"
                      class="w-full px-3 sm:px-4 py-1.5 sm:py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm sm:text-base text-gray-900 dark:text-white focus:outline-none focus:border-blue-500"
                      :placeholder="t('product.info.specsPlaceholder')"
                    />
                    <p v-else class="text-sm sm:text-base text-gray-900 dark:text-white">{{ product.license_type || 'N/A' }}</p>
                  </div>
                </div>
              </div>

              <!-- Release Date & Notes -->
              <div v-if="product.release_date || product.release_notes || isEditing" class="border-t border-gray-200 dark:border-gray-700 pt-4 sm:pt-6">
                <h3 class="text-base sm:text-lg font-bold text-gray-900 dark:text-white mb-2 sm:mb-3 flex items-center">
                  <span class="mr-2 text-lg sm:text-xl">📅</span>
                  {{ t('product.info.releaseInfo') }}
                </h3>
                <div class="space-y-2 sm:space-y-3">
                  <div v-if="product.release_date || isEditing">
                    <h4 class="text-xs sm:text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1">{{ t('product.info.releaseDate') }}</h4>
                    <input
                      v-if="isEditing"
                      v-model="editForm.release_date"
                      type="text"
                      :placeholder="t('product.info.releaseDatePlaceholder')"
                      class="w-full px-2.5 sm:px-3 py-1.5 sm:py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm sm:text-base text-gray-900 dark:text-white focus:outline-none focus:border-blue-500"
                    />
                    <p v-else class="text-sm sm:text-base text-gray-900 dark:text-white">{{ product.release_date }}</p>
                  </div>
                  <div v-if="product.release_notes || isEditing">
                    <h4 class="text-xs sm:text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1">{{ t('product.info.releaseNotes') }}</h4>
                    <textarea
                      v-if="isEditing"
                      v-model="editForm.release_notes"
                      rows="3"
                      :placeholder="t('product.info.releaseNotesPlaceholder')"
                      class="w-full px-2.5 sm:px-3 py-1.5 sm:py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm sm:text-base text-gray-900 dark:text-white focus:outline-none focus:border-blue-500 resize-none"
                    ></textarea>
                    <p v-else class="text-sm sm:text-base text-gray-700 dark:text-gray-300">{{ product.release_notes }}</p>
                  </div>
                </div>
              </div>

              <!-- Features -->
              <div v-if="product.features || isEditing" class="border-t border-gray-200 dark:border-gray-700 pt-4 sm:pt-6">
                <h3 class="text-base sm:text-lg font-bold text-gray-900 dark:text-white mb-2 sm:mb-3 flex items-center">
                  <span class="mr-2 text-lg sm:text-xl">✨</span>
                  {{ t('product.info.keyFeatures') }}
                </h3>
                <div v-if="product.features && product.features.length > 0" class="space-y-1.5 sm:space-y-2">
                  <div v-for="(feature, idx) in product.features" :key="idx" class="flex items-start">
                    <span class="text-blue-500 mr-2 sm:mr-3 mt-0.5 text-sm sm:text-base">•</span>
                    <span class="text-sm sm:text-base text-gray-700 dark:text-gray-300">{{ feature }}</span>
                  </div>
                </div>
                <p v-else class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">{{ t('product.info.noFeatures') }}</p>
              </div>

              <!-- System Requirements -->
              <div v-if="product.system_requirements || isEditing" class="border-t border-gray-200 dark:border-gray-700 pt-4 sm:pt-6">
                <h3 class="text-base sm:text-lg font-bold text-gray-900 dark:text-white mb-2 sm:mb-3 flex items-center">
                  <span class="mr-2 text-lg sm:text-xl">💻</span>
                  {{ t('product.info.systemRequirements') }}
                </h3>
                <div v-if="product.system_requirements && Object.keys(product.system_requirements).length > 0" class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                  <div v-for="(value, key) in product.system_requirements" :key="key">
                    <h4 class="text-xs sm:text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1">{{ key }}</h4>
                    <p class="text-sm sm:text-base text-gray-900 dark:text-white">{{ typeof value === 'object' ? JSON.stringify(value) : value }}</p>
                  </div>
                </div>
                <p v-else class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">{{ t('product.info.noSystemRequirements') }}</p>
              </div>

              <!-- Supported Formats -->
              <div v-if="product.supported_formats || isEditing" class="border-t border-gray-200 dark:border-gray-700 pt-4 sm:pt-6">
                <h3 class="text-base sm:text-lg font-bold text-gray-900 dark:text-white mb-2 sm:mb-3 flex items-center">
                  <span class="mr-2 text-lg sm:text-xl">📂</span>
                  {{ t('product.info.supportedFormats') }}
                </h3>
                <div v-if="product.supported_formats && product.supported_formats.length > 0" class="flex flex-wrap gap-1.5 sm:gap-2">
                  <span v-for="(format, idx) in product.supported_formats" :key="idx" class="inline-block px-2.5 sm:px-3 lg:px-4 py-1.5 sm:py-2 bg-gradient-to-r from-blue-100 to-purple-100 dark:from-blue-900 dark:to-purple-900 text-blue-700 dark:text-blue-300 rounded-lg text-xs sm:text-sm font-medium border border-blue-200 dark:border-blue-700">
                    {{ format }}
                  </span>
                </div>
                <p v-else class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">{{ t('product.info.noSupportedFormats') }}</p>
              </div>

              <!-- Installation Info -->
              <div v-if="product.installation_info || isEditing" class="border-t border-gray-200 dark:border-gray-700 pt-4 sm:pt-6">
                <h3 class="text-base sm:text-lg font-bold text-gray-900 dark:text-white mb-2 sm:mb-3 flex items-center">
                  <span class="mr-2 text-lg sm:text-xl">⚙️</span>
                  {{ t('product.info.installationInfo') }}
                </h3>
                <div v-if="product.installation_info && Object.keys(product.installation_info).length > 0" class="space-y-1.5 sm:space-y-2">
                  <div v-for="(value, key) in product.installation_info" :key="key">
                    <h4 class="text-xs sm:text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1">{{ key }}</h4>
                    <p class="text-sm sm:text-base text-gray-900 dark:text-white">{{ typeof value === 'object' ? JSON.stringify(value) : value }}</p>
                  </div>
                </div>
                <p v-else class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">{{ t('product.info.noInstallationInfo') }}</p>
              </div>
            </div>

            <!-- Versions Tab -->
            <div v-if="activeTab === 'versions'">
              <h3 class="text-base sm:text-lg lg:text-xl font-bold text-gray-900 dark:text-white mb-4 sm:mb-6 flex items-center">
                <span class="mr-2 text-lg sm:text-xl">📦</span>
                {{ t('product.versions.title') }}
              </h3>
              <div v-if="product.versions?.length === 0" class="text-center py-12 sm:py-16">
                <div class="w-16 h-16 sm:w-20 sm:h-20 mx-auto mb-4 sm:mb-6 bg-gradient-to-br from-gray-100 to-gray-50 dark:from-gray-700 dark:to-gray-800 rounded-2xl sm:rounded-3xl flex items-center justify-center">
                  <svg class="w-8 h-8 sm:w-10 sm:h-10 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                  </svg>
                </div>
                <h3 class="text-base sm:text-lg font-semibold text-gray-900 dark:text-white mb-1.5 sm:mb-2">{{ t('product.versions.noVersions') }}</h3>
                <p class="text-gray-500 dark:text-gray-400 text-xs sm:text-sm">{{ t('product.versions.noVersionsDesc') }}</p>
              </div>
              <div v-else class="space-y-3 sm:space-y-4">
                <div
                  v-for="version in product.versions"
                  :key="version.id"
                  class="flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 sm:p-5 lg:p-6 border border-gray-200 dark:border-gray-700 rounded-xl sm:rounded-2xl hover:border-blue-200 dark:hover:border-blue-700 hover:shadow-md transition-all bg-gradient-to-br from-gray-50 to-white dark:from-gray-700 dark:to-gray-800 gap-3 sm:gap-4"
                >
                  <div class="flex-1 w-full sm:w-auto">
                    <div class="flex items-center mb-1.5 sm:mb-2">
                      <svg class="w-4 h-4 sm:w-5 sm:h-5 text-blue-500 dark:text-blue-400 mr-1.5 sm:mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                      </svg>
                      <p class="font-semibold text-sm sm:text-base text-gray-900 dark:text-white truncate">{{ version.file_name }}</p>
                    </div>

                    <div class="flex flex-wrap items-center gap-2 sm:gap-3 lg:gap-4 text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-2">
                      <span class="flex items-center">
                        <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4 mr-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                        </svg>
                        {{ t('product.versions.version') }} {{ version.version_name }}
                      </span>
                      <span class="flex items-center">
                        <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4 mr-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                        </svg>
                        {{ formatSize(version.file_size) }}
                      </span>
                      <span class="flex items-center">
                        <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4 mr-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        {{ formatDate(version.release_date) }}
                      </span>
                      <!-- 파일 삭제 상태 뱃지 -->
                      <span
                        v-if="version.file_exists === false"
                        class="inline-flex items-center px-2 py-1 rounded-lg text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-700"
                      >
                        {{ t('productDetail.fileNotFoundBadge') }}
                      </span>
                      <!-- 포터블/설치형 뱃지 -->
                      <span
                        v-if="version.is_portable"
                        class="inline-flex items-center px-2 py-1 rounded-lg text-xs font-medium bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-700"
                      >
                        <span class="mr-1">🎒</span>
                        {{ t('product.versions.portable') }}
                      </span>
                      <span
                        v-else
                        class="inline-flex items-center px-2 py-1 rounded-lg text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-700"
                      >
                        <span class="mr-1">💿</span>
                        {{ t('product.versions.installer') }}
                      </span>
                    </div>

                    <!-- 파일 경로 표시 (/library부터) -->
                    <div class="flex items-start gap-1.5">
                      <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                      </svg>
                      <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 font-mono break-all">
                        {{ formatFilePath(version.file_path) }}
                      </p>
                    </div>
                  </div>
                  <!-- 파일이 삭제된 경우 삭제 버튼 표시 (관리자만) -->
                  <button
                    v-if="version.file_exists === false && authStore.user?.role === 'admin'"
                    @click="deleteVersion(version.id)"
                    class="w-full sm:w-auto flex items-center justify-center px-4 sm:px-5 lg:px-6 py-2.5 sm:py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg sm:rounded-xl hover:from-red-600 hover:to-red-700 transition-all shadow-md hover:shadow-lg font-medium text-sm sm:text-base"
                  >
                    <svg class="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    {{ t('productDetail.deleteFromDb') }}
                  </button>
                  <!-- 파일이 없는 경우 비활성화된 다운로드 버튼 (일반 사용자) -->
                  <button
                    v-else-if="version.file_exists === false"
                    disabled
                    class="w-full sm:w-auto flex items-center justify-center px-4 sm:px-5 lg:px-6 py-2.5 sm:py-3 bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 rounded-lg sm:rounded-xl cursor-not-allowed font-medium text-sm sm:text-base opacity-60"
                  >
                    <svg class="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                    </svg>
                    {{ t('productDetail.fileNotFound') }}
                  </button>
                  <!-- 정상 다운로드 버튼 -->
                  <button
                    v-else
                    @click="download(version.id)"
                    class="w-full sm:w-auto flex items-center justify-center px-4 sm:px-5 lg:px-6 py-2.5 sm:py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg sm:rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all shadow-md hover:shadow-lg font-medium text-sm sm:text-base"
                  >
                    <svg class="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    {{ t('product.versions.download') }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Screenshots Tab (3번 요구사항: 최대 4개까지 표시) -->
            <div v-if="activeTab === 'screenshots'">
              <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-4 mb-4 sm:mb-6">
                <h3 class="text-base sm:text-lg lg:text-xl font-bold text-gray-900 dark:text-white flex items-center">
                  <span class="mr-2 text-lg sm:text-xl">📸</span>
                  {{ t('product.screenshots.title') }}
                </h3>

                <!-- Screenshot Buttons (Admin only) -->
                <div v-if="authStore.user?.role === 'admin'" class="flex gap-2">
                  <!-- 스크린샷 검색 -->
                  <button
                    @click="openScreenshotSearch"
                    class="flex items-center justify-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-2 sm:py-2.5 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-lg sm:rounded-xl hover:shadow-lg transition-all duration-200 font-medium text-xs sm:text-sm"
                  >
                    <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    <span>{{ t('product.screenshots.searchButton') }}</span>
                  </button>
                </div>
              </div>

              <div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
                  <div
                    v-for="idx in 4"
                    :key="idx"
                    class="group relative bg-gray-100 dark:bg-gray-700 rounded-xl sm:rounded-2xl overflow-hidden border border-gray-200 dark:border-gray-600 hover:shadow-lg transition-all"
                    :class="{ 'cursor-pointer': !isEditing && getScreenshotAtIndex(idx - 1) }"
                    @click="!isEditing && getScreenshotAtIndex(idx - 1) && openScreenshot(getScreenshotAtIndex(idx - 1))"
                  >
                    <div class="aspect-video relative">
                      <!-- 스크린샷이 있는 경우 -->
                      <img
                        v-if="getScreenshotAtIndex(idx - 1)"
                        :src="getScreenshotAtIndex(idx - 1)"
                        :alt="`${product.title} 스크린샷 ${idx}`"
                        class="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
                        @error="handleImageError($event)"
                      />

                      <!-- 스크린샷이 없는 경우 -->
                      <div v-else class="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-50 dark:from-gray-700 dark:to-gray-800">
                        <svg class="w-12 h-12 sm:w-16 sm:h-16 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </div>

                      <div v-if="!isEditing && getScreenshotAtIndex(idx - 1)" class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-opacity flex items-center justify-center">
                        <svg class="w-10 h-10 sm:w-12 sm:h-12 text-white opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                        </svg>
                      </div>

                      <!-- Admin 전용: 업로드 버튼 -->
                      <button
                        v-if="authStore.user?.role === 'admin'"
                        @click.stop="triggerScreenshotUpload(idx - 1)"
                        class="absolute bottom-1.5 right-1.5 sm:bottom-2 sm:right-2 p-1.5 sm:p-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-lg transition-colors opacity-0 group-hover:opacity-100"
                        :title="t('product.screenshots.uploadButton')"
                      >
                        <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                      </button>

                      <!-- 편집 모드: 삭제 버튼 (스크린샷이 있을 때만) -->
                      <button
                        v-if="isEditing && getScreenshotAtIndex(idx - 1)"
                        @click.stop="deleteScreenshot(idx - 1)"
                        class="absolute top-1.5 right-1.5 sm:top-2 sm:right-2 p-1.5 sm:p-2 bg-red-600 hover:bg-red-700 text-white rounded-lg shadow-lg transition-colors"
                        :title="t('product.screenshots.deleteButton')"
                      >
                        <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                    <div class="p-3 sm:p-4 bg-white dark:bg-gray-800">
                      <p class="text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('product.screenshots.screenshot') }} {{ idx }}</p>
                    </div>
                  </div>
                </div>

                <!-- 숨겨진 파일 업로드 input (각 스크린샷마다) -->
                <input
                  v-for="idx in 4"
                  :key="`screenshot-upload-${idx-1}`"
                  :ref="el => screenshotFileInputs[idx-1] = el"
                  type="file"
                  accept="image/*"
                  class="hidden"
                  @change="uploadScreenshot($event, idx-1)"
                />
              </div>
            </div>

            <!-- Installation Guide Tab -->
            <div v-if="activeTab === 'installation'">
              <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-4 mb-4 sm:mb-6">
                <h3 class="text-base sm:text-lg lg:text-xl font-bold text-gray-900 dark:text-white flex items-center">
                  <span class="mr-2 text-lg sm:text-xl">⚙️</span>
                  {{ t('product.installation.title') }}
                </h3>

                <!-- 가이드 작성 버튼 (가이드가 없고, 편집/작성 모드가 아닐 때 표시) -->
                <button
                  v-if="authStore.user?.role === 'admin' && !isEditing && !isWritingGuide && (!product.installation_guide || product.installation_guide.trim() === '')"
                  @click="startWritingGuide"
                  class="w-full sm:w-auto px-3 sm:px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg flex items-center justify-center gap-1.5 sm:gap-2 text-sm sm:text-base"
                >
                  <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  {{ t('product.installation.writeGuide') }}
                </button>

                <!-- 수정/삭제 버튼 (가이드가 있고, 편집/작성 모드가 아닐 때 표시) -->
                <div v-if="authStore.user?.role === 'admin' && !isEditing && !isWritingGuide && product.installation_guide && product.installation_guide.trim() !== ''" class="w-full sm:w-auto flex gap-2">
                  <button
                    @click="startWritingGuide"
                    class="flex-1 sm:flex-none px-3 sm:px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-1.5 sm:gap-2 text-sm sm:text-base"
                  >
                    <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    {{ t('product.installation.edit') }}
                  </button>
                  <button
                    @click="deleteGuide"
                    :disabled="saving"
                    class="flex-1 sm:flex-none px-3 sm:px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-1.5 sm:gap-2 text-sm sm:text-base"
                  >
                    <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    <span class="hidden sm:inline">{{ t('product.installation.delete') }}</span>
                  </button>
                </div>

                <!-- 저장/취소 버튼 (작성 모드일 때만 표시) -->
                <div v-if="isWritingGuide && !isEditing" class="w-full sm:w-auto flex gap-2">
                  <button
                    @click="saveGuide"
                    :disabled="saving"
                    class="flex-1 sm:flex-none px-3 sm:px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-1.5 sm:gap-2 text-sm sm:text-base"
                  >
                    <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    {{ saving ? t('product.installation.saving') : t('product.installation.save') }}
                  </button>
                  <button
                    @click="cancelWritingGuide"
                    :disabled="saving"
                    class="flex-1 sm:flex-none px-3 sm:px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors disabled:opacity-50 text-sm sm:text-base"
                  >
                    {{ t('product.installation.cancel') }}
                  </button>
                </div>
              </div>

              <!-- 가이드가 없고, 편집/작성 모드가 아닐 때 -->
              <div v-if="!isEditing && !isWritingGuide && (!product.installation_guide || product.installation_guide.trim() === '')" class="text-center py-12 sm:py-16">
                <div class="w-16 h-16 sm:w-20 sm:h-20 mx-auto mb-4 sm:mb-6 bg-gradient-to-br from-gray-100 to-gray-50 dark:from-gray-700 dark:to-gray-800 rounded-2xl sm:rounded-3xl flex items-center justify-center">
                  <svg class="w-8 h-8 sm:w-10 sm:h-10 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 class="text-base sm:text-lg font-semibold text-gray-900 dark:text-white mb-1.5 sm:mb-2">{{ t('product.installation.noGuideTitle') }}</h3>
                <p class="text-gray-500 dark:text-gray-400 text-xs sm:text-sm">{{ t('product.installation.noGuideDescAdmin') }}</p>
              </div>

              <!-- TinyMCE Editor (편집 모드 또는 작성 모드) -->
              <div v-else-if="isEditing || isWritingGuide">
                <textarea
                  id="installation-guide-editor"
                  v-model="editForm.installation_guide"
                  class="w-full"
                ></textarea>
              </div>

              <!-- HTML Content (보기 모드) -->
              <div v-else class="prose prose-sm sm:prose-base lg:prose-lg dark:prose-invert max-w-none" v-html="product.installation_guide"></div>
            </div>

            <!-- Patches Tab -->
            <div v-if="activeTab === 'patches'">
              <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-4 mb-4 sm:mb-6">
                <h3 class="text-base sm:text-lg lg:text-xl font-bold text-gray-900 dark:text-white flex items-center">
                  <span class="mr-2 text-lg sm:text-xl">📦</span>
                  {{ t('product.patches.title') }}
                </h3>
              </div>

              <!-- 파일 업로드 영역 (관리자만) -->
              <div v-if="authStore.user?.role === 'admin'" class="mb-6">
                <div
                  @drop.prevent="handleDrop"
                  @dragover.prevent="isDragging = true"
                  @dragleave.prevent="isDragging = false"
                  :class="[
                    'border-2 border-dashed rounded-lg p-8 text-center transition-colors',
                    isDragging
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800'
                  ]"
                >
                  <input
                    ref="fileInput"
                    type="file"
                    @change="handleFileSelect"
                    class="hidden"
                  />
                  <div class="space-y-4">
                    <svg class="w-16 h-16 mx-auto text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <div>
                      <button
                        @click="$refs.fileInput.click()"
                        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        {{ t('common.selectFile') }}
                      </button>
                      <p class="text-sm text-gray-600 dark:text-gray-400 mt-2">{{ t('common.dragAndDrop') }}</p>
                    </div>
                  </div>
                </div>

                <!-- 파일 업로드 폼 (파일 선택 후) -->
                <div v-if="selectedFile" class="mt-4 p-4 bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                  <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center gap-3">
                      <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <div>
                        <p class="font-medium text-gray-900 dark:text-white">{{ selectedFile.name }}</p>
                        <p class="text-sm text-gray-500 dark:text-gray-400">{{ formatFileSize(selectedFile.size) }}</p>
                      </div>
                    </div>
                    <button
                      @click="selectedFile = null"
                      class="p-2 text-gray-500 hover:text-red-600 transition-colors"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  <div class="space-y-3">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('product.patches.fileType') }}</label>
                      <select v-model="uploadForm.type" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
                        <option value="patch">{{ t('product.patches.types.patch') }}</option>
                        <option value="crack">{{ t('product.patches.types.crack') }}</option>
                        <option value="manual">{{ t('product.patches.types.manual') }}</option>
                        <option value="other">{{ t('product.patches.types.other') }}</option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('product.patches.descriptionOptional') }}</label>
                      <textarea
                        v-model="uploadForm.note"
                        rows="2"
                        :placeholder="t('product.patches.descriptionPlaceholder')"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white resize-none"
                      ></textarea>
                    </div>
                    <div class="flex gap-2">
                      <button
                        @click="uploadFile"
                        :disabled="uploading"
                        class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                      >
                        <svg v-if="!uploading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                        </svg>
                        <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        {{ uploading ? t('common.uploading') : t('common.upload') }}
                      </button>
                      <button
                        @click="selectedFile = null"
                        :disabled="uploading"
                        class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors disabled:opacity-50"
                      >
                        {{ t('common.cancel') }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 링크 관리 섹션 (관리자만) -->
              <div v-if="authStore.user?.role === 'admin'" class="mb-6">
                <div class="flex items-center justify-between mb-3">
                  <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    {{ t('product.patches.linksTitle') }} ({{ patchLinks.length }}/5)
                  </h4>
                  <button
                    v-if="patchLinks.length < 5 && !showAddLinkForm"
                    @click="showAddLinkForm = true"
                    class="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-1"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    {{ t('product.patches.addLink') }}
                  </button>
                </div>

                <!-- 링크 추가 폼 -->
                <div v-if="showAddLinkForm" class="mb-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-600">
                  <div class="space-y-3">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('product.patches.linkTitle') }}</label>
                      <input
                        v-model="newLink.title"
                        type="text"
                        :placeholder="t('product.patches.linkTitlePlaceholder')"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('product.patches.linkUrl') }}</label>
                      <input
                        v-model="newLink.url"
                        type="url"
                        :placeholder="t('product.patches.linkUrlPlaceholder')"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                    <div class="flex gap-2">
                      <button
                        @click="addPatchLink"
                        class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                      >
                        {{ t('common.add') }}
                      </button>
                      <button
                        @click="showAddLinkForm = false; newLink = { title: '', url: '' }"
                        class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                      >
                        {{ t('common.cancel') }}
                      </button>
                    </div>
                  </div>
                </div>

                <!-- 링크 목록 -->
                <div v-if="patchLinks.length > 0" class="space-y-2 mb-4">
                  <div
                    v-for="(link, index) in patchLinks"
                    :key="index"
                    class="flex items-center justify-between p-3 bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
                  >
                    <div class="flex items-center gap-3 flex-1 min-w-0">
                      <svg class="w-5 h-5 text-blue-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                      </svg>
                      <div class="flex-1 min-w-0">
                        <p class="font-medium text-gray-900 dark:text-white truncate">{{ link.title }}</p>
                        <p class="text-sm text-gray-500 dark:text-gray-400 truncate">{{ link.url }}</p>
                      </div>
                    </div>
                    <button
                      @click="removePatchLink(index)"
                      class="p-2 text-gray-500 hover:text-red-600 transition-colors flex-shrink-0"
                      :title="t('common.delete')"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>

                <!-- 링크 저장 버튼 -->
                <button
                  v-if="patchLinks.length > 0 || (product?.patch_links?.length || 0) > 0"
                  @click="savePatchLinks"
                  :disabled="savingLinks"
                  class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <svg v-if="!savingLinks" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ savingLinks ? t('common.saving') : t('product.patches.saveLinks') }}
                </button>
              </div>

              <!-- 링크 목록 (일반 사용자용 - 읽기 전용) -->
              <div v-else-if="product?.patch_links?.length > 0" class="mb-6">
                <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                  {{ t('product.patches.linksTitle') }}
                </h4>
                <div class="space-y-2">
                  <div
                    v-for="(link, index) in product.patch_links"
                    :key="index"
                    @click="openPatchLink(link.url)"
                    class="flex items-center gap-3 p-3 bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500 cursor-pointer transition-colors"
                  >
                    <svg class="w-5 h-5 text-blue-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    <div class="flex-1 min-w-0">
                      <p class="font-medium text-blue-600 dark:text-blue-400 truncate">{{ link.title }}</p>
                      <p class="text-sm text-gray-500 dark:text-gray-400 truncate">{{ link.url }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 파일 목록 -->
              <div v-if="attachments && attachments.length > 0" class="space-y-3">
                <div
                  v-for="attachment in attachments"
                  :key="attachment.id"
                  class="flex items-center justify-between p-4 bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500 transition-colors"
                >
                  <div class="flex items-center gap-3 flex-1 min-w-0">
                    <div class="flex-shrink-0">
                      <svg class="w-10 h-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center gap-2 mb-1">
                        <p class="font-medium text-gray-900 dark:text-white truncate">{{ attachment.file_name }}</p>
                        <span :class="[
                          'px-2 py-0.5 text-xs rounded-full flex-shrink-0',
                          attachment.type === 'patch' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' :
                          attachment.type === 'crack' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300' :
                          attachment.type === 'manual' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300' :
                          'bg-gray-100 text-gray-800 dark:bg-gray-600 dark:text-gray-300'
                        ]">
                          {{ t(`product.patches.types.${attachment.type}`) }}
                        </span>
                      </div>
                      <p class="text-sm text-gray-500 dark:text-gray-400">{{ formatFileSize(attachment.file_size) }} · {{ formatDate(attachment.created_at) }}</p>
                      <p v-if="attachment.note" class="text-sm text-gray-600 dark:text-gray-300 mt-1">{{ attachment.note }}</p>
                    </div>
                  </div>
                  <div class="flex items-center gap-2 ml-4">
                    <button
                      @click="downloadPatchFile(attachment.id, attachment.file_name)"
                      class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      {{ t('common.download') }}
                    </button>
                    <button
                      v-if="authStore.user?.role === 'admin'"
                      @click="deleteAttachment(attachment.id)"
                      class="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                      :title="t('common.delete')"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              <!-- 파일 없음 -->
              <div v-else class="text-center py-12">
                <div class="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-gray-100 to-gray-50 dark:from-gray-700 dark:to-gray-800 rounded-3xl flex items-center justify-center">
                  <svg class="w-10 h-10 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">{{ t('product.patches.noFiles') }}</h3>
                <p class="text-gray-500 dark:text-gray-400 text-sm">
                  {{ authStore.user?.role === 'admin' ? t('product.patches.noFilesAdmin') : t('product.patches.noFilesDesc') }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Logo Search Dialog -->
    <ProductLogoSearchDialog
      :is-open="logoSearchDialogOpen"
      :product="product"
      @close="closeLogoSearchDialog"
      @saved="handleLogoSaved"
    />

    <!-- Screenshot Search Dialog -->
    <ProductImageSearchDialog
      :is-open="screenshotSearchDialogOpen"
      :product="product"
      @close="closeScreenshotSearchDialog"
      @saved="handleScreenshotsSaved"
    />

    <!-- Screenshot Viewer Dialog -->
    <div
      v-if="screenshotViewerOpen"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-75"
      @click="screenshotViewerOpen = false"
    >
      <div class="relative max-w-7xl max-h-full" @click.stop>
        <button
          @click="screenshotViewerOpen = false"
          class="absolute -top-12 right-0 p-2 text-white hover:text-gray-300 transition-colors"
        >
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        <img
          :src="currentScreenshot"
          class="max-w-full max-h-[90vh] object-contain rounded-lg"
          @click.stop
        />
      </div>
    </div>

    <!-- Reference Sites Dialog -->
    <div
      v-if="showReferenceSitesDialog"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50"
      @click="showReferenceSitesDialog = false"
    >
      <div
        class="relative max-w-4xl w-full max-h-[80vh] bg-white dark:bg-gray-800 rounded-2xl shadow-2xl overflow-hidden"
        @click.stop
      >
        <!-- Dialog Header -->
        <div class="bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-4 flex items-center justify-between">
          <div class="flex items-center">
            <svg class="w-6 h-6 text-white mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <h3 class="text-xl font-bold text-white">{{ t('productDetail.referenceSitesTitle') }}</h3>
          </div>
          <button
            @click="showReferenceSitesDialog = false"
            class="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Dialog Content -->
        <div class="p-6 overflow-y-auto max-h-[calc(80vh-80px)]">
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
            {{ t('productDetail.referenceSitesDescription') }}
          </p>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <a
              v-for="site in referenceSites"
              :key="site.url"
              :href="site.url"
              target="_blank"
              rel="noopener noreferrer"
              class="flex items-center px-4 py-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900 border border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-700 transition-all group"
            >
              <svg class="w-5 h-5 mr-2 flex-shrink-0 text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300 group-hover:text-blue-600 dark:group-hover:text-blue-400 flex-1 truncate">
                {{ site.name }}
              </span>
              <svg class="w-4 h-4 ml-auto flex-shrink-0 text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Logo URL Input Dialog -->
    <div
      v-if="showLogoUrlDialog"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50"
      @click="showLogoUrlDialog = false"
    >
      <div
        class="relative max-w-lg w-full bg-white dark:bg-gray-800 rounded-2xl shadow-2xl overflow-hidden"
        @click.stop
      >
        <div class="bg-gradient-to-r from-green-500 to-emerald-600 px-6 py-4 flex items-center justify-between">
          <div class="flex items-center">
            <svg class="w-6 h-6 text-white mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <h3 class="text-xl font-bold text-white">{{ t('productDetail.addLogoFromUrlTitle') }}</h3>
          </div>
          <button @click="showLogoUrlDialog = false" class="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('productDetail.imageUrl') }}</label>
          <input
            v-model="logoUrlInput"
            type="url"
            class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent"
            :placeholder="t('productDetail.imageUrlPlaceholder')"
            @keyup.enter="addLogoFromUrl"
          />
          <div class="flex gap-3 mt-6">
            <button
              @click="showLogoUrlDialog = false"
              class="flex-1 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
            >
              {{ t('common.cancel') }}
            </button>
            <button
              @click="addLogoFromUrl"
              class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              {{ t('common.add') }}
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { productsApi } from '../api/products'
import { imagesApi } from '../api/images'
import attachmentsApi from '../api/attachments'
import { settingsApi } from '../api/settings'
import { useAuthStore } from '../store/auth'
import { useThemeStore } from '../store/theme'
import { getDownloadUrl, getIconUrl, getBackendUrl } from '../utils/env'
import ProductLogoSearchDialog from '../components/product/ProductLogoSearchDialog.vue'
import ProductImageSearchDialog from '../components/product/ProductImageSearchDialog.vue'
import { useDialog } from '../composables/useDialog'

const route = useRoute()
const { t, locale } = useI18n({ useScope: 'global' })
const authStore = useAuthStore()
const themeStore = useThemeStore()
const { alert, confirm } = useDialog()
const product = ref(null)
const activeTab = ref('info')
const loading = ref(true)
const error = ref(null)
const isEditing = ref(false)
const saving = ref(false)
const showReferenceSites = ref(false)
const showReferenceSitesDialog = ref(false)
const logoSearchDialogOpen = ref(false)
const screenshotSearchDialogOpen = ref(false)
const screenshotViewerOpen = ref(false)
const currentScreenshot = ref('')
const iconTimestamp = ref(Date.now()) // 로고 캐시 버스팅용 타임스탬프
const isWritingGuide = ref(false) // 설치방법 가이드 작성 모드
const screenshotFileInputs = ref([]) // 스크린샷 파일 input refs
const showLogoUrlDialog = ref(false) // 로고 URL 입력 다이얼로그
const logoUrlInput = ref('') // 로고 URL 입력값
const configCategories = ref([]) // config에서 가져온 카테고리 목록

// 로고 URL에 타임스탬프 추가 (브라우저 캐시 우회)
const iconUrlWithTimestamp = computed(() => {
  if (!product.value?.icon_url) return null
  const url = getIconUrl(product.value.icon_url)
  if (!url) return null
  const separator = url.includes('?') ? '&' : '?'
  return `${url}${separator}t=${iconTimestamp.value}`
})

let editorInstance = null

// 편집 폼 데이터
const editForm = ref({
  title: '',
  subtitle: '',
  vendor: '',
  category: '',
  description: '',
  official_website: '',
  platform: '',
  license_type: '',
  detailed_description: '',
  icon_url: '',
  installation_guide: '',
  release_date: '',
  release_notes: '',
  screenshots: []
})

// 카테고리 목록 (config에서 동적으로 가져옴)
const categories = computed(() => configCategories.value.map(cat => cat.name))

// 카테고리 아이콘 맵 (config에서 동적으로 가져옴)
const categoryIcons = computed(() => {
  const icons = {}
  configCategories.value.forEach(cat => {
    icons[cat.name] = cat.icon || '📦'
  })
  return icons
})

const referenceSites = [
  { name: 'Portable Freeware', url: 'https://www.portablefreeware.com/' },
  { name: 'Giveaway of the Day', url: 'https://www.giveawayoftheday.com/' },
  { name: 'Softpedia', url: 'https://www.softpedia.com/' },
  { name: 'CNET Download', url: 'https://download.cnet.com/' },
  { name: 'Softonic', url: 'https://en.softonic.com/' },
  { name: 'SnapFiles', url: 'https://www.snapfiles.com/' },
  { name: 'Microsoft Store', url: 'https://apps.microsoft.com/home?hl=ko-KR&gl=KR' },
  { name: 'Uptodown', url: 'https://kr.uptodown.com/windows' },
  { name: 'SoftPick (한국)', url: 'https://www.softpick.co.kr/' }
]

const getCategoryIcon = (category) => {
  return categoryIcons.value[category] || '📦'
}

// 카테고리 레이블 가져오기 (한글 표시용)
const getCategoryLabel = (categoryName) => {
  const cat = configCategories.value.find(c => c.name === categoryName)
  return cat?.label || categoryName
}

const tabClass = (tab) => {
  return activeTab.value === tab
    ? 'py-4 border-b-2 border-blue-500 dark:border-blue-400 text-blue-600 dark:text-blue-400 font-medium'
    : 'py-4 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  if (bytes >= 1073741824) return (bytes / 1073741824).toFixed(2) + ' GB'
  if (bytes >= 1048576) return (bytes / 1048576).toFixed(2) + ' MB'
  return (bytes / 1024).toFixed(2) + ' KB'
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })
  } catch {
    return dateStr
  }
}

const formatFilePath = (fullPath) => {
  if (!fullPath) return ''
  // /library 이후의 경로만 표시
  const libraryIndex = fullPath.indexOf('/library')
  let path = libraryIndex !== -1 ? fullPath.substring(libraryIndex) : fullPath

  // 경로를 /로 분리
  const parts = path.split('/').filter(Boolean)

  // /library/폴더1/폴더2/파일명 형태에서 마지막 2개 경로만 표시
  if (parts.length > 3) {
    // library를 제외한 경로가 3개 이상이면 축약
    const lastTwo = parts.slice(-2)
    return `.../${lastTwo.join('/')}`
  }

  return path
}

const parseDetailedDescription = (description) => {
  if (!description) return []
  return description.split('|').map(line => line.trim()).filter(line => line.length > 0)
}

const openScreenshot = (url) => {
  currentScreenshot.value = url
  screenshotViewerOpen.value = true
}

const handleImageError = (event) => {
  event.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23f0f0f0" width="400" height="300"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif"%3E이미지를 불러올 수 없습니다%3C/text%3E%3C/svg%3E'
}

const download = (versionId) => {
  const token = localStorage.getItem('access_token')
  window.open(getDownloadUrl(versionId, token), '_blank')
}

// 버전 삭제 (파일이 없는 경우)
const deleteVersion = async (versionId) => {
  const confirmed = await confirm.danger(t('productDetail.deleteVersionConfirm'))
  if (!confirmed) {
    return
  }

  try {
    // 해당 버전만 삭제하는 API가 필요하지만, 우선 전체 정리 API 사용
    await productsApi.cleanupDeleted()
    await alert.success(t('productDetail.deletedFilesCleanedUp'))

    // 제품 정보 새로고침
    await loadProduct()
  } catch (error) {
    console.error('Failed to delete version:', error)
    await alert.error(t('productDetail.versionDeleteFailed'))
  }
}

// 아이콘 업로드 처리
const handleIconUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  if (file.size > 5 * 1024 * 1024) {
    await alert.warning(t('productDetail.fileSizeExceeds'))
    return
  }

  if (!file.type.startsWith('image/')) {
    await alert.warning(t('productDetail.imageOnly'))
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    editForm.value.icon_url = e.target.result
  }
  reader.readAsDataURL(file)
}

// TinyMCE 초기화
const initTinyMCE = () => {
  // 편집 모드 또는 가이드 작성 모드일 때만 초기화
  if (!isEditing.value && !isWritingGuide.value) return

  if (window.tinymce) {
    initEditor()
    return
  }

  const script = document.createElement('script')
  script.src = '/tinymce/tinymce.min.js'
  script.onload = () => {
    initEditor()
  }
  document.head.appendChild(script)
}

const initEditor = () => {
  // 기존 에디터 인스턴스가 있으면 제거
  const existingEditor = window.tinymce.get('installation-guide-editor')
  if (existingEditor) {
    existingEditor.remove()
  }

  window.tinymce.init({
    selector: '#installation-guide-editor',
    license_key: 'gpl',
    height: 500,
    menubar: true,
    plugins: [
      'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
      'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
      'insertdatetime', 'media', 'table', 'help', 'wordcount'
    ],
    toolbar: 'undo redo | blocks | ' +
      'bold italic forecolor backcolor | alignleft aligncenter ' +
      'alignright alignjustify | bullist numlist outdent indent | ' +
      'link image media table | removeformat code | help',
    images_upload_handler: (blobInfo, progress) => new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => {
        resolve(reader.result)
      }
      reader.onerror = () => {
        reject('Image upload failed')
      }
      reader.readAsDataURL(blobInfo.blob())
    }),
    convert_urls: false,
    relative_urls: false,
    remove_script_host: false,
    content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 14px; line-height: 1.6; }',
    language: locale.value === 'ko' ? 'ko_KR' : 'en',
    branding: false,
    promotion: false,
    resize: false,
    statusbar: true,
    elementpath: false,
    skin: themeStore.isDark ? 'oxide-dark' : 'oxide',
    content_css: themeStore.isDark ? 'dark' : 'default',
    placeholder: t('product.installation.placeholder'),
    setup: (editor) => {
      editorInstance = editor
      editor.on('init', () => {
        if (editForm.value.installation_guide) {
          editor.setContent(editForm.value.installation_guide)
        }
      })
      editor.on('change keyup', () => {
        editForm.value.installation_guide = editor.getContent()
      })
    }
  })
}

// 테마 변경 감지하여 에디터 재초기화
watch(() => themeStore.isDark, () => {
  if (editorInstance && (isEditing.value || isWritingGuide.value)) {
    const currentContent = editorInstance.getContent()
    editorInstance.remove()
    initEditor()
    setTimeout(() => {
      if (window.tinymce.get('installation-guide-editor')) {
        window.tinymce.get('installation-guide-editor').setContent(currentContent)
      }
    }, 100)
  }
})

// 언어 변경 감지하여 에디터 재초기화
watch(() => locale.value, () => {
  if (editorInstance && (isEditing.value || isWritingGuide.value)) {
    const currentContent = editorInstance.getContent()
    editorInstance.remove()
    initEditor()
    setTimeout(() => {
      if (window.tinymce.get('installation-guide-editor')) {
        window.tinymce.get('installation-guide-editor').setContent(currentContent)
      }
    }, 100)
  }
})

// 편집 모드 변경 감지
watch(isEditing, (newValue) => {
  if (newValue && activeTab.value === 'installation') {
    setTimeout(() => {
      initTinyMCE()
    }, 100)
  } else if (!newValue && editorInstance && !isWritingGuide.value) {
    editorInstance.remove()
    editorInstance = null
  }
})

// 가이드 작성 모드 변경 감지
watch(isWritingGuide, (newValue) => {
  if (newValue && activeTab.value === 'installation') {
    setTimeout(() => {
      initTinyMCE()
    }, 100)
  } else if (!newValue && editorInstance && !isEditing.value) {
    editorInstance.remove()
    editorInstance = null
  }
})

// 편집 시작
const startEdit = () => {
  isEditing.value = true
  editForm.value = {
    title: product.value.title || '',
    subtitle: product.value.subtitle || '',
    vendor: product.value.vendor || '',
    category: product.value.category || '',
    description: product.value.description || '',
    official_website: product.value.official_website || '',
    platform: product.value.platform || '',
    license_type: product.value.license_type || '',
    detailed_description: product.value.detailed_description || '',
    icon_url: product.value.icon_url || '',
    installation_guide: product.value.installation_guide || '',
    release_date: product.value.release_date || '',
    release_notes: product.value.release_notes || '',
    screenshots: product.value.screenshots ? [...product.value.screenshots] : []
  }

  if (activeTab.value === 'installation') {
    setTimeout(() => {
      initTinyMCE()
    }, 100)
  }
}

// 가이드 작성 시작
const startWritingGuide = () => {
  isWritingGuide.value = true
  editForm.value.installation_guide = product.value.installation_guide || ''
  // watch(isWritingGuide)에서 TinyMCE 초기화를 처리하므로 여기서는 제거
}

// 가이드 저장
const saveGuide = async () => {
  if (saving.value) return

  saving.value = true
  try {
    // 에디터 내용 가져오기
    if (editorInstance) {
      editForm.value.installation_guide = editorInstance.getContent()
    }

    // 외부 이미지 처리
    let processedContent = editForm.value.installation_guide
    try {
      const imageProcessResult = await imagesApi.processPostContent(processedContent)
      if (imageProcessResult.data) {
        processedContent = imageProcessResult.data.content
        const downloadedImages = imageProcessResult.data.images || []

        if (downloadedImages.length > 0) {
          console.log(`[ProductDetail] Downloaded ${downloadedImages.length} external images`)
        }
      }
    } catch (imageError) {
      console.error('이미지 처리 오류:', imageError)
      // 이미지 처리 실패 시에도 가이드 저장은 계속 진행
    }

    // 백엔드에 저장
    await productsApi.updateProduct(product.value.id, {
      installation_guide: processedContent
    })

    // 제품 정보 업데이트
    product.value.installation_guide = processedContent

    // 에디터 정리 및 작성 모드 종료
    if (editorInstance) {
      editorInstance.remove()
      editorInstance = null
    }
    isWritingGuide.value = false

    await alert.success(t('productDetail.guideSaved'))
  } catch (error) {
    console.error('Failed to save guide:', error)
    await alert.error(t('productDetail.saveFailed') + ': ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

// 가이드 작성 취소
const cancelWritingGuide = () => {
  if (editorInstance) {
    editorInstance.remove()
    editorInstance = null
  }
  isWritingGuide.value = false
  editForm.value.installation_guide = product.value.installation_guide || ''
}

// 가이드 삭제
const deleteGuide = async () => {
  const shouldDelete = await confirm.danger(t('productDetail.deleteGuide'))
  if (!shouldDelete) {
    return
  }

  saving.value = true
  try {
    // 백엔드에 빈 내용으로 업데이트
    await productsApi.updateProduct(product.value.id, {
      installation_guide: ''
    })

    // 제품 정보 업데이트
    product.value.installation_guide = ''

    await alert.success(t('productDetail.guideDeleted'))
  } catch (error) {
    console.error('Failed to delete guide:', error)
    await alert.error(t('productDetail.deleteFailed') + ': ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

// 편집 취소
const cancelEdit = () => {
  if (editorInstance) {
    editorInstance.remove()
    editorInstance = null
  }
  isEditing.value = false
  editForm.value = {
    title: '',
    subtitle: '',
    vendor: '',
    category: '',
    description: '',
    official_website: '',
    platform: '',
    license_type: '',
    detailed_description: '',
    icon_url: '',
    installation_guide: '',
    release_date: '',
    release_notes: '',
    screenshots: []
  }
}

// 편집 저장
const saveEdit = async () => {
  if (!editForm.value.title.trim()) {
    await alert.warning(t('productDetail.enterProductName'))
    return
  }

  saving.value = true
  try {
    await productsApi.updateProduct(product.value.id, editForm.value)

    const response = await productsApi.getById(product.value.id)
    product.value = response.data

    if (editorInstance) {
      editorInstance.remove()
      editorInstance = null
    }
    isEditing.value = false

    await alert.success(t('productDetail.saved'))
  } catch (error) {
    console.error('Failed to save product:', error)
    await alert.error(t('productDetail.saveFailed') + ': ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

// Logo search dialog handlers
// 로고 파일 업로드
const logoFileInput = ref(null)

const triggerLogoUpload = () => {
  logoFileInput.value?.click()
}

const handleLogoFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  try {
    const response = await imagesApi.uploadLogo(product.value.id, file)
    if (response.data.success) {
      product.value.icon_url = response.data.url
      iconTimestamp.value = Date.now()
      await alert.success(t('productDetail.logoUploaded'))
    } else {
      await alert.error(response.data.error || t('productDetail.logoUploadFailed'))
    }
  } catch (error) {
    console.error('Failed to upload logo:', error)
    await alert.error(t('productDetail.logoUploadFailed'))
  } finally {
    // input 초기화
    if (logoFileInput.value) logoFileInput.value.value = ''
  }
}

const openLogoSearch = () => {
  logoSearchDialogOpen.value = true
}

const closeLogoSearchDialog = () => {
  logoSearchDialogOpen.value = false
}

const handleLogoSaved = async (data) => {
  console.log('Logo saved from dialog', data)

  // 전달받은 icon_url로 즉시 UI 업데이트
  if (data && data.icon_url) {
    product.value.icon_url = data.icon_url
    // 타임스탬프 업데이트하여 브라우저 캐시 우회
    iconTimestamp.value = Date.now()
    console.log('Logo updated:', data.icon_url)
  }

  // 제품 정보 새로고침 (다른 필드도 업데이트되었을 수 있음)
  try {
    const response = await productsApi.getById(product.value.id)
    product.value = response.data
    // 제품 정보 로드 후에도 타임스탬프 업데이트
    iconTimestamp.value = Date.now()
  } catch (error) {
    console.error('Failed to reload product:', error)
  }

  // 다이얼로그 닫기
  closeLogoSearchDialog()
}

// Screenshot search dialog handlers
const openScreenshotSearch = () => {
  screenshotSearchDialogOpen.value = true
}

const closeScreenshotSearchDialog = () => {
  screenshotSearchDialogOpen.value = false
}

const handleScreenshotsSaved = async () => {
  console.log('Screenshots saved from dialog')
  // 제품 정보 새로고침
  try {
    const response = await productsApi.getById(product.value.id)
    product.value = response.data
  } catch (error) {
    console.error('Failed to reload product:', error)
  }

  // 다이얼로그 닫기
  closeScreenshotSearchDialog()
}

// URL로 로고 추가
const addLogoFromUrl = async () => {
  if (!logoUrlInput.value.trim()) {
    await alert.warning(t('productDetail.enterLogoUrl'))
    return
  }

  try {
    const response = await imagesApi.downloadLogo(product.value.id, logoUrlInput.value.trim())
    if (response.data.success) {
      product.value.icon_url = response.data.url
      iconTimestamp.value = Date.now()
      showLogoUrlDialog.value = false
      logoUrlInput.value = ''
      await alert.success(t('productDetail.logoAdded'))
    } else {
      await alert.error(response.data.error || t('productDetail.logoAddFailed'))
    }
  } catch (error) {
    console.error('Failed to add logo from URL:', error)
    await alert.error(t('productDetail.logoAddFailed'))
  }
}

// Delete screenshot
const deleteScreenshot = async (index) => {
  const shouldDelete = await confirm.danger(t('productDetail.deleteScreenshot'))
  if (!shouldDelete) return

  // editForm.screenshots 배열에서 해당 인덱스 제거
  if (editForm.value && editForm.value.screenshots) {
    editForm.value.screenshots = editForm.value.screenshots.filter((_, idx) => idx !== index)
  }
}

// Get screenshot at specific index
const getScreenshotAtIndex = (index) => {
  const screenshots = isEditing.value ? editForm.value.screenshots : product.value?.screenshots
  if (!screenshots || !screenshots[index]) return null

  const screenshot = screenshots[index]
  // Handle object format { url: '...' } or string format
  const screenshotPath = typeof screenshot === 'object' ? screenshot.url : screenshot

  if (!screenshotPath) return null

  // 절대 URL이면 그대로 반환
  if (screenshotPath.startsWith('http://') || screenshotPath.startsWith('https://')) {
    return screenshotPath
  }
  // 상대 경로면 그대로 반환 (nginx/vite 프록시가 처리)
  if (screenshotPath.startsWith('/static')) {
    return screenshotPath
  }
  return screenshotPath
}

// Trigger screenshot upload
const triggerScreenshotUpload = (index) => {
  if (screenshotFileInputs.value[index]) {
    screenshotFileInputs.value[index].click()
  }
}

// Upload screenshot at specific index (단일 슬롯만 교체, 다른 슬롯 유지)
const uploadScreenshot = async (event, index) => {
  const file = event.target.files[0]
  if (!file) return

  try {
    const response = await imagesApi.uploadScreenshotFile(product.value.id, file, index)

    if (response.data.success) {
      // Product 다시 로드 (백엔드가 DB를 이미 업데이트함)
      const updatedProduct = await productsApi.getById(product.value.id)
      product.value = updatedProduct.data
    } else {
      await alert.error(response.data.error || t('productDetail.screenshotUploadFailed'))
    }
  } catch (error) {
    console.error('Screenshot upload error:', error)
    await alert.error(t('productDetail.screenshotUploadFailed'))
  } finally {
    event.target.value = ''
  }
}

// Attachments (패치/크랙 파일) 관련
const attachments = ref([])
const selectedFile = ref(null)
const isDragging = ref(false)
const uploading = ref(false)
const fileInput = ref(null)
const uploadForm = ref({
  type: 'patch',
  note: ''
})

// 패치 링크 관련
const patchLinks = ref([])
const showAddLinkForm = ref(false)
const newLink = ref({ title: '', url: '' })
const editingLinkIndex = ref(-1)
const savingLinks = ref(false)

// 패치 링크 로드 (product에서 가져옴)
const loadPatchLinks = () => {
  patchLinks.value = product.value?.patch_links || []
}

// 링크 추가
const addPatchLink = () => {
  if (!newLink.value.title.trim() || !newLink.value.url.trim()) return
  if (patchLinks.value.length >= 5) {
    alert.warning(t('product.patches.maxLinksReached'))
    return
  }
  patchLinks.value.push({ ...newLink.value })
  newLink.value = { title: '', url: '' }
  showAddLinkForm.value = false
}

// 링크 삭제
const removePatchLink = (index) => {
  patchLinks.value.splice(index, 1)
}

// 링크 저장
const savePatchLinks = async () => {
  savingLinks.value = true
  try {
    await productsApi.update(product.value.id, { patch_links: patchLinks.value })
    product.value.patch_links = [...patchLinks.value]
    await alert.success(t('product.patches.linksSaved'))
  } catch (error) {
    console.error('Failed to save patch links:', error)
    await alert.error(t('product.patches.linksSaveFailed'))
  } finally {
    savingLinks.value = false
  }
}

// 링크 열기
const openPatchLink = (url) => {
  window.open(url, '_blank', 'noopener,noreferrer')
}

// 파일 선택 핸들러
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

// 드래그 앤 드롭 핸들러
const handleDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    selectedFile.value = file
  }
}

// 파일 크기 포맷팅
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 파일 업로드
const uploadFile = async () => {
  if (!selectedFile.value) return

  uploading.value = true
  try {
    await attachmentsApi.uploadAttachment(
      product.value.id,
      selectedFile.value,
      uploadForm.value.note,
      uploadForm.value.type
    )

    // 업로드 성공 후 목록 갱신
    await loadAttachments()

    // 폼 초기화
    selectedFile.value = null
    uploadForm.value.note = ''
    uploadForm.value.type = 'patch'

    await alert.success(t('product.patches.uploadSuccess'))
  } catch (error) {
    console.error('File upload error:', error)
    await alert.error(t('product.patches.uploadFailed'))
  } finally {
    uploading.value = false
  }
}

// 패치 파일 다운로드
const downloadPatchFile = async (attachmentId, filename) => {
  try {
    const response = await attachmentsApi.downloadAttachment(attachmentId)

    // Blob URL 생성 및 다운로드
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('File download error:', error)
    await alert.error(t('product.patches.downloadFailed'))
  }
}

// 패치 파일 삭제
const deleteAttachment = async (attachmentId) => {
  const shouldDelete = await confirm.danger(t('product.patches.deleteConfirm'))
  if (!shouldDelete) return

  try {
    await attachmentsApi.deleteAttachment(attachmentId)
    await loadAttachments()
    await alert.success(t('product.patches.deleteSuccess'))
  } catch (error) {
    console.error('File delete error:', error)
    await alert.error(t('product.patches.deleteFailed'))
  }
}

// 패치 파일 목록 로드
const loadAttachments = async () => {
  try {
    attachments.value = await attachmentsApi.getProductAttachments(product.value.id)
  } catch (error) {
    console.error('Failed to load attachments:', error)
    attachments.value = []
  }
}

onMounted(async () => {
  // 카테고리 목록 로드 (config에서)
  try {
    const configResponse = await settingsApi.getSection('categories')
    configCategories.value = configResponse.data || []
  } catch (e) {
    console.error('Failed to load categories from config:', e)
    configCategories.value = []
  }

  try {
    const response = await productsApi.getById(route.params.id)
    product.value = response.data

    // 패치 파일 목록 로드
    await loadAttachments()

    // 패치 링크 로드
    loadPatchLinks()
  } catch (err) {
    console.error('Failed to load product:', err)
    error.value = err.response?.data?.detail || err.message || '제품을 불러오는데 실패했습니다.'
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  if (editorInstance) {
    editorInstance.remove()
  }
})
</script>
