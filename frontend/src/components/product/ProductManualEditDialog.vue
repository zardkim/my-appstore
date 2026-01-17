<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 overflow-y-auto"
    @click.self="close"
  >
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div
        class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75 dark:bg-gray-900 dark:bg-opacity-75"
        @click="close"
      ></div>

      <!-- Modal content -->
      <div class="inline-block w-full max-w-5xl my-8 overflow-hidden text-left align-middle transition-all transform bg-white dark:bg-gray-800 shadow-2xl rounded-2xl">
        <!-- Header -->
        <div class="bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-4">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-bold text-white flex items-center gap-2">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              {{ t('manualEditDialog.title') }}
            </h3>
            <div class="flex items-center gap-2">
              <!-- 참조사이트 아이콘 -->
              <button
                @click="showReferenceSitesDialog = true"
                class="text-white hover:text-gray-200 transition-colors p-2 hover:bg-white/10 rounded-lg"
                :title="t('manualEditDialog.viewReferences')"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
              </button>
              <button
                @click="close"
                class="text-white hover:text-gray-200 transition-colors p-2 hover:bg-white/10 rounded-lg"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Body -->
        <div class="px-6 py-6 max-h-[calc(100vh-200px)] overflow-y-auto">
          <form @submit.prevent="save" class="space-y-6">
            <!-- Basic Info Section -->
            <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
              <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ t('manualEditDialog.basicInfo') }}</h4>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('manualEditDialog.productName') }}</label>
                  <input
                    v-model="formData.title"
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('manualEditDialog.subtitle') }}</label>
                  <input
                    v-model="formData.subtitle"
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('manualEditDialog.vendor') }}</label>
                  <input
                    v-model="formData.vendor"
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('manualEditDialog.category') }}</label>
                  <select
                    v-model="formData.category"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="">{{ t('manualEditDialog.selectCategory') }}</option>
                    <option value="Graphics">Graphics</option>
                    <option value="Office">Office</option>
                    <option value="Development">Development</option>
                    <option value="Utility">Utility</option>
                    <option value="Media">Media</option>
                    <option value="OS">OS</option>
                    <option value="Security">Security</option>
                    <option value="Network">Network</option>
                    <option value="Mac">Mac</option>
                    <option value="Mobile">Mobile</option>
                    <option value="Patch">Patch</option>
                    <option value="Driver">Driver</option>
                    <option value="Source">Source</option>
                    <option value="Backup">Backup</option>
                    <option value="Business">Business</option>
                    <option value="Engineering">Engineering</option>
                    <option value="Theme">Theme</option>
                    <option value="Hardware">Hardware</option>
                    <option value="Uncategorized">Uncategorized</option>
                  </select>
                </div>
                <div class="col-span-2">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('manualEditDialog.shortDescription') }}</label>
                  <textarea
                    v-model="formData.description"
                    rows="3"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- Extended Info Section -->
            <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
              <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ t('manualEditDialog.extendedInfo') }}</h4>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('manualEditDialog.officialWebsite') }}</label>
                  <input
                    v-model="formData.official_website"
                    type="url"
                    placeholder="https://example.com"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('manualEditDialog.downloadUrl') }}</label>
                  <input
                    v-model="formData.download_url"
                    type="url"
                    :placeholder="t('manualEditDialog.downloadUrlPlaceholder')"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('manualEditDialog.supportedSpecs') }}</label>
                  <input
                    v-model="formData.license_type"
                    type="text"
                    :placeholder="t('manualEditDialog.supportedSpecsPlaceholder')"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('manualEditDialog.platform') }}</label>
                  <input
                    v-model="formData.platform"
                    type="text"
                    :placeholder="t('manualEditDialog.platformPlaceholder')"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('manualEditDialog.releaseDate') }}</label>
                  <input
                    v-model="formData.release_date"
                    type="text"
                    :placeholder="t('manualEditDialog.releaseDatePlaceholder')"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('manualEditDialog.supportedFormats') }}</label>
                  <input
                    v-model="supportedFormatsText"
                    type="text"
                    :placeholder="t('manualEditDialog.supportedFormatsPlaceholder')"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <div class="col-span-2">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('manualEditDialog.keyFeatures') }}</label>
                  <textarea
                    v-model="featuresText"
                    rows="4"
                    :placeholder="t('manualEditDialog.keyFeaturesPlaceholder')"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  ></textarea>
                </div>
                <div class="col-span-2">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('manualEditDialog.releaseNotes') }}</label>
                  <textarea
                    v-model="formData.release_notes"
                    rows="3"
                    :placeholder="t('manualEditDialog.releaseNotesPlaceholder')"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  ></textarea>
                </div>
                <div class="col-span-2">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ t('manualEditDialog.systemRequirements') }}</label>
                  <textarea
                    v-model="systemRequirementsText"
                    rows="4"
                    placeholder='{"OS": "Windows 10+", "CPU": "Intel Core i5", "RAM": "8GB"}'
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- Images Section -->
            <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
              <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ t('manualEditDialog.images') }}</h4>

              <!-- Logo -->
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('manualEditDialog.logo') }}</label>
                <div class="flex gap-2 mb-2">
                  <input
                    v-model="logoUrl"
                    type="url"
                    :placeholder="t('manualEditDialog.logoUrlPlaceholder')"
                    class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                  <button
                    type="button"
                    @click="downloadLogoFromUrl"
                    :disabled="!logoUrl || uploadingLogo"
                    class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {{ t('manualEditDialog.download') }}
                  </button>
                </div>
                <div class="flex items-center gap-2">
                  <input
                    ref="logoFileInput"
                    type="file"
                    accept="image/*"
                    @change="uploadLogo"
                    class="hidden"
                  />
                  <button
                    type="button"
                    @click="$refs.logoFileInput.click()"
                    class="px-4 py-2 bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded-lg text-sm font-medium hover:bg-blue-100 dark:hover:bg-blue-800 transition-colors"
                  >
                    {{ t('manualEditDialog.selectFile') }}
                  </button>
                  <span class="text-sm text-gray-500 dark:text-gray-400">
                    {{ logoFileName || t('manualEditDialog.noFileSelected') }}
                  </span>
                </div>
                <div v-if="formData.icon_url" class="mt-2">
                  <img :src="formData.icon_url" alt="Logo" class="w-24 h-24 object-contain bg-white dark:bg-gray-800 rounded border border-gray-300 dark:border-gray-600" />
                </div>
              </div>

              <!-- Screenshots -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ t('manualEditDialog.screenshots') }}</label>
                <div class="flex gap-2 mb-2">
                  <input
                    v-model="screenshotUrl"
                    type="url"
                    :placeholder="t('manualEditDialog.screenshotsUrlPlaceholder')"
                    class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                  <button
                    type="button"
                    @click="downloadScreenshotsFromUrl"
                    :disabled="!screenshotUrl || uploadingScreenshots"
                    class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {{ t('manualEditDialog.download') }}
                  </button>
                </div>
                <div class="flex items-center gap-2">
                  <input
                    ref="screenshotFileInput"
                    type="file"
                    accept="image/*"
                    multiple
                    @change="uploadScreenshots"
                    class="hidden"
                  />
                  <button
                    type="button"
                    @click="$refs.screenshotFileInput.click()"
                    class="px-4 py-2 bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded-lg text-sm font-medium hover:bg-blue-100 dark:hover:bg-blue-800 transition-colors"
                  >
                    {{ t('manualEditDialog.selectFile') }}
                  </button>
                  <span class="text-sm text-gray-500 dark:text-gray-400">
                    {{ screenshotFileNames || t('manualEditDialog.noFileSelected') }}
                  </span>
                </div>
                <div v-if="formData.screenshots?.length > 0" class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div v-for="(screenshot, index) in formData.screenshots" :key="index" class="relative group bg-gray-100 dark:bg-gray-700 rounded-xl overflow-hidden border border-gray-200 dark:border-gray-600 hover:shadow-lg transition-all">
                    <div class="aspect-video relative">
                      <img :src="screenshot.url || screenshot" alt="Screenshot" class="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300" />
                      <button
                        type="button"
                        @click="removeScreenshot(index)"
                        class="absolute top-2 right-2 p-2 bg-red-600 hover:bg-red-700 text-white rounded-lg shadow-lg transition-colors"
                        :title="t('manualEditDialog.deleteScreenshot')"
                      >
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                    <div class="p-3 bg-white dark:bg-gray-800">
                      <p class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('manualEditDialog.screenshotLabel') }} {{ index + 1 }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </form>
        </div>

        <!-- Footer -->
        <div class="sticky bottom-0 bg-gray-50 dark:bg-gray-700 px-6 py-4 border-t border-gray-200 dark:border-gray-600 flex justify-between gap-3">
          <button
            @click="close"
            class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors"
          >
            {{ t('manualEditDialog.cancel') }}
          </button>
          <button
            @click="save"
            :disabled="saving"
            class="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ saving ? t('manualEditDialog.saving') : t('manualEditDialog.save') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Reference Sites Dialog -->
    <div
      v-if="showReferenceSitesDialog"
      class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black bg-opacity-50"
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
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { productsApi } from '../../api/products'
import { imagesApi } from '../../api/images'
import { useDialog } from '../../composables/useDialog'

const { t } = useI18n({ useScope: 'global' })
const { alert } = useDialog()

const props = defineProps({
  product: {
    type: Object,
    default: null
  },
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'saved'])

const formData = ref({
  title: '',
  subtitle: '',
  description: '',
  vendor: '',
  category: '',
  official_website: '',
  license_type: '',
  platform: '',
  release_notes: '',
  release_date: '',
  icon_url: '',
  screenshots: [],
  features: [],
  system_requirements: {},
  supported_formats: [],
  download_url: ''
})

const logoUrl = ref('')
const screenshotUrl = ref('')
const uploadingLogo = ref(false)
const uploadingScreenshots = ref(false)
const saving = ref(false)
const showReferenceSitesDialog = ref(false)
const logoFileName = ref('')
const screenshotFileNames = ref('')

// Helper refs for text-based inputs
const featuresText = ref('')
const systemRequirementsText = ref('')
const supportedFormatsText = ref('')

// Reference sites
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

// Initialize form data when dialog opens
watch(() => props.isOpen, (isOpen) => {
  if (isOpen && props.product) {
    formData.value = {
      title: props.product.title || '',
      subtitle: props.product.subtitle || '',
      description: props.product.description || '',
      vendor: props.product.vendor || '',
      category: props.product.category || '',
      official_website: props.product.official_website || '',
      license_type: props.product.license_type || '',
      platform: props.product.platform || '',
      release_notes: props.product.release_notes || '',
      release_date: props.product.release_date || '',
      icon_url: props.product.icon_url || '',
      screenshots: props.product.screenshots || [],
      features: props.product.features || [],
      system_requirements: props.product.system_requirements || {},
      supported_formats: props.product.supported_formats || [],
      download_url: props.product.download_url || ''
    }

    // Initialize text fields
    featuresText.value = (props.product.features || []).join('\n')
    systemRequirementsText.value = props.product.system_requirements ? JSON.stringify(props.product.system_requirements, null, 2) : ''
    supportedFormatsText.value = (props.product.supported_formats || []).join(', ')

    logoUrl.value = ''
    screenshotUrl.value = ''
    logoFileName.value = ''
    screenshotFileNames.value = ''
  }
})

// Logo upload
const uploadLogo = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  logoFileName.value = file.name
  uploadingLogo.value = true
  try {
    const response = await imagesApi.uploadLogo(props.product.id, file)
    formData.value.icon_url = response.data.icon_url
  } catch (error) {
    console.error('Logo upload error:', error)
    await alert.error(t('manualEditDialog.logoUploadFailed'))
    logoFileName.value = ''
  } finally {
    uploadingLogo.value = false
    event.target.value = ''
  }
}

// Logo download from URL
const downloadLogoFromUrl = async () => {
  if (!logoUrl.value) return

  uploadingLogo.value = true
  try {
    const response = await imagesApi.downloadLogo(props.product.id, logoUrl.value)
    formData.value.icon_url = response.data.icon_url
    logoUrl.value = ''
  } catch (error) {
    console.error('Logo download error:', error)
    await alert.error(t('manualEditDialog.logoDownloadFailed'))
  } finally {
    uploadingLogo.value = false
  }
}

// Screenshots upload
const uploadScreenshots = async (event) => {
  const files = Array.from(event.target.files)
  if (!files.length) return

  screenshotFileNames.value = `${files.length} ${t('manualEditDialog.filesSelected')}`
  uploadingScreenshots.value = true
  try {
    const response = await imagesApi.uploadScreenshots(props.product.id, files)
    formData.value.screenshots = response.data.screenshots
  } catch (error) {
    console.error('Screenshots upload error:', error)
    await alert.error(t('manualEditDialog.screenshotUploadFailed'))
    screenshotFileNames.value = ''
  } finally {
    uploadingScreenshots.value = false
    event.target.value = ''
  }
}

// Screenshots download from URL
const downloadScreenshotsFromUrl = async () => {
  if (!screenshotUrl.value) return

  // Split by comma if multiple URLs
  const urls = screenshotUrl.value.split(',').map(url => url.trim()).filter(url => url)
  if (!urls.length) return

  uploadingScreenshots.value = true
  try {
    const response = await imagesApi.downloadScreenshots(props.product.id, urls)
    formData.value.screenshots = response.data.screenshots
    screenshotUrl.value = ''
  } catch (error) {
    console.error('Screenshots download error:', error)
    await alert.error(t('manualEditDialog.screenshotDownloadFailed'))
  } finally {
    uploadingScreenshots.value = false
  }
}

// Remove screenshot
const removeScreenshot = (index) => {
  formData.value.screenshots.splice(index, 1)
}

// Save changes
const save = async () => {
  saving.value = true

  try {
    // Convert text fields to arrays/objects
    const dataToSave = {
      ...formData.value,
      features: featuresText.value.split('\n').filter(f => f.trim()),
      supported_formats: supportedFormatsText.value.split(',').map(f => f.trim()).filter(f => f)
    }

    // Parse system requirements JSON
    if (systemRequirementsText.value.trim()) {
      try {
        dataToSave.system_requirements = JSON.parse(systemRequirementsText.value)
      } catch (e) {
        await alert.warning(t('manualEditDialog.invalidJsonFormat'))
        saving.value = false
        return
      }
    } else {
      dataToSave.system_requirements = {}
    }

    await productsApi.updateProduct(props.product.id, dataToSave)
    emit('saved', dataToSave)
    emit('close')
  } catch (error) {
    console.error('Save error:', error)
    await alert.error(t('manualEditDialog.saveError'))
  } finally {
    saving.value = false
  }
}

const close = () => {
  emit('close')
}
</script>
