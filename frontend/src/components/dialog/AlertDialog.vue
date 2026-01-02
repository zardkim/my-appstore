<template>
  <Teleport to="body">
    <Transition name="dialog-fade">
      <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @click.self="close">
        <Transition name="dialog-scale">
          <div v-if="modelValue" class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full overflow-hidden" @click.stop>
            <!-- Header with Icon -->
            <div class="p-6 pb-4">
              <div class="flex items-start space-x-4">
                <div :class="iconClass" class="flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center">
                  <svg v-if="type === 'success'" class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <svg v-else-if="type === 'error'" class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  <svg v-else-if="type === 'warning'" class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <svg v-else class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <h3 v-if="title" class="text-lg font-bold text-gray-900 dark:text-white mb-2">{{ title }}</h3>
                  <p class="text-gray-600 dark:text-gray-300 leading-relaxed">{{ message }}</p>
                </div>
              </div>
            </div>

            <!-- Footer with Action Button -->
            <div class="px-6 py-4 bg-gray-50 dark:bg-gray-900/50 flex justify-end">
              <button
                @click="close"
                :class="buttonClass"
                class="px-6 py-2.5 rounded-xl font-medium transition-all shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 text-white"
              >
                {{ confirmText }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  type: {
    type: String,
    default: 'info', // success, error, warning, info
    validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
  },
  title: {
    type: String,
    default: ''
  },
  message: {
    type: String,
    required: true
  },
  confirmText: {
    type: String,
    default: '확인'
  }
})

const emit = defineEmits(['update:modelValue', 'confirm'])

const close = () => {
  emit('update:modelValue', false)
  emit('confirm')
}

const iconClass = computed(() => {
  switch (props.type) {
    case 'success':
      return 'bg-gradient-to-br from-green-500 to-emerald-600'
    case 'error':
      return 'bg-gradient-to-br from-red-500 to-rose-600'
    case 'warning':
      return 'bg-gradient-to-br from-yellow-500 to-orange-600'
    default:
      return 'bg-gradient-to-br from-blue-500 to-indigo-600'
  }
})

const buttonClass = computed(() => {
  switch (props.type) {
    case 'success':
      return 'bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 focus:ring-green-500'
    case 'error':
      return 'bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 focus:ring-red-500'
    case 'warning':
      return 'bg-gradient-to-r from-yellow-500 to-orange-600 hover:from-yellow-600 hover:to-orange-700 focus:ring-yellow-500'
    default:
      return 'bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 focus:ring-blue-500'
  }
})
</script>

<style scoped>
.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: opacity 0.2s ease;
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
}

.dialog-scale-enter-active {
  transition: all 0.3s ease;
}

.dialog-scale-leave-active {
  transition: all 0.2s ease;
}

.dialog-scale-enter-from {
  opacity: 0;
  transform: scale(0.9) translateY(-20px);
}

.dialog-scale-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
