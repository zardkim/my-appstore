/**
 * Environment variable utilities
 * Provides centralized access to environment variables
 */

// 백엔드 포트 추출 함수
function getBackendPort() {
  const envUrl = import.meta.env.VITE_BACKEND_URL
  if (envUrl) {
    try {
      const url = new URL(envUrl)
      return url.port || (url.protocol === 'https:' ? '443' : '80')
    } catch (e) {
      // URL 파싱 실패 시 기본값
    }
  }
  return '8110' // 기본 백엔드 포트
}

// 동적으로 백엔드 URL 생성
function getBackendBaseUrl() {
  const envUrl = import.meta.env.VITE_BACKEND_URL

  // 환경 변수가 절대 URL이면서 localhost가 아니면 그대로 사용
  if (envUrl && (envUrl.startsWith('http://') || envUrl.startsWith('https://'))) {
    // localhost로 설정되어 있지만 현재 접속 호스트가 다르면 현재 호스트 사용
    const currentHostname = window.location.hostname
    if (envUrl.includes('localhost') && currentHostname !== 'localhost' && currentHostname !== '127.0.0.1') {
      const protocol = window.location.protocol
      // HTTPS 프로덕션 환경에서는 포트 명시하지 않음 (리버스 프록시 사용)
      if (protocol === 'https:') {
        return `${protocol}//${currentHostname}`
      }
      // HTTP 개발 환경에서는 포트 명시
      const port = getBackendPort()
      return `${protocol}//${currentHostname}:${port}`
    }
    return envUrl
  }

  // 환경 변수가 없으면 현재 호스트 기준으로 생성
  const hostname = window.location.hostname
  const protocol = window.location.protocol

  // HTTPS 환경에서는 포트 명시하지 않음 (리버스 프록시 또는 기본 443 포트 사용)
  if (protocol === 'https:') {
    return `${protocol}//${hostname}`
  }

  // HTTP 환경에서는 개발용 포트 사용
  const port = getBackendPort()
  return `${protocol}//${hostname}:${port}`
}

// 동적으로 앱 URL 생성
function getAppBaseUrl() {
  const envUrl = import.meta.env.VITE_APP_URL

  // 환경 변수가 절대 URL이면 그대로 사용
  if (envUrl && (envUrl.startsWith('http://') || envUrl.startsWith('https://'))) {
    return envUrl
  }

  // 환경 변수가 없으면 현재 location 사용
  return `${window.location.protocol}//${window.location.host}`
}

export const ENV = {
  // API Base URL (for axios requests)
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || `${getBackendBaseUrl()}/api`,

  // Backend Base URL (for direct file access, downloads)
  BACKEND_URL: getBackendBaseUrl(),

  // Frontend App URL (this application's URL)
  APP_URL: getAppBaseUrl(),
}

/**
 * Get full backend URL
 * @param {string} path - Path to append (e.g., '/static/icons/1.png')
 * @returns {string} Full URL
 */
export function getBackendUrl(path) {
  if (!path) return ENV.BACKEND_URL

  // Remove leading slash if present to avoid double slashes
  const cleanPath = path.startsWith('/') ? path : `/${path}`
  return `${ENV.BACKEND_URL}${cleanPath}`
}

/**
 * Get download URL with token
 * @param {number} versionId - Version ID
 * @param {string} token - Access token
 * @returns {string} Download URL
 */
export function getDownloadUrl(versionId, token) {
  return `${ENV.BACKEND_URL}/api/download/${versionId}?token=${token}`
}

/**
 * Get icon URL
 * @param {string} iconUrl - Icon path from database
 * @returns {string} Full icon URL or empty string
 */
export function getIconUrl(iconUrl) {
  if (!iconUrl) return ''

  // If already a full URL, return as-is
  if (iconUrl.startsWith('http://') || iconUrl.startsWith('https://')) {
    return iconUrl
  }

  // If relative path starting with /static, return as relative path
  // Both dev (vite proxy) and prod (nginx proxy) will handle /static requests
  if (iconUrl.startsWith('/static')) {
    return iconUrl
  }

  return iconUrl
}

/**
 * Get screenshot URL
 * @param {string|object} screenshot - Screenshot path or object from database
 * @returns {string} Full screenshot URL or empty string
 */
export function getScreenshotUrl(screenshot) {
  if (!screenshot) return ''

  // Handle object format { url: '...' }
  const url = typeof screenshot === 'object' ? screenshot.url : screenshot

  if (!url) return ''

  // If already a full URL, return as-is
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }

  // If relative path starting with /static, return as relative path
  if (url.startsWith('/static')) {
    return url
  }

  return url
}
