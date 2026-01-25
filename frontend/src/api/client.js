import axios from 'axios'

// 동적으로 API URL 생성
// 환경 변수가 설정되어 있으면 사용하고, 없으면 현재 호스트를 기준으로 생성
function getApiBaseUrl() {
  const envUrl = import.meta.env.VITE_API_BASE_URL

  // 환경 변수가 설정되어 있고 절대 URL이면 그대로 사용
  if (envUrl && (envUrl.startsWith('http://') || envUrl.startsWith('https://'))) {
    return envUrl
  }

  // 환경 변수가 상대 경로면 그대로 사용
  if (envUrl && envUrl.startsWith('/')) {
    return envUrl
  }

  // 환경 변수가 없으면 상대 경로 사용 (역방향 프록시 환경 지원)
  // 이렇게 하면 https://app.nuripc.kr에서 접속하면 https://app.nuripc.kr/api를 사용
  return '/api'
}

const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    // Check if we received HTML instead of JSON (indicates reverse proxy misconfiguration)
    const contentType = response.headers['content-type']
    if (contentType && contentType.includes('text/html')) {
      const error = new Error('Received HTML instead of JSON - check reverse proxy configuration')
      error.response = response
      return Promise.reject(error)
    }
    return response
  },
  (error) => {
    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }

    // Suppress console logging for HTML responses (reverse proxy misconfiguration)
    if (error.response?.headers?.['content-type']?.includes('text/html')) {
      error.silent = true
    }

    return Promise.reject(error)
  }
)

export default apiClient
