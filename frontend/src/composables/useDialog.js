import { ref } from 'vue'

// Alert Dialog State
const alertDialogState = ref({
  show: false,
  type: 'info',
  title: '',
  message: '',
  confirmText: '확인',
  onConfirm: null
})

// Confirm Dialog State
const confirmDialogState = ref({
  show: false,
  type: 'info',
  title: '',
  message: '',
  confirmText: '확인',
  cancelText: '취소',
  onConfirm: null,
  onCancel: null
})

export function useDialog() {
  // Alert Dialog Methods
  const showAlert = (options) => {
    return new Promise((resolve) => {
      alertDialogState.value = {
        show: true,
        type: options.type || 'info',
        title: options.title || '',
        message: options.message || '',
        confirmText: options.confirmText || '확인',
        onConfirm: () => {
          alertDialogState.value.show = false
          resolve()
        }
      }
    })
  }

  const hideAlert = () => {
    alertDialogState.value.show = false
  }

  // Confirm Dialog Methods
  const showConfirm = (options) => {
    return new Promise((resolve, reject) => {
      confirmDialogState.value = {
        show: true,
        type: options.type || 'info',
        title: options.title || '',
        message: options.message || '',
        confirmText: options.confirmText || '확인',
        cancelText: options.cancelText || '취소',
        onConfirm: () => {
          confirmDialogState.value.show = false
          resolve(true)
        },
        onCancel: () => {
          confirmDialogState.value.show = false
          resolve(false)
        }
      }
    })
  }

  const hideConfirm = () => {
    confirmDialogState.value.show = false
  }

  // Convenience methods with preset types
  const alert = {
    success: (message, title = '성공') => showAlert({ type: 'success', title, message }),
    error: (message, title = '오류') => showAlert({ type: 'error', title, message }),
    warning: (message, title = '경고') => showAlert({ type: 'warning', title, message }),
    info: (message, title = '') => showAlert({ type: 'info', title, message })
  }

  const confirm = {
    danger: (message, title = '확인') => showConfirm({ type: 'danger', title, message, confirmText: '삭제', cancelText: '취소' }),
    warning: (message, title = '확인') => showConfirm({ type: 'warning', title, message }),
    info: (message, title = '확인') => showConfirm({ type: 'info', title, message })
  }

  return {
    // States
    alertDialogState,
    confirmDialogState,

    // Methods
    showAlert,
    hideAlert,
    showConfirm,
    hideConfirm,

    // Convenience
    alert,
    confirm
  }
}
