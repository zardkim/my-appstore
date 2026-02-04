import apiClient from './client'

export const authApi = {
  async login(username, password) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    return apiClient.post('auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  async checkSetup() {
    return apiClient.get('auth/check-setup')
  },

  async setup(username, password) {
    return apiClient.post('auth/setup', {
      username,
      password,
      role: 'admin'
    })
  },

  async changePassword(currentPassword, newPassword) {
    return apiClient.post('auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    })
  },

  async getRegistrationStatus() {
    return apiClient.get('auth/registration-status')
  },

  async register(username, password, email) {
    return apiClient.post('auth/register', {
      username,
      password,
      email
    })
  }
}
