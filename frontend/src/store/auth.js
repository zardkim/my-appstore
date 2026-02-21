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

// Helper to check if token is expired
function isTokenExpired(decoded) {
  if (!decoded || !decoded.exp) return true
  // decoded.exp is in seconds (Unix timestamp)
  return Date.now() >= decoded.exp * 1000
}

export const useAuthStore = defineStore('auth', () => {
  // 로컬스토리지 우선, 없으면 세션스토리지 확인 (remember me 지원)
  const token = ref(localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || null)
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  // Initialize user from token if available
  if (token.value) {
    const decodedToken = decodeJwt(token.value)
    if (decodedToken && !isTokenExpired(decodedToken)) {
      user.value = { username: decodedToken.sub, role: decodedToken.role }
    } else {
      // Token expired or invalid - clear it
      token.value = null
      localStorage.removeItem('access_token')
      sessionStorage.removeItem('access_token')
    }
  }

  async function login(username, password, remember = true) {
    const response = await authApi.login(username, password)
    token.value = response.data.access_token

    if (remember) {
      // 30일 유지: localStorage에 저장
      localStorage.setItem('access_token', token.value)
      sessionStorage.removeItem('access_token')
    } else {
      // 브라우저 닫으면 만료: sessionStorage에 저장
      sessionStorage.setItem('access_token', token.value)
      localStorage.removeItem('access_token')
    }

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
    sessionStorage.removeItem('access_token')
  }

  function checkAuth() {
    if (token.value) {
      const decodedToken = decodeJwt(token.value)
      if (decodedToken && !isTokenExpired(decodedToken)) {
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
