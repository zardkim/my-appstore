<template>
  <div id="app">
    <router-view />

    <!-- Global Dialog Components -->
    <AlertDialog
      v-model="alertDialogState.show"
      :type="alertDialogState.type"
      :title="alertDialogState.title"
      :message="alertDialogState.message"
      :confirm-text="alertDialogState.confirmText"
      @confirm="alertDialogState.onConfirm"
    />

    <ConfirmDialog
      v-model="confirmDialogState.show"
      :type="confirmDialogState.type"
      :title="confirmDialogState.title"
      :message="confirmDialogState.message"
      :confirm-text="confirmDialogState.confirmText"
      :cancel-text="confirmDialogState.cancelText"
      @confirm="confirmDialogState.onConfirm"
      @cancel="confirmDialogState.onCancel"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './store/auth'
import { useThemeStore } from './store/theme'
import { useDialog } from './composables/useDialog'
import AlertDialog from './components/dialog/AlertDialog.vue'
import ConfirmDialog from './components/dialog/ConfirmDialog.vue'

const authStore = useAuthStore()
const themeStore = useThemeStore()
const { alertDialogState, confirmDialogState } = useDialog()

onMounted(() => {
  // Initialize theme from localStorage or system preference
  themeStore.initTheme()

  // Check authentication on app mount
  authStore.checkAuth()
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  width: 100%;
  overflow: hidden;
}

#app {
  background-color: #f9fafb;
  transition: background-color 0.3s ease;
}

.dark #app {
  background-color: #111827;
}

/* 스크롤바 숨기기 */
.scrollbar-hide {
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;  /* Chrome, Safari and Opera */
}
</style>
