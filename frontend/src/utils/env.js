/**
 * Environment variable utilities
 * Provides centralized access to environment variables
 */

// 동적으로 백엔드 URL 생성
function getBackendBaseUrl() {
  const envUrl = import.meta.env.VITE_BACKEND_URL

  // 환경 변수가 절대 URL이면 그대로 사용
  if (envUrl && (envUrl.startsWith('http://') || envUrl.startsWith('https://'))) {
    return envUrl
  }

  // 환경 변수가 없으면 현재 호스트 기준으로 생성
  const hostname = window.location.hostname
  const protocol = window.location.protocol
  return `${protocol}//${hostname}:8100`
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

  // If relative path starting with /static, prepend backend URL
  if (iconUrl.startsWith('/static')) {
    return getBackendUrl(iconUrl)
  }

  return iconUrl
}
