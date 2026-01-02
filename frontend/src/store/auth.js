import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'

// Helper function to decode JWT token
function decodeJwt(token) {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
    }).join(''))
    return JSON.parse(jsonPayload)
  } catch (e) {
    console.error("Error decoding JWT token:", e)
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || null)
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  // Initialize user from token if available
  if (token.value) {
    const decodedToken = decodeJwt(token.value)
    if (decodedToken) {
      user.value = { username: decodedToken.sub, role: decodedToken.role }
    }
  }

  async function login(username, password) {
    const response = await authApi.login(username, password)
    token.value = response.data.access_token
    localStorage.setItem('access_token', token.value)

    const decodedToken = decodeJwt(token.value)
    if (decodedToken) {
      user.value = { username: decodedToken.sub, role: decodedToken.role }
    } else {
      // Fallback if decoding fails
      user.value = { username, role: 'user' }
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
  }

  function checkAuth() {
    if (token.value) {
      const decodedToken = decodeJwt(token.value)
      if (decodedToken) {
        user.value = { username: decodedToken.sub, role: decodedToken.role }
      } else {
        logout()
      }
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout,
    checkAuth
  }
})
