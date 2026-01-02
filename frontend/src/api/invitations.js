import client from './client'

export const invitationsApi = {
  // Send invitation email
  send: async (email) => {
    const response = await client.post('/invitations/send', { email })
    return response.data
  },

  // Verify invitation code
  verify: async (code) => {
    const response = await client.get(`/invitations/verify/${code}`)
    return response.data
  },

  // Register with invitation code
  register: async (code, username, password) => {
    const response = await client.post('/invitations/register', {
      code,
      username,
      password
    })
    return response.data
  },

  // Get all invitations (admin only)
  getAll: async () => {
    const response = await client.get('/invitations/')
    return response.data
  },

  // Delete invitation (admin only)
  delete: async (invitationId) => {
    const response = await client.delete(`/invitations/${invitationId}`)
    return response.data
  }
}
