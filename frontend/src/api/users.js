import client from './client'

export const usersApi = {
  // Get all users (admin only)
  getAll: async () => {
    const response = await client.get('/users/')
    return response.data
  },

  // Create user (admin only)
  create: async (username, password, role = 'user') => {
    const response = await client.post('/users/', {
      username,
      password,
      role
    })
    return response.data
  },

  // Change user password (admin only)
  changePassword: async (userId, newPassword) => {
    const response = await client.patch(`/users/${userId}/password`, {
      new_password: newPassword
    })
    return response.data
  },

  // Toggle user status (admin only)
  toggleStatus: async (userId, isActive) => {
    const response = await client.patch(`/users/${userId}/status`, {
      is_active: isActive
    })
    return response.data
  },

  // Delete user (admin only)
  delete: async (userId) => {
    const response = await client.delete(`/users/${userId}`)
    return response.data
  }
}
